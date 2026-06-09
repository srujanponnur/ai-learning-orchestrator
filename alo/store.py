"""Load and persist the curriculum (md = source of truth).

`concepts.yaml` is the concept DAG; `curriculum/units/*.md` are the units (YAML
frontmatter + a short body). Notion is a downstream mirror, never the source.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CURRICULUM = REPO / "curriculum"
CONCEPTS_YAML = CURRICULUM / "concepts.yaml"
UNITS_DIR = CURRICULUM / "units"

VALID_TIERS = ["foundational", "intermediate", "advanced", "capstone"]


# --- concepts ---------------------------------------------------------------

def load_concepts(path: Path = CONCEPTS_YAML) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("concepts", []) if isinstance(data, dict) else []


def concepts_by_id(concepts: list[dict]) -> dict[str, dict]:
    return {c["id"]: c for c in concepts}


# --- units ------------------------------------------------------------------

def _parse_frontmatter(text: str) -> dict | None:
    if not text.lstrip().startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = yaml.safe_load(parts[1])
    return fm if isinstance(fm, dict) else None


_BODY_FIELDS = [("deliverable", "Deliverable"), ("depth_objective", "Depth objective"),
                ("mastery_check", "Mastery check"), ("resources", "Resources")]


def _parse_body(text: str) -> dict:
    """Pull the **Deliverable:** / **Depth objective:** / ... sections out of a unit's body."""
    parts = text.split("---", 2)
    body = parts[2] if len(parts) >= 3 else text
    out: dict[str, str] = {}
    for key, label in _BODY_FIELDS:
        m = re.search(r"\*\*" + re.escape(label) + r":\*\*\s*(.+?)(?=\n\n\*\*|\Z)", body, re.S)
        if m:
            out[key] = m.group(1).strip()
    return out


def load_units(units_dir: Path = UNITS_DIR) -> list[dict]:
    """All units (incl. case-studies/) as frontmatter + parsed body sections + `_path`."""
    units: list[dict] = []
    for md in sorted(units_dir.rglob("*.md")):
        if md.name.lower() == "readme.md":
            continue
        text = md.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        if fm and fm.get("id"):
            fm["_path"] = str(md)
            fm.update(_parse_body(text))
            units.append(fm)
    return units


def covered_concepts(units: list[dict]) -> set[str]:
    """Concepts that have appeared in any unit (introduced or reinforced) = 'seen'."""
    seen: set[str] = set()
    for u in units:
        seen.update(u.get("introduces") or [])
        seen.update(u.get("reinforces") or [])
    return seen


def highest_unit_number(units: list[dict]) -> int:
    nums = [int(m.group(1)) for u in units
            if (m := re.match(r"u(\d+)", str(u.get("id", ""))))]
    return max(nums, default=0)


# --- rendering --------------------------------------------------------------

def _fmt_list(xs) -> str:
    return "[" + ", ".join(str(x) for x in (xs or [])) + "]"


def _dq(s) -> str:
    """Double-quote a YAML scalar so colons/special chars in free text (e.g. titles) stay valid."""
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_unit_md(u: dict) -> str:
    created = u.get("created") or _dt.date.today().isoformat()
    resources = u.get("resources")
    if isinstance(resources, list):
        resources = "; ".join(str(r) for r in resources)
    frontmatter = (
        "---\n"
        f"id: {u['id']}\n"
        f"title: {_dq(u['title'])}\n"
        f"tier: {u['tier']}\n"
        f"created: {created}\n"
        f"status: {u.get('status', 'todo')}\n"
        f"prerequisites: {_fmt_list(u.get('prerequisites'))}\n"
        f"introduces: {_fmt_list(u.get('introduces'))}\n"
        f"reinforces: {_fmt_list(u.get('reinforces'))}\n"
        f"builds_on: {_fmt_list(u.get('builds_on'))}\n"
        f'est_effort: "{u.get("est_effort", "<= 1 week")}"\n'
        "---\n\n"
    )
    body = (
        f"**Deliverable:** {str(u.get('deliverable', '')).strip()}\n\n"
        f"**Depth objective:** {str(u.get('depth_objective', '')).strip()}\n\n"
        f"**Mastery check:** {str(u.get('mastery_check', '')).strip()}\n\n"
        f"**Resources:** {resources or ''}\n"
    )
    return frontmatter + body


def write_unit(u: dict, units_dir: Path = UNITS_DIR) -> Path:
    path = units_dir / f"{u['id']}.md"
    path.write_text(render_unit_md(u), encoding="utf-8")
    return path


# --- mastery mutations (targeted line edits so concepts.yaml comments/format survive) ---

MASTERY_LOG = CURRICULUM / "mastery-log.md"
DONE_STATES = {"done", "built", "complete", "completed"}


def set_mastery(concept_id: str, level: int, path: Path = CONCEPTS_YAML) -> int:
    """Set a concept's mastery in concepts.yaml via a single-line edit. Returns the previous level."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    pat = re.compile(r"id:\s*" + re.escape(concept_id) + r"(?![\w-])")
    for i, line in enumerate(lines):
        if pat.search(line):
            m = re.search(r"mastery:\s*(\d+)", line)
            old = int(m.group(1)) if m else 0
            lines[i] = re.sub(r"mastery:\s*\d+", f"mastery: {level}", line)
            path.write_text("".join(lines), encoding="utf-8")
            return old
    raise KeyError(f"concept {concept_id!r} not found in {path.name}")


def set_unit_status(unit_id: str, status: str, units_dir: Path = UNITS_DIR) -> str:
    """Set a unit's frontmatter `status` via a single-line edit. Returns the previous status."""
    for md in sorted(units_dir.rglob("*.md")):
        if md.name.lower() == "readme.md":
            continue
        text = md.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        if fm and fm.get("id") == unit_id:
            old = str(fm.get("status", "todo"))
            md.write_text(re.sub(r"(?m)^status:.*$", f"status: {status}", text, count=1), encoding="utf-8")
            return old
    raise KeyError(f"unit {unit_id!r} not found")


def append_mastery_log(concept_id: str, old: int, new: int, evidence: list[str], note: str = "") -> None:
    entry = (f"- {_dt.date.today().isoformat()} · **{concept_id}** {old}→{new} · "
             f"evidence: {', '.join(evidence) or '—'}" + (f" · {note}" if note else "") + "\n")
    if MASTERY_LOG.exists():
        MASTERY_LOG.write_text(MASTERY_LOG.read_text(encoding="utf-8") + entry, encoding="utf-8")
    else:
        MASTERY_LOG.write_text(
            "# Mastery log\n\nEvidence-backed mastery changes written by `master.py` "
            "(newest at bottom).\n\n" + entry, encoding="utf-8")
