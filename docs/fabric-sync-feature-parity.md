# Purview → Fabric Sync: Feature Parity Map

> Tracks what `pvw fabric sync` implements today versus governance capabilities that
> are not yet portable because Fabric (or Purview) doesn't yet expose a confirmed,
> documented API for them. Revisit the "Not yet implemented" rows whenever Fabric/Purview
> ship a new public API — each row lists exactly what to re-verify first.
>
> See [Purview to Fabric OneLake Sync Overview](purview-to-fabric-onelake-sync.md) for a
> condensed, roadmap-aware summary of this same information.

## Implemented today (live-verified)

| Purview capability | Fabric target | Command flag | Verified against |
|---|---|---|---|
| Data asset display name / description | Fabric item `displayName`/`description` | *(always on)* | Live tenant `GET/PATCH .../items/{id}` |
| Governance domain | Fabric domain + workspace assignment | *(always on)* | Live tenant `GET/POST /v1/admin/domains` |
| Glossary term / data product / critical data element name | Namespaced Fabric tag `purview:<type>:<name>` | *(always on)* | Live tenant `GET/POST /v1/tags`, `applyTags`/`unapplyTags` |
| Data Map entity classifications (e.g. `MICROSOFT.PERSONAL.EMAIL`) | Namespaced Fabric tag `purview:classification:<name>` | `--sync-classifications` | Live tenant `entityReadUniqueAttribute` (classic Atlas API) |
| Data Map entity labels (free-text) | Namespaced Fabric tag `purview:label:<name>` | `--sync-classifications` | Live tenant `entityReadUniqueAttribute` |

All of the above are additive-only (existing Fabric tags/values are never removed by a sync)
and one-way (Purview → Fabric; nothing is ever written back to Purview).

## Not yet implemented (tracked for later)

| Capability | Why it's blocked | What to re-verify before implementing |
|---|---|---|
| Sensitivity label (MIP) sync | **Fabric side is ready** (verified 2026-09-22 against `microsoft/fabric-rest-api-specs`): Get/List/Create Item responses include `sensitivityLabel.id`, Create accepts `sensitivityLabelSettings.{labelId, sensitivityLabelApplyStrategy}`, and `POST /admin/items/bulkSetLabels`/`bulkRemoveLabels` exist. The remaining blocker is the **Purview read side** — no confirmed per-asset API returns a data asset's applied MIP label ID; only tenant-wide aggregate reporting endpoints (`sensitivityLabel/labelSummary`, `labelInsights`) exist in this codebase today, and the live UC Data Asset read returned no sensitivity field. | Confirm whether a per-asset Purview API (Data Map entity attribute, UC data asset field, or a new endpoint) surfaces the asset's actual MIP label ID. If found, add a `sensitivity_label_id` field to `PurviewAsset`/`FabricItemState`, a new `SET_SENSITIVITY_LABEL` operation type, and `fabric_client` set/remove label methods. |
| Data quality / observability metadata | No portable Fabric OneLake catalog equivalent identified yet. | Check whether Fabric's data-quality features (if/when generally available) expose a documented API for attaching quality scores/rules to catalog items. |
| Lineage | Fabric's OneLake catalog lineage model differs structurally from Purview's Atlas-based lineage graph; no confirmed mapping exists. | Check whether Fabric exposes a lineage-ingestion API compatible with Purview's process/relationship entities. |
| Data Products as first-class Fabric objects (beyond name-as-tag) | Fabric has no first-class "data product" object today; only the term/data-product/CDE *name* is portable as a tag. | Re-check if Fabric introduces a native data-product concept with its own API. |
| RBAC → ABAC policy migration | Purview's attribute-based access policies have no confirmed Fabric equivalent/API. | Check Fabric's item-level or workspace-level access-policy APIs once (if) they support attribute-based rules. |
| Custom attributes / managed attributes | Present in Purview UC domain responses (`managedAttributes`) but no confirmed Fabric item field to receive them. | Check whether Fabric items support arbitrary custom properties beyond tags/sensitivity labels. |
| Full glossary hierarchy (parent/child terms, relationships) | Only the term's *name* survives as a tag today; hierarchy/relationships have no Fabric equivalent. | Re-check if Fabric's OneLake catalog adds a structured glossary/term-hierarchy object, or see the Fabric Ontology row below. |
| Structured governance model (typed entity properties, relationships) via **Fabric Ontology** | **Live-verified 2026-09-23** against `microsoft/fabric-rest-api-specs`: Ontology has a public REST spec (`/workspaces/{id}/ontologies` -- GET/POST/PATCH/DELETE, `getDefinition`/`updateDefinition`) with a typed `EntityType` model (`name`, `namespace`, typed `properties`, `timeseriesProperties`) defined via base64-encoded definition parts, the same "item + definition parts" pattern as Notebooks/Reports. Fabric's `DataAgent` API already lists `"Ontology"` as a supported `FabricItemDatasource.fabricItemType`, so an Ontology-backed sync could feed Fabric's Data Agent/Copilot Studio/Agent 365 natural-language surfaces directly. Not yet adopted here: per Fabric GPS (`product_name=IQ`), "Public API for Ontology", entity-type relationships, "Full Ontology canvas experience", and "Ontology Versioning" are all still Planned (Q3-Q4 2026 as of this review), so the object model isn't finalized, and no `RelationshipType`-equivalent was found in the spec (`gh api "search/code?q=Relationship+repo:microsoft/fabric-rest-api-specs"` returned 0 hits). | Re-check `ontology/swagger.json` and `ontology/definitions.json` in `microsoft/fabric-rest-api-specs` for relationship/versioning support, and Fabric GPS `product_name=IQ` for the "Public API for Ontology" status. If both have shipped, design a `PurviewGovernanceObject` -> Ontology `EntityType` mapping (likely replacing the term/data-product/CDE tag rows above with structured entities) rather than extending the tag-based approach further. |

## How to extend this map

When a new Fabric or Purview API makes one of the "not yet implemented" rows possible:

1. Live-verify the exact request/response shape against a real tenant first (this project's
   convention — see the "Verification status" section of
   [`fabric-sync-guide.md`](fabric-sync-guide.md)).
2. Move the row from "Not yet implemented" to "Implemented today" here, recording what was
   verified and against what.
3. Extend `purviewcli/sync/models.py`, `service.py`, `purview_to_fabric.py`,
   `execution.py`, `fabric_client.py`, and `cli/fabric.py` following the same additive,
   opt-in pattern used for `--sync-classifications`.
