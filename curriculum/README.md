# AI-Engineering Curriculum (depth-first, spiral)

The **curated agenda** this repo's orchestrator maintains. Not a reading list — a *spiral*: each unit
deliberately **reuses** concepts from earlier units and adds a small frontier, so concepts reach **depth**
by reappearing in progressively harder contexts. Implementing each unit is the owner's separate effort.

- **Concept graph:** [`concepts.yaml`](concepts.yaml) — the DAG of topics, prerequisites, domains, and
  per-concept **mastery** (`0 unseen → 4 fluent`). A concept climbs to 3–4 only by being reused.
- **Units:** [`units/`](units/) — the buildable mini-projects, ordered foundational → capstone. Each
  carries `introduces` / `reinforces` / `builds_on`, a `depth_objective`, and a `mastery_check`.

## The seeded spine (one path through the graph)

```mermaid
flowchart TD
    u01["u01 · Structured extractor<br/><i>structured-outputs</i>"]
    u02["u02 · Tool-calling agent<br/><i>+function-calling, agent-loop</i>"]
    u03["u03 · RAG Q&A bot<br/><i>+retrieval</i>"]
    u04["u04 · Eval harness for u03<br/><i>+llm-as-judge</i>"]
    u05["u05 · Cost-routed, traced agent<br/><i>+caching, routing, tracing</i>"]
    u06["u06 · Context + memory<br/><i>+context-eng, memory</i>"]
    u07["u07 · Multi-agent + MCP<br/><i>+multi-agent, mcp</i>"]
    u08["u08 · Capstone: served + guardrailed<br/><i>+serving, guardrails</i>"]
    u01 --> u02 --> u03 --> u04 --> u05 --> u06 --> u07 --> u08
    u02 --> u05
    u06 --> u07
```

By u08, `structured-outputs` and `function-calling` have been **reused five+ times** in harder contexts —
that reuse is what builds depth, not a single pass.

## How to use it

1. Pick the lowest-numbered unit you haven't built. Build it (separately) to hit its `depth_objective`.
2. Confirm the `mastery_check` honestly. Then bump its concepts' mastery in `concepts.yaml`
   (later: `master.py <concept> <level>`).
3. Ask the curator for the next units (later: `curate.py "next"`) — it will respect prerequisites,
   schedule **reuse of concepts due for a depth bump**, add 1–3 frontier concepts, and raise the tier.

## What's unlocked *next* (frontier, not yet in the spine)

Concepts present in the graph but not yet covered by the 8-unit spine — natural targets once the spine's
prerequisites are met: `streaming`, `reranking`, `programmatic-tool-calling`, `regression-evals`,
`telemetry-cost`, `latency-scaling`, `finetuning-lora`. The curator weaves these in (and adds new frontier
nodes from a weekly trend scan) as later spiral steps.
