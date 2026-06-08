---
id: cs-contextual-retrieval
title: "Case study: contextual retrieval RAG (Anthropic)"
tier: advanced
created: 2026-06-05
status: todo
source: "Anthropic — Introducing Contextual Retrieval"
source_urls:
  - https://www.anthropic.com/news/contextual-retrieval
  - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
prerequisites: [retrieval-rag, embeddings]
introduces: [contextual-retrieval, hybrid-search]
reinforces: [retrieval-rag, embeddings]
builds_on: [u03-rag-qa-bot]
est_effort: "1 week"
---

**The real lesson:** prepend a short LLM-generated **context blurb** to each chunk *before* embedding
(and pair embeddings with BM25), and retrieval-failure rate drops sharply — naive chunking loses the
context a chunk needs to be findable.

**Scoped deliverable:** upgrade the u03 RAG bot with contextual chunk augmentation + **hybrid search**
(vector + BM25), and measure the retrieval-failure delta on the u04 eval set (this is the spiral — u03 + u04 feed in).

**Depth objective:** you can explain *why* context-augmented chunks + hybrid search beat naive chunking,
and quantify it with your own eval rather than trusting the claim.

**Mastery check:** given a retrieval miss, you can say whether contextual augmentation, hybrid search, or
reranking is the right fix — and prove it.
