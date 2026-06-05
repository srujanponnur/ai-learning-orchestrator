# AI Learning Orchestrator

A Claude-powered agent that proposes scoped AI-engineering mini-lessons (hosting, ops, staying current)
and catalogs them as a Notion-synced to-do list — so learning is planned, tracked, and never vague.
A self-directed learning project, built as a clean, standalone portfolio repo.

**Status:** Planned. Scope & MVP live in the `/ai-learning-orchestrator` skill.

## Stack

Python + Claude Agent SDK · Notion (via MCP).

## Setup

- **Auth:** uses the Claude Max subscription via the Claude Agent SDK — no API key needed (see hub README).
- **Env:** copy `.env.example` → `.env`, or set the vars globally. MCP config in `.mcp.json` (`/mcp` to verify).
