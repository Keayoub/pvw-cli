---
name: Fabric sync capability re-check
about: Periodic re-check of blocked Purview -> Fabric sync capabilities against the Fabric/Purview roadmap and API surface
title: "Fabric sync capability re-check: <YYYY-MM>"
labels: fabric-sync, roadmap-recheck
assignees: ''
---

## Purpose

Periodically re-verify whether any capability currently marked "Planned / TBD" or "Not
supported" in
[`docs/purview-to-fabric-onelake-sync.md`](../../docs/purview-to-fabric-onelake-sync.md)
(source of truth: [`purviewcli/sync/capabilities.py`](../../purviewcli/sync/capabilities.py))
has become possible because Fabric or Purview shipped a new public API.

See the ["Re-check checklist"](../../docs/purview-to-fabric-onelake-sync.md#re-check-checklist)
in that doc for the specific items and links to check.

## Checklist

- [ ] Sensitivity label (MIP) per-asset read API — checked Purview REST API reference and
      Fabric roadmap (Governance filter)
- [ ] Fabric data-quality per-item API — checked Fabric roadmap and REST API reference
- [ ] Fabric lineage-ingestion API — checked Fabric roadmap and REST API reference
- [ ] Fabric native data-product object — checked Fabric roadmap and blog
- [ ] Fabric arbitrary custom/managed item properties — checked Fabric REST API reference
      (Items)
- [ ] Fabric attribute-based access policy API — checked Fabric roadmap (Governance filter)

## Outcome

<!-- For each item above that changed status, describe what was found and link the source. -->

- [ ] No changes found this cycle — update the "Last reviewed" date in
      `docs/purview-to-fabric-onelake-sync.md` and close.
- [ ] Changes found — live-verify against a real tenant, then update
      `purviewcli/sync/capabilities.py`, `docs/purview-to-fabric-onelake-sync.md`, and
      `docs/fabric-sync-feature-parity.md` before implementing the newly-unblocked sync.
