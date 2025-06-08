#  Purview CLI v2.0 - Full Stack Runner
# This script starts both backend (FastAPI) and frontend (React) services

param(
    [string]$Mode = "dev",  # dev, prod, test
    [switch]$SkipInstall,   # Skip dependency installation
    [switch]$BackendOnly,   # Run only backend
    [switch]$FrontendOnly,  # Run only frontend
    [switch]$Clean,         # Clean build artifacts
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 3000
)

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$Magenta = "Magenta"
$White = "White"

# Global variables
$RootDir = $PSScriptRoot
$BackendDir = Join-Path $RootDir "backend"
$FrontendDir = Join-Path $RootDir "web-ui"
$VenvPath = Join-Path $RootDir ".venv"
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"
$PipExe = Join-Path $VenvPath "Scripts\pip.exe"

# Function to print colored messages
function Write-ColorMessage {
    param($Message, $Color = $White)
    Write-Host $Message -ForegroundColor $Color
}

# Function to check if port is available
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $false  # Port is in use
    }
    catch {
        return $true   # Port is available
    }
}

# Function to find available port
function Get-AvailablePort {
    param([int]$StartPort)
    $port = $StartPort
    while (-not (Test-Port $port)) {
        $port++
        if ($port -gt ($StartPort + 100)) {
            throw "No available port found in range $StartPort-$($StartPort + 100)"
        }
    }
    return $port
}

# Function to cleanup processes
function Stop-Services {
    Write-ColorMessage "`n🛑 Stopping services..." $Yellow
    
    # Stop any running uvicorn processes
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*uvicorn*" -or $_.CommandLine -like "*main:app*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Stop any running React dev server
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like "*react-scripts*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-ColorMessage "✅ Services stopped" $Green
}

# Function to setup Python environment
function Setup-PythonEnvironment {
    Write-ColorMessage "`n🐍 Setting up Python environment..." $Cyan
    
    if (-not (Test-Path $VenvPath)) {
        Write-ColorMessage "Creating virtual environment..." $Yellow
        python -m venv $VenvPath
        if ($LASTEXITCODE -ne 0) {
            Write-ColorMessage "❌ Failed to create virtual environment" $Red
            exit 1
        }
    }
    
    if (-not $SkipInstall) {
        Write-ColorMessage "Installing Python dependencies..." $Yellow
        & $PipExe install -r "requirements.txt"
        if ($LASTEXITCODE -ne 0) {
            Write-ColorMessage "❌ Failed to install Python dependencies" $Red
            exit 1
        }
    }
    
    Write-ColorMessage "✅ Python environment ready" $Green
}

# Function to setup Node.js environment
function Setup-NodeEnvironment {
    Write-ColorMessage "`n📦 Setting up Node.js environment..." $Cyan
    
    Push-Location $FrontendDir
    try {
        if (-not (Test-Path "node_modules") -or -not $SkipInstall) {
            Write-ColorMessage "Installing Node.js dependencies..." $Yellow
            npm install
            if ($LASTEXITCODE -ne 0) {
                Write-ColorMessage "❌ Failed to install Node.js dependencies" $Red
                exit 1
            }
        }
        Write-ColorMessage "✅ Node.js environment ready" $Green
    }
    finally {
        Pop-Location
    }
}

# Function to clean build artifacts
function Clean-Artifacts {
    Write-ColorMessage "`n🧹 Cleaning build artifacts..." $Yellow
    
    # Clean Python cache
    Get-ChildItem -Path $RootDir -Recurse -Directory -Name "__pycache__" | ForEach-Object {
        Remove-Item -Path $_ -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    # Clean React build
    $BuildDir = Join-Path $FrontendDir "build"
    if (Test-Path $BuildDir) {
        Remove-Item -Path $BuildDir -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    Write-ColorMessage "✅ Artifacts cleaned" $Green
}

# Function to start backend service
function Start-Backend {
    Write-ColorMessage "`n🚀 Starting Backend Service..." $Cyan
    
    # Check if backend port is available
    if (-not (Test-Port $BackendPort)) {
        $BackendPort = Get-AvailablePort $BackendPort
        Write-ColorMessage "⚠️ Port 8000 in use, using port $BackendPort" $Yellow
    }
    
    Push-Location $BackendDir
    try {
        Write-ColorMessage "Starting FastAPI server on http://localhost:$BackendPort" $Green
        Write-ColorMessage "API Documentation: http://localhost:$BackendPort/docs" $Magenta
        Write-ColorMessage "Alternative docs: http://localhost:$BackendPort/redoc" $Magenta
        
        # Set environment variables
        $env:PYTHONPATH = $BackendDir
        $env:BACKEND_PORT = $BackendPort
        
        if ($Mode -eq "dev") {
            # Development mode with auto-reload
            & $PythonExe -m uvicorn main:app --host 0.0.0.0 --port $BackendPort --reload --log-level info
        } elseif ($Mode -eq "prod") {
            # Production mode
            & $PythonExe -m uvicorn main:app --host 0.0.0.0 --port $BackendPort --workers 4
        } else {
            # Test mode
            & $PythonExe -m uvicorn main:app --host 0.0.0.0 --port $BackendPort --log-level debug
        }
    }
    finally {
        Pop-Location
    }
}

# Function to start frontend service
function Start-Frontend {
    Write-ColorMessage "`n🌐 Starting Frontend Service..." $Cyan
    
    # Check if frontend port is available
    if (-not (Test-Port $FrontendPort)) {
        $FrontendPort = Get-AvailablePort $FrontendPort
        Write-ColorMessage "⚠️ Port 3000 in use, using port $FrontendPort" $Yellow
    }
    
    Push-Location $FrontendDir
    try {
        Write-ColorMessage "Starting React development server on http://localhost:$FrontendPort" $Green
        
        # Set environment variables
        $env:PORT = $FrontendPort
        $env:REACT_APP_API_URL = "http://localhost:$BackendPort"
        $env:REACT_APP_WS_URL = "ws://localhost:$BackendPort"
        $env:BROWSER = "none"  # Don't auto-open browser
        
        if ($Mode -eq "dev") {
            npm start
        } elseif ($Mode -eq "prod") {
            npm run build
            Write-ColorMessage "✅ Production build completed in build/" $Green
        } else {
            npm run test
        }
    }
    finally {
        Pop-Location
    }
}

# Function to run health checks
function Test-Services {
    Write-ColorMessage "`n🏥 Running health checks..." $Cyan
    
    # Wait for services to start
    Start-Sleep -Seconds 3
    
    # Test backend
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$BackendPort/health" -Method GET -TimeoutSec 10
        Write-ColorMessage "✅ Backend health check passed" $Green
    }
    catch {
        Write-ColorMessage "❌ Backend health check failed: $($_.Exception.Message)" $Red
    }
    
    # Test frontend (if running)
    if (-not $BackendOnly) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:$FrontendPort" -Method GET -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-ColorMessage "✅ Frontend health check passed" $Green
            }
        }
        catch {
            Write-ColorMessage "❌ Frontend health check failed: $($_.Exception.Message)" $Red
        }
    }
}

# Function to start both services in parallel
function Start-FullStack {
    Write-ColorMessage "`n🚀 Starting Full Stack Application..." $Cyan
    
    # Start backend in background job
    $backendJob = Start-Job -ScriptBlock {
        param($BackendDir, $PythonExe, $BackendPort, $Mode)
        Set-Location $BackendDir
        $env:PYTHONPATH = $BackendDir
        
        if ($Mode -eq "dev") {
            & $PythonExe -m uvicorn main:app --host 0.0.0.0 --port $BackendPort --reload
        } else {
            & $PythonExe -m uvicorn main:app --host 0.0.0.0 --port $BackendPort
        }
    } -ArgumentList $BackendDir, $PythonExe, $BackendPort, $Mode
    
    Write-ColorMessage "Backend starting in background (Job ID: $($backendJob.Id))..." $Yellow
    Start-Sleep -Seconds 5  # Give backend time to start
    
    # Start frontend in foreground
    Start-Frontend
}

# Main script execution
try {
    Write-ColorMessage "🔥  Purview CLI v2.0 - Full Stack Runner" $Magenta
    Write-ColorMessage "=================================================" $Magenta
    Write-ColorMessage "Mode: $Mode" $White
    Write-ColorMessage "Backend Port: $BackendPort" $White
    Write-ColorMessage "Frontend Port: $FrontendPort" $White
    Write-ColorMessage "" $White
    
    # Handle cleanup on Ctrl+C
    Register-ObjectEvent -InputObject ([Console]) -EventName CancelKeyPress -Action {
        Stop-Services
        exit 0
    } | Out-Null
    
    # Clean artifacts if requested
    if ($Clean) {
        Clean-Artifacts
    }
    
    # Setup environments
    if (-not $FrontendOnly) {
        Setup-PythonEnvironment
    }
    if (-not $BackendOnly) {
        Setup-NodeEnvironment
    }
    
    # Start services based on mode
    if ($BackendOnly) {
        Start-Backend
    }
    elseif ($FrontendOnly) {
        Start-Frontend
    }
    else {
        Start-FullStack
    }
    
    # Run health checks
    if ($Mode -ne "test") {
        Test-Services
    }
    
    Write-ColorMessage "`n✅ All services started successfully!" $Green
    Write-ColorMessage "Press Ctrl+C to stop all services" $Yellow
    
    # Keep script running
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
catch {
    Write-ColorMessage "`n❌ Error: $($_.Exception.Message)" $Red
    exit 1
}
finally {
    Stop-Services
}
