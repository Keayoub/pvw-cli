import os
import sys
import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main


RUNNER = CliRunner()
ENTITY_GUID = "entity-guid-123"


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


def normalize_output(text):
    return " ".join(text.split())


class TestBusinessMetadataCli:
    @patch("purviewcli.client._entity.Entity")
    def test_add_business_metadata_direct_mode(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityAddOrUpdateBusinessMetadata.return_value = {"status": "ok"}

        result = invoke(
            "entity",
            "add-business-metadata",
            "--guid",
            ENTITY_GUID,
            "--bm-name",
            "group1",
            "--attr-name",
            "attr1",
            "--attr-value",
            "value1",
            "--is-overwrite",
        )

        assert result.exit_code == 0, result.output
        mock_client.entityAddOrUpdateBusinessMetadata.assert_called_once()
        call_args = mock_client.entityAddOrUpdateBusinessMetadata.call_args[0][0]
        assert call_args["--guid"] == [ENTITY_GUID]
        assert call_args["--payloadFile"] == {"group1": {"attr1": "value1"}}
        assert call_args["--isOverwrite"] is True
        assert "OK" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_add_business_metadata_rejects_mixed_modes(self, mock_entity_cls, tmp_path):
        payload_file = tmp_path / "group.json"
        payload_file.write_text(json.dumps({"group1": {"attr1": "value1"}}), encoding="utf-8")

        result = invoke(
            "entity",
            "add-business-metadata",
            "--guid",
            ENTITY_GUID,
            "--payload-file",
            str(payload_file),
            "--bm-name",
            "group1",
            "--attr-name",
            "attr1",
            "--attr-value",
            "value1",
        )

        assert result.exit_code == 0, result.output
        assert (
            "Use either --payload-file OR --bm-name/--attr-name/--attr-value, not both"
            in normalize_output(result.output)
        )
        mock_entity_cls.assert_not_called()

    @patch("purviewcli.client._entity.Entity")
    def test_add_business_metadata_attributes_direct_mode(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityAddOrUpdateBusinessMetadataAttributes.return_value = {"status": "ok"}

        result = invoke(
            "entity",
            "add-business-metadata-attributes",
            "--guid",
            ENTITY_GUID,
            "--bm-name",
            "group1",
            "--attr-name",
            "attr1",
            "--attr-value",
            "value1",
        )

        assert result.exit_code == 0, result.output
        mock_client.entityAddOrUpdateBusinessMetadataAttributes.assert_called_once()
        call_args = mock_client.entityAddOrUpdateBusinessMetadataAttributes.call_args[0][0]
        assert call_args["--guid"] == [ENTITY_GUID]
        assert call_args["--businessMetadataName"] == "group1"
        assert call_args["--payloadFile"] == {"attr1": "value1"}
        assert "OK" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_remove_business_metadata_direct_mode(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRemoveBusinessMetadata.return_value = {"status": "ok"}

        result = invoke(
            "entity",
            "remove-business-metadata",
            "--guid",
            ENTITY_GUID,
            "--bm-name",
            "group1",
        )

        assert result.exit_code == 0, result.output
        mock_client.entityRemoveBusinessMetadata.assert_called_once()
        call_args = mock_client.entityRemoveBusinessMetadata.call_args[0][0]
        assert call_args["--guid"] == [ENTITY_GUID]
        assert call_args["--businessMetadataName"] == "group1"
        assert "OK" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_remove_business_metadata_attributes_direct_mode(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRemoveBusinessMetadataAttributes.return_value = {"status": "ok"}

        result = invoke(
            "entity",
            "remove-business-metadata-attributes",
            "--guid",
            ENTITY_GUID,
            "--bm-name",
            "group1",
            "--attr-name",
            "attr1",
        )

        assert result.exit_code == 0, result.output
        mock_client.entityRemoveBusinessMetadataAttributes.assert_called_once()
        call_args = mock_client.entityRemoveBusinessMetadataAttributes.call_args[0][0]
        assert call_args["--guid"] == [ENTITY_GUID]
        assert call_args["--businessMetadataName"] == "group1"
        assert call_args["--attributes"] == ["attr1"]
        assert "OK" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_remove_business_metadata_attributes_payload_file_mode(self, mock_entity_cls, tmp_path):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityRemoveBusinessMetadataAttributes.return_value = {"status": "ok"}

        payload_file = tmp_path / "attrs.json"
        payload_file.write_text(
            json.dumps({"businessMetadataAttributes": ["attr1", "attr2"]}),
            encoding="utf-8",
        )

        result = invoke(
            "entity",
            "remove-business-metadata-attributes",
            "--guid",
            ENTITY_GUID,
            "--bm-name",
            "group1",
            "--payload-file",
            str(payload_file),
        )

        assert result.exit_code == 0, result.output
        mock_client.entityRemoveBusinessMetadataAttributes.assert_called_once()
        call_args = mock_client.entityRemoveBusinessMetadataAttributes.call_args[0][0]
        assert call_args["--attributes"] == ["attr1", "attr2"]

    def test_remove_business_metadata_attributes_rejects_missing_input(self):
        result = invoke(
            "entity",
            "remove-business-metadata-attributes",
            "--guid",
            ENTITY_GUID,
            "--bm-name",
            "group1",
        )

        assert result.exit_code == 0, result.output
        assert "Provide either --payload-file or --attr-name" in normalize_output(result.output)