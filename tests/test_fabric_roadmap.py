# SPDX-License-Identifier: Apache-2.0
"""Read-only Fabric GPS roadmap retrieval and CLI rendering."""

import json

import pytest
import requests
from click.testing import CliRunner

from purviewcli.cli.fabric import fabric
from purviewcli.sync.roadmap import PRODUCTS, RoadmapError, fetch_governance_roadmap


class FakeResponse:
    def __init__(self, payload, error=None):
        self.payload = payload
        self.error = error

    def raise_for_status(self):
        if self.error:
            raise requests.HTTPError(self.error)

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def get(self, url, *, params, timeout):
        self.calls.append((url, params, timeout))
        return next(self.responses)


def page(product, number, rows, next_page=None):
    return FakeResponse(
        {
            "data": [
                {
                    "product_name": product,
                    "release_status": "Planned",
                    "last_modified": "2026-09-25",
                    **row,
                }
                for row in rows
            ],
            "pagination": {
                "page": number,
                "has_next": next_page is not None,
                "next_page": next_page,
            },
        }
    )


def test_fetch_all_pages_filters_governance_and_preserves_roadmap_status():
    session = FakeSession(
        [
            page(
                PRODUCTS[0],
                1,
                [
                    {"feature_name": "OneLake catalog search", "last_modified": "2026-09-25"},
                    {"feature_name": "SQL performance", "last_modified": "2026-09-25"},
                ],
                2,
            ),
            page(
                PRODUCTS[0],
                2,
                [{"feature_name": "Sensitivity labels API", "last_modified": "2026-09-23"}],
            ),
            page(
                PRODUCTS[1],
                1,
                [{"feature_name": "Ontology Versioning", "last_modified": "2026-09-24"}],
            ),
        ]
    )
    result = fetch_governance_roadmap(session=session)
    assert [row["feature_name"] for row in result["items"]] == [
        "OneLake catalog search",
        "Ontology Versioning",
        "Sensitivity labels API",
    ]
    assert all(row["release_status"] == "Planned" for row in result["items"])
    assert [call[1]["page"] for call in session.calls] == [1, 2, 1]
    assert all(call[2] == 15 for call in session.calls)


def test_status_filter_and_empty_result():
    session = FakeSession(
        [
            page(PRODUCTS[0], 1, [{"feature_name": "OneLake catalog"}]),
            page(PRODUCTS[1], 1, [{"feature_name": "Ontology"}]),
        ]
    )
    assert fetch_governance_roadmap(status="shipped", session=session)["items"] == []


@pytest.mark.parametrize(
    "response",
    [
        FakeResponse({"data": [], "pagination": {"page": 1, "has_next": True, "next_page": 1}}),
        FakeResponse({"data": {}, "pagination": {}}),
        FakeResponse(
            {"data": [{"feature_name": "Ontology"}], "pagination": {"page": 1, "has_next": False}}
        ),
        FakeResponse({}, error="503 Service Unavailable"),
    ],
)
def test_invalid_gps_response_is_an_error(response):
    with pytest.raises(RoadmapError):
        fetch_governance_roadmap(session=FakeSession([response]))


def test_cli_json_is_clean_and_never_creates_purview_clients(monkeypatch):
    def fake_fetch(*, status=None):
        assert status == "planned"
        return {"checked_at": "2026-09-25", "source": "GPS", "note": "Roadmap only", "items": []}

    monkeypatch.setattr("purviewcli.sync.roadmap.fetch_governance_roadmap", fake_fetch)
    monkeypatch.setattr(
        "purviewcli.cli.fabric._get_clients", lambda ctx: pytest.fail("created client")
    )
    result = CliRunner().invoke(
        fabric, ["sync", "roadmap", "--status", "planned", "--output", "json"]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.output)["items"] == []


def test_cli_reports_network_failure(monkeypatch):
    def fail(**kwargs):
        raise RoadmapError("Fabric GPS unavailable")

    monkeypatch.setattr("purviewcli.sync.roadmap.fetch_governance_roadmap", fail)
    result = CliRunner().invoke(fabric, ["sync", "roadmap", "--output", "json"])
    assert result.exit_code != 0
    assert "Fabric GPS unavailable" in result.output


def test_cli_table_marks_roadmap_as_unverified(monkeypatch):
    monkeypatch.setattr(
        "purviewcli.sync.roadmap.fetch_governance_roadmap",
        lambda **kwargs: {
            "checked_at": "2026-09-25",
            "source": "GPS",
            "note": "Roadmap only; API verification required.",
            "items": [
                {
                    "last_modified": "2026-09-25",
                    "feature_name": "Ontology",
                    "product_name": "IQ",
                    "release_status": "Planned",
                    "release_date": "Q4 2026",
                }
            ],
        },
    )
    result = CliRunner().invoke(fabric, ["sync", "roadmap"])
    assert result.exit_code == 0, result.output
    assert "Ontology" in result.output
    assert "API verification required" in result.output
