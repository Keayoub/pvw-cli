---
name: release-all
description: Orchestrate full pvw-cli release in one command: version bump, release notes generation, commit, tag, push, build, and GitHub release publication.
---

# Release All (One Command)

## Intent
Use this skill when the user asks to run a full release end-to-end in one action.

## Required Input
- New version number in semantic format `MAJOR.MINOR.PATCH`.

## Single Command
Run only this command from repository root:

```powershell
./scripts/release.ps1 -NewVersion <MAJOR.MINOR.PATCH> -Push -Build
```

Example:

```powershell
./scripts/release.ps1 -NewVersion 1.11.10 -Push -Build
```

## What This Command Handles
- Update package version files.
- Auto-create release notes at `releases/v<version>.md` if missing.
- Commit release changes.
- Create annotated git tag `v<version>`.
- Push commit and tag to origin.
- Build package artifacts.
- Create GitHub release from the generated notes.

## Strict Orchestration Rules
- Do not manually run separate `git tag`, `git push`, or `gh release create` commands when this flow is requested.
- Do not call `scripts/create_github_release.ps1` directly for full releases.
- Use manual sub-commands only for troubleshooting after a failed full release run.

## Optional Overrides
- Skip GitHub release creation:

```powershell
./scripts/release.ps1 -NewVersion <MAJOR.MINOR.PATCH> -Push -Build -SkipGitHubRelease
```

- Release without build:

```powershell
./scripts/release.ps1 -NewVersion <MAJOR.MINOR.PATCH> -Push
```

## Post-Run Validation
- Confirm tag exists remotely.
- Confirm GitHub release page exists for `v<version>`.
- Confirm package version is published as expected.
