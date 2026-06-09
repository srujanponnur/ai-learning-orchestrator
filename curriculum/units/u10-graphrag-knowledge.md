---
id: u10-graphrag-knowledge
title: "GraphRAG: Multi-Hop Retrieval over a Knowledge Graph"
tier: advanced
created: 2026-06-07
status: todo
prerequisites: [retrieval-rag, embeddings, contextual-retrieval]
introduces: [graphrag]
reinforces: [retrieval-rag, contextual-retrieval, reranking]
builds_on: [u09-rerank-and-rewrite]
est_effort: "<= 1 week"
---

**Deliverable:** A GraphRAG pipeline (entity/relation extraction -> graph construction -> community summarization) over a corpus, evaluated on a hand-built multi-hop question set where graph retrieval beats flat vector RAG; feeds candidates through the u09 reranker for a fair head-to-head.

**Depth objective:** Decide when graph-structured retrieval is worth its indexing cost, build entity/community summaries, and answer multi-hop / global-sensemaking questions that single-vector retrieval cannot.

**Mastery check:** Explain from first principles why chunk-level vector RAG fails on global and multi-hop questions, sketch how community summarization restores that capability, and name the indexing/freshness costs that make GraphRAG the wrong tool for a frequently-changing corpus.

**Resources:** Microsoft Research, 'From Local to Global: A GraphRAG Approach to Query-Focused Summarization'; microsoft/graphrag repository; Neo4j GraphRAG guides
