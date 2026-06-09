"""run_cycle.py — the automated daily cycle. Notion is the cockpit; this runs unattended.

1. Pull each unit's Status from Notion → local md (Notion is the source of truth for progress).
2. Auto-advance concept mastery from built units (evidence-gated).
3. Teach-me: for units with the "Teach me" box ticked, write a learning brief into the page, untick.
4. Top up: if no 'todo' units remain, curate the next spiral units.
5. Push everything back to Notion (properties, page bodies, legend).

Runs on the Max subscription (teach-me calls Claude). No manual steps — schedule it daily.
"""
from __future__ import annotations

import sys

import curate
import master
from alo import agent, env, notion, store

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

TEACH_SYSTEM = (
    "You are a learning coach. Given ONE curriculum unit, write a SHORT orientation on how to learn it "
    "— point to material and sequence it; do NOT teach the whole topic. Minimal markdown: a 2–3 sentence "
    "intro, then '### Start here' with 3–5 ordered bullets (what to read/do, naming the listed resources), "
    "then '### Watch out for' with 2–3 pitfall bullets. Under ~220 words."
)


def teach_brief(u: dict) -> str:
    prompt = (f"Unit: {u.get('title')}\nTier: {u.get('tier')}\n"
              f"Introduces: {u.get('introduces')}\nReinforces: {u.get('reinforces')}\n"
              f"Depth objective: {u.get('depth_objective', '')}\n"
              f"Resources: {u.get('resources', '')}\n\nWrite the orientation.")
    return agent.run_text_sync(prompt, TEACH_SYSTEM)


def main() -> int:
    token = env.notion_token()
    if not token or token == "ntn_your_secret_here":
        print("✗ no real NOTION_TOKEN in .env")
        return 1

    db_id, _ = notion.ensure_units_db(token)
    rows = notion.fetch_units(token, db_id)
    rows_by_id = {r["unit_id"]: r for r in rows if r["unit_id"]}

    # 1. Notion Status -> local md (Notion owns progress)
    pulled = []
    for u in store.load_units():
        r = rows_by_id.get(u["id"])
        if r and r["status"] and r["status"] != str(u.get("status", "todo")):
            store.set_unit_status(u["id"], r["status"])
            pulled.append(f"{u['id']}: {u.get('status', 'todo')}→{r['status']}")
    print("status pulled:", ", ".join(pulled) if pulled else "(no changes)")

    # 2. auto-advance mastery from built units
    units = store.load_units()
    concepts = store.load_concepts()
    bumps = master.auto_advance(concepts, units)
    print("mastery advanced:", ", ".join(f"{c} {a}→{b}" for c, a, b in bumps) if bumps else "(none)")

    # 3. teach-me (checkbox-triggered)
    taught = 0
    for r in rows:
        if not r.get("teach_me"):
            continue
        u = next((x for x in units if x["id"] == r["unit_id"]), None)
        if not u:
            continue
        try:
            brief = teach_brief(u)
            notion.append_blocks(token, r["page_id"],
                                 notion.markdown_to_blocks("### 🧭 How to learn this\n" + brief))
            notion.set_teach_me(token, r["page_id"], False)
            taught += 1
            print(f"taught: {r['unit_id']}")
        except Exception as exc:  # an LLM/Notion hiccup mustn't abort the whole cycle
            print(f"  teach-me failed for {r['unit_id']}: {exc}")
    print(f"teach-me: {taught} unit(s) written")

    # 4. top up the roadmap only if nothing is left to build
    todo = [u for u in units if str(u.get("status", "todo")).lower() == "todo"]
    if not todo:
        print("no 'todo' units left — curating the next ones")
        try:
            curate.propose_and_write("next")
            units = store.load_units()
        except Exception as exc:
            print(f"  curate failed: {exc}")
    else:
        print(f"{len(todo)} 'todo' unit(s) remain — not curating new ones")

    # 5. push everything back to Notion
    notion.write_legend(token, store.load_concepts(), units)
    for u in units:
        _, page_id = notion.upsert_unit(token, db_id, u)
        notion.write_body_if_empty(token, page_id, u)
    print(f"pushed {len(units)} units + legend. cycle complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
