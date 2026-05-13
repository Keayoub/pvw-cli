"""Tests for pvw entity list --collection-id / --guid command."""
import json
import os
import sys
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main

RUNNER = CliRunner()

MOCK_SEARCH_RESPONSE = {
    "@search.count": 3,
    "value": [
        {
            "id": "aaaa0000-0000-0000-0000-000000000001",
            "name": "SalesTable",
            "entityType": "azure_sql_table",
            "qualifiedName": "mssql://server/db/SalesLT/SalesTable",
            "collection": {"name": "pp3hth"},
        },
        {
            "id": "bbbb0000-0000-0000-0000-000000000002",
            "name": "CustomerView",
            "entityType": "azure_sql_view",
            "qualifiedName": "mssql://server/db/SalesLT/CustomerView",
            "collection": {"name": "pp3hth"},
        },
        {
            "id": "cccc0000-0000-0000-0000-000000000003",
            "name": "OrderDataset",
            "entityType": "DataSet",
            "qualifiedName": "storage://container/orders",
            "collection": {"name": "pp3hth"},
        },
    ],
}

MOCK_EMPTY_RESPONSE = {"@search.count": 0, "value": []}


def _invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


class TestEntityListCommand:
    # ------------------------------------------------------------------ #
    # Basic invocation — no filter                                         #
    # ------------------------------------------------------------------ #
    @patch("purviewcli.client._search.Search")
    def test_list_no_filter_table_output(self, mock_search_cls):
        mock_client = MagicMock()
        mock_search_cls.return_value = mock_client
        mock_client.searchQuery.return_value = MOCK_SEARCH_RESPONSE

        result = _invoke("entity", "list")
        assert result.exit_code == 0, result.output
        # Table must contain GUIDs and names
        assert "aaaa0000" in result.output
        assert "SalesTable" in result.output
        assert "azure_sql_table" in result.output

    # ------------------------------------------------------------------ #
    # --collection-id filter                                               #
    # ------------------------------------------------------------------ #
    @patch("purviewcli.client._search.Search")
    def test_list_by_collection_id(self, mock_search_cls):
        mock_client = MagicMock()
        mock_search_cls.return_value = mock_client
        mock_client.searchQuery.return_value = MOCK_SEARCH_RESPONSE

        result = _invoke("entity", "list", "--collection-id", "pp3hth")
        assert result.exit_code == 0, result.output

        # Verify the API was called with a collectionId filter
        call_args = mock_client.searchQuery.call_args[0][0]
        payload = json.loads(call_args["--payload"])
        assert payload["filter"]["collectionId"] == "pp3hth"

        # Table should render
        assert "aaaa0000" in result.output
        assert "SalesTable" in result.output

    # ------------------------------------------------------------------ #
    # --guid alias behaves identically to --collection-id                 #
    # ------------------------------------------------------------------ #
    @patch("purviewcli.client._search.Search")
    def test_list_guid_alias(self, mock_search_cls):
        mock_client = MagicMock()
        mock_search_cls.return_value = mock_client
        mock_client.searchQuery.return_value = MOCK_SEARCH_RESPONSE

        result = _invoke("entity", "list", "--guid", "pp3hth")
        assert result.exit_code == 0, result.output

        call_args = mock_client.searchQuery.call_args[0][0]
        payload = json.loads(call_args["--payload"])
        assert payload["filter"]["collectionId"] == "pp3hth"

    # ------------------------------------------------------------------ #
    # Combined filters: --collection-id + --type-name                     #
    # ------------------------------------------------------------------ #
    @patch("purviewcli.client._search.Search")
    def test_list_collection_and_type_filter(self, mock_search_cls):
        mock_client = MagicMock()
        mock_search_cls.return_value = mock_client
        mock_client.searchQuery.return_value = MOCK_SEARCH_RESPONSE

        result = _invoke(
            "entity", "list",
            "--collection-id", "pp3hth",
            "--type-name", "azure_sql_table",
        )
        assert result.exit_code == 0, result.output

        payload = json.loads(mock_client.searchQuery.call_args[0][0]["--payload"])
        # Combined filter must use "and" clause
        assert "and" in payload["filter"]
        clauses = payload["filter"]["and"]
        collection_clause = next((c for c in clauses if "collectionId" in c), None)
        type_clause = next((c for c in clauses if "entityType" in c), None)
        assert collection_clause is not None and collection_clause["collectionId"] == "pp3hth"
        assert type_clause is not None and type_clause["entityType"] == "azure_sql_table"

    # ------------------------------------------------------------------ #
    # --output json                                                        #
    # ------------------------------------------------------------------ #
    @patch("purviewcli.client._search.Search")
    def test_list_output_json(self, mock_search_cls):
        mock_client = MagicMock()
        mock_search_cls.return_value = mock_client
        mock_client.searchQuery.return_value = MOCK_SEARCH_RESPONSE

        result = _invoke("entity", "list", "--guid", "pp3hth", "--output", "json")
        assert result.exit_code == 0, result.output
        parsed = json.loads(result.output)
        assert parsed["@search.count"] == 3

    # ------------------------------------------------------------------ #
    # --limit and --offset forwarded to API                               #
    # ------------------------------------------------------------------ #
    @patch("purviewcli.client._search.Search")
    def test_list_limit_and_offset(self, mock_search_cls):
        mock_client = MagicMock()
        mock_search_cls.return_value = mock_client
        mock_client.searchQuery.return_value = MOCK_SEARCH_RESPONSE

        result = _invoke(
            "entity", "list",
            "--collection-id", "pp3hth",
            "--limit", "200",
            "--offset", "50",
        )
        assert result.exit_code == 0, result.output

        payload = json.loads(mock_client.searchQuery.call_args[0][0]["--payload"])
        assert payload["limit"] == 200
        assert payload["offset"] == 50

    # ------------------------------------------------------------------ #
    # Empty collection                                                     #
    # ------------------------------------------------------------------ #
    @patch("purviewcli.client._search.Search")
    def test_list_empty_collection(self, mock_search_cls):
        mock_client = MagicMock()
        mock_search_cls.return_value = mock_client
        mock_client.searchQuery.return_value = MOCK_EMPTY_RESPONSE

        result = _invoke("entity", "list", "--collection-id", "empty-coll")
        assert result.exit_code == 0, result.output
        assert "No entities found" in result.output

    # ------------------------------------------------------------------ #
    # --show-qualified-name adds extra column                             #
    # ------------------------------------------------------------------ #
    @patch("purviewcli.client._search.Search")
    def test_list_show_qualified_name(self, mock_search_cls):
        mock_client = MagicMock()
        mock_search_cls.return_value = mock_client
        mock_client.searchQuery.return_value = MOCK_SEARCH_RESPONSE

        result = _invoke("entity", "list", "--show-qualified-name")
        # The flag must not crash the command; table content renders regardless
        assert result.exit_code == 0, result.output
        # Core identifiers always appear (GUID and name are left-most columns)
        assert "aaaa0000" in result.output
        assert "SalesTable" in result.output

    # ------------------------------------------------------------------ #
    # Help text exposed correctly                                          #
    # ------------------------------------------------------------------ #
    def test_list_help(self):
        result = _invoke("entity", "list", "--help")
        assert result.exit_code == 0
        assert "--collection-id" in result.output
        assert "--guid" in result.output
        assert "--limit" in result.output
        assert "--output" in result.output

