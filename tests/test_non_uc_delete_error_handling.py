# SPDX-License-Identifier: Apache-2.0
"""Regression tests for non-UC delete command error handling.

Ensures delete commands outside Unified Catalog do not report false success
when API clients return error dictionaries.
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


class TestDomainDeleteErrorHandling:
    @patch("purviewcli.cli.domain.Domain")
    def test_domain_delete_error_prints_error_not_success(self, mock_domain_cls):
        mock_client = MagicMock()
        mock_domain_cls.return_value = mock_client
        mock_client.domainsDelete.return_value = {
            "status": "error",
            "message": "HTTP 404: Domain not found",
            "status_code": 404,
        }

        result = invoke("domain", "delete", "--domain-name", "finance", "--force")

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output
        assert "404" in result.output


class TestEntityDeleteErrorHandling:
    @patch("purviewcli.client._relationship.Relationship")
    @patch("purviewcli.client._entity.Entity")
    def test_entity_delete_error_prints_error_not_success(self, mock_entity_cls, mock_rel_cls):
        mock_entity = MagicMock()
        mock_entity_cls.return_value = mock_entity
        mock_entity.entityRead.return_value = {"entity": {"relationshipAttributes": {}}}
        mock_entity.entityDelete.return_value = {
            "status": "error",
            "message": "HTTP 403: Forbidden",
            "status_code": 403,
        }

        mock_rel = MagicMock()
        mock_rel_cls.return_value = mock_rel

        result = invoke("entity", "delete", "--guid", "1111-2222-3333-4444")

        assert result.exit_code == 0, result.output
        assert "failed" in result.output.lower()
        assert "completed successfully" not in result.output.lower()
        assert "403" in result.output


class TestLineageDeleteColumnErrorHandling:
    @patch("purviewcli.client.endpoint.get_data")
    def test_lineage_delete_column_error_prints_error_not_success(self, mock_get_data):
        mock_get_data.side_effect = [
            {
                "entity": {
                    "attributes": {"name": "proc-1", "description": "test"},
                    "relationshipAttributes": {"inputs": [], "outputs": []},
                }
            },
            {
                "status": "error",
                "message": "HTTP 404: Process not found",
                "status_code": 404,
            },
        ]

        result = invoke(
            "lineage",
            "delete-column",
            "--process-guid",
            "aaaa-bbbb-cccc-dddd",
            "--force",
        )

        assert result.exit_code == 0, result.output
        assert "ERROR" in result.output
        assert "SUCCESS" not in result.output
        assert "404" in result.output


class TestScanDeleteIntegrationRuntimeSafeErrorHandling:
    @patch("purviewcli.cli.scan.Scan")
    def test_scan_deleteintegrationruntimesafe_raises_on_error_result(self, mock_scan_cls):
        mock_scan = MagicMock()
        mock_scan_cls.return_value = mock_scan
        mock_scan.scanIntegrationRuntimeRead.return_value = {"name": "ir1"}
        mock_scan.scanDataSourcesRead.return_value = {"value": []}
        mock_scan.scanIntegrationRuntimeDelete.return_value = {
            "status": "error",
            "message": "HTTP 403: Forbidden",
            "status_code": 403,
        }

        result = invoke(
            "scan",
            "deleteintegrationruntimesafe",
            "--integrationRuntimeName",
            "ir1",
        )

        assert result.exit_code != 0, result.output
        assert "Failed to delete integration runtime" in result.output
        assert "403" in result.output
