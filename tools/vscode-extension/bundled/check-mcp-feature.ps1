#!/usr/bin/env pwsh
# Script to check why MCP Servers feature is not showing in VS Code extension

Write-Host "`n=== Checking Purview MCP Extension ===" -ForegroundColor Cyan

# Find installed Purview MCP extensions
$purviewExts = Get-ChildItem -Path "$env:USERPROFILE\.vscode\extensions" -Directory |
    Where-Object { $_.Name -like 'keayoub.purview-mcp-server*' } |
    Sort-Object Name

Write-Host "`nInstalled Purview MCP versions:" -ForegroundColor Yellow
$purviewExts | ForEach-Object { Write-Host "  - $($_.Name)" }

if ($purviewExts.Count -eq 0) {
    Write-Host "`n[ERROR] No Purview MCP extension found!" -ForegroundColor Red
    exit 1
}

# Get the most recent version
$latestExt = $purviewExts | Select-Object -Last 1
Write-Host "`n[Using latest] $($latestExt.Name)" -ForegroundColor Green

# Read package.json
$pkgPath = Join-Path $latestExt.FullName 'package.json'
$pkg = Get-Content $pkgPath -Raw | ConvertFrom-Json

Write-Host "`n=== Checking MCP Configuration ===" -ForegroundColor Cyan

# Check if 'mcp' key exists at top level
if ($pkg.PSObject.Properties.Name -contains 'mcp') {
    Write-Host "[OK] Top-level 'mcp' key exists" -ForegroundColor Green
    
    if ($pkg.mcp.PSObject.Properties.Name -contains 'servers') {
        Write-Host "[OK] 'mcp.servers' key exists" -ForegroundColor Green
        
        $serverCount = ($pkg.mcp.servers.PSObject.Properties | Measure-Object).Count
        Write-Host "[OK] Found $serverCount server(s)" -ForegroundColor Green
        
        Write-Host "`n--- MCP Servers Configuration ---" -ForegroundColor Cyan
        $pkg.mcp.servers.PSObject.Properties | ForEach-Object {
            $serverId = $_.Name
            $server = $_.Value
            
            Write-Host "`nServer ID: $serverId" -ForegroundColor Yellow
            Write-Host "  Display Name: $($server.displayName)" -ForegroundColor White
            Write-Host "  Command: $($server.command)" -ForegroundColor White
            Write-Host "  Args: $($server.args -join ' ')" -ForegroundColor White
            
            if ($server.PSObject.Properties.Name -contains 'env') {
                Write-Host "  Environment variables:" -ForegroundColor White
                $server.env.PSObject.Properties | ForEach-Object {
                    Write-Host "    $($_.Name) = $($_.Value)" -ForegroundColor Gray
                }
            }
        }
    } else {
        Write-Host "[ERROR] 'mcp.servers' key is missing!" -ForegroundColor Red
    }
} else {
    Write-Host "[ERROR] Top-level 'mcp' key is missing!" -ForegroundColor Red
}

Write-Host "`n=== Comparing with Azure MCP Server ===" -ForegroundColor Cyan

# Find Azure MCP extension
$azureExt = Get-ChildItem -Path "$env:USERPROFILE\.vscode\extensions" -Directory |
    Where-Object { $_.Name -like 'ms-azuretools.azure-mcp*' } |
    Select-Object -First 1

if ($azureExt) {
    Write-Host "[Found] $($azureExt.Name)" -ForegroundColor Green
    
    $azurePkgPath = Join-Path $azureExt.FullName 'package.json'
    $azurePkg = Get-Content $azurePkgPath -Raw | ConvertFrom-Json
    
    if ($azurePkg.PSObject.Properties.Name -contains 'mcp') {
        Write-Host "`n--- Azure MCP Servers Configuration ---" -ForegroundColor Cyan
        $azurePkg.mcp.servers.PSObject.Properties | ForEach-Object {
            $serverId = $_.Name
            $server = $_.Value
            
            Write-Host "`nServer ID: $serverId" -ForegroundColor Yellow
            Write-Host "  Display Name: $($server.displayName)" -ForegroundColor White
            Write-Host "  Command: $($server.command)" -ForegroundColor White
        }
    }
} else {
    Write-Host "[NOT FOUND] Azure MCP Server extension not installed" -ForegroundColor Yellow
}

Write-Host "`n=== Recommendations ===" -ForegroundColor Cyan

if ($purviewExts.Count -gt 1) {
    Write-Host "[ISSUE] Multiple versions installed - this may cause confusion" -ForegroundColor Yellow
    Write-Host "        Uninstall old versions and keep only the latest" -ForegroundColor Yellow
}

Write-Host "`n[ACTION] After any changes, RESTART VS Code (not just reload)" -ForegroundColor Yellow
Write-Host "[ACTION] Check that bundled/server.py exists in the extension folder" -ForegroundColor Yellow
Write-Host "[ACTION] Verify the extension is enabled (not disabled)" -ForegroundColor Yellow

Write-Host "`n=== Done ===" -ForegroundColor Green
