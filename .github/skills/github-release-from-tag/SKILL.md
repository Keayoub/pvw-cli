---
name: github-release-from-tag
description: Create a GitHub Release from an already-created git tag and a release note markdown file in releases/. Use this whenever the user asks to publish a release after tagging.
---

# GitHub Release From Tag

## When To Use
- User asks to create/publish a GitHub release after creating a tag.
- User mentions a specific version like 1.11.9 and wants release notes from `releases/`.
- Tag exists but release page is missing.

## Inputs
- Version (example: `1.11.9`) or tag (example: `v1.11.9`).
- Release notes file in `releases/`.

Default notes resolution order:
1. `releases/v<version>.md`
2. `releases/<version>.md`

## Standard Command
From repository root:

```powershell
./scripts/create_github_release.ps1 -Version <MAJOR.MINOR.PATCH>
```

Example:

```powershell
./scripts/create_github_release.ps1 -Version 1.11.9
```

## Advanced Options
- Explicit tag and notes file:

```powershell
./scripts/create_github_release.ps1 -Tag v1.11.9 -NotesFile releases/v1.11.9.md
```

- Draft or prerelease:

```powershell
./scripts/create_github_release.ps1 -Version 1.11.9 -Draft
./scripts/create_github_release.ps1 -Version 1.11.9 -PreRelease
```

- Replace an existing release for same tag:

```powershell
./scripts/create_github_release.ps1 -Version 1.11.9 -Force
```

## Validation Checklist
Before executing:
- Ensure git tag exists locally and on `origin`.
- Ensure release note file exists in `releases/`.

After executing:
- Confirm the release is visible at:
  `https://github.com/Keayoub/pvw-cli/releases/tag/v<version>`

## Failure Recovery
- If tag is missing on origin, run:

```powershell
git push origin v<version>
```

- If `gh` is unavailable, script falls back to REST API and requires `GITHUB_TOKEN`.
