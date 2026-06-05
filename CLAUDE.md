# AI Learning Orchestrator — project context

> Personal conventions (persona, Claude **auth strategy**, language/stack prefs) live in your global
> `~/.claude/CLAUDE.md` and load automatically — including the gotcha: use the **Claude Agent SDK on the
> Max subscription** and **don't set `ANTHROPIC_API_KEY`** (it bills the paid API). This file is this
> repo's own context. Run the `/ai-learning-orchestrator` skill to work on it.

**Goal:** a Claude agent that proposes scoped AI-engineering mini-lessons (hosting, ops, keeping up with
trends) and catalogs them as a to-do list synced to Notion.
**Stack:** Python + Claude Agent SDK.
**MCP:** `notion` (`.mcp.json`; token via `${NOTION_TOKEN}` — see `.env.example`).
**Saves to:** `lessons/YYYY-MM-DD-<slug>.md` + a Notion "AI Eng Lessons" database.

## Cross-cutting practices (build in after the MVP)

- **Eval / feedback loop** — an LLM-as-judge pass and/or a quick human 👍/👎 logged over time.
- **Cost & usage telemetry** — log tokens + latency per Claude call (cost-attunement even on Max).
- **Observability / tracing** — Langfuse or OpenTelemetry, to see *why* the agent acted.
- **Ship-it milestone** — containerize → schedule (Task Scheduler/cron) → small host.

The skill's "Additions worth building" lean on one pattern: **a second LLM checking the first**
(judge / critic / persona panel) — practice it deliberately.
