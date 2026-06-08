---
id: cs-sim-eval-flywheel
title: "Case study: simulation + eval flywheel for a chatbot (DoorDash)"
tier: advanced
created: 2026-06-05
status: todo
source: "DoorDash — A Simulation and Evaluation Flywheel to Develop LLM Chatbots at Scale"
source_urls:
  - https://careersatdoordash.com/blog/doordash-simulation-evaluation-flywheel-to-develop-llm-chatbots-at-scale/
prerequisites: [llm-as-judge]
introduces: [synthetic-data, agent-eval-trajectory]
reinforces: [llm-as-judge, eval-datasets]
builds_on: [u04-eval-harness]
est_effort: "1–2 weeks"
---

**The real lesson:** DoorDash used an LLM to **simulate dynamic customers** that adapt to the bot's
replies, generating realistic multi-turn conversations to evaluate the support agent at scale — a
flywheel: simulate → evaluate trajectories → fix → re-simulate.

**Scoped deliverable:** a simulator (an LLM "user" with a goal/persona) that drives multi-turn dialogues
against a small support agent, plus **trajectory evaluation** (did the conversation reach the goal? where
did it break?) feeding back into fixes. Extends the u04 eval harness from single-turn to multi-turn.

**Depth objective:** you can design a synthetic-user simulator and **trajectory-level** evals, and explain
why turn-by-turn evaluation catches failures single-response evals miss.

**Mastery check:** you can read a failed simulated conversation and localize the failure to a turn + cause,
then propose the fix and re-run.
