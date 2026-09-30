# SPDX-License-Identifier: Apache-2.0
"""Portable Unified Catalog snapshot, independent of Fabric."""

from __future__ import annotations

import json
import hashlib
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from purviewcli.sync.service import normalize_purview_assets, normalize_purview_domains

ASSET_PAGE_SIZE = 100


def _rows(response: Any, name: str, *, paged: bool = False) -> List[Dict[str, Any]]:
    if isinstance(response, dict):
        rows = response.get("value")
        if response.get("nextLink") or response.get("continuationToken"):
            raise ValueError(
                f"{name}: continuation is not supported by this endpoint; export aborted"
            )
        count = response.get("totalCount")
        if count is not None and (
            isinstance(count, bool) or not isinstance(count, int) or count < 0
        ):
            raise ValueError(f"{name}: invalid totalCount; export aborted")
    elif isinstance(response, list):
        rows = response
    else:
        raise ValueError(f"{name}: expected a list or a 'value' response")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f"{name}: expected a list of objects")
    if isinstance(response, dict) and not paged and count is not None and count != len(rows):
        raise ValueError(f"{name}: response is incomplete (totalCount mismatch); export aborted")
    return rows


def _assets(client: Any) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    seen: set[str] = set()
    skip = 0
    expected_count = None
    while True:
        response = client.list_data_assets({"--skip": skip, "--top": ASSET_PAGE_SIZE})
        page = _rows(response, "assets", paged=True)
        if isinstance(response, dict) and response.get("totalCount") is not None:
            count = response["totalCount"]
            if expected_count is not None and count != expected_count:
                raise ValueError("assets: totalCount changed between pages; export aborted")
            expected_count = count
        for row in page:
            asset_id = row.get("id")
            if not isinstance(asset_id, str) or not asset_id:
                raise ValueError("assets: an asset is missing its Purview ID")
            if asset_id in seen:
                raise ValueError(
                    "assets: duplicate ID across pages; pagination may not be advancing"
                )
            seen.add(asset_id)
        result.extend(page)
        skip += len(page)
        if expected_count is not None and skip > expected_count:
            raise ValueError("assets: response exceeds totalCount; export aborted")
        if len(page) < ASSET_PAGE_SIZE:
            if expected_count is not None and skip != expected_count:
                raise ValueError("assets: response ended before totalCount; export aborted")
            break
    return result


def _business_objects(client: Any, method: str, name: str) -> List[Dict[str, Any]]:
    records = _rows(getattr(client, method)({}), name)
    result = []
    for record in records:
        if not isinstance(record.get("id"), str) or not record["id"]:
            raise ValueError(f"{name}: object is missing its Purview ID")
        result.append(
            {
                key: record.get(key)
                for key in ("id", "name", "description", "domainId", "parentId", "status")
                if key in record
            }
        )
    return result


def export_catalog(client: Any, output_dir: Path) -> Dict[str, Any]:
    """Read Purview first, then publish a complete snapshot as a new directory."""
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"Export destination already exists: {output_dir}")
    domains = _rows(client.get_governance_domains({}), "domains")
    if any(not isinstance(domain.get("id"), str) or not domain["id"] for domain in domains):
        raise ValueError("domains: a domain is missing its Purview ID")
    assets = _assets(client)
    terms = _business_objects(client, "get_terms", "terms")
    products = _business_objects(client, "get_data_products", "data_products")
    cdes = _business_objects(client, "get_critical_data_elements", "cdes")
    documents = {
        "domains.json": [d.to_dict() for d in normalize_purview_domains(domains)],
        "assets.json": [a.to_dict() for a in normalize_purview_assets(assets)],
        "terms.json": terms,
        "data_products.json": products,
        "cdes.json": cdes,
    }
    manifest = {
        "schemaVersion": 1,
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "source": "Purview Unified Catalog",
        "lineageIncluded": False,
        "files": {name: len(records) for name, records in documents.items()},
    }
    parent = output_dir.absolute().parent
    parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".purview-export-", dir=parent) as temporary:
        folder = Path(temporary)
        for name, records in documents.items():
            content = json.dumps(records, indent=2, ensure_ascii=False) + "\n"
            (folder / name).write_text(content, encoding="utf-8")
            manifest.setdefault("sha256", {})[name] = hashlib.sha256(
                (folder / name).read_bytes()
            ).hexdigest()
        (folder / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        digest = hashlib.sha256((folder / "manifest.json").read_bytes()).hexdigest()
        (folder / "decisions.example.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "snapshotSha256": digest,
                    "selectedAssetIds": [],
                    "descriptions": {},
                    "mappings": [],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        os.rename(folder, output_dir)
    return manifest
