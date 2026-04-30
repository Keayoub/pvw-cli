---
name: "PurviewCli"
description: "Coding assistant for the pvw-cli repository. Specializes in Microsoft Purview CLI tooling, Python Click commands, REST client abstractions, bulk operations, and Azure/Purview API integrations."
tools: [execute/getTerminalOutput, execute/killTerminal, execute/sendToTerminal, execute/createAndRunTask, execute/runInTerminal, execute/runNotebookCell, execute/testFailure, execute/runTests, read/terminalSelection, read/terminalLastCommand, read/getNotebookSummary, read/problems, read/readFile, read/viewImage, read/readNotebookCellOutput, edit/createDirectory, edit/createFile, edit/createJupyterNotebook, edit/editFiles, edit/editNotebook, edit/rename, search/changes, search/codebase, search/fileSearch, search/listDirectory, search/searchResults, search/textSearch, search/usages, web/fetch, azure-mcp/acr, azure-mcp/advisor, azure-mcp/aks, azure-mcp/appconfig, azure-mcp/applens, azure-mcp/applicationinsights, azure-mcp/appservice, azure-mcp/azd, azure-mcp/azuremigrate, azure-mcp/azureterraformbestpractices, azure-mcp/bicepschema, azure-mcp/cloudarchitect, azure-mcp/communication, azure-mcp/compute, azure-mcp/confidentialledger, azure-mcp/containerapps, azure-mcp/cosmos, azure-mcp/datadog, azure-mcp/deploy, azure-mcp/deviceregistry, azure-mcp/documentation, azure-mcp/eventgrid, azure-mcp/eventhubs, azure-mcp/extension_azqr, azure-mcp/extension_cli_generate, azure-mcp/extension_cli_install, azure-mcp/fileshares, azure-mcp/foundry, azure-mcp/foundryextensions, azure-mcp/functionapp, azure-mcp/functions, azure-mcp/get_azure_bestpractices, azure-mcp/grafana, azure-mcp/group_list, azure-mcp/group_resource_list, azure-mcp/keyvault, azure-mcp/kusto, azure-mcp/loadtesting, azure-mcp/managedlustre, azure-mcp/marketplace, azure-mcp/monitor, azure-mcp/mysql, azure-mcp/policy, azure-mcp/postgres, azure-mcp/pricing, azure-mcp/quota, azure-mcp/redis, azure-mcp/resourcehealth, azure-mcp/role, azure-mcp/search, azure-mcp/servicebus, azure-mcp/servicefabric, azure-mcp/signalr, azure-mcp/speech, azure-mcp/sql, azure-mcp/storage, azure-mcp/storagesync, azure-mcp/subscription_list, azure-mcp/virtualdesktop, azure-mcp/wellarchitectedframework, azure-mcp/workbooks]
---

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
**Lazy CLI Module Loading:** [IMPLEMENTED] CLI now uses LazyGroup to defer module imports until first use. When adding commands, register in _MODULE_MAP in cli.py. Reduces startup time for help/version-only invocations by 200-500ms.

**Client Singleton Caching:** [IMPLEMENTED] Use `get_cached_client(Entity, profile=ctx.obj.get("profile"))` instead of `Entity()`. Reduces credential initialization overhead per command by 500-1500ms. Cache is profile-scoped via `purviewcli.client.client_cache`.

**Lazy Credential Loading:** [IMPLEMENTED] DefaultAzureCredential initialization deferred until first API call in `PurviewClient._initialize_session()`. No action needed—inherited by all client classes.

**Read-Query Caching:** [IMPLEMENTED] Use `get_read_query_cache()` for search/list/read ops. Configure TTL (default 60s). Invalidate on mutations. Access via `purviewcli.client.query_cache`. Caches result with MD5(method_name + params) as key, excludes auth fields.

**Table Rendering:** [IMPLEMENTED] Use `create_cached_table(schema_name)` instead of creating tables manually. Pre-registered schemas: entity_summary, entity_list, glossary_terms, classifications, lineage_graph, search_results. Register custom schemas via `get_table_cache().register_schema()`.

**Diagnostics & Monitoring:** New `pvw diagnostics` command group provides cache-stats, profile-info, clear-cache. Use to check hit rates, memory usage, and profile scope.

**Batch API Requests:** [PLANNED] Not yet implemented. Requires endpoint analysis to identify batch-capable operations and request coalescing in api_client layer.

See `doc/performance-optimization-guide.md` for implementation patterns and best practices.

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