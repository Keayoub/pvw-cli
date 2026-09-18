# SPDX-License-Identifier: Apache-2.0
"""``pvw fabric`` command group: Purview Unified Catalog -> Fabric OneLake catalog sync.

Commands:
  - ``pvw fabric migration assess``  : always read-only; produces a plan/report.
  - ``pvw fabric migration sync``    : dry-run by default; pass --apply to write.
  - ``pvw fabric migration run``     : config-file-driven equivalent of ``sync``, for schedulers.
  - ``pvw fabric migration rollback``: preview by default; pass --apply to restore.

All writes are metadata-only (Fabric item display name/description, tenant tags, domain
assignment) and one-way (Purview -> Fabric); nothing is ever written back to Purview.
"""

from __future__ import annotations

import json
import sys
from typing import List, Optional, Tuple

import click

from .console_utils import get_console

console = get_console()


def _get_clients(ctx):
    from purviewcli.client._entity import Entity
    from purviewcli.client._unified_catalog import UnifiedCatalogClient
    from purviewcli.client.client_cache import get_cached_client
    from purviewcli.client.fabric_client import FabricClient

    profile = ctx.obj.get("profile", "default")
    uc_client = get_cached_client(UnifiedCatalogClient, profile=profile)
    fabric_client = get_cached_client(FabricClient, profile=profile)
    entity_client = get_cached_client(Entity, profile=profile)
    return uc_client, fabric_client, entity_client


def _shared_assessment_options(func):
    """Attach the option stack shared by ``assess`` and ``sync``."""
    decorators = [
        click.option("--purview-domain-id", "purview_domain_ids", multiple=True, help="Restrict to these Purview domain IDs (repeatable). Default: all domains."),
        click.option("--workspace-id", "workspace_ids", multiple=True, help="Restrict to these Fabric workspace IDs (repeatable). Default: all workspaces."),
        click.option("--mapping-file", type=click.Path(exists=True, dir_okay=False), default=None, help="JSON file of explicit Purview-asset-id -> Fabric workspace/item bindings."),
        click.option("--overwrite", is_flag=True, default=False, help="Allow overwriting already-populated Fabric display name/description values."),
        click.option("--truncate-descriptions", is_flag=True, default=False, help="Truncate descriptions over Fabric's 256-character limit instead of flagging a validation error."),
        click.option("--sync-classifications", is_flag=True, default=False, help="Also sync Purview classifications/labels onto Fabric items as tags (opt-in: requires Data Map linkage; see docs/fabric-migration-feature-parity.md)."),
        click.option("--report-file", type=click.Path(dir_okay=False), default=None, help="Write the full JSON assessment/apply report to this path."),
        click.option("--csv-report-file", type=click.Path(dir_okay=False), default=None, help="Write a flattened CSV audit report to this path."),
        click.option("--output", default="table", type=click.Choice(["table", "json"]), help="Console summary format."),
    ]
    for decorator in reversed(decorators):
        func = decorator(func)
    return func


def _run_assessment(
    ctx,
    purview_domain_ids: Tuple[str, ...],
    workspace_ids: Tuple[str, ...],
    mapping_file: Optional[str],
    overwrite: bool,
    truncate_descriptions: bool,
    sync_classifications: bool = False,
    run_id: Optional[str] = None,
):
    """Fetch Purview + Fabric state and build a MigrationPlan. Shared by assess/sync/run.

    ``run_id`` should be supplied by callers that persist a checkpoint (e.g.
    ``sync``) so repeated invocations against the same checkpoint file reuse
    its run id rather than generating a new one each time -- required for
    :meth:`~purviewcli.migration.state.CheckpointStore.load_or_create`'s
    resume/idempotency guard. ``assess`` (which never checkpoints) leaves it
    unset and always gets a fresh run id.
    """
    from purviewcli.migration.service import (
        build_migration_plan,
        fetch_fabric_catalog,
        fetch_fabric_domains_and_workspace_assignments,
        fetch_purview_state,
        load_mapping_file,
    )
    from purviewcli.migration.state import new_run_id

    uc_client, fabric_client, entity_client = _get_clients(ctx)

    mapping = load_mapping_file(mapping_file)
    purview_state = fetch_purview_state(
        uc_client,
        domain_ids=list(purview_domain_ids),
        entity_client=entity_client,
        sync_classifications=sync_classifications,
    )
    catalog_entries = fetch_fabric_catalog(fabric_client, workspace_ids=list(workspace_ids))
    fabric_domains, workspace_current_domain = fetch_fabric_domains_and_workspace_assignments(fabric_client)

    plan = build_migration_plan(
        run_id=run_id or new_run_id(),
        purview_assets=purview_state["assets"],
        purview_domains=purview_state["domains"],
        governance_objects=purview_state["governance_objects"],
        catalog_entries=catalog_entries,
        fabric_domains=fabric_domains,
        workspace_current_domain=workspace_current_domain,
        fabric_client=fabric_client,
        mapping=mapping,
        target_workspace_ids=list(workspace_ids),
        overwrite=overwrite,
        truncate_descriptions=truncate_descriptions,
        sync_classifications=sync_classifications,
    )
    return plan, fabric_client


def _write_reports(plan, report_file: Optional[str], csv_report_file: Optional[str], sync_result=None, rollback_result=None):
    from purviewcli.migration.reporting import write_csv_report, write_json_report

    if report_file:
        write_json_report(plan, report_file, sync_result=sync_result, rollback_result=rollback_result)
        console.print(f"[dim]JSON report written to {report_file}[/dim]")
    if csv_report_file:
        write_csv_report(plan, csv_report_file)
        console.print(f"[dim]CSV report written to {csv_report_file}[/dim]")


def _render_plan_summary(plan, output: str) -> None:
    if output == "json":
        print(json.dumps(plan.to_dict(), indent=2, default=str))
        return

    from rich.table import Table

    match_counts: dict = {}
    for match in plan.matches:
        match_counts[match.outcome.value] = match_counts.get(match.outcome.value, 0) + 1
    item_counts: dict = {}
    for item_plan in plan.item_plans:
        item_counts[item_plan.decision.value] = item_counts.get(item_plan.decision.value, 0) + 1
    tag_counts: dict = {}
    for tag_plan in plan.tag_plans:
        tag_counts[tag_plan.decision.value] = tag_counts.get(tag_plan.decision.value, 0) + 1
    domain_counts: dict = {}
    for domain_plan in plan.domain_plans:
        domain_counts[domain_plan.action.value] = domain_counts.get(domain_plan.action.value, 0) + 1

    table = Table(title=f"Assessment summary (run {plan.run_id})")
    table.add_column("Category", style="cyan")
    table.add_column("Outcome", style="yellow")
    table.add_column("Count", style="magenta")
    for category, counts in (
        ("Asset match", match_counts),
        ("Item metadata", item_counts),
        ("Governance tags", tag_counts),
        ("Domain", domain_counts),
    ):
        for outcome, count in counts.items():
            table.add_row(category, outcome, str(count))
    console.print(table)


def _exit_nonzero_if_needed(plan, sync_result=None) -> None:
    """Exit nonzero if the assessment/apply surfaced anything requiring attention."""
    from purviewcli.migration.models import ItemDecision, TagDecision

    has_conflicts = any(
        p.decision in (ItemDecision.CONFLICT, ItemDecision.VALIDATION_ERROR) for p in plan.item_plans
    )
    has_tag_overflow = any(t.decision == TagDecision.TAG_OVERFLOW for t in plan.tag_plans)
    has_failures = sync_result is not None and sync_result.failed_count > 0
    if has_conflicts or has_tag_overflow or has_failures:
        sys.exit(1)


@click.group()
def fabric():
    """Purview Unified Catalog -> Fabric OneLake catalog migration commands."""
    pass


@fabric.group()
def migration():
    """Assess, sync, and roll back the Purview -> Fabric metadata migration."""
    pass


@migration.command(name="assess")
@_shared_assessment_options
@click.pass_context
def migration_assess(ctx, purview_domain_ids, workspace_ids, mapping_file, overwrite, truncate_descriptions, sync_classifications, report_file, csv_report_file, output):
    """Read-only assessment: build and report a migration plan without writing anything."""
    plan, _fabric_client = _run_assessment(ctx, purview_domain_ids, workspace_ids, mapping_file, overwrite, truncate_descriptions, sync_classifications=sync_classifications)
    _write_reports(plan, report_file, csv_report_file)
    _render_plan_summary(plan, output)
    _exit_nonzero_if_needed(plan)


@migration.command(name="sync")
@_shared_assessment_options
@click.option("--checkpoint-file", type=click.Path(dir_okay=False), required=True, help="Path to this run's checkpoint file (created on first apply; required for resume/rollback).")
@click.option("--apply", "apply_", is_flag=True, default=False, help="Actually write changes to Fabric. Without this flag, sync always dry-runs.")
@click.pass_context
def migration_sync(ctx, purview_domain_ids, workspace_ids, mapping_file, overwrite, truncate_descriptions, sync_classifications, report_file, csv_report_file, output, checkpoint_file, apply_):
    """Assess, then apply (or dry-run) the resulting plan against Fabric."""
    from purviewcli.migration.service import sync_plan
    from purviewcli.migration.state import CheckpointStore

    store = CheckpointStore(checkpoint_file)
    # Reuse an existing checkpoint's run id so repeated syncs against the same
    # checkpoint file are idempotent (see CheckpointStore.load_or_create).
    existing_checkpoint = store.load()
    run_id = existing_checkpoint.run_id if existing_checkpoint is not None else None

    plan, fabric_client = _run_assessment(ctx, purview_domain_ids, workspace_ids, mapping_file, overwrite, truncate_descriptions, sync_classifications=sync_classifications, run_id=run_id)
    sync_result = sync_plan(fabric_client, plan, store, plan.run_id, dry_run=not apply_)

    _write_reports(plan, report_file, csv_report_file, sync_result=sync_result)
    _render_plan_summary(plan, output)
    if output == "json":
        print(json.dumps(sync_result.to_dict(), indent=2, default=str))
    else:
        mode = "DRY RUN (no changes written)" if not apply_ else "APPLIED"
        console.print(
            f"[bold]{mode}[/bold]: {sync_result.succeeded_count} succeeded, "
            f"{sync_result.failed_count} failed, run_id={sync_result.run_id}"
        )
        if sync_result.failed_count:
            for failure in sync_result.failures:
                console.print(f"[red]  - {failure.operation_id}: {failure.message}[/red]")
    _exit_nonzero_if_needed(plan, sync_result)


@migration.command(name="run")
@click.option("--config", "config_path", type=click.Path(exists=True, dir_okay=False), required=True, help="JSON config file with the same keys as the sync command's options (for scheduled/unattended runs).")
@click.pass_context
def migration_run(ctx, config_path):
    """Config-file-driven equivalent of ``sync``, intended for schedulers/automation."""
    with open(config_path, "r", encoding="utf-8") as handle:
        config = json.load(handle)

    ctx.invoke(
        migration_sync,
        purview_domain_ids=tuple(config.get("purview_domain_ids", [])),
        workspace_ids=tuple(config.get("workspace_ids", [])),
        mapping_file=config.get("mapping_file"),
        overwrite=bool(config.get("overwrite", False)),
        truncate_descriptions=bool(config.get("truncate_descriptions", False)),
        sync_classifications=bool(config.get("sync_classifications", False)),
        report_file=config.get("report_file"),
        csv_report_file=config.get("csv_report_file"),
        output=config.get("output", "table"),
        checkpoint_file=config["checkpoint_file"],
        apply_=bool(config.get("apply", False)),
    )


@migration.command(name="rollback")
@click.option("--checkpoint-file", type=click.Path(exists=True, dir_okay=False), required=True, help="Checkpoint file of the run to roll back.")
@click.option("--apply", "apply_", is_flag=True, default=False, help="Actually restore prior state in Fabric. Without this flag, rollback always previews.")
@click.option("--report-file", type=click.Path(dir_okay=False), default=None, help="Write the full JSON rollback report to this path.")
@click.option("--output", default="table", type=click.Choice(["table", "json"]), help="Console summary format.")
@click.pass_context
def migration_rollback(ctx, checkpoint_file, apply_, report_file, output):
    """Reverse a completed run's item metadata, tag, and domain-assignment changes.

    Rollback is derived purely from the checkpoint file -- it never re-runs
    matching/planning -- so it is safe to run long after the source data has
    moved on. Domains and tag definitions created by a run are never deleted.
    """
    from purviewcli.migration.models import MigrationPlan
    from purviewcli.migration.service import rollback_run
    from purviewcli.migration.state import CheckpointStore, new_run_id

    _uc_client, fabric_client, _entity_client = _get_clients(ctx)
    store = CheckpointStore(checkpoint_file)
    result = rollback_run(fabric_client, store, dry_run=not apply_)

    if report_file:
        empty_plan = MigrationPlan(run_id=result.run_id or new_run_id(), generated_at="")
        from purviewcli.migration.reporting import write_json_report

        write_json_report(empty_plan, report_file, rollback_result=result)
        console.print(f"[dim]JSON report written to {report_file}[/dim]")

    if output == "json":
        print(json.dumps(result.to_dict(), indent=2, default=str))
    else:
        mode = "PREVIEW (no changes written)" if not apply_ else "ROLLED BACK"
        console.print(
            f"[bold]{mode}[/bold]: run_id={result.run_id}, {len(result.results)} operation(s), "
            f"{len(result.failures)} failed"
        )
        for failure in result.failures:
            console.print(f"[red]  - {failure.operation_id}: {failure.message}[/red]")

    if result.failures:
        sys.exit(1)
