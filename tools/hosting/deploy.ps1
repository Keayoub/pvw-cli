<#
.SYNOPSIS
    Deployment helper for Purview MCP Server → Azure Functions.

.DESCRIPTION
    Stages mcp code into this folder so Azure Functions can
    bundle it, then optionally deploys via 'func azure functionapp publish'
    or 'azd deploy'.

.PARAMETER StageOnly
    Copy the mcp files without deploying. Used by azd preprovision hook.

.PARAMETER FunctionAppName
    Name of the Azure Function App. Required when -Deploy is specified.

.PARAMETER ResourceGroup
    Azure Resource Group containing the Function App.

.PARAMETER Deploy
    Publish to Azure after staging.

.PARAMETER Clean
    Remove the staged mcp folder after deployment.

.EXAMPLE
    # Stage files only (used by azd hooks)
    ./deploy.ps1 -StageOnly

    # Full deploy via Azure Functions Core Tools
    ./deploy.ps1 -FunctionAppName my-pvw-mcp -ResourceGroup my-rg -Deploy

    # Stage + deploy + clean up staged files
    ./deploy.ps1 -FunctionAppName my-pvw-mcp -ResourceGroup my-rg -Deploy -Clean
#>
[CmdletBinding()]
param(
    [switch]$StageOnly,
    [string]$FunctionAppName,
    [string]$ResourceGroup,
    [switch]$Deploy,
    [switch]$Clean
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptDir = $PSScriptRoot
$AppDir   = Join-Path $ScriptDir "app"
$SourceDir = Join-Path $ScriptDir ".." "mcp"
$StagedDir = Join-Path $AppDir "mcp"

# ---------------------------------------------------------------------------
# Stage: copy mcp into this folder
# ---------------------------------------------------------------------------
Write-Host "Staging mcp from: $SourceDir" -ForegroundColor Cyan

if (-not (Test-Path $SourceDir)) {
    Write-Error "mcp not found at '$SourceDir'. Run this script from tools/hosting/."
}
}

# Remove stale staged copy
if (Test-Path $StagedDir) {
    Write-Host "Removing stale staged copy..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $StagedDir
}

# Copy, excluding dev-only artefacts
$excludeItems = @(
    "__pycache__", "*.pyc", "*.egg-info",
    ".venv", "Dockerfile", "docker-compose.yml",
    "diagnose.ps1", "docs"
)

Copy-Item -Recurse -Path $SourceDir -Destination $StagedDir

foreach ($pattern in $excludeItems) {
    Get-ChildItem -Recurse -Path $StagedDir -Filter $pattern -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Staged OK → $StagedDir" -ForegroundColor Green

if ($StageOnly) {
    Write-Host "StageOnly requested. Done." -ForegroundColor Green
    exit 0
}

# ---------------------------------------------------------------------------
# Deploy
# ---------------------------------------------------------------------------
if (-not $Deploy) {
    Write-Host ""
    Write-Host "Files staged. To deploy manually:" -ForegroundColor Yellow
    Write-Host "  func azure functionapp publish <FunctionAppName> --python" -ForegroundColor White
    Write-Host "  -or-"
    Write-Host "  azd deploy" -ForegroundColor White
    exit 0
}

if (-not $FunctionAppName) {
    Write-Error "-FunctionAppName is required when using -Deploy."
}

Write-Host "Deploying to Azure Functions app: $FunctionAppName ..." -ForegroundColor Cyan

$funcArgs = @("azure", "functionapp", "publish", $FunctionAppName, "--python")
if ($ResourceGroup) {
    $funcArgs += "--resource-group", $ResourceGroup
}

& func @funcArgs
if ($LASTEXITCODE -ne 0) { throw "func publish failed (exit $LASTEXITCODE)" }

Write-Host "Setting PYTHONPATH app setting..." -ForegroundColor Cyan
$azArgs = @(
    "functionapp", "config", "appsettings", "set",
    "--name", $FunctionAppName,
    "--settings", "PYTHONPATH=/home/site/wwwroot/.python_packages/lib/site-packages"
)
if ($ResourceGroup) { $azArgs += "--resource-group", $ResourceGroup }
& az @azArgs

# ---------------------------------------------------------------------------
# Optional: clean up staged copy
# ---------------------------------------------------------------------------
if ($Clean -and (Test-Path $StagedDir)) {
    Write-Host "Cleaning staged copy..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $StagedDir
}

Write-Host ""
Write-Host "Deployment complete." -ForegroundColor Green
Write-Host "MCP endpoint: https://$FunctionAppName.azurewebsites.net/mcp" -ForegroundColor Cyan
