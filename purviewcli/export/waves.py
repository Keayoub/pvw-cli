# SPDX-License-Identifier: Apache-2.0
"""Plan explicit migration waves without authenticating to either tenant."""

import hashlib
import json
from pathlib import Path
from typing import AbstractSet, Any, Optional

from purviewcli.export.decisions import load_snapshot_with_digest, validate_decisions

WAVE_SCHEMA_VERSION = 1


def _read_object(path: Path) -> tuple[dict[str, Any], str]:
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{path}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    content = path.read_bytes()
    try:
        value = json.loads(content.decode("utf-8"), object_pairs_hook=unique_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value, hashlib.sha256(content).hexdigest()


def _validate_waves(
    manifest: dict[str, Any],
    snapshot_digest: str,
    decisions_digest: str,
    asset_ids: AbstractSet[str],
    reviewed_ids: AbstractSet[str],
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    if (
        set(manifest) != {"schemaVersion", "snapshotSha256", "decisionsSha256", "waves"}
        or type(manifest["schemaVersion"]) is not int
        or manifest["schemaVersion"] != WAVE_SCHEMA_VERSION
    ):
        raise ValueError("Expected a version 1 wave manifest with snapshotSha256, decisionsSha256 and waves")
    if manifest["snapshotSha256"] != snapshot_digest:
        raise ValueError("Wave manifest does not match this snapshot (snapshotSha256)")
    if manifest["decisionsSha256"] != decisions_digest:
        raise ValueError("Wave manifest does not match these reviewed decisions (decisionsSha256)")
    waves = manifest["waves"]
    if not isinstance(waves, list) or not waves:
        raise ValueError("waves must be a nonempty array in migration order")

    wave_names = set()
    assignments = {}
    for wave in waves:
        if not isinstance(wave, dict) or set(wave) != {"name", "assetIds"}:
            raise ValueError("Each wave must contain name and assetIds")
        name, ids = wave["name"], wave["assetIds"]
        if not isinstance(name, str) or not name or name != name.strip():
            raise ValueError("Wave name must be a nonempty string without surrounding whitespace")
        if name in wave_names:
            raise ValueError(f"Duplicate wave name {name!r}")
        wave_names.add(name)
        if not isinstance(ids, list) or not ids or any(
            not isinstance(asset_id, str) or not asset_id.strip() for asset_id in ids
        ):
            raise ValueError(f"Wave {name!r}: assetIds must contain at least one Purview asset ID")
        for asset_id in ids:
            if asset_id not in asset_ids:
                raise ValueError(f"Wave {name!r}: asset ID {asset_id!r} is absent from the snapshot")
            if asset_id not in reviewed_ids:
                raise ValueError(f"Wave {name!r}: asset ID {asset_id!r} has no reviewed mapping")
            if asset_id in assignments:
                raise ValueError(
                    f"Duplicate assignment for asset ID {asset_id!r}: "
                    f"already assigned to wave {assignments[asset_id]!r}, repeated in {name!r}"
                )
            assignments[asset_id] = name
    return waves, assignments


def plan_waves(
    snapshot_dir: Path,
    decisions_file: Path,
    wave_file: Optional[Path] = None,
    wave_name: Optional[str] = None,
    output_file: Optional[Path] = None,
) -> dict[str, Any]:
    """Report reviewed wave assignments and optionally export one wave's decisions."""
    if (wave_name is None) != (output_file is None) or (wave_name is not None and wave_file is None):
        raise ValueError("--wave and --output-file must be used together with --wave-file")

    documents, snapshot_digest = load_snapshot_with_digest(snapshot_dir)
    decisions, decisions_digest = _read_object(decisions_file)
    _, mapping = validate_decisions(documents, snapshot_digest, decisions)
    reviewed = mapping.by_purview_asset_id()
    assets = {asset["id"]: asset for asset in documents["assets.json"]}
    waves, assignments = [], {}
    if wave_file is not None:
        manifest, _ = _read_object(wave_file)
        waves, assignments = _validate_waves(
            manifest, snapshot_digest, decisions_digest, assets.keys(), reviewed.keys()
        )

    unassigned = [
        {
            "id": asset_id,
            "sourceType": asset.get("type"),
            "disposition": "reviewed_not_scheduled" if asset_id in reviewed else "not_reviewed",
        }
        for asset_id, asset in assets.items()
        if asset_id not in assignments
    ]
    report = {
        "schemaVersion": WAVE_SCHEMA_VERSION,
        "snapshotSha256": snapshot_digest,
        "decisionsSha256": decisions_digest,
        "snapshotAssetCount": len(assets),
        "reviewedAssetCount": len(reviewed),
        "assignedAssetCount": len(assignments),
        "unassignedAssetCount": len(unassigned),
        "waves": waves,
        "unassignedAssets": unassigned,
        "exportedWave": wave_name,
        "targetsVerified": False,
    }

    if output_file is not None:
        wave = next((wave for wave in waves if wave["name"] == wave_name), None)
        if wave is None:
            raise ValueError(f"Unknown wave {wave_name!r}")
        if output_file.parent.resolve().is_relative_to(snapshot_dir.resolve()):
            raise ValueError("Wave decisions must be written outside the snapshot directory")
        ids = wave["assetIds"]
        bindings = {binding["purviewAssetId"]: binding for binding in decisions["mappings"]}
        descriptions = decisions["descriptions"]
        scoped = {
            "schemaVersion": decisions["schemaVersion"],
            "snapshotSha256": snapshot_digest,
            "selectedAssetIds": ids,
            "descriptions": {asset_id: descriptions[asset_id] for asset_id in ids if asset_id in descriptions},
            "mappings": [bindings[asset_id] for asset_id in ids],
        }
        validate_decisions(documents, snapshot_digest, scoped)
        content = json.dumps(scoped, indent=2) + "\n"
        try:
            with output_file.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError as exc:
            raise ValueError(f"Wave decisions destination already exists: {output_file}") from exc

    return report
