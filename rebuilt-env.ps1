# Filename: reset-env.ps1
Write-Host "`n🔄 Cleaning existing .venv environment..." -ForegroundColor Yellow
Remove-Item -Recurse -Force .\.venv -ErrorAction SilentlyContinue

Write-Host "`n🐍 Creating new virtual environment with Python 3.10..." -ForegroundColor Cyan
py -3.10 -m venv .venv

if (!(Test-Path .\.venv)) {
    Write-Host "❌ Failed to create .venv. Make sure Python 3.10 is installed and accessible via 'py -3.10'" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Virtual environment created: .venv" -ForegroundColor Green
Write-Host "`n⚠️ To activate the environment, run the following command manually:" -ForegroundColor Magenta
Write-Host ".\.venv\Scripts\Activate.ps1" -ForegroundColor White
.\.venv\Scripts\Activate.ps1
# Optional: install pip-tools if requirements.in exists
if (Test-Path requirements.in) {
    Write-Host "`n📦 Detected requirements.in. Installing pip-tools and compiling dependencies..." -ForegroundColor Cyan
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\pip.exe install pip-tools
    .\.venv\Scripts\pip-compile.exe requirements.in
}

# Install from requirements.txt
if (Test-Path requirements.txt) {
    Write-Host "`n📦 Installing dependencies from requirements.txt..." -ForegroundColor Cyan
    .\.venv\Scripts\pip.exe install -r requirements.txt
    Write-Host "`n✅ All dependencies installed successfully." -ForegroundColor Green
} else {
    Write-Host "`n⚠️ requirements.txt not found. Please create one with pip-compile or install manually." -ForegroundColor Yellow
}
