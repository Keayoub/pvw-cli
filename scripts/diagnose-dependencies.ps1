#!/usr/bin/env pwsh
<#
.SYNOPSIS
Diagnose dependency update issues and test environment

.EXAMPLE
./scripts/diagnose-dependencies.ps1
#>

Write-Host "`n=== Dependency Diagnostic Report ===" -ForegroundColor Cyan

# 1. Python & Environment
Write-Host "`n[1] Python Environment" -ForegroundColor Cyan
python --version
python -c "import sys; print('Pip: ' + sys.version.split()[0])"

# 2. Current Dependency Versions
Write-Host "`n[2] Critical Package Versions" -ForegroundColor Cyan
$packages = @(
    'cryptography',
    'PyYAML', 
    'aiohttp',
    'azure-identity',
    'azure-core',
    'requests',
    'pydantic',
    'click',
    'rich'
)

$packages | ForEach-Object {
    try {
        $version = python -c "import pkg_resources; print(pkg_resources.get_distribution('$_').version)" 2>$null
        Write-Host "  $_ : $version" -ForegroundColor Green
    }
    catch {
        Write-Host "  $_ : NOT INSTALLED" -ForegroundColor Yellow
    }
}

# 3. Test Environment
Write-Host "`n[3] Test Environment" -ForegroundColor Cyan
try {
    $pytestVersion = python -c "import pytest; print(pytest.__version__)" 2>$null
    Write-Host "  pytest : $pytestVersion" -ForegroundColor Green
} catch {
    Write-Host "  pytest : NOT INSTALLED (required for tests)" -ForegroundColor Red
}

# 4. Test Count
Write-Host "`n[4] Test Discovery" -ForegroundColor Cyan
$testFiles = @(Get-ChildItem tests/*.py -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Host "  Test files: $testFiles"

if ($testFiles -gt 0) {
    try {
        $testCount = python -m pytest tests/ --collect-only -q 2>$null | Measure-Object
        Write-Host "  Total tests: $($testCount.Count)"
    } catch {
        Write-Host "  Could not collect tests" -ForegroundColor Yellow
    }
}

# 5. Try running one test
Write-Host "`n[5] Test Execution" -ForegroundColor Cyan
$testFile = Get-ChildItem tests/test_*.py | Select-Object -First 1
if ($testFile) {
    Write-Host "  Running: $($testFile.Name)..." -ForegroundColor Gray
    $output = python -m pytest $testFile.FullName -v 2>&1 | Select-Object -Last 20
    if ($output) {
        $output | ForEach-Object { Write-Host "    $_" -ForegroundColor Yellow }
    } else {
        Write-Host "    (No output - check if pytest is installed)" -ForegroundColor Yellow
    }
}

# 6. Security Tools
Write-Host "`n[6] Security Tools" -ForegroundColor Cyan
$tools = @('bandit', 'safety', 'pip-audit')
$tools | ForEach-Object {
    try {
        python -m $_ --version 2>$null | Out-Null
        Write-Host "  $_ : INSTALLED" -ForegroundColor Green
    } catch {
        Write-Host "  $_ : NOT INSTALLED" -ForegroundColor Yellow
    }
}

# 7. Recommendations
Write-Host "`n[7] Recommendations" -ForegroundColor Cyan

$recommendations = @()

$testFile = Get-ChildItem tests/test_*.py -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $testFile) {
    $recommendations += "- No tests found in tests/ directory"
}

try {
    python -c "import pytest" 2>$null
} catch {
    $recommendations += "- Install pytest: pip install pytest pytest-asyncio"
}

if ($recommendations.Count -eq 0) {
    $recommendations = @("- Environment looks good. Try running updates with '-SkipTests' flag")
}

$recommendations | ForEach-Object { Write-Host $_ }

Write-Host "`n=== Next Steps ===" -ForegroundColor Cyan
Write-Host "1. Run: .\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -SkipTests" -ForegroundColor Yellow
Write-Host "2. Or: .\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -DryRun" -ForegroundColor Yellow
Write-Host "3. Check report: VULNERABILITY-FIX-REPORT-*.md" -ForegroundColor Yellow
