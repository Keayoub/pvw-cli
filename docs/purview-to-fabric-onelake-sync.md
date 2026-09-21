# Purview → Fabric OneLake Catalog: Sync Overview & Roadmap

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
| Sensitivity label (MIP) | Fabric `bulkSetLabels`/`bulkRemoveLabels` | 🔜 Planned / TBD | Fabric's write API exists and is documented; Purview has no confirmed **per-asset** read API for the applied label — only tenant-wide aggregate reports today. Re-check both APIs before starting. |
| Data quality rules / scores | *(no Fabric OneLake catalog field identified)* | 🔜 Planned / TBD | Watch Fabric's data-quality feature area on the roadmap for a documented per-item API. |
| Lineage | *(no confirmed mapping)* | 🔜 Planned / TBD | Fabric's lineage model differs structurally from Purview's Atlas process/relationship graph. Needs its own design once/if a compatible ingestion API ships. |
| Data Products as first-class Fabric objects | *(no Fabric object exists)* | ⛔ Not supported | Fabric has no native "data product" concept beyond tags today; re-evaluate if that changes. |
| RBAC → ABAC access policies | *(no confirmed Fabric equivalent)* | ⛔ Not supported | Purview's attribute-based access policies have no matching Fabric item/workspace policy API today. |
| Custom / managed attributes | *(no confirmed Fabric field)* | 🔜 Planned / TBD | Present in Purview UC domain responses (`managedAttributes`); no confirmed arbitrary-property field on Fabric items yet. |
| Full glossary hierarchy (parent/child terms, relationships) | *(no Fabric equivalent)* | ⛔ Not supported | Only the term's name is portable as a tag; Fabric has no structured term/hierarchy object. |

## How this table is kept current

This page reflects the same facts recorded in
[`fabric-sync-feature-parity.md`](fabric-sync-feature-parity.md), summarized for a quick
read. It should be revisited:

- Whenever Microsoft publishes updates to the
  [Fabric roadmap](https://roadmap.fabric.microsoft.com/) or OneLake catalog/governance
  "what's new" notes — look specifically for sensitivity-label read APIs, data quality
  APIs, lineage ingestion APIs, or a native data-product object.
- Whenever this project live-verifies a new Purview or Fabric API shape (see the
  "Verification status" section of the [Fabric Sync Guide](fabric-sync-guide.md) for the
  project's live-verify-first convention).

When a 🔜/⛔ row becomes possible:

1. Live-verify the exact request/response shape against a real tenant first — never assume
   a shape from documentation alone.
2. Flip the row here and in `fabric-sync-feature-parity.md` to ✅/🟡, recording what was
   verified and against what.
3. Extend `purviewcli/sync/models.py`, `service.py`, `purview_to_fabric.py`,
   `execution.py`, `fabric_client.py`, and `cli/fabric.py`, following the same additive,
   opt-in pattern used for `--sync-classifications`.

> **Note:** the specific "not yet possible" reasons above reflect this project's most
> recent live-tenant verification and public API research; they are not a live feed from
> Microsoft's roadmap site. Treat any 🔜 row as "worth re-checking," not as a committed
> Microsoft ship date.
