#!/usr/bin/env pwsh
# Script to register Purview MCP Server in VS Code's MCP configuration

$mcpConfigPath = Join-Path $env:APPDATA "Code\User\mcp.json"

Write-Host "`n=== Registering Purview MCP Server ===" -ForegroundColor Cyan

# Read current config
if (Test-Path $mcpConfigPath) {
    Write-Host "[OK] Found existing mcp.json" -ForegroundColor Green
    $config = Get-Content $mcpConfigPath -Raw | ConvertFrom-Json
} else {
    Write-Host "[INFO] Creating new mcp.json" -ForegroundColor Yellow
    $config = @{
        servers = @{}
        inputs = @()
    } | ConvertTo-Json -Depth 10 | ConvertFrom-Json
}

# Find the installed Purview MCP extension
$purviewExt = Get-ChildItem -Path "$env:USERPROFILE\.vscode\extensions" -Directory |
    Where-Object { $_.Name -like 'keayoub.purview-mcp-server*' } |
    Sort-Object Name |
    Select-Object -Last 1

if (-not $purviewExt) {
    Write-Host "[ERROR] Purview MCP extension not found!" -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Found extension: $($purviewExt.Name)" -ForegroundColor Green

# Get extension path and read package.json for config
$extPath = $purviewExt.FullName
$pkgPath = Join-Path $extPath "package.json"
$pkg = Get-Content $pkgPath -Raw | ConvertFrom-Json

# Check if server already exists
$serverId = "chat.mcp.purview"
if ($config.servers.PSObject.Properties.Name -contains $serverId) {
    Write-Host "[INFO] Server '$serverId' already exists, updating..." -ForegroundColor Yellow
} else {
    Write-Host "[INFO] Adding new server '$serverId'..." -ForegroundColor Yellow
}

# Create server configuration
$serverPath = Join-Path $extPath "bundled\server.py"
$serverConfig = @{
    type = "stdio"
    command = "python"
    args = @(
        $serverPath.Replace('\', '/')
        "--no-banner"
    )
    env = @{
        PURVIEW_ACCOUNT_NAME = ""
        PURVIEW_ACCOUNT_ID = ""
        AZURE_TENANT_ID = ""
    }
}

# Add/update server in config
if ($config.servers -is [PSCustomObject]) {
    $config.servers | Add-Member -NotePropertyName $serverId -NotePropertyValue $serverConfig -Force
} else {
    $config.servers[$serverId] = $serverConfig
}

# Backup original file
if (Test-Path $mcpConfigPath) {
    $backupPath = "$mcpConfigPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item $mcpConfigPath $backupPath
    Write-Host "[OK] Backup created: $backupPath" -ForegroundColor Green
}

# Write updated config
$config | ConvertTo-Json -Depth 10 | Set-Content $mcpConfigPath -Encoding UTF8

Write-Host "`n[SUCCESS] Purview MCP Server registered!" -ForegroundColor Green
Write-Host "`nServer configuration:" -ForegroundColor Cyan
Write-Host "  ID: $serverId" -ForegroundColor White
Write-Host "  Command: python" -ForegroundColor White
Write-Host "  Script: $serverPath" -ForegroundColor White

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. RESTART VS Code (complete restart, not just reload)" -ForegroundColor Yellow
Write-Host "2. Configure environment variables in Settings:" -ForegroundColor Yellow
Write-Host "   - Purview Mcp: Account Name" -ForegroundColor White
Write-Host "   - Purview Mcp: Account Id" -ForegroundColor White
Write-Host "   - Purview Mcp: Tenant Id" -ForegroundColor White
Write-Host "3. Check extension details page for 'MCP Servers' section" -ForegroundColor Yellow
Write-Host "4. Try using @mcp in GitHub Copilot Chat" -ForegroundColor Yellow

Write-Host "`n=== Done ===" -ForegroundColor Green
