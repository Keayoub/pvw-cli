"""
Access Purview insight reports and analytics using modular Click-based commands.

Usage:
  insight asset-distribution           Show asset distribution insight
  insight files-aggregation            Show files aggregation insight
  insight files-without-resource-set   Show files without resource set insight
  insight scan-status-summary          Show scan status summary insight
  insight scan-status-summary-by-ts    Show scan status summary by timestamp insight
  insight tags                         Show tags insight
  insight tags-time-series             Show tags time series insight
  insight --help                       Show this help message and exit

Options:
  -h --help                            Show this help message and exit
"""

import click
import json
from .console_utils import get_console

console = get_console()

@click.group()
def insight():
    """
    Access Purview insight reports and analytics.
    """
    pass

@insight.command()
def asset_distribution():
    """Show asset distribution insight"""
    try:
        from purviewcli.client._insight import Insight
        client = Insight()
        result = client.assetDistribution({})
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@insight.command()
def files_aggregation():
    """Show files aggregation insight"""
    try:
        from purviewcli.client._insight import Insight
        client = Insight()
        result = client.filesAggregation({})
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@insight.command()
def files_without_resource_set():
    """Show files without resource set insight"""
    try:
        from purviewcli.client._insight import Insight
        client = Insight()
        result = client.filesWithoutResourceSet({})
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@insight.command()
@click.option('--number-of-days', default=30, show_default=True, type=int, help='Trailing time period in days')
def scan_status_summary(number_of_days):
    """Show scan status summary insight"""
    try:
        from purviewcli.client._insight import Insight
        client = Insight()
        args = {'--numberOfDays': number_of_days}
        result = client.scanStatusSummary(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@insight.command()
@click.option('--number-of-days', default=30, show_default=True, type=int, help='Trailing time period in days')
def scan_status_summary_by_ts(number_of_days):
    """Show scan status summary by timestamp insight"""
    try:
        from purviewcli.client._insight import Insight
        client = Insight()
        args = {'--numberOfDays': number_of_days}
        result = client.scanStatusSummaryByTs(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@insight.command()
def tags():
    """Show tags insight"""
    try:
        from purviewcli.client._insight import Insight
        client = Insight()
        result = client.tags({})
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@insight.command()
def tags_time_series():
    """Show tags time series insight"""
    try:
        from purviewcli.client._insight import Insight
        client = Insight()
        result = client.tagsTimeSeries({})
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

# Make the insight group available for import
__all__ = ['insight']
