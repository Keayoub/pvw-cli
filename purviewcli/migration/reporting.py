# SPDX-License-Identifier: Apache-2.0
"""JSON and CSV report generation for the Purview UC -> Fabric sync.

Reports are always written atomically (see :func:`purviewcli.migration.state._atomic_write`)
so a crash mid-write never leaves a truncated report file that looks valid.
"""

from __future__ import annotations

import csv
import io
import json
from typing import Any, Dict, List, Optional

from .models import MigrationPlan, RollbackResult, SyncRunResult
from .state import atomic_write


def write_json_report(
    plan: MigrationPlan,
    path: str,
    sync_result: Optional[SyncRunResult] = None,
    rollback_result: Optional[RollbackResult] = None,
) -> None:
    """Write the full assessment (and, if present, apply/rollback outcome) as JSON."""
    document: Dict[str, Any] = {"plan": plan.to_dict()}
    if sync_result is not None:
        document["syncResult"] = sync_result.to_dict()
    if rollback_result is not None:
        document["rollbackResult"] = rollback_result.to_dict()
    atomic_write(path, json.dumps(document, indent=2, sort_keys=True))


#: Column order for the flattened CSV report.
_CSV_COLUMNS = [
    "category",
    "purviewId",
    "workspaceId",
    "itemId",
    "decision",
    "details",
]


def _item_plan_rows(plan: MigrationPlan) -> List[Dict[str, str]]:
    rows = []
    for item_plan in plan.item_plans:
        details = "; ".join(f"{c.field}: {c.current!r} -> {c.desired!r}" for c in item_plan.changes)
        if item_plan.validation_errors:
            details = (details + "; " if details else "") + "; ".join(item_plan.validation_errors)
        rows.append(
            {
                "category": "item_metadata",
                "purviewId": item_plan.purview_asset_id,
                "workspaceId": item_plan.workspace_id,
                "itemId": item_plan.item_id,
                "decision": item_plan.decision.value,
                "details": details,
            }
        )
    return rows


def _tag_plan_rows(plan: MigrationPlan) -> List[Dict[str, str]]:
    rows = []
    for tag_plan in plan.tag_plans:
        parts = []
        if tag_plan.tags_to_apply:
            parts.append(f"apply: {', '.join(tag_plan.tags_to_apply)}")
        if tag_plan.overflow_tags:
            parts.append(f"overflow (not applied): {', '.join(tag_plan.overflow_tags)}")
        rows.append(
            {
                "category": "governance_tags",
                "purviewId": "",
                "workspaceId": tag_plan.workspace_id,
                "itemId": tag_plan.item_id,
                "decision": tag_plan.decision.value,
                "details": "; ".join(parts),
            }
        )
    return rows


def _domain_plan_rows(plan: MigrationPlan) -> List[Dict[str, str]]:
    rows = []
    for domain_plan in plan.domain_plans:
        rows.append(
            {
                "category": "domain",
                "purviewId": domain_plan.purview_domain_id,
                "workspaceId": "",
                "itemId": "",
                "decision": domain_plan.action.value,
                "details": f"fabricDomainName={domain_plan.fabric_domain_name!r}",
            }
        )
        for assignment in domain_plan.workspace_assignments:
            details = f"desiredDomainId={assignment.desired_domain_id!r}"
            if assignment.conflict_reason:
                details += f"; {assignment.conflict_reason}"
            rows.append(
                {
                    "category": "domain_workspace_assignment",
                    "purviewId": domain_plan.purview_domain_id,
                    "workspaceId": assignment.workspace_id,
                    "itemId": "",
                    "decision": assignment.action.value,
                    "details": details,
                }
            )
    return rows


def _match_rows(plan: MigrationPlan) -> List[Dict[str, str]]:
    rows = []
    for match in plan.matches:
        details = match.reason or ""
        if match.suggestions:
            names = ", ".join(f"{s.display_name} ({s.workspace_id}/{s.item_id})" for s in match.suggestions)
            details = (details + "; " if details else "") + f"suggestions: {names}"
        rows.append(
            {
                "category": "match",
                "purviewId": match.purview_asset_id,
                "workspaceId": match.workspace_id or "",
                "itemId": match.item_id or "",
                "decision": match.outcome.value,
                "details": details,
            }
        )
    return rows


def plan_to_csv_rows(plan: MigrationPlan) -> List[Dict[str, str]]:
    """Flatten a plan into rows suitable for a single CSV audit report."""
    return _match_rows(plan) + _item_plan_rows(plan) + _tag_plan_rows(plan) + _domain_plan_rows(plan)


def write_csv_report(plan: MigrationPlan, path: str) -> None:
    """Write a flattened CSV audit report covering matches, items, tags, and domains."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=_CSV_COLUMNS)
    writer.writeheader()
    for row in plan_to_csv_rows(plan):
        writer.writerow(row)
    atomic_write(path, buffer.getvalue())
