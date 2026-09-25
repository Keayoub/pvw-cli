# SPDX-License-Identifier: Apache-2.0
"""Read-only Fabric GPS roadmap retrieval for data-governance topics."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import requests

GPS_RELEASES_URL = "https://www.fabric-gps.com/api/releases"
PRODUCTS = ("Administration, Governance and Security", "IQ")
TOPICS = (
    "ontology",
    "fabric graph",
    "onelake catalog",
    "governance",
    "govern skills",
    "sensitivity label",
    "data quality",
    "lineage",
    "data product",
    "domain",
    "tagging",
    "purview",
    "access policy",
    "metadata",
)


class RoadmapError(ValueError):
    """Fabric GPS could not provide a trustworthy roadmap response."""


def fetch_governance_roadmap(
    *, status: Optional[str] = None, session: Optional[requests.Session] = None
) -> dict[str, Any]:
    """Fetch all pages from relevant product categories, without changing sync state."""
    http = session or requests.Session()
    entries: list[dict[str, Any]] = []
    try:
        for product in PRODUCTS:
            page = 1
            while True:
                try:
                    response = http.get(
                        GPS_RELEASES_URL,
                        params={"product_name": product, "page_size": 100, "page": page},
                        timeout=15,
                    )
                    response.raise_for_status()
                    payload = response.json()
                except (requests.RequestException, ValueError) as exc:
                    raise RoadmapError(
                        f"Fabric GPS request failed for {product}, page {page}: {exc}"
                    ) from exc
                if not isinstance(payload, dict):
                    raise RoadmapError(
                        f"Invalid Fabric GPS response for {product}, page {page}: expected an object"
                    )
                rows = payload.get("data")
                pagination = payload.get("pagination")
                if not isinstance(rows, list) or not isinstance(pagination, dict):
                    raise RoadmapError(
                        f"Invalid Fabric GPS response for {product}, page {page}: missing data/pagination"
                    )
                for row in rows:
                    if not isinstance(row, dict) or not isinstance(row.get("feature_name"), str):
                        raise RoadmapError(f"Invalid Fabric GPS release for {product}, page {page}")
                    if row.get("product_name") != product or not isinstance(
                        row.get("release_status"), str
                    ):
                        raise RoadmapError(
                            f"Invalid Fabric GPS release fields for {product}, page {page}"
                        )
                    if not isinstance(row.get("last_modified"), str):
                        raise RoadmapError(
                            f"Invalid Fabric GPS last_modified for {product}, page {page}"
                        )
                    for field in ("release_date", "release_type", "blog_url"):
                        if row.get(field) is not None and not isinstance(row[field], str):
                            raise RoadmapError(
                                f"Invalid Fabric GPS {field} for {product}, page {page}"
                            )
                    if any(topic in row["feature_name"].lower() for topic in TOPICS):
                        if status is None or row["release_status"].lower() == status.lower():
                            entries.append(
                                {
                                    key: row.get(key)
                                    for key in (
                                        "release_item_id",
                                        "feature_name",
                                        "product_name",
                                        "release_status",
                                        "release_date",
                                        "release_type",
                                        "last_modified",
                                        "blog_url",
                                    )
                                }
                            )
                if (
                    type(pagination.get("page")) is not int
                    or pagination["page"] != page
                    or not isinstance(pagination.get("has_next"), bool)
                ):
                    raise RoadmapError(f"Invalid Fabric GPS pagination for {product}, page {page}")
                if not pagination["has_next"]:
                    break
                next_page = pagination.get("next_page")
                if (
                    not isinstance(next_page, int)
                    or isinstance(next_page, bool)
                    or next_page != page + 1
                ):
                    raise RoadmapError(f"Invalid Fabric GPS next page for {product}, page {page}")
                page = next_page
    finally:
        if session is None:
            http.close()
    entries.sort(key=lambda row: (row["last_modified"] or "", row["feature_name"]), reverse=True)
    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "source": GPS_RELEASES_URL,
        "note": "Roadmap announcements only; sync capability status requires API and tenant verification.",
        "items": entries,
    }
