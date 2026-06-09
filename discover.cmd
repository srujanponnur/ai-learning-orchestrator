@echo off
REM Scheduled entrypoint for the weekly discovery swarm (Windows Task Scheduler).
REM Paths relative to this file; logs to discover.log (gitignored).
cd /d "%~dp0"
".venv\Scripts\python.exe" "discover.py" >> "discover.log" 2>&1
