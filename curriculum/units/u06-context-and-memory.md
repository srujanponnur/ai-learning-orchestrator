---
id: u06-context-and-memory
title: Context engineering + memory
tier: advanced
created: 2026-06-05
status: todo
prerequisites: [agent-loop, prompt-caching]
introduces: [context-engineering, memory-state, token-budgeting]
reinforces: [agent-loop, prompt-caching, tracing]
builds_on: [u05-cost-routed-traced-agent]
est_effort: "<= 1 week"
---

**Deliverable:** a long-running version of the u05 agent that **compacts** context as it grows and
**persists memory** across sessions, on a token budget — surviving a multi-session task.

**Depth objective:** you can manage a context window deliberately and explain **when to reach for
compaction vs memory vs retrieval** — three different tools for three different problems.

**Mastery check:** given a task that blows the context window, you can choose compaction/memory/RAG
correctly and defend the choice on cost and fidelity.

**Resources:** Anthropic docs — compaction, context editing, memory tool; your u05 traces to see the win.
