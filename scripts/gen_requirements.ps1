$backendDir = Split-Path $PSScriptRoot -Parent
$backendDir = Join-Path $backendDir "backend"
$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
& $venvPython -m pip freeze | Out-File -FilePath (Join-Path $backendDir "requirements.txt") -Encoding UTF8
Write-Host "requirements.txt written."
