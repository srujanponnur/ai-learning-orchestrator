@echo off
REM Scheduled entrypoint for the daily curriculum cycle (Windows Task Scheduler).
REM Uses paths relative to this file, logs to cycle.log (gitignored).
cd /d "%~dp0"
".venv\Scripts\python.exe" "run_cycle.py" >> "cycle.log" 2>&1
