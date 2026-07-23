# SPDX-License-Identifier: Apache-2.0
"""Regression tests for `pvw uc data-asset find` and entity-guid lookup."""

import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main
from purviewcli.client._unified_catalog import UnifiedCatalogClient

RUNNER = CliRunner()

ENTITY_GUID = "006c1e48-e342-47e9-ab5d-0dd9ff89bd96"


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


class TestFindDataAssetByEntityGuidClient:
    @patch("purviewcli.client.endpoint.get_data")
    def test_query_payload_uses_entity_guids(self, mock_get_data):
        mock_get_data.return_value = {}

        client = UnifiedCatalogClient()
        client.find_data_asset_by_entity_guid({"--entity-guid": [ENTITY_GUID]})

        call_args = mock_get_data.call_args[0][0]
        assert call_args["method"] == "POST"
        assert call_args["endpoint"].endswith("/datagovernance/catalog/dataAssets/query")
        assert call_args["params"].get("api-version") == "2026-03-20-preview"
        assert call_args["payload"] == {"entityGuids": [ENTITY_GUID]}


class TestFindDataAssetByEntityGuidCli:
    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_cli_invokes_client_and_renders(self, mock_get_cached_client):
        mock_client = MagicMock()
        mock_client.find_data_asset_by_entity_guid.return_value = {
            "value": [{"id": "6cca846e-f2b6-4eff-a271-dbf6f6f60000"}]
        }
        mock_get_cached_client.return_value = mock_client

        result = invoke(
            "uc",
            "data-asset",
            "find",
            "--entity-guid",
            ENTITY_GUID,
            "--output",
            "json",
        )

        assert result.exit_code == 0, result.output
        call_payload = mock_client.find_data_asset_by_entity_guid.call_args[0][0]
        assert call_payload["--entity-guid"] == ENTITY_GUID
        assert "6cca846e-f2b6-4eff-a271-dbf6f6f60000" in result.output
