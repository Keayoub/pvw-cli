# SPDX-License-Identifier: Apache-2.0
"""
Tests for the two bugs fixed in `pvw collections resources`:

1. --asset-type now sends an {"and": [...]} compound filter to the Search API
   instead of a flat dict that caused assets from the wrong collection to be returned.

2. --collection-name now resolves against the collection's `friendlyName` field
   in addition to its technical `name` field.
"""

import json
import os
import sys
from unittest.mock import MagicMock, call, patch

import pytest
from click.testing import CliRunner

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.cli.cli import main

RUNNER = CliRunner()


def invoke(*args, **kwargs):
    return RUNNER.invoke(main, list(args), catch_exceptions=False, **kwargs)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

COLLECTIONS_RESPONSE = {
    "value": [
        {"name": "col1", "friendlyName": "My First Collection"},
        {"name": "col2", "friendlyName": "My Second Collection"},
    ]
}

ASSET_FABRIC_TABLE = {
    "id": "aaaa-1111",
    "name": "Drivers",
    "entityType": "fabric_lakehouse_table",
    "assetType": ["Fabric"],
    "qualifiedName": "https://app.fabric.microsoft.com/groups/xxx/Drivers",
}

ASSET_POWERBI = {
    "id": "bbbb-2222",
    "name": "peakon_verification",
    "entityType": "powerbi_report",
    "assetType": ["Power BI"],
    "qualifiedName": "Power BI/peakon_verification",
}


# ---------------------------------------------------------------------------
# Bug 1: compound AND filter for --asset-type
# ---------------------------------------------------------------------------


class TestAssetTypeFilterUsesAndSyntax:
    """The Search API requires {"and": [...]} for compound filters.
    Sending a flat dict {"collectionId": "x", "entityType": "y"} caused the
    collectionId restriction to be ignored, returning assets from all collections.
    """

    @patch("purviewcli.cli.collections.Collections")
    @patch("purviewcli.client._search.Search")
    def test_no_asset_type_sends_plain_collectionid_filter(
        self, mock_search_cls, mock_collections_cls
    ):
        """Without --asset-type the filter stays a simple {"collectionId": "..."} dict."""
        mock_collections = MagicMock()
        mock_collections_cls.return_value = mock_collections
        mock_collections.collectionsRead.return_value = COLLECTIONS_RESPONSE

        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search
        mock_search.searchQuery.return_value = {"value": [ASSET_FABRIC_TABLE]}

        result = invoke("collections", "resources", "--collection-name", "col1", "--format", "json")

        assert result.exit_code == 0, result.output
        mock_search.searchQuery.assert_called_once()
        call_args = mock_search.searchQuery.call_args[0][0]
        sent_filter = json.loads(call_args["--filter"])

        # Must be a plain dict, not wrapped in "and"
        assert "and" not in sent_filter
        assert sent_filter.get("collectionId") == "col1"

    @patch("purviewcli.cli.collections.Collections")
    @patch("purviewcli.client._search.Search")
    def test_with_asset_type_sends_and_compound_filter(
        self, mock_search_cls, mock_collections_cls
    ):
        """With --asset-type the filter must use {"and": [{collectionId}, {entityType}]}."""
        mock_collections = MagicMock()
        mock_collections_cls.return_value = mock_collections
        mock_collections.collectionsRead.return_value = COLLECTIONS_RESPONSE

        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search
        mock_search.searchQuery.return_value = {"value": [ASSET_FABRIC_TABLE]}

        result = invoke(
            "collections",
            "resources",
            "--collection-name",
            "col1",
            "--asset-type",
            "fabric_lakehouse_table",
            "--format",
            "json",
        )

        assert result.exit_code == 0, result.output
        mock_search.searchQuery.assert_called_once()
        call_args = mock_search.searchQuery.call_args[0][0]
        sent_filter = json.loads(call_args["--filter"])

        # MUST use the compound AND syntax
        assert "and" in sent_filter, (
            "Expected {'and': [...]} compound filter but got: " + json.dumps(sent_filter)
        )
        conditions = sent_filter["and"]
        assert isinstance(conditions, list) and len(conditions) == 2

        coll_condition = next((c for c in conditions if "collectionId" in c), None)
        type_condition = next((c for c in conditions if "entityType" in c), None)

        assert coll_condition is not None, "Missing collectionId condition"
        assert type_condition is not None, "Missing entityType condition"
        assert coll_condition["collectionId"] == "col1"
        assert type_condition["entityType"] == "fabric_lakehouse_table"

    @patch("purviewcli.cli.collections.Collections")
    @patch("purviewcli.client._search.Search")
    def test_flat_filter_is_NOT_sent_when_asset_type_given(
        self, mock_search_cls, mock_collections_cls
    ):
        """Regression: the old broken form {"collectionId": x, "entityType": y} must not appear."""
        mock_collections = MagicMock()
        mock_collections_cls.return_value = mock_collections
        mock_collections.collectionsRead.return_value = COLLECTIONS_RESPONSE

        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search
        mock_search.searchQuery.return_value = {"value": []}

        invoke(
            "collections",
            "resources",
            "--collection-name",
            "col1",
            "--asset-type",
            "fabric_lakehouse_table",
        )

        call_args = mock_search.searchQuery.call_args[0][0]
        sent_filter = json.loads(call_args["--filter"])

        # The old broken flat form must NOT appear
        assert not (
            "collectionId" in sent_filter and "entityType" in sent_filter
        ), "Found old flat filter — collectionId+entityType must not be top-level siblings"

    @patch("purviewcli.cli.collections.Collections")
    @patch("purviewcli.client._search.Search")
    def test_asset_type_filter_only_fetches_matching_collection(
        self, mock_search_cls, mock_collections_cls
    ):
        """Only the targeted collection should be queried when --collection-name is given."""
        mock_collections = MagicMock()
        mock_collections_cls.return_value = mock_collections
        mock_collections.collectionsRead.return_value = COLLECTIONS_RESPONSE

        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search
        mock_search.searchQuery.return_value = {"value": [ASSET_FABRIC_TABLE]}

        invoke(
            "collections",
            "resources",
            "--collection-name",
            "col1",
            "--asset-type",
            "fabric_lakehouse_table",
        )

        # searchQuery called exactly once — only for col1, not col2
        assert mock_search.searchQuery.call_count == 1


# ---------------------------------------------------------------------------
# Bug 2: --collection-name resolves friendly name
# ---------------------------------------------------------------------------


class TestCollectionNameFriendlyNameResolution:
    """--collection-name should match either the technical 'name' or 'friendlyName'."""

    @patch("purviewcli.cli.collections.Collections")
    @patch("purviewcli.client._search.Search")
    def test_technical_name_still_works(self, mock_search_cls, mock_collections_cls):
        """Existing behaviour: match by technical short-id is preserved."""
        mock_collections = MagicMock()
        mock_collections_cls.return_value = mock_collections
        mock_collections.collectionsRead.return_value = COLLECTIONS_RESPONSE

        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search
        mock_search.searchQuery.return_value = {"value": [ASSET_FABRIC_TABLE]}

        result = invoke("collections", "resources", "--collection-name", "col2", "--format", "json")

        assert result.exit_code == 0, result.output
        assert mock_search.searchQuery.call_count == 1
        call_args = mock_search.searchQuery.call_args[0][0]
        sent_filter = json.loads(call_args["--filter"])
        assert sent_filter.get("collectionId") == "col2"

    @patch("purviewcli.cli.collections.Collections")
    @patch("purviewcli.client._search.Search")
    def test_friendly_name_is_resolved_to_technical_name(
        self, mock_search_cls, mock_collections_cls
    ):
        """New behaviour: passing the friendly name must find and query the correct collection."""
        mock_collections = MagicMock()
        mock_collections_cls.return_value = mock_collections
        mock_collections.collectionsRead.return_value = COLLECTIONS_RESPONSE

        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search
        mock_search.searchQuery.return_value = {"value": [ASSET_POWERBI]}

        result = invoke(
            "collections",
            "resources",
            "--collection-name",
            "My Second Collection",  # friendly name, not technical "col2"
            "--format",
            "json",
        )

        assert result.exit_code == 0, result.output
        # Must have queried exactly one collection
        assert mock_search.searchQuery.call_count == 1
        call_args = mock_search.searchQuery.call_args[0][0]
        sent_filter = json.loads(call_args["--filter"])
        # And the filter must use the TECHNICAL name "col2", not the friendly name
        assert sent_filter.get("collectionId") == "col2", (
            f"Expected collectionId='col2' but got '{sent_filter.get('collectionId')}'"
        )

    @patch("purviewcli.cli.collections.Collections")
    @patch("purviewcli.client._search.Search")
    def test_unknown_name_prints_warning_and_returns(
        self, mock_search_cls, mock_collections_cls
    ):
        """An unrecognised collection name must emit a warning and NOT call the Search API."""
        mock_collections = MagicMock()
        mock_collections_cls.return_value = mock_collections
        mock_collections.collectionsRead.return_value = COLLECTIONS_RESPONSE

        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search

        result = invoke(
            "collections", "resources", "--collection-name", "does-not-exist"
        )

        assert result.exit_code == 0, result.output
        mock_search.searchQuery.assert_not_called()

    @patch("purviewcli.cli.collections.Collections")
    @patch("purviewcli.client._search.Search")
    def test_no_collection_name_queries_all_collections(
        self, mock_search_cls, mock_collections_cls
    ):
        """Without --collection-name every collection in the account is queried."""
        mock_collections = MagicMock()
        mock_collections_cls.return_value = mock_collections
        mock_collections.collectionsRead.return_value = COLLECTIONS_RESPONSE

        mock_search = MagicMock()
        mock_search_cls.return_value = mock_search
        mock_search.searchQuery.return_value = {"value": []}

        invoke("collections", "resources")

        # Two collections in the fixture -> two Search API calls
        assert mock_search.searchQuery.call_count == 2
