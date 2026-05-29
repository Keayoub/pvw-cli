"""Tests for pvw entity bulk-read-tables command."""
import json
import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main

RUNNER = CliRunner()

# ------------------------------------------------------------------ #
# Fixtures                                                             #
# ------------------------------------------------------------------ #

GUID_TABLE_1 = "ea3412c3-7387-4bc1-9923-11f6f6f60000"
GUID_TABLE_2 = "2d21eba5-b08b-4571-b31d-7bf6f6f60000"
GUID_COL_1A = "ea3412c3-0000-0000-0000-aaaaaaaaaaaa"
GUID_COL_1B = "ea3412c3-0000-0000-0000-bbbbbbbbbbbb"
GUID_COL_2A = "2d21eba5-0000-0000-0000-aaaaaaaaaaaa"

# Simulates the entityReadBulk response shape:
#   entities[]  -> table entities with relationshipAttributes.columns
#   referredEntities{} -> column entities keyed by guid (may carry data_type)
MOCK_BULK_RESPONSE = {
    "referredEntities": {
        GUID_COL_1A: {"attributes": {"data_type": "int", "name": "CustomerID"}},
        GUID_COL_1B: {"attributes": {"data_type": "nvarchar", "name": "FullName"}},
        GUID_COL_2A: {"attributes": {"data_type": "uniqueidentifier", "name": "AddressID"}},
    },
    "entities": [
        {
            "guid": GUID_TABLE_1,
            "attributes": {"name": "Customer"},
            "relationshipAttributes": {
                "columns": [
                    {"guid": GUID_COL_1A, "displayText": "CustomerID"},
                    {"guid": GUID_COL_1B, "displayText": "FullName"},
                ]
            },
        },
        {
            "guid": GUID_TABLE_2,
            "attributes": {"name": "Address"},
            "relationshipAttributes": {
                "columns": [
                    {"guid": GUID_COL_2A, "displayText": "AddressID"},
                ]
            },
        },
    ],
}

MOCK_EMPTY_RESPONSE = {"referredEntities": {}, "entities": []}

MOCK_NO_COLUMNS_RESPONSE = {
    "referredEntities": {},
    "entities": [
        {
            "guid": GUID_TABLE_1,
            "attributes": {"name": "EmptyTable"},
            "relationshipAttributes": {"columns": []},
        }
    ],
}


def _invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


# ------------------------------------------------------------------ #
# Mock-mode tests (no network, no patch needed)                        #
# ------------------------------------------------------------------ #

class TestBulkReadTablesMockMode:
    def test_mock_single_guid(self):
        result = _invoke("--mock", "entity", "bulk-read-tables", "--guid", GUID_TABLE_1)
        assert result.exit_code == 0, result.output
        assert "MOCK" in result.output
        assert GUID_TABLE_1 in result.output

    def test_mock_multiple_guids(self):
        result = _invoke(
            "--mock",
            "entity",
            "bulk-read-tables",
            "--guid", GUID_TABLE_1,
            "--guid", GUID_TABLE_2,
        )
        assert result.exit_code == 0, result.output
        assert GUID_TABLE_1 in result.output
        assert GUID_TABLE_2 in result.output

    def test_mock_exits_zero(self):
        result = _invoke("--mock", "entity", "bulk-read-tables", "--guid", GUID_TABLE_1)
        assert result.exit_code == 0


# ------------------------------------------------------------------ #
# Unit tests with patched entityReadBulk                               #
# ------------------------------------------------------------------ #

class TestBulkReadTablesUnit:

    @patch("purviewcli.client._entity.Entity")
    def test_table_output_contains_table_names(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_BULK_RESPONSE

        result = _invoke(
            "entity", "bulk-read-tables",
            "--guid", GUID_TABLE_1,
            "--guid", GUID_TABLE_2,
        )
        assert result.exit_code == 0, result.output
        assert "Customer" in result.output
        assert "Address" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_table_output_contains_column_names(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_BULK_RESPONSE

        result = _invoke(
            "entity", "bulk-read-tables",
            "--guid", GUID_TABLE_1,
            "--guid", GUID_TABLE_2,
        )
        assert result.exit_code == 0, result.output
        assert "CustomerID" in result.output
        assert "FullName" in result.output
        assert "AddressID" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_table_output_contains_data_types(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_BULK_RESPONSE

        result = _invoke(
            "entity", "bulk-read-tables",
            "--guid", GUID_TABLE_1,
        )
        assert result.exit_code == 0, result.output
        assert "int" in result.output
        assert "nvarchar" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_only_tables_are_reported_not_referred_entities(self, mock_entity_cls):
        """Ensure referredEntities (columns) are NOT surfaced as top-level table rows."""
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_BULK_RESPONSE

        result = _invoke(
            "entity", "bulk-read-tables",
            "--guid", GUID_TABLE_1,
            "--guid", GUID_TABLE_2,
        )
        assert result.exit_code == 0, result.output
        # Column GUIDs must not appear as top-level entity names/headers
        # (they are valid in the GUID column but the table header should show table names)
        assert "Customer" in result.output
        assert "Address" in result.output
        # Summary must report 2 tables, not 3 (the referred entities count)
        assert "2 table" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_summary_counts_correct_columns(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_BULK_RESPONSE

        result = _invoke(
            "entity", "bulk-read-tables",
            "--guid", GUID_TABLE_1,
            "--guid", GUID_TABLE_2,
        )
        assert result.exit_code == 0, result.output
        # 2 cols in Customer + 1 col in Address = 3 total
        assert "3" in result.output

    @patch("purviewcli.client._entity.Entity")
    def test_json_output_is_valid_and_contains_all_rows(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_BULK_RESPONSE

        result = _invoke(
            "entity", "bulk-read-tables",
            "--guid", GUID_TABLE_1,
            "--guid", GUID_TABLE_2,
            "--output", "json",
        )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 3  # 2 cols for table1, 1 col for table2
        table_names = {row["table_name"] for row in data}
        assert table_names == {"Customer", "Address"}

    @patch("purviewcli.client._entity.Entity")
    def test_json_output_rows_have_required_keys(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_BULK_RESPONSE

        result = _invoke(
            "entity", "bulk-read-tables",
            "--guid", GUID_TABLE_1,
            "--output", "json",
        )
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)
        required_keys = {"table_guid", "table_name", "column_guid", "column_name", "data_type"}
        for row in data:
            assert required_keys.issubset(row.keys()), f"Missing keys in row: {row}"

    @patch("purviewcli.client._entity.Entity")
    def test_csv_output_has_header_and_rows(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_BULK_RESPONSE

        result = _invoke(
            "entity", "bulk-read-tables",
            "--guid", GUID_TABLE_1,
            "--guid", GUID_TABLE_2,
            "--output", "csv",
        )
        assert result.exit_code == 0, result.output
        lines = [l for l in result.output.splitlines() if l.strip()]
        # header + 3 data rows
        assert lines[0] == "table_guid,table_name,column_guid,column_name,data_type"
        assert len(lines) == 4

    @patch("purviewcli.client._entity.Entity")
    def test_empty_response_warns_gracefully(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_EMPTY_RESPONSE

        result = _invoke("entity", "bulk-read-tables", "--guid", GUID_TABLE_1)
        assert result.exit_code == 0, result.output
        assert "no result" in result.output.lower() or "no columns" in result.output.lower()

    @patch("purviewcli.client._entity.Entity")
    def test_table_with_no_columns_warns(self, mock_entity_cls):
        mock_client = MagicMock()
        mock_entity_cls.return_value = mock_client
        mock_client.entityReadBulk.return_value = MOCK_NO_COLUMNS_RESPONSE

        result = _invoke("entity", "bulk-read-tables", "--guid", GUID_TABLE_1)
        assert result.exit_code == 0, result.output
        assert "no columns" in result.output.lower()
