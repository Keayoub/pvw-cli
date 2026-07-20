# SPDX-License-Identifier: Apache-2.0
"""Regression tests for Unified Catalog relationship delete error handling.

Ensures relationship delete commands do not print false SUCCESS on API errors.
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


class TestCdeRemoveRelationship:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_cde_remove_relationship_404_prints_error_not_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_cde_relationship.return_value = {
            "status": "error",
            "message": "HTTP 404: Relationship not found",
            "status_code": 404,
        }

        result = invoke(
            "uc",
            "cde",
            "remove-relationship",
            "--cde-id",
            "cde-aaaa-1111",
            "--entity-type",
            "DATAPRODUCT",
            "--entity-id",
            "prod-bbbb-2222",
            "--no-confirm",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output
        assert "404" in result.output


class TestTermDeleteRelationship:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_term_delete_relationship_403_prints_error_not_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_term_relationship.return_value = {
            "status": "error",
            "message": "HTTP 403: Insufficient permissions",
            "status_code": 403,
        }

        result = invoke(
            "uc",
            "term",
            "delete-relationship",
            "--term-id",
            "term-aaaa-1111",
            "--entity-id",
            "term-bbbb-2222",
            "--confirm",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output
        assert "403" in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_term_delete_relationship_none_is_success(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.delete_term_relationship.return_value = None

        result = invoke(
            "uc",
            "term",
            "delete-relationship",
            "--term-id",
            "term-aaaa-1111",
            "--entity-id",
            "term-bbbb-2222",
            "--confirm",
        )

        assert result.exit_code == 0, result.output
        assert "SUCCESS" in result.output
