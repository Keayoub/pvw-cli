import click
from purviewcli.client._domain import Domain

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
    endpoint = ctx.obj.get("endpoint")
    token = ctx.obj.get("token")
    if not endpoint or not token:
        click.echo("[ERROR] Endpoint and token must be set in context.")
        return
    domain_client = Domain(endpoint, token)
    try:
        # Create the domain using the correct API and friendlyName
        result = domain_client.create_domain(domain_name, friendly_name, description)
        click.echo(f"[SUCCESS] Governance domain created: {result}")
        if collection:
            click.echo(f"[INFO] To associate collection '{collection}' with domain '{domain_name}', set the 'domain' attribute on assets in that collection.")
    except Exception as e:
        click.echo(f"[ERROR] Failed to create governance domain: {e}")

@domain.command(help="List all governance domains.")
@click.pass_context
def list(ctx):
    """List all governance domains."""
    endpoint = ctx.obj.get("endpoint")
    token = ctx.obj.get("token")
    if not endpoint or not token:
        click.echo("[ERROR] Endpoint and token must be set in context.")
        return
    domain_client = Domain(endpoint, token)
    try:
        result = domain_client.list_domains()
        click.echo(result)
    except Exception as e:
        click.echo(f"[ERROR] Failed to list governance domains: {e}")

@domain.command(help="Get a governance domain by name.")
@click.argument("domain_name")
@click.pass_context
def get(ctx, domain_name):
    """Get a governance domain by name."""
    endpoint = ctx.obj.get("endpoint")
    token = ctx.obj.get("token")
    if not endpoint or not token:
        click.echo("[ERROR] Endpoint and token must be set in context.")
        return
    domain_client = Domain(endpoint, token)
    try:
        result = domain_client.get_domain(domain_name)
        click.echo(result)
    except Exception as e:
        click.echo(f"[ERROR] Failed to get governance domain: {e}")

@domain.command(help="Update a governance domain's friendly name and/or description.")
@click.argument("domain_name")
@click.option("--friendly-name", help="A new user-friendly display name for the domain")
@click.option("--description", help="A new description for the domain")
@click.pass_context
def update(ctx, domain_name, friendly_name, description):
    """Update a governance domain's friendly name and/or description."""
    endpoint = ctx.obj.get("endpoint")
    token = ctx.obj.get("token")
    if not endpoint or not token:
        click.echo("[ERROR] Endpoint and token must be set in context.")
        return
    domain_client = Domain(endpoint, token)
    try:
        result = domain_client.update_domain(domain_name, friendly_name, description)
        click.echo(result)
    except Exception as e:
        click.echo(f"[ERROR] Failed to update governance domain: {e}")

@domain.command(help="Delete a governance domain by name.")
@click.argument("domain_name")
@click.pass_context
def delete(ctx, domain_name):
    """Delete a governance domain by name."""
    endpoint = ctx.obj.get("endpoint")
    token = ctx.obj.get("token")
    if not endpoint or not token:
        click.echo("[ERROR] Endpoint and token must be set in context.")
        return
    domain_client = Domain(endpoint, token)
    try:
        result = domain_client.delete_domain(domain_name)
        click.echo(result)
    except Exception as e:
        click.echo(f"[ERROR] Failed to delete governance domain: {e}")
