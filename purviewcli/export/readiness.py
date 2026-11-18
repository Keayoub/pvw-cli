# SPDX-License-Identifier: Apache-2.0
"""Offline migration inventory for the portable Unified Catalog snapshot."""

from collections import Counter
from pathlib import Path
from typing import Optional

from purviewcli.export.decisions import (
    FABRIC_ITEM_TYPES,
    load_snapshot_with_digest,
    validate_snapshot_decisions,
)
from purviewcli.sync.purview_to_fabric import namespaced_tag_name

GOVERNANCE = (
    ("term", "terms.json", "term_ids"),
    ("data_product", "data_products.json", "data_product_ids"),
    ("cde", "cdes.json", "cde_ids"),
)
NOT_CAPTURED = (
    "lineage", "data_quality_rules_and_scores", "access_policies",
    "data_map_classifications", "data_map_labels", "sensitivity_labels",
    "custom_and_managed_attributes",
)


def build_readiness_report(snapshot_dir: Path, decisions_file: Optional[Path] = None) -> dict:
    """Inventory the whole snapshot; locally approved mappings are optional evidence."""
    documents, digest = load_snapshot_with_digest(snapshot_dir)
    mappings = {}
    if decisions_file is not None:
        _, mapping = validate_snapshot_decisions(documents, digest, decisions_file)
        mappings = mapping.by_purview_asset_id()

    domain_ids = {row["id"] for row in documents["domains.json"]}
    object_ids = {kind: {row["id"] for row in documents[file]} for kind, file, _ in GOVERNANCE}
    linked = {kind: Counter() for kind, _, _ in GOVERNANCE}
    incomplete_links = set()
    assets = []
    for row in sorted(documents["assets.json"], key=lambda record: record["id"]):
        asset_id = row["id"]
        binding = mappings.get(asset_id)
        source_type = row.get("type")
        name = row.get("name")
        candidate_basis = None
        if binding is not None:
            candidate_basis = "reviewed_mapping"
        elif (
            isinstance(name, str) and name.strip()
            and isinstance(source_type, str) and source_type in FABRIC_ITEM_TYPES
        ):
            candidate_basis = "source_type_hint"
        relationships = {}
        for kind, _, field in GOVERNANCE:
            ids = row.get(field)
            if field in row and (
                not isinstance(ids, list)
                or any(not isinstance(ref, str) or not ref for ref in ids)
            ):
                raise ValueError(f"Asset {asset_id}: invalid {field} in snapshot")
            observed = sorted(set(ids)) if ids is not None else None
            # Schema v1 normalizes absent CDE links to []; that is not evidence of absence.
            if kind == "cde" and not observed:
                observed = None
            if observed is None:
                incomplete_links.add(kind)
            unresolved = (
                sorted(set(observed) - object_ids[kind]) if observed is not None else None
            )
            linked[kind].update(ref for ref in observed or [] if ref in object_ids[kind])
            relationships[kind] = {"observedIds": observed, "unresolvedIds": unresolved}
        domain_id = row.get("domain_id")
        assets.append({
            "id": asset_id,
            "name": name,
            "sourceType": source_type,
            "domainId": domain_id,
            "domainReferenceResolved": (
                domain_id in domain_ids if isinstance(domain_id, str) and domain_id else None
            ),
            "outcome": "native_candidate" if candidate_basis else "unknown",
            "candidateBasis": candidate_basis,
            "reviewedMapping": (
                {
                    "workspaceId": binding.workspace_id,
                    "itemId": binding.item_id,
                    "expectedFabricType": binding.expected_fabric_type,
                    "targetVerified": False,
                }
                if binding else None
            ),
            "relationships": relationships,
        })

    domains = [
        {
            "id": row["id"], "name": row.get("name"),
            "parentId": row.get("parent_id"), "outcome": "retain_manual_redesign",
        }
        for row in sorted(documents["domains.json"], key=lambda record: record["id"])
    ]
    governance = {}
    for kind, file, _ in GOVERNANCE:
        records = []
        for row in sorted(documents[file], key=lambda record: record["id"]):
            name = row.get("name")
            count = linked[kind][row["id"]]
            named = isinstance(name, str) and bool(name.strip())
            tag = namespaced_tag_name(kind, name) if count and named else None
            if not named:
                outcome = "unknown"
            elif tag and tag != f"purview:{kind}:":
                outcome = "lossy_tag"
            else:
                outcome = "retain_manual_redesign"
                tag = None
            records.append({
                "id": row["id"], "name": name, "domainId": row.get("domainId"),
                "parentId": row.get("parentId"), "outcome": outcome, "candidateTag": tag,
                "observedLinkedAssetCount": count if count or kind not in incomplete_links else None,
            })
        governance[kind] = records

    inventory = {"assets": assets, "domains": domains, **governance}
    return {
        "schemaVersion": 1,
        "snapshotSha256": digest,
        "reviewedDecisionsIncluded": decisions_file is not None,
        "reviewedMappingCount": len(mappings) if decisions_file is not None else None,
        "summary": {
            kind: {
                "snapshotCount": len(records),
                "outcomes": dict(Counter(record["outcome"] for record in records)),
            }
            for kind, records in inventory.items()
        },
        "inventory": inventory,
        "notCaptured": {kind: {"outcome": "not_captured", "count": None} for kind in NOT_CAPTURED},
        "limitations": [
            "Counts describe the snapshot, not the tenant. Empty CDE link lists are unknown; "
            "the export does not independently enumerate those links.",
            "Native candidates refer to display name and description on existing Fabric items. "
            "This report does not verify targets or permissions. Use fabric sync assess to "
            "verify targets and check for sync conflicts.",
            "Tags are name-only, not native governance objects. Names may collide, and tags "
            "do not preserve definitions, hierarchies or governance semantics.",
            "Domains and workspace assignments are excluded from reviewed snapshot sync.",
        ],
    }
