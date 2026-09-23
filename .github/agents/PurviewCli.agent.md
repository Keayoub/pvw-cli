---
name: "PurviewCli"
description: "Coding assistant for the pvw-cli repository. Specializes in Microsoft Purview CLI tooling, Python Click commands, REST client abstractions, bulk operations, and Azure/Purview API integrations."
tools: [vscode, execute, read, agent, edit, search, web, azure-mcp/search, browser, todo]
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

**Batch API Requests:** [PLANNED] Not yet implemented. Requires endpoint analysis to identify batch-capable operations and request coalescing in api_client layer. If the user requests batch API operations, inform them this feature is not yet implemented and suggest using built-in rate limiting with `--bulk-size` and `--max-parallel` parameters as a workaround.

See `doc/performance-optimization-guide.md` for implementation patterns and best practices.

## Release Workflow (repo-specific)

Use this decision table to select the correct release path:

| Scenario | Action |
| --- | --- |
| Tag does **not** yet exist (full end-to-end release) | Run `./scripts/release.ps1 -NewVersion <MAJOR.MINOR.PATCH> -Push -Build` |
| Tag **already exists** and only a GitHub Release object is needed | Run `./scripts/create_github_release.ps1 -Version <MAJOR.MINOR.PATCH>` |

**A tag-only request** is one where the user explicitly states the git tag already exists and only wants the GitHub Release object created (e.g., "create a GitHub release from the existing tag v1.2.3"). Otherwise treat as a full end-to-end release.

- The release script (`scripts/release.ps1`) is the source of truth for version bump, commit, tag, and push. Do not create tags or perform manual commit/push steps before running it.
- For release requests, ask only for missing required input (`-NewVersion`) and then execute the script.
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

## Purview -> Fabric OneLake Catalog Sync (feature area)

Purview's standalone data governance experience is converging into Microsoft Fabric, so
`pvw fabric sync` provides a one-way, metadata-only, dry-run-by-default sync from Purview
Unified Catalog into the Fabric OneLake catalog.

Layout and entry points:
- Logic lives in `purviewcli/sync/` (`models.py`, `service.py`, `purview_to_fabric.py`,
  `execution.py`, `state.py`, `reporting.py`, `capabilities.py`); CLI in `purviewcli/cli/fabric.py`.
- Commands: `pvw fabric sync capabilities|assess|apply|run|rollback`. Prefer the wording
  "sync" over "migration" (it is a repeatable, checkpointed sync, not a one-time cutover).
- Writes are additive-only and never write back to Purview. `apply`/`rollback` require
  `--apply`; everything else dry-runs or previews.

Feature status tracking (keep these three in agreement):
- `purviewcli/sync/capabilities.py` is the single source of truth, rendered live by
  `pvw fabric sync capabilities`.
- `docs/purview-to-fabric-onelake-sync.md` is the summary/status board (carries a
  "Last reviewed" date and a re-check checklist).
- `docs/fabric-sync-feature-parity.md` holds full per-capability implementation detail.

Live-verify-first convention (important):
- Never assume a Purview/Fabric request or response shape from documentation alone. Verify
  against a real tenant or the published OpenAPI specs before implementing or before
  flipping a capability's status. This convention has already caught real discrepancies.
- Known verified facts: classifications/labels are only exposed by the classic Atlas Entity
  API (`entityReadUniqueAttribute`), NOT the UC Data Asset API (even with
  `includeExtendedProperties=true`); creating a UC data asset requires
  `source.type = "DataMap"`.

Sources for re-checking the Fabric roadmap and API surface (browser-free where possible):
- `https://github.com/microsoft/fabric-rest-api-specs` - authoritative OpenAPI specs, best
  signal for "does this API exist?". Fetch raw JSON, or use
  `gh api "search/code?q=<term>+repo:microsoft/fabric-rest-api-specs"`.
- `https://www.fabric-gps.com/api/releases` - queryable JSON mirror of the Fabric roadmap
  (`q`, `product_name`, `release_status`, `release_type`, `modified_within_days`); response
  envelope is `data`/`links`/`pagination`. Docs at `https://www.fabric-gps.com/endpoints`.
- `https://roadmap.fabric.microsoft.com/` - official roadmap, but a JS-rendered SPA, so it
  requires actual browser tools; the two sources above work with plain HTTP. It renders
  correctly and completely, but note the filter defaults to `Planned`, so the card count
  looks small (e.g. 8 for Administration/Governance/Security - verified 2026-09-22 to be
  the true planned total, not truncation). Prefer Fabric GPS for bulk queries anyway,
  since it needs no browser and is filterable.
- `https://github.com/microsoft/fabric-cli` - read-only reference for client patterns. It is
  NOT a runtime dependency of this repo; do not add it as one.

Fabric GPS query gotchas:
- `product_name` must match exactly, including commas - it is
  `"Administration, Governance and Security"`, not `"Administration and governance"`.
  A wrong value returns `total_items: 0` rather than an error.
- The title field is `feature_name` (not `title`); other useful fields are
  `release_status`, `release_type`, `release_date`, `feature_description`, `blog_url`.
- Discover valid product names with `?page_size=200` and grouping on `product_name`.

Browser tooling notes (Windows):
- The built-in integrated browser tools (`openBrowserPage` / `readPage` /
  `runPlaywrightCode`) do render the roadmap SPA correctly - use these first.
- `runPlaywrightCode` does NOT surface return values and has no `fs` access, so results must
  be read back via `readPage`. React re-renders wipe any DOM you inject, so do not try to
  stash output in the page. Driving `playwright-core` directly from PowerShell avoids both
  limits and is a good fallback when MCP browser tools are absent from the session.
- Do not run `npx playwright install chrome`: it fails without Administrator rights AND
  deletes the bundled `chromium-*` build as "unused" first. Recover with
  `npx playwright install chromium`.
- Playwright MCP defaults to the real Chrome channel. It is configured in
  `%APPDATA%\Code\User\mcp.json` with `"--browser", "chromium"` so it uses the bundled
  build instead of requiring a Chrome install.
- The bundled build is version-pinned: `@playwright/mcp@latest` tracks a specific
  `chromium-<rev>` and fails with `Browser "chrome-for-testing" is not installed` if only
  an older revision is present. Install the matching revision with that package's own CLI
  (`node_modules/.bin/playwright install chromium`) - a bare
  `npx playwright@<ver> install chromium` may silently no-op.

## Profiling and Performance Diagnosis
- For startup performance: Time CLI invocation with `Measure-Command` in PowerShell; profile module imports using `python -m cProfile`.
- For bulk operations: Compare execution time across `--bulk-size`, `--max-parallel` parameters; refer to `entity analyze-performance` command for baseline math.
- For API latency: Enable debug mode to inspect request/response timing; check rate limit headers (`x-ms-ratelimit-remaining-subscription-requests`).
- For memory usage: Use `memory_profiler` on bulk jobs; watch for client/credential leak patterns.