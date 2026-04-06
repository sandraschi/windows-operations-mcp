@echo off
cd backend
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)
start "Backend - windows-operations-mcp" python -m app.main
cd ..\frontend
if not exist node_modules (
    call npm install
)
start "Frontend - windows-operations-mcp" npm run dev
