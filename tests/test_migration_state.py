# SPDX-License-Identifier: Apache-2.0
"""Tests for purviewcli.migration.models and purviewcli.migration.state."""

import json
import os
import tempfile

import pytest

from purviewcli.migration.models import (
    AssetMatch,
    CheckpointRecord,
    MappingEntry,
    MappingValidationError,
    MatchOutcome,
    MigrationMapping,
    OperationStatus,
    OperationType,
    RunCheckpoint,
)
from purviewcli.migration.state import (
    CheckpointStore,
    compute_fingerprint,
    new_run_id,
)


# ---------------------------------------------------------------------------
# models.py
# ---------------------------------------------------------------------------


class TestMigrationMapping:
    def test_valid_mapping_builds_lookup(self):
        mapping = MigrationMapping(
            entries=[
                MappingEntry(purview_asset_id="a1", workspace_id="ws1", item_id="it1"),
                MappingEntry(purview_asset_id="a2", workspace_id="ws1", item_id="it2"),
            ]
        )
        by_source = mapping.by_purview_asset_id()
        assert by_source["a1"].item_id == "it1"
        assert by_source["a2"].item_id == "it2"

    def test_duplicate_source_binding_rejected(self):
        with pytest.raises(MappingValidationError, match="Duplicate purviewAssetId"):
            MigrationMapping(
                entries=[
                    MappingEntry(purview_asset_id="a1", workspace_id="ws1", item_id="it1"),
                    MappingEntry(purview_asset_id="a1", workspace_id="ws2", item_id="it2"),
                ]
            )

    def test_duplicate_target_binding_rejected(self):
        with pytest.raises(MappingValidationError, match="Duplicate Fabric target"):
            MigrationMapping(
                entries=[
                    MappingEntry(purview_asset_id="a1", workspace_id="ws1", item_id="it1"),
                    MappingEntry(purview_asset_id="a2", workspace_id="ws1", item_id="it1"),
                ]
            )

    def test_missing_field_rejected(self):
        with pytest.raises(MappingValidationError):
            MigrationMapping(entries=[MappingEntry(purview_asset_id="", workspace_id="ws1", item_id="it1")])

    def test_from_dict_round_trip(self):
        data = {
            "mappings": [
                {"purviewAssetId": "a1", "workspaceId": "ws1", "itemId": "it1", "note": "manual"},
            ]
        }
        mapping = MigrationMapping.from_dict(data)
        assert mapping.entries[0].note == "manual"


class TestAssetMatch:
    @pytest.mark.parametrize(
        "outcome,expected",
        [
            (MatchOutcome.MATCHED_BY_ID, True),
            (MatchOutcome.MATCHED_BY_MAPPING, True),
            (MatchOutcome.UNMATCHED, False),
            (MatchOutcome.INVALID_MAPPING, False),
            (MatchOutcome.TARGET_NOT_FOUND, False),
        ],
    )
    def test_is_writable(self, outcome, expected):
        match = AssetMatch(purview_asset_id="a1", outcome=outcome)
        assert match.is_writable() is expected

    def test_to_dict_serializes_enum_as_plain_string(self):
        match = AssetMatch(purview_asset_id="a1", outcome=MatchOutcome.MATCHED_BY_ID)
        as_dict = match.to_dict()
        assert as_dict["outcome"] == "matched_by_id"
        # Must be JSON-serializable without a custom encoder.
        json.dumps(as_dict)


class TestCheckpointRecordRoundTrip:
    def test_to_dict_and_from_dict(self):
        record = CheckpointRecord(
            operation_id="op-1",
            operation_type=OperationType.UPDATE_ITEM,
            run_id="run-1",
            applied_at="2024-01-01T00:00:00Z",
            fingerprint="abc123",
            target={"workspaceId": "ws1", "itemId": "it1"},
            before_state={"description": "old"},
            after_state={"description": "new"},
            purview_source_id="a1",
        )
        restored = CheckpointRecord.from_dict(json.loads(json.dumps(record.to_dict())))
        assert restored.operation_type == OperationType.UPDATE_ITEM
        assert restored.target == {"workspaceId": "ws1", "itemId": "it1"}
        assert restored.fingerprint == "abc123"


# ---------------------------------------------------------------------------
# state.py
# ---------------------------------------------------------------------------


class TestFingerprint:
    def test_deterministic_regardless_of_key_order(self):
        a = compute_fingerprint({"description": "x", "displayName": "y"})
        b = compute_fingerprint({"displayName": "y", "description": "x"})
        assert a == b

    def test_changes_when_value_changes(self):
        a = compute_fingerprint({"description": "x"})
        b = compute_fingerprint({"description": "y"})
        assert a != b

    def test_nested_structures_are_stable(self):
        a = compute_fingerprint({"tags": ["b", "a"], "meta": {"k": 1}})
        b = compute_fingerprint({"meta": {"k": 1}, "tags": ["b", "a"]})
        assert a == b


class TestNewRunId:
    def test_format(self):
        run_id = new_run_id()
        assert run_id.startswith("run-")
        parts = run_id.split("-")
        assert len(parts) == 3
        assert len(parts[2]) == 8

    def test_unique_across_calls(self):
        ids = {new_run_id() for _ in range(20)}
        assert len(ids) == 20


@pytest.fixture
def checkpoint_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield os.path.join(tmp_dir, "nested", "checkpoint.json")


class TestCheckpointStore:
    def test_load_returns_none_when_missing(self, checkpoint_path):
        store = CheckpointStore(checkpoint_path)
        assert store.load() is None

    def test_load_or_create_creates_new_checkpoint(self, checkpoint_path):
        store = CheckpointStore(checkpoint_path)
        checkpoint = store.load_or_create("run-1")
        assert checkpoint.run_id == "run-1"
        assert checkpoint.records == []
        # Nothing written to disk yet until an operation is recorded or saved.
        assert not store.exists()

    def test_save_then_load_round_trips(self, checkpoint_path):
        store = CheckpointStore(checkpoint_path)
        checkpoint = store.load_or_create("run-1")
        store.save(checkpoint)

        reloaded_store = CheckpointStore(checkpoint_path)
        reloaded = reloaded_store.load()
        assert reloaded is not None
        assert reloaded.run_id == "run-1"

    def test_load_or_create_rejects_mismatched_run_id(self, checkpoint_path):
        store = CheckpointStore(checkpoint_path)
        store.save(store.load_or_create("run-1"))

        with pytest.raises(ValueError, match="belongs to run"):
            CheckpointStore(checkpoint_path).load_or_create("run-2")

    def test_record_operation_persists_immediately(self, checkpoint_path):
        store = CheckpointStore(checkpoint_path)
        checkpoint = store.load_or_create("run-1")
        record = CheckpointRecord(
            operation_id="op-1",
            operation_type=OperationType.UPDATE_ITEM,
            run_id="run-1",
            applied_at="2024-01-01T00:00:00Z",
            fingerprint="fp-1",
        )
        store.record_operation(checkpoint, record)

        reloaded = CheckpointStore(checkpoint_path).load()
        assert reloaded is not None
        assert len(reloaded.records) == 1
        assert reloaded.records[0].operation_id == "op-1"

    def test_record_operation_replaces_existing_operation_id(self, checkpoint_path):
        store = CheckpointStore(checkpoint_path)
        checkpoint = store.load_or_create("run-1")
        store.record_operation(
            checkpoint,
            CheckpointRecord(
                operation_id="op-1",
                operation_type=OperationType.UPDATE_ITEM,
                run_id="run-1",
                applied_at="2024-01-01T00:00:00Z",
                fingerprint="fp-1",
            ),
        )
        store.record_operation(
            checkpoint,
            CheckpointRecord(
                operation_id="op-1",
                operation_type=OperationType.UPDATE_ITEM,
                run_id="run-1",
                applied_at="2024-01-02T00:00:00Z",
                fingerprint="fp-2",
            ),
        )
        assert len(checkpoint.records) == 1
        assert checkpoint.records[0].fingerprint == "fp-2"

    def test_has_applied_true_on_fingerprint_match(self, checkpoint_path):
        checkpoint = RunCheckpoint(
            run_id="run-1",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            records=[
                CheckpointRecord(
                    operation_id="op-1",
                    operation_type=OperationType.UPDATE_ITEM,
                    run_id="run-1",
                    applied_at="2024-01-01T00:00:00Z",
                    fingerprint="fp-1",
                )
            ],
        )
        assert CheckpointStore.has_applied(checkpoint, "op-1", "fp-1") is True

    def test_has_applied_false_when_fingerprint_changed(self, checkpoint_path):
        checkpoint = RunCheckpoint(
            run_id="run-1",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            records=[
                CheckpointRecord(
                    operation_id="op-1",
                    operation_type=OperationType.UPDATE_ITEM,
                    run_id="run-1",
                    applied_at="2024-01-01T00:00:00Z",
                    fingerprint="fp-1",
                )
            ],
        )
        assert CheckpointStore.has_applied(checkpoint, "op-1", "fp-2") is False

    def test_has_applied_false_when_operation_unknown(self, checkpoint_path):
        checkpoint = RunCheckpoint(run_id="run-1", created_at="t", updated_at="t", records=[])
        assert CheckpointStore.has_applied(checkpoint, "op-missing", "fp-1") is False

    def test_atomic_write_leaves_no_temp_files_on_success(self, checkpoint_path):
        store = CheckpointStore(checkpoint_path)
        store.save(store.load_or_create("run-1"))
        directory = os.path.dirname(checkpoint_path)
        leftovers = [f for f in os.listdir(directory) if f.startswith(".tmp-")]
        assert leftovers == []
