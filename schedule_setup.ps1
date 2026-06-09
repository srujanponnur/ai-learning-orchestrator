# Registers (or updates) the daily curriculum cycle in Windows Task Scheduler.
# This is the source-of-truth for the schedule — the OS stores the live copy at
#   C:\Windows\System32\Tasks\AILearningOrchestrator
# Run once per machine (no admin needed):
#   powershell -ExecutionPolicy Bypass -File schedule_setup.ps1
#
# Inspect:  schtasks /Query /TN AILearningOrchestrator /V /FO LIST
# Run now:  schtasks /Run   /TN AILearningOrchestrator
# Remove:   schtasks /Delete /TN AILearningOrchestrator /F

$ErrorActionPreference = "Stop"

$taskName = "AILearningOrchestrator"
$startTime = "09:00"
$cmd = Join-Path $PSScriptRoot "run_cycle.cmd"   # the payload the task runs (next to this script)

# 1. Daily trigger at $startTime, running run_cycle.cmd as the current user (Interactive — no
#    stored password; runs while you're logged on, locked is fine).
schtasks /Create /TN $taskName /SC DAILY /ST $startTime /F /TR "$cmd"

# 2. Robustness: catch up a missed run (PC asleep/off at $startTime → runs at next login),
#    and don't let battery state block it.
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Set-ScheduledTask -TaskName $taskName -Settings $settings | Out-Null

Write-Host "Scheduled '$taskName' daily at $startTime (catch-up on missed runs enabled)."
Write-Host "Runs: $cmd"
