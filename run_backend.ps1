# NutriLens Standalone / FastAPI Server Starter
$pythonPath = "C:\Users\dhanu kun\AppData\Local\Programs\Python\Python315\python.exe"
if (-not (Test-Path $pythonPath)) {
    $pythonPath = "python"
}

Write-Host "🥑 Starting NutriLens Backend API on http://127.0.0.1:8000..." -ForegroundColor Green
& $pythonPath backend/app/standalone_server.py 8000
