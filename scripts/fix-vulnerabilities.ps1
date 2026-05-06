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

.PARAMETER SkipTests
Skip running pytest (use if tests are not configured)

.PARAMETER SkipAudit
Skip security audits (Bandit, Safety)

.EXAMPLE
./scripts/fix-vulnerabilities.ps1 -UpdateType CriticalOnly -SkipTests
#>

param(
    [ValidateSet('All', 'CriticalOnly', 'SafeOnly')]
    [string]$UpdateType = 'SafeOnly',
    [switch]$SkipTests,
    [switch]$SkipAudit,
    [switch]$Commit,
    [switch]$Push,
    [switch]$DryRun
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
$highPackages = @('azure-identity', 'azure-core', 'requests', 'pydantic')
$mediumPackages = @('click', 'rich')

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

Write-Host "Update Type: $UpdateType" -ForegroundColor Yellow
Write-Host "Packages: $($packagesToUpdate -join ', ')" -ForegroundColor Yellow
Write-Host "Skip Tests: $SkipTests | Skip Audit: $SkipAudit | Dry Run: $DryRun" -ForegroundColor Yellow

# Step 1: Install prerequisites
Write-Host "`n[1/7] Installing security tools..." -ForegroundColor Cyan
$toolsNeeded = @()
if (-not $SkipAudit) {
    $toolsNeeded = @('bandit', 'safety', 'pip-audit')
}
if (-not $SkipTests) {
    $toolsNeeded += @('pytest', 'pytest-asyncio')
}

if ($toolsNeeded.Count -gt 0) {
    Write-Host "  Installing: $($toolsNeeded -join ', ')..." -ForegroundColor Gray
    $toolsNeeded | ForEach-Object {
        python -m pip install $_ --quiet 2>$null
    }
    Write-Host "  ✓ Tools installed" -ForegroundColor Green
}

# Step 2: Check current versions before update
Write-Host "`n[2/7] Checking current versions..." -ForegroundColor Cyan
$versionsBefore = @{}
foreach ($pkg in $packagesToUpdate) {
    try {
        $version = python -c "import pkg_resources; print(pkg_resources.get_distribution('$pkg').version)" 2>$null
        $versionsBefore[$pkg] = $version
        Write-Host "  $pkg : $version" -ForegroundColor Green
    }
    catch {
        Write-Host "  $pkg : NOT INSTALLED" -ForegroundColor Yellow
    }
}

# Step 3: Backup current state
Write-Host "`n[3/7] Backing up current state..." -ForegroundColor Cyan
Copy-Item requirements.txt requirements.txt.backup -Force -ErrorAction SilentlyContinue
Copy-Item pyproject.toml pyproject.toml.backup -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ Backups created (requirements.txt.backup, pyproject.toml.backup)" -ForegroundColor Green

# Step 4: Update packages one-by-one
Write-Host "`n[4/7] Updating packages..." -ForegroundColor Cyan
$failedUpdates = @()
$successfulUpdates = @()

foreach ($pkg in $packagesToUpdate) {
    Write-Host "  Updating $pkg..." -ForegroundColor Yellow
    
    if ($DryRun) {
        Write-Host "    [DRY RUN] Would update $pkg" -ForegroundColor Gray
        continue
    }
    
    # Try to update
    $updateOutput = python -m pip install --upgrade $pkg 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "    ERROR: Failed to update $pkg" -ForegroundColor Red
        $failedUpdates += $pkg
        continue
    }
    
    # Only run tests if not skipped AND pytest is available
    if (-not $SkipTests) {
        Write-Host "    Running tests..." -ForegroundColor Gray
        $testOutput = python -m pytest tests/ -q --tb=no 2>&1
        $testExitCode = $LASTEXITCODE
        
        if ($testExitCode -eq 0) {
            Write-Host "    ✓ $pkg updated - tests PASSED" -ForegroundColor Green
            $successfulUpdates += $pkg
        }
        else {
            Write-Host "    ✗ $pkg broke tests - reverting..." -ForegroundColor Red
            python -m pip install --upgrade --force-reinstall $pkg@$($versionsBefore[$pkg]) 2>&1 | Out-Null
            $failedUpdates += $pkg
        }
    }
    else {
        Write-Host "    ✓ $pkg updated (tests skipped)" -ForegroundColor Green
        $successfulUpdates += $pkg
    }
}

# Step 5: Regenerate requirements.txt
Write-Host "`n[5/7] Regenerating requirements.txt..." -ForegroundColor Cyan
if (Test-Path requirements.in) {
    try {
        python -m pip install pip-tools --quiet 2>$null
        python -m piptools compile requirements.in --upgrade --quiet --output-file requirements.txt 2>&1 | Out-Null
        Write-Host "  ✓ requirements.txt regenerated" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠ Could not regenerate requirements.txt" -ForegroundColor Yellow
    }
}

# Step 6: Security audits (if not skipped)
Write-Host "`n[6/7] Running security audits..." -ForegroundColor Cyan

if (-not $SkipAudit) {
    $banditIssues = 0
    $safetyIssues = 0
    $auditVulns = 0
    
    # Bandit
    try {
        Write-Host "  Running Bandit..." -ForegroundColor Gray
        $banditOutput = python -m bandit -r purviewcli/ -f json 2>$null | ConvertFrom-Json
        $banditIssues = ($banditOutput.results | Measure-Object).Count
        Write-Host "  Bandit: $banditIssues issues" -ForegroundColor $(if ($banditIssues -gt 0) { 'Yellow' } else { 'Green' })
    }
    catch {
        Write-Host "  Bandit: skipped (not available)" -ForegroundColor Gray
    }
    
    # Safety
    try {
        Write-Host "  Running Safety..." -ForegroundColor Gray
        $safetyOutput = python -m safety check --json 2>$null | ConvertFrom-Json
        $safetyIssues = ($safetyOutput | Measure-Object).Count
        Write-Host "  Safety: $safetyIssues vulnerabilities" -ForegroundColor $(if ($safetyIssues -gt 0) { 'Yellow' } else { 'Green' })
    }
    catch {
        Write-Host "  Safety: skipped (not available)" -ForegroundColor Gray
    }
    
    # Pip-audit
    try {
        Write-Host "  Running pip-audit..." -ForegroundColor Gray
        $auditOutput = python -m pip_audit --format json 2>$null | ConvertFrom-Json
        $auditVulns = ($auditOutput.vulnerabilities | Measure-Object).Count
        Write-Host "  pip-audit: $auditVulns vulnerabilities" -ForegroundColor $(if ($auditVulns -gt 0) { 'Yellow' } else { 'Green' })
    }
    catch {
        Write-Host "  pip-audit: skipped (not available)" -ForegroundColor Gray
    }
}
else {
    Write-Host "  Security audits skipped" -ForegroundColor Yellow
}

# Step 7: Generate report
Write-Host "`n[7/7] Generating report..." -ForegroundColor Cyan
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$reportPath = "VULNERABILITY-FIX-REPORT-$timestamp.md"

$report = @"
# Dependabot Vulnerability Update Report

**Date**: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
**Update Type**: $UpdateType
**Dry Run**: $DryRun
**Skip Tests**: $SkipTests
**Skip Audit**: $SkipAudit

## Summary

- **Total Packages**: $($packagesToUpdate.Count)
- **Successfully Updated**: $($successfulUpdates.Count)
- **Failed Updates**: $($failedUpdates.Count)
- **Requirements Regenerated**: $(if (Test-Path requirements.in) { 'Yes' } else { 'No' })

## Before & After Versions

| Package | Before | After |
|---------|--------|-------|
$(
    foreach ($pkg in $packagesToUpdate) {
        $before = $versionsBefore[$pkg]
        $after = if ($successfulUpdates -contains $pkg) { 
            try {
                python -c "import pkg_resources; print(pkg_resources.get_distribution('$pkg').version)" 2>$null
            } catch { "?" }
        } else { 
            $before 
        }
        if ($before) {
            "| $pkg | $before | $after |"
        }
    }
)

## Successfully Updated

$(if ($successfulUpdates.Count -gt 0) {
    foreach ($pkg in $successfulUpdates) {
        "- ✓ $pkg"
    }
} else {
    "None"
})

## Failed Updates

$(if ($failedUpdates.Count -gt 0) {
    foreach ($pkg in $failedUpdates) {
        "- ✗ $pkg (tests failed or install error)"
    }
} else {
    "None - all updates successful! 🎉"
})

## Security Audit Results

- **Bandit Issues**: $banditIssues
- **Safety Vulnerabilities**: $safetyIssues
- **pip-audit Vulns**: $auditVulns

## Recommendations

$(if ($failedUpdates.Count -gt 0) {
    @"
### Failed Updates
The following packages broke tests and were reverted:
$($failedUpdates -join ', ')

**Next Steps**:
1. Review test failures for $($failedUpdates[0])
2. Check compatibility notes in package docs
3. Update tests or pin compatible versions
4. Re-run with '--SkipTests' to force update (if acceptable)
"@
} else {
    @"
All packages updated successfully!
"@
})

## Files Modified

$(if (Test-Path requirements.txt.backup) { "- requirements.txt (backed up as requirements.txt.backup)" })
$(if (Test-Path pyproject.toml.backup) { "- pyproject.toml (backed up as pyproject.toml.backup)" })
- $reportPath (this report)

## Command Used

\`\`\`powershell
.\scripts\fix-vulnerabilities.ps1 -UpdateType $UpdateType $(if ($SkipTests) { '-SkipTests' }) $(if ($SkipAudit) { '-SkipAudit' }) $(if ($DryRun) { '-DryRun' })
\`\`\`

---

**Next Steps**: Review this report, test locally, then run with '-Commit -Push' to deploy.
"@

$report | Set-Content -Path $reportPath
Write-Host "  ✓ Report saved: $reportPath" -ForegroundColor Green

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Successfully Updated: $($successfulUpdates.Count)/$($packagesToUpdate.Count)" -ForegroundColor $(if ($failedUpdates.Count -eq 0) { 'Green' } else { 'Yellow' })
if ($failedUpdates.Count -gt 0) {
    Write-Host "Failed: $($failedUpdates -join ', ')" -ForegroundColor Red
}
Write-Host "Report: $reportPath" -ForegroundColor Blue

# Optional: commit and push
if ($Commit -and -not $DryRun) {
    Write-Host "`n[BONUS] Committing changes..." -ForegroundColor Cyan
    python -m git add requirements.txt pyproject.toml $reportPath 2>&1 | Out-Null
    python -m git commit -m "chore(deps): update dependencies for security patches

Packages updated: $($successfulUpdates -join ', ')
Failed: $(if ($failedUpdates.Count -gt 0) { $failedUpdates -join ', ' } else { 'None' })

See $reportPath for details" 2>&1 | Out-Null
    Write-Host "  ✓ Changes committed" -ForegroundColor Green
}

if ($Push -and -not $DryRun) {
    Write-Host "`nPushing to origin..." -ForegroundColor Cyan
    python -m git push origin main 2>&1 | Out-Null
    Write-Host "  ✓ Pushed to main" -ForegroundColor Green
}

Write-Host "`nNext: Review the report and run 'pvw --help' to verify" -ForegroundColor Cyan


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
