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

## Performance Optimizations (Purview CLI-specific)
**Lazy CLI Module Loading:** CLI registers all 8+ module groups upfront in `cli.py`. When adding commands, use dynamic discovery or Click's lazy loading pattern to defer module import until first use. This reduces startup time for help/version-only invocations.

**Client Singleton Caching:** Each CLI command instantiates new client objects (Entity(), Glossary(), etc.), which triggers credential initialization. Implement module-level or context-based client caching with weak references. Cache key should include auth profile to support multi-profile workflows.

**Batch API Requests:** Bulk operations spawn sequential API calls with 200ms throttling. When designing bulk features, use batching endpoints where available or implement request coalescing in the API client layer. Validate endpoint supports batching before coalescing.

**Read-Query Caching:** Search, list, and read ops often repeat in user scripts. Add optional in-memory cache with configurable TTL (default 5-60s) for read-only queries. Exclude writes and mutations. Cache key must include filter parameters; invalidate on mutations in same session.

**Lazy Credential Loading:** DefaultAzureCredential initialization on every client creation adds latency. Defer credential loading until first API call. Use a single global credential instance shared across clients; test with `--no-auth-cache` flag if needed.

**Table Rendering:** Rich tables are regenerated per command. Cache table schema definitions (columns, styles) in template classes. Reuse across similar report commands; update only data rows.

**Anti-patterns to avoid:** Do not add disk-based persistent caching (stateless CLI principle); avoid unclean global state (always cleanup in context managers); do not cache mutable/mutable results without invalidation strategy; do not cache across different Azure subscriptions/profiles without explicit scoping.

## Release Workflow (repo-specific)
- When the user says they are ready to publish, use the release script at `scripts/release.ps1` (case-insensitive path on Windows; user may refer to `scripts/Release.ps1`).
- Prefer command pattern: `./scripts/release.ps1 -NewVersion <MAJOR.MINOR.PATCH> -Push -Build`.
- The script is the source of truth for release automation and must be used instead of manual version/tag steps unless the user explicitly asks otherwise.
- Expected script behavior to rely on:
  - Validates semantic version format.
  - Requires clean git working tree unless `-Force` is provided.
  - Updates version values in `pyproject.toml` and `purviewcli/__init__.py`.
  - Updates matching version strings in `README.md`.
  - Runs pre-commit build verification via `scripts/build_pypi.ps1` when available.
  - Commits changes with message `Bump version to <version>`.
  - Creates annotated git tag `v<version>`.
  - Pushes commit and tag when `-Push` is used.
  - Runs build step when `-Build` is used.
- For release requests, ask only for missing required input (`-NewVersion`) and then execute the script.
- Do not create tags or perform separate manual commit/push steps before the script, because the script already handles those operations.

## Profiling and Performance Diagnosis
- For startup performance: Time CLI invocation with `Measure-Command` in PowerShell; profile module imports using `python -m cProfile`.
- For bulk operations: Compare execution time across `--bulk-size`, `--max-parallel` parameters; refer to `entity analyze-performance` command for baseline math.
- For API latency: Enable debug mode to inspect request/response timing; check rate limit headers (`x-ms-ratelimit-remaining-subscription-requests`).
- For memory usage: Use `memory_profiler` on bulk jobs; watch for client/credential leak patterns.


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