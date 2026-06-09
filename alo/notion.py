"""Notion REST client — mirror the curriculum into a self-contained dashboard.

Deterministic CRUD with the integration token (from .env). We sync via the REST API rather than the
Notion MCP: it's plain idempotent CRUD, and the headless agent+MCP path is overkill and blocked by
the safe-agent guard. The MCP stays for interactive Claude Code use.

Notion holds everything needed to work a unit (properties + a page body with resources) plus a
legend page — so you never have to open the repo.
"""
from __future__ import annotations

import json
import re
import time

import requests

from . import env as _env

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
STATE = _env.REPO / ".notion.json"
UNITS_DB_TITLE = "AI Eng Curriculum — Units"
LEGEND_TITLE = "📘 Curriculum legend"

# properties added on top of the base create-schema (idempotent PATCH)
EXTRA_PROPS = {
    "Number": {"number": {"format": "number"}},
    "Deliverable": {"rich_text": {}},
    "Resources": {"rich_text": {}},
    "Teach me": {"checkbox": {}},
}


class NotionError(RuntimeError):
    pass


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Notion-Version": VERSION,
            "Content-Type": "application/json"}


def _req(method: str, path: str, token: str, _tries: int = 4, **kw) -> dict:
    """Notion request with retry/backoff on transient errors (timeouts, 429, 5xx)."""
    last: Exception | None = None
    for attempt in range(_tries):
        try:
            resp = requests.request(method, f"{API}{path}", headers=_headers(token), timeout=45, **kw)
        except requests.exceptions.RequestException as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
            continue
        if resp.status_code in (429, 500, 502, 503, 504):
            last = NotionError(f"{method} {path} -> {resp.status_code}")
            time.sleep(1.5 * (attempt + 1))
            continue
        if resp.status_code >= 300:
            raise NotionError(f"{method} {path} -> {resp.status_code}: {resp.text[:400]}")
        return resp.json() if resp.text else {}
    raise NotionError(f"{method} {path} failed after {_tries} attempts: {last}")


def _load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def _save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# --- property + block builders ---------------------------------------------

def _title(text: str) -> dict:
    return {"title": [{"type": "text", "text": {"content": (text or "")[:1900]}}]}


def _rt(text: str) -> dict:
    return {"rich_text": ([{"type": "text", "text": {"content": text[:1900]}}] if text else [])}


def _select(name: str | None) -> dict:
    return {"select": ({"name": name[:90]} if name else None)}


def _multi(names) -> dict:
    return {"multi_select": [{"name": str(n)[:90]} for n in (names or [])]}


def _num(n) -> dict:
    return {"number": n}


def _h3(text: str) -> dict:
    return {"object": "block", "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]}}


def _para(text: str) -> dict:
    return {"object": "block", "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]}}


def _bullet(text: str) -> dict:
    return {"object": "block", "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text[:1900]}}]}}


def _plain_title(page: dict) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in prop.get("title", [])) or "(untitled)"
    return "(untitled)"


def _unit_number(uid: str) -> int | None:
    m = re.match(r"u(\d+)", uid)
    return int(m.group(1)) if m else None


# --- database lifecycle -----------------------------------------------------

def find_parent_page(token: str) -> tuple[str, str]:
    """First page the integration can access — used as the home for the DB + legend."""
    data = _req("POST", "/search", token,
                json={"filter": {"value": "page", "property": "object"}, "page_size": 20})
    pages = data.get("results", [])
    if not pages:
        raise NotionError(
            "the integration can't access any Notion page. Open the page you want as the dashboard "
            "→ ••• → Connections → add your integration, then retry.")
    page = pages[0]
    return page["id"], _plain_title(page)


def ensure_schema(token: str, db_id: str) -> None:
    """Add any missing properties (Number/Deliverable/Resources/Teach me) — idempotent."""
    _req("PATCH", f"/databases/{db_id}", token, json={"properties": EXTRA_PROPS})


def _db_ok(token: str, db_id: str) -> bool:
    try:
        _req("GET", f"/databases/{db_id}", token)
        return True
    except NotionError:
        return False


def ensure_units_db(token: str) -> tuple[str, str]:
    """Return (database_id, note). Reuse the cached DB if valid, else create it; ensure schema."""
    state = _load_state()
    db_id = state.get("units_db_id")
    if db_id and _db_ok(token, db_id):
        note = f"reused database {db_id}"
    else:
        parent_id, parent_title = find_parent_page(token)
        base = {
            "Unit": {"title": {}},
            "UnitId": {"rich_text": {}},
            "Tier": {"select": {"options": [{"name": t} for t in
                     ["foundational", "intermediate", "advanced", "capstone"]]}},
            "Status": {"select": {"options": [{"name": s} for s in ["todo", "in_progress", "done"]]}},
            "Introduces": {"multi_select": {}},
            "Reinforces": {"multi_select": {}},
            "BuildsOn": {"rich_text": {}},
            "DepthObjective": {"rich_text": {}},
            "MasteryCheck": {"rich_text": {}},
        }
        db = _req("POST", "/databases", token, json={
            "parent": {"type": "page_id", "page_id": parent_id},
            "title": [{"type": "text", "text": {"content": UNITS_DB_TITLE}}],
            "properties": base,
        })
        db_id = db["id"]
        state.update({"units_db_id": db_id, "parent_page_id": parent_id, "parent_title": parent_title})
        _save_state(state)
        note = f"created database under page '{parent_title}'"
    ensure_schema(token, db_id)
    return db_id, note


# --- units ------------------------------------------------------------------

def _unit_props(u: dict) -> dict:
    # NB: deliberately does NOT set "Teach me" — that checkbox is user-owned.
    return {
        "Unit": _title(u.get("title", u["id"])),
        "UnitId": _rt(u["id"]),
        "Number": _num(_unit_number(u["id"])),
        "Tier": _select(u.get("tier")),
        "Status": _select(u.get("status", "todo")),
        "Introduces": _multi(u.get("introduces")),
        "Reinforces": _multi(u.get("reinforces")),
        "BuildsOn": _rt(", ".join(u.get("builds_on") or [])),
        "DepthObjective": _rt(u.get("depth_objective", "")),
        "MasteryCheck": _rt(u.get("mastery_check", "")),
        "Deliverable": _rt(u.get("deliverable", "")),
        "Resources": _rt(u.get("resources", "")),
    }


def _unit_body_blocks(u: dict) -> list[dict]:
    blocks: list[dict] = []
    if u.get("deliverable"):
        blocks += [_h3("Deliverable"), _para(u["deliverable"])]
    if u.get("depth_objective"):
        blocks += [_h3("Depth objective"), _para(u["depth_objective"])]
    if u.get("mastery_check"):
        blocks += [_h3("Mastery check — you understand it when…"), _para(u["mastery_check"])]
    res = u.get("resources", "")
    if res:
        blocks.append(_h3("Where to learn this (resources)"))
        for item in (r.strip() for r in re.split(r";|\n", res) if r.strip()):
            blocks.append(_bullet(item))
    return blocks


def _children(token: str, page_id: str) -> list[dict]:
    return _req("GET", f"/blocks/{page_id}/children?page_size=100", token).get("results", [])


def write_body_if_empty(token: str, page_id: str, u: dict) -> bool:
    """Write the unit brief into the page body only if the page has no content yet."""
    if _children(token, page_id):
        return False
    blocks = _unit_body_blocks(u)
    if not blocks:
        return False
    _req("PATCH", f"/blocks/{page_id}/children", token, json={"children": blocks})
    return True


def upsert_unit(token: str, db_id: str, u: dict) -> tuple[str, str]:
    """Create or update the row whose UnitId == u['id']. Returns (action, page_id)."""
    found = _req("POST", f"/databases/{db_id}/query", token,
                 json={"filter": {"property": "UnitId", "rich_text": {"equals": u["id"]}},
                       "page_size": 1}).get("results", [])
    props = _unit_props(u)
    if found:
        page_id = found[0]["id"]
        _req("PATCH", f"/pages/{page_id}", token, json={"properties": props})
        return "updated", page_id
    page = _req("POST", "/pages", token, json={"parent": {"database_id": db_id}, "properties": props})
    return "created", page["id"]


# --- legend page ------------------------------------------------------------

def ensure_legend_page(token: str) -> str:
    state = _load_state()
    pid = state.get("legend_page_id")
    if pid:
        try:
            _req("GET", f"/pages/{pid}", token)
            return pid
        except NotionError:
            pass
    parent = state.get("parent_page_id") or find_parent_page(token)[0]
    page = _req("POST", "/pages", token, json={
        "parent": {"type": "page_id", "page_id": parent},
        "properties": {"title": [{"type": "text", "text": {"content": LEGEND_TITLE}}]}})
    state["legend_page_id"] = page["id"]
    _save_state(state)
    return page["id"]


def write_legend(token: str, concepts: list[dict], units: list[dict]) -> str:
    """(Re)write the legend page: mastery ladder, tiers, domains, and live coverage."""
    pid = ensure_legend_page(token)
    for block in _children(token, pid):
        _req("DELETE", f"/blocks/{block['id']}", token)

    domains = sorted({c["domain"] for c in concepts})
    covered = {x for u in units for x in (u.get("introduces") or []) + (u.get("reinforces") or [])}
    blocks = [
        _h3("Mastery ladder"),
        _para("0 unseen · 1 introduced · 2 applied once · 3 reused in a harder context · 4 fluent / can-teach"),
        _h3("Tiers (difficulty)"),
        _para("foundational → intermediate → advanced → capstone"),
        _h3("Fields on each unit"),
        _para("Introduces = new concepts · Reinforces = older concepts reused (the spiral) · "
              "BuildsOn = a prior unit it extends."),
        _h3("Domains"),
    ]
    for d in domains:
        n = sum(1 for c in concepts if c["domain"] == d)
        blocks.append(_bullet(f"{d} — {n} concepts"))
    blocks += [
        _h3("Coverage"),
        _para(f"{len(covered)}/{len(concepts)} concepts are touched by a unit · {len(units)} units total."),
    ]
    _req("PATCH", f"/blocks/{pid}/children", token, json={"children": blocks})
    return pid


# --- reverse sync (Notion -> local) + teach-me ------------------------------

def _prop_text(prop: dict | None) -> str:
    if not prop:
        return ""
    kind = prop.get("type")
    if kind == "rich_text":
        return "".join(x.get("plain_text", "") for x in prop["rich_text"])
    if kind == "title":
        return "".join(x.get("plain_text", "") for x in prop["title"])
    if kind == "select":
        return (prop.get("select") or {}).get("name", "")
    return ""


def fetch_units(token: str, db_id: str) -> list[dict]:
    """Every row as {unit_id, status, teach_me, page_id} — the Notion-side state."""
    rows: list[dict] = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = _req("POST", f"/databases/{db_id}/query", token, json=body)
        for row in data.get("results", []):
            props = row.get("properties", {})
            rows.append({
                "unit_id": _prop_text(props.get("UnitId")),
                "status": _prop_text(props.get("Status")) or "todo",
                "teach_me": bool((props.get("Teach me") or {}).get("checkbox", False)),
                "page_id": row["id"],
            })
        if data.get("has_more"):
            cursor = data.get("next_cursor")
        else:
            break
    return rows


def set_teach_me(token: str, page_id: str, value: bool) -> None:
    _req("PATCH", f"/pages/{page_id}", token, json={"properties": {"Teach me": {"checkbox": value}}})


def append_blocks(token: str, page_id: str, blocks: list[dict]) -> None:
    _req("PATCH", f"/blocks/{page_id}/children", token, json={"children": blocks})


def markdown_to_blocks(text: str) -> list[dict]:
    """Very small markdown → Notion blocks (headings, bullets, paragraphs)."""
    blocks: list[dict] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("### "):
            blocks.append(_h3(s[4:]))
        elif s.startswith("## "):
            blocks.append(_h3(s[3:]))
        elif s.startswith("# "):
            blocks.append(_h3(s[2:]))
        elif s.startswith(("- ", "* ")):
            blocks.append(_bullet(s[2:]))
        else:
            blocks.append(_para(s))
    return blocks[:90]
