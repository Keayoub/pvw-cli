# SPDX-License-Identifier: Apache-2.0
"""Dependency-ordered apply and rollback execution for the Fabric sync.

This module turns a :class:`~purviewcli.sync.models.SyncPlan`
into concrete, checkpointed :class:`~purviewcli.sync.models.PlannedOperation`
mutations, executes them against a Fabric client, and can later reverse a
completed run using only its checkpoint (never by re-deriving a plan).

Design notes:
  - Operations execute in a fixed dependency order (domains before
    workspace assignment before tags before item metadata) so that, e.g., a
    workspace's domain is correct before governance tags are applied.
  - Every successful mutation is checkpointed immediately (see
    :mod:`purviewcli.sync.state`), so partial failures never lose
    track of what already succeeded.
  - Domains and tag *definitions* created by a run are never deleted by
    rollback (Fabric policy the user approved); only item metadata,
    workspace-domain assignment, and run-owned item tags are reversed.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Protocol, Sequence

from .models import (
    DomainAction,
    DomainPlan,
    ItemDecision,
    ItemPlan,
    ItemTagPlan,
    OperationResult,
    OperationStatus,
    OperationType,
    PlannedOperation,
    RollbackResult,
    RunCheckpoint,
    SyncRunResult,
    TagDecision,
)
from .state import CheckpointStore, compute_fingerprint

logger = logging.getLogger(__name__)

#: Execution order for operation types: domains, then workspace assignment,
#: then tag definitions, then item tag application, then item metadata.
_EXECUTION_ORDER = {
    OperationType.CREATE_DOMAIN: 0,
    OperationType.ASSIGN_WORKSPACE_DOMAIN: 1,
    OperationType.CREATE_TAG: 2,
    OperationType.APPLY_ITEM_TAGS: 3,
    OperationType.UPDATE_ITEM: 4,
    # Rollback-only reverse operation types execute in the opposite order.
    OperationType.UNAPPLY_ITEM_TAGS: 0,
    OperationType.UNASSIGN_WORKSPACE_DOMAIN: 1,
}


#: Maps the Fabric REST field names used inside planned-operation payloads
#: ("displayName"/"description") onto FabricClient.update_item's snake_case
#: keyword arguments.
_UPDATE_ITEM_FIELD_MAP = {"displayName": "display_name", "description": "description"}


class FabricMutationClient(Protocol):
    """The subset of :class:`~purviewcli.client.fabric_client.FabricClient` used to apply mutations.

    Defined as a ``Protocol`` (structural typing) so tests can supply a
    lightweight fake without importing the real HTTP client.
    """

    def update_item(self, workspace_id: str, item_id: str, **fields: Any) -> Dict[str, Any]: ...

    def create_domain(self, display_name: str, description: Optional[str] = None) -> Dict[str, Any]: ...

    def assign_domain_workspaces(self, domain_id: str, workspace_ids: List[str]) -> None: ...

    def unassign_domain_workspaces(self, domain_id: str, workspace_ids: List[str]) -> None: ...

    def bulk_create_tags(self, display_names: List[str]) -> List[Dict[str, Any]]: ...

    def apply_tags(self, workspace_id: str, item_id: str, tag_ids: List[str]) -> None: ...

    def unapply_tags(self, workspace_id: str, item_id: str, tag_ids: List[str]) -> None: ...


# ---------------------------------------------------------------------------
# Building planned operations from a plan
# ---------------------------------------------------------------------------


def build_item_metadata_operations(item_plans: Sequence[ItemPlan]) -> List[PlannedOperation]:
    """Build ``UPDATE_ITEM`` operations for item plans in the ``ready`` state only."""
    operations: List[PlannedOperation] = []
    for plan in item_plans:
        if plan.decision != ItemDecision.READY:
            continue
        payload = {change.field: change.desired for change in plan.changes}
        before_state = {change.field: change.current for change in plan.changes}
        operations.append(
            PlannedOperation(
                operation_id=f"item:update:{plan.workspace_id}:{plan.item_id}",
                operation_type=OperationType.UPDATE_ITEM,
                fingerprint=compute_fingerprint(payload),
                purview_source_id=plan.purview_asset_id,
                target={"workspaceId": plan.workspace_id, "itemId": plan.item_id},
                payload=payload,
                before_state=before_state,
            )
        )
    return operations


def build_domain_operations(domain_plans: Sequence[DomainPlan]) -> List[PlannedOperation]:
    """Build ``CREATE_DOMAIN`` and ``ASSIGN_WORKSPACE_DOMAIN`` operations.

    Assignment operations key off the Purview domain ID (not the Fabric
    domain ID) in their target, since a to-be-created domain has no Fabric
    ID yet; the executor resolves it at apply time.
    """
    operations: List[PlannedOperation] = []
    for domain_plan in domain_plans:
        if domain_plan.action == DomainAction.CREATE_DOMAIN:
            payload = {"displayName": domain_plan.fabric_domain_name}
            operations.append(
                PlannedOperation(
                    operation_id=f"domain:create:{domain_plan.purview_domain_id}",
                    operation_type=OperationType.CREATE_DOMAIN,
                    fingerprint=compute_fingerprint(payload),
                    purview_source_id=domain_plan.purview_domain_id,
                    target={"purviewDomainId": domain_plan.purview_domain_id},
                    payload=payload,
                )
            )
        for assignment in domain_plan.workspace_assignments:
            if assignment.action != DomainAction.ASSIGN_WORKSPACE:
                continue
            fingerprint_payload = {
                "purviewDomainId": domain_plan.purview_domain_id,
                "workspaceId": assignment.workspace_id,
            }
            operations.append(
                PlannedOperation(
                    operation_id=f"domain:assign:{domain_plan.purview_domain_id}:{assignment.workspace_id}",
                    operation_type=OperationType.ASSIGN_WORKSPACE_DOMAIN,
                    fingerprint=compute_fingerprint(fingerprint_payload),
                    purview_source_id=domain_plan.purview_domain_id,
                    target={
                        "purviewDomainId": domain_plan.purview_domain_id,
                        "workspaceId": assignment.workspace_id,
                    },
                    payload={},
                    before_state={"previousDomainId": assignment.current_domain_id},
                )
            )
    return operations


def build_tag_definition_operations(
    desired_tag_names: Sequence[str], existing_tenant_tag_names: Sequence[str]
) -> List[PlannedOperation]:
    """Build ``CREATE_TAG`` operations for governance tag names not yet on the tenant."""
    existing = {name.strip().lower() for name in existing_tenant_tag_names}
    operations: List[PlannedOperation] = []
    for name in desired_tag_names:
        if name.strip().lower() in existing:
            continue
        payload = {"displayName": name}
        operations.append(
            PlannedOperation(
                operation_id=f"tag:create:{name}",
                operation_type=OperationType.CREATE_TAG,
                fingerprint=compute_fingerprint(payload),
                target={"tagName": name},
                payload=payload,
            )
        )
    return operations


def build_item_tag_operations(tag_plans: Sequence[ItemTagPlan]) -> List[PlannedOperation]:
    """Build ``APPLY_ITEM_TAGS`` operations for item tag plans in the ``ready`` state only."""
    operations: List[PlannedOperation] = []
    for plan in tag_plans:
        if plan.decision != TagDecision.READY:
            continue
        payload = {"tagNames": sorted(plan.tags_to_apply)}
        operations.append(
            PlannedOperation(
                operation_id=f"tags:apply:{plan.workspace_id}:{plan.item_id}",
                operation_type=OperationType.APPLY_ITEM_TAGS,
                fingerprint=compute_fingerprint(payload),
                target={"workspaceId": plan.workspace_id, "itemId": plan.item_id},
                payload=payload,
                before_state={"existingTagNames": sorted(plan.tags_already_present)},
            )
        )
    return operations


def build_planned_operations(
    item_plans: Sequence[ItemPlan],
    domain_plans: Sequence[DomainPlan],
    tag_plans: Sequence[ItemTagPlan],
    desired_governance_tag_names: Sequence[str] = (),
    existing_tenant_tag_names: Sequence[str] = (),
) -> List[PlannedOperation]:
    """Build every writable operation for a plan, in execution order."""
    operations = (
        build_domain_operations(domain_plans)
        + build_tag_definition_operations(desired_governance_tag_names, existing_tenant_tag_names)
        + build_item_tag_operations(tag_plans)
        + build_item_metadata_operations(item_plans)
    )
    return sorted(operations, key=lambda op: _EXECUTION_ORDER.get(op.operation_type, 99))


# ---------------------------------------------------------------------------
# Applying operations
# ---------------------------------------------------------------------------


def apply_operations(
    client: FabricMutationClient,
    operations: Sequence[PlannedOperation],
    checkpoint_store: CheckpointStore,
    checkpoint: RunCheckpoint,
    dry_run: bool = True,
    existing_tag_ids_by_name: Optional[Dict[str, str]] = None,
) -> SyncRunResult:
    """Apply planned operations in order, checkpointing each success immediately.

    Independent failures do not stop the run: every remaining operation is
    still attempted, and the caller (CLI layer) is expected to exit nonzero
    if :attr:`SyncRunResult.failed_count` is nonzero. Resolves Fabric domain
    IDs created earlier in the same run for dependent workspace-assignment
    operations, and resolves governance tag *names* to tag *ids* (seeded from
    ``existing_tag_ids_by_name`` and updated as ``CREATE_TAG`` operations
    succeed) for dependent ``APPLY_ITEM_TAGS`` operations.
    """
    results: List[OperationResult] = []
    resolved_domain_ids: Dict[str, str] = {}
    resolved_tag_ids: Dict[str, str] = dict(existing_tag_ids_by_name or {})

    for operation in operations:
        if CheckpointStore.has_applied(checkpoint, operation.operation_id, operation.fingerprint):
            results.append(
                OperationResult(
                    operation_id=operation.operation_id,
                    operation_type=operation.operation_type,
                    status=OperationStatus.SKIPPED_NO_CHANGE,
                    message="Already applied with the same desired state; skipping.",
                    target=operation.target,
                )
            )
            continue

        if dry_run:
            results.append(
                OperationResult(
                    operation_id=operation.operation_id,
                    operation_type=operation.operation_type,
                    status=OperationStatus.SKIPPED_DRY_RUN,
                    target=operation.target,
                )
            )
            continue

        try:
            after_state = _execute_operation(client, operation, resolved_domain_ids, resolved_tag_ids)
        except Exception as exc:  # noqa: BLE001 - deliberately broad: report and continue
            logger.warning("Operation %s failed: %s", operation.operation_id, exc)
            results.append(
                OperationResult(
                    operation_id=operation.operation_id,
                    operation_type=operation.operation_type,
                    status=OperationStatus.FAILED,
                    message=str(exc),
                    target=operation.target,
                )
            )
            continue

        record = _checkpoint_record_for(checkpoint.run_id, operation, after_state)
        checkpoint_store.record_operation(checkpoint, record)
        results.append(
            OperationResult(
                operation_id=operation.operation_id,
                operation_type=operation.operation_type,
                status=OperationStatus.APPLIED,
                target=operation.target,
            )
        )

    return SyncRunResult(run_id=checkpoint.run_id, dry_run=dry_run, results=results)


def _checkpoint_record_for(run_id: str, operation: PlannedOperation, after_state: Dict[str, Any]):
    from .models import CheckpointRecord  # local import to avoid a cycle at module import time

    return CheckpointRecord(
        operation_id=operation.operation_id,
        operation_type=operation.operation_type,
        run_id=run_id,
        applied_at=datetime.now(timezone.utc).isoformat(),
        fingerprint=operation.fingerprint,
        target=operation.target,
        before_state=operation.before_state,
        after_state=after_state,
        purview_source_id=operation.purview_source_id,
    )


def _execute_operation(
    client: FabricMutationClient,
    operation: PlannedOperation,
    resolved_domain_ids: Dict[str, str],
    resolved_tag_ids: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    op_type = operation.operation_type

    if op_type == OperationType.UPDATE_ITEM:
        # PlannedOperation payloads use the Fabric REST field names
        # ("displayName"/"description"); FabricClient.update_item takes the
        # equivalent snake_case keyword arguments, so map between the two here.
        kwargs = {_UPDATE_ITEM_FIELD_MAP.get(k, k): v for k, v in operation.payload.items()}
        client.update_item(operation.target["workspaceId"], operation.target["itemId"], **kwargs)
        return dict(operation.payload)

    if op_type == OperationType.CREATE_DOMAIN:
        result = client.create_domain(operation.payload["displayName"])
        domain_id = result.get("id") if isinstance(result, dict) else None
        if domain_id:
            resolved_domain_ids[operation.target["purviewDomainId"]] = domain_id
        return {"domainId": domain_id}

    if op_type == OperationType.ASSIGN_WORKSPACE_DOMAIN:
        domain_id = resolved_domain_ids.get(operation.target["purviewDomainId"])
        if not domain_id:
            raise RuntimeError(
                f"No resolved Fabric domain id for Purview domain "
                f"{operation.target['purviewDomainId']!r}; the domain-create operation "
                f"must run (and succeed) before its workspace assignments."
            )
        client.assign_domain_workspaces(domain_id, [operation.target["workspaceId"]])
        return {"domainId": domain_id}

    if op_type == OperationType.CREATE_TAG:
        display_name = operation.payload["displayName"]
        result = client.bulk_create_tags([display_name])
        tag_id = result[0].get("id") if result else None
        if tag_id is not None and resolved_tag_ids is not None:
            resolved_tag_ids[display_name] = tag_id
        return {"tagId": tag_id}

    if op_type == OperationType.APPLY_ITEM_TAGS:
        # Planned operations carry the desired tag *names*; resolve them here
        # to ids using tags that either already existed on the tenant or were
        # just created earlier in this same run (see ``resolved_tag_ids``).
        tag_names = operation.payload.get("tagNames", [])
        resolved_tag_ids = resolved_tag_ids or {}
        missing = [name for name in tag_names if name not in resolved_tag_ids]
        if missing:
            raise RuntimeError(
                f"No resolved Fabric tag id for tag name(s) {missing!r}; the corresponding "
                f"CREATE_TAG operation must run (and succeed) before tags are applied."
            )
        tag_ids = [resolved_tag_ids[name] for name in tag_names]
        client.apply_tags(operation.target["workspaceId"], operation.target["itemId"], tag_ids)
        return {"appliedTags": tag_ids}

    raise ValueError(f"Unsupported operation type for apply: {op_type}")


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------

#: Operation types eligible for reversal. Domain and tag *definitions* are
#: deliberately excluded -- rollback never deletes them.
_REVERSIBLE_TYPES = {
    OperationType.UPDATE_ITEM,
    OperationType.ASSIGN_WORKSPACE_DOMAIN,
    OperationType.APPLY_ITEM_TAGS,
}


def build_rollback_operations(checkpoint: RunCheckpoint) -> List[PlannedOperation]:
    """Derive reverse operations purely from a run's checkpoint records.

    Rollback never re-runs matching/planning -- it only knows how to undo
    exactly what was recorded, which is what makes it safe to run long after
    the source Purview/Fabric state has moved on.
    """
    reverse_ops: List[PlannedOperation] = []
    for record in checkpoint.records:
        if record.operation_type not in _REVERSIBLE_TYPES:
            continue

        if record.operation_type == OperationType.UPDATE_ITEM:
            payload = dict(record.before_state)
            reverse_ops.append(
                PlannedOperation(
                    operation_id=f"rollback:{record.operation_id}",
                    operation_type=OperationType.UPDATE_ITEM,
                    fingerprint=compute_fingerprint(payload),
                    purview_source_id=record.purview_source_id,
                    target=record.target,
                    payload=payload,
                )
            )
        elif record.operation_type == OperationType.ASSIGN_WORKSPACE_DOMAIN:
            # Our conflict policy never assigns over an existing assignment,
            # so the pre-run state is always "unassigned" for anything this
            # run itself assigned.
            reverse_ops.append(
                PlannedOperation(
                    operation_id=f"rollback:{record.operation_id}",
                    operation_type=OperationType.UNASSIGN_WORKSPACE_DOMAIN,
                    fingerprint=compute_fingerprint({"target": record.target}),
                    purview_source_id=record.purview_source_id,
                    target=record.target,
                    payload={"domainId": record.after_state.get("domainId")},
                )
            )
        elif record.operation_type == OperationType.APPLY_ITEM_TAGS:
            applied = record.after_state.get("appliedTags", [])
            reverse_ops.append(
                PlannedOperation(
                    operation_id=f"rollback:{record.operation_id}",
                    operation_type=OperationType.UNAPPLY_ITEM_TAGS,
                    fingerprint=compute_fingerprint({"tags": sorted(applied)}),
                    purview_source_id=record.purview_source_id,
                    target=record.target,
                    payload={"tagIds": applied},
                )
            )

    return sorted(reverse_ops, key=lambda op: _EXECUTION_ORDER.get(op.operation_type, 99))


def apply_rollback(
    client: FabricMutationClient,
    reverse_operations: Sequence[PlannedOperation],
    dry_run: bool = True,
) -> RollbackResult:
    """Execute reverse operations. Independent failures do not stop the rollback."""
    results: List[OperationResult] = []
    run_id = ""
    for operation in reverse_operations:
        if not run_id and operation.operation_id.startswith("rollback:"):
            run_id = operation.operation_id

        if dry_run:
            results.append(
                OperationResult(
                    operation_id=operation.operation_id,
                    operation_type=operation.operation_type,
                    status=OperationStatus.SKIPPED_DRY_RUN,
                    target=operation.target,
                )
            )
            continue
        try:
            if operation.operation_type == OperationType.UPDATE_ITEM:
                kwargs = {_UPDATE_ITEM_FIELD_MAP.get(k, k): v for k, v in operation.payload.items()}
                client.update_item(operation.target["workspaceId"], operation.target["itemId"], **kwargs)
            elif operation.operation_type == OperationType.UNASSIGN_WORKSPACE_DOMAIN:
                domain_id = operation.payload.get("domainId")
                if domain_id:
                    client.unassign_domain_workspaces(domain_id, [operation.target["workspaceId"]])
            elif operation.operation_type == OperationType.UNAPPLY_ITEM_TAGS:
                client.unapply_tags(
                    operation.target["workspaceId"],
                    operation.target["itemId"],
                    operation.payload.get("tagIds", []),
                )
            else:
                raise ValueError(f"Unsupported operation type for rollback: {operation.operation_type}")
        except Exception as exc:  # noqa: BLE001 - deliberately broad: report and continue
            logger.warning("Rollback operation %s failed: %s", operation.operation_id, exc)
            results.append(
                OperationResult(
                    operation_id=operation.operation_id,
                    operation_type=operation.operation_type,
                    status=OperationStatus.FAILED,
                    message=str(exc),
                    target=operation.target,
                )
            )
            continue

        results.append(
            OperationResult(
                operation_id=operation.operation_id,
                operation_type=operation.operation_type,
                status=OperationStatus.ROLLED_BACK,
                target=operation.target,
            )
        )

    return RollbackResult(run_id=run_id, dry_run=dry_run, results=results)
