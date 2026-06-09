# setup.ps1 — one-time environment setup for the AI Learning Orchestrator (Windows).
# Run:  powershell -ExecutionPolicy Bypass -File setup.ps1
# Idempotent: safe to re-run. Does the scriptable setup, then lists the manual steps left.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Write-Host "== AI Learning Orchestrator - setup ==" -ForegroundColor Cyan

# 1. Python launcher
$py = if (Get-Command py -ErrorAction SilentlyContinue) { "py" }
      elseif (Get-Command python -ErrorAction SilentlyContinue) { "python" }
      else { throw "Python 3.11+ not found. Install it and re-run." }
Write-Host ("Python: " + (& $py --version))

# 2. virtual environment
$venvPy = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Creating .venv ..."
    & $py -m venv (Join-Path $root ".venv")
} else {
    Write-Host ".venv already exists."
}

# 3. dependencies
Write-Host "Installing dependencies (requirements.txt) ..."
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r (Join-Path $root "requirements.txt") --quiet
Write-Host "Dependencies installed."

# 4. .env scaffold (never overwrites an existing .env)
$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $root ".env.example") $envFile
    Write-Host ".env created from .env.example - set your real NOTION_TOKEN in it." -ForegroundColor Yellow
} else {
    Write-Host ".env already exists (left untouched)."
}

# 5. prerequisite checks (report only)
Write-Host "`n-- prerequisite checks --"
if (Get-Command claude -ErrorAction SilentlyContinue) {
    Write-Host "  [ok] claude CLI on PATH"
} elseif (Get-ChildItem "$env:USERPROFILE\.vscode\extensions" -Filter "anthropic.claude-code-*" -Directory -ErrorAction SilentlyContinue) {
    Write-Host "  [ok] claude CLI via VSCode extension (found automatically by the Agent SDK)"
} else {
    Write-Host "  [!] claude CLI not found - install Claude Code and run 'claude' to log in (Max subscription)" -ForegroundColor Yellow
}
if (Get-Command node -ErrorAction SilentlyContinue) {
    Write-Host "  [ok] node $(node --version) - interactive Notion MCP available"
} else {
    Write-Host "  [--] node not found (optional; only the interactive Notion MCP needs it, not the sync scripts)"
}

# 6. manual steps that cannot be scripted
Write-Host "`n-- manual steps left --" -ForegroundColor Cyan
Write-Host "  1. Create a Notion integration -> https://www.notion.so/profile/integrations"
Write-Host "     copy the ntn_... secret into .env  (NOTION_TOKEN=ntn_...)"
Write-Host "  2. In Notion, open your dashboard page -> (...) -> Connections -> add that integration"
Write-Host "  3. Make sure Claude Code is logged in with your Max subscription:  claude"
Write-Host "`n-- then --"
Write-Host "  First sync:      .\.venv\Scripts\python.exe sync.py"
Write-Host "  Automate daily:  powershell -ExecutionPolicy Bypass -File schedule_setup.ps1"
Write-Host "  (Do NOT set ANTHROPIC_API_KEY - this project uses the Max subscription.)"
