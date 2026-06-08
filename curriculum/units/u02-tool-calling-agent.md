---
id: u02-tool-calling-agent
title: Tool-calling mini-agent
tier: foundational
created: 2026-06-05
status: todo
prerequisites: [structured-outputs]
introduces: [function-calling, agent-loop, workflow-vs-agent]
reinforces: [structured-outputs]
builds_on: [u01-structured-extractor]
est_effort: "<= 1 week"
---

**Deliverable:** an agent loop that calls 2–3 tools (e.g. a calculator + a web fetch) and iterates until
the task is done, reusing the typed-output discipline from u01 for each tool's I/O.

**Depth objective:** you can implement the tool-use loop *by hand* (request → tool_use → result → repeat →
stop), and articulate **when a fixed workflow beats an agent** (and the cost of getting that wrong).

**Mastery check:** you can trace one full tool call end-to-end and explain the loop's stop condition; you
can take a task and decide agent-vs-workflow with a reason.

**Resources:** Anthropic docs — tool use / agent loop; `shared/agent-design.md` patterns (tier choice).
