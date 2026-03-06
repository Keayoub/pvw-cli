"""
Diagnostic and performance monitoring commands for the Purview CLI.
Includes cache statistics, performance metrics, and optimization guidance.
"""

import click
import json
from .console_utils import get_console
from rich.table import Table

console = get_console()


@click.group()
@click.pass_context
def diagnostics(ctx):
    """
    Performance diagnostics and cache management.
    """
    pass


@diagnostics.command("cache-stats")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.pass_context
def cache_stats(ctx, json_output):
    """
    Show client singleton cache and query cache statistics.
    
    Diagnostics include:
    - Active client instances by profile
    - Query cache hit rate and entries
    - Memory usage estimates
    """
    try:
        from purviewcli.client.client_cache import cache_stats as client_cache_stats
        from purviewcli.client.query_cache import get_read_query_cache

        client_stats = client_cache_stats()
        query_cache = get_read_query_cache()
        query_stats = query_cache.stats()

        if json_output:
            stats = {
                "client_cache": client_stats,
                "query_cache": query_stats,
            }
            print(json.dumps(stats, indent=2))
        else:
            console.print("[cyan]== CACHE STATISTICS ==[/cyan]")

            # Client cache stats
            table1 = Table(title="Client Singleton Cache")
            table1.add_column("Metric", style="cyan")
            table1.add_column("Value", style="green")
            for key, value in client_stats.items():
                table1.add_row(key.replace("_", " ").title(), str(value))
            console.print(table1)

            # Query cache stats
            table2 = Table(title="Read-Query Cache")
            table2.add_column("Metric", style="cyan")
            table2.add_column("Value", style="green")
            for key, value in query_stats.items():
                table2.add_row(key.replace("_", " ").title(), str(value))
            console.print(table2)

            console.print("\n[dim]Cache helps reduce:[/dim]")
            console.print("  - Credential initialization overhead")
            console.print("  - API round-trip latency for repeated queries")
            console.print("  - Connection setup time between commands")

    except Exception as e:
        console.print(f"[red][X] Error retrieving cache stats: {str(e)}[/red]")


@diagnostics.command("profile-info")
@click.pass_context
def profile_info(ctx):
    """
    Show current authentication profile and cache scope.
    """
    try:
        profile = ctx.obj.get("profile", "default")
        console.print(f"[cyan]Current Profile:[/cyan] [green]{profile}[/green]")
        console.print("[dim]Cache is scoped to this profile to prevent cross-profile contamination.[/dim]")
        console.print(f"[dim]All cached clients and queries are isolated to '{profile}'.[/dim]")

    except Exception as e:
        console.print(f"[red][X] Error: {str(e)}[/red]")


@diagnostics.command("clear-cache")
@click.option("--confirm", is_flag=True, help="Skip confirmation prompt")
@click.pass_context
def clear_cache(ctx, confirm):
    """
    Clear all cached client instances and query results.
    
    Use this if you encounter stale data or want to reset optimizations.
    """
    try:
        if not confirm:
            if not click.confirm("[yellow]Clear all caches?[/yellow]"):
                console.print("[dim]Cancelled[/dim]")
                return

        from purviewcli.client.client_cache import clear_client_cache
        from purviewcli.client.query_cache import get_read_query_cache

        profile = ctx.obj.get("profile", "default")
        clear_client_cache(profile=profile)
        query_cache = get_read_query_cache()
        query_cache.clear()

        console.print(f"[green][OK] Cache cleared for profile '{profile}'[/green]")

    except Exception as e:
        console.print(f"[red][X] Error clearing cache: {str(e)}[/red]")
