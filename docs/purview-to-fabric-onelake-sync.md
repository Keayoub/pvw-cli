# Purview → Fabric OneLake Catalog: Sync Overview & Roadmap

> **Last reviewed: 2026-09-22**, against a live Purview tenant (`kaydemopurview`, test data
> only), the [`microsoft/fabric-rest-api-specs`](https://github.com/microsoft/fabric-rest-api-specs)
> OpenAPI specs, and the [Fabric GPS roadmap API](https://www.fabric-gps.com/endpoints). See
> ["Re-check checklist"](#re-check-checklist) below for what to re-verify and when.

> Microsoft Purview's standalone data governance experience is being retired in favor of
> governance capabilities built directly into Microsoft Fabric (OneLake catalog, Fabric
> domains/tags, Fabric admin APIs). This page is the single at-a-glance status board for
> **what `pvw-cli` can already sync from Purview Unified Catalog (UC) into Fabric today**,
> what's blocked and why, and what to watch on the Fabric roadmap.
>
> For hands-on usage see the [Fabric Sync Guide](fabric-sync-guide.md) (commands, options,
> permissions, scheduling). For the exhaustive implementation-level detail behind each row
> below, see the [Fabric Sync Feature Parity Map](fabric-sync-feature-parity.md). This page
> is the summary; those two are the source of truth.

## Get the live version from the CLI

The table below is a snapshot. The CLI renders the same data live, straight from
[`purviewcli/sync/capabilities.py`](../purviewcli/sync/capabilities.py) — the single source
of truth both this page and the CLI draw from — so it can never silently drift from what's
actually implemented:

```bash
pvw fabric sync capabilities                       # table
pvw fabric sync capabilities --output json         # machine-readable
pvw fabric sync capabilities --status planned       # only "planned/TBD" rows
```

## Status legend

| Status | Meaning |
|---|---|
| ✅ **Supported** | Live-verified against a real tenant; ships in `pvw fabric sync` today. |
| 🟡 **Partial** | Some of the concept is portable (e.g. just a name-as-tag); the rest has no Fabric equivalent yet. |
| 🔜 **Planned / TBD** | Believed technically possible once a specific, currently-missing API exists; not started. Re-check the Fabric roadmap before starting. |
| ⛔ **Not supported** | No known path today — blocked on a Fabric or Purview product decision, not just an API gap. |

## Sync status by capability

| Purview UC capability | Fabric target | Status | Notes |
|---|---|---|---|
| Data asset display name / description | Item `displayName` / `description` | ✅ Supported | Always on; additive-only, dry-run by default. |
| Governance domain | Fabric domain + workspace assignment | ✅ Supported | Matched/created by name; always on. |
| Glossary term name | Namespaced Fabric tag `purview:glossary:<name>` | 🟡 Partial | Only the name is portable — no hierarchy, definitions, or relationships. |
| Data product name | Namespaced Fabric tag `purview:dataproduct:<name>` | 🟡 Partial | Name only; Fabric has no first-class "data product" object yet. |
| Critical Data Element (CDE) name | Namespaced Fabric tag `purview:cde:<name>` | 🟡 Partial | Name only. |
| Data Map classifications (e.g. `MICROSOFT.PERSONAL.EMAIL`) | Namespaced Fabric tag `purview:classification:<name>` | ✅ Supported | Opt-in via `--sync-classifications`; requires a resolvable Data Map link + known type mapping. |
| Data Map labels (free-text) | Namespaced Fabric tag `purview:label:<name>` | ✅ Supported | Opt-in via `--sync-classifications`; same source/limitations as classifications. |
| Sensitivity label (MIP) | Item `sensitivityLabel.id` + admin `bulkSetLabels`/`bulkRemoveLabels` | 🔜 Planned / TBD | **Fabric side is ready** (verified 2026-09-22): Get/List/Create Item return `sensitivityLabel.id`, Create accepts `sensitivityLabelSettings.labelId`, and admin bulk set/remove label APIs exist. Still blocked on the **Purview read side** — no confirmed per-asset API returns an asset's applied MIP label ID (only tenant-wide aggregate reports). |
| Data quality rules / scores | *(no Fabric OneLake catalog field identified)* | 🔜 Planned / TBD | Watch Fabric's data-quality feature area on the roadmap for a documented per-item API. |
| Lineage | *(no confirmed mapping)* | 🔜 Planned / TBD | Fabric's lineage model differs structurally from Purview's Atlas process/relationship graph. Needs its own design once/if a compatible ingestion API ships. |
| Data Products as first-class Fabric objects | *(no Fabric object exists)* | ⛔ Not supported | Fabric has no native "data product" concept beyond tags today; re-evaluate if that changes. |
| RBAC → ABAC access policies | *(no confirmed Fabric equivalent)* | ⛔ Not supported | Purview's attribute-based access policies have no matching Fabric item/workspace policy API today. |
| Custom / managed attributes | *(no confirmed Fabric field)* | 🔜 Planned / TBD | Present in Purview UC domain responses (`managedAttributes`); no confirmed arbitrary-property field on Fabric items yet. |
| Full glossary hierarchy (parent/child terms, relationships) | *(no Fabric equivalent)* | ⛔ Not supported | Only the term's name is portable as a tag; Fabric has no structured term/hierarchy object. |

## Re-check checklist

Run through this list periodically (e.g. quarterly, or whenever Microsoft announces a
Fabric governance update) to see if any 🔜/⛔ row can move to ✅/🟡. Each item links directly
to where the answer would show up — no need to rediscover these sources from scratch:

| # | Re-check this | Where to look | Unblocks |
|---|---|---|---|
| 1 | Does **Purview** expose a per-asset sensitivity-label read API yet (Data Map entity attribute, UC data asset field, or a new endpoint)? *(Fabric's side is already confirmed ready as of 2026-09-22 — this is the only remaining blocker.)* | [Purview REST API reference](https://learn.microsoft.com/en-us/rest/api/purview/), [Fabric GPS roadmap API](https://www.fabric-gps.com/api/releases?q=sensitivity+label) | Sensitivity label (MIP) sync |
| 2 | Has Fabric shipped a documented **data-quality** API for attaching scores/rules to *catalog items*? (As of 2026-09-22 only transformation-level checks exist: shortcut-transformation corrupt rows, MLV column checks — neither is catalog metadata.) | [Fabric GPS roadmap API](https://www.fabric-gps.com/api/releases?q=data+quality), [Fabric REST API reference](https://learn.microsoft.com/en-us/rest/api/fabric/) | Data quality rules / scores sync |
| 3 | Has Fabric shipped a **lineage-ingestion** API compatible with Purview's process/relationship entities? | [Fabric GPS roadmap API](https://www.fabric-gps.com/api/releases?q=lineage), [Fabric REST API reference](https://learn.microsoft.com/en-us/rest/api/fabric/) | Lineage sync |
| 4 | Has Fabric introduced a **native data-product** object (beyond tags)? | [Fabric GPS roadmap API](https://www.fabric-gps.com/api/releases?product_name=Administration%2C+Governance+and+Security), [Microsoft Fabric blog](https://blog.fabric.microsoft.com/) | Data Products as first-class Fabric objects |
| 5 | Does Fabric support **arbitrary custom/managed properties** on items (beyond tags/sensitivity labels)? | [`fabric-rest-api-specs` — platform definitions](https://github.com/microsoft/fabric-rest-api-specs/tree/main/platform/definitions), [Fabric REST API reference — Items](https://learn.microsoft.com/en-us/rest/api/fabric/core/items) | Custom / managed attributes sync |
| 6 | Has Fabric added an **attribute-based access policy** API at the item/workspace level? (As of 2026-09-22, "Outbound Access Protection" items are network-egress controls, not ABAC.) | [Fabric GPS roadmap API](https://www.fabric-gps.com/api/releases?product_name=Administration%2C+Governance+and+Security) | RBAC → ABAC policy sync |

### Useful sources for re-checking

- **[`microsoft/fabric-rest-api-specs`](https://github.com/microsoft/fabric-rest-api-specs)** — the authoritative OpenAPI specs. Best signal for "does this API actually exist?", and fetchable without a browser (raw JSON). Example: `gh api "search/code?q=sensitivityLabel+repo:microsoft/fabric-rest-api-specs"`.
- **[Fabric GPS roadmap API](https://www.fabric-gps.com/endpoints)** — a queryable JSON/RSS mirror of the Fabric roadmap (`/api/releases?q=...&product_name=...&release_status=...`). Useful because roadmap.fabric.microsoft.com itself is a JS-rendered SPA that can't be read without a browser.
- **[Fabric roadmap](https://roadmap.fabric.microsoft.com/)** — the official source (requires a browser to read).

## How this table is kept current

This page reflects the same facts recorded in
[`fabric-sync-feature-parity.md`](fabric-sync-feature-parity.md) and in
[`purviewcli/sync/capabilities.py`](../purviewcli/sync/capabilities.py) (the CLI's source
of truth), summarized for a quick read. It should be revisited:

- Whenever the ["Re-check checklist"](#re-check-checklist) above turns up a new API.
- Whenever this project live-verifies a new Purview or Fabric API shape (see the
  "Verification status" section of the [Fabric Sync Guide](fabric-sync-guide.md) for the
  project's live-verify-first convention).

When a 🔜/⛔ row becomes possible:

1. Live-verify the exact request/response shape against a real tenant first — never assume
   a shape from documentation alone.
2. Update the row in `purviewcli/sync/capabilities.py` first (the CLI's source of truth),
   then mirror the change here and in `fabric-sync-feature-parity.md`, recording what was
   verified and against what. Update the "Last reviewed" date at the top of this page.
3. Extend `purviewcli/sync/models.py`, `service.py`, `purview_to_fabric.py`,
   `execution.py`, `fabric_client.py`, and `cli/fabric.py`, following the same additive,
   opt-in pattern used for `--sync-classifications`.

> **Note:** the specific "not yet possible" reasons above reflect this project's most
> recent live-tenant verification and public API research; they are not a live feed from
> Microsoft's roadmap site. Treat any 🔜 row as "worth re-checking," not as a committed
> Microsoft ship date.
