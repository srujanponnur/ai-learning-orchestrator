---
id: u07-multi-agent-mcp
title: Multi-agent research + critic over MCP
tier: advanced
created: 2026-06-05
status: todo
prerequisites: [agent-loop, tracing, tool-design]
introduces: [multi-agent, mcp, tool-design]
reinforces: [tracing, llm-as-judge, model-routing]
builds_on: [u05-cost-routed-traced-agent, u06-context-and-memory]
est_effort: "1–2 weeks"
---

**Deliverable:** a coordinator that fans out research **subagents** plus a **critic** that adversarially
verifies their findings before they're accepted, with tools exposed via an **MCP** server you design.

**Depth objective:** you can design a multi-agent topology and **justify it over a single agent** — and
name the failure modes (cost blow-up, lost context between agents, false consensus).

**Mastery check:** you can state, for a given task, whether multi-agent earns its keep or just adds cost
and latency — with the trace/eval evidence to back it.

**Resources:** Anthropic docs — subagents, MCP; reuse u05 routing + u06 memory inside the agents.
