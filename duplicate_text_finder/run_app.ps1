# Duplicate Text Finder - Local Flask Server Launcher
$ErrorActionPreference = "Stop"
$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment not found at $venvPython. Please create it first." -ForegroundColor Red
    exit 1
}
Write-Host "Starting Duplicate Text Finder on http://127.0.0.1:5050 ..." -ForegroundColor Cyan
& $venvPython (Join-Path $PSScriptRoot "app.py")
