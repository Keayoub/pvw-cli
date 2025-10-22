<#
.SYNOPSIS
  Release helper: bump version, commit, tag, push, and optionally build.

.DESCRIPTION
  This script updates the package version in `pyproject.toml` and `purviewcli/__init__.py`,
  updates README occurrences of the old version, commits the changes, creates an annotated
  tag `v<version>`, and can optionally push and run the project's build script.

.USAGE
  # Bump to 1.0.13, commit and tag locally
  .\release.ps1 -NewVersion 1.0.13

  # Bump, commit, tag and push to origin
  .\release.ps1 -NewVersion 1.0.13 -Push

  # Bump, commit, tag, push and run build_pypi.bat
  .\release.ps1 -NewVersion 1.0.13 -Push -Build

.NOTES
  - Recommended to run in PowerShell Core (pwsh). A small batch wrapper is included
    for convenience when using cmd.exe.
  - The script refuses to run if there are uncommitted changes unless -Force is provided.
#>

param(
    [Parameter(Mandatory=$true, Position=0)][string]$NewVersion,
    [switch]$Push,
    [switch]$Build,
    [switch]$Force
)

function Write-Info([string]$m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Warn([string]$m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err([string]$m) { Write-Host "[ERROR] $m" -ForegroundColor Red }

# Basic semver-ish validation
if (-not ($NewVersion -match '^[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9\.]+)?$')) {
    Write-Err "Version '$NewVersion' doesn't look like a semantic version (MAJOR.MINOR.PATCH)."
    exit 2
}

# Ensure git is available
try { git --version | Out-Null } catch { Write-Err "git is not available on PATH"; exit 3 }

$repoRoot = (git rev-parse --show-toplevel) 2>&1
if ($LASTEXITCODE -ne 0) { Write-Err "Not inside a git repository."; exit 4 }
$repoRoot = $repoRoot.Trim()
Set-Location $repoRoot

# Ensure working tree is clean unless forced
$status = git status --porcelain
if ($status -and -not $Force) {
    Write-Err "Working tree is not clean. Commit or stash changes first, or run with -Force to override."
    git status --short
    exit 5
}

# Paths
$pyproject = Join-Path $repoRoot 'pyproject.toml'
$initFile = Join-Path $repoRoot 'purviewcli\__init__.py'
$readme = Join-Path $repoRoot 'README.md'

if (-not (Test-Path $pyproject -PathType Leaf)) { Write-Err "pyproject.toml not found at $pyproject"; exit 6 }
if (-not (Test-Path $initFile -PathType Leaf)) { Write-Err "__init__.py not found at $initFile"; exit 6 }

Write-Info "Reading current version from pyproject.toml..."
$pytext = Get-Content -Raw -Path $pyproject
# Try a resilient match: look for a line like: version = "1.2.3"
$matchInfo = Select-String -Path $pyproject -Pattern '^[ \t]*version[ \t]*=[ \t]*"([^\"]+)"' -AllMatches
if (-not $matchInfo -or $matchInfo.Count -eq 0) {
  Write-Err "Could not find current version in pyproject.toml"
  Write-Info "Showing the first 20 lines of pyproject.toml for debugging:"
  Get-Content -Path $pyproject -TotalCount 20 | ForEach-Object { Write-Host "  $_" }
  exit 7
}
# Select-String returns MatchInfo objects; take the first match group's capture
$firstMatch = $matchInfo[0].Matches[0]
$oldVersion = $firstMatch.Groups[1].Value
Write-Info "Current version: $oldVersion -> New version: $NewVersion"

if ($oldVersion -eq $NewVersion) { Write-Warn "New version is identical to current version. Nothing to do."; exit 0 }

function Backup-File($path) {
  $bak = "$path.bak"
  if (Test-Path $bak) {
    $ts = Get-Date -Format yyyyMMddHHmmss
    $bak = "$path.bak.$ts"
  }
  Copy-Item -Force -Path $path -Destination $bak
  Write-Info "Backup created: $bak"
}

Backup-File $pyproject
Backup-File $initFile
if (Test-Path $readme) { Backup-File $readme }

Write-Info "Updating pyproject.toml..."
# Use concatenation for replacement to avoid PowerShell/regex replacement string escape issues
$patternPy = '(version\s*=\s*")([^"]+)(")'
$replacementPy = '$1' + $NewVersion + '$3'
$newPy = [regex]::Replace($pytext, $patternPy, $replacementPy, [System.Text.RegularExpressions.RegexOptions]::Multiline)
Set-Content -Path $pyproject -Value $newPy -Encoding utf8

Write-Info "Updating purviewcli/__init__.py..."
# Read file as lines and replace the __version__ line or insert at top if missing
$lines = (Get-Content -Path $initFile -Encoding UTF8)
$found = $false
for ($i = 0; $i -lt $lines.Count; $i++) {
  if ($lines[$i] -match '^[ \t]*__version__\s*=') {
    $lines[$i] = "__version__ = `"$NewVersion`""
    $found = $true
    break
  }
}
if (-not $found) {
  # insert at top
  $lines = ,("__version__ = `"$NewVersion`"" ) + $lines
}
# Write back with UTF8 encoding
Set-Content -Path $initFile -Value $lines -Encoding utf8

if (Test-Path $readme) {
    Write-Info "Updating README.md occurrences of version..."
    $readmeText = Get-Content -Raw -Path $readme
    # Replace v<oldVersion> and PVW CLI v<oldVersion>
    $r = $readmeText -replace [regex]::Escape("v$oldVersion"), "v$NewVersion"
    $r = $r -replace [regex]::Escape("PVW CLI v$oldVersion"), "PVW CLI v$NewVersion"
    Set-Content -NoNewline -Path $readme -Value $r
}

# Verify package builds before committing
Write-Info "Verifying package can be built before committing..."
$buildScriptPS = Join-Path (Join-Path $repoRoot 'scripts') 'build_pypi.ps1'
if (Test-Path $buildScriptPS) {
  Write-Info "Running build verification script: $buildScriptPS (no upload)"
  # Prefer pwsh if available, otherwise invoke using the current PowerShell
  $pwshCmd = Get-Command pwsh -ErrorAction SilentlyContinue
  if ($pwshCmd) {
    & $pwshCmd.Source -NoProfile -ExecutionPolicy Bypass -File $buildScriptPS
  } else {
    # already in PowerShell; run script directly
    & $buildScriptPS
  }
  if ($LASTEXITCODE -ne 0) {
    Write-Err "Build verification failed. Aborting release. See build output above for details."
    exit 14
  }
  Write-Info "Build verification succeeded. Proceeding to commit and tagging."
} else {
  Write-Warn "Build verification script not found at $buildScriptPS - skipping build verification."
}

Write-Info "Staging changes..."
git add $pyproject $initFile $readme
if ($LASTEXITCODE -ne 0) { Write-Err "git add failed"; exit 8 }

$commitMsg = "Bump version to $NewVersion"
Write-Info "Committing: $commitMsg"
git commit -m $commitMsg --no-verify
if ($LASTEXITCODE -ne 0) { Write-Err "git commit failed"; git status --short; exit 9 }

Write-Info "Creating annotated tag v$NewVersion"
git tag -a "v$NewVersion" -m "Release v$NewVersion"
if ($LASTEXITCODE -ne 0) { Write-Err "git tag failed"; exit 10 }

if ($Push) {
    Write-Info "Pushing commit to origin..."
    git push origin HEAD
    if ($LASTEXITCODE -ne 0) { Write-Err "git push failed"; exit 11 }

    Write-Info "Pushing tag v$NewVersion to origin..."
    git push origin "v$NewVersion"
    if ($LASTEXITCODE -ne 0) { Write-Err "git push tag failed"; exit 12 }
}

if ($Build) {
  # Prefer PowerShell build script (build_pypi.ps1); fall back to batch if missing
  $buildScriptPS = Join-Path (Join-Path $repoRoot 'scripts') 'build_pypi.ps1'
  if (Test-Path $buildScriptPS) {
    Write-Info "Running PowerShell build script: $buildScriptPS"
    $pwshCmd = Get-Command pwsh -ErrorAction SilentlyContinue
    if ($pwshCmd) {
      & $pwshCmd.Source -NoProfile -ExecutionPolicy Bypass -File $buildScriptPS
    } else {
      & $buildScriptPS
    }
    if ($LASTEXITCODE -ne 0) { Write-Err "PowerShell build script failed with exit code $LASTEXITCODE"; exit 13 }
  } else {
    $buildScript = Join-Path $repoRoot 'build_pypi.bat'
    if (Test-Path $buildScript) {
      Write-Info "PowerShell build script not found; falling back to batch: $buildScript"
      & cmd /c $buildScript
      if ($LASTEXITCODE -ne 0) { Write-Err "Batch build script failed with exit code $LASTEXITCODE"; exit 13 }
    } else {
      Write-Warn "No build script found: checked scripts\build_pypi.ps1 and build_pypi.bat"
    }
  }
}

Write-Info "Release steps completed successfully. New tag: v$NewVersion"
exit 0
