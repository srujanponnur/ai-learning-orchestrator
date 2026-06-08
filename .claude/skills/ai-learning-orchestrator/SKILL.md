---
name: ai-learning-orchestrator
description: Work on Project 1 — a curation engine (NOT an implementer) that builds a depth-first, spiral AI-engineering curriculum: a concept graph plus an ordered sequence of mini-projects where each one deliberately reuses earlier-learned concepts to scaffold toward harder builds, with mastery tracked per concept and synced to Notion. The curator **self-maintains via the Claude Agent SDK** — its own agents do live web discovery (web_search/web_fetch + subagents) on a schedule to keep concepts and sources current; any seeded files are a starting snapshot, not hand-maintained. Use when designing, extending, or running the curriculum curator.
---

# Project 1 — AI Learning Orchestrator (spiral-curriculum curator)

**What it is:** a **curation engine**. It designs *what to learn and in what order* so the owner reaches
**depth** in AI engineering — latest frameworks, tool chaining, orchestration, evals, serving, the lot.
It does **NOT** implement the mini-projects; the owner builds those separately. Its product is the agenda.

**The core idea — depth via a spiral, not a checklist.** Depth comes from **reusing a concept in
progressively harder contexts**, not from meeting it once. So the curator maintains a *learning graph*
and proposes mini-projects where **each new one deliberately reuses concepts from earlier units** and
adds a small frontier — compounding toward advanced / capstone builds.

**Stack:** Python + Claude Agent SDK · Notion (catalog) · Mermaid (graph render).

## The model (what makes it depth-first + spiral)

**Two node types:**

- **Concept** — an AI-eng topic (e.g. tool/function calling, agent eval, prompt caching, retrieval,
  multi-agent orchestration, cost routing, tracing, guardrails, MCP, memory/state, structured outputs,
  context engineering, serving/quantization, fine-tuning). Has `domain`, `tier`, `prerequisites` (other
  concepts), and a **mastery level**.
- **Unit** (a mini-project / use-case) — a buildable thing that `introduces` 1–3 new concepts and
  **`reinforces` ≥1 already-seen concept** (the spiral), at a difficulty that compounds, ideally
  `builds_on` a prior unit's output.

**Mastery ladder (depth):** `0 unseen → 1 introduced → 2 applied once → 3 reused in a harder context →
4 fluent / can-teach`. A concept only climbs to 3–4 by **reappearing in later units**, so the curator
deliberately schedules reuse. **Never mark "deep" on first contact.** **Evidence-gated:** a bump is earned
by *evidence* — the unit's deliverable exists and its `mastery_check` passed — not self-report; `master.py`
records that evidence and refuses an unbacked jump to 3–4.

**Unit schema:**

```json
{
  "id": "u07-rag-with-eval",
  "title": "...",
  "tier": "foundational | intermediate | advanced | capstone",
  "prerequisites": ["retrieval-basics", "structured-outputs"],   // must be >= applied
  "introduces": ["llm-as-judge", "eval-harness"],                // frontier (1-3)
  "reinforces": ["tool-calling", "prompt-caching"],              // deliberate reuse (>=1) — the spiral
  "builds_on": ["u03-rag-bot"],                                  // composes earlier work
  "depth_objective": "by the end you can design the eval set and argue the metric — not just wire it",
  "mastery_check": "you understand it when you can <derive/critique/extend> without looking it up",
  "deliverable": "...", "est_effort": "<= 1 week", "resources": ["..."]
}
```

## Landscape coverage (so curation is intentional, not random)

Track breadth *and* depth across AI-eng domains: **orchestration** (Agent SDK, LangGraph,
workflow-vs-agent) · **tool use & chaining** (function calling, programmatic tool calling, MCP) ·
**retrieval / RAG** · **memory & state** · **evals** (LLM-as-judge, datasets, regression) · **cost**
(caching, model routing, token budgets) · **serving / hosting** (quantization, latency, scaling) ·
**observability** (tracing, telemetry) · **multi-agent & agent protocols** (MCP, A2A, ACP, AG-UI) ·
**model gateways** (routing, fallbacks, limits) · **multimodal** (vision/audio) · **reasoning/thinking
modes** · **guardrails / safety** (prompt-injection defense, red-teaming, PII) · **structured
outputs & streaming** · **retrieval depth** (hybrid, contextual, agentic, GraphRAG) · **context engineering** (compaction,
windowing) · **fine-tuning** (LoRA, preference tuning, distillation, when-not-to).
The curator reports coverage and the deepest-vs-thinnest domains. The full, current taxonomy lives in
[`curriculum/concepts.yaml`](../../../curriculum/concepts.yaml); the **discovery swarm** (below) keeps it growing.

## What the curator does (the algorithm)

1. Load the concept graph + mastery + prior units (md = source of truth; Notion = dashboard).
2. Propose the **next** unit(s) such that: every `prerequisite` is ≥ *applied*; it `reinforces` 1–2
   concepts **due for a depth bump** (spaced/spiral); it `introduces` 1–3 frontier concepts; it **raises
   the tier**; and it `builds_on` a prior unit where natural.
3. Emit an **ordered roadmap** (a path through the graph) — not a flat backlog.
4. After the owner implements a unit (separately), bump that unit's concepts' mastery → unlocks the next step.

## Discovery swarm — keep the knowledge base current (core, not a stretch)

Frameworks, protocols, and best practices move weekly, so discovery is a **first-class subsystem built
into the curator itself** — implemented with the **Claude Agent SDK**: the script's *own* agents use
`web_search` / `web_fetch` and subagents to do the research **at runtime**, and the job is **scheduled to
run repeatedly and unattended**. The pre-seeded [`sources.md`](../../../curriculum/sources.md) and
case-study units are only a **starting snapshot** the script then maintains and grows on its own — they are
**not** meant to be hand-curated (by a human or by Claude in chat) going forward. Each run is a
**fan-out of N scout agents** (a "team of N" — scale to budget) that find *and procure* new material:

1. **Seed** from [`curriculum/sources.md`](../../../curriculum/sources.md) (engineering blogs, case-study
   DBs, newsletters, papers, protocol trackers) plus open WebSearch.
2. **Fan out** scouts by angle — by-source (each owns a few feeds), by-domain (one per landscape domain),
   by-recency (last 7/30 days), by-protocol/framework. Each returns candidate concepts + links + a one-line
   "why it matters".
3. **Dedup** candidates against the existing graph (`concepts.yaml`) and `sources.md`.
4. **Verify (adversarial):** a judge pass keeps only what's *real, novel, and relevant* — kills
   hype/marketing. Default to reject on doubt.
5. **Procure:** add survivors as new concept nodes (prerequisites wired into the DAG), append new sources,
   and **mine standout posts into case-study units** (below). Then re-spiral: slot new concepts into upcoming units.
6. **Cadence & convergence:** weekly run; loop-until-dry (stop after K rounds surface nothing new).

**Implemented in code, run unattended — this is the whole point.** The loop is **Claude Agent SDK** code
(subagent fan-out + `web_search`/`web_fetch`), not a human (or a chat session) fetching sources. It is
**scheduled to run periodically** — Windows **Task Scheduler** or cron firing `discover.py` on a cadence
(e.g. daily quick scan + weekly deep scan), or a long-running scheduler. It authenticates via the **Max
subscription** (Agent SDK — no `ANTHROPIC_API_KEY`), so recurring runs cost no API credits. Every run is
idempotent: it appends to `concepts.yaml` / `sources.md` / `units/case-studies/`, syncs Notion, and logs
exactly what it added so you can review the diff.

## Real-world case-study mining (learn how the best teams ship)

Turn real engineering blogs (Anthropic, OpenAI, Google, Uber, DoorDash, LinkedIn, Netflix, Meta…) into
**scoped, solvable** units in `curriculum/units/case-studies/`. Each cites the source, scopes a slice
**rebuildable in ≤1–2 weeks at smaller scale** (extract the lesson, not the whole production system), and
ties into the graph via `introduces`/`reinforces`. Seeded examples: orchestrator-worker research
(Anthropic), GenAI gateway (Uber), contextual retrieval (Anthropic), sim+eval flywheel (DoorDash).

## MVP — the thinnest loop that proves it

Resist building all the tooling at once. The smallest slice that *proves the idea* is just:

1. **`concepts.yaml`** — the seeded concept graph (already in the repo).
2. **`curate.py "<domain | 'next'>"`** — reads the graph + existing units, proposes the next 1–3 **spiral
   units** (schema above) honoring prereqs + deliberate reuse + a tier bump, validates the spiral invariant,
   and writes md to `curriculum/units/`.
3. **Notion sync** (via the `notion` MCP) — mirror units (and optionally concepts) to a dashboard DB.

Run that, judge whether the proposed units are actually good, iterate the *prompt* — that's the learning.
Everything below is an upgrade, not the MVP.

## v2 — self-maintaining (the built-in discovery)

4. **`discover.py`** — the discovery swarm in code: Claude Agent SDK subagents with `web_search` /
   `web_fetch` seeded from `sources.md` → dedup vs `concepts.yaml` → adversarial verify → **write** new
   concepts / sources / case-study units. Start with ~3–5 scouts.
5. **Schedule it** — Windows Task Scheduler / cron fires `discover.py` periodically, unattended (on the Max
   subscription, no API spend). This is what makes the curriculum self-maintaining.

## Supporting tools

- **`graph.py`** — render the concept graph as **Mermaid** + a coverage/mastery report (deep vs thin, unlocked-next).
- **`master.py <concept> <level>`** — bump mastery *with evidence* (see Conventions); re-opens the next spiral step.
- **Notion schema** — two related DBs: **Concepts** (Domain, Tier, Mastery, Prereqs↩) and **Units** (Tier,
  Status, Introduces↩, Reinforces↩, BuildsOn↩, DepthObjective, MasteryCheck). The relations *are* the graph.

## Stretch

- (Discovery swarm + case-study mining are now **core** above — no longer a stretch.)
- Difficulty/cost routing: cheap model drafts candidate units, stronger model curates + checks the spiral.
- Render the roadmap + concept graph as Mermaid; export the "what unlocks next" frontier.
- A "teach me" mode that turns a unit's `mastery_check` into a guided self-quiz.

## Conventions (the invariants that keep it depth-first)

- **Curate, don't implement.** This project produces the agenda + understanding checks; the owner builds
  each mini-project separately.
- **Spiral invariant:** every non-foundational unit MUST `reinforce` ≥1 prior concept (ideally `builds_on`
  a prior unit). Reject all-new units — that's breadth, not depth.
- **Depth gate (evidence-based):** a concept reaches mastery 3–4 only after (a) it's been reinforced in ≥2
  distinct later units **and** (b) those units were actually built and their `mastery_check`s passed with
  recorded evidence — never self-declared.
- **Scoped:** each unit ≤ ~1 week and carries a concrete `depth_objective` + `mastery_check`.
- Markdown first, then Notion sync — never the reverse. Idempotent.
- **Definition of done (MVP):** `curate.py "next"` emits spiral units that respect prereqs and reuse prior
  concepts, written to md and mirrored to Notion.
- **Definition of done (v2):** `discover.py` runs the SDK fan-out and writes ≥1 verified new
  concept/source/case-study; a scheduled task (Task Scheduler/cron) fires it periodically, unattended.

## Additions worth building (beyond MVP)

- **Self-judge curation:** an LLM-as-judge pass that rejects units violating the spiral invariant (no
  reuse) or whose `mastery_check` is surface-level — keeps the curriculum honest. (Cheap eval practice.)
- **Gap & staleness analysis:** surface domains gone thin and concepts overdue for reuse (spaced
  repetition), and bias the next units toward them.
- (Plus the cross-cutting practices in this repo's [CLAUDE.md](../../../CLAUDE.md): eval loop, cost
  telemetry, tracing, ship-it.)
