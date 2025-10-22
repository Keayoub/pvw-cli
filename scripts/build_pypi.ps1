<#
Build and Deploy Script for pvw-cli Package (PowerShell / pwsh)

This script performs the same actions as build_pypi.bat but uses PowerShell features:
- install/upgrade build tools using python -m pip
- clean previous builds
- verify package version
- build (sdist + wheel) using python -m build
- validate with twine
- test local installation of the wheel

Usage (PowerShell):
  pwsh -NoProfile -ExecutionPolicy Bypass -File .\build_pypi.ps1

Notes:
  - For uploads to PyPI use: python -m twine upload dist/*  (requires credentials)
  - Prefer running inside a virtualenv or CI to avoid changing global packages interactively
#>

function Write-Info($m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Success($m) { Write-Host "[OK] $m" -ForegroundColor Green }
function Write-ErrorAndExit($m, $code=1) { Write-Host "[ERROR] $m" -ForegroundColor Red; exit $code }

Write-Host "`n========================================"
Write-Host "Building pvw-cli Package"
Write-Host "========================================`n"

Write-Info "Installing/updating build dependencies (python -m pip)..."
& python -m pip install --upgrade build twine setuptools wheel
if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Failed to install build dependencies" 1 }
Write-Success "Build dependencies installed successfully`n"

Write-Info "Cleaning previous builds..."
if (Test-Path build) { Remove-Item -Recurse -Force build; Write-Host "  Removed build/" }
if (Test-Path dist) { Remove-Item -Recurse -Force dist; Write-Host "  Removed dist/" }
if (Test-Path *.egg-info) { Get-ChildItem -Filter *.egg-info | Remove-Item -Recurse -Force; Write-Host "  Removed egg-info/" }
Write-Success "Previous builds cleaned`n"

Write-Info "Checking version consistency (reads purviewcli.__version__)..."
$verCmd = "import sys; sys.path.insert(0, '.'); from purviewcli import __version__; print(__version__)"
try {
    $verOutput = & python -c $verCmd 2>&1
} catch {
    Write-ErrorAndExit "Failed to run python to read version: $_" 2
}
if ($LASTEXITCODE -ne 0) { Write-Host $verOutput; Write-ErrorAndExit "Failed to read version from purviewcli/__init__.py" 3 }
Write-Host "📋 Current version: $verOutput`n"

Write-Info "Building package (python -m build)..."
& python -m build
if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Package build failed" 4 }
Write-Success "Package built successfully`n"

Write-Info "Build artifacts in dist/:"
if (Test-Path dist) { 
    Get-ChildItem -Path dist -File | ForEach-Object { 
        $sizeKB = [math]::Round($_.Length / 1024, 1)
        Write-Host ('   {0} ({1} KB)' -f $_.Name, $sizeKB)
    } 
} else { 
    Write-Host '  (no dist directory found)' 
}
Write-Host ''

Write-Info "Validating package with twine..."
& python -m twine check dist/*
if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Package validation failed" 5 }
Write-Success "Package validation passed`n"

Write-Info 'Testing local installation (first wheel found)...'
$wheel = Get-ChildItem -Path dist -Filter *.whl -File | Select-Object -First 1
if (-not $wheel) { Write-ErrorAndExit 'No wheel file found in dist/ to test.' 6 }
Write-Host "  Installing: $($wheel.Name)"
& python -m pip install --force-reinstall "dist\$($wheel.Name)"
if ($LASTEXITCODE -ne 0) { Write-ErrorAndExit "Local installation failed" 7 }
Write-Success "Local installation succeeded`n"

Write-Info "Testing pvw command..."
try {
    $pvwVer = & pvw --version 2>&1
} catch {
    Write-ErrorAndExit "pvw command not found or failed: $_" 8
}
Write-Host $pvwVer

Write-Info "Testing UC help output for expected text..."
$helpOut = & pvw uc --help 2>&1 | Out-String
if ($helpOut -notmatch 'Manage Unified Catalog') {
    Write-ErrorAndExit "UC command test failed - expected 'Manage Unified Catalog' in help output" 9
}
Write-Success "Command tests passed`n"

Write-Host "========================================"
Write-Host "✅ Build Complete and Verified!"
Write-Host "========================================`n"

Write-Host "📤 Deployment Options:`n"
Write-Host "  Upload to PyPI Test (recommended first):`n  python -m twine upload --repository testpypi dist/*`n"
Write-Host "  Upload to Production PyPI:`n  python -m twine upload dist/*`n"
Write-Host "  Install from TestPyPI:`n  pip install --index-url https://test.pypi.org/simple/ pvw-cli`n"
Write-Host "Tips:`n  - Test installation from TestPyPI before production upload`n  - Ensure TWINE_USERNAME and TWINE_PASSWORD are set for automated upload`n  - Use API tokens instead of passwords for better security`n"

Write-Host "Package Info:`n"
if (Test-Path dist) { 
    Get-ChildItem -Path dist -File | ForEach-Object { 
        $sizeKB = [math]::Round($_.Length / 1024, 1)
        Write-Host ('   [package] {0} ({1} KB)' -f $_.Name, $sizeKB)
    } 
}

exit 0
