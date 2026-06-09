"""sync.py — mirror curriculum units into a Notion database (idempotent, keyed on UnitId).

Usage: python sync.py
Reads NOTION_TOKEN from .env, ensures the units database exists (creating it under an accessible
page on first run and caching the id in .notion.json), then upserts every unit. md stays the
source of truth; Notion is the mirror.
"""
from __future__ import annotations

import sys

from alo import env, notion, store

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> int:
    token = env.notion_token()
    if not token or token == "ntn_your_secret_here":
        print("✗ no real NOTION_TOKEN found — put it in .env as: NOTION_TOKEN=ntn_...")
        return 1

    units = store.load_units()
    concepts = store.load_concepts()
    print(f"syncing {len(units)} units to Notion ...")
    try:
        db_id, note = notion.ensure_units_db(token)
        print(f"  {note}")
        notion.write_legend(token, concepts, units)
        print("  legend page updated")
        created = updated = bodies = 0
        for u in units:
            action, page_id = notion.upsert_unit(token, db_id, u)
            if notion.write_body_if_empty(token, page_id, u):
                bodies += 1
            created += action == "created"
            updated += action == "updated"
            print(f"  ✓ {u['id']} ({action})")
    except notion.NotionError as e:
        print(f"✗ {e}")
        return 1

    print(f"done: {created} created, {updated} updated, {bodies} page-bodies written · cached in .notion.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
