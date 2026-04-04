@echo off
REM Opportunity OS Dashboard - start Streamlit on port 8501

SET PROJECT_ROOT=C:\Users\ferra\OneDrive\Desktop\Projects\.worktrees\daily-opportunity-os
SET UV=C:\Users\ferra\.local\bin\uv.exe
SET PYTHONPATH=%PROJECT_ROOT%\src

cd /d "%PROJECT_ROOT%"

REM Open browser after 3 seconds
start "" /b cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8501"

"%UV%" run --no-sync streamlit run src/opportunity_os/dashboard.py --server.port 8501 --server.headless true
