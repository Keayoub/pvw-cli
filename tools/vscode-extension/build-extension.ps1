#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build and package the Purview MCP VS Code extension with latest server files.

.DESCRIPTION
    This script automates the process of:
    1. Copying the latest server.py and requirements.txt from mcp/server to bundled/
    2. Building the TypeScript extension
    3. Packaging the extension into a .vsix file

.PARAMETER SkipBuild
    Skip the npm build step (useful if TypeScript hasn't changed)

.PARAMETER SkipPackage
    Skip the packaging step (useful for testing builds only)

.PARAMETER Clean
    Clean the dist/ directory before building

.EXAMPLE
    .\build-extension.ps1
    Full build and package

.EXAMPLE
    .\build-extension.ps1 -SkipBuild
    Only copy files and package (skip TypeScript compilation)

.EXAMPLE
    .\build-extension.ps1 -Clean
    Clean build with fresh dist/
#>

param(
    [switch]$SkipBuild,
    [switch]$SkipPackage,
    [switch]$Clean
)

# Color output functions
function Write-Step {
    param([string]$Message)
    Write-Host "`n▶ $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "  $Message" -ForegroundColor Gray
}

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "   Purview MCP Extension Builder" -ForegroundColor Magenta
Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor Magenta

# Step 1: Copy server files to bundled/
Write-Step "Copying server files from tools/PurviewMCPServer/ to bundled/"

$serverSource = Join-Path $scriptDir "..\PurviewMCPServer\server.py"
$requirementsSource = Join-Path $scriptDir "..\PurviewMCPServer\requirements.txt"
$diagnoseScriptSource = Join-Path $scriptDir "..\PurviewMCPServer\diagnose.ps1"
$bundledDir = Join-Path $scriptDir "bundled"
$serverDest = Join-Path $bundledDir "server.py"
$requirementsDest = Join-Path $bundledDir "requirements.txt"
$diagnoseScriptDest = Join-Path $bundledDir "diagnose.ps1"

# Create bundled directory if it doesn't exist
if (-not (Test-Path $bundledDir)) {
    New-Item -ItemType Directory -Path $bundledDir | Out-Null
    Write-Info "Created bundled/ directory"
}

# Check source files exist
if (-not (Test-Path $serverSource)) {
    Write-Error "server.py not found at: $serverSource"
    exit 1
}

if (-not (Test-Path $requirementsSource)) {
    Write-Error "requirements.txt not found at: $requirementsSource"
    exit 1
}

if (-not (Test-Path $diagnoseScriptSource)) {
    Write-Error "diagnose.ps1 not found at: $diagnoseScriptSource"
    exit 1
}

# Copy files
try {
    Copy-Item $serverSource $serverDest -Force
    $serverSize = (Get-Item $serverDest).Length / 1KB
    Write-Success "Copied server.py ($([math]::Round($serverSize, 2)) KB)"
    
    Copy-Item $requirementsSource $requirementsDest -Force
    $reqSize = (Get-Item $requirementsDest).Length / 1KB
    Write-Success "Copied requirements.txt ($([math]::Round($reqSize, 2)) KB)"
    
    Copy-Item $diagnoseScriptSource $diagnoseScriptDest -Force
    $diagnoseSize = (Get-Item $diagnoseScriptDest).Length / 1KB
    Write-Success "Copied diagnose.ps1 ($([math]::Round($diagnoseSize, 2)) KB)"
}
catch {
    Write-Error "Failed to copy files: $_"
    exit 1
}

# Step 2: Clean (optional)
if ($Clean) {
    Write-Step "Cleaning build artifacts"
    
    # Clean dist/ directory
    $distDir = Join-Path $scriptDir "dist"
    if (Test-Path $distDir) {
        Remove-Item $distDir -Recurse -Force
        Write-Success "Cleaned dist/"
    }
    
    # Clean package-lock.json
    $packageLock = Join-Path $scriptDir "package-lock.json"
    if (Test-Path $packageLock) {
        Remove-Item $packageLock -Force
        Write-Success "Removed package-lock.json"
    }
    
    # Clean node_modules/.cache if it exists
    $nodeCache = Join-Path $scriptDir "node_modules\.cache"
    if (Test-Path $nodeCache) {
        Remove-Item $nodeCache -Recurse -Force
        Write-Success "Cleaned node_modules/.cache"
    }
    
    # Clean .vsix files
    $vsixFiles = Get-ChildItem -Path $scriptDir -Filter "*.vsix"
    if ($vsixFiles.Count -gt 0) {
        $vsixFiles | Remove-Item -Force
        Write-Success "Removed old .vsix files ($($vsixFiles.Count) files)"
    }
}

# Step 3: Build TypeScript
if (-not $SkipBuild) {
    Write-Step "Building TypeScript (npm run build)"
    try {
        $buildOutput = npm run build 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Error "TypeScript build failed"
            Write-Info $buildOutput
            exit 1
        }
        Write-Success "TypeScript compiled successfully"
    }
    catch {
        Write-Error "Build failed: $_"
        exit 1
    }
}
else {
    Write-Info "Skipping TypeScript build (--SkipBuild flag)"
}

# Step 4: Package extension
if (-not $SkipPackage) {
    Write-Step "Packaging extension (npx @vscode/vsce package)"
    
    try {
        $packageOutput = npx @vscode/vsce package 2>&1 | Out-String
        
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Packaging failed"
            Write-Info $packageOutput
            exit 1
        }
        
        # Extract VSIX filename and size from output
        if ($packageOutput -match 'Packaged: (.+\.vsix) \((\d+) files, (.+)\)') {
            $vsixFile = Split-Path -Leaf $matches[1]
            $fileCount = $matches[2]
            $totalSize = $matches[3]
            
            Write-Success "Extension packaged successfully"
            Write-Info "File: $vsixFile"
            Write-Info "Files: $fileCount"
            Write-Info "Size: $totalSize"
            
            # Check if bundled files are included
            if ($packageOutput -match 'bundled/') {
                Write-Success "Bundled server files included ✓"
            }
            else {
                Write-Error "Warning: Bundled files might not be included!"
            }
        }
        else {
            Write-Success "Extension packaged"
        }
    }
    catch {
        Write-Error "Packaging failed: $_"
        exit 1
    }
}
else {
    Write-Info "Skipping packaging (--SkipPackage flag)"
}

# Summary
Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "   Build Complete! 🎉" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor Magenta

# Show next steps
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Install: " -NoNewline
Write-Host "code --install-extension .\$vsixFile --force" -ForegroundColor White
Write-Host "  2. Reload:  " -NoNewline
Write-Host "Ctrl+Shift+P → 'Developer: Reload Window'" -ForegroundColor White
Write-Host "  3. Test:    " -NoNewline
Write-Host "Ctrl+Shift+P → 'Purview MCP: Start Server'" -ForegroundColor White
Write-Host ""
