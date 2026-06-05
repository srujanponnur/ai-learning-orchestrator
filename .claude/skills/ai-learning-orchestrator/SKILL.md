---
name: ai-learning-orchestrator
description: Work on Project 1 — an agent that uses the Claude API to propose scoped AI-engineering mini-lessons (hosting, ops, trends), then catalogs them as a to-do list synced to Notion. Use when building, planning, or running the learning orchestrator.
---

# Project 1 — AI Learning Orchestrator

**Goal:** software that uses the Claude API to *generate and curate* scoped mini-projects/lessons
that make the owner a stronger AI engineer (hosting, maintaining, deploying, and tracking AI/agent
trends), then catalogs them into a tracked to-do list. Notion is the catalog; VSCode is where the
lessons get built.

**Folder:** `01-ai-learning-orchestrator/`  ·  **Stack:** Python + Claude Agent SDK.

## MVP (build this first)

1. A CLI/script `propose.py` that calls Claude to generate **3–5 scoped lesson cards** for a given
   focus area (e.g. "serving LLMs cheaply", "agent eval", "RAG ops"). Each card =
   `{title, why_it_matters, concepts, est_effort, deliverable, resources}`.
2. Persist cards as dated markdown in `01-ai-learning-orchestrator/lessons/` (source of truth).
3. **Sync to Notion** via the `notion` MCP: create/append rows in a "Learning Backlog" database
   (props: Status, Area, Effort, Concept, Deliverable, Created). Idempotent — don't duplicate.
4. `status.py` to move a card todo → in-progress → done and reflect it back to Notion.

## Stretch

- A weekly "trend scan" sub-agent (WebSearch) that surfaces what's new in AI eng and proposes lessons.
- Difficulty/cost routing: cheap model drafts, stronger model curates.
- A "teach me" mode that turns a card into a guided build session.

## Conventions

- Markdown card first, then Notion sync — never the reverse.
- Keep each generated lesson genuinely scoped (≤ a week of effort). Reject vague ones.
- **Definition of done (MVP):** `propose.py "topic"` produces md cards + Notion rows, and `status.py`
  round-trips a status change to Notion.

## Additions worth building (beyond MVP)

- **Self-judge generated lessons:** an LLM-as-judge pass scores each card for scope / clarity /
  non-vagueness before it's saved; reject or regenerate low scorers. The cheapest place to practice eval.
- **Gap analysis:** track which areas you actually complete vs. neglect, and bias the next batch of
  proposals toward the gaps — turns the backlog into a self-correcting curriculum.
- (Plus the hub-wide cross-cutting practices: eval loop, cost telemetry, tracing, ship-it.)
