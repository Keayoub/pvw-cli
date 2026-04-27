"""
Manage Purview account and collections using modular Click-based commands.

Usage:
  account get-account           Get account information
  account get-access-keys       Get account access keys
  account regenerate-access-keys Regenerate account access keys
  account update-account        Update account information
  account get-collections       Get all collections
  account get-collection        Get specific collection information
  account --help                Show this help message and exit

Options:
  -h --help                     Show this help message and exit
  
"""

import json
import click
from .console_utils import get_console

console = get_console()


@click.group()
@click.pass_context
def account(ctx):
    """
    Manage Purview account and collections.
    """
    pass


@account.command()
@click.pass_context
def get_account(ctx):
    """Get account information"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account get-account command[/yellow]")
            console.print("[green][OK] Mock account get-account completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.accountRead(args)

        if result:
            console.print("[green][OK] Account information retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Account get-account completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account get-account: {str(e)}[/red]")


@account.command()
@click.pass_context
def get_access_keys(ctx):
    """Get account access keys"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account get-access-keys command[/yellow]")
            console.print("[green][OK] Mock account get-access-keys completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.accountReadAccessKeys(args)

        if result:
            console.print("[green][OK] Access keys retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Account get-access-keys completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account get-access-keys: {str(e)}[/red]")


@account.command()
@click.option('--key-type', required=True, 
              type=click.Choice(['AtlasKafkaPrimaryKey', 'AtlasKafkaSecondaryKey']),
              help='The access key type to regenerate')
@click.pass_context
def regenerate_access_keys(ctx, key_type):
    """Regenerate account access keys"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account regenerate-access-keys command[/yellow]")
            console.print(f"[dim]Key Type: {key_type}[/dim]")
            console.print("[green][OK] Mock account regenerate-access-keys completed successfully[/green]")
            return

        args = {"--keyType": key_type}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.accountRegenerateAccessKey(args)

        if result:
            console.print("[green][OK] Access keys regenerated successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Account regenerate-access-keys completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account regenerate-access-keys: {str(e)}[/red]")


@account.command()
@click.option('--friendly-name', required=True, help='The friendly name for the azure resource')
@click.pass_context
def update_account(ctx, friendly_name):
    """Update account information"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account update-account command[/yellow]")
            console.print(f"[dim]Friendly Name: {friendly_name}[/dim]")
            console.print("[green][OK] Mock account update-account completed successfully[/green]")
            return

        args = {"--friendlyName": friendly_name}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.accountUpdate(args)

        if result:
            console.print("[green][OK] Account updated successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Account update-account completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account update-account: {str(e)}[/red]")


@account.command()
@click.pass_context
def get_collections(ctx):
    """Get all collections"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account get-collections command[/yellow]")
            console.print("[green][OK] Mock account get-collections completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._collections import Collections
        account_client = Collections()
        result = account_client.collectionsRead(args)

        if result:
            console.print("[green][OK] Collections retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Account get-collections completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account get-collections: {str(e)}[/red]")


@account.command()
@click.option('--collection-name', required=True, help='The technical name of the collection')
@click.pass_context
def get_collection(ctx, collection_name):
    """Get specific collection information"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account get-collection command[/yellow]")
            console.print(f"[dim]Collection Name: {collection_name}[/dim]")
            console.print("[green][OK] Mock account get-collection completed successfully[/green]")
            return

        args = {"--collectionName": collection_name}

        from purviewcli.client._collections import Collections
        account_client = Collections()
        result = account_client.collectionsRead(args)

        if result:
            console.print("[green][OK] Collection information retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Account get-collection completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account get-collection: {str(e)}[/red]")


@account.command()
@click.option('--output', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def analytics(ctx, output):
    """Get account analytics including entity counts, collection metrics, and storage usage.
    
    Provides comprehensive analytics data for the Purview account including:
    - Total entity counts by type
    - Collection statistics
    - Storage usage metrics
    - Activity trends
    
    Examples:
        # View analytics in table format
        pvw account analytics
        
        # Get analytics as JSON
        pvw account analytics --output json
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account analytics command[/yellow]")
            console.print("[green][OK] Mock account analytics completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.accountReadAnalytics(args)

        if result:
            if output == 'json':
                console.print(json.dumps(result, indent=2))
            else:
                # Display analytics in table format
                console.print(f"\n[bold cyan]Account Analytics[/bold cyan]\n")
                
                try:
                    from rich.table import Table
                    
                    # Entity counts table
                    if 'entityCounts' in result:
                        entity_table = Table(title="Entity Counts by Type")
                        entity_table.add_column("Entity Type", style="cyan")
                        entity_table.add_column("Count", style="green", justify="right")
                        
                        for entity_type, count in result['entityCounts'].items():
                            entity_table.add_row(entity_type, str(count))
                        
                        console.print(entity_table)
                        console.print()
                    
                    # Collection metrics
                    if 'collections' in result:
                        console.print(f"[cyan]Collections:[/cyan] {result['collections']}")
                    
                    # Storage usage
                    if 'storageUsage' in result:
                        storage = result['storageUsage']
                        console.print(f"[cyan]Storage Used:[/cyan] {storage.get('used', 'N/A')}")
                        console.print(f"[cyan]Storage Limit:[/cyan] {storage.get('limit', 'N/A')}")
                    
                    # Activity metrics
                    if 'activity' in result:
                        activity = result['activity']
                        console.print(f"\n[cyan]Recent Activity:[/cyan]")
                        console.print(f"  Scans: {activity.get('scans', 0)}")
                        console.print(f"  Lineages: {activity.get('lineages', 0)}")
                        console.print(f"  Classifications: {activity.get('classifications', 0)}")
                    
                except ImportError:
                    # Fallback if Rich isn't available
                    console.print(json.dumps(result, indent=2))
            
            console.print("\n[green][OK] Account analytics retrieved successfully[/green]")
        else:
            console.print("[yellow][!] No analytics data available[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account analytics: {str(e)}[/red]")


@account.command()
@click.option('--output', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def usage(ctx, output):
    """Get account resource usage statistics.
    
    Provides detailed usage metrics including:
    - API call counts and limits
    - Storage consumption
    - Scan usage
    - Active connections
    
    Examples:
        # View usage in table format
        pvw account usage
        
        # Get usage as JSON
        pvw account usage --output json
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account usage command[/yellow]")
            console.print("[green][OK] Mock account usage completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.accountReadUsage(args)

        if result:
            if output == 'json':
                console.print(json.dumps(result, indent=2))
            else:
                # Display usage in table format
                console.print(f"\n[bold cyan]Account Usage Statistics[/bold cyan]\n")
                
                try:
                    from rich.table import Table
                    
                    usage_table = Table(title="Resource Usage")
                    usage_table.add_column("Resource", style="cyan")
                    usage_table.add_column("Current", style="yellow", justify="right")
                    usage_table.add_column("Limit", style="green", justify="right")
                    usage_table.add_column("Utilization", style="magenta", justify="right")
                    
                    if 'usage' in result:
                        for resource, metrics in result['usage'].items():
                            current = metrics.get('current', 0)
                            limit = metrics.get('limit', 'Unlimited')
                            if isinstance(limit, (int, float)) and limit > 0:
                                utilization = f"{(current / limit * 100):.1f}%"
                            else:
                                utilization = "N/A"
                            
                            usage_table.add_row(
                                resource,
                                str(current),
                                str(limit),
                                utilization
                            )
                    
                    console.print(usage_table)
                    
                except ImportError:
                    console.print(json.dumps(result, indent=2))
            
            console.print("\n[green][OK] Account usage statistics retrieved successfully[/green]")
        else:
            console.print("[yellow][!] No usage data available[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account usage: {str(e)}[/red]")


@account.command()
@click.option('--output', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def limits(ctx, output):
    """Get account resource limits and quotas.
    
    Displays configured limits and quotas for the Purview account including:
    - Entity limits
    - Scan limits
    - Storage limits
    - API rate limits
    
    Examples:
        # View limits in table format
        pvw account limits
        
        # Get limits as JSON
        pvw account limits --output json
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] account limits command[/yellow]")
            console.print("[green][OK] Mock account limits completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.accountReadLimits(args)

        if result:
            if output == 'json':
                console.print(json.dumps(result, indent=2))
            else:
                # Display limits in table format
                console.print(f"\n[bold cyan]Account Resource Limits[/bold cyan]\n")
                
                try:
                    from rich.table import Table
                    
                    limits_table = Table(title="Resource Limits")
                    limits_table.add_column("Resource", style="cyan")
                    limits_table.add_column("Limit", style="green", justify="right")
                    limits_table.add_column("Description", style="dim")
                    
                    if 'limits' in result:
                        for resource, details in result['limits'].items():
                            limit_value = details.get('value', 'Unlimited')
                            description = details.get('description', '')
                            
                            limits_table.add_row(
                                resource,
                                str(limit_value),
                                description
                            )
                    
                    console.print(limits_table)
                    
                except ImportError:
                    console.print(json.dumps(result, indent=2))
            
            console.print("\n[green][OK] Account limits retrieved successfully[/green]")
        else:
            console.print("[yellow][!] No limits data available[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing account limits: {str(e)}[/red]")


# Make the account group available for import
__all__ = ['account']
