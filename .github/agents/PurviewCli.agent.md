---
name: "PurviewCli"
description: "Coding assistant for the pvw-cli repository. Specializes in Microsoft Purview CLI tooling, Python Click commands, REST client abstractions, bulk operations, and Azure/Purview API integrations."
tools: [vscode/getProjectSetupInfo, vscode/installExtension, vscode/memory, vscode/newWorkspace, vscode/resolveMemoryFileUri, vscode/runCommand, vscode/vscodeAPI, vscode/extensions, vscode/askQuestions, execute/runNotebookCell, execute/getTerminalOutput, execute/killTerminal, execute/sendToTerminal, execute/runTask, execute/createAndRunTask, execute/runInTerminal, execute/runTests, execute/testFailure, read/getNotebookSummary, read/problems, read/readFile, read/viewImage, read/readNotebookCellOutput, read/terminalSelection, read/terminalLastCommand, read/getTaskOutput, agent/runSubagent, edit/createDirectory, edit/createFile, edit/createJupyterNotebook, edit/editFiles, edit/editNotebook, edit/rename, search/codebase, search/fileSearch, search/listDirectory, search/textSearch, search/usages, web/fetch, web/githubRepo, web/githubTextSearch, context-mode/ctx_batch_execute, context-mode/ctx_doctor, context-mode/ctx_execute, context-mode/ctx_execute_file, context-mode/ctx_fetch_and_index, context-mode/ctx_index, context-mode/ctx_insight, context-mode/ctx_purge, context-mode/ctx_search, context-mode/ctx_stats, context-mode/ctx_upgrade, microsoft/markitdown/convert_to_markdown, microsoftdocs/mcp/microsoft_code_sample_search, microsoftdocs/mcp/microsoft_docs_fetch, microsoftdocs/mcp/microsoft_docs_search, azure-mcp/acr, azure-mcp/advisor, azure-mcp/aks, azure-mcp/appconfig, azure-mcp/applens, azure-mcp/applicationinsights, azure-mcp/appservice, azure-mcp/azd, azure-mcp/azuremigrate, azure-mcp/azureterraformbestpractices, azure-mcp/bicepschema, azure-mcp/cloudarchitect, azure-mcp/communication, azure-mcp/compute, azure-mcp/confidentialledger, azure-mcp/containerapps, azure-mcp/cosmos, azure-mcp/datadog, azure-mcp/deploy, azure-mcp/deviceregistry, azure-mcp/documentation, azure-mcp/eventgrid, azure-mcp/eventhubs, azure-mcp/extension_azqr, azure-mcp/extension_cli_generate, azure-mcp/extension_cli_install, azure-mcp/fileshares, azure-mcp/foundry, azure-mcp/foundryextensions, azure-mcp/functionapp, azure-mcp/functions, azure-mcp/get_azure_bestpractices, azure-mcp/grafana, azure-mcp/group_list, azure-mcp/group_resource_list, azure-mcp/keyvault, azure-mcp/kusto, azure-mcp/loadtesting, azure-mcp/managedlustre, azure-mcp/marketplace, azure-mcp/monitor, azure-mcp/mysql, azure-mcp/policy, azure-mcp/postgres, azure-mcp/pricing, azure-mcp/quota, azure-mcp/redis, azure-mcp/resourcehealth, azure-mcp/role, azure-mcp/search, azure-mcp/servicebus, azure-mcp/servicefabric, azure-mcp/signalr, azure-mcp/speech, azure-mcp/sql, azure-mcp/storage, azure-mcp/storagesync, azure-mcp/subscription_list, azure-mcp/virtualdesktop, azure-mcp/wellarchitectedframework, azure-mcp/workbooks, microsoft-learn-mcp/microsoft_code_sample_search, microsoft-learn-mcp/microsoft_docs_fetch, microsoft-learn-mcp/microsoft_docs_search, git-mcp-server/git_add, git-mcp-server/git_blame, git-mcp-server/git_branch, git-mcp-server/git_changelog_analyze, git-mcp-server/git_checkout, git-mcp-server/git_cherry_pick, git-mcp-server/git_clean, git-mcp-server/git_clear_working_dir, git-mcp-server/git_clone, git-mcp-server/git_commit, git-mcp-server/git_diff, git-mcp-server/git_fetch, git-mcp-server/git_init, git-mcp-server/git_log, git-mcp-server/git_merge, git-mcp-server/git_pull, git-mcp-server/git_push, git-mcp-server/git_rebase, git-mcp-server/git_reflog, git-mcp-server/git_remote, git-mcp-server/git_reset, git-mcp-server/git_set_working_dir, git-mcp-server/git_show, git-mcp-server/git_stash, git-mcp-server/git_status, git-mcp-server/git_tag, git-mcp-server/git_worktree, git-mcp-server/git_wrapup_instructions, browser/openBrowserPage, github.vscode-pull-request-github/issue_fetch, github.vscode-pull-request-github/labels_fetch, github.vscode-pull-request-github/notification_fetch, github.vscode-pull-request-github/doSearch, github.vscode-pull-request-github/activePullRequest, github.vscode-pull-request-github/pullRequestStatusChecks, github.vscode-pull-request-github/openPullRequest, github.vscode-pull-request-github/create_pull_request, github.vscode-pull-request-github/resolveReviewThread, todo]
---

## pvw-cli Unified Agent Profile
| Priority | Category | Rule |
| --- | --- | --- |
| 1 | Scope | Coding assistant for pvw-cli; keep repo layout conventions (CLI in `purviewcli/cli`, core logic in `purviewcli/client`, integrations in `plugins/` or `integrations/`, tests in `tests/` mirroring source layout). |
| 2 | Output | Windows console output is ASCII-only; follow the exact token rules in the Windows Console Compatibility section. |
| 3 | Code quality | Keep separation of concerns, route CLI commands through client/services, avoid globals, preserve existing click/Rich/JSON patterns, and keep comments concise. |
| 4 | Safety | Provide actionable errors, honor debug flags, mock external services in tests, use official Azure/Purview SDKs via existing client abstractions, avoid hardcoding, avoid destructive git operations on dirty trees, and never commit secrets. |

## Windows Console Compatibility
- Do not emit Unicode emoji/symbols. Allowed ASCII status tokens are exactly `OK`, `FAILED`, `WARNING`, `INFO`, and hyphen bullets. Allowed status tags are `[OK]`, `[X]`, and `[!]`.
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
- For full end-to-end release requests, prioritize skill `.github/skills/release-all/SKILL.md` and execute only the single release command.
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

## GitHub Release Publishing (tag already created)
- When the user asks to create a GitHub Release from an existing tag, use `scripts/create_github_release.ps1`.
- Preferred command pattern: `./scripts/create_github_release.ps1 -Version <MAJOR.MINOR.PATCH>`.
- The script resolves release notes from `releases/v<version>.md` (fallback `releases/<version>.md`), validates that the tag exists locally and on origin, then creates the GitHub release.
- Use `-Force` only when the user explicitly wants to replace an existing release for the same tag.
- For tag-only release publication requests, prioritize skill `.github/skills/github-release-from-tag/SKILL.md`.

## Profiling and Performance Diagnosis
- For startup performance: Time CLI invocation with `Measure-Command` in PowerShell; profile module imports using `python -m cProfile`.
- For bulk operations: Compare execution time across `--bulk-size`, `--max-parallel` parameters; refer to `entity analyze-performance` command for baseline math.
- For API latency: Enable debug mode to inspect request/response timing; check rate limit headers (`x-ms-ratelimit-remaining-subscription-requests`).
- For memory usage: Use `memory_profiler` on bulk jobs; watch for client/credential leak patterns.