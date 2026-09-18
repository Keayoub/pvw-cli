# SPDX-License-Identifier: Apache-2.0
"""Tests for purviewcli.migration.execution (apply + rollback)."""

import os
import tempfile

import pytest

from purviewcli.migration.execution import (
    apply_operations,
    apply_rollback,
    build_domain_operations,
    build_item_metadata_operations,
    build_item_tag_operations,
    build_planned_operations,
    build_rollback_operations,
    build_tag_definition_operations,
)
from purviewcli.migration.models import (
    DomainAction,
    DomainPlan,
    FieldChange,
    ItemDecision,
    ItemPlan,
    ItemTagPlan,
    OperationStatus,
    OperationType,
    TagDecision,
    WorkspaceDomainAssignmentPlan,
)
from purviewcli.migration.state import CheckpointStore, compute_fingerprint


# ---------------------------------------------------------------------------
# Fake client
# ---------------------------------------------------------------------------


class FakeFabricClient:
    """A minimal in-memory stand-in for FabricClient's mutation surface."""

    def __init__(self, fail_operations=None):
        self.fail_operations = fail_operations or set()
        self.updated_items = []
        self.created_domains = []
        self.assigned = []
        self.unassigned = []
        self.created_tags = []
        self.applied_tags = []
        self.unapplied_tags = []
        self._next_domain_id = 1

    def update_item(self, workspace_id, item_id, display_name=None, description=None):
        if "update_item" in self.fail_operations:
            raise RuntimeError("simulated failure")
        fields = {}
        if display_name is not None:
            fields["display_name"] = display_name
        if description is not None:
            fields["description"] = description
        self.updated_items.append((workspace_id, item_id, fields))
        return {}

    def create_domain(self, display_name, description=None):
        if "create_domain" in self.fail_operations:
            raise RuntimeError("simulated failure")
        domain_id = f"fd-{self._next_domain_id}"
        self._next_domain_id += 1
        self.created_domains.append(display_name)
        return {"id": domain_id, "displayName": display_name}

    def assign_domain_workspaces(self, domain_id, workspace_ids):
        if "assign_domain_workspaces" in self.fail_operations:
            raise RuntimeError("simulated failure")
        self.assigned.append((domain_id, workspace_ids))

    def unassign_domain_workspaces(self, domain_id, workspace_ids):
        self.unassigned.append((domain_id, workspace_ids))

    def bulk_create_tags(self, display_names):
        if "bulk_create_tags" in self.fail_operations:
            raise RuntimeError("simulated failure")
        result = [{"id": f"tag-{name}", "displayName": name} for name in display_names]
        self.created_tags.extend(display_names)
        return result

    def apply_tags(self, workspace_id, item_id, tag_ids):
        if "apply_tags" in self.fail_operations:
            raise RuntimeError("simulated failure")
        self.applied_tags.append((workspace_id, item_id, tag_ids))

    def unapply_tags(self, workspace_id, item_id, tag_ids):
        self.unapplied_tags.append((workspace_id, item_id, tag_ids))


@pytest.fixture
def checkpoint_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield os.path.join(tmp_dir, "checkpoint.json")


@pytest.fixture
def store_and_checkpoint(checkpoint_path):
    store = CheckpointStore(checkpoint_path)
    checkpoint = store.load_or_create("run-1")
    return store, checkpoint


# ---------------------------------------------------------------------------
# Building operations
# ---------------------------------------------------------------------------


class TestBuildOperations:
    def test_item_metadata_operations_only_for_ready_plans(self):
        ready = ItemPlan(
            purview_asset_id="a1",
            workspace_id="ws1",
            item_id="it1",
            decision=ItemDecision.READY,
            changes=[FieldChange(field="description", current=None, desired="new")],
        )
        no_change = ItemPlan(
            purview_asset_id="a2", workspace_id="ws1", item_id="it2", decision=ItemDecision.NO_CHANGE
        )
        conflict = ItemPlan(
            purview_asset_id="a3", workspace_id="ws1", item_id="it3", decision=ItemDecision.CONFLICT
        )
        ops = build_item_metadata_operations([ready, no_change, conflict])
        assert len(ops) == 1
        assert ops[0].operation_type == OperationType.UPDATE_ITEM
        assert ops[0].payload == {"description": "new"}

    def test_domain_operations_create_and_assign(self):
        domain_plan = DomainPlan(
            purview_domain_id="d1",
            fabric_domain_name="Finance",
            action=DomainAction.CREATE_DOMAIN,
            workspace_assignments=[
                WorkspaceDomainAssignmentPlan(
                    workspace_id="ws1",
                    current_domain_id=None,
                    desired_domain_id="",
                    action=DomainAction.ASSIGN_WORKSPACE,
                )
            ],
        )
        ops = build_domain_operations([domain_plan])
        types = [op.operation_type for op in ops]
        assert OperationType.CREATE_DOMAIN in types
        assert OperationType.ASSIGN_WORKSPACE_DOMAIN in types

    def test_domain_operations_skip_conflicts_and_no_change(self):
        domain_plan = DomainPlan(
            purview_domain_id="d1",
            fabric_domain_name="Finance",
            fabric_domain_id="fd1",
            action=DomainAction.NO_CHANGE,
            workspace_assignments=[
                WorkspaceDomainAssignmentPlan(
                    workspace_id="ws1",
                    current_domain_id="fd-other",
                    desired_domain_id="fd1",
                    action=DomainAction.WORKSPACE_CONFLICT,
                ),
                WorkspaceDomainAssignmentPlan(
                    workspace_id="ws2",
                    current_domain_id="fd1",
                    desired_domain_id="fd1",
                    action=DomainAction.NO_CHANGE,
                ),
            ],
        )
        ops = build_domain_operations([domain_plan])
        assert ops == []

    def test_tag_definition_operations_skip_existing(self):
        ops = build_tag_definition_operations(
            ["purview:term:A", "purview:term:B"], existing_tenant_tag_names=["purview:term:A"]
        )
        assert len(ops) == 1
        assert ops[0].payload == {"displayName": "purview:term:B"}

    def test_item_tag_operations_only_for_ready(self):
        ready = ItemTagPlan(
            workspace_id="ws1", item_id="it1", decision=TagDecision.READY, tags_to_apply=["purview:term:A"]
        )
        overflow = ItemTagPlan(
            workspace_id="ws1", item_id="it2", decision=TagDecision.TAG_OVERFLOW, overflow_tags=["purview:term:B"]
        )
        ops = build_item_tag_operations([ready, overflow])
        assert len(ops) == 1
        assert ops[0].payload == {"tagNames": ["purview:term:A"]}

    def test_build_planned_operations_orders_by_dependency(self):
        domain_plan = DomainPlan(
            purview_domain_id="d1",
            fabric_domain_name="Finance",
            action=DomainAction.CREATE_DOMAIN,
            workspace_assignments=[],
        )
        item_plan = ItemPlan(
            purview_asset_id="a1",
            workspace_id="ws1",
            item_id="it1",
            decision=ItemDecision.READY,
            changes=[FieldChange(field="description", current=None, desired="new")],
        )
        tag_plan = ItemTagPlan(
            workspace_id="ws1", item_id="it1", decision=TagDecision.READY, tags_to_apply=["purview:term:A"]
        )
        ops = build_planned_operations(
            item_plans=[item_plan],
            domain_plans=[domain_plan],
            tag_plans=[tag_plan],
            desired_governance_tag_names=["purview:term:A"],
            existing_tenant_tag_names=[],
        )
        types_in_order = [op.operation_type for op in ops]
        assert types_in_order.index(OperationType.CREATE_DOMAIN) < types_in_order.index(
            OperationType.CREATE_TAG
        )
        assert types_in_order.index(OperationType.CREATE_TAG) < types_in_order.index(
            OperationType.APPLY_ITEM_TAGS
        )
        assert types_in_order.index(OperationType.APPLY_ITEM_TAGS) < types_in_order.index(
            OperationType.UPDATE_ITEM
        )


# ---------------------------------------------------------------------------
# Applying operations
# ---------------------------------------------------------------------------


class TestApplyOperations:
    def _update_item_op(self, workspace_id="ws1", item_id="it1", desired="new desc"):
        from purviewcli.migration.models import PlannedOperation

        payload = {"description": desired}
        return PlannedOperation(
            operation_id=f"item:update:{workspace_id}:{item_id}",
            operation_type=OperationType.UPDATE_ITEM,
            fingerprint=compute_fingerprint(payload),
            target={"workspaceId": workspace_id, "itemId": item_id},
            payload=payload,
            before_state={"description": None},
        )

    def test_dry_run_never_calls_client(self, store_and_checkpoint):
        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        result = apply_operations(client, [self._update_item_op()], store, checkpoint, dry_run=True)
        assert result.dry_run is True
        assert result.results[0].status == OperationStatus.SKIPPED_DRY_RUN
        assert client.updated_items == []
        assert not store.exists()

    def test_apply_updates_item_and_checkpoints(self, store_and_checkpoint):
        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        result = apply_operations(client, [self._update_item_op()], store, checkpoint, dry_run=False)
        assert result.succeeded_count == 1
        assert client.updated_items == [("ws1", "it1", {"description": "new desc"})]
        reloaded = store.load()
        assert len(reloaded.records) == 1

    def test_resume_skips_matching_fingerprint(self, store_and_checkpoint):
        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        op = self._update_item_op()
        apply_operations(client, [op], store, checkpoint, dry_run=False)

        # Simulate a fresh run against the same checkpoint: same op, same fingerprint.
        client2 = FakeFabricClient()
        result2 = apply_operations(client2, [op], store, checkpoint, dry_run=False)
        assert result2.results[0].status == OperationStatus.SKIPPED_NO_CHANGE
        assert client2.updated_items == []

    def test_reapplies_when_fingerprint_changed(self, store_and_checkpoint):
        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        op_v1 = self._update_item_op(desired="version 1")
        apply_operations(client, [op_v1], store, checkpoint, dry_run=False)

        op_v2 = self._update_item_op(desired="version 2")  # same operation_id, new fingerprint
        result = apply_operations(client, [op_v2], store, checkpoint, dry_run=False)
        assert result.results[0].status == OperationStatus.APPLIED
        assert client.updated_items[-1] == ("ws1", "it1", {"description": "version 2"})

    def test_failure_is_isolated_and_run_continues(self, store_and_checkpoint):
        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient(fail_operations={"update_item"})
        ops = [self._update_item_op(item_id="it1"), self._update_item_op(item_id="it2")]
        result = apply_operations(client, ops, store, checkpoint, dry_run=False)
        assert result.failed_count == 2
        assert all(r.status == OperationStatus.FAILED for r in result.results)
        # Checkpoint file should not exist since nothing succeeded.
        assert store.load() is None

    def test_domain_creation_resolves_id_for_dependent_assignment(self, store_and_checkpoint):
        from purviewcli.migration.models import PlannedOperation

        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        create_op = PlannedOperation(
            operation_id="domain:create:d1",
            operation_type=OperationType.CREATE_DOMAIN,
            fingerprint=compute_fingerprint({"displayName": "Finance"}),
            target={"purviewDomainId": "d1"},
            payload={"displayName": "Finance"},
        )
        assign_op = PlannedOperation(
            operation_id="domain:assign:d1:ws1",
            operation_type=OperationType.ASSIGN_WORKSPACE_DOMAIN,
            fingerprint=compute_fingerprint({"purviewDomainId": "d1", "workspaceId": "ws1"}),
            target={"purviewDomainId": "d1", "workspaceId": "ws1"},
            payload={},
        )
        result = apply_operations(client, [create_op, assign_op], store, checkpoint, dry_run=False)
        assert result.succeeded_count == 2
        assert client.assigned == [("fd-1", ["ws1"])]

    def test_assignment_without_prior_domain_creation_fails_cleanly(self, store_and_checkpoint):
        from purviewcli.migration.models import PlannedOperation

        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        assign_op = PlannedOperation(
            operation_id="domain:assign:d1:ws1",
            operation_type=OperationType.ASSIGN_WORKSPACE_DOMAIN,
            fingerprint=compute_fingerprint({"purviewDomainId": "d1", "workspaceId": "ws1"}),
            target={"purviewDomainId": "d1", "workspaceId": "ws1"},
            payload={},
        )
        result = apply_operations(client, [assign_op], store, checkpoint, dry_run=False)
        assert result.failed_count == 1

    def test_tag_creation_resolves_id_for_dependent_apply(self, store_and_checkpoint):
        """CREATE_TAG's id must be resolved for a same-run APPLY_ITEM_TAGS by name."""
        from purviewcli.migration.models import PlannedOperation

        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        create_op = PlannedOperation(
            operation_id="tag:create:purview:term:A",
            operation_type=OperationType.CREATE_TAG,
            fingerprint=compute_fingerprint({"displayName": "purview:term:A"}),
            target={"tagName": "purview:term:A"},
            payload={"displayName": "purview:term:A"},
        )
        apply_op = PlannedOperation(
            operation_id="tags:apply:ws1:it1",
            operation_type=OperationType.APPLY_ITEM_TAGS,
            fingerprint=compute_fingerprint({"tagNames": ["purview:term:A"]}),
            target={"workspaceId": "ws1", "itemId": "it1"},
            payload={"tagNames": ["purview:term:A"]},
        )
        result = apply_operations(client, [create_op, apply_op], store, checkpoint, dry_run=False)
        assert result.succeeded_count == 2
        assert client.applied_tags == [("ws1", "it1", ["tag-purview:term:A"])]

    def test_apply_tags_resolves_via_preexisting_tag_ids(self, store_and_checkpoint):
        """A tag that already existed on the tenant (no CREATE_TAG in this run) still resolves."""
        from purviewcli.migration.models import PlannedOperation

        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        apply_op = PlannedOperation(
            operation_id="tags:apply:ws1:it1",
            operation_type=OperationType.APPLY_ITEM_TAGS,
            fingerprint=compute_fingerprint({"tagNames": ["purview:term:A"]}),
            target={"workspaceId": "ws1", "itemId": "it1"},
            payload={"tagNames": ["purview:term:A"]},
        )
        result = apply_operations(
            client,
            [apply_op],
            store,
            checkpoint,
            dry_run=False,
            existing_tag_ids_by_name={"purview:term:A": "existing-tag-1"},
        )
        assert result.succeeded_count == 1
        assert client.applied_tags == [("ws1", "it1", ["existing-tag-1"])]

    def test_apply_tags_without_resolvable_name_fails_cleanly(self, store_and_checkpoint):
        from purviewcli.migration.models import PlannedOperation

        store, checkpoint = store_and_checkpoint
        client = FakeFabricClient()
        apply_op = PlannedOperation(
            operation_id="tags:apply:ws1:it1",
            operation_type=OperationType.APPLY_ITEM_TAGS,
            fingerprint=compute_fingerprint({"tagNames": ["purview:term:A"]}),
            target={"workspaceId": "ws1", "itemId": "it1"},
            payload={"tagNames": ["purview:term:A"]},
        )
        result = apply_operations(client, [apply_op], store, checkpoint, dry_run=False)
        assert result.failed_count == 1
        assert client.applied_tags == []


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------


class TestRollback:
    def _checkpoint_with(self, records):
        from purviewcli.migration.models import RunCheckpoint

        return RunCheckpoint(run_id="run-1", created_at="t", updated_at="t", records=records)

    def test_rollback_reverses_item_update(self):
        from purviewcli.migration.models import CheckpointRecord

        checkpoint = self._checkpoint_with(
            [
                CheckpointRecord(
                    operation_id="item:update:ws1:it1",
                    operation_type=OperationType.UPDATE_ITEM,
                    run_id="run-1",
                    applied_at="t",
                    fingerprint="fp",
                    target={"workspaceId": "ws1", "itemId": "it1"},
                    before_state={"description": "old"},
                    after_state={"description": "new"},
                )
            ]
        )
        reverse_ops = build_rollback_operations(checkpoint)
        assert len(reverse_ops) == 1
        assert reverse_ops[0].operation_type == OperationType.UPDATE_ITEM
        assert reverse_ops[0].payload == {"description": "old"}

    def test_rollback_unassigns_domain(self):
        from purviewcli.migration.models import CheckpointRecord

        checkpoint = self._checkpoint_with(
            [
                CheckpointRecord(
                    operation_id="domain:assign:d1:ws1",
                    operation_type=OperationType.ASSIGN_WORKSPACE_DOMAIN,
                    run_id="run-1",
                    applied_at="t",
                    fingerprint="fp",
                    target={"purviewDomainId": "d1", "workspaceId": "ws1"},
                    after_state={"domainId": "fd-1"},
                )
            ]
        )
        reverse_ops = build_rollback_operations(checkpoint)
        assert reverse_ops[0].operation_type == OperationType.UNASSIGN_WORKSPACE_DOMAIN
        assert reverse_ops[0].payload == {"domainId": "fd-1"}

    def test_rollback_unapplies_only_run_owned_tags(self):
        from purviewcli.migration.models import CheckpointRecord

        checkpoint = self._checkpoint_with(
            [
                CheckpointRecord(
                    operation_id="tags:apply:ws1:it1",
                    operation_type=OperationType.APPLY_ITEM_TAGS,
                    run_id="run-1",
                    applied_at="t",
                    fingerprint="fp",
                    target={"workspaceId": "ws1", "itemId": "it1"},
                    before_state={"existingTagNames": ["custom-tag"]},
                    after_state={"appliedTags": ["tag-1", "tag-2"]},
                )
            ]
        )
        reverse_ops = build_rollback_operations(checkpoint)
        assert reverse_ops[0].operation_type == OperationType.UNAPPLY_ITEM_TAGS
        assert reverse_ops[0].payload == {"tagIds": ["tag-1", "tag-2"]}

    def test_rollback_never_touches_domain_or_tag_creation(self):
        from purviewcli.migration.models import CheckpointRecord

        checkpoint = self._checkpoint_with(
            [
                CheckpointRecord(
                    operation_id="domain:create:d1",
                    operation_type=OperationType.CREATE_DOMAIN,
                    run_id="run-1",
                    applied_at="t",
                    fingerprint="fp",
                ),
                CheckpointRecord(
                    operation_id="tag:create:purview:term:A",
                    operation_type=OperationType.CREATE_TAG,
                    run_id="run-1",
                    applied_at="t",
                    fingerprint="fp",
                ),
            ]
        )
        assert build_rollback_operations(checkpoint) == []

    def test_apply_rollback_dry_run(self):
        from purviewcli.migration.models import PlannedOperation

        client = FakeFabricClient()
        op = PlannedOperation(
            operation_id="rollback:item:update:ws1:it1",
            operation_type=OperationType.UPDATE_ITEM,
            fingerprint="fp",
            target={"workspaceId": "ws1", "itemId": "it1"},
            payload={"description": "old"},
        )
        result = apply_rollback(client, [op], dry_run=True)
        assert result.dry_run is True
        assert result.results[0].status == OperationStatus.SKIPPED_DRY_RUN
        assert client.updated_items == []

    def test_apply_rollback_executes_and_reports_failures(self):
        from purviewcli.migration.models import PlannedOperation

        client = FakeFabricClient(fail_operations={"update_item"})
        ops = [
            PlannedOperation(
                operation_id="rollback:item:update:ws1:it1",
                operation_type=OperationType.UPDATE_ITEM,
                fingerprint="fp",
                target={"workspaceId": "ws1", "itemId": "it1"},
                payload={"description": "old"},
            ),
            PlannedOperation(
                operation_id="rollback:tags:apply:ws1:it1",
                operation_type=OperationType.UNAPPLY_ITEM_TAGS,
                fingerprint="fp2",
                target={"workspaceId": "ws1", "itemId": "it1"},
                payload={"tagIds": ["tag-1"]},
            ),
        ]
        result = apply_rollback(client, ops, dry_run=False)
        statuses = {r.operation_id: r.status for r in result.results}
        assert statuses["rollback:item:update:ws1:it1"] == OperationStatus.FAILED
        assert statuses["rollback:tags:apply:ws1:it1"] == OperationStatus.ROLLED_BACK
        assert client.unapplied_tags == [("ws1", "it1", ["tag-1"])]
