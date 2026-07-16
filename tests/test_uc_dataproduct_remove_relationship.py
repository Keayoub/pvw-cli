# SPDX-License-Identifier: Apache-2.0
"""
Tests for the two bugs fixed in `pvw uc dataproduct remove-relationship`:

1. The DELETE endpoint now has {entityId} in the URL path
   (previously it was sent only as a query param, which the Purview API ignores for DELETE).

2. API errors are now surfaced to the user correctly.
   Previously, any response without a literal "error" key was printed as SUCCESS,
   masking real HTTP errors (404, 403, 400, ...).
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main
from purviewcli.client._unified_catalog import UnifiedCatalogClient
from purviewcli.client.endpoints import ENDPOINTS

RUNNER = CliRunner()


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


PRODUCT_ID = "prod-aaaa-1111"
ENTITY_ID = "asset-bbbb-2222"


# ---------------------------------------------------------------------------
# Bug 1: endpoint shape — entityId in URL path
# ---------------------------------------------------------------------------


class TestDeleteRelationshipEndpoint:
    """The entityId must appear in the URL path, not only as a query param."""

    @patch("purviewcli.client.endpoint.get_data")
    def test_entity_id_in_url_path(self, mock_get_data):
        """Verify the endpoint string contains the entityId as a path segment."""
        mock_get_data.return_value = {}  # simulate 204 No Content

        client = UnifiedCatalogClient()
        client.delete_data_product_relationship(
            {
                "--product-id": [PRODUCT_ID],
                "--entity-type": ["DATAASSET"],
                "--entity-id": [ENTITY_ID],
            }
        )

        call_args = mock_get_data.call_args[0][0]
        endpoint = call_args["endpoint"]

        assert ENTITY_ID in endpoint, (
            f"entityId '{ENTITY_ID}' should appear as a path segment in the endpoint, "
            f"but got: '{endpoint}'"
        )
        assert endpoint.endswith(f"/relationships/{ENTITY_ID}"), (
            f"Endpoint must end with /relationships/{{entityId}}, got: '{endpoint}'"
        )

    @patch("purviewcli.client.endpoint.get_data")
    def test_entity_id_NOT_in_query_params(self, mock_get_data):
        """Regression: entityId must NOT be sent as a query parameter."""
        mock_get_data.return_value = {}

        client = UnifiedCatalogClient()
        client.delete_data_product_relationship(
            {
                "--product-id": [PRODUCT_ID],
                "--entity-type": ["DATAASSET"],
                "--entity-id": [ENTITY_ID],
            }
        )

        call_args = mock_get_data.call_args[0][0]
        params = call_args.get("params", {}) or {}

        assert "entityId" not in params, (
            f"entityId must NOT be a query param (it belongs in the path), "
            f"but found params={params}"
        )

    @patch("purviewcli.client.endpoint.get_data")
    def test_entity_type_sent_as_query_param(self, mock_get_data):
        """entityType must still be sent as a query parameter."""
        mock_get_data.return_value = {}

        client = UnifiedCatalogClient()
        client.delete_data_product_relationship(
            {
                "--product-id": [PRODUCT_ID],
                "--entity-type": ["DATAASSET"],
                "--entity-id": [ENTITY_ID],
            }
        )

        call_args = mock_get_data.call_args[0][0]
        params = call_args.get("params", {}) or {}

        assert params.get("entityType") == "DATAASSET", (
            f"entityType should be uppercase query param 'DATAASSET', got params={params}"
        )

    @patch("purviewcli.client.endpoint.get_data")
    def test_http_method_is_delete(self, mock_get_data):
        mock_get_data.return_value = {}

        client = UnifiedCatalogClient()
        client.delete_data_product_relationship(
            {
                "--product-id": [PRODUCT_ID],
                "--entity-type": ["TERM"],
                "--entity-id": [ENTITY_ID],
            }
        )

        call_args = mock_get_data.call_args[0][0]
        assert call_args["method"] == "DELETE"

    def test_endpoint_template_contains_entity_id_placeholder(self):
        """Sanity-check the endpoint definition in endpoints.py."""
        template = ENDPOINTS["unified_catalog"]["delete_data_product_relationship"]
        assert "{entityId}" in template, (
            f"Endpoint template must contain {{entityId}} placeholder, got: '{template}'"
        )
        assert "{productId}" in template


# ---------------------------------------------------------------------------
# Bug 2: error detection — false SUCCESS masking real API errors
# ---------------------------------------------------------------------------


class TestRemoveRelationshipErrorHandling:
    """The CLI must surface API errors; previously any response without a literal
    'error' key was printed as SUCCESS."""

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_204_success_prints_success(self, mock_client_cls):
        """A real 204 No Content (empty dict) must still show SUCCESS."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_data_product_relationship.return_value = {}  # 204 → {}

        result = invoke(
            "uc", "dataproduct", "remove-relationship",
            "--product-id", PRODUCT_ID,
            "--entity-type", "DATAASSET",
            "--entity-id", ENTITY_ID,
            "--no-confirm",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output
        assert "ERROR" not in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_404_error_prints_error_not_success(self, mock_client_cls):
        """A 404 from the API must display ERROR, not SUCCESS.

        This is the regression test for the false-SUCCESS bug:
        the old code checked result.get('error') which is None for
        {'status': 'error', 'message': '...', 'status_code': 404},
        causing it to incorrectly print SUCCESS.
        """
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_data_product_relationship.return_value = {
            "status": "error",
            "message": "HTTP 404: Relationship not found",
            "status_code": 404,
        }

        result = invoke(
            "uc", "dataproduct", "remove-relationship",
            "--product-id", PRODUCT_ID,
            "--entity-type", "DATAASSET",
            "--entity-id", ENTITY_ID,
            "--no-confirm",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output, (
            "Expected ERROR in output for a 404 response, got: " + result.output
        )
        assert "SUCCESS" not in result.output, (
            "Got SUCCESS for a 404 — false-SUCCESS bug still present: " + result.output
        )

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_403_error_includes_message_in_output(self, mock_client_cls):
        """The actual API error message must appear in the output."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_data_product_relationship.return_value = {
            "status": "error",
            "message": "HTTP 403: Insufficient permissions",
            "status_code": 403,
        }

        result = invoke(
            "uc", "dataproduct", "remove-relationship",
            "--product-id", PRODUCT_ID,
            "--entity-type", "DATAASSET",
            "--entity-id", ENTITY_ID,
            "--no-confirm",
        )

        assert "403" in result.output or "Insufficient permissions" in result.output, (
            "Expected error details in output, got: " + result.output
        )

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_none_return_treated_as_success(self, mock_client_cls):
        """None is a valid no-op success return (some DELETE paths return None)."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_data_product_relationship.return_value = None

        result = invoke(
            "uc", "dataproduct", "remove-relationship",
            "--product-id", PRODUCT_ID,
            "--entity-type", "DATAASSET",
            "--entity-id", ENTITY_ID,
            "--no-confirm",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_error_output_includes_debug_tip(self, mock_client_cls):
        """Errors should hint that PURVIEWCLI_DEBUG=1 can help diagnose the issue."""
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_data_product_relationship.return_value = {
            "status": "error",
            "message": "HTTP 500: Internal server error",
            "status_code": 500,
        }

        result = invoke(
            "uc", "dataproduct", "remove-relationship",
            "--product-id", PRODUCT_ID,
            "--entity-type", "DATAASSET",
            "--entity-id", ENTITY_ID,
            "--no-confirm",
        )

        assert "PURVIEWCLI_DEBUG" in result.output, (
            "Expected PURVIEWCLI_DEBUG hint in error output, got: " + result.output
        )
