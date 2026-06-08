---
id: u04-eval-harness
title: Eval harness for the RAG bot
tier: intermediate
created: 2026-06-05
status: todo
prerequisites: [retrieval-rag, structured-outputs]
introduces: [eval-datasets, llm-as-judge]
reinforces: [retrieval-rag, structured-outputs]
builds_on: [u03-rag-qa-bot]
est_effort: "<= 1 week"
---

**Deliverable:** a small labelled eval set for u03 + an **LLM-as-judge** scoring groundedness & relevance,
producing a pass/fail report you can re-run after any change.

**Depth objective:** you can design an eval set and **justify the rubric**, and you know the judge's
failure modes (position bias, verbosity bias, self-preference) and how to blunt them.

**Mastery check:** shown a misleading eval result, you can identify the rubric/judge flaw and fix it so the
score reflects reality.

**Resources:** Anthropic docs — structured outputs (for judge output); your u03 bot as the system-under-test.
