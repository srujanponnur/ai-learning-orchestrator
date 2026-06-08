---
id: u11-agentic-rag-orchestrator
title: Agentic RAG: An Agent That Decides How to Retrieve
tier: advanced
created: 2026-06-07
status: todo
prerequisites: [retrieval-rag, agent-loop, agentic-patterns]
introduces: [agentic-rag]
reinforces: [retrieval-rag, agent-loop, reranking, tracing]
builds_on: [u10-graphrag-knowledge, cs-multi-agent-research]
est_effort: "<= 1 week"
---

**Deliverable:** An agent that chooses whether to retrieve at all, routes between vector and graph strategies (u09/u10), reformulates on low-confidence hits, and self-checks groundedness before answering; fully traced and scored on retrieval trajectories via the agent-eval harness.

**Depth objective:** Turn static retrieval into a control loop: the agent plans retrieval, picks a strategy, verifies grounding, and retries — measurably improving correctness on queries where one fixed pipeline fails.

**Mastery check:** Diagram the agentic-RAG control loop and its failure modes, argue when retrieve-then-read beats an agentic loop on cost/latency, and extend the design with a corrective-retrieval (CRAG-style) self-grading step explained from scratch.

**Resources:** Asai et al., 'Self-RAG: Learning to Retrieve, Generate, and Critique'; Yan et al., 'Corrective Retrieval Augmented Generation (CRAG)'; LangGraph agentic RAG tutorial; Anthropic, 'Building Effective Agents'
