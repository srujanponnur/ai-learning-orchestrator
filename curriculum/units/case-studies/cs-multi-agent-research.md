---
id: cs-multi-agent-research
title: "Case study: orchestrator-worker research system (Anthropic)"
tier: advanced
created: 2026-06-05
status: todo
source: "Anthropic — How we built our multi-agent research system / Building effective agents"
source_urls:
  - https://www.anthropic.com/engineering/multi-agent-research-system
  - https://www.anthropic.com/engineering/building-effective-agents
prerequisites: [multi-agent, tracing]
introduces: [agentic-patterns]
reinforces: [multi-agent, context-engineering, tracing]
builds_on: [u07-multi-agent-mcp]
est_effort: "1–2 weeks"
---

**The real lesson:** a lead agent that spawns parallel subagents with **independent context windows**
beat single-agent by ~90% on research breadth — but the win comes from deliberate **orchestrator-worker**
design, tool-result handoffs, and context discipline, *not* from "more agents."

**Scoped deliverable:** a smaller orchestrator-worker researcher — 1 lead + N parallel scout subagents
over a fixed corpus/web — with explicit subagent prompts, result summarization into shared memory, and
traces showing the parallel speedup vs a single agent.

**Depth objective:** you can explain *why/when* parallel subagents help (independent context, breadth)
and the failure modes (cost blow-up, coordination overhead, lost context) — and design the handoffs.

**Mastery check:** given a task, you can decide single-vs-multi-agent and justify the topology with trace
evidence, not vibes.
