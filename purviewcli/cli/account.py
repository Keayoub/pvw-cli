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

# Initialize console with UTF-8 encoding for Windows compatibility
console = Console(legacy_windows=False)


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


# Make the account group available for import
__all__ = ['account']
