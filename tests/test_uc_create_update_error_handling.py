# SPDX-License-Identifier: Apache-2.0
"""Regression tests: UC create/update/delete commands must not report false success.

Covers:
 - domain create
 - dataproduct create / update
 - data-asset delete
 - _uc_render (via data-asset create)
 - term create
"""

import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main

RUNNER = CliRunner()


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


ERROR_RESPONSE = {
    "status": "error",
    "message": "HTTP 400: Property contacts is required.",
    "status_code": 400,
}


# ---------------------------------------------------------------------------
# domain create
# ---------------------------------------------------------------------------
class TestDomainCreateErrorHandling:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_domain_create_status_error_prints_error_not_success(self, mock_cls):
        mock_cls.return_value.create_governance_domain.return_value = ERROR_RESPONSE

        result = invoke(
            "uc", "domain", "create",
            "--name", "test-domain",
            "--description", "test",
            "--type", "FunctionalUnit",
            "--status", "Draft",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "HTTP 400" in result.output
        assert "SUCCESS" not in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_domain_create_success_prints_success(self, mock_cls):
        mock_cls.return_value.create_governance_domain.return_value = {
            "id": "aaa-bbb",
            "name": "test-domain",
        }

        result = invoke(
            "uc", "domain", "create",
            "--name", "test-domain",
            "--description", "test",
            "--type", "FunctionalUnit",
            "--status", "Draft",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output
        assert "ERROR" not in result.output


# ---------------------------------------------------------------------------
# dataproduct create
# ---------------------------------------------------------------------------
class TestDataProductCreateErrorHandling:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_dataproduct_create_status_error_not_success(self, mock_cls):
        mock_cls.return_value.create_data_product.return_value = ERROR_RESPONSE

        result = invoke(
            "uc", "dataproduct", "create",
            "--name", "dp-test",
            "--domain-id", "bd112d6c-0000-0000-0000-000000000000",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_dataproduct_create_success_prints_success(self, mock_cls):
        mock_cls.return_value.create_data_product.return_value = {
            "id": "dp-111",
            "name": "dp-test",
        }

        result = invoke(
            "uc", "dataproduct", "create",
            "--name", "dp-test",
            "--domain-id", "bd112d6c-0000-0000-0000-000000000000",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output
        assert "ERROR" not in result.output


# ---------------------------------------------------------------------------
# dataproduct update
# ---------------------------------------------------------------------------
class TestDataProductUpdateErrorHandling:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_dataproduct_update_status_error_not_success(self, mock_cls):
        mock_cls.return_value.update_data_product.return_value = ERROR_RESPONSE

        result = invoke(
            "uc", "dataproduct", "update",
            "--product-id", "dp-111",
            "--name", "new-name",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output


# ---------------------------------------------------------------------------
# data-asset delete
# ---------------------------------------------------------------------------
class TestDataAssetDeleteErrorHandling:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_data_asset_delete_error_not_success(self, mock_cache, mock_cls):
        mock_client = MagicMock()
        mock_cache.return_value = mock_client
        mock_client.delete_data_asset.return_value = {
            "status": "error",
            "message": "HTTP 404: Asset not found",
            "status_code": 404,
        }

        result = invoke(
            "uc", "data-asset", "delete",
            "--asset-id", "aaaa-bbbb-cccc-dddd",
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "Failed to delete" in result.output or "ERROR" in result.output or "[X]" in result.output
        assert "SUCCESS" not in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_data_asset_delete_success_prints_success(self, mock_cache, mock_cls):
        mock_client = MagicMock()
        mock_cache.return_value = mock_client
        mock_client.delete_data_asset.return_value = None  # Empty 204 body

        result = invoke(
            "uc", "data-asset", "delete",
            "--asset-id", "aaaa-bbbb-cccc-dddd",
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output


# ---------------------------------------------------------------------------
# term create
# ---------------------------------------------------------------------------
class TestTermCreateErrorHandling:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_term_create_status_error_not_success(self, mock_cls):
        mock_cls.return_value.create_term.return_value = ERROR_RESPONSE

        result = invoke(
            "uc", "term", "create",
            "--name", "Revenue",
            "--description", "test",
            "--domain-id", "bd112d6c-0000-0000-0000-000000000000",
            "--status", "Draft",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output


# ---------------------------------------------------------------------------
# _uc_render error gate (via data-asset create)
# ---------------------------------------------------------------------------
class TestUcRenderErrorGate:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    @patch("purviewcli.client.client_cache.get_cached_client")
    def test_uc_render_displays_error_not_title(self, mock_cache, mock_cls):
        """_uc_render must not print the success title when result is an error dict."""
        mock_client = MagicMock()
        mock_cache.return_value = mock_client
        mock_client.create_data_asset.return_value = {
            "status": "error",
            "message": "HTTP 400: Property type is required.",
            "status_code": 400,
        }

        result = invoke(
            "uc", "data-asset", "create",
            "--payload-file", "nonexistent_but_mocked.json",
        )

        assert result.exit_code == 0, result.output
        # Error gate should include a failure token — not a bare success message
        assert "[X]" in result.output or "failed" in result.output.lower()
        # Should NOT silently print the title as a standalone success header
        assert "Data Asset Created\n" not in result.output
