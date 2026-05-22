<#
.SYNOPSIS
    Build and optionally publish purview-mcp-server to PyPI.

.DESCRIPTION
    Builds the purview-mcp-server package (sdist + wheel) from tools/mcp/
    and optionally uploads to PyPI (or TestPyPI for dry-run validation).

.PARAMETER Publish
    Upload to PyPI after a successful build. Requires PyPI credentials (API token).

.PARAMETER TestPyPI
    Upload to TestPyPI instead of the real PyPI index. Useful for validation.
    Implies -Publish.

.PARAMETER SkipInstallTest
    Skip the post-build local install test.

.EXAMPLE
    # Build only (no upload)
    .\build_pypi.ps1

.EXAMPLE
    # Build + upload to TestPyPI for validation
    .\build_pypi.ps1 -TestPyPI

.EXAMPLE
    # Build + upload to production PyPI
    .\build_pypi.ps1 -Publish

.NOTES
    Prerequisites:
      uv pip install build twine
    PyPI authentication:
      Set TWINE_USERNAME to __token__ and TWINE_PASSWORD to your API token,
      or configure ~/.pypirc with the appropriate index.
#>

[CmdletBinding()]
param(
    [switch]$Publish,
    [switch]$TestPyPI,
    [switch]$SkipInstallTest
)

$ErrorActionPreference = "Stop"

function Write-Info($m)    { Write-Host "[INFO]    $m" -ForegroundColor Cyan }
function Write-Success($m) { Write-Host "[OK]      $m" -ForegroundColor Green }
function Write-Step($m)    { Write-Host "`n--- $m ---" -ForegroundColor Yellow }
function Fail($m, $code=1) { Write-Host "[ERROR]   $m" -ForegroundColor Red; exit $code }

# ---------------------------------------------------------------------------
# Locate the package root (this script lives inside it)
# ---------------------------------------------------------------------------
$PackageRoot = $PSScriptRoot
Push-Location $PackageRoot

try {
    Write-Host "`n========================================"
    Write-Host " Building purview-mcp-server"
    Write-Host "========================================`n"

    # ------------------------------------------------------------------
    # 1. Read current version
    # ------------------------------------------------------------------
    Write-Step "Version"
    $verScript = "import sys; sys.path.insert(0,'.'); from __version__ import __version__; print(__version__)"
    $version = & uv run python -c $verScript 2>&1
    if ($LASTEXITCODE -ne 0) { Fail "Could not read version: $version" 2 }
    Write-Success "Package version: $version"

    # ------------------------------------------------------------------
    # 2. Install / upgrade build tools
    # ------------------------------------------------------------------
    Write-Step "Build tools"
    & uv pip install --upgrade build twine setuptools wheel
    if ($LASTEXITCODE -ne 0) { Fail "Failed to install build tools" 3 }
    Write-Success "build, twine, setuptools, wheel are up to date"

    # ------------------------------------------------------------------
    # 3. Clean previous build artefacts
    # ------------------------------------------------------------------
    Write-Step "Cleaning"
    @("build", "dist", "pvw_mcp_server.egg-info", "pvw-mcp-server.egg-info", "purview-mcp-server.egg-info") | ForEach-Object {
        if (Test-Path $_) { Remove-Item -Recurse -Force $_; Write-Info "Removed $_" }
    }
    Write-Success "Working tree clean"

    # ------------------------------------------------------------------
    # 4. Build sdist + wheel
    # ------------------------------------------------------------------
    Write-Step "Building"
    & uv build
    if ($LASTEXITCODE -ne 0) { Fail "Build failed" 4 }
    Write-Success "Build complete"

    Write-Info "Artefacts in dist/:"
    Get-ChildItem -Path dist -File | ForEach-Object {
        $kb = [math]::Round($_.Length / 1024, 1)
        Write-Host ("   {0}  ({1} KB)" -f $_.Name, $kb)
    }

    # ------------------------------------------------------------------
    # 5. Validate with twine check
    # ------------------------------------------------------------------
    Write-Step "Validation"
    & python -m twine check dist/*
    if ($LASTEXITCODE -ne 0) { Fail "twine check failed — fix the package metadata before uploading" 5 }
    Write-Success "twine check passed"

    # ------------------------------------------------------------------
    # 6. Optional: local install test
    # ------------------------------------------------------------------
    if (-not $SkipInstallTest) {
        Write-Step "Local install test"
        $wheel = Get-ChildItem -Path dist -Filter "*.whl" -File | Select-Object -First 1
        if (-not $wheel) { Fail "No wheel found in dist/" 6 }

        & uv pip install --reinstall "dist\$($wheel.Name)"
        if ($LASTEXITCODE -ne 0) { Fail "Local install failed" 7 }

        $importTest = & uv run python -c "from server import mcp; print('mcp object:', type(mcp).__name__)" 2>&1
        if ($LASTEXITCODE -ne 0) { Fail "Import test failed: $importTest" 8 }
        Write-Success "Import test: $importTest"
    }

    # ------------------------------------------------------------------
    # 7. Optional: upload
    # ------------------------------------------------------------------
    if ($TestPyPI -or $Publish) {
        Write-Step "Upload"

        if ($TestPyPI) {
            Write-Info "Target: TestPyPI  (https://test.pypi.org)"
            & uv run python -m twine upload --repository testpypi dist/*
        } else {
            Write-Info "Target: PyPI  (https://pypi.org)"
            & uv run python -m twine upload dist/*
        }

        if ($LASTEXITCODE -ne 0) { Fail "Upload failed" 9 }
        Write-Success "Upload complete"

        $index = if ($TestPyPI) { "https://test.pypi.org/project/purview-mcp-server/$version/" } else { "https://pypi.org/project/purview-mcp-server/$version/" }
        Write-Host "`nPackage URL: $index" -ForegroundColor Cyan
    } else {
        Write-Host "`n[SKIP] Upload skipped. Re-run with -Publish or -TestPyPI to upload." -ForegroundColor DarkGray
        Write-Host "       Manual upload:  uv run python -m twine upload dist/*" -ForegroundColor DarkGray
    }

    Write-Host "`n[DONE] purview-mcp-server $version built successfully.`n" -ForegroundColor Green

} finally {
    Pop-Location
}
