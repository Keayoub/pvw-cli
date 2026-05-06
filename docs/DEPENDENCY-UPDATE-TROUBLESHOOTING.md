# Dependency Update Troubleshooting Guide

## Problem 1: "All packages broke tests"

### Symptoms
```
✗ cryptography broke tests! Reverting...
✗ PyYAML broke tests! Reverting...
✗ aiohttp broke tests! Reverting...
```

### Root Causes

1. **Tests not properly configured** - pytest or test dependencies not installed
2. **Incompatible test setup** - Tests use old API patterns
3. **Azure SDK compatibility** - Tests depend on specific Azure SDK versions

### Solutions

#### Option A: Run without tests (Recommended for now)
```powershell
.\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -SkipTests
```

#### Option B: Install test dependencies first
```bash
pip install pytest pytest-asyncio pytest-cov

# Then try again
.\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly
```

#### Option C: Diagnose test issues
```powershell
.\scripts\diagnose-dependencies.ps1

# Try running tests manually
python -m pytest tests/ -v --tb=short
```

---

## Problem 2: "Security tools not found"

### Symptoms
```
The term 'bandit' is not recognized as a cmdlet...
```

### Cause
Bandit, Safety, and pip-audit are not installed in the virtual environment.

### Solution

The updated script now auto-installs these tools. Just run with audit enabled:

```powershell
.\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly
```

Or install manually:
```bash
pip install bandit safety pip-audit
```

---

## Problem 3: "No tests found"

### Symptoms
```
Could not collect tests
Total tests: 0
```

### Cause
Tests directory exists but tests aren't discoverable by pytest.

### Solution

1. Check test file naming:
```bash
ls tests/test_*.py
```

2. Run with verbose discovery:
```bash
python -m pytest tests/ --collect-only -v
```

3. Skip tests and proceed:
```powershell
.\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -SkipTests
```

---

## Recommended Safe Update Path

### Step 1: Diagnose
```powershell
.\scripts\diagnose-dependencies.ps1
```

### Step 2: Dry Run (No actual changes)
```powershell
.\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -DryRun
```

### Step 3: Update Low-Risk Packages
```powershell
.\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -SkipTests
```

### Step 4: Review Report
```bash
cat VULNERABILITY-FIX-REPORT-*.md
```

### Step 5: Verify CLI Works
```bash
pvw --version
pvw --help
```

### Step 6: Test Against Azure (if credentials available)
```bash
pvw account readaccounts
```

### Step 7: Commit Changes
```powershell
.\scripts\fix-vulnerabilities.ps1 -UpdateType SafeOnly -SkipTests -Commit -Push
```

---

## Manual Updates (If Script Fails)

### Update One Package Safely

```powershell
# 1. Backup
Copy-Item requirements.txt requirements.txt.bak

# 2. Update
pip install --upgrade cryptography

# 3. Verify
pvw --version

# 4. Check imports work
python -c "from cryptography import x509; print('OK')"

# 5. Regenerate requirements
pip-compile requirements.in --upgrade --output-file requirements.txt

# 6. Commit
git add requirements.txt
git commit -m "chore(deps): update cryptography"
git push origin main
```

### Rollback If Needed

```powershell
# Restore backup
Copy-Item requirements.txt.bak requirements.txt

# Reinstall
pip install -r requirements.txt

# Commit rollback
git add requirements.txt
git commit -m "revert: dependency update caused issues"
git push origin main
```

---

## Package-Specific Fixes

### cryptography

**Issue**: Often requires C++ build tools

**Fix**:
```powershell
# On Windows, ensure build tools are available
pip install --upgrade cryptography --no-binary cryptography
```

### PyYAML

**Issue**: May have breaking changes in YAML parsing

**Fix**:
```powershell
# Audit YAML usage in code
grep -r "yaml.load" purviewcli/ --include="*.py"

# Ensure using yaml.safe_load()
# Update: yaml.load(f) → yaml.safe_load(f)
```

### Azure Packages

**Issue**: Inter-dependencies between azure-core, azure-identity, etc.

**Fix**:
```powershell
# Update all together
pip install --upgrade `
  azure-identity `
  azure-core `
  azure-mgmt-purview `
  azure-purview-catalog `
  azure-purview-datamap `
  azure-purview-scanning
```

### pydantic

**Issue**: Major version 2 breaks Pydantic 1.x code

**Fix**:
```powershell
# Check current version
python -c "import pydantic; print(pydantic.VERSION)"

# If upgrading from 1.x to 2.x, expect migration needed:
# https://docs.pydantic.dev/latest/concepts/migration/
```

---

## Testing After Update

After any dependency update, run these checks:

```powershell
# 1. CLI Help
pvw --help

# 2. CLI Version
pvw --version

# 3. Entity Commands
pvw entity --help

# 4. Authentication (requires Azure setup)
pvw account readaccounts

# 5. Python Imports
python -c "
import purviewcli
from purviewcli.client import PurviewClient
print('Imports: OK')
"

# 6. Code Quality
flake8 purviewcli/
mypy purviewcli/ --ignore-missing-imports

# 7. Security Audit
bandit -r purviewcli/
safety check
```

---

## When to Update, When to Wait

### Update Immediately 🔴
- Critical security vulnerability (CVE with active exploits)
- Version has known remote code execution
- Package is unsupported/deprecated

### Update Soon 🟡
- High-severity vulnerability with limited exposure
- Moderate vulnerability affecting your use case
- Security patches available

### Update Eventually 🟢
- Low-severity issues
- Minor version updates
- When you have time to test thoroughly

### Hold Off ⚪
- Major version upgrades (need code migration)
- Packages with known issues (wait for patch)
- During critical production periods

---

## Reference Links

- [Dependabot Docs](https://docs.github.com/code-security/dependabot)
- [Fix Vulnerabilities Script](./scripts/fix-vulnerabilities.ps1)
- [Diagnose Dependencies Script](./scripts/diagnose-dependencies.ps1)
- [Dependency Analysis](./docs/DEPENDENCY-VULNERABILITIES.md)

---

**Last Updated**: May 6, 2026
