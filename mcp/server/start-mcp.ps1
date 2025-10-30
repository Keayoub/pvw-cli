param(
    [string] $AccountName,
    [string] $AccountId,
    [string] $TenantId,
    [string] $ClientId,
    [string] $ClientSecret,
    [switch] $UseDocker,
    [switch] $Dev,
    [switch] $Background,
    [switch] $Status,
    [switch] $StopBackground
)

if (-not $AccountName -and -not $StopBackground -and -not $Status) {
    Write-Host "Usage: .\start-mcp.ps1 -AccountName <your-purview-account> [-AccountId <id>] [-TenantId <id>] [-ClientId <id>] [-ClientSecret <secret>] [-UseDocker] [-Dev]"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\start-mcp.ps1 -AccountName 'my-account'                     # Run with Python directly"
    Write-Host "  .\start-mcp.ps1 -AccountName 'my-account' -UseDocker          # Run with Docker"
    Write-Host "  .\start-mcp.ps1 -AccountName 'my-account' -AccountId '123'    # With account ID"
    Write-Host "  .\start-mcp.ps1 -AccountName 'my-account' -Dev                # Development mode (editable install)"
    Write-Host "  .\start-mcp.ps1 -AccountName 'my-account' -Background         # Start server in background (detached)"
    Write-Host "  .\start-mcp.ps1 -StopBackground                               # Stop background server started earlier"
    exit 1
}

# Set environment variables
$env:PURVIEW_ACCOUNT_NAME = $AccountName
if ($AccountId) { $env:PURVIEW_ACCOUNT_ID = $AccountId }
if ($TenantId) { $env:AZURE_TENANT_ID = $TenantId }
if ($ClientId) { $env:AZURE_CLIENT_ID = $ClientId }
if ($ClientSecret) { $env:AZURE_CLIENT_SECRET = $ClientSecret }

# Determine script directory and server.py path
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ServerPath = Join-Path $ScriptDir "server.py"

if ($UseDocker) {
    Write-Host "=== Running Purview MCP Server in Docker ===" -ForegroundColor Cyan
    Write-Host "Building Docker image (this may take a few minutes)..."
    
    # When this script is run from the mcp folder, use the parent directory as the
    # build context and the Dockerfile in the current folder.
    $RepoRoot = Split-Path -Parent $ScriptDir
    docker build -t purview-mcp:local -f "$ScriptDir\Dockerfile" $RepoRoot
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker build failed!" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    
    Write-Host "Running Docker container (interactive - attach stdin/stdout)..."
    Write-Host "Use Ctrl+C to stop the container."
    
    docker run --rm -i `
        -e PURVIEW_ACCOUNT_NAME="$env:PURVIEW_ACCOUNT_NAME" `
        -e PURVIEW_ACCOUNT_ID="$env:PURVIEW_ACCOUNT_ID" `
        -e AZURE_TENANT_ID="$env:AZURE_TENANT_ID" `
        -e AZURE_CLIENT_ID="$env:AZURE_CLIENT_ID" `
        -e AZURE_CLIENT_SECRET="$env:AZURE_CLIENT_SECRET" `
        purview-mcp:local
} else {
    Write-Host "=== Running Purview MCP Server with Python ===" -ForegroundColor Cyan
    Write-Host "Server path: $ServerPath"
    Write-Host "Account: $AccountName"
    if ($AccountId) { Write-Host "Account ID: $AccountId" }
    if ($TenantId) { Write-Host "Tenant: $TenantId" }
    Write-Host ""
    
    # Check if server.py exists
    if (-not (Test-Path $ServerPath)) {
        Write-Host "ERROR: server.py not found at: $ServerPath" -ForegroundColor Red
        exit 1
    }
    
    # Check if python is available
    try {
        $PythonVersion = python --version 2>&1
        Write-Host "Using: $PythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: Python not found. Please install Python or activate your virtual environment." -ForegroundColor Red
        exit 1
    }
    
    Write-Host ""
    Write-Host "=== Preparation Steps ===" -ForegroundColor Yellow
    
    # Step 1: Check if pvw-cli package is installed
    Write-Host "[1/2] Checking pvw-cli package..." -ForegroundColor Cyan
    
    if ($Dev) {
        # Development mode: always install in editable mode from local source
        Write-Host "  Development mode: Installing pvw-cli in editable mode..." -ForegroundColor Yellow
        $RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
        Push-Location $RepoRoot
        try {
            python -m pip install -e . --quiet
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  SUCCESS: pvw-cli installed in editable mode" -ForegroundColor Green
            } else {
                Write-Host "  WARNING: pvw-cli installation had issues (non-critical)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  WARNING: Failed to install pvw-cli (non-critical)" -ForegroundColor Yellow
        }
        Pop-Location
    } else {
        # Production mode: check if installed, install from PyPI if needed
        try {
            $PvwCheck = python -m pip show pvw-cli 2>$null
            if ($PvwCheck) {
                Write-Host "  SUCCESS: pvw-cli already installed" -ForegroundColor Green
            } else {
                throw "Not installed"
            }
        } catch {
            Write-Host "  Installing pvw-cli package from PyPI..." -ForegroundColor Yellow
            try {
                python -m pip install pvw-cli --quiet
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  SUCCESS: pvw-cli installed" -ForegroundColor Green
                } else {
                    Write-Host "  WARNING: pvw-cli installation had issues (non-critical)" -ForegroundColor Yellow
                }
            } catch {
                Write-Host "  WARNING: Failed to install pvw-cli (non-critical)" -ForegroundColor Yellow
            }
        }
    }
    
    # Step 2: Check Azure authentication
    Write-Host "[2/2] Checking Azure authentication..." -ForegroundColor Cyan
    try {
        $AzAccount = az account show 2>$null | ConvertFrom-Json
        if ($AzAccount) {
            Write-Host "  SUCCESS: Already authenticated to Azure" -ForegroundColor Green
            Write-Host "    Subscription: $($AzAccount.name)" -ForegroundColor Gray
        } else {
            throw "Not authenticated"
        }
    } catch {
        Write-Host "  WARNING: Not authenticated to Azure" -ForegroundColor Yellow
        Write-Host "  Please run 'az login' in another terminal before starting the server" -ForegroundColor Yellow
        Write-Host "  Or press Ctrl+C to stop and authenticate now" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Waiting 5 seconds before continuing..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
    
    Write-Host ""
    Write-Host "Starting MCP server... (Use Ctrl+C to stop)" -ForegroundColor Cyan
    Write-Host ""
    
    # Background/foreground control
    $PidFile = Join-Path $ScriptDir "server.pid"
    $MetaFile = Join-Path $ScriptDir "server.meta.json"

    if ($Status) {
        Write-Host "MCP Server Status:" -ForegroundColor Cyan
        if (Test-Path $PidFile) {
            $pidValue = (Get-Content $PidFile | Out-String).Trim()
            Write-Host "  PID file: $PidFile -> $pidValue" -ForegroundColor Green
            try {
                $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
                if ($proc) {
                    Write-Host "  Process running: PID $($proc.Id) - $($proc.Path)" -ForegroundColor Green
                } else {
                    Write-Host "  PID file present but process not running." -ForegroundColor Yellow
                }
            } catch {
                Write-Host "  Could not inspect process: $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  No PID file present." -ForegroundColor Yellow
        }

        if (Test-Path $MetaFile) {
            Write-Host "  Meta file: $MetaFile" -ForegroundColor Green
            try {
                Get-Content $MetaFile | ConvertFrom-Json | Format-List | ForEach-Object { Write-Host "    $_" }
            } catch {
                Write-Host "    Failed to read meta file: $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  No meta file present." -ForegroundColor Yellow
        }

        # Also scan for matching processes
        try {
            $escapedPath = [regex]::Escape($ServerPath)
            $matching = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.Name -and ($_.Name -match 'python') -and ($_.CommandLine -match $escapedPath) }
            if ($matching) {
                Write-Host "  Found running server processes:" -ForegroundColor Green
                foreach ($proc in $matching) { Write-Host "    PID $($proc.ProcessId): $($proc.CommandLine)" }
            } else {
                Write-Host "  No running server.py processes found." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  Process scanning failed: $_" -ForegroundColor Yellow
        }

        exit 0
    }

    if ($StopBackground) {
        if (Test-Path $PidFile) {
            try {
                $pidValue = (Get-Content $PidFile | Out-String).Trim()
                $intRef = 0
                if ($pidValue -and [int]::TryParse($pidValue, [ref]$intRef)) {
                    Write-Host "Stopping background MCP server with PID $pidValue" -ForegroundColor Cyan
                    Stop-Process -Id $pidValue -ErrorAction SilentlyContinue
                    Remove-Item $PidFile -ErrorAction SilentlyContinue
                    # remove meta file if present
                    if (Test-Path $MetaFile) { Remove-Item $MetaFile -ErrorAction SilentlyContinue }
                    Write-Host "Stopped." -ForegroundColor Green
                    exit 0
                } else {
                    Write-Host "Invalid PID file. Removing." -ForegroundColor Yellow
                    Remove-Item $PidFile -ErrorAction SilentlyContinue
                }
            } catch {
                Write-Host "Failed to stop background process: $_" -ForegroundColor Yellow
            }
        } else {
            Write-Host "No background server PID file found." -ForegroundColor Yellow
            # Fallback: try to find any running python processes whose command line references server.py
            try {
                Write-Host "Searching for stray MCP server processes (looking for server.py in process command lines)..." -ForegroundColor Cyan
                $escapedPath = [regex]::Escape($ServerPath)
                # Only match processes running python where the command line contains the exact server path
                $matching = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.Name -and ($_.Name -match 'python') -and ($_.CommandLine -match $escapedPath) }
                if ($matching) {
                    foreach ($proc in $matching) {
                        $procId = $proc.ProcessId
                        $cmd = $proc.CommandLine
                        Write-Host "Stopping process PID $procId -> $cmd" -ForegroundColor Yellow
                        try {
                            Stop-Process -Id $procId -ErrorAction SilentlyContinue
                            Write-Host "Stopped PID $procId" -ForegroundColor Green
                        } catch {
                            # Wrap variables to avoid parsing issues when followed by punctuation
                            Write-Host ("Failed to stop PID {0}: {1}" -f $procId, $_) -ForegroundColor Yellow
                        }
                    }
                    # remove meta file if present
                    if (Test-Path $MetaFile) { Remove-Item $MetaFile -ErrorAction SilentlyContinue }
                    exit 0
                } else {
                    Write-Host "No running server.py processes found." -ForegroundColor Yellow
                }
            } catch {
                Write-Host "Failed while scanning processes: $_" -ForegroundColor Yellow
            }
        }
        exit 0
    }

    if ($Background) {
    # Start the server detached and save PID
        Write-Host "Starting MCP server in background..." -ForegroundColor Cyan
        $pythonExe = "python"
    $procArgs = "`"$ServerPath`""
        # If Dev mode requested, set CWD to repo root for editable install
        if ($Dev) {
            $RepoRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
            Push-Location $RepoRoot
            try {
                python -m pip install -e . --quiet
            } catch { }
            Pop-Location
        }

    # Use Start-Process to run detached and redirect logs
    $logPath = Join-Path $ScriptDir 'server.log'
    $errPath = Join-Path $ScriptDir 'server.err'
    # Use unbuffered python (-u) so logs are flushed promptly
    $procArgsArray = @('-u', $ServerPath)
    $proc = Start-Process -FilePath $pythonExe -ArgumentList $procArgsArray -RedirectStandardOutput $logPath -RedirectStandardError $errPath -WindowStyle Hidden -PassThru -WorkingDirectory $ScriptDir
    Write-Host "Logs redirected to: $logPath and $errPath" -ForegroundColor Gray
        if ($proc) {
            $proc.Id | Out-File -FilePath $PidFile -Encoding ascii
            Write-Host "Background server started (PID: $($proc.Id)). Use -StopBackground to stop." -ForegroundColor Green
            # write meta file with useful info
            try {
                $meta = [PSCustomObject]@{
                    pid = $proc.Id
                    startedAt = (Get-Date).ToString('o')
                    python = $pythonExe
                    serverPath = $ServerPath
                    workingDirectory = $ScriptDir
                    dev = [bool]$Dev
                    stdout = $logPath
                    stderr = $errPath
                }
                $meta | ConvertTo-Json -Depth 4 | Out-File -FilePath $MetaFile -Encoding utf8
            } catch {
                Write-Host "Warning: failed to write meta file: $_" -ForegroundColor Yellow
            }
            exit 0
        } else {
            Write-Host "Failed to start background server." -ForegroundColor Red
            exit 1
        }
    }

    # Run the Python MCP server directly (foreground)
    python $ServerPath
}
