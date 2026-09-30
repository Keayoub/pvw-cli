# SPDX-License-Identifier: Apache-2.0
"""Generate reviewable, non-authorizing Fabric mapping suggestions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence

from purviewcli.export.decisions import FABRIC_ITEM_TYPES, load_snapshot
from purviewcli.sync.models import FabricCatalogEntry


def prepare_decisions(
    snapshot_dir: Path,
    entries: Sequence[FabricCatalogEntry],
    output_file: Path,
) -> Dict[str, Any]:
    """Generate a draft; suggestions never populate selections or mappings."""
    snapshot_dir = Path(snapshot_dir)
    output_file = Path(output_file)
    if output_file.exists() or output_file.resolve().is_relative_to(snapshot_dir.resolve()):
        raise ValueError("Draft destination must be new and outside the snapshot directory")
    records = load_snapshot(snapshot_dir)["assets.json"]
    candidates: List[Dict[str, Any]] = []
    for asset in records:
        matches = [
            {
                "workspaceId": entry.workspace_id,
                "workspaceName": entry.workspace_display_name,
                "itemId": entry.id,
                "fabricType": entry.type,
                "reason": "exact_name_match_only; verify asset type and identity manually",
                "proposedMapping": {
                    "purviewAssetId": asset["id"],
                    "workspaceId": entry.workspace_id,
                    "itemId": entry.id,
                    "expectedFabricType": entry.type,
                },
            }
            for entry in entries
            if entry.type in FABRIC_ITEM_TYPES
            and entry.workspace_id
            and entry.id
            and isinstance(asset.get("name"), str)
            and asset["name"].strip()
            and asset["name"].strip().casefold() == entry.display_name.strip().casefold()
        ]
        candidates.append(
            {
                "purviewAssetId": asset["id"],
                "purviewName": asset.get("name"),
                "purviewType": asset.get("type"),
                "reviewStatus": (
                    "no_candidate"
                    if not matches
                    else "single_candidate" if len(matches) == 1 else "multiple_candidates"
                ),
                "suggestions": matches,
            }
        )
    draft = {
        "schemaVersion": 1,
        "snapshotSha256": hashlib.sha256((snapshot_dir / "manifest.json").read_bytes()).hexdigest(),
        "selectedAssetIds": [],
        "descriptions": {},
        "mappings": [],
        "candidates": candidates,
    }
    output_file.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation avoids replacing a customer's previous decisions file.
    with output_file.open("x", encoding="utf-8") as handle:
        json.dump(draft, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return draft
