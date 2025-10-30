# Stop the background Purview MCP server (convenience wrapper)
param()

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartScript = Join-Path $ScriptDir 'start-mcp.ps1'

if (-not (Test-Path $StartScript)) {
    Write-Host "start-mcp.ps1 not found in $ScriptDir" -ForegroundColor Red
    exit 1
}

# Delegate stopping to start-mcp.ps1's -StopBackground
& "$StartScript" -StopBackground

# If PID file remains, attempt manual stop
$PidFile = Join-Path $ScriptDir 'server.pid'
if (Test-Path $PidFile) {
    try {
        $pidValue = (Get-Content $PidFile | Out-String).Trim()
        $intRef = 0
        if ($pidValue -and [int]::TryParse($pidValue, [ref]$intRef)) {
            Stop-Process -Id $pidValue -ErrorAction SilentlyContinue
            Remove-Item $PidFile -ErrorAction SilentlyContinue
            Write-Host "Stopped process $pidValue" -ForegroundColor Green
        }
    } catch {
        Write-Host "Failed to stop background process: $_" -ForegroundColor Yellow
    }
}
