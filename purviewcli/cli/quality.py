"""Data Quality CLI commands."""

import json
import click
from rich.syntax import Syntax
from rich.table import Table

from .console_utils import get_console
from purviewcli.client._quality import DataQuality
from purviewcli.client._unified_catalog import UnifiedCatalogClient
from purviewcli.client.client_cache import get_cached_client

console = get_console()


def _client(ctx):
    return get_cached_client(DataQuality, profile=ctx.obj.get("profile", "default"))


def _uc_client(ctx):
    return get_cached_client(UnifiedCatalogClient, profile=ctx.obj.get("profile", "default"))


def _format_json_output(data):
    json_str = json.dumps(data, indent=2)
    console.print(Syntax(json_str, "json", theme="monokai", line_numbers=True))


def _render(data, output, title="Result"):
    if output == "json":
        console.print(json.dumps(data, indent=2))
        return
    if output == "jsonc":
        _format_json_output(data)
        return

    if isinstance(data, list):
        table = Table(title=title)
        table.add_column("#", style="cyan")
        table.add_column("Data", style="magenta")
        for i, item in enumerate(data, start=1):
            table.add_row(str(i), json.dumps(item, default=str)[:180])
        console.print(table)
        return

    if isinstance(data, dict):
        table = Table(title=title)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="magenta")
        for key, value in data.items():
            table.add_row(str(key), json.dumps(value, default=str)[:180])
        console.print(table)
        return

    console.print(str(data))


def _build_page_args(skip, top, filter_expr):
    args = {}
    if skip is not None:
        args["--skip"] = skip
    if top is not None:
        args["--top"] = top
    if filter_expr:
        args["--filter"] = filter_expr
    return args


def _is_resource_not_found_error(result):
    if not isinstance(result, dict):
        return False
    status = str(result.get("status", "")).lower()
    message = str(result.get("message", "")).lower()
    return status == "error" and ("resourcenotfound" in message or "http 404" in message)


def _unsupported_result(feature):
    return {
        "status": "error",
        "message": (
            f"{feature} is not mapped to a live endpoint in this tenant yet. "
            "Use the supported domain-scoped quality commands instead."
        ),
        "supported": [
            "python -m purviewcli uc quality domains --output json",
            "python -m purviewcli uc quality domain-report --domain-id <DOMAIN_ID> --output json",
            "python -m purviewcli uc quality data-sources --domain-id <DOMAIN_ID> --output json",
            "python -m purviewcli uc quality schedules --domain-id <DOMAIN_ID> --output json",
            "python -m purviewcli uc quality alerts --domain-id <DOMAIN_ID> --output json",
            "python -m purviewcli uc quality assets --domain-id <DOMAIN_ID> --output json",
        ],
    }


@click.group()
def quality():
    """Manage Data Quality (connections, rules, profiles, scans, scores)."""


@quality.command("domains")
@click.option("--output", default="table", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.option("--filter", "filter_expr", default="")
@click.pass_context
def list_domains(ctx, output, skip, top, filter_expr):
    """List business domains with quality support."""
    # Use UC domains as source of truth to avoid tenant-specific DQ domain-list gaps.
    result = _uc_client(ctx).get_governance_domains({})
    _render(result, output, "Data Quality Business Domains")


@quality.command("domain-report")
@click.option("--domain-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def domain_report(ctx, domain_id, output):
    """Get domain quality report."""
    result = _client(ctx).get_domain_report({"--domain-id": domain_id})
    _render(result, output, "Domain Quality Report")


@quality.command("data-sources")
@click.option("--domain-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.pass_context
def data_sources(ctx, domain_id, output, skip, top):
    """List live Data Quality data sources for a domain."""
    args = {"--domain-id": domain_id}
    if skip is not None:
        args["--skip"] = skip
    if top is not None:
        args["--top"] = top
    result = _client(ctx).list_domain_data_sources(args)
    _render(result, output, "Data Quality Data Sources")


@quality.command("schedules")
@click.option("--domain-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.pass_context
def schedules(ctx, domain_id, output, skip, top):
    """List live Data Quality schedules for a domain."""
    args = {"--domain-id": domain_id}
    if skip is not None:
        args["--skip"] = skip
    if top is not None:
        args["--top"] = top
    result = _client(ctx).list_domain_schedules(args)
    _render(result, output, "Data Quality Schedules")


@quality.command("alerts")
@click.option("--domain-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.pass_context
def alerts(ctx, domain_id, output, skip, top):
    """List live Data Quality alerts for a domain."""
    args = {"--domain-id": domain_id}
    if skip is not None:
        args["--skip"] = skip
    if top is not None:
        args["--top"] = top
    result = _client(ctx).list_domain_alerts(args)
    _render(result, output, "Data Quality Alerts")


@quality.command("assets")
@click.option("--domain-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.pass_context
def assets(ctx, domain_id, output, skip, top):
    """List live Data Quality assets for a domain."""
    args = {"--domain-id": domain_id}
    if skip is not None:
        args["--skip"] = skip
    if top is not None:
        args["--top"] = top
    result = _client(ctx).list_domain_assets(args)
    _render(result, output, "Data Quality Assets")


@quality.group()
def connection():
    """Manage data quality connections."""


@connection.command("list")
@click.option("--output", default="table", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.option("--filter", "filter_expr", default="")
@click.pass_context
def connection_list(ctx, output, skip, top, filter_expr):
    _render(_unsupported_result("Connection list without domain scope"), output, "Data Quality Connections")


@connection.command("show")
@click.option("--connection-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def connection_show(ctx, connection_id, output):
    _render(_unsupported_result("Connection show"), output, "Connection")


@connection.command("create")
@click.option("--name", required=True)
@click.option("--type", "conn_type", required=True)
@click.option("--description", default="")
@click.option("--connection-string", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def connection_create(ctx, name, conn_type, description, connection_string, output):
    _render(_unsupported_result("Connection create"), output, "Connection Created")


@connection.command("update")
@click.option("--connection-id", required=True)
@click.option("--name", default="")
@click.option("--type", "conn_type", default="")
@click.option("--description", default="")
@click.option("--connection-string", default="")
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def connection_update(ctx, connection_id, name, conn_type, description, connection_string, output):
    _render(_unsupported_result("Connection update"), output, "Connection Updated")


@connection.command("delete")
@click.option("--connection-id", required=True)
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def connection_delete(ctx, connection_id, yes):
    _render(_unsupported_result("Connection delete"), "table", "Connection Deleted")


@quality.group()
def rule():
    """Manage data quality rules."""


@rule.command("list")
@click.option("--output", default="table", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.option("--filter", "filter_expr", default="")
@click.option("--domain-id", default="", help="Governance domain ID for tenant-scoped fallback context")
@click.pass_context
def rule_list(ctx, output, skip, top, filter_expr, domain_id):
    args = _build_page_args(skip, top, filter_expr)
    if domain_id:
        args["--domain-id"] = domain_id

    result = _client(ctx).list_rules(args)
    if _is_resource_not_found_error(result):
        hint = {
            "status": "error",
            "message": (
                "Rules endpoint is not exposed for this tenant/path. "
                "This tenant currently supports domain quality report at "
                "/datagovernance/quality/business-domains/{domainId}/report."
            ),
            "next": [
                "python -m purviewcli uc domain list --output json",
                "python -m purviewcli uc quality domain-report --domain-id <DOMAIN_ID> --output json",
            ],
        }
        if domain_id:
            report = _client(ctx).get_domain_report({"--domain-id": domain_id})
            hint["domainReportSample"] = report
        result = hint

    _render(result, output, "Data Quality Rules")


@rule.command("show")
@click.option("--rule-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def rule_show(ctx, rule_id, output):
    _render(_unsupported_result("Rule show"), output, "Rule")


@rule.command("create")
@click.option("--name", required=True)
@click.option("--type", "rule_type", required=True)
@click.option("--asset-id", required=True)
@click.option("--column", default="")
@click.option("--threshold", type=float, default=None)
@click.option("--description", default="")
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def rule_create(ctx, name, rule_type, asset_id, column, threshold, description, output):
    _render(_unsupported_result("Rule create"), output, "Rule Created")


@rule.command("update")
@click.option("--rule-id", required=True)
@click.option("--name", default="")
@click.option("--type", "rule_type", default="")
@click.option("--asset-id", default="")
@click.option("--column", default="")
@click.option("--threshold", type=float, default=None)
@click.option("--description", default="")
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def rule_update(ctx, rule_id, name, rule_type, asset_id, column, threshold, description, output):
    _render(_unsupported_result("Rule update"), output, "Rule Updated")


@rule.command("delete")
@click.option("--rule-id", required=True)
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def rule_delete(ctx, rule_id, yes):
    _render(_unsupported_result("Rule delete"), "table", "Rule Deleted")


@rule.command("apply")
@click.option("--rule-id", required=True)
@click.option("--asset-id", multiple=True, help="Repeat for multiple assets")
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def rule_apply(ctx, rule_id, asset_id, output):
    _render(_unsupported_result("Rule apply"), output, "Rule Apply Result")


@quality.group()
def profile():
    """Manage data quality profiles."""


@profile.command("list")
@click.option("--output", default="table", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.option("--filter", "filter_expr", default="")
@click.pass_context
def profile_list(ctx, output, skip, top, filter_expr):
    _render(_unsupported_result("Profile list"), output, "Data Quality Profiles")


@profile.command("show")
@click.option("--profile-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def profile_show(ctx, profile_id, output):
    _render(_unsupported_result("Profile show"), output, "Profile")


@profile.command("create")
@click.option("--name", required=True)
@click.option("--asset-id", required=True)
@click.option("--connection-id", required=True)
@click.option("--scope", default="AllColumns")
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def profile_create(ctx, name, asset_id, connection_id, scope, output):
    _render(_unsupported_result("Profile create"), output, "Profile Created")


@profile.command("update")
@click.option("--profile-id", required=True)
@click.option("--name", default="")
@click.option("--asset-id", default="")
@click.option("--connection-id", default="")
@click.option("--scope", default="")
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def profile_update(ctx, profile_id, name, asset_id, connection_id, scope, output):
    _render(_unsupported_result("Profile update"), output, "Profile Updated")


@profile.command("delete")
@click.option("--profile-id", required=True)
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def profile_delete(ctx, profile_id, yes):
    _render(_unsupported_result("Profile delete"), "table", "Profile Deleted")


@profile.command("run")
@click.option("--profile-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def profile_run(ctx, profile_id, output):
    _render(_unsupported_result("Profile run"), output, "Profile Run")


@profile.command("results")
@click.option("--profile-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.pass_context
def profile_results(ctx, profile_id, output, skip, top):
    _render(_unsupported_result("Profile results"), output, "Profile Results")


@quality.group()
def scan():
    """Manage data quality scans."""


@scan.command("list")
@click.option("--output", default="table", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.option("--filter", "filter_expr", default="")
@click.pass_context
def scan_list(ctx, output, skip, top, filter_expr):
    _render(_unsupported_result("Scan list"), output, "Data Quality Scans")


@scan.command("show")
@click.option("--scan-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def scan_show(ctx, scan_id, output):
    _render(_unsupported_result("Scan show"), output, "Scan")


@scan.command("create")
@click.option("--name", required=True)
@click.option("--product-id", required=True)
@click.option("--rule-id", multiple=True, help="Repeat for multiple rules")
@click.option("--schedule", default="Manual")
@click.option("--threshold", type=float, default=None)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def scan_create(ctx, name, product_id, rule_id, schedule, threshold, output):
    _render(_unsupported_result("Scan create"), output, "Scan Created")


@scan.command("update")
@click.option("--scan-id", required=True)
@click.option("--name", default="")
@click.option("--product-id", default="")
@click.option("--rule-id", multiple=True, help="Repeat for multiple rules")
@click.option("--schedule", default="")
@click.option("--threshold", type=float, default=None)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def scan_update(ctx, scan_id, name, product_id, rule_id, schedule, threshold, output):
    _render(_unsupported_result("Scan update"), output, "Scan Updated")


@scan.command("delete")
@click.option("--scan-id", required=True)
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def scan_delete(ctx, scan_id, yes):
    _render(_unsupported_result("Scan delete"), "table", "Scan Deleted")


@scan.command("run")
@click.option("--scan-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def scan_run(ctx, scan_id, output):
    _render(_unsupported_result("Scan run"), output, "Scan Run")


@scan.command("stop")
@click.option("--scan-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def scan_stop(ctx, scan_id, output):
    _render(_unsupported_result("Scan stop"), output, "Scan Stop")


@scan.command("results")
@click.option("--scan-id", required=True)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.pass_context
def scan_results(ctx, scan_id, output, skip, top):
    _render(_unsupported_result("Scan results"), output, "Scan Results")


@quality.group()
def score():
    """View data quality scores."""


@score.command("asset")
@click.option("--asset-id", required=True)
@click.option("--domain-id", default="", help="Governance domain ID for domain-scoped asset lookup")
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def score_asset(ctx, asset_id, domain_id, output):
    if not domain_id:
        _render(_unsupported_result("Asset score without domain scope"), output, "Asset Quality Score")
        return
    result = _client(ctx).list_domain_assets({"--domain-id": domain_id})
    if isinstance(result, dict) and isinstance(result.get("response"), list):
        filtered = [item for item in result["response"] if item.get("assetId") == asset_id]
        result = filtered[0] if filtered else {"status": "error", "message": f"Asset {asset_id} not found in domain {domain_id}"}
    _render(result, output, "Asset Quality Score")


@score.command("list")
@click.option("--product-id", default="")
@click.option("--threshold", type=float, default=None)
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.option("--output", default="table", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def score_list(ctx, product_id, threshold, skip, top, output):
    args = _build_page_args(skip, top, "")
    if product_id:
        args["--product-id"] = product_id
    if threshold is not None:
        args["--threshold"] = threshold
    _render(_unsupported_result("Score list without domain scope"), output, "Asset Quality Scores")
    return


@score.command("domain")
@click.option("--domain-id", required=True)
@click.option("--skip", type=int, default=None)
@click.option("--top", type=int, default=None)
@click.option("--output", default="json", type=click.Choice(["table", "json", "jsonc"]))
@click.pass_context
def score_domain(ctx, domain_id, skip, top, output):
    args = {"--domain-id": domain_id}
    if skip is not None:
        args["--skip"] = skip
    if top is not None:
        args["--top"] = top
    result = _client(ctx).list_asset_scores(args)
    _render(result, output, "Asset Quality Scores")
