"""discover.py — the discovery swarm: keep the curriculum current, automatically.

Fans out N scout agents (Claude Agent SDK + WebSearch/WebFetch, on the Max subscription) seeded by
angle from sources.md, dedups their candidate concepts/sources against the existing graph, runs an
adversarial judge to keep only what's real / novel / relevant (kills hype), then appends survivors to
concepts.yaml and sources.md. Idempotent and append-only; schedule it (e.g. weekly).

Usage:
  python discover.py [--dry-run] [--scouts N]
"""
from __future__ import annotations

import asyncio
import json
import re
import sys

import anyio

from alo import agent, store

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCOUT_SYSTEM = (
    "You are a scout for an AI-engineering curriculum. Using web search/fetch, find GENUINELY NEW, real, "
    "and relevant concepts/techniques/tools/protocols for your assigned angle — things a serious AI engineer "
    "should learn. Prefer the last ~1-2 months. Be conservative: only include an item you can back with a real, "
    "citable source URL you actually found, and that is NOT already in the KNOWN list. Output ONLY a JSON object "
    "inside a ```json fence:\n"
    '{"concepts":[{"id":"kebab-id","name":"Short name","domain":"<one of the allowed domains>",'
    '"tier":"foundational|intermediate|advanced","prerequisites":["existing-concept-id"],'
    '"why":"one line","source_url":"https://..."}],'
    '"sources":[{"name":"Source name","url":"https://...","note":"one line"}]}\n'
    "Choose domain only from the allowed list; choose prerequisites only from KNOWN ids; keep ids kebab-case and "
    "specific (not vendor brands). If nothing new, return empty arrays. No prose outside the fence."
)

SCOUTS = [
    ("recency", "the last 1-2 months of AI engineering broadly: new techniques, tools, or patterns"),
    ("agents", "agent frameworks, orchestration patterns, and agent protocols (MCP, A2A, AG-UI, ...)"),
    ("serving", "LLM serving, inference optimization, quantization, and GPU efficiency"),
    ("evals-ops", "evaluation, observability, guardrails, and production reliability for LLM apps"),
]

VERIFY_SYSTEM = (
    "You are an adversarial reviewer for an AI-engineering curriculum. For each candidate concept decide if it is "
    "REAL (not hype/marketing), NOVEL (a distinct learnable concept, not a vendor brand or trivial rename), and "
    "RELEVANT to learning AI engineering. Default to REJECT on any doubt. You may fetch a source to check. Output "
    'ONLY a JSON object in a ```json fence: {"keep":["id",...],"reject":[{"id":"...","reason":"..."}]}.'
)


def _extract_json(text: str):
    m = re.search(r"```json\s*(.*?)```", text, re.S) or re.search(r"```\s*(\{.*\}|\[.*\])\s*```", text, re.S)
    blob = m.group(1) if m else None
    if blob is None:
        s, e = text.find("{"), text.rfind("}")
        blob = text[s:e + 1] if s != -1 and e > s else None
    if not blob:
        return None
    try:
        return json.loads(blob)
    except json.JSONDecodeError:
        return None


def main() -> int:
    args = sys.argv[1:]
    dry = "--dry-run" in args
    n_scouts = int(args[args.index("--scouts") + 1]) if "--scouts" in args else len(SCOUTS)

    concepts = store.load_concepts()
    known_ids = {c["id"] for c in concepts}
    known_names = {c["name"].lower() for c in concepts}
    domains = sorted({c["domain"] for c in concepts})
    sources_text = store.SOURCES_MD.read_text(encoding="utf-8") if store.SOURCES_MD.exists() else ""

    base_ctx = (f"KNOWN concept ids ({len(known_ids)}): {', '.join(sorted(known_ids))}\n\n"
                f"Allowed domains: {', '.join(domains)}\n")

    print(f"discovery: {n_scouts} scouts · {len(known_ids)} known concepts{' · DRY RUN' if dry else ''}\n")

    # 1-2. fan out scouts CONCURRENTLY — each query() is its own claude subprocess, so they
    #       research in parallel; a semaphore caps how many hit the subscription at once.
    async def _scout(label: str, angle: str, sem: asyncio.Semaphore):
        prompt = base_ctx + f"\nYour angle: {angle}\nFind new concepts + sources for this angle."
        async with sem:
            print(f"scout[{label}] researching: {angle} ...")
            raw = await agent.run_research(prompt, SCOUT_SYSTEM, max_turns=24)
        return label, _extract_json(raw) or {}

    async def _run_scouts():
        sem = asyncio.Semaphore(min(4, n_scouts))
        return await asyncio.gather(
            *(_scout(label, angle, sem) for label, angle in SCOUTS[:n_scouts]),
            return_exceptions=True,   # one scout's crash must not kill the batch
        )

    # merge + dedup AFTER the barrier (sequential here → no locks needed)
    candidates: dict[str, dict] = {}
    new_sources: dict[str, dict] = {}
    for result in anyio.run(_run_scouts):
        if isinstance(result, Exception):
            print(f"  scout failed: {result}")
            continue
        label, data = result
        cs, ss = data.get("concepts", []) or [], data.get("sources", []) or []
        for c in cs:
            cid = (c.get("id") or "").strip()
            if cid and cid not in known_ids and cid not in candidates and c.get("name", "").lower() not in known_names:
                candidates[cid] = c
        for s in ss:
            url = (s.get("url") or "").strip()
            if url and url not in sources_text and url not in new_sources:
                new_sources[url] = s
        print(f"  scout[{label}] returned {len(cs)} concepts, {len(ss)} sources")

    print(f"\nafter dedup: {len(candidates)} new concept candidates, {len(new_sources)} new sources.")
    if not candidates and not new_sources:
        print("nothing new — done.")
        return 0

    # 3. adversarial verify (concepts only; sources are low-risk)
    kept = candidates
    if candidates:
        listing = "\n".join(
            f"- {cid} ({c.get('domain')}/{c.get('tier')}): {c.get('name')} — {c.get('why', '')} "
            f"[src: {c.get('source_url', '')}]" for cid, c in candidates.items())
        try:
            vraw = agent.run_research_sync("Candidates:\n" + listing, VERIFY_SYSTEM,
                                           allowed_tools=("WebFetch",), max_turns=12)
            verdict = _extract_json(vraw) or {}
            keep_ids = set(verdict.get("keep", []) or [])
            if verdict:  # only filter if the judge actually returned a verdict
                kept = {cid: c for cid, c in candidates.items() if cid in keep_ids}
            for r in verdict.get("reject", []) or []:
                print(f"  ✗ rejected {r.get('id')}: {r.get('reason', '')}")
        except Exception as exc:
            print(f"  verify step failed ({exc}); keeping candidates unverified")
    print(f"{len(kept)} concept(s) survived verification.\n")

    # 4. procure (append-only)
    added_c = added_s = 0
    for cid, c in kept.items():
        prereqs = [p for p in (c.get("prerequisites") or []) if p in known_ids]
        rec = {"id": cid, "name": c.get("name", cid), "domain": c.get("domain", "misc"),
               "tier": c.get("tier", "intermediate"), "prerequisites": prereqs}
        if dry:
            print(f"  [dry] concept {cid} [{rec['domain']}/{rec['tier']}] prereqs={prereqs}  ({c.get('source_url','')})")
        elif store.append_concept(rec):
            added_c += 1
            print(f"  ✓ concept {cid} [{rec['domain']}/{rec['tier']}]")
    for url, s in new_sources.items():
        if dry:
            print(f"  [dry] source {s.get('name')} <{url}>")
        elif store.append_source(s.get("name", url), url, s.get("note", "")):
            added_s += 1
            print(f"  ✓ source {s.get('name')}")

    print(f"\ndone: {'(dry run) ' if dry else ''}{added_c} concepts, {added_s} sources added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
