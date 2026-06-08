---
id: u08-capstone-served-guardrailed
title: "Capstone: served, guardrailed, evaluated agent"
tier: capstone
created: 2026-06-05
status: todo
prerequisites: [multi-agent, guardrails, serving-quantization]
introduces: [guardrails, serving-quantization, telemetry-cost]
reinforces: [llm-as-judge, tracing, model-routing, memory-state, multi-agent]
builds_on: [u07-multi-agent-mcp]
est_effort: "2–3 weeks"
---

**Deliverable:** put the u07 system behind an API with **guardrails** (input/output checks), host a
**quantized open model** for one cheap sub-task, wire **cost/latency telemetry**, and gate deploys with
**regression evals** in CI. The "I'd run this in front of users" build.

**Depth objective:** you can **ship and operate** an agent end-to-end — serving, safety, cost, and
regression-proofing — and defend every operational trade-off.

**Mastery check:** you can walk someone through the whole system and justify each choice (why quantize
here, why this guardrail, why this eval gate) without hand-waving — i.e. you can *teach* it.

**Resources:** a serving runtime (vLLM/Ollama) + quantized model; CI; your u04/u05 evals as the deploy gate.
