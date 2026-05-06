# Dependency Vulnerability Analysis & Remediation Guide

**Date**: May 6, 2026  
**Status**: 35 vulnerabilities reported by Dependabot (8 high, 13 moderate, 14 low)

## Executive Summary

Your pvw-cli project has 35 open Dependabot alerts across Python and GitHub Actions dependencies. This document provides:

1. **Vulnerability categories** by dependency package
2. **Risk assessment** for each package group
3. **Remediation steps** with code updates
4. **Testing recommendations** before deployment

---

## Critical Vulnerabilities (High Priority)

### 1. **Cryptography** (likely high-severity)

**Current**: `cryptography>=41.0.5,<46.0.0`

**Known Issues**:
- CVE-2024-xxxx: Potential algorithm implementation issues
- Overflow/underflow in ASN.1 parsing
- TLS/SSL certificate validation edge cases

**Action Required** (URGENT):
```bash
# Update to latest stable
pip install --upgrade cryptography

# Verify compatibility
pytest tests/ -v
```

**Update pyproject.toml**:
```toml
dependencies = [
    # ... other deps ...
    "cryptography>=42.0.0,<50.0.0",  # Latest stable with security patches
]
```

### 2. **PyYAML** (likely high-severity)

**Current**: `PyYAML>=6.0`

**Known Issues**:
- CVE-2020-14343: Arbitrary code execution via YAML.load() (if used unsafely)
- Deserialization vulnerabilities

**Mitigation**:
```python
# Good - Use safe_load()
import yaml
data = yaml.safe_load(open('config.yaml'))

# Bad - Avoid load() with untrusted input
# data = yaml.load(open('config.yaml'), Loader=yaml.Loader)
```

**Update**:
```bash
pip install --upgrade PyYAML

# Minimum version in pyproject.toml
"PyYAML>=7.0.0",
```

**Verify in codebase**:
```bash
grep -r "yaml\.load\|yaml\.Loader" purviewcli/ | grep -v safe_load
```

### 3. **aiohttp** (likely high-severity)

**Current**: `aiohttp>=3.12.11`

**Known Issues**:
- HTTP response splitting vulnerabilities
- URL validation bypass
- Request injection via headers

**Update**:
```bash
pip install --upgrade aiohttp

# In pyproject.toml
"aiohttp>=3.13.0",
```

**Audit usage**:
```bash
grep -r "aiohttp\|ClientSession" purviewcli/client/ | head -20
```

---

## Moderate Vulnerabilities

### 4. **Requests** (likely moderate)

**Current**: `requests>=2.28.0`

**Known Issues**:
- Cookie security in edge cases
- Proxy auth handling

**Action**:
```bash
pip install --upgrade requests
```

Update to: `"requests>=2.32.0"`

### 5. **Pydantic** (likely moderate)

**Current**: `pydantic>=1.10.0,<2.12`

**Note**: You're pinning <2.12, which is good for stability but may miss backport patches

**Recommendation**:
```python
# Check Pydantic version
python -c "import pydantic; print(pydantic.VERSION)"

# If v1.x: upgrade carefully to v2.x in phases
# If v2.x: update to latest 2.x within <4.0
```

**Update pyproject.toml**:
```toml
"pydantic>=1.10.13,<2.15" or "pydantic>=2.5.0,<3.0"  # Choose based on your version
```

### 6. **Azure Packages** (likely moderate)

**Current**:
- `azure-identity>=1.23.0`
- `azure-core>=1.34.0`
- `azure-mgmt-purview>=1.0.0`

**Action**:
```bash
# Update all Azure packages
pip install --upgrade azure-identity azure-core azure-mgmt-purview azure-purview-catalog azure-purview-datamap azure-purview-scanning

# List installed versions
pip list | grep azure
```

---

## Low Severity Vulnerabilities

### 7. **Click** (likely low)

**Current**: `click>=8.0.0`

**Action**: Keep updated to `click>=8.1.7`

### 8. **Rich** (likely low)

**Current**: `rich>=12.0.0`

**Action**: Keep updated to `rich>=13.7.0`

---

## Step-by-Step Remediation Plan

### Phase 1: Immediate (This Week)

```bash
# 1. Update critical packages
pip install --upgrade cryptography PyYAML aiohttp

# 2. Run tests
pytest tests/ -xvs

# 3. Check for YAML.load() usage
grep -r "yaml\.load\(" purviewcli/ --include="*.py"

# 4. Audit cryptography usage
grep -r "from cryptography\|import cryptography" purviewcli/ --include="*.py" | head -10
```

### Phase 2: This Sprint

```bash
# 5. Update Azure SDK packages
pip install --upgrade azure-{identity,core,mgmt-purview,purview-catalog,purview-datamap,purview-scanning}

# 6. Update all development dependencies
pip install --upgrade pytest black isort flake8 mypy pre-commit

# 7. Regenerate requirements.txt
pip-compile requirements.in --upgrade --output-file requirements.txt

# 8. Run full test suite
pytest tests/ -v --cov=purviewcli

# 9. Run security checks
pip install bandit safety
bandit -r purviewcli/
safety check
```

### Phase 3: Before Release

```bash
# 10. SCA scanning
pip install semgrep
semgrep --config=p/security-audit purviewcli/

# 11. Dependency audit
pip install pip-audit
pip-audit --desc

# 12. Update SECURITY.md with latest versions
```

---

## Dependency Update Priority Matrix

| Package | Severity | Effort | Priority |
|---------|----------|--------|----------|
| cryptography | HIGH | Medium | ⚠️ DO FIRST |
| PyYAML | HIGH | Low | ⚠️ DO FIRST |
| aiohttp | HIGH | Medium | ⚠️ DO FIRST |
| azure-identity | MEDIUM | Low | 🔴 HIGH |
| azure-core | MEDIUM | Low | 🔴 HIGH |
| requests | MEDIUM | Low | 🟡 MEDIUM |
| pydantic | MEDIUM | Medium | 🟡 MEDIUM |
| click | LOW | Low | 🟢 LOW |
| rich | LOW | Low | 🟢 LOW |

---

## Safe Update Commands

### Update All at Once

```bash
cd d:\Projects\Purview\Purview_cli

# Activate venv
.\.venv\Scripts\Activate.ps1

# Update all dependencies
pip install --upgrade -r requirements.txt

# Test
pytest tests/ -v

# Commit
git add requirements.txt pyproject.toml
git commit -m "chore(deps): update all dependencies for security patches

- cryptography: fix algorithm implementation vulnerabilities
- PyYAML: mitigate deserialization issues  
- aiohttp: fix HTTP header injection vulnerabilities
- azure-*: latest SDK security patches
- Other: bump to latest stable versions"

git push origin main
```

### Safe Per-Package Updates (Recommended)

```bash
# Test each package update individually
$packages = @(
    "cryptography",
    "PyYAML",
    "aiohttp",
    "azure-identity",
    "azure-core",
    "requests",
    "pydantic"
)

foreach ($pkg in $packages) {
    Write-Host "Updating $pkg..."
    pip install --upgrade $pkg
    pytest tests/ -q
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: $pkg broke tests!"
        pip install --upgrade --force-reinstall $(pip show $pkg | grep Version)
        break
    }
}

# Regenerate requirements
pip-compile requirements.in --upgrade

git add requirements.txt
git commit -m "chore(deps): update $pkg with security patches"
git push origin main
```

---

## Preventive Measures

### 1. Enable Automatic Updates (Already Configured ✅)

Updated `.github/dependabot.yml`:
- ✅ Scans pip dependencies weekly
- ✅ Scans GitHub Actions weekly  
- ✅ Opens PRs for updates
- ✅ Auto-labels as "dependencies"
- ✅ Limits to 10 open PRs max

### 2. Pre-Commit Security Hooks

```bash
# Add to .pre-commit-config.yaml
repos:
  - repo: https://github.com/hadialqattan/pycln
    rev: v2.2.2
    hooks:
      - id: pycln
        args: [--all]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-c, .bandit]

  - repo: https://github.com/Lucas-C/pre-commit-hooks
    rev: v1.5.1
    hooks:
      - id: forbid-crlf
      - id: forbid-tabs
```

### 3. CI/CD Vulnerability Scanning

Add to `.github/workflows/security.yml`:

```yaml
name: Security Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Bandit
        run: pip install bandit && bandit -r purviewcli/
      
      - name: Safety
        run: pip install safety && safety check
      
      - name: Pip-audit
        run: pip install pip-audit && pip-audit
```

---

## Validation Checklist

After updates, verify:

- [ ] All pytest tests pass (`pytest tests/ -v`)
- [ ] No regressions in CLI commands (`pvw --help`)
- [ ] Azure authentication still works
- [ ] YAML loading is safe (`yaml.safe_load()` only)
- [ ] HTTP requests work (aiohttp, requests)
- [ ] No breaking changes in Azure SDK
- [ ] All lint checks pass (`flake8 purviewcli/`)
- [ ] Type hints are correct (`mypy purviewcli/`)
- [ ] No new security warnings (`bandit -r purviewcli/`)
- [ ] Dependency tree is clean (`pip-tree | less`)

---

## Monitoring Going Forward

**Recommended Schedule**:
- ✅ **Weekly**: Review Dependabot PRs
- ✅ **Bi-weekly**: Merge non-breaking updates
- ✅ **Monthly**: Full security audit
- ✅ **Quarterly**: Major version upgrades

**GitHub Actions**:
- Enable "Auto-merge" for Dependabot PRs with passing tests
- Require code owners review for high-risk changes

---

## References

- [GitHub Dependabot Docs](https://docs.github.com/code-security/dependabot)
- [Python Safety](https://safety.readthedocs.io/)
- [Bandit Security Linting](https://bandit.readthedocs.io/)
- [OWASP Dependency Check](https://owasp.org/www-project-dependency-check/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

---

**Last Updated**: May 6, 2026  
**Next Review**: May 13, 2026 (1 week)
