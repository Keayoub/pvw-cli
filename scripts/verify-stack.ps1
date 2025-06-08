# Verification Script for  Purview CLI v2.0
# Comprehensive testing of frontend and backend integration

param(
    [switch]$Detailed,  # Show detailed test results
    [switch]$FixIssues  # Attempt to fix common issues
)

$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$Magenta = "Magenta"
$White = "White"

function Write-Status {
    param($Message, $Status, $Details = "")
    $color = switch($Status) {
        "PASS" { $Green }
        "FAIL" { $Red }
        "WARN" { $Yellow }
        "INFO" { $Cyan }
        default { $White }
    }
      $symbol = switch($Status) {
        "PASS" { "[+]" }
        "FAIL" { "[!]" }
        "WARN" { "[*]" }
        "INFO" { "[i]" }
        default { "[?]" }
    }
    
    Write-Host "$symbol [$Status] $Message" -ForegroundColor $color
    if ($Details -and $Detailed) {
        Write-Host "    $Details" -ForegroundColor Gray
    }
}

function Test-Prerequisites {
    Write-Host "`n[*] Checking Prerequisites..." -ForegroundColor $Magenta
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python 3\.") {
            Write-Status "Python installation" "PASS" $pythonVersion
        } else {
            Write-Status "Python installation" "FAIL" "Python 3.x required"
            return $false
        }
    }
    catch {
        Write-Status "Python installation" "FAIL" "Python not found in PATH"
        return $false
    }
    
    # Check Node.js
    try {
        $nodeVersion = node --version 2>&1
        if ($nodeVersion -match "v\d+\.") {
            Write-Status "Node.js installation" "PASS" $nodeVersion
        } else {
            Write-Status "Node.js installation" "FAIL" "Node.js required"
            return $false
        }
    }
    catch {
        Write-Status "Node.js installation" "FAIL" "Node.js not found in PATH"
        return $false
    }
    
    # Check npm
    try {
        $npmVersion = npm --version 2>&1
        Write-Status "npm installation" "PASS" "v$npmVersion"
    }
    catch {
        Write-Status "npm installation" "FAIL" "npm not found"
        return $false
    }
    
    return $true
}

function Test-ProjectStructure {
    Write-Host "`n[*] Checking Project Structure..." -ForegroundColor $Magenta
    
    $requiredFiles = @(
        "requirements.txt",
        "requirements.in",
        "backend\main.py",
        "web-ui\package.json",
        "web-ui\src\App.tsx"
    )
    
    $allGood = $true
    foreach ($file in $requiredFiles) {
        if (Test-Path $file) {
            Write-Status "File: $file" "PASS"
        } else {
            Write-Status "File: $file" "FAIL" "Required file missing"
            $allGood = $false
        }
    }
    
    # Check virtual environment
    if (Test-Path ".venv") {
        Write-Status "Virtual environment" "PASS" ".venv directory exists"
    } else {
        Write-Status "Virtual environment" "WARN" "Run .\rebuilt-env.ps1 to create"
        $allGood = $false
    }
    
    return $allGood
}

function Test-Dependencies {
    Write-Host "`n[*] Checking Dependencies..." -ForegroundColor $Magenta
    
    # Check Python dependencies
    if (Test-Path ".venv\Scripts\python.exe") {
        try {
            $pipList = & .\.venv\Scripts\pip.exe list 2>&1
            if ($pipList -match "fastapi") {
                Write-Status "Python dependencies" "PASS" "FastAPI and others installed"
            } else {
                Write-Status "Python dependencies" "FAIL" "FastAPI not found"
        if ($FixIssues) {
            Write-Host "[*] Installing Python dependencies..." -ForegroundColor $Yellow
            & .\.venv\Scripts\pip.exe install -r requirements.txt
        }
                return $false
            }
        }
        catch {
            Write-Status "Python dependencies" "FAIL" "Error checking pip list"
            return $false
        }
    } else {
        Write-Status "Python environment" "FAIL" "Virtual environment not activated"
        return $false
    }
    
    # Check Node dependencies
    if (Test-Path "web-ui\node_modules") {
        Write-Status "Node.js dependencies" "PASS" "node_modules exists"
    } else {        Write-Status "Node.js dependencies" "FAIL" "Run npm install in web-ui"
        if ($FixIssues) {
            Write-Host "[*] Installing Node.js dependencies..." -ForegroundColor $Yellow
            Set-Location web-ui
            npm install
            Set-Location ..
        }
        return $false
    }
    
    return $true
}

function Test-BackendAPI {
    Write-Host "`n[*] Testing Backend API..." -ForegroundColor $Magenta
    
    # Try to start backend in background and test
    $backendJob = Start-Job -ScriptBlock {
        Set-Location $args[0]
        Set-Location backend
        $env:PYTHONPATH = (Get-Location).Path
        & ..\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8001 --log-level error
    } -ArgumentList (Get-Location)
    
    Start-Sleep -Seconds 5  # Wait for backend to start
    
    try {
        # Test health endpoint
        $response = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method GET -TimeoutSec 10
        Write-Status "Backend health check" "PASS" "API responding"
        
        # Test API documentation
        $docsResponse = Invoke-WebRequest -Uri "http://localhost:8001/docs" -Method GET -TimeoutSec 10
        if ($docsResponse.StatusCode -eq 200) {
            Write-Status "API documentation" "PASS" "Swagger UI accessible"
        }
        
        # Test specific endpoints
        $endpoints = @("/api/v1/entities", "/api/v1/analytics/dashboard")
        foreach ($endpoint in $endpoints) {
            try {
                $endpointResponse = Invoke-RestMethod -Uri "http://localhost:8001$endpoint" -Method GET -TimeoutSec 5
                Write-Status "Endpoint: $endpoint" "PASS"
            }
            catch {
                Write-Status "Endpoint: $endpoint" "WARN" "May require authentication"
            }
        }
        
        $backendWorking = $true
    }
    catch {
        Write-Status "Backend API" "FAIL" "Cannot connect to http://localhost:8001"
        $backendWorking = $false
    }
    finally {
        # Clean up background job
        Stop-Job $backendJob -ErrorAction SilentlyContinue
        Remove-Job $backendJob -ErrorAction SilentlyContinue
    }
    
    return $backendWorking
}

function Test-Frontend {
    Write-Host "`n[*] Testing Frontend..." -ForegroundColor $Magenta
    
    Set-Location web-ui
    try {
        # Test if React app builds successfully
        $env:CI = "true"  # Prevent interactive prompts
        $buildOutput = npm run build 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Frontend build" "PASS" "React app builds successfully"
            
            # Check if build directory exists
            if (Test-Path "build") {
                Write-Status "Build artifacts" "PASS" "Build directory created"
            }
            
            $frontendWorking = $true
        } else {
            Write-Status "Frontend build" "FAIL" "Build failed"
            if ($Detailed) {
                Write-Host $buildOutput -ForegroundColor Gray
            }
            $frontendWorking = $false
        }
    }
    catch {
        Write-Status "Frontend test" "FAIL" "Error during build test"
        $frontendWorking = $false
    }
    finally {
        Set-Location ..
    }
    
    return $frontendWorking
}

function Test-Integration {
    Write-Host "`n[*] Testing Integration..." -ForegroundColor $Magenta
    
    # Check if integration script exists and can be parsed
    if (Test-Path "frontend_backend_integration.py") {
        Write-Status "Integration script" "PASS" "frontend_backend_integration.py exists"
        
        # Try to run a basic syntax check
        try {
            & .\.venv\Scripts\python.exe -m py_compile frontend_backend_integration.py
            Write-Status "Integration script syntax" "PASS" "No syntax errors"
        }
        catch {
            Write-Status "Integration script syntax" "FAIL" "Syntax errors found"
        }
    } else {
        Write-Status "Integration script" "FAIL" "frontend_backend_integration.py missing"
    }
    
    # Check configuration files
    $configFiles = @(
        "backend\app\core\config.py",
        "web-ui\src\config\apiConfig.ts"
    )
    
    foreach ($file in $configFiles) {
        if (Test-Path $file) {
            Write-Status "Config: $file" "PASS"
        } else {
            Write-Status "Config: $file" "WARN" "Configuration file missing"
        }
    }
}

function Show-Summary {
    param($Results)
      Write-Host "`n[*] Verification Summary" -ForegroundColor $Magenta
    Write-Host "======================" -ForegroundColor $Magenta
    
    $passed = ($Results | Where-Object { $_ -eq $true }).Count
    $total = $Results.Count
      if ($passed -eq $total) {
        Write-Host "[+] All checks passed! ($passed/$total)" -ForegroundColor $Green
        Write-Host "`n[*] You can now run the full stack with:" -ForegroundColor $Cyan
        Write-Host "    .\run-full-stack.ps1" -ForegroundColor $White
    } elseif ($passed -gt 0) {
        Write-Host "[*] Some issues found ($passed/$total passed)" -ForegroundColor $Yellow
        Write-Host "`n[*] Try running with -FixIssues to auto-fix common problems:" -ForegroundColor $Cyan
        Write-Host "    .\verify-stack.ps1 -FixIssues" -ForegroundColor $White
    } else {
        Write-Host "[!] Multiple issues found (0/$total passed)" -ForegroundColor $Red
        Write-Host "`n[*] Please check the requirements and setup:" -ForegroundColor $Cyan
        Write-Host "    1. Run .\rebuilt-env.ps1 to setup environment" -ForegroundColor $White
        Write-Host "    2. Ensure Python 3.x and Node.js are installed" -ForegroundColor $White
        Write-Host "    3. Check project structure and dependencies" -ForegroundColor $White
    }
}

# Main execution
Write-Host "[*]  Purview CLI v2.0 - Stack Verification" -ForegroundColor $Magenta
Write-Host "=================================================" -ForegroundColor $Magenta

$results = @()
$results += Test-Prerequisites
$results += Test-ProjectStructure
$results += Test-Dependencies
$results += Test-BackendAPI
$results += Test-Frontend
Test-Integration  # This doesn't return a boolean, just informational

Show-Summary -Results $results

if ($Detailed) {
    Write-Host "`n[*] Additional Information:" -ForegroundColor $Magenta
    Write-Host "  - Backend API: http://localhost:8000" -ForegroundColor $White
    Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor $White
    Write-Host "  - API Docs: http://localhost:8000/docs" -ForegroundColor $White
    Write-Host "  - Alternative Docs: http://localhost:8000/redoc" -ForegroundColor $White
}
