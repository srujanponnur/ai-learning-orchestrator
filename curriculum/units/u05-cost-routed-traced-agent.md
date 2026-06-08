---
id: u05-cost-routed-traced-agent
title: Cost-routed, traced agent
tier: advanced
created: 2026-06-05
status: todo
prerequisites: [agent-loop, llm-as-judge]
introduces: [prompt-caching, model-routing, tracing]
reinforces: [function-calling, agent-loop, llm-as-judge]
builds_on: [u02-tool-calling-agent, u04-eval-harness]
est_effort: "<= 1 week"
---

**Deliverable:** take the u02 agent and add prompt caching + a **cheap-drafts / strong-curates router**
gated by the u04 eval signal, with every step **traced**. Prove cost dropped without quality dropping.

**Depth objective:** you can measure and cut token cost (caching + routing) and **demonstrate** no quality
regression using the eval and the traces — not assert it.

**Mastery check:** you can read a trace and explain where the tokens/$ went, and justify each routing
decision against the eval.

**Resources:** Anthropic docs — prompt caching, model overview/pricing; a tracer (Langfuse or OTel).
