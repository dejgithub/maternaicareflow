# MaternAI CareFlow - Windows Setup Script
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  MaternAI CareFlow - Setup Script" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Setting up Backend..." -ForegroundColor Yellow
Push-Location "..\backend"
python -m venv venv
if ($?) {
    .\venv\Scripts\pip install -r requirements.txt
    if ($?) {
        Write-Host "✓ Backend dependencies installed" -ForegroundColor Green
    }
}
if (Test-Path ".env.example") {
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ Created .env from .env.example" -ForegroundColor Green
    }
}
Pop-Location

Write-Host ""
Write-Host "Setting up Frontend..." -ForegroundColor Yellow
Push-Location "..\frontend"
npm install
if ($?) {
    Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green
}
Pop-Location

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor White
Write-Host "  Backend:  cd backend && .\venv\Scripts\uvicorn app.main:app --reload"
Write-Host "  Frontend: cd frontend && npm run dev"
Write-Host ""
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Blue
