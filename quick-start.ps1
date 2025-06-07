# Quick Start Script for Enhanced Purview CLI v2.0
# Simple script to quickly test both frontend and backend

param(
    [switch]$Backend,    # Start only backend
    [switch]$Frontend,   # Start only frontend
    [switch]$Test        # Run tests instead of starting services
)

$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$Magenta = "Magenta"

function Write-Message {
    param($Message, $Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

Write-Message "🚀 Enhanced Purview CLI v2.0 - Quick Start" $Magenta
Write-Message "==========================================" $Magenta

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Message "⚠️ Virtual environment not found. Running setup..." $Yellow
    .\rebuilt-env.ps1
}

# Activate virtual environment
Write-Message "`n🔧 Activating virtual environment..." $Cyan
. .\.venv\Scripts\Activate.ps1

if ($Test) {
    # Run backend tests
    Write-Message "`n🧪 Running backend tests..." $Cyan
    python backend_api_test.py
    
    # Run frontend tests if available
    if (Test-Path "web-ui\package.json") {
        Write-Message "`n🧪 Running frontend tests..." $Cyan
        cd web-ui
        npm test -- --coverage --watchAll=false
        cd ..
    }
}
elseif ($Backend) {
    # Start only backend
    Write-Message "`n🔧 Starting Backend Only..." $Cyan
    cd backend
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
}
elseif ($Frontend) {
    # Start only frontend (requires backend to be running)
    Write-Message "`n🌐 Starting Frontend Only..." $Cyan
    cd web-ui
    npm start
}
else {
    # Quick health check
    Write-Message "`n🏥 Running quick health check..." $Cyan
    
    # Check if backend is running
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
        Write-Message "✅ Backend is running" $Green
    }
    catch {
        Write-Message "❌ Backend is not running" $Red
        Write-Message "💡 Start backend with: .\quick-start.ps1 -Backend" $Yellow
    }
    
    # Check if frontend is running
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -TimeoutSec 5
        Write-Message "✅ Frontend is running" $Green
    }
    catch {
        Write-Message "❌ Frontend is not running" $Red
        Write-Message "💡 Start frontend with: .\quick-start.ps1 -Frontend" $Yellow
    }
    
    Write-Message "`n📋 Quick Start Options:" $Cyan
    Write-Message "  .\quick-start.ps1 -Backend    # Start backend only" $White
    Write-Message "  .\quick-start.ps1 -Frontend   # Start frontend only" $White
    Write-Message "  .\quick-start.ps1 -Test       # Run tests" $White
    Write-Message "  .\run-full-stack.ps1          # Start full stack" $White
}
