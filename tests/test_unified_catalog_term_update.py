import json
import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main
from purviewcli.client._unified_catalog import UnifiedCatalogClient


RUNNER = CliRunner()


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


@patch("purviewcli.client.endpoint.get_data")
@patch("purviewcli.client._unified_catalog.UnifiedCatalogClient.get_term_by_id")
def test_update_term_preserves_existing_fields(mock_get_term_by_id, mock_get_data):
    mock_get_term_by_id.return_value = {
        "id": "term-123",
        "name": "Old name",
        "description": "Old description",
        "domain": "domain-1",
        "status": "Draft",
        "parentId": "parent-1",
        "contacts": {
            "owner": [{"id": "owner-old"}],
            "steward": [{"id": "steward-1"}],
        },
        "acronyms": ["OLD"],
        "resources": [{"name": "Docs", "url": "https://example.invalid"}],
        "managedAttributes": [{"name": "team", "value": "platform"}],
        "updateTime": 123,
    }
    mock_get_data.return_value = {"status": "ok"}

    client = UnifiedCatalogClient()
    result = client.update_term(
        {
            "--term-id": ["term-123"],
            "--name": ["New name"],
            "--owner-id": ["owner-new"],
        }
    )

    assert result == {"status": "ok"}
    payload = mock_get_data.call_args[0][0]["payload"]
    assert payload["id"] == "term-123"
    assert payload["name"] == "New name"
    assert payload["parentId"] == "parent-1"
    assert payload["contacts"]["owner"] == [{"id": "owner-new"}]
    assert payload["contacts"]["steward"] == [{"id": "steward-1"}]
    assert payload["acronyms"] == ["OLD"]
    assert payload["resources"] == [{"name": "Docs", "url": "https://example.invalid"}]
    assert payload["managedAttributes"] == [{"name": "team", "value": "platform"}]
    assert payload["updateTime"] == 123


@patch("purviewcli.cli.unified_catalog.time.sleep", return_value=None)
@patch("purviewcli.cli.unified_catalog.UnifiedCatalogClient")
def test_update_json_accepts_debug_and_forwards_it(mock_client_cls, _mock_sleep, tmp_path):
    json_file = tmp_path / "updates.json"
    json_file.write_text(
        json.dumps(
            {
                "updates": [
                    {
                        "term_id": "term-123",
                        "name": "New name",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    mock_client = MagicMock()
    mock_client.update_term.return_value = {"status": "ok"}
    mock_client_cls.return_value = mock_client

    result = invoke(
        "uc",
        "term",
        "update-json",
        "--json-file",
        str(json_file),
        "--debug",
    )

    assert result.exit_code == 0, result.output
    assert mock_client.update_term.call_count == 1
    call_args = mock_client.update_term.call_args[0][0]
    assert call_args["--term-id"] == ["term-123"]
    assert call_args["--debug"] is True
