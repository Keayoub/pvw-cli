# Purview Unified Catalog → Fabric OneLake Catalog Sync

> Microsoft Purview's data governance capabilities are converging into Microsoft Fabric.
> This guide covers `pvw fabric sync`, a repeatable, safe path for moving portable
> Unified Catalog (UC) metadata into the Fabric OneLake catalog.
>
> For an at-a-glance status board of everything that is/isn't portable today (and what to
> watch on the Fabric roadmap), see
> [Purview to Fabric OneLake Sync Overview](purview-to-fabric-onelake-sync.md).

> **WARNING: `pvw fabric sync` is experimental. Do not use sync operations in
> production.** Test only with non-production Purview and Fabric resources. The
> operational commands display this warning in table mode; JSON mode omits
> notices so stdout remains machine-readable. `capabilities` and `roadmap` are
> read-only status/roadmap lookups, not proof of production readiness.

## What this does (and does not) do

`pvw fabric sync` is a **one-way, metadata-only** sync from Purview UC into Fabric:

| Purview UC concept | Fabric target | Portable? |
|---|---|---|
| Data asset display name / description | Fabric item `displayName` / `description` | Yes |
| Governance domain | Fabric domain (+ workspace assignment) | Yes (by name) |
| Glossary term / data product / critical data element (CDE) | Namespaced Fabric tag (`purview:<type>:<name>`) | Partial — only the name survives as a tag |
| Term/CDE/data product hierarchy, relationships, custom attributes, lineage | *(no Fabric equivalent)* | No — reported for audit only |

Nothing is ever written back to Purview. Every command defaults to a **dry run**; only
`--apply` performs writes, and only to Fabric.

## Matching policy: how an asset is linked to a Fabric item

### Reviewed offline export to Fabric

To let a customer select assets and approve description changes before sync,
use the standalone [Purview UC export](commands/unified-catalog.md#portable-catalog-export-no-fabric-dependency).
Run the read-only preparation command to discover existing Fabric items by
exact name. It writes a **new draft outside the export folder** with item IDs,
workspace names, Fabric types and reasons for each suggestion. Each asset has
a `reviewStatus` (`no_candidate`, `single_candidate`, or `multiple_candidates`);
each suggestion includes a `proposedMapping` object ready to copy. Suggestions
never pre-select an asset or approve a mapping:

```powershell
pvw fabric sync prepare --snapshot-dir .\purview-snapshot --output-file .\decisions.json
```

Review the draft with the customer. Copy **only verified** `proposedMapping`
objects into the top-level `mappings` array, add their Purview IDs to
`selectedAssetIds`, and supply optional `descriptions`. Exactly one explicit
mapping is required per selected asset, including
`expectedFabricType` (`Lakehouse`, `SemanticModel` or `Warehouse`). A UC asset
of type `General` does **not** prove which Fabric item type it represents:
confirm its identity and type manually. The prepared file is a convenience,
not an authorization. Then run:

```powershell
pvw uc validate-export --snapshot-dir .\purview-snapshot --decisions-file .\decisions.json
pvw fabric sync assess --snapshot-dir .\purview-snapshot --decisions-file .\decisions.json --report-file .\assessment.json
pvw fabric sync apply --snapshot-dir .\purview-snapshot --decisions-file .\decisions.json --checkpoint-file .\checkpoint.json
# Only after reviewing the assessment and dry-run, on non-production resources:
pvw fabric sync apply --snapshot-dir .\purview-snapshot --decisions-file .\decisions.json --checkpoint-file .\checkpoint.json --apply
```

This mode **does not call Purview** during assess/apply. It verifies export
checksums, integer schema versions and file counts, selected IDs,
relationships and mappings before reading Fabric, then
uses the existing planner with fresh Fabric state. It compares the approved
workspace/item IDs and the approved item type against the current catalog and
Get Item response and plans from that same verified response (not a second
unverified read);
unknown, missing or mismatched types block the entire reviewed apply before
any write. Missing mapping targets and conflicts must be resolved before
application. It does not infer mappings from
embedded IDs, update Fabric domains, or support `--sync-classifications`;
`--mapping-file` and `--purview-domain-id` cannot be combined with this mode.
It remains experimental and **must not be used in production**. An export can
be stale: re-export if Purview changes and review a new decisions file.

**Future enhancement, not yet implemented:** a local mapping UI under `tools/`
could simplify reviewing candidates and editing the same decisions file. Build
it after tenant validation of this CLI workflow; it must reuse the CLI validation
and safety gates rather than approve matches or apply changes on its own.

A Purview asset is only ever written to if it resolves to **exactly one** Fabric item, via
(in priority order):

1. **Embedded Fabric reference** — a `fabricRef`-shaped hint already present in the asset's
   `source`/`typeProperties` (e.g. populated by a prior integration).
2. **Explicit mapping file** (`--mapping-file`) — see
   [`samples/json/fabric_sync/mapping_file.json`](../samples/json/fabric_sync/mapping_file.json).

Anything else is reported `unmatched` with **non-authoritative name suggestions only** —
name similarity alone never authorizes a write. Resolve genuine matches by adding an entry
to the mapping file, or leave the asset unmatched and migrate it manually.

## Conflict and overflow policies

- **Item metadata**: filling a *blank* Fabric field from Purview data is never a conflict.
  Overwriting an *already-populated*, differing value requires `--overwrite`.
- **Descriptions** over Fabric's 256-character limit are a validation error unless you pass
  `--truncate-descriptions` (which truncates to exactly 256 characters).
- **Governance tags**: Fabric allows at most 10 tags per item. If applying every new
  governance tag would exceed that limit, **none** of the new tags are applied (all-or-nothing)
  and the item is reported `tag_overflow` for manual pruning. Pre-existing tags are always
  preserved.
- **Domain workspace assignment**: a workspace already assigned to a *different* Fabric
  domain is always reported as a conflict and never reassigned automatically — this is
  independent of `--overwrite`, which only governs item metadata.

## Syncing classifications & labels onto existing Fabric items

For assets that already exist as Fabric items (created directly in Fabric, or by an earlier
run of this tool), you can optionally sync a Purview asset's **classifications** and
**labels** onto the matched Fabric item as tags, in addition to the glossary-term/data-
product/CDE tags described above. This is opt-in via `--sync-classifications` on
`assess`/`apply`/`run`.

- Classification names (e.g. `MICROSOFT.PERSONAL.EMAIL`) and free-text labels are each
  namespaced as Fabric tags: `purview:classification:<name>` and `purview:label:<name>`
  (same 40-character-truncated, additive-only pipeline as governance-object tags — see
  above).
- **Source**: classifications/labels are read from the classic Atlas **Entity API**
  (`entityReadUniqueAttribute`), not the Unified Catalog Data Asset API — the UC wrapper does
  not expose this data at all, even with `includeExtendedProperties=true` (live-verified).
  This means the sync only works for assets that have a resolvable Data Map entity: the
  asset's `source.qualifiedName` must be present, and its UC `type` must have a known
  Atlas-`typeName` mapping (currently: `ADLSGen2Path`, `AzureSqlTable`). Assets that don't
  meet both conditions are silently skipped (reported as having no classifications/labels)
  rather than failing the run.
- **Sensitivity labels (MIP) are not synced.** Purview exposes no confirmed per-asset read
  API for a data asset's actual sensitivity label — only tenant-wide aggregate reporting
  endpoints exist. See [`fabric-sync-feature-parity.md`](fabric-sync-feature-parity.md)
  for what's implemented today versus tracked as a future item once a Fabric/Purview API
  makes this possible.

```powershell
pvw fabric sync assess --sync-classifications --mapping-file .\mapping_file.json
```

## Commands

### `pvw fabric sync assess`

Always read-only. Fetches Purview UC state and the current Fabric catalog, computes the
full plan, and reports it — nothing is written.

```powershell
pvw fabric sync assess `
  --purview-domain-id b1c9e6b0-0000-0000-0000-000000000001 `
  --workspace-id 9d6a6f2f-2e2b-4f8b-9b3b-000000000010 `
  --mapping-file .\mapping_file.json `
  --report-file .\reports\assessment.json `
  --csv-report-file .\reports\assessment.csv
```

Exits non-zero if the plan contains any conflicts, validation errors, tag overflow, a
workspace-domain assignment conflict, or an unresolvable mapping-file entry, so it can gate
a pipeline before anyone runs `apply --apply`.

### `pvw fabric sync apply`

Same assessment, then applies (or dry-runs) the resulting operations against Fabric in
dependency order: domains → workspace assignment → tag definitions → tag application →
item metadata.

```powershell
# Dry run (default) — shows exactly what would change, writes nothing.
pvw fabric sync apply --mapping-file .\mapping_file.json --checkpoint-file .\checkpoints\run1.json

# Apply for real.
pvw fabric sync apply --mapping-file .\mapping_file.json --checkpoint-file .\checkpoints\run1.json --apply
```

Every successful write is checkpointed immediately to `--checkpoint-file`. Re-running
`apply --apply` against the same checkpoint file is **idempotent**: operations whose desired
state hasn't changed are skipped, and only genuinely new/changed operations are (re)applied.
Independent operation failures don't stop the run — the command reports every failure and
exits non-zero if any occurred.

### `pvw fabric sync run --config <file>`

A config-file-driven equivalent of `apply`, intended for schedulers/pipelines where passing a
long option list isn't convenient. See
[`samples/json/fabric_sync/run_config.json`](../samples/json/fabric_sync/run_config.json)
for the full set of keys (they mirror `apply`'s option names).

```powershell
pvw fabric sync run --config .\run_config.json
```

### `pvw fabric sync rollback`

Reverses a completed run's item metadata, tag application, and workspace-domain assignment
changes — derived **purely from the checkpoint file**, never by re-running matching or
planning. This makes it safe to run long after the source Purview/Fabric state has moved on.

```powershell
# Preview (default) — shows what would be reverted, writes nothing.
pvw fabric sync rollback --checkpoint-file .\checkpoints\run1.json

# Actually restore.
pvw fabric sync rollback --checkpoint-file .\checkpoints\run1.json --apply
```

**Fabric domains and tag definitions created by a run are never deleted by rollback** —
only item metadata, tag *application*, and workspace-domain *assignment* are reversed.

## Required Fabric permissions

The identity running these commands needs, at minimum:

- **Fabric administrator** (tenant-level) — to list/read tenant tags, create tags, and
  list/create/update domains.
- **Contributor or higher** on every target workspace — to read and update items and to
  accept domain assignment.

Authentication uses the same Azure identity chain as the rest of `pvw` (`DefaultAzureCredential`,
falling back to the Azure CLI's cached login), scoped to the Fabric API audience.

## Scheduling and unattended runs

`pvw fabric sync run --config <file>` is the intended entry point for scheduled jobs
(cron, Azure DevOps/GitHub Actions pipelines, Fabric/ADF pipelines invoking a shell step,
etc.). Keep `--checkpoint-file` on durable storage shared across runs so repeated
invocations remain idempotent, and treat a non-zero exit code as a signal to alert/stop the
pipeline rather than silently retry (conflicts and validation errors require a human to
resolve the mapping file or adjust `--overwrite`/`--truncate-descriptions`).

## Command reference

| Command | Writes to Fabric? | Default | Key options |
|---|---|---|---|
| `pvw fabric sync capabilities` | Never (no client I/O at all) | — | `--status`, `--output` |
| `pvw fabric sync roadmap` | Never (reads public Fabric GPS API) | — | `--status planned\|shipped`, `--output table\|json` |
| `pvw fabric sync prepare` | Never (reads Fabric catalog) | — | `--snapshot-dir`, `--output-file`, `--workspace-id` |
| `pvw fabric sync assess` | Never | — | `--purview-domain-id`, `--workspace-id`, `--mapping-file` or `--snapshot-dir` + `--decisions-file`, `--overwrite`, `--truncate-descriptions`, `--sync-classifications` (live source only), `--report-file`, `--csv-report-file`, `--output` |
| `pvw fabric sync apply` | Only with `--apply` | Dry run | All of the above, plus `--checkpoint-file` (required), `--apply` |
| `pvw fabric sync run --config <file>` | Only if `"apply": true` in the config | Dry run | `--config` (JSON file with the same keys as `apply`) |
| `pvw fabric sync rollback` | Only with `--apply` | Preview | `--checkpoint-file` (required), `--apply`, `--report-file`, `--output` |

`pvw fabric sync capabilities` prints the same feature-status board as
[Purview to Fabric OneLake Sync Overview](purview-to-fabric-onelake-sync.md), live from the
CLI's own capability data — useful for scripting a quick "what's supported today" check
without reading docs.

`pvw fabric sync roadmap` retrieves the current Fabric GPS governance roadmap in
read-only mode; see the [dated snapshot and caveats](purview-to-fabric-onelake-sync.md#fabric-gps-snapshot-2026-09-25).
Roadmap `Shipped` does not mean the sync capability is implemented or tenant-verified.

## Verification status

The Fabric-side API shapes this tool relies on (catalog search, domains, item read/update, tag
list/apply/unapply, item create with `source.type`) were confirmed against a live Fabric
tenant, which surfaced and fixed two real discrepancies from the initial implementation:

- `GET /v1/admin/domains` returns `{"domains": [...]}`, not a `value`-keyed envelope.
- `POST /v1/catalog/search` entries nest their workspace under `hierarchy.workspace.{id,displayName}`,
  not flat `workspaceId`/`workspaceDisplayName` fields.

The Purview side has been partially verified against a live tenant. A read-only
validation on 2026-09-30 exported a valid schema-v1 snapshot containing one domain,
one term, and zero assets/data products/CDEs. Direct `data-asset list` returned
`{"value": [], "count": 0}`, confirming that zero assets came from the selected
profile rather than export filtering:

- `pvw uc domain list` matches the field names already assumed (`id`/`name`/`description`/
  `type`/`status`/`managedAttributes`).
- The classic Atlas Entity API's `classifications` (`[{"typeName", ...}]`) and `labels`
  (`["..."]`) fields were confirmed live and are the source for `--sync-classifications`.
- The Unified Catalog Data Asset API (`list_data_assets`/`get_data_asset`) was confirmed to
  **not** expose classifications, labels, tags, or a sensitivity label, even with
  `includeExtendedProperties=true`.
- Purview's Unified Catalog data asset/domain/term/data-product/CDE field names beyond
  the observed empty/list responses are still unverified against a populated live tenant.
  If your responses differ from what's assumed in `purviewcli/sync/service.py`, the
  normalization functions there are the place to adjust.
- The same 2026-09-30 run normalized 312 live Fabric catalog items, including 25
  Lakehouses, 37 Semantic Models, and 11 Warehouses. `sync prepare` completed without
  writes; its empty decisions draft was correctly rejected because no Purview asset was
  selected or mapped. This validates connectivity and safeguards, not an end-to-end asset
  sync.

See [`fabric-sync-feature-parity.md`](fabric-sync-feature-parity.md) for the full
feature-by-feature implementation status, including what's tracked as future work pending
Fabric/Purview API availability (e.g. sensitivity-label sync).
