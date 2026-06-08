---
id: cs-genai-gateway
title: "Case study: a GenAI gateway / model router (Uber)"
tier: advanced
created: 2026-06-05
status: todo
source: "Uber — Navigating the LLM Landscape: GenAI Gateway"
source_urls:
  - https://www.uber.com/blog/genai-gateway/
prerequisites: [agent-loop, model-routing]
introduces: [model-gateway]
reinforces: [model-routing, token-budgeting]
builds_on: [u05-cost-routed-traced-agent]
est_effort: "1 week"
---

**The real lesson:** Uber put a **single gateway** in front of every LLM (OpenAI, Vertex, self-hosted) to
get one interface, central rate-limit/quota handling, fallbacks, cost tracking, and consistent logging —
the boring infra that makes LLM use sane at scale.

**Scoped deliverable:** a small gateway in front of ≥2 providers exposing one API, with provider
fallback on error/limit, per-call cost + latency logging, and a routing policy (cheap default → strong on
hard tasks). Point your u05 agent at it.

**Depth objective:** you can articulate *why a gateway* (vendor abstraction, resilience, central cost/limits)
and where it sits vs the agent — and implement fallback + quota handling.

**Mastery check:** you can take an agent off a hard-coded model and onto a policy-driven gateway and
explain each routing/fallback decision from the logs.
