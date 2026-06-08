---
id: u01-structured-extractor
title: Structured extractor
tier: foundational
created: 2026-06-05
status: todo
prerequisites: []
introduces: [prompt-fundamentals, structured-outputs]
reinforces: []
builds_on: []
est_effort: "<= 3 days"
---

**Deliverable:** a CLI that turns messy text (an email, a job post) into **schema-validated typed JSON**,
rejecting/repairing outputs that don't conform.

**Depth objective:** you can design a schema that *constrains* the model (enums, required fields, strict
mode) and explain *why* validation beats string-parsing — and predict where extraction will fail.

**Mastery check:** given a brand-new extraction task, you can write the schema + validation and name two
likely failure modes before running it.

**Resources:** Anthropic docs — structured outputs / tool input schemas; your repo `CLAUDE.md` (auth: Agent SDK on Max).
