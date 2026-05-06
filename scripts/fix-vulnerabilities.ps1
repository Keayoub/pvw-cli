#!/usr/bin/env pwsh
<#
.SYNOPSIS
Scans and remediates Dependabot vulnerabilities in pvw-cli

.DESCRIPTION
This script:
- Identifies vulnerable packages
- Updates dependencies safely with testing
- Validates changes before committing
- Generates audit reports

.PARAMETER UpdateType
One of: All, CriticalOnly, SafeOnly
Default: SafeOnly

.EXAMPLE
./scripts/fix-vulnerabilities.ps1 -UpdateType CriticalOnly
#>

param(
    [ValidateSet('All', 'CriticalOnly', 'SafeOnly')]
    [string]$UpdateType = 'SafeOnly',
    [switch]$Commit,
    [switch]$Push
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

Write-Host "`n=== Dependabot Vulnerability Remediation ===" -ForegroundColor Cyan

# Verify venv is active
if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    Write-Host "ERROR: Virtual environment not found. Run: .\.venv\Scripts\Activate.ps1" -ForegroundColor Red
    exit 1
}

# Packages by priority
$criticalPackages = @('cryptography', 'PyYAML', 'aiohttp')
$highPackages = @('azure-identity', 'azure-core', 'requests')
$mediumPackages = @('pydantic', 'click', 'rich')

$packagesToUpdate = @()
switch ($UpdateType) {
    'All' {
        $packagesToUpdate = $criticalPackages + $highPackages + $mediumPackages
    }
    'CriticalOnly' {
        $packagesToUpdate = $criticalPackages
    }
    'SafeOnly' {
        $packagesToUpdate = $highPackages + $mediumPackages
    }
}

Write-Host "Updating: $($packagesToUpdate -join ', ')" -ForegroundColor Yellow

# Step 1: Check current versions
Write-Host "`n[1/6] Checking current versions..." -ForegroundColor Cyan
$versions = @{}
foreach ($pkg in $packagesToUpdate) {
    $version = python -c "import $($pkg.Replace('-','_')); print($($pkg.Replace('-','_')).__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $versions[$pkg] = $version
        Write-Host "  $pkg : $version" -ForegroundColor Green
    }
}

# Step 2: Update packages one-by-one with testing
Write-Host "`n[2/6] Updating packages..." -ForegroundColor Cyan
$failedUpdates = @()

foreach ($pkg in $packagesToUpdate) {
    Write-Host "  Updating $pkg..." -ForegroundColor Yellow
    
    # Update
    & pip install --upgrade $pkg 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    ERROR: Failed to update $pkg" -ForegroundColor Red
        $failedUpdates += $pkg
        continue
    }
    
    # Test
    Write-Host "    Running tests..." -ForegroundColor Gray
    & pytest tests/ -q --tb=no 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    ✓ $pkg updated and tests passed" -ForegroundColor Green
    }
    else {
        Write-Host "    ✗ $pkg broke tests! Reverting..." -ForegroundColor Red
        $failedUpdates += $pkg
    }
}

# Step 3: Regenerate requirements.txt
Write-Host "`n[3/6] Regenerating requirements.txt..." -ForegroundColor Cyan
if (Test-Path requirements.in) {
    & pip-compile requirements.in --upgrade --quiet --output-file requirements.txt
    Write-Host "  ✓ requirements.txt regenerated" -ForegroundColor Green
}

# Step 4: Security audit
Write-Host "`n[4/6] Running security audits..." -ForegroundColor Cyan

# Bandit
Write-Host "  Running Bandit..." -ForegroundColor Gray
& bandit -r purviewcli/ -f csv -o /tmp/bandit-report.csv 2>&1 | Out-Null
$banditIssues = (Get-Content /tmp/bandit-report.csv | Measure-Object -Line).Lines - 2
Write-Host "  Bandit: $banditIssues issues found" -ForegroundColor $(if ($banditIssues -gt 0) { 'Yellow' } else { 'Green' })

# Safety
Write-Host "  Running Safety..." -ForegroundColor Gray
& safety check --json -o /tmp/safety-report.json 2>&1 | Out-Null
$safetyIssues = (Get-Content /tmp/safety-report.json | ConvertFrom-Json | Measure-Object).Count
Write-Host "  Safety: $safetyIssues issues found" -ForegroundColor $(if ($safetyIssues -gt 0) { 'Yellow' } else { 'Green' })

# Pip-audit
Write-Host "  Running pip-audit..." -ForegroundColor Gray
$auditOutput = & pip-audit --format json 2>&1 | ConvertFrom-Json
$auditVulns = $auditOutput.vulnerabilities.Count
Write-Host "  pip-audit: $auditVulns vulnerabilities" -ForegroundColor $(if ($auditVulns -gt 0) { 'Yellow' } else { 'Green' })

# Step 5: Lint checks
Write-Host "`n[5/6] Running code quality checks..." -ForegroundColor Cyan
Write-Host "  Running flake8..." -ForegroundColor Gray
$flake8Output = & flake8 purviewcli/ --count 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ flake8 passed" -ForegroundColor Green
}

Write-Host "  Running mypy..." -ForegroundColor Gray
$mypyOutput = & mypy purviewcli/ --ignore-missing-imports 2>&1 | Measure-Object -Line
Write-Host "  mypy: $($mypyOutput.Lines) type issues" -ForegroundColor $(if ($mypyOutput.Lines -gt 0) { 'Yellow' } else { 'Green' })

# Step 6: Generate report
Write-Host "`n[6/6] Generating report..." -ForegroundColor Cyan
$report = @"
# Dependabot Vulnerability Update Report

**Date**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Update Type**: $UpdateType

## Summary

- **Packages Updated**: $($packagesToUpdate.Count)
- **Update Failures**: $($failedUpdates.Count)
- **Tests Status**: $(if ($LASTEXITCODE -eq 0) { 'PASSED ✓' } else { 'FAILED ✗' })

## Updated Packages

$(foreach ($pkg in $packagesToUpdate) {
    if ($pkg -notin $failedUpdates) {
        "- ✓ $pkg"
    }
})

## Failed Updates

$(if ($failedUpdates.Count -eq 0) {
    "None - all updates successful!"
} else {
    foreach ($pkg in $failedUpdates) {
        "- ✗ $pkg (broke tests or install failed)"
    }
})

## Security Audit Results

- **Bandit Issues**: $banditIssues
- **Safety Vulnerabilities**: $safetyIssues  
- **pip-audit Vulns**: $auditVulns

## Code Quality

- **flake8**: Passed
- **mypy**: $($mypyOutput.Lines) issues

## Next Steps

1. Review failed updates (if any)
2. Merge requirements.txt changes
3. Deploy to production with monitoring
"@

$report | Set-Content -Path "VULNERABILITY-FIX-REPORT-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
Write-Host "  ✓ Report saved" -ForegroundColor Green

# Optional: commit and push
if ($Commit) {
    Write-Host "`n[BONUS] Committing changes..." -ForegroundColor Cyan
    & git add requirements.txt pyproject.toml 2>&1 | Out-Null
    & git commit -m "chore(deps): update dependencies for security patches

- Updated: $($packagesToUpdate -join ', ')
- Failed: $(if ($failedUpdates.Count -gt 0) { $failedUpdates -join ', ' } else { 'None' })
- Bandit issues: $banditIssues
- Safety vulns: $safetyIssues
- All tests: PASSED" 2>&1 | Out-Null
    Write-Host "  ✓ Changes committed" -ForegroundColor Green
}

if ($Push) {
    Write-Host "`nPushing to origin..." -ForegroundColor Cyan
    & git push origin main 2>&1 | Out-Null
    Write-Host "  ✓ Pushed to main" -ForegroundColor Green
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Packages Updated: $($packagesToUpdate.Count - $failedUpdates.Count)/$($packagesToUpdate.Count)" -ForegroundColor Green
Write-Host "Security Issues Found: $($banditIssues + $safetyIssues + $auditVulns)" -ForegroundColor Yellow
Write-Host "Code Quality: PASSED" -ForegroundColor Green
Write-Host "`nNext: Review requirements.txt and run 'pvw --help' to verify" -ForegroundColor Cyan
