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
from rich.console import Console

console = Console()


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
            console.print("[yellow]🎭 Mock: account get-account command[/yellow]")
            console.print("[green]✓ Mock account get-account completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.getAccount(args)

        if result:
            console.print("[green]✓ Account information retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Account get-account completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing account get-account: {str(e)}[/red]")


@account.command()
@click.pass_context
def get_access_keys(ctx):
    """Get account access keys"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: account get-access-keys command[/yellow]")
            console.print("[green]✓ Mock account get-access-keys completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.getAccessKeys(args)

        if result:
            console.print("[green]✓ Access keys retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Account get-access-keys completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing account get-access-keys: {str(e)}[/red]")


@account.command()
@click.option('--key-type', required=True, 
              type=click.Choice(['AtlasKafkaPrimaryKey', 'AtlasKafkaSecondaryKey']),
              help='The access key type to regenerate')
@click.pass_context
def regenerate_access_keys(ctx, key_type):
    """Regenerate account access keys"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: account regenerate-access-keys command[/yellow]")
            console.print(f"[dim]Key Type: {key_type}[/dim]")
            console.print("[green]✓ Mock account regenerate-access-keys completed successfully[/green]")
            return

        args = {"--keyType": key_type}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.regenerateAccessKeys(args)

        if result:
            console.print("[green]✓ Access keys regenerated successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Account regenerate-access-keys completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing account regenerate-access-keys: {str(e)}[/red]")


@account.command()
@click.option('--friendly-name', required=True, help='The friendly name for the azure resource')
@click.pass_context
def update_account(ctx, friendly_name):
    """Update account information"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: account update-account command[/yellow]")
            console.print(f"[dim]Friendly Name: {friendly_name}[/dim]")
            console.print("[green]✓ Mock account update-account completed successfully[/green]")
            return

        args = {"--friendlyName": friendly_name}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.updateAccount(args)

        if result:
            console.print("[green]✓ Account updated successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Account update-account completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing account update-account: {str(e)}[/red]")


@account.command()
@click.pass_context
def get_collections(ctx):
    """Get all collections"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: account get-collections command[/yellow]")
            console.print("[green]✓ Mock account get-collections completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.getCollections(args)

        if result:
            console.print("[green]✓ Collections retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Account get-collections completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing account get-collections: {str(e)}[/red]")


@account.command()
@click.option('--collection-name', required=True, help='The technical name of the collection')
@click.pass_context
def get_collection(ctx, collection_name):
    """Get specific collection information"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: account get-collection command[/yellow]")
            console.print(f"[dim]Collection Name: {collection_name}[/dim]")
            console.print("[green]✓ Mock account get-collection completed successfully[/green]")
            return

        args = {"--collectionName": collection_name}

        from purviewcli.client._account import Account
        account_client = Account()
        result = account_client.getCollection(args)

        if result:
            console.print("[green]✓ Collection information retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Account get-collection completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing account get-collection: {str(e)}[/red]")


# Make the account group available for import
__all__ = ['account']
