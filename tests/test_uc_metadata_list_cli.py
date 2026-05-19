import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main


RUNNER = CliRunner()


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


class TestUcMetadataListCli:
    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_metadata_list_default_uses_atlas_shape(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.list_custom_metadata.return_value = {
            "businessMetadataDefs": [
                {
                    "name": "Governance",
                    "attributeDefs": [
                        {"name": "Owner", "typeName": "string", "description": "Data owner"}
                    ],
                }
            ]
        }

        result = invoke("uc", "metadata", "list")

        assert result.exit_code == 0, result.output
        mock_client.list_custom_metadata.assert_called_once_with(
            {
                "--include-expired": False,
                "--api-version": ["2026-03-20-preview"],
            }
        )
        assert "Business Metadata Attributes" in result.output
        assert "Owner" in result.output

    @patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
    def test_metadata_list_include_expired_uses_catalog_preview(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.list_custom_metadata.return_value = {
            "value": [
                {
                    "groupName": "Attribut_test1",
                    "groupId": "946dda4d-9484-21c1-025f-a16f6fbbacdc",
                    "groupStatus": "Published",
                    "groupExpired": False,
                    "attributeName": "test2",
                    "attributeId": "4f0732c7-e8f9-4cf4-a5ef-3127ab4ddbb7",
                },
                {
                    "groupName": "GroupTest",
                    "groupId": "8429b16e-222d-445a-940b-8fe0dc5d9a40",
                    "groupStatus": "Expired",
                    "groupExpired": True,
                    "attributeName": "AttributTest",
                    "attributeId": "00112233-4455-6677-8899-aabbccddeeff",
                },
            ]
        }

        result = invoke("uc", "metadata", "list", "--include-expired")

        assert result.exit_code == 0, result.output
        mock_client.list_custom_metadata.assert_called_once_with(
            {
                "--include-expired": True,
                "--api-version": ["2026-03-20-preview"],
            }
        )
        assert "Custom Metadata (Including Expired)" in result.output
        assert "GroupTest" in result.output
        assert "yes" in result.output
        assert "00112233-4455-6677-8899-aabbccddeeff" in result.output
