# NutriLens Frontend Starter
Set-Location frontend
if (-not (Test-Path node_modules)) {
    Write-Host "📦 Installing dependencies (npm install)..." -ForegroundColor Yellow
    npm install
}
Write-Host "🚀 Launching NutriLens Vite Dev Server..." -ForegroundColor Green
npm run dev
