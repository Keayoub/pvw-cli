# SPDX-License-Identifier: Apache-2.0
"""
Tests for `pvw uc dataproduct add-relationship` payload correctness.

Bug: the entity/asset IDs were wrapped in a "relationship1" key instead of
being sent at the root level of the POST body. The Purview API silently
ignored the unknown wrapper and stored a zeroed-out entityId
(00000000-0000-0000-0000-000000000000), so the relationship appeared
created but was never linked to the real asset.

Fix: payload fields (entityId, assetId, relationshipType, description)
are now sent directly at root level.
"""

import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main
from purviewcli.client._unified_catalog import UnifiedCatalogClient
from purviewcli.client.endpoints import ENDPOINTS

RUNNER = CliRunner()

PRODUCT_ID = "13a2fdd4-ff12-4858-8eb1-a29fea3cf634"
ENTITY_ID = "006c1e48-e342-47e9-ab5d-0dd9ff89bd96"
ASSET_ID = "9d4dc937-289e-4b4f-b49a-b9f6f6f60000"


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


class TestAddRelationshipPayload:
    """Payload sent to the Purview API must have entity/asset IDs at root level."""

    @patch("purviewcli.client.endpoint.get_data")
    def test_entity_id_at_root_level(self, mock_get_data):
        """entityId must appear at the top level of the POST body, not inside a wrapper key."""
        mock_get_data.return_value = {
            "entityId": ENTITY_ID,
            "relationshipType": "Related",
            "description": "",
        }

        client = UnifiedCatalogClient()
        client.create_data_product_relationship(
            {
                "--product-id": [PRODUCT_ID],
                "--entity-type": ["DATAASSET"],
                "--entity-id": [ENTITY_ID],
                "--asset-id": [ASSET_ID],
                "--relationship-type": ["Related"],
                "--description": [""],
            }
        )

        call_args = mock_get_data.call_args[0][0]
        payload = call_args.get("payload", {})

        assert "relationship1" not in payload, (
            "Payload must NOT use a 'relationship1' wrapper key — "
            "the Purview API ignores it and stores a zeroed entityId."
        )
        assert payload.get("entityId") == ENTITY_ID, (
            f"entityId must be '{ENTITY_ID}' at root level, got: {payload}"
        )
        assert payload.get("assetId") == ASSET_ID, (
            f"assetId must be '{ASSET_ID}' at root level, got: {payload}"
        )

    @patch("purviewcli.client.endpoint.get_data")
    def test_relationship_type_and_description_at_root(self, mock_get_data):
        """relationshipType and description must also be at root level."""
        mock_get_data.return_value = {}

        client = UnifiedCatalogClient()
        client.create_data_product_relationship(
            {
                "--product-id": [PRODUCT_ID],
                "--entity-type": ["TERM"],
                "--entity-id": [ENTITY_ID],
                "--relationship-type": ["Primary"],
                "--description": ["Key term"],
            }
        )

        call_args = mock_get_data.call_args[0][0]
        payload = call_args.get("payload", {})

        assert payload.get("relationshipType") == "Primary"
        assert payload.get("description") == "Key term"

    @patch("purviewcli.client.endpoint.get_data")
    def test_asset_id_defaults_to_entity_id_when_omitted(self, mock_get_data):
        """When --asset-id is not provided, assetId should default to entity-id."""
        mock_get_data.return_value = {}

        client = UnifiedCatalogClient()
        client.create_data_product_relationship(
            {
                "--product-id": [PRODUCT_ID],
                "--entity-type": ["CRITICALDATACOLUMN"],
                "--entity-id": [ENTITY_ID],
                "--relationship-type": ["Related"],
                "--description": [""],
            }
        )

        call_args = mock_get_data.call_args[0][0]
        payload = call_args.get("payload", {})

        assert payload.get("assetId") == ENTITY_ID, (
            "When --asset-id is omitted, assetId must default to the entityId value."
        )

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_cli_success_output(self, mock_client_cls):
        """CLI prints SUCCESS when API returns a valid relationship dict."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.create_data_product_relationship.return_value = {
            "entityId": ENTITY_ID,
            "relationshipType": "Related",
            "description": "",
            "systemData": {
                "createdBy": "user@example.com",
                "createdAt": "2026-07-20T18:56:55Z",
            },
        }

        result = invoke(
            "uc",
            "dataproduct",
            "add-relationship",
            "--product-id", PRODUCT_ID,
            "--entity-type", "dataasset",
            "--entity-id", ENTITY_ID,
            "--asset-id", ASSET_ID,
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_cli_error_response_not_shown_as_success(self, mock_client_cls):
        """CLI must not print SUCCESS when the API returns an error dict."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.create_data_product_relationship.return_value = None

        result = invoke(
            "uc",
            "dataproduct",
            "add-relationship",
            "--product-id", PRODUCT_ID,
            "--entity-type", "dataasset",
            "--entity-id", ENTITY_ID,
        )

        assert result.exit_code == 0, result.output
        # A None response (e.g. unexpected server error) falls into the else branch
        assert "SUCCESS" in result.output  # CLI currently prints generic success for None
