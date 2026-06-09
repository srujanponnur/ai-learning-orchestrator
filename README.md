# AI Learning Orchestrator

A spiral-curriculum **curator** for AI engineering. It decides *what to learn and in what order* — a
concept graph plus an ordered sequence of mini-project "units," where each new unit **reinforces
earlier concepts** so you reach depth, not just coverage. It mirrors everything to **Notion** (your
cockpit) and runs itself daily. It plans and tracks; *you* build the units.

Built on the **Claude Agent SDK** against a **Claude Max subscription** — no metered API key.

## How it works

- **Source of truth:** the concept graph (`curriculum/concepts.yaml`) + units (`curriculum/units/*.md`).
- `curate.py` — proposes the next spiral units (validated: each must reuse prior concepts).
- `sync.py` — mirrors units → a Notion database (properties + per-unit page bodies + a legend page).
- `master.py` — advances concept mastery, **evidence-gated** (only when units are actually built/done).
- `run_cycle.py` — the daily loop: pull Notion status → advance mastery → teach-me (on request) →
  top up units → push back. **You drive it entirely from Notion.**

## Prerequisites

- **Python 3.11+**
- **Claude Code**, logged in with a **Max/Pro subscription** (`claude`). The Agent SDK uses it — no API key.
- A **Notion** account + a free internal integration.
- *(optional)* **Node.js** — only for the interactive Notion MCP in `.mcp.json`; the sync scripts don't need it.

## Setup

```powershell
# Scriptable setup: venv, dependencies, .env scaffold, prerequisite checks
powershell -ExecutionPolicy Bypass -File setup.ps1
```

Then the manual steps it reminds you of (can't be scripted):

1. **Create a Notion integration** → <https://www.notion.so/profile/integrations>, copy the `ntn_…`
   secret into **`.env`** (`NOTION_TOKEN=ntn_...`).
2. **Connect it** → open your Notion dashboard page → **••• → Connections → add the integration**
   (it can only see pages it's connected to).
3. **Claude login** → ensure `claude` is logged in with your Max subscription.

> Do **not** set `ANTHROPIC_API_KEY` — the code strips it so runs bill the subscription, not the API.

## Usage

First mirror to Notion:

```powershell
.\.venv\Scripts\python.exe sync.py
```

Then **drive it from Notion** — no scripts to run by hand:

- Set a unit's **Status** → `in_progress` / `done` → its concepts' mastery advances automatically.
- Tick **"Teach me"** on a unit → a learning brief (how to learn it + which resources) is written into its page.
- As your `todo` queue drops below ~3, new spiral units are proposed automatically.

Manual commands (optional):

| Command | Does |
| --- | --- |
| `python curate.py next` | propose the next spiral unit(s) |
| `python sync.py` | mirror units → Notion |
| `python master.py --status` | show mastery + what's unlocked next |
| `python run_cycle.py` | run one full cycle now |

## Automation (daily)

```powershell
powershell -ExecutionPolicy Bypass -File schedule_setup.ps1
```

Registers a Windows Task Scheduler job (`AILearningOrchestrator`, daily 09:00, with catch-up on missed
runs) that executes `run_cycle.cmd`. Inspect/run/remove:

```powershell
schtasks /Query  /TN AILearningOrchestrator /V /FO LIST
schtasks /Run    /TN AILearningOrchestrator
schtasks /Delete /TN AILearningOrchestrator /F
```

**Non-Windows:** the Python scripts are cross-platform; use cron instead of Task Scheduler, e.g.
`0 9 * * * cd /path/to/repo && .venv/bin/python run_cycle.py >> cycle.log 2>&1`.

## Layout

```text
curate.py · sync.py · master.py · run_cycle.py     # entrypoints
alo/    agent.py (Agent SDK) · store.py · validate.py · notion.py · env.py
curriculum/   concepts.yaml · units/*.md · sources.md
setup.ps1 · schedule_setup.ps1 · run_cycle.cmd     # setup & scheduling
```
