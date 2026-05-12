<#
.SYNOPSIS
  Creates a GitHub release from an existing tag and a release note file.

.DESCRIPTION
  This script creates a GitHub Release in the current repository using:
  - an existing tag (for example: v1.11.9), and
  - a markdown note file from the releases folder.

  Preferred path for notes is releases/v<version>.md.

  It first tries GitHub CLI (gh). If gh is unavailable, it falls back
  to GitHub REST API and requires GITHUB_TOKEN.

.USAGE
  .\scripts\create_github_release.ps1 -Version 1.11.9
  .\scripts\create_github_release.ps1 -Tag v1.11.9 -NotesFile releases\v1.11.9.md
  .\scripts\create_github_release.ps1 -Version 1.11.9 -Draft
#>

param(
    [string]$Version,
    [string]$Tag,
    [string]$NotesFile,
    [switch]$Draft,
    [switch]$PreRelease,
    [switch]$Force
)

function Write-Info([string]$m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Write-Warn([string]$m) { Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Write-Err([string]$m) { Write-Host "[ERROR] $m" -ForegroundColor Red }

if (-not $Tag -and -not $Version) {
    Write-Err "Provide either -Version (for example 1.11.9) or -Tag (for example v1.11.9)."
    exit 2
}

if ($Version -and -not ($Version -match '^[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9\.]+)?$')) {
    Write-Err "Version '$Version' is invalid. Expected MAJOR.MINOR.PATCH."
    exit 2
}

if (-not $Tag) {
    $Tag = "v$Version"
}

if (-not $Version) {
    if ($Tag -match '^v(.+)$') {
        $Version = $Matches[1]
    } else {
        $Version = $Tag
    }
}

try { git --version | Out-Null } catch { Write-Err "git is not available on PATH."; exit 3 }

$repoRoot = (git rev-parse --show-toplevel) 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Err "Not inside a git repository."
    exit 4
}
$repoRoot = $repoRoot.Trim()
Set-Location $repoRoot

# Ensure tag exists locally
git rev-parse --verify "refs/tags/$Tag" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Err "Tag '$Tag' does not exist locally. Create/pull the tag first."
    exit 5
}

# Ensure tag exists on origin
git ls-remote --tags origin "refs/tags/$Tag" | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Err "Could not query origin tags. Check network and remote access."
    exit 6
}
$remoteTag = git ls-remote --tags origin "refs/tags/$Tag"
if (-not $remoteTag) {
    Write-Err "Tag '$Tag' was not found on origin. Push it with: git push origin $Tag"
    exit 7
}

if (-not $NotesFile) {
    $candidate1 = Join-Path $repoRoot ("releases\v{0}.md" -f $Version)
    $candidate2 = Join-Path $repoRoot ("releases\{0}.md" -f $Version)
    if (Test-Path $candidate1 -PathType Leaf) {
        $NotesFile = $candidate1
    } elseif (Test-Path $candidate2 -PathType Leaf) {
        $NotesFile = $candidate2
    }
}

if (-not $NotesFile) {
    Write-Err "Release notes file not found. Expected releases/v$Version.md or pass -NotesFile."
    exit 8
}

if (-not (Test-Path $NotesFile -PathType Leaf)) {
    Write-Err "Release notes file does not exist: $NotesFile"
    exit 8
}

$releaseTitle = "v$Version"
if ($Tag -notmatch '^v') {
    $releaseTitle = $Tag
}

Write-Info "Repository root: $repoRoot"
Write-Info "Tag: $Tag"
Write-Info "Release title: $releaseTitle"
Write-Info "Release notes file: $NotesFile"

$gh = Get-Command gh -ErrorAction SilentlyContinue
if ($gh) {
    Write-Info "Using GitHub CLI to create release..."

    $args = @('release', 'view', $Tag)
    & $gh.Source @args *> $null
    if ($LASTEXITCODE -eq 0 -and -not $Force) {
        Write-Err "A release already exists for tag '$Tag'. Use -Force to replace it."
        exit 9
    }

    if ($LASTEXITCODE -eq 0 -and $Force) {
        Write-Warn "Release already exists for '$Tag'. Deleting due to -Force..."
        & $gh.Source release delete $Tag --yes
        if ($LASTEXITCODE -ne 0) {
            Write-Err "Failed to delete existing release for '$Tag'."
            exit 10
        }
    }

    $createArgs = @('release', 'create', $Tag, '--title', $releaseTitle, '--notes-file', $NotesFile)
    if ($Draft) { $createArgs += '--draft' }
    if ($PreRelease) { $createArgs += '--prerelease' }

    & $gh.Source @createArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Err "gh release create failed."
        exit 11
    }

    Write-Info "GitHub release created successfully for '$Tag'."
    exit 0
}

Write-Warn "GitHub CLI (gh) is not available. Falling back to REST API."

$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Err "GITHUB_TOKEN is required for REST fallback."
    exit 12
}

$remoteUrl = (git remote get-url origin).Trim()
if (-not $remoteUrl) {
    Write-Err "Could not resolve origin remote URL."
    exit 13
}

$owner = $null
$repo = $null

if ($remoteUrl -match 'github\.com[:/](.+?)/(.+?)(\.git)?$') {
    $owner = $Matches[1]
    $repo = $Matches[2]
}

if (-not $owner -or -not $repo) {
    Write-Err "Could not parse owner/repo from origin URL: $remoteUrl"
    exit 14
}

$notes = Get-Content -Raw -Path $NotesFile -Encoding UTF8
$headers = @{
    Authorization = "Bearer $token"
    Accept = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$releaseApi = "https://api.github.com/repos/$owner/$repo/releases"

if ($Force) {
    try {
        $existing = Invoke-RestMethod -Method Get -Uri "$releaseApi/tags/$Tag" -Headers $headers -ErrorAction Stop
        if ($existing -and $existing.id) {
            Write-Warn "Release already exists for '$Tag'. Deleting due to -Force..."
            Invoke-RestMethod -Method Delete -Uri "$releaseApi/$($existing.id)" -Headers $headers -ErrorAction Stop | Out-Null
        }
    } catch {
        # Ignore if not found
    }
}

if (-not $Force) {
    try {
        $existing = Invoke-RestMethod -Method Get -Uri "$releaseApi/tags/$Tag" -Headers $headers -ErrorAction Stop
        if ($existing) {
            Write-Err "A release already exists for tag '$Tag'. Use -Force to replace it."
            exit 15
        }
    } catch {
        # Not found is expected
    }
}

$body = @{
    tag_name = $Tag
    name = $releaseTitle
    body = $notes
    draft = [bool]$Draft
    prerelease = [bool]$PreRelease
    generate_release_notes = $false
} | ConvertTo-Json -Depth 4

try {
    $resp = Invoke-RestMethod -Method Post -Uri $releaseApi -Headers $headers -Body $body -ContentType "application/json" -ErrorAction Stop
    Write-Info "GitHub release created successfully for '$Tag'."
    if ($resp.html_url) {
        Write-Info "Release URL: $($resp.html_url)"
    }
    exit 0
} catch {
    Write-Err "REST release creation failed: $($_.Exception.Message)"
    exit 16
}
