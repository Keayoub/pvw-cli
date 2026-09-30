# SPDX-License-Identifier: Apache-2.0
"""Validate an immutable Purview snapshot and explicit customer decisions."""

from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from purviewcli.sync.models import PurviewAsset, PurviewGovernanceObject, SyncMapping

FILES = ("assets.json", "domains.json", "terms.json", "data_products.json", "cdes.json")
FABRIC_ITEM_TYPES = {"Lakehouse", "SemanticModel", "Warehouse"}
SCHEMA_VERSION = 1


def _is_int(value: Any) -> bool:
    # bool subclasses int in Python, so JSON true would otherwise equal 1.
    return isinstance(value, int) and not isinstance(value, bool)


def _object(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def load_snapshot(snapshot_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Verify the immutable exported records before they can be used."""
    snapshot_dir = Path(snapshot_dir)
    manifest = _object(snapshot_dir / "manifest.json")
    if (
        not _is_int(manifest.get("schemaVersion"))
        or manifest["schemaVersion"] != SCHEMA_VERSION
        or not isinstance(manifest.get("sha256"), dict)
        or not isinstance(manifest.get("files"), dict)
    ):
        raise ValueError("Unsupported or unverified snapshot manifest")
    documents: Dict[str, List[Dict[str, Any]]] = {}
    for name in FILES:
        path = snapshot_dir / name
        content = path.read_bytes()
        if hashlib.sha256(content).hexdigest() != manifest["sha256"].get(name):
            raise ValueError(f"{name}: snapshot checksum mismatch")
        records = json.loads(content)
        if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
            raise ValueError(f"{name}: expected an array of objects")
        count = manifest["files"].get(name)
        if not _is_int(count) or count != len(records):
            raise ValueError(f"{name}: manifest count mismatch")
        identifiers = [record.get("id") for record in records]
        if any(not isinstance(identifier, str) or not identifier for identifier in identifiers):
            raise ValueError(f"{name}: missing Purview ID")
        if len(set(identifiers)) != len(identifiers):
            raise ValueError(f"{name}: duplicate Purview ID")
        documents[name] = records

    return documents


def load_reviewed_snapshot(
    snapshot_dir: Path, decisions_file: Path
) -> Tuple[Dict[str, List[Any]], SyncMapping]:
    """Return selected source records only after local integrity/reference checks."""
    snapshot_dir = Path(snapshot_dir)
    documents = load_snapshot(snapshot_dir)
    decisions = _object(Path(decisions_file))
    if set(decisions) not in (
        {
            "schemaVersion",
            "snapshotSha256",
            "selectedAssetIds",
            "descriptions",
            "mappings",
        },
        {
            "schemaVersion",
            "snapshotSha256",
            "selectedAssetIds",
            "descriptions",
            "mappings",
            "candidates",
        },
    ):
        raise ValueError(
            "Decisions must contain schemaVersion, snapshotSha256, selectedAssetIds, descriptions, mappings (and optionally candidates)"
        )
    digest = hashlib.sha256((snapshot_dir / "manifest.json").read_bytes()).hexdigest()
    if (
        not _is_int(decisions["schemaVersion"])
        or decisions["schemaVersion"] != SCHEMA_VERSION
        or decisions["snapshotSha256"] != digest
    ):
        raise ValueError("Decisions do not match this snapshot version and manifest")
    selected = decisions["selectedAssetIds"]
    if (
        not isinstance(selected, list)
        or not selected
        or any(not isinstance(value, str) or not value.strip() for value in selected)
    ):
        raise ValueError("selectedAssetIds must contain at least one Purview asset ID")
    if len(set(selected)) != len(selected):
        raise ValueError("selectedAssetIds contains duplicates")
    descriptions = decisions["descriptions"]
    if not isinstance(descriptions, dict) or any(
        not isinstance(key, str) or not isinstance(value, str)
        for key, value in descriptions.items()
    ):
        raise ValueError("descriptions must map asset IDs to strings")
    asset_ids = {row["id"] for row in documents["assets.json"]}
    if not set(selected) <= asset_ids or not set(descriptions) <= set(selected):
        raise ValueError("Selected or edited asset ID is absent from the snapshot")
    mappings = decisions["mappings"]
    if not isinstance(mappings, list) or any(not isinstance(entry, dict) for entry in mappings):
        raise ValueError("mappings must be an array of explicit bindings")
    for entry in mappings:
        for field in ("purviewAssetId", "workspaceId", "itemId"):
            value = entry.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Mapping {field} must be a nonempty string")
        fabric_type = entry.get("expectedFabricType")
        if not isinstance(fabric_type, str) or fabric_type not in FABRIC_ITEM_TYPES:
            raise ValueError(
                f"Mapping for {entry.get('purviewAssetId', '<unknown>')}: "
                f"expectedFabricType must be one of {', '.join(sorted(FABRIC_ITEM_TYPES))}"
            )
    if "candidates" in decisions and not isinstance(decisions["candidates"], list):
        raise ValueError("candidates must be an array of informational suggestions")
    try:
        mapping = SyncMapping.from_dict({"mappings": mappings})
    except (KeyError, TypeError) as exc:
        raise ValueError(
            "Invalid mapping: purviewAssetId, workspaceId and itemId required"
        ) from exc
    if set(mapping.by_purview_asset_id()) != set(selected):
        raise ValueError("Every selected asset must have exactly one explicit Fabric mapping")
    mapping_by_id = mapping.by_purview_asset_id()
    domains = {row["id"]: row for row in documents["domains.json"]}
    objects = {
        key: {row["id"]: row for row in documents[key]}
        for key in ("terms.json", "data_products.json", "cdes.json")
    }
    assets = []
    for record in documents["assets.json"]:
        if record["id"] not in selected:
            continue
        asset = PurviewAsset.from_dict(record)
        if not isinstance(asset.name, str) or not asset.name.strip():
            raise ValueError(f"Asset {asset.id}: name must be a nonempty string")
        if not isinstance(asset.type, str):
            raise ValueError(f"Asset {asset.id}: type must be a string")
        if asset.description is not None and not isinstance(asset.description, str):
            raise ValueError(f"Asset {asset.id}: description must be a string or null")
        if asset.domain_id is not None and not isinstance(asset.domain_id, str):
            raise ValueError(f"Asset {asset.id}: domain_id must be a string or null")
        if (
            asset.type in FABRIC_ITEM_TYPES
            and mapping_by_id[asset.id].expected_fabric_type != asset.type
        ):
            raise ValueError(
                f"Asset {asset.id}: approved Fabric type "
                f"{mapping_by_id[asset.id].expected_fabric_type} conflicts with Purview type {asset.type}"
            )
        if asset.domain_id and asset.domain_id not in domains:
            raise ValueError(f"Asset {asset.id}: unknown domain {asset.domain_id}")
        for field, file in (
            ("term_ids", "terms.json"),
            ("data_product_ids", "data_products.json"),
            ("cde_ids", "cdes.json"),
        ):
            refs = getattr(asset, field)
            if not isinstance(refs, list) or any(
                not isinstance(ref, str) or ref not in objects[file] for ref in refs
            ):
                raise ValueError(f"Asset {asset.id}: unresolved {field}")
        # Explicit mapping always wins in reviewed mode; never use embedded hints.
        assets.append(
            dataclasses.replace(
                asset,
                description=descriptions.get(asset.id, asset.description),
                source={},
                type_properties={},
            )
        )
    governance_objects = [
        PurviewGovernanceObject(
            id=row["id"], name=row.get("name", ""), domain_id=row.get("domainId"), object_type=kind
        )
        for name, kind in (
            ("terms.json", "term"),
            ("data_products.json", "data_product"),
            ("cdes.json", "cde"),
        )
        for row in documents[name]
    ]
    for obj in governance_objects:
        if not isinstance(obj.name, str) or not obj.name:
            raise ValueError(f"{obj.object_type} {obj.id}: missing name")
        if obj.domain_id and obj.domain_id not in domains:
            raise ValueError(f"{obj.object_type} {obj.id}: unknown domain {obj.domain_id}")
    return {
        "assets": assets,
        # Domain assignment is intentionally excluded from the reviewed import path.
        "domains": [],
        "governance_objects": governance_objects,
    }, mapping
