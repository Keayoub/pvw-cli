@echo off
REM Deploy improved dependency scripts and documentation

cd /d "%~dp0"

echo.
echo === Committing Dependency Script Improvements ===
echo.

git add scripts\fix-vulnerabilities.ps1 scripts\diagnose-dependencies.ps1 docs\DEPENDENCY-UPDATE-TROUBLESHOOTING.md SCRIPT-IMPROVEMENTS.md

git commit -m "chore(security): improve dependency update tools with diagnostics and better error handling

- Enhanced fix-vulnerabilities.ps1:
  * Auto-installs security tools (bandit, safety, pip-audit)
  * -SkipTests flag for environments without test setup
  * -DryRun flag to preview changes without executing
  * Better error handling and per-package rollback
  * Generates before/after version reports
  
- Added diagnose-dependencies.ps1:
  * Scans Python environment and installed packages
  * Tests pytest availability
  * Recommends appropriate next steps
  
- Created DEPENDENCY-UPDATE-TROUBLESHOOTING.md:
  * Fixes for 'all packages broke tests' issue
  * Solutions for missing security tools
  * Manual update procedures
  * Package-specific troubleshooting
  * Testing checklist and when-to-update guidance

Safe usage: .\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -SkipTests"

git push origin main

echo.
echo === Deployment Complete ===
echo.
echo Next steps:
echo 1. Run: .\scripts\diagnose-dependencies.ps1
echo 2. Run: .\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -DryRun
echo 3. Review: VULNERABILITY-FIX-REPORT-*.md
echo.
