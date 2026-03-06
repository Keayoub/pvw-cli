## pvw-cli Unified Agent Profile
- Role: Coding assistant for the pvw-cli repository (Purview CLI tooling). Follow repo structure: CLI in `purviewcli/cli`, core logic in `purviewcli/client`, integrations in `plugins/` or `integrations/`, tests in `tests/` mirroring source layout.
- Windows console compatibility is mandatory: ASCII-only output (no Unicode emoji/symbols such as checkmarks or warning icons). Use words like OK, FAILED, WARNING, INFO and hyphen bullets; color tags allowed (e.g., `[green]OK[/green]`).
- Adhere to clean architecture and separation of concerns; delegate CLI commands to client/services; avoid mixing layers or using globals.
- Preserve existing coding patterns in touched files (click options, Rich console usage, status tables, JSON handling). Keep output parse-friendly.
- Error handling: provide actionable messages; respect debug flags; do not leak stack traces unless debug is enabled.
- Documentation/comments: keep concise and only when logic is non-obvious; default to ASCII.
- Testing: place tests in `tests/` mirroring source; mock external services.
- Azure/Purview integrations: use official SDKs/REST; route through existing client abstractions; prefer configuration over hardcoding.
- Avoid destructive git operations on dirty worktrees; do not commit secrets; avoid bulk shell replaces that risk corruption.

## Windows Console Compatibility
- Do not emit Unicode emoji/symbols. Use ASCII substitutes: OK/FAILED/WARNING/INFO; hyphen bullets; status tags like `[OK]`, `[X]`, `[!]` are acceptable.
- Example: `console.print("[green]OK[/green] Term created")` instead of Unicode checkmarks.

## Common Failure Avoidance
- Guard against missing imports (e.g., `time`, `csv`, `json`, `rich.syntax`).
- Avoid Rich-formatted output when callers expect JSON; prefer `--output json` for parseable responses.
- Use Entra Object IDs (GUIDs) for owner fields; avoid emails.
- Use built-in rate limiting for bulk ops; add delays (~200ms) if scripting.
- Make dry-run behavior explicit; warn users when `--dry-run` is set.

## Microsoft 365 Agents Toolkit (mapping reference)
- Microsoft 365 Agents Toolkit (new) = Teams Toolkit (former)
- App Manifest = Teams app manifest
- Microsoft 365 Agents Playground = Test Tool
- `m365agents.yml` = `teamsapp.yml`
- CLI package `@microsoft/m365agentstoolkit-cli` (command `atk`) = `@microsoft/teamsapp-cli` (command `teamsapp`)
- Use new names by default; mention the mapping only when it aids clarity.

## Microsoft 365/Copilot App Guidance
- For manifest work, get the schema version and use **get_schema** if available.
- For how-to/troubleshooting, use **get_knowledge** or **troubleshoot** tools when available.
- When generating/modifying code or config for M365/Copilot apps, call **get_code_snippets** with the relevant API/config/comment.