"""curate.py — propose the next spiral unit(s) for the AI-engineering curriculum.

Usage:
    python curate.py [next | <domain>] [--dry-run] [--model <id>]

Reads the concept graph + existing units, asks the Claude curator (Agent SDK, Max
subscription) for 1–3 next units that honor the spiral invariant, validates them, and
writes the survivors to curriculum/units/. `--dry-run` validates without writing.
"""
from __future__ import annotations

import json
import re
import sys

from alo import agent, store
from alo.validate import validate_unit

# Windows consoles default to cp1252; ensure our status glyphs (✓ ✗ ⚠) encode.
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

SYSTEM = """You are a meticulous AI-engineering curriculum curator. You decide WHAT to learn \
and in WHAT ORDER to reach real DEPTH in AI engineering — you do NOT implement anything.

Depth comes from a SPIRAL, not a checklist: each new unit (a ~1-week mini-project) reuses \
concepts from earlier units in a harder context and adds a small frontier.

Hard rules for every unit you propose:
- `introduces`: 1–3 concepts that EXIST in the provided graph and are NOT yet covered (the frontier).
- `reinforces`: unless tier is 'foundational', MUST include ≥1 ALREADY-covered concept (the spiral). \
Never propose an all-new unit — that is breadth, not depth.
- `prerequisites`: every one must ALREADY be covered (introduced by a prior unit) so the order holds.
- `builds_on`: reference a prior unit id where natural; raise the tier over time toward a capstone.
- Scope ≤ ~1 week. Give a concrete `depth_objective` (what you can DO afterwards) and a `mastery_check` \
(how you know you understand it — derive/critique/extend it without looking it up).
- Use ONLY concept ids from the provided graph. If a needed concept seems missing, leave it out — \
discovery of new concepts is a separate job, not yours.

Output ONLY a JSON array (inside a ```json fence) of 1–3 unit objects, in build order. Shape:
{"id":"uNN-kebab-title","title":"...","tier":"foundational|intermediate|advanced|capstone",
 "prerequisites":[...],"introduces":[...],"reinforces":[...],"builds_on":[...],
 "est_effort":"<= 1 week","deliverable":"...","depth_objective":"...","mastery_check":"...",
 "resources":["..."]}
Number ids sequentially after the highest existing uNN. Emit no prose outside the JSON fence."""


def build_prompt(target: str, concepts: list[dict], units: list[dict], covered: set[str]) -> str:
    by_domain: dict[str, list[str]] = {}
    lines_graph = []
    for c in concepts:
        mark = "COVERED" if c["id"] in covered else "uncovered"
        lines_graph.append(
            f"- {c['id']} [{c['domain']}/{c['tier']}] m{c.get('mastery', 0)} "
            f"prereqs={c.get('prerequisites') or []} -> {mark}"
        )
        if c["id"] not in covered:
            by_domain.setdefault(c["domain"], []).append(c["id"])

    lines_units = [
        f"- {u['id']} [{u.get('tier')}] introduces={u.get('introduces') or []} "
        f"reinforces={u.get('reinforces') or []} builds_on={u.get('builds_on') or []}"
        for u in units
    ]
    frontier = "\n".join(f"  {dom}: {', '.join(ids)}" for dom, ids in sorted(by_domain.items()))
    due = sorted(c["id"] for c in concepts if c["id"] in covered and c.get("mastery", 0) < 3)
    highest = store.highest_unit_number(units)

    if target == "next":
        ask = ("Propose the next 1–3 units that best advance the spiral from the current state, "
               "preferring to reinforce concepts listed as 'due for depth'.")
    else:
        ask = (f"Bias the next 1–3 units toward the {target!r} domain while honoring every spiral "
               "rule (prereqs covered, reinforce prior concepts, sensible tier progression).")

    return f"""{ask}

EXISTING UNITS (in build order):
{chr(10).join(lines_units) or '(none yet)'}

CONCEPT GRAPH (id [domain/tier] prereqs -> covered?):
{chr(10).join(lines_graph)}

COVERED concepts: {', '.join(sorted(covered)) or '(none)'}

DUE FOR DEPTH (covered, mastery<3 — reinforce these to climb the ladder): {', '.join(due) or '(none)'}

FRONTIER (uncovered) concepts by domain:
{frontier or '  (all covered)'}

Highest existing unit number: u{highest:02d}. Number new ids from u{highest + 1:02d} upward.
"""


def extract_units(text: str) -> list[dict]:
    m = re.search(r"```json\s*(.*?)```", text, re.S) or re.search(r"```\s*(\[.*?\])\s*```", text, re.S)
    blob = m.group(1) if m else None
    if blob is None:
        start, end = text.find("["), text.rfind("]")
        blob = text[start:end + 1] if start != -1 and end > start else None
    if not blob:
        raise ValueError("no JSON array found in the model output:\n" + text[:500])
    data = json.loads(blob)
    if not isinstance(data, list):
        raise ValueError("expected a JSON array of units")
    return data


def propose_and_write(target: str = "next", model: str | None = None,
                      dry_run: bool = False) -> list[dict]:
    """Propose 1–3 spiral units for `target`, validate, write survivors. Returns accepted units."""
    concepts = store.load_concepts()
    graph_ids = set(store.concepts_by_id(concepts))
    units = store.load_units()
    covered = store.covered_concepts(units)
    existing_ids = {u["id"] for u in units}

    print(f"curating target={target!r} · {len(concepts)} concepts · {len(units)} units "
          f"· {len(covered)} covered{' · DRY RUN' if dry_run else ''}")

    prompt = build_prompt(target, concepts, units, covered)
    raw = agent.run_text_sync(prompt, SYSTEM, model=model)
    proposed = extract_units(raw)
    print(f"curator proposed {len(proposed)} unit(s).")

    accepted: list[dict] = []
    for u in proposed:
        uid = u.get("id", "<no id>")
        errors, warnings = validate_unit(u, graph_ids, covered, existing_ids)
        if errors:
            print(f"✗ {uid} — REJECTED: {'; '.join(errors)}")
            continue
        for w in warnings:
            print(f"  ⚠ {uid}: {w}")
        if not dry_run:
            store.write_unit(u)
        # let later units in this batch build on the ones just accepted
        covered.update((u.get("introduces") or []) + (u.get("reinforces") or []))
        existing_ids.add(uid)
        accepted.append(u)
        print(f"✓ {uid} — '{u.get('title')}' [{u.get('tier')}]{' (dry)' if dry_run else ''}")

    print(f"done: {len(accepted)}/{len(proposed)} accepted.")
    return accepted


def main() -> int:
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    model = None
    if "--model" in args and args.index("--model") + 1 < len(args):
        model = args[args.index("--model") + 1]
    target = next((a for a in args if not a.startswith("--") and a != model), "next")
    accepted = propose_and_write(target, model=model, dry_run=dry_run)
    return 0 if accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
