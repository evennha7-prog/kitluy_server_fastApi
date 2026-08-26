# PowerShell Runner for FastAPI Server
Set-Location -Path $PSScriptRoot

if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "[INFO] Using virtual environment (.venv)..." -ForegroundColor Cyan
    & ".\.venv\Scripts\python.exe" run.py
} else {
    Write-Host "[INFO] Using system python..." -ForegroundColor Yellow
    python run.py
}
