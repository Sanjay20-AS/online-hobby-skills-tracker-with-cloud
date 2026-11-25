$backendDir = "d:\cloud projects\online-hobby-and-skills-tracker-with-community-sharing-cloud\backend"
$python = Join-Path $backendDir ".venv\Scripts\python.exe"
Set-Location $backendDir
& $python -m uvicorn app.main:app --app-dir . --host 127.0.0.1 --port 8000
