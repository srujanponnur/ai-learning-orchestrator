"""master.py — evidence-gated mastery changes (the depth mechanic).

Ladder: 0 unseen · 1 introduced · 2 applied once · 3 reused in a harder context · 4 fluent/can-teach.
A concept only reaches 3–4 once it has been REINFORCED in >=2 distinct units that were actually BUILT
(status done) — proven by the curriculum, not self-declared.

Usage:
  python master.py <concept-id> <level> [--note "..."]   bump a concept's mastery (gated by evidence)
  python master.py --unit <unit-id> <status>             set a unit's status (e.g. done) = the evidence
  python master.py --status                              show mastery + what each concept needs next
"""
from __future__ import annotations

import sys

from alo import store

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DONE = store.DONE_STATES


def _evidence(cid: str, units: list[dict]):
    introducers = [u for u in units if cid in (u.get("introduces") or [])]
    reinforcers = [u for u in units if cid in (u.get("reinforces") or [])]
    touching = introducers + reinforcers
    built = [u for u in touching if str(u.get("status", "")).lower() in DONE]
    built_reinf = [u for u in reinforcers if str(u.get("status", "")).lower() in DONE]
    return introducers, reinforcers, touching, built, built_reinf


def gate(cid: str, level: int, units: list[dict], note: str) -> tuple[bool, str, list[str]]:
    """Is bumping `cid` to `level` earned by evidence? Returns (ok, reason, evidence_unit_ids)."""
    if not 0 <= level <= 4:
        return False, "level must be 0–4", []
    _, _, touching, built, built_reinf = _evidence(cid, units)
    evidence = sorted({u["id"] for u in built})
    if level == 0:
        return True, "", []
    if not touching:
        return False, f"{cid} is not introduced or reinforced by any unit yet", []
    if level >= 2 and not built:
        ids = [u["id"] for u in touching]
        return False, (f"reaching 'applied' (2) needs >=1 BUILT unit touching {cid}; "
                       f"units touching it: {ids} (none done) — mark one with "
                       f"`python master.py --unit <id> done`"), []
    if level >= 3 and len(built_reinf) < 2:
        return False, (f"depth gate: 3–4 needs {cid} REINFORCED in >=2 distinct BUILT units (the spiral); "
                       f"built reinforcers so far: {[u['id'] for u in built_reinf] or 'none'}"), evidence
    if level == 4 and not note:
        return False, ("level 4 (fluent/can-teach) also requires --note attesting how the mastery_check "
                       "passed, on top of the structural evidence"), evidence
    return True, "", evidence


def earned_level(cid: str, units: list[dict]) -> int:
    """Highest mastery a concept has *earned* from unit status (evidence-based; auto caps at 3)."""
    _, _, touching, built, built_reinf = _evidence(cid, units)
    if len(built_reinf) >= 2:
        return 3
    if built:
        return 2
    if any(str(u.get("status", "")).lower() in {"in_progress", "in-progress", "learning"}
           for u in touching):
        return 1
    return 0


def auto_advance(concepts: list[dict], units: list[dict]) -> list[tuple[str, int, int]]:
    """Bump each concept up to the level its built units justify. Returns [(cid, old, new)]."""
    changes: list[tuple[str, int, int]] = []
    for c in concepts:
        cur = c.get("mastery", 0)
        earned = earned_level(c["id"], units)
        if earned > cur:
            store.set_mastery(c["id"], earned)
            _, _, _, built, _ = _evidence(c["id"], units)
            store.append_mastery_log(c["id"], cur, earned,
                                     sorted({u["id"] for u in built}), "auto from Notion status")
            changes.append((c["id"], cur, earned))
    return changes


def cmd_status(units: list[dict], concepts: list[dict]) -> None:
    print(f"{'concept':<32}{'mastery':^9}  next")
    print("-" * 78)
    for c in concepts:
        cid, m = c["id"], c.get("mastery", 0)
        if m >= 4:
            nxt = "maxed ✓"
        else:
            ok, reason, _ = gate(cid, m + 1, units, note="x")
            nxt = f"→ {m + 1} ready" if ok else reason.split(";")[0]
        print(f"{cid:<32}{m:^9}  {nxt}")


def main() -> int:
    args = sys.argv[1:]
    concepts = store.load_concepts()
    units = store.load_units()

    if not args or args[0] == "--status":
        cmd_status(units, concepts)
        return 0

    if args[0] == "--unit":
        if len(args) < 3:
            print('usage: python master.py --unit <unit-id> <status>')
            return 2
        uid, status = args[1], args[2]
        try:
            old = store.set_unit_status(uid, status)
        except KeyError as e:
            print(f"✗ {e}")
            return 1
        print(f"✓ unit {uid}: status {old} → {status}")
        return 0

    cid = args[0]
    try:
        level = int(args[1])
    except (IndexError, ValueError):
        print('usage: python master.py <concept-id> <level 0-4> [--note "..."]')
        return 2
    note = ""
    if "--note" in args and args.index("--note") + 1 < len(args):
        note = args[args.index("--note") + 1]

    if cid not in {c["id"] for c in concepts}:
        print(f"✗ unknown concept {cid!r}")
        return 1

    ok, reason, evidence = gate(cid, level, units, note)
    if not ok:
        print(f"✗ refused: {reason}")
        return 1
    old = store.set_mastery(cid, level)
    store.append_mastery_log(cid, old, level, evidence, note)
    print(f"✓ {cid}: mastery {old} → {level}  (evidence: {', '.join(evidence) or '—'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
