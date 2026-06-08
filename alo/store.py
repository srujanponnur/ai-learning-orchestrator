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


def load_units(units_dir: Path = UNITS_DIR) -> list[dict]:
    """All units (including case-studies/), each as its frontmatter dict + `_path`."""
    units: list[dict] = []
    for md in sorted(units_dir.rglob("*.md")):
        if md.name.lower() == "readme.md":
            continue
        fm = _parse_frontmatter(md.read_text(encoding="utf-8"))
        if fm and fm.get("id"):
            fm["_path"] = str(md)
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


def render_unit_md(u: dict) -> str:
    created = u.get("created") or _dt.date.today().isoformat()
    resources = u.get("resources")
    if isinstance(resources, list):
        resources = "; ".join(str(r) for r in resources)
    frontmatter = (
        "---\n"
        f"id: {u['id']}\n"
        f"title: {u['title']}\n"
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
