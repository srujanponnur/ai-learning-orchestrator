"""Minimal Notion REST client to mirror curriculum units into a dashboard database.

Deterministic CRUD with the integration token (from .env). We sync via the REST API directly
rather than the Notion MCP: it's plain idempotent CRUD, and the headless agent+MCP path is both
overkill and blocked by the safe-agent guard. The MCP stays for interactive Claude Code use.
"""
from __future__ import annotations

import json

import requests

from . import env as _env

API = "https://api.notion.com/v1"
VERSION = "2022-06-28"
STATE = _env.REPO / ".notion.json"
UNITS_DB_TITLE = "AI Eng Curriculum — Units"


class NotionError(RuntimeError):
    pass


def _headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Notion-Version": VERSION,
            "Content-Type": "application/json"}


def _req(method: str, path: str, token: str, **kw) -> dict:
    resp = requests.request(method, f"{API}{path}", headers=_headers(token), timeout=30, **kw)
    if resp.status_code >= 300:
        raise NotionError(f"{method} {path} -> {resp.status_code}: {resp.text[:400]}")
    return resp.json()


def _load_state() -> dict:
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def _save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# --- property-value builders ---

def _title(text: str) -> dict:
    return {"title": [{"type": "text", "text": {"content": (text or "")[:1900]}}]}


def _rt(text: str) -> dict:
    return {"rich_text": ([{"type": "text", "text": {"content": text[:1900]}}] if text else [])}


def _select(name: str | None) -> dict:
    return {"select": ({"name": name[:90]} if name else None)}


def _multi(names) -> dict:
    return {"multi_select": [{"name": str(n)[:90]} for n in (names or [])]}


def _plain_title(page: dict) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            return "".join(t.get("plain_text", "") for t in prop.get("title", [])) or "(untitled)"
    return "(untitled)"


def find_parent_page(token: str) -> tuple[str, str]:
    """First page the integration can access — used as the home for the units DB."""
    data = _req("POST", "/search", token,
                json={"filter": {"value": "page", "property": "object"}, "page_size": 20})
    pages = data.get("results", [])
    if not pages:
        raise NotionError(
            "the integration can't access any Notion page. Open the page you want as the dashboard "
            "→ ••• → Connections → add your integration, then retry.")
    page = pages[0]
    return page["id"], _plain_title(page)


def ensure_units_db(token: str) -> tuple[str, str]:
    """Return (database_id, note). Reuse the cached id if still valid, else create the DB."""
    state = _load_state()
    db_id = state.get("units_db_id")
    if db_id:
        try:
            _req("GET", f"/databases/{db_id}", token)
            return db_id, f"reused cached database {db_id}"
        except NotionError:
            pass  # stale or inaccessible — recreate
    parent_id, parent_title = find_parent_page(token)
    props = {
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
        "properties": props,
    })
    state.update({"units_db_id": db["id"], "parent_page_id": parent_id, "parent_title": parent_title})
    _save_state(state)
    return db["id"], f"created database under page '{parent_title}'"


def _unit_props(u: dict) -> dict:
    return {
        "Unit": _title(u.get("title", u["id"])),
        "UnitId": _rt(u["id"]),
        "Tier": _select(u.get("tier")),
        "Status": _select(u.get("status", "todo")),
        "Introduces": _multi(u.get("introduces")),
        "Reinforces": _multi(u.get("reinforces")),
        "BuildsOn": _rt(", ".join(u.get("builds_on") or [])),
        "DepthObjective": _rt(u.get("depth_objective", "")),
        "MasteryCheck": _rt(u.get("mastery_check", "")),
    }


def upsert_unit(token: str, db_id: str, u: dict) -> str:
    """Create or update the row whose UnitId == u['id']. Returns 'created' | 'updated'."""
    found = _req("POST", f"/databases/{db_id}/query", token,
                 json={"filter": {"property": "UnitId", "rich_text": {"equals": u["id"]}},
                       "page_size": 1}).get("results", [])
    props = _unit_props(u)
    if found:
        _req("PATCH", f"/pages/{found[0]['id']}", token, json={"properties": props})
        return "updated"
    _req("POST", "/pages", token, json={"parent": {"database_id": db_id}, "properties": props})
    return "created"
