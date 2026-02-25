"""Unit tests for scripts/copy_data_products.py"""

import argparse
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scripts.copy_data_products import build_parser, copy_data_products

SAMPLE_DATA_PRODUCT = {
    "typeName": "DataProduct",
    "status": "ACTIVE",
    "attributes": {
        "qualifiedName": "dataproduct://MyProduct",
        "name": "MyProduct",
        "displayName": "My Product",
    },
    "contacts": {
        "Expert": [{"id": "user-obj-id-1", "info": "expert"}],
        "Owner":  [{"id": "user-obj-id-2", "info": "owner"}],
    },
    "labels": ["dp-label"],
    "businessMetadata": {},
}

SAMPLE_SQL_TABLE = {
    "typeName": "azure_sql_table",
    "status": "ACTIVE",
    "attributes": {
        "qualifiedName": "mssql://server/db/schema/table",
        "name": "table",
    },
}


def _make_args(**kwargs):
    defaults = dict(
        guids_file="fake.txt",
        collection_id="target-collection",
        qualified_name_suffix="-copy",
        name_suffix="-copy",
        copy_asset_links=False,
        skip_classifications=False,
        skip_business_metadata=False,
        skip_labels=False,
        throttle_ms=0,
        dry_run=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _make_entity_mock(entity_obj):
    mock = MagicMock()
    mock.entityRead.return_value = {"entity": entity_obj}
    mock.entityCreate.return_value = {"guidAssignments": {"-1": "new-dp-guid"}}
    mock.entityMoveToCollection.return_value = {}
    mock.entityReadClassifications.return_value = {"classifications": []}
    mock.entityCreateClassifications.return_value = {}
    mock.entityCreateLabels.return_value = {}
    mock.entityAddOrUpdateBusinessMetadata.return_value = {}
    return mock


class TestBuildParser(unittest.TestCase):

    def test_required_args(self):
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([])

    def test_minimal_valid_args(self):
        parser = build_parser()
        args = parser.parse_args([
            "--guids-file", "guids.txt",
            "--collection-id", "col1",
        ])
        self.assertEqual(args.qualified_name_suffix, "-copy")
        self.assertFalse(args.dry_run)
        self.assertFalse(args.copy_asset_links)

    def test_all_flags(self):
        parser = build_parser()
        args = parser.parse_args([
            "--guids-file", "guids.txt",
            "--collection-id", "col1",
            "--name-suffix=v2",
            "--copy-asset-links",
            "--skip-classifications",
            "--skip-business-metadata",
            "--skip-labels",
            "--dry-run",
        ])
        self.assertTrue(args.copy_asset_links)
        self.assertTrue(args.skip_classifications)
        self.assertEqual(args.name_suffix, "v2")


class TestCopyDataProducts(unittest.TestCase):

    @patch("scripts.copy_data_products.Relationship")
    @patch("scripts.copy_data_products.Entity")
    def test_data_product_copied(self, MockEntity, MockRelationship):
        MockEntity.return_value = _make_entity_mock(SAMPLE_DATA_PRODUCT)

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("dp-guid-001\n")
            guids_file = f.name

        try:
            rc = copy_data_products(_make_args(guids_file=guids_file))
        finally:
            os.remove(guids_file)

        self.assertEqual(rc, 0)
        MockEntity.return_value.entityCreate.assert_called_once()
        MockEntity.return_value.entityMoveToCollection.assert_called_once()

    @patch("scripts.copy_data_products.Relationship")
    @patch("scripts.copy_data_products.Entity")
    def test_non_data_product_is_skipped(self, MockEntity, MockRelationship):
        MockEntity.return_value = _make_entity_mock(SAMPLE_SQL_TABLE)

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("sql-guid-001\n")
            guids_file = f.name

        try:
            rc = copy_data_products(_make_args(guids_file=guids_file))
        finally:
            os.remove(guids_file)

        # No error, but nothing created
        self.assertEqual(rc, 0)
        MockEntity.return_value.entityCreate.assert_not_called()

    @patch("scripts.copy_data_products.Relationship")
    @patch("scripts.copy_data_products.Entity")
    def test_dry_run_no_writes(self, MockEntity, MockRelationship):
        MockEntity.return_value = _make_entity_mock(SAMPLE_DATA_PRODUCT)

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("dp-guid-001\n")
            guids_file = f.name

        try:
            rc = copy_data_products(_make_args(guids_file=guids_file, dry_run=True))
        finally:
            os.remove(guids_file)

        self.assertEqual(rc, 0)
        MockEntity.return_value.entityCreate.assert_not_called()
        MockEntity.return_value.entityMoveToCollection.assert_not_called()

    @patch("scripts.copy_data_products.Relationship")
    @patch("scripts.copy_data_products.Entity")
    def test_mixed_guids_only_dp_copied(self, MockEntity, MockRelationship):
        """When the file has mixed types, only DataProducts are copied."""
        # entityRead is called ONCE per GUID (prefetched_entity avoids double call)
        side_effects = [
            {"entity": SAMPLE_DATA_PRODUCT},  # guid-1 peek → DataProduct, used as prefetched
            {"entity": SAMPLE_SQL_TABLE},      # guid-2 peek → skipped
            {"entity": SAMPLE_DATA_PRODUCT},  # guid-3 peek → DataProduct, used as prefetched
        ]
        mock = MagicMock()
        mock.entityRead.side_effect = side_effects
        mock.entityCreate.return_value = {"guidAssignments": {"-1": "new-guid"}}
        mock.entityMoveToCollection.return_value = {}
        mock.entityReadClassifications.return_value = {"classifications": []}
        mock.entityCreateClassifications.return_value = {}
        mock.entityCreateLabels.return_value = {}
        mock.entityAddOrUpdateBusinessMetadata.return_value = {}
        MockEntity.return_value = mock

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("guid-1\nguid-2\nguid-3\n")
            guids_file = f.name

        try:
            rc = copy_data_products(_make_args(guids_file=guids_file))
        finally:
            os.remove(guids_file)

        self.assertEqual(rc, 0)
        # entityCreate called only for guid-1 and guid-3 (2 DataProducts)
        self.assertEqual(mock.entityCreate.call_count, 2)

    @patch("scripts.copy_data_products.Relationship")
    @patch("scripts.copy_data_products.Entity")
    def test_api_error_reported_continues(self, MockEntity, MockRelationship):
        mock = MagicMock()
        mock.entityRead.side_effect = RuntimeError("API down")
        MockEntity.return_value = mock

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("guid-1\nguid-2\n")
            guids_file = f.name

        try:
            rc = copy_data_products(_make_args(guids_file=guids_file))
        finally:
            os.remove(guids_file)

        self.assertEqual(rc, 1)
        self.assertEqual(mock.entityRead.call_count, 2)

    @patch("scripts.copy_data_products._copy_relationships")
    @patch("scripts.copy_data_products.Relationship")
    @patch("scripts.copy_data_products.Entity")
    def test_copy_asset_links_calls_relationships(self, MockEntity, MockRelationship, mock_copy_rel):
        MockEntity.return_value = _make_entity_mock(SAMPLE_DATA_PRODUCT)

        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("dp-guid-001\n")
            guids_file = f.name

        try:
            rc = copy_data_products(_make_args(guids_file=guids_file, copy_asset_links=True))
        finally:
            os.remove(guids_file)

        self.assertEqual(rc, 0)
        mock_copy_rel.assert_called_once()
        # clone_related must be False — assets are re-linked, not duplicated
        call_kwargs = mock_copy_rel.call_args[1]
        self.assertFalse(call_kwargs.get("clone_related", True))

    @patch("scripts.copy_data_products.Relationship")
    @patch("scripts.copy_data_products.Entity")
    def test_no_asset_links_by_default(self, MockEntity, MockRelationship):
        MockEntity.return_value = _make_entity_mock(SAMPLE_DATA_PRODUCT)

        with patch("scripts.copy_data_products._copy_relationships") as mock_rel:
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
                f.write("dp-guid-001\n")
                guids_file = f.name

            try:
                copy_data_products(_make_args(guids_file=guids_file))
            finally:
                os.remove(guids_file)

            mock_rel.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
