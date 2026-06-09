---
id: u09-rerank-and-rewrite
title: "Precision Retrieval: Query Rewriting + Reranking"
tier: advanced
created: 2026-06-07
status: todo
prerequisites: [retrieval-rag, hybrid-search, embeddings, eval-datasets]
introduces: [reranking, query-rewriting]
reinforces: [retrieval-rag, hybrid-search, llm-as-judge]
builds_on: [cs-contextual-retrieval, u04-eval-harness]
est_effort: "<= 1 week"
---

**Deliverable:** A two-stage retrieval pipeline over your u03 corpus: multi-query rewriting -> hybrid recall -> cross-encoder rerank, wired into the u04 eval harness with an A/B report (nDCG@k + recall@k + judge-scored answer quality) against the contextual-retrieval baseline.

**Depth objective:** Take a recall-limited RAG pipeline and reliably lift precision@k by reformulating the query and reordering candidates with a reranker, proving the lift with retrieval metrics rather than vibes.

**Mastery check:** Without looking it up: explain why a cross-encoder reranker scores higher than bi-encoder cosine similarity, derive the regimes where query rewriting helps vs. actively hurts recall, and quantify the latency/cost you traded for the precision gain.

**Resources:** Anthropic Cookbook: Contextual Retrieval & reranking; Cohere Rerank documentation; Liu et al., 'Lost in the Middle: How Language Models Use Long Contexts'; RAG-Fusion / multi-query retrieval write-ups
