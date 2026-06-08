---
id: u03-rag-qa-bot
title: RAG Q&A bot
tier: intermediate
created: 2026-06-05
status: todo
prerequisites: [structured-outputs, function-calling]
introduces: [embeddings, vector-store, retrieval-rag]
reinforces: [function-calling, structured-outputs]
builds_on: [u02-tool-calling-agent]
est_effort: "<= 1 week"
---

**Deliverable:** ingest a doc set → embed + index → retrieve → answer **with citations**, exposing
retrieval as a tool the u02 agent calls.

**Depth objective:** you can reason about chunk size, embedding choice, and top-k, and explain **why
retrieval quality bounds answer quality** — retrieval is the lever, not the prompt.

**Mastery check:** given a wrong answer, you can correctly diagnose it as a *retrieval* failure vs a
*generation* failure, and say what you'd change.

**Resources:** an embeddings model + a local vector store (e.g. FAISS/Chroma); Anthropic docs — citations.
