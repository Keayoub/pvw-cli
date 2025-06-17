import click
import os
import json
from purviewcli.client._domain import Domain
from rich.console import Console

console = Console()

def get_endpoint_and_token(ctx):
    """Get endpoint and token from context or environment variables."""
    endpoint = ctx.obj.get("endpoint") or os.environ.get("PURVIEW_ENDPOINT")
    token = ctx.obj.get("token") or os.environ.get("PURVIEW_TOKEN")
    
    if not endpoint:
        raise click.ClickException(
            "[ERROR] Endpoint not found. Set with --endpoint or PURVIEW_ENDPOINT environment variable"
        )
    if not token:
        raise click.ClickException(
            "[ERROR] Token not found. Set with --token or PURVIEW_TOKEN environment variable"
        )
    
    return endpoint, token

@click.group(help="Manage governance domains in Microsoft Purview using the official Governance Domain API. Domains are business-level groupings for stewardship, policy, and reporting. Use this command to create, list, and manage governance domains visible in the Purview Governance Domains section.")
def domain():
    pass

@domain.command(help="Create a new governance domain. The domain will be visible in the Governance domains section of the Purview portal. Optionally, specify a collection to associate assets with this domain.")
@click.option("--domain-name", required=True, help="The unique name of the governance domain")
@click.option("--friendly-name", help="A user-friendly display name for the domain")
@click.option("--description", help="Description of the governance domain")
@click.option("--collection", help="The collection to associate with this domain (optional)")
@click.pass_context
def create(ctx, domain_name, friendly_name, description, collection):
    """Create a new governance domain and optionally map it to a collection."""
    try:
        endpoint, token = get_endpoint_and_token(ctx)
        domain_client = Domain(endpoint, token)
        result = domain_client.create_domain(domain_name, friendly_name, description)
        console.print(f"[green]SUCCESS:[/green] Governance domain created: {domain_name}")
        console.print(json.dumps(result, indent=2))
        if collection:
            console.print(f"\n[yellow]INFO:[/yellow] To associate collection '{collection}' with domain '{domain_name}', set the 'domain' attribute on assets in that collection.")
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to create governance domain: {e}")

@domain.command(help="List all governance domains.")
@click.pass_context
def list(ctx):
    """List all governance domains."""
    try:
        endpoint, token = get_endpoint_and_token(ctx)
        domain_client = Domain(endpoint, token)
        result = domain_client.list_domains()
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to list governance domains: {e}")

@domain.command(help="Get a governance domain by name.")
@click.argument("domain_name")
@click.pass_context
def get(ctx, domain_name):
    """Get a governance domain by name."""
    try:
        endpoint, token = get_endpoint_and_token(ctx)
        domain_client = Domain(endpoint, token)
        result = domain_client.get_domain(domain_name)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to get governance domain: {e}")

@domain.command(help="Update a governance domain's friendly name and/or description.")
@click.argument("domain_name")
@click.option("--friendly-name", help="A new user-friendly display name for the domain")
@click.option("--description", help="A new description for the domain")
@click.pass_context
def update(ctx, domain_name, friendly_name, description):
    """Update a governance domain's friendly name and/or description."""
    try:
        endpoint, token = get_endpoint_and_token(ctx)
        domain_client = Domain(endpoint, token)
        result = domain_client.update_domain(domain_name, friendly_name, description)
        console.print(f"[green]SUCCESS:[/green] Updated governance domain: {domain_name}")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to update governance domain: {e}")

@domain.command(help="Delete a governance domain by name.")
@click.argument("domain_name")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
@click.pass_context
def delete(ctx, domain_name, force):
    """Delete a governance domain by name."""
    try:
        if not force and not click.confirm(f"Are you sure you want to delete domain '{domain_name}'?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
            
        endpoint, token = get_endpoint_and_token(ctx)
        domain_client = Domain(endpoint, token)
        result = domain_client.delete_domain(domain_name)
        console.print(f"[green]SUCCESS:[/green] Deleted governance domain: {domain_name}")
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to delete governance domain: {e}")
