# SPDX-License-Identifier: Apache-2.0
"""Regression tests for `pvw uc data-asset remove-relationship`.

Covers:
1. DELETE endpoint shape includes entityId in URL path.
2. entityType is sent as query parameter.
3. CLI surfaces API errors instead of printing false SUCCESS.
"""

import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main
from purviewcli.client._unified_catalog import UnifiedCatalogClient

RUNNER = CliRunner()


ASSET_ID = "asset-aaaa-1111"
ENTITY_ID = "product-bbbb-2222"
ENTITY_GUID = "entity-guid-cccc-3333"


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


class TestDataAssetDeleteRelationshipEndpoint:
    @patch("purviewcli.client.endpoint.get_data")
    def test_entity_id_in_url_path(self, mock_get_data):
        mock_get_data.return_value = {}

        client = UnifiedCatalogClient()
        client.delete_data_asset_relationship(
            {
                "--asset-id": [ASSET_ID],
                "--entity-id": [ENTITY_ID],
                "--entity-type": ["DATAPRODUCT"],
            }
        )

        call_args = mock_get_data.call_args[0][0]
        endpoint = call_args["endpoint"]
        params = call_args.get("params", {})

        assert endpoint.endswith(f"/relationships/{ENTITY_ID}")
        assert params.get("entityType") == "DATAPRODUCT"
        assert call_args["method"] == "DELETE"


class TestDataAssetDeleteRelationshipCli:
    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_cli_uses_default_entity_type_dataproduct(self, mock_get_cached_client):
        mock_client = MagicMock()
        mock_client.delete_data_asset_relationship.return_value = {}
        mock_get_cached_client.return_value = mock_client

        result = invoke(
            "uc",
            "data-asset",
            "remove-relationship",
            "--asset-id",
            ASSET_ID,
            "--entity-id",
            ENTITY_ID,
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output

        call_payload = mock_client.delete_data_asset_relationship.call_args[0][0]
        assert call_payload["--entity-type"] == "DATAPRODUCT"

    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_cli_error_response_prints_error_not_success(self, mock_get_cached_client):
        mock_client = MagicMock()
        mock_client.delete_data_asset_relationship.return_value = {
            "status": "error",
            "message": "HTTP 404: Relationship not found",
            "status_code": 404,
        }
        mock_client.delete_data_product_relationship.return_value = {
            "status": "error",
            "message": "HTTP 404:",
            "status_code": 404,
        }
        mock_get_cached_client.return_value = mock_client

        result = invoke(
            "uc",
            "data-asset",
            "remove-relationship",
            "--asset-id",
            ASSET_ID,
            "--entity-id",
            ENTITY_ID,
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output
        assert "404" in result.output

    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_cli_fallback_to_dataproduct_delete_on_404(self, mock_get_cached_client):
        mock_client = MagicMock()
        mock_client.delete_data_asset_relationship.return_value = {
            "status": "error",
            "message": "HTTP 404:",
            "status_code": 404,
        }
        mock_client.delete_data_product_relationship.return_value = None
        mock_get_cached_client.return_value = mock_client

        result = invoke(
            "uc",
            "data-asset",
            "remove-relationship",
            "--asset-id",
            ASSET_ID,
            "--entity-id",
            ENTITY_ID,
            "--entity-type",
            "DATAPRODUCT",
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output
        assert "ERROR" not in result.output

        mock_client.delete_data_product_relationship.assert_called_once_with(
            {
                "--product-id": [ENTITY_ID],
                "--entity-type": ["DATAASSET"],
                "--entity-id": [ASSET_ID],
            }
        )

    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_cli_fallback_uses_entity_guid_when_provided(self, mock_get_cached_client):
        mock_client = MagicMock()
        mock_client.delete_data_asset_relationship.return_value = {
            "status": "error",
            "message": "HTTP 404:",
            "status_code": 404,
        }
        mock_client.delete_data_product_relationship.return_value = None
        mock_get_cached_client.return_value = mock_client

        result = invoke(
            "uc",
            "data-asset",
            "remove-relationship",
            "--asset-id",
            ASSET_ID,
            "--entity-id",
            ENTITY_ID,
            "--entity-type",
            "DATAPRODUCT",
            "--entity-guid",
            ENTITY_GUID,
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output
        assert "ERROR" not in result.output

        mock_client.delete_data_product_relationship.assert_called_once_with(
            {
                "--product-id": [ENTITY_ID],
                "--entity-type": ["DATAASSET"],
                "--entity-id": [ENTITY_GUID],
            }
        )

    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_cli_fallback_error_still_prints_error(self, mock_get_cached_client):
        mock_client = MagicMock()
        mock_client.delete_data_asset_relationship.return_value = {
            "status": "error",
            "message": "HTTP 404:",
            "status_code": 404,
        }
        mock_client.delete_data_product_relationship.return_value = {
            "status": "error",
            "message": "HTTP 404:",
            "status_code": 404,
        }
        mock_get_cached_client.return_value = mock_client

        result = invoke(
            "uc",
            "data-asset",
            "remove-relationship",
            "--asset-id",
            ASSET_ID,
            "--entity-id",
            ENTITY_ID,
            "--entity-type",
            "DATAPRODUCT",
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output
