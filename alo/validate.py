"""The spiral invariant — the rules that keep the curriculum depth-first, not a flat backlog.

A proposed unit is rejected (hard error) if it breaks ordering or the spiral; softer issues
are returned as warnings so they surface without blocking.
"""
from __future__ import annotations

from .store import VALID_TIERS

_REQUIRED = ("id", "title", "tier", "deliverable", "depth_objective", "mastery_check")


def validate_unit(unit: dict, graph_ids: set[str], covered: set[str],
                  existing_unit_ids: set[str]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Empty errors => safe to write."""
    errors: list[str] = []
    warnings: list[str] = []

    for field in _REQUIRED:
        if not str(unit.get(field, "")).strip():
            errors.append(f"missing required field: {field}")

    tier = unit.get("tier")
    if tier not in VALID_TIERS:
        errors.append(f"invalid tier {tier!r} (expected one of {VALID_TIERS})")

    introduces = unit.get("introduces") or []
    reinforces = unit.get("reinforces") or []
    prerequisites = unit.get("prerequisites") or []
    builds_on = unit.get("builds_on") or []

    # frontier: 1–3 known, not-yet-covered concepts
    if not 1 <= len(introduces) <= 3:
        errors.append(f"introduces must list 1–3 concepts (got {len(introduces)})")
    for cid in introduces:
        if cid not in graph_ids:
            errors.append(
                f"introduces unknown concept {cid!r} — not in concepts.yaml; new concepts "
                "are discover.py's job, not curate.py's"
            )
        elif cid in covered:
            warnings.append(f"introduces {cid!r} which is already covered — move it to 'reinforces'?")

    # the spiral: non-foundational units must reuse >=1 already-seen concept
    if tier and tier != "foundational":
        if not any(cid in covered for cid in reinforces):
            errors.append(
                "spiral invariant violated: a non-foundational unit must reinforce ≥1 "
                "already-covered concept (else it's breadth, not depth)"
            )
    for cid in reinforces:
        if cid not in graph_ids:
            errors.append(f"reinforces unknown concept {cid!r}")

    # ordering: prerequisites must already be introduced by a prior unit
    for cid in prerequisites:
        if cid not in graph_ids:
            errors.append(f"prerequisite unknown concept {cid!r}")
        elif cid not in covered:
            errors.append(f"prerequisite {cid!r} not yet introduced by any prior unit (roadmap out of order)")

    for uid in builds_on:
        if uid not in existing_unit_ids:
            warnings.append(f"builds_on references unknown unit {uid!r}")

    if unit.get("id") in existing_unit_ids:
        errors.append(f"unit id {unit.get('id')!r} already exists")

    return errors, warnings
