#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build and package the Purview MCP VS Code extension with latest server files.

.DESCRIPTION
    This script automates the process of:
    1. Copying the latest server.py, requirements.txt, and scripts from tools/PurviewMCPServer/ to bundled/
    2. Building the TypeScript extension
    3. Packaging the extension into a .vsix file
    4. Optionally installing and registering the MCP server in VS Code

.PARAMETER SkipBuild
    Skip the npm build step (useful if TypeScript hasn't changed)

.PARAMETER SkipPackage
    Skip the packaging step (useful for testing builds only)

.PARAMETER Clean
    Clean the dist/ directory and old build artifacts before building

.PARAMETER RegisterServer
    After building and packaging, install the extension and register the MCP server
    in VS Code's MCP configuration file. This makes the server appear in the 
    "MCP Servers" section of the extension's Features tab.

.PARAMETER CheckMcpFeature
    Run diagnostic checks to verify the MCP server configuration and installation.
    Shows the current MCP configuration, installed extensions, and compares with
    other MCP extensions like Azure MCP Server.

.EXAMPLE
    .\build-extension.ps1
    Full build and package

.EXAMPLE
    .\build-extension.ps1 -Clean
    Clean build with fresh dist/

.EXAMPLE
    .\build-extension.ps1 -CheckMcpFeature
    Build, package, and check MCP feature configuration

.EXAMPLE
    .\build-extension.ps1 -RegisterServer
    Build, package, install, and register the MCP server automatically

.EXAMPLE
    .\build-extension.ps1 -Clean -RegisterServer -CheckMcpFeature
    Full clean build with automatic installation, MCP registration, and verification
#>

param(
    [switch]$SkipBuild,
    [switch]$SkipPackage,
    [switch]$Clean,
    [switch]$RegisterServer,
    [switch]$CheckMcpFeature
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
$registerScriptSource = Join-Path $scriptDir "scripts\register-mcp-server.ps1"
$checkMcpScriptSource = Join-Path $scriptDir "scripts\check-mcp-feature.ps1"
$bundledDir = Join-Path $scriptDir "bundled"
$scriptsDir = Join-Path $scriptDir "scripts"
$serverDest = Join-Path $bundledDir "server.py"
$requirementsDest = Join-Path $bundledDir "requirements.txt"
$diagnoseScriptDest = Join-Path $bundledDir "diagnose.ps1"
$registerScriptDest = Join-Path $bundledDir "register-mcp-server.ps1"
$checkMcpScriptDest = Join-Path $bundledDir "check-mcp-feature.ps1"

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

if (-not (Test-Path $registerScriptSource)) {
    Write-Error "register-mcp-server.ps1 not found at: $registerScriptSource"
    exit 1
}

if (-not (Test-Path $checkMcpScriptSource)) {
    Write-Error "check-mcp-feature.ps1 not found at: $checkMcpScriptSource"
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
    
    Copy-Item $registerScriptSource $registerScriptDest -Force
    $registerSize = (Get-Item $registerScriptDest).Length / 1KB
    Write-Success "Copied register-mcp-server.ps1 ($([math]::Round($registerSize, 2)) KB)"
    
    Copy-Item $checkMcpScriptSource $checkMcpScriptDest -Force
    $checkSize = (Get-Item $checkMcpScriptDest).Length / 1KB
    Write-Success "Copied check-mcp-feature.ps1 ($([math]::Round($checkSize, 2)) KB)"
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

# Step 5: Check MCP Feature (optional)
if ($CheckMcpFeature) {
    Write-Step "Checking MCP Feature configuration"
    
    try {
        Write-Info "Running MCP feature check..."
        & $checkMcpScriptSource
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCP Feature check completed"
        }
        else {
            Write-Error "MCP Feature check encountered issues"
        }
    }
    catch {
        Write-Error "Failed to run MCP feature check: $_"
    }
}

# Step 6: Register MCP Server (optional)
if ($RegisterServer) {
    Write-Step "Registering MCP Server in VS Code configuration"
    
    # Install the extension first if VSIX was built
    if (-not $SkipPackage -and (Test-Path $vsixFile)) {
        Write-Info "Installing extension..."
        $installOutput = code --install-extension ".\$vsixFile" --force 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Extension installed"
        }
        else {
            Write-Error "Extension installation failed"
            Write-Info $installOutput
        }
    }
    
    # Run the registration script
    try {
        Write-Info "Running registration script..."
        $registerOutput = & $registerScriptSource 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCP Server registered successfully"
            Write-Info "The Purview MCP server has been added to VS Code's MCP configuration"
        }
        else {
            Write-Error "Registration failed"
            Write-Info $registerOutput
        }
    }
    catch {
        Write-Error "Failed to register MCP server: $_"
    }
    
    # Run MCP feature check after registration
    if ($CheckMcpFeature) {
        Write-Host ""
        Write-Step "Verifying MCP Feature after registration"
        
        try {
            & $checkMcpScriptSource
        }
        catch {
            Write-Error "Failed to verify MCP feature: $_"
        }
    }
}

# Summary
Write-Host "`n═══════════════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "   Build Complete! 🎉" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════`n" -ForegroundColor Magenta

# Show next steps
Write-Host "Next steps:" -ForegroundColor Yellow
if (-not $RegisterServer) {
    Write-Host "  1. Check:    " -NoNewline
    Write-Host ".\build-extension.ps1 -CheckMcpFeature" -ForegroundColor White
    Write-Host "     (verify current MCP configuration)" -ForegroundColor Gray
    Write-Host "  2. Install:  " -NoNewline
    Write-Host "code --install-extension .\$vsixFile --force" -ForegroundColor White
    Write-Host "  3. Register: " -NoNewline
    Write-Host ".\build-extension.ps1 -RegisterServer" -ForegroundColor White
    Write-Host "     (or manually: .\bundled\register-mcp-server.ps1)" -ForegroundColor Gray
    Write-Host "  4. Restart:  " -NoNewline
    Write-Host "Completely restart VS Code (not just reload)" -ForegroundColor White
    Write-Host "  5. Test:     " -NoNewline
    Write-Host "Type @mcp in GitHub Copilot Chat" -ForegroundColor White
}
else {
    Write-Host "  1. RESTART VS Code completely (not just reload)" -ForegroundColor White
    Write-Host "  2. Configure settings: Purview MCP Account Name/ID/Tenant" -ForegroundColor White
    Write-Host "  3. Check extension Features tab for 'MCP Servers' section" -ForegroundColor White
    Write-Host "  4. Test with @mcp in GitHub Copilot Chat" -ForegroundColor White
    if (-not $CheckMcpFeature) {
        Write-Host "  5. Verify:   " -NoNewline
        Write-Host ".\build-extension.ps1 -CheckMcpFeature" -ForegroundColor White
        Write-Host "     (optional: verify MCP configuration)" -ForegroundColor Gray
    }
}
Write-Host ""
