import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main


RUNNER = CliRunner()


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


def write_csv(path, rows):
    header = "info_object_guid,target_entity_guid,target_entity_type,relationship_type\n"
    body = "\n".join(rows)
    path.write_text(header + body + "\n", encoding="utf-8")


@patch("purviewcli.cli.relationship.Relationship")
def test_bulk_create_csv_uses_bulk_endpoint(mock_relationship_cls, tmp_path):
    mock_client = MagicMock()
    mock_relationship_cls.return_value = mock_client
    mock_client.relationshipCreateBulk.return_value = {"status": "ok"}

    csv_file = tmp_path / "relationships.csv"
    write_csv(
        csv_file,
        [
            "723d9e39-0000-0000-0000-000000000001,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has",
            "723d9e39-0000-0000-0000-000000000001,8c680380-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has",
        ],
    )

    result = invoke("relationship", "bulk-create-csv", "--csv-file", str(csv_file))

    assert result.exit_code == 0, result.output
    assert "OK: Generated 2 relationship(s)" in result.output
    assert "Bulk API call completed" in result.output

    mock_client.relationshipCreateBulk.assert_called_once()
    bulk_args = mock_client.relationshipCreateBulk.call_args[0][0]
    assert "--payloadFile" in bulk_args
    assert len(bulk_args["--payloadFile"]) == 2
    mock_client.relationshipCreate.assert_not_called()


@patch("purviewcli.cli.relationship.Relationship")
def test_bulk_create_csv_falls_back_to_single_create(mock_relationship_cls, tmp_path):
    mock_client = MagicMock()
    mock_relationship_cls.return_value = mock_client
    mock_client.relationshipCreateBulk.side_effect = RuntimeError("bulk not available")
    mock_client.relationshipCreate.return_value = {"status": "ok"}

    csv_file = tmp_path / "relationships.csv"
    write_csv(
        csv_file,
        [
            "723d9e39-0000-0000-0000-000000000001,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has",
            "723d9e39-0000-0000-0000-000000000001,8c680380-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has",
        ],
    )

    result = invoke("relationship", "bulk-create-csv", "--csv-file", str(csv_file))

    assert result.exit_code == 0, result.output
    assert "fallback to single create" in result.output
    assert "Created: 2/2" in result.output

    assert mock_client.relationshipCreateBulk.call_count == 1
    assert mock_client.relationshipCreate.call_count == 2


@patch("purviewcli.cli.relationship.Relationship")
def test_bulk_create_csv_dry_run_does_not_call_api(mock_relationship_cls, tmp_path):
    csv_file = tmp_path / "relationships.csv"
    write_csv(
        csv_file,
        [
            "723d9e39-0000-0000-0000-000000000001,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has",
        ],
    )

    result = invoke(
        "relationship",
        "bulk-create-csv",
        "--csv-file",
        str(csv_file),
        "--dry-run",
    )

    assert result.exit_code == 0, result.output
    assert "[DRY RUN]" in result.output
    mock_relationship_cls.assert_not_called()
