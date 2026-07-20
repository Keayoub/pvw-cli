# SPDX-License-Identifier: Apache-2.0
"""Regression tests for Unified Catalog non-relationship delete commands.

Ensures delete commands do not print false SUCCESS on API errors.
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


class TestDataProductDeleteErrorHandling:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_delete_dataproduct_404_prints_error_not_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_data_product.return_value = {
            "status": "error",
            "message": "HTTP 404: Data product not found",
            "status_code": 404,
        }

        result = invoke(
            "uc",
            "dataproduct",
            "delete",
            "--product-id",
            "prod-aaaa-1111",
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output
        assert "404" in result.output


class TestKeyResultDeleteErrorHandling:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_delete_key_result_403_prints_error_not_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_key_result.return_value = {
            "status": "error",
            "message": "HTTP 403: Insufficient permissions",
            "status_code": 403,
        }

        result = invoke(
            "uc",
            "keyresult",
            "delete",
            "--objective-id",
            "obj-aaaa-1111",
            "--key-result-id",
            "kr-bbbb-2222",
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output
        assert "403" in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_delete_key_result_none_is_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_key_result.return_value = None

        result = invoke(
            "uc",
            "keyresult",
            "delete",
            "--objective-id",
            "obj-aaaa-1111",
            "--key-result-id",
            "kr-bbbb-2222",
            "--yes",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output
