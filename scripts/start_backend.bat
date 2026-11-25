@echo off
cd /d "d:\cloud projects\online-hobby-and-skills-tracker-with-community-sharing-cloud\backend"
"d:\cloud projects\online-hobby-and-skills-tracker-with-community-sharing-cloud\backend\.venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir . --host 127.0.0.1 --port 8000
