# Purview Unified Catalog → Fabric OneLake Catalog Migration

> Microsoft Purview's data governance capabilities are converging into Microsoft Fabric.
> This guide covers `pvw fabric migration`, a repeatable, safe path for moving portable
> Unified Catalog (UC) metadata into the Fabric OneLake catalog.

## What this does (and does not) do

`pvw fabric migration` is a **one-way, metadata-only** sync from Purview UC into Fabric:

| Purview UC concept | Fabric target | Portable? |
|---|---|---|
| Data asset display name / description | Fabric item `displayName` / `description` | Yes |
| Governance domain | Fabric domain (+ workspace assignment) | Yes (by name) |
| Glossary term / data product / critical data element (CDE) | Namespaced Fabric tag (`purview:<type>:<name>`) | Partial — only the name survives as a tag |
| Term/CDE/data product hierarchy, relationships, custom attributes, lineage | *(no Fabric equivalent)* | No — reported for audit only |

Nothing is ever written back to Purview. Every command defaults to a **dry run**; only
`--apply` performs writes, and only to Fabric.

## Matching policy: how an asset is linked to a Fabric item

A Purview asset is only ever written to if it resolves to **exactly one** Fabric item, via
(in priority order):

1. **Embedded Fabric reference** — a `fabricRef`-shaped hint already present in the asset's
   `source`/`typeProperties` (e.g. populated by a prior integration).
2. **Explicit mapping file** (`--mapping-file`) — see
   [`samples/json/fabric_migration/mapping_file.json`](../samples/json/fabric_migration/mapping_file.json).

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

## Commands

### `pvw fabric migration assess`

Always read-only. Fetches Purview UC state and the current Fabric catalog, computes the
full plan, and reports it — nothing is written.

```powershell
pvw fabric migration assess `
  --purview-domain-id b1c9e6b0-0000-0000-0000-000000000001 `
  --workspace-id 9d6a6f2f-2e2b-4f8b-9b3b-000000000010 `
  --mapping-file .\mapping_file.json `
  --report-file .\reports\assessment.json `
  --csv-report-file .\reports\assessment.csv
```

Exits non-zero if the plan contains any conflicts, validation errors, or tag overflow, so it
can gate a pipeline before anyone runs `sync --apply`.

### `pvw fabric migration sync`

Same assessment, then applies (or dry-runs) the resulting operations against Fabric in
dependency order: domains → workspace assignment → tag definitions → tag application →
item metadata.

```powershell
# Dry run (default) — shows exactly what would change, writes nothing.
pvw fabric migration sync --mapping-file .\mapping_file.json --checkpoint-file .\checkpoints\run1.json

# Apply for real.
pvw fabric migration sync --mapping-file .\mapping_file.json --checkpoint-file .\checkpoints\run1.json --apply
```

Every successful write is checkpointed immediately to `--checkpoint-file`. Re-running
`sync --apply` against the same checkpoint file is **idempotent**: operations whose desired
state hasn't changed are skipped, and only genuinely new/changed operations are (re)applied.
Independent operation failures don't stop the run — the command reports every failure and
exits non-zero if any occurred.

### `pvw fabric migration run --config <file>`

A config-file-driven equivalent of `sync`, intended for schedulers/pipelines where passing a
long option list isn't convenient. See
[`samples/json/fabric_migration/run_config.json`](../samples/json/fabric_migration/run_config.json)
for the full set of keys (they mirror `sync`'s option names).

```powershell
pvw fabric migration run --config .\run_config.json
```

### `pvw fabric migration rollback`

Reverses a completed run's item metadata, tag application, and workspace-domain assignment
changes — derived **purely from the checkpoint file**, never by re-running matching or
planning. This makes it safe to run long after the source Purview/Fabric state has moved on.

```powershell
# Preview (default) — shows what would be reverted, writes nothing.
pvw fabric migration rollback --checkpoint-file .\checkpoints\run1.json

# Actually restore.
pvw fabric migration rollback --checkpoint-file .\checkpoints\run1.json --apply
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

`pvw fabric migration run --config <file>` is the intended entry point for scheduled jobs
(cron, Azure DevOps/GitHub Actions pipelines, Fabric/ADF pipelines invoking a shell step,
etc.). Keep `--checkpoint-file` on durable storage shared across runs so repeated
invocations remain idempotent, and treat a non-zero exit code as a signal to alert/stop the
pipeline rather than silently retry (conflicts and validation errors require a human to
resolve the mapping file or adjust `--overwrite`/`--truncate-descriptions`).

## Command reference

| Command | Writes to Fabric? | Default | Key options |
|---|---|---|---|
| `pvw fabric migration assess` | Never | — | `--purview-domain-id`, `--workspace-id`, `--mapping-file`, `--overwrite`, `--truncate-descriptions`, `--report-file`, `--csv-report-file`, `--output` |
| `pvw fabric migration sync` | Only with `--apply` | Dry run | All of the above, plus `--checkpoint-file` (required), `--apply` |
| `pvw fabric migration run --config <file>` | Only if `"apply": true` in the config | Dry run | `--config` (JSON file with the same keys as `sync`) |
| `pvw fabric migration rollback` | Only with `--apply` | Preview | `--checkpoint-file` (required), `--apply`, `--report-file`, `--output` |
