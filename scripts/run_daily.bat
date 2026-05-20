@echo off
REM Daily Opportunity OS - Windows Task Scheduler entry point

SET PROJECT_ROOT=C:\Users\ferra\OneDrive\Desktop\Projects\.worktrees\daily-opportunity-os
SET UV=C:\Users\ferra\.local\bin\uv.exe

SET PYTHONPATH=%PROJECT_ROOT%\src

cd /d "%PROJECT_ROOT%"

REM Log run start via Python (avoids batch echo + JSON quote hell)
"%UV%" run --no-sync python -c "import json,os; f=open('data/automation_runs.jsonl','a'); f.write(json.dumps({'status':'started','trigger':'task_scheduler','date':__import__('datetime').datetime.now().isoformat()})+chr(10)); f.close()"

REM Run the daily pipeline, capture all output
"%UV%" run --no-sync opp-os daily >> "%PROJECT_ROOT%\data\automation_runs.log" 2>&1
SET EXIT_CODE=%ERRORLEVEL%

REM Log completion
"%UV%" run --no-sync python -c "import json,os; f=open('data/automation_runs.jsonl','a'); f.write(json.dumps({'status':'completed','exit_code':%EXIT_CODE%,'date':__import__('datetime').datetime.now().isoformat()})+chr(10)); f.close()"
