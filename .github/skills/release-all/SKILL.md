---
name: release-all
description: Orchestrate full pvw-cli release in one command: version bump, release notes generation, commit, tag, push, build, and GitHub release publication.
---

# Release All (One Command)

## Intent
Use this skill when the user asks to run a full release end-to-end in one action.

## Required Input
- New version number in semantic format `MAJOR.MINOR.PATCH`.
- If the version number is not in the format `MAJOR.MINOR.PATCH`, respond with an error message and do not proceed with the release.

## Single Command
Run only this command from repository root:

```powershell
./scripts/release.ps1 -NewVersion <MAJOR.MINOR.PATCH> -Push -Build
```

Example:

```powershell
./scripts/release.ps1 -NewVersion X.Y.Z -Push -Build
```

## What This Command Handles
- Update package version files.
- Auto-create release notes at `releases/v<version>.md` if missing. The process will fail if release notes cannot be created.
- Commit release changes.
- Create annotated git tag `v<version>`.
- Push commit and tag to origin.
- Build package artifacts.
- Create GitHub release from the generated notes.

## Orchestration Rules

### Strict Rules (always apply)
1. Do not manually run separate `git tag`, `git push`, or `gh release create` commands when this flow is requested.
2. Do not call `scripts/create_github_release.ps1` directly for full releases.
3. Use manual sub-commands only for troubleshooting after a failed full release run.

### Optional Overrides (apply only when explicitly requested)
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
