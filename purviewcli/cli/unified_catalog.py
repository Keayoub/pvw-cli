"""
Microsoft Purview Unified Catalog CLI Commands
Replaces data_product functionality with comprehensive Unified Catalog operations
"""

import click
import csv
import json
import tempfile
import os
import time
from .console_utils import get_console
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from purviewcli.client._unified_catalog import UnifiedCatalogClient

console = get_console()


def _format_json_output(data):
    """Format JSON output with syntax highlighting using Rich"""
    # Pretty print JSON with syntax highlighting
    json_str = json.dumps(data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(syntax)


@click.group()
def uc():
    """Manage Unified Catalog in Microsoft Purview (domains, terms, data products, OKRs, CDEs)."""
    pass


# ========================================
# GOVERNANCE DOMAINS
# ========================================


@uc.group()
def domain():
    """Manage governance domains."""
    pass


@domain.command()
@click.option("--name", required=True, help="Name of the governance domain")
@click.option(
    "--description", required=False, default="", help="Description of the governance domain"
)
@click.option(
    "--type",
    required=False,
    default="FunctionalUnit",
    help="Type of governance domain (default: FunctionalUnit). Note: UC API currently only accepts 'FunctionalUnit'.",
)
@click.option(
    "--owner-id",
    required=False,
    help="Owner Entra ID (can be specified multiple times)",
    multiple=True,
)
@click.option(
    "--status",
    required=False,
    default="Draft",
    type=click.Choice(["Draft", "Published", "Archived"]),
    help="Status of the governance domain",
)
@click.option(
    "--parent-id",
    required=False,
    help="Parent governance domain ID (create as subdomain under this domain)",
)
@click.option(
    "--payload-file",
    required=False,
    type=click.Path(exists=True),
    help="Optional JSON payload file to use for creating the domain (overrides flags if provided)",
)
def create(name, description, type, owner_id, status, parent_id, payload_file):
    """Create a new governance domain."""
    try:
        client = UnifiedCatalogClient()

        # Build args dictionary in Purview CLI format
        # If payload-file is provided we will let the client read the file directly
        # otherwise build args from individual flags.
        args = {}
        # Note: click will pass None for owner_id if not provided, but multiple=True returns ()
        # We'll only include values if payload-file not used.
        if locals().get('payload_file'):
            args = {"--payloadFile": locals().get('payload_file')}
        else:
            args = {
                "--name": [name],
                "--description": [description],
                "--type": [type],
                "--status": [status],
            }
            if owner_id:
                args["--owner-id"] = list(owner_id)
            # include parent id if provided
            parent_id = locals().get('parent_id')
            if parent_id:
                # use a consistent arg name for client lookup
                args["--parent-domain-id"] = [parent_id]

        # Call the client to create the governance domain
        result = client.create_governance_domain(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green] SUCCESS:[/green] Created governance domain '{name}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@domain.command(name="list")
@click.option(
    "--output",
    type=click.Choice(["table", "json", "jsonc"]),
    default="table",
    help="Output format: table (default, formatted), json (plain, parseable), jsonc (colored JSON)"
)
def list_domains(output):
    """List all governance domains.
    
    Output formats:
    - table: Formatted table output with Rich (default)
    - json: Plain JSON for scripting (use with PowerShell ConvertFrom-Json)
    - jsonc: Colored JSON with syntax highlighting for viewing
    """
    try:
        client = UnifiedCatalogClient()
        args = {}  # No arguments needed for list operation
        result = client.get_governance_domains(args)

        if not result:
            console.print("[yellow]No governance domains found.[/yellow]")
            return

        # Handle both list and dict responses
        if isinstance(result, (list, tuple)):
            domains = result
        elif isinstance(result, dict):
            domains = result.get("value", [])
        else:
            domains = []

        if not domains:
            console.print("[yellow]No governance domains found.[/yellow]")
            return

        # Handle output format
        if output == "json":
            # Plain JSON for scripting (PowerShell compatible)
            print(json.dumps(domains, indent=2))
            return
        elif output == "jsonc":
            # Colored JSON for viewing
            _format_json_output(domains)
            return

        table = Table(title="Governance Domains")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Owners", style="magenta")

        for domain in domains:
            owners = ", ".join(
                [o.get("name", o.get("id", "Unknown")) for o in domain.get("owners", [])]
            )
            table.add_row(
                domain.get("id", "N/A"),
                domain.get("name", "N/A"),
                domain.get("type", "N/A"),
                domain.get("status", "N/A"),
                owners or "None",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@domain.command()
@click.option("--domain-id", required=True, help="ID of the governance domain")
def show(domain_id):
    """Show details of a governance domain."""
    try:
        client = UnifiedCatalogClient()
        args = {"--domain-id": [domain_id]}
        result = client.get_governance_domain_by_id(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and result.get("error"):
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Domain not found')}")
            return

        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


# ========================================
# DATA PRODUCTS (for backwards compatibility)
# ========================================


@uc.group()
def dataproduct():
    """Manage data products."""
    pass


@dataproduct.command()
@click.option("--name", required=True, help="Name of the data product")
@click.option("--description", required=False, default="", help="Description of the data product")
@click.option("--domain-id", required=True, help="Governance domain ID")
@click.option(
    "--type",
    required=False,
    default="Operational",
    type=click.Choice(["Operational", "Analytical", "Reference"]),
    help="Type of data product",
)
@click.option(
    "--owner-id",
    required=False,
    help="Owner Entra ID (can be specified multiple times)",
    multiple=True,
)
@click.option("--business-use", required=False, default="", help="Business use description")
@click.option(
    "--update-frequency",
    required=False,
    default="Weekly",
    type=click.Choice(["Daily", "Weekly", "Monthly", "Quarterly", "Annually"]),
    help="Update frequency",
)
@click.option("--endorsed", is_flag=True, help="Mark as endorsed")
@click.option(
    "--status",
    required=False,
    default="Draft",
    type=click.Choice(["Draft", "Published", "Archived"]),
    help="Status of the data product",
)
def create(
    name, description, domain_id, type, owner_id, business_use, update_frequency, endorsed, status
):
    """Create a new data product."""
    try:
        client = UnifiedCatalogClient()
        owners = [{"id": oid} for oid in owner_id] if owner_id else []

        # Build args dictionary in Purview CLI format
        args = {
            "--governance-domain-id": [domain_id],
            "--name": [name],
            "--description": [description],
            "--type": [type],
            "--status": [status],
            "--business-use": [business_use],
            "--update-frequency": [update_frequency],
        }
        if endorsed:
            args["--endorsed"] = ["true"]
        if owners:
            args["--owner-id"] = [owner["id"] for owner in owners]

        result = client.create_data_product(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green] SUCCESS:[/green] Created data product '{name}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command(name="list")
@click.option("--domain-id", required=False, help="Governance domain ID (optional filter)")
@click.option("--status", required=False, help="Status filter (Draft, Published, Archived)")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
def list_data_products(domain_id, status, output_json):
    """List all data products (optionally filtered by domain or status)."""
    try:
        client = UnifiedCatalogClient()

        # Build args dictionary in Purview CLI format
        args = {}
        if domain_id:
            args["--domain-id"] = [domain_id]
        if status:
            args["--status"] = [status]

        result = client.get_data_products(args)

        # Handle both list and dict responses
        if isinstance(result, (list, tuple)):
            products = result
        elif isinstance(result, dict):
            products = result.get("value", [])
        else:
            products = []

        if not products:
            filter_msg = ""
            if domain_id:
                filter_msg += f" in domain '{domain_id}'"
            if status:
                filter_msg += f" with status '{status}'"
            console.print(f"[yellow]No data products found{filter_msg}.[/yellow]")
            return

        # Output in JSON format if requested
        if output_json:
            _format_json_output(products)
            return

        table = Table(title="Data Products")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Domain ID", style="blue", no_wrap=True)
        table.add_column("Status", style="yellow")
        table.add_column("Description", style="white", max_width=50)

        for product in products:
            # Get domain ID and handle "N/A" display
            domain_id = product.get("domain") or product.get("domainId", "")
            domain_display = domain_id if domain_id else "N/A"
            
            # Clean HTML tags from description
            description = product.get("description", "")
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()
            
            table.add_row(
                product.get("id", "N/A"),
                product.get("name", "N/A"),
                domain_display,
                product.get("status", "N/A"),
                (description[:50] + "...") if len(description) > 50 else description,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command()
@click.option("--product-id", required=True, help="ID of the data product")
def show(product_id):
    """Show details of a data product."""
    try:
        client = UnifiedCatalogClient()
        args = {"--product-id": [product_id]}
        result = client.get_data_product_by_id(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Data product not found')}")
            return

        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command()
@click.option("--product-id", required=True, help="ID of the data product to update")
@click.option("--name", required=False, help="Name of the data product")
@click.option("--description", required=False, help="Description of the data product")
@click.option("--domain-id", required=False, help="Governance domain ID")
@click.option(
    "--type",
    required=False,
    type=click.Choice(["Operational", "Analytical", "Reference"]),
    help="Type of data product",
)
@click.option(
    "--owner-id",
    required=False,
    help="Owner Entra ID (can be specified multiple times)",
    multiple=True,
)
@click.option("--business-use", required=False, help="Business use description")
@click.option(
    "--update-frequency",
    required=False,
    type=click.Choice(["Daily", "Weekly", "Monthly", "Quarterly", "Annually"]),
    help="Update frequency",
)
@click.option("--endorsed", is_flag=True, help="Mark as endorsed")
@click.option(
    "--status",
    required=False,
    type=click.Choice(["Draft", "Published", "Archived"]),
    help="Status of the data product",
)
def update(
    product_id, name, description, domain_id, type, owner_id, business_use, update_frequency, endorsed, status
):
    """Update an existing data product."""
    try:
        client = UnifiedCatalogClient()

        # Build args dictionary - only include provided values
        args = {"--product-id": [product_id]}
        
        if name:
            args["--name"] = [name]
        if description is not None:  # Allow empty string
            args["--description"] = [description]
        if domain_id:
            args["--domain-id"] = [domain_id]
        if type:
            args["--type"] = [type]
        if status:
            args["--status"] = [status]
        if business_use is not None:
            args["--business-use"] = [business_use]
        if update_frequency:
            args["--update-frequency"] = [update_frequency]
        if endorsed:
            args["--endorsed"] = ["true"]
        if owner_id:
            args["--owner-id"] = list(owner_id)

        result = client.update_data_product(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green] SUCCESS:[/green] Updated data product '{product_id}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command()
@click.option("--product-id", required=True, help="ID of the data product to delete")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def delete(product_id, yes):
    """Delete a data product."""
    try:
        if not yes:
            confirm = click.confirm(
                f"Are you sure you want to delete data product '{product_id}'?",
                default=False
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return

        client = UnifiedCatalogClient()
        args = {"--product-id": [product_id]}
        result = client.delete_data_product(args)

        # DELETE operations may return empty response on success
        if result is None or (isinstance(result, dict) and not result.get("error")):
            console.print(f"[green] SUCCESS:[/green] Deleted data product '{product_id}'")
        elif isinstance(result, dict) and "error" in result:
                console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
        else:
            console.print(f"[green] SUCCESS:[/green] Deleted data product '{product_id}'")
            if result:
                console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command(name="add-relationship")
@click.option("--product-id", required=True, help="Data product ID (GUID)")
@click.option("--entity-type", required=True, 
              type=click.Choice(["CRITICALDATACOLUMN", "TERM", "DATAASSET", "CRITICALDATAELEMENT"], case_sensitive=False),
              help="Type of entity to relate to")
@click.option("--entity-id", required=True, help="Entity ID (GUID) to relate to")
@click.option("--asset-id", help="Asset ID (GUID) - defaults to entity-id if not provided")
@click.option("--relationship-type", default="Related", help="Relationship type (default: Related)")
@click.option("--description", default="", help="Description of the relationship")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def add_relationship(product_id, entity_type, entity_id, asset_id, relationship_type, description, output):
    """Create a relationship for a data product.
    
    Links a data product to another entity like a critical data column, term, or asset.
    
    Examples:
        pvw uc dataproduct add-relationship --product-id <id> --entity-type CRITICALDATACOLUMN --entity-id <col-id>
        pvw uc dataproduct add-relationship --product-id <id> --entity-type TERM --entity-id <term-id> --description "Primary term"
    """
    try:
        client = UnifiedCatalogClient()
        args = {
            "--product-id": [product_id],
            "--entity-type": [entity_type],
            "--entity-id": [entity_id],
            "--relationship-type": [relationship_type],
            "--description": [description]
        }
        
        if asset_id:
            args["--asset-id"] = [asset_id]
        
        result = client.create_data_product_relationship(args)
        
        if output == "json":
            console.print_json(data=result)
        else:
            if result and isinstance(result, dict):
                console.print("[green]SUCCESS:[/green] Created relationship")
                table = Table(title="Data Product Relationship", show_header=True)
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")
                
                table.add_row("Entity ID", result.get("entityId", "N/A"))
                table.add_row("Relationship Type", result.get("relationshipType", "N/A"))
                table.add_row("Description", result.get("description", "N/A"))
                
                if "systemData" in result:
                    sys_data = result["systemData"]
                    table.add_row("Created By", sys_data.get("createdBy", "N/A"))
                    table.add_row("Created At", sys_data.get("createdAt", "N/A"))
                
                console.print(table)
            else:
                console.print("[green]SUCCESS:[/green] Created relationship")
                
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command(name="list-relationships")
@click.option("--product-id", required=True, help="Data product ID (GUID)")
@click.option("--entity-type", 
              type=click.Choice(["CRITICALDATACOLUMN", "TERM", "DATAASSET", "CRITICALDATAELEMENT"], case_sensitive=False),
              help="Filter by entity type (optional)")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def list_relationships(product_id, entity_type, output):
    """List relationships for a data product.
    
    Shows all entities linked to this data product, optionally filtered by type.
    
    Examples:
        pvw uc dataproduct list-relationships --product-id <id>
        pvw uc dataproduct list-relationships --product-id <id> --entity-type CRITICALDATACOLUMN
    """
    try:
        client = UnifiedCatalogClient()
        args = {"--product-id": [product_id]}
        
        if entity_type:
            args["--entity-type"] = [entity_type]
        
        result = client.get_data_product_relationships(args)
        
        if output == "json":
            console.print_json(data=result)
        else:
            relationships = result.get("value", []) if result else []
            
            if not relationships:
                console.print(f"[yellow]No relationships found for data product '{product_id}'[/yellow]")
                return
            
            table = Table(title=f"Data Product Relationships ({len(relationships)} found)", show_header=True)
            table.add_column("Entity ID", style="cyan")
            table.add_column("Relationship Type", style="white")
            table.add_column("Description", style="white")
            table.add_column("Created", style="dim")
            
            for rel in relationships:
                table.add_row(
                    rel.get("entityId", "N/A"),
                    rel.get("relationshipType", "N/A"),
                    rel.get("description", "")[:50] + ("..." if len(rel.get("description", "")) > 50 else ""),
                    rel.get("systemData", {}).get("createdAt", "N/A")[:10]
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command(name="remove-relationship")
@click.option("--product-id", required=True, help="Data product ID (GUID)")
@click.option("--entity-type", required=True,
              type=click.Choice(["CRITICALDATACOLUMN", "TERM", "DATAASSET", "CRITICALDATAELEMENT"], case_sensitive=False),
              help="Type of entity to unlink")
@click.option("--entity-id", required=True, help="Entity ID (GUID) to unlink")
@click.option("--confirm/--no-confirm", default=True, help="Ask for confirmation before deleting")
def remove_relationship(product_id, entity_type, entity_id, confirm):
    """Delete a relationship between a data product and an entity.
    
    Removes the link between a data product and a specific entity.
    
    Examples:
        pvw uc dataproduct remove-relationship --product-id <id> --entity-type CRITICALDATACOLUMN --entity-id <col-id>
        pvw uc dataproduct remove-relationship --product-id <id> --entity-type TERM --entity-id <term-id> --no-confirm
    """
    try:
        if confirm:
            confirm = click.confirm(
                f"Are you sure you want to delete relationship to {entity_type} '{entity_id}'?",
                default=False
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        client = UnifiedCatalogClient()
        args = {
            "--product-id": [product_id],
            "--entity-type": [entity_type],
            "--entity-id": [entity_id]
        }
        
        result = client.delete_data_product_relationship(args)
        
        # DELETE returns 204 No Content on success
        if result is None or (isinstance(result, dict) and not result.get("error")):
            console.print(f"[green]SUCCESS:[/green] Deleted relationship to {entity_type} '{entity_id}'")
        elif isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
        else:
            console.print(f"[green]SUCCESS:[/green] Deleted relationship")
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command(name="query")
@click.option("--ids", multiple=True, help="Filter by specific product IDs (GUIDs)")
@click.option("--domain-ids", multiple=True, help="Filter by domain IDs (GUIDs)")
@click.option("--name-keyword", help="Filter by name keyword (partial match)")
@click.option("--owners", multiple=True, help="Filter by owner IDs (GUIDs)")
@click.option("--status", type=click.Choice(["Draft", "Published", "Expired"], case_sensitive=False),
              help="Filter by status")
@click.option("--multi-status", multiple=True,
              type=click.Choice(["Draft", "Published", "Expired"], case_sensitive=False),
              help="Filter by multiple statuses")
@click.option("--type", help="Filter by data product type (e.g., Master, Operational)")
@click.option("--types", multiple=True, help="Filter by multiple data product types")
@click.option("--skip", type=int, default=0, help="Number of items to skip (pagination)")
@click.option("--top", type=int, default=100, help="Number of items to return (max 1000)")
@click.option("--order-by-field", help="Field to sort by (e.g., 'name', 'status')")
@click.option("--order-by-direction", type=click.Choice(["asc", "desc"]), default="asc",
              help="Sort direction")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def query_data_products(ids, domain_ids, name_keyword, owners, status, multi_status, type, types,
                       skip, top, order_by_field, order_by_direction, output):
    """Query data products with advanced filters.
    
    Perform complex searches across data products using multiple filter criteria.
    Supports pagination and custom sorting.
    
    Examples:
        # Find all data products in a specific domain
        pvw uc dataproduct query --domain-ids <domain-guid>
        
        # Search by keyword
        pvw uc dataproduct query --name-keyword "customer"
        
        # Filter by owner and status
        pvw uc dataproduct query --owners <user-guid> --status Published
        
        # Pagination example
        pvw uc dataproduct query --skip 0 --top 50 --order-by-field name
        
        # Multiple filters
        pvw uc dataproduct query --domain-ids <guid1> <guid2> --status Published --type Master
    """
    try:
        client = UnifiedCatalogClient()
        args = {}
        
        # Build args dict from parameters
        if ids:
            args["--ids"] = list(ids)
        if domain_ids:
            args["--domain-ids"] = list(domain_ids)
        if name_keyword:
            args["--name-keyword"] = [name_keyword]
        if owners:
            args["--owners"] = list(owners)
        if status:
            args["--status"] = [status]
        if multi_status:
            args["--multi-status"] = list(multi_status)
        if type:
            args["--type"] = [type]
        if types:
            args["--types"] = list(types)
        if skip:
            args["--skip"] = [str(skip)]
        if top:
            args["--top"] = [str(top)]
        if order_by_field:
            args["--order-by-field"] = [order_by_field]
            args["--order-by-direction"] = [order_by_direction]
        
        result = client.query_data_products(args)
        
        if output == "json":
            console.print_json(data=result)
        else:
            products = result.get("value", []) if result else []
            
            if not products:
                console.print("[yellow]No data products found matching the query.[/yellow]")
                return
            
            # Check for pagination
            next_link = result.get("nextLink")
            if next_link:
                console.print(f"[dim]Note: More results available (nextLink provided)[/dim]\n")
            
            table = Table(title=f"Query Results ({len(products)} found)", show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("ID", style="dim", no_wrap=True)
            table.add_column("Domain", style="yellow", no_wrap=True)
            table.add_column("Type", style="green")
            table.add_column("Status", style="white")
            table.add_column("Owner", style="magenta")
            
            for product in products:
                # Extract owner info
                contacts = product.get("contacts", {})
                owners_list = contacts.get("owner", [])
                owner_display = owners_list[0].get("id", "N/A")[:8] if owners_list else "N/A"
                
                table.add_row(
                    product.get("name", "N/A"),
                    product.get("id", "N/A")[:13] + "...",
                    product.get("domain", "N/A")[:13] + "...",
                    product.get("type", "N/A"),
                    product.get("status", "N/A"),
                    owner_display + "..."
                )
            
            console.print(table)
            
            # Show pagination info
            if skip > 0 or next_link:
                console.print(f"\n[dim]Showing items {skip + 1} to {skip + len(products)}[/dim]")
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@dataproduct.command(name="facets")
@click.option("--domain-id", help="Filter by domain ID", required=False)
@click.option("--facet-fields", multiple=True, help="Specific facet fields to retrieve (status, domain, owner, dataAssetCount)")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def get_data_product_facets(domain_id, facet_fields, output):
    """Get facets (aggregated statistics) for Data Products.
    
    Shows distribution of data products by status, domain, asset count, and owner.
    Useful for analytics, dashboards, and building search filters.
    
    Examples:
        # Get all data product facets
        pvw uc dataproduct facets
        
        # Get facets for specific domain
        pvw uc dataproduct facets --domain-id <domain-guid>
        
        # Get specific facet fields only
        pvw uc dataproduct facets --facet-fields status --facet-fields domain
        
        # Export as JSON
        pvw uc dataproduct facets --output json
    """
    try:
        client = UnifiedCatalogClient()
        args = {}
        
        if domain_id:
            args["--domain-id"] = [domain_id]
        if facet_fields:
            args["--facet-fields"] = list(facet_fields)
        
        result = client.get_data_product_facets(args)
        
        if output == "json":
            console.print_json(data=result)
            return
        
        facets = result.get("facets", {})
        total_count = result.get("totalCount", 0)
        
        if not facets:
            console.print("[yellow]No facets data available.[/yellow]")
            return
        
        console.print(f"\n[bold]📦 Data Products Facets[/bold] (Total: {total_count} products)\n")
        
        # Define facet display order and styling
        facet_order = ["status", "domain", "dataAssetCount", "owner"]
        facet_icons = {
            "status": "📊",
            "domain": "🏢",
            "dataAssetCount": "💾",
            "owner": "👤"
        }
        
        for facet_name in facet_order:
            if facet_name not in facets:
                continue
                
            facet_values = facets[facet_name]
            icon = facet_icons.get(facet_name, "📌")
            
            table = Table(title=f"{icon} {facet_name.capitalize()} Distribution", show_header=True)
            table.add_column("Value", style="cyan")
            table.add_column("Count", style="green", justify="right")
            table.add_column("Percentage", style="yellow", justify="right")
            
            # Sort by count descending
            sorted_values = sorted(facet_values.items(), key=lambda x: x[1], reverse=True)
            
            for value, count in sorted_values:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                
                # Add color coding for status
                if facet_name == "status":
                    if value.lower() == "published":
                        value_display = f"[green bold]{value}[/green bold]"
                    elif value.lower() == "draft":
                        value_display = f"[yellow]{value}[/yellow]"
                    elif value.lower() == "archived":
                        value_display = f"[dim]{value}[/dim]"
                    else:
                        value_display = str(value)
                else:
                    value_display = str(value)
                
                table.add_row(
                    value_display,
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(table)
            console.print()  # Blank line between tables
        
        # Display any remaining facets not in the predefined order
        for facet_name, facet_values in facets.items():
            if facet_name in facet_order:
                continue
                
            table = Table(title=f"{facet_name.capitalize()} Distribution", show_header=True)
            table.add_column("Value", style="cyan")
            table.add_column("Count", style="green", justify="right")
            table.add_column("Percentage", style="yellow", justify="right")
            
            sorted_values = sorted(facet_values.items(), key=lambda x: x[1], reverse=True)
            
            for value, count in sorted_values:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                table.add_row(
                    str(value),
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(table)
            console.print()
        
        # Show summary metrics
        if "status" in facets:
            published = facets["status"].get("Published", 0)
            draft = facets["status"].get("Draft", 0)
            console.print("[bold]✅ Product Readiness:[/bold]")
            console.print(f"  • Published: {published} ({published/total_count*100:.1f}%)")
            console.print(f"  • Draft: {draft} ({draft/total_count*100:.1f}%)")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


# ========================================
# GLOSSARIES
# ========================================
@uc.group()
def glossary():
    """Manage glossaries (for finding glossary GUIDs)."""
    pass


@glossary.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
def list_glossaries(output_json):
    """List all glossaries with their GUIDs."""
    try:
        from purviewcli.client._glossary import Glossary
        
        client = Glossary()
        result = client.glossaryRead({})

        # Normalize response
        if isinstance(result, dict):
            glossaries = result.get("value", []) or []
        elif isinstance(result, (list, tuple)):
            glossaries = result
        else:
            glossaries = []

        if not glossaries:
            console.print("[yellow]No glossaries found.[/yellow]")
            return

        # Output in JSON format if requested
        if output_json:
            _format_json_output(glossaries)
            return

        table = Table(title="Glossaries")
        table.add_column("GUID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Qualified Name", style="yellow")
        table.add_column("Description", style="white")

        for g in glossaries:
            if not isinstance(g, dict):
                continue
            table.add_row(
                g.get("guid", "N/A"),
                g.get("name", "N/A"),
                g.get("qualifiedName", "N/A"),
                (g.get("shortDescription", "")[:60] + "...") if len(g.get("shortDescription", "")) > 60 else g.get("shortDescription", ""),
            )

        console.print(table)
        console.print("\n[dim]Tip: Use the GUID with --glossary-guid option when listing/creating terms[/dim]")

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@glossary.command(name="create")
@click.option("--name", required=True, help="Name of the glossary")
@click.option("--description", required=False, default="", help="Description of the glossary")
@click.option("--domain-id", required=False, help="Associate with governance domain ID (optional)")
def create_glossary(name, description, domain_id):
    """Create a new glossary."""
    try:
        from purviewcli.client._glossary import Glossary
        
        client = Glossary()
        
        # Build qualified name - include domain_id if provided
        if domain_id:
            qualified_name = f"{name}@{domain_id}"
        else:
            qualified_name = name
        
        payload = {
            "name": name,
            "qualifiedName": qualified_name,
            "shortDescription": description,
            "longDescription": description,
        }
        
        result = client.glossaryCreate({"--payloadFile": payload})
        
        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return
        
        guid = result.get("guid") if isinstance(result, dict) else None
        console.print(f"[green] SUCCESS:[/green] Created glossary '{name}'")
        if guid:
            console.print(f"[cyan]GUID:[/cyan] {guid}")
            console.print(f"\n[dim]Use this GUID: --glossary-guid {guid}[/dim]")
        console.print(json.dumps(result, indent=2))
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@glossary.command(name="create-for-domains")
def create_glossaries_for_domains():
    """Create glossaries for all governance domains that don't have one."""
    try:
        from purviewcli.client._glossary import Glossary
        
        uc_client = UnifiedCatalogClient()
        glossary_client = Glossary()
        
        # Get all domains
        domains_result = uc_client.get_governance_domains({})
        if isinstance(domains_result, dict):
            domains = domains_result.get("value", [])
        elif isinstance(domains_result, (list, tuple)):
            domains = domains_result
        else:
            domains = []
        
        if not domains:
            console.print("[yellow]No governance domains found.[/yellow]")
            return
        
        # Get existing glossaries
        glossaries_result = glossary_client.glossaryRead({})
        if isinstance(glossaries_result, dict):
            existing_glossaries = glossaries_result.get("value", [])
        elif isinstance(glossaries_result, (list, tuple)):
            existing_glossaries = glossaries_result
        else:
            existing_glossaries = []
        
        # Build set of domain IDs that already have glossaries (check qualifiedName)
        existing_domain_ids = set()
        for g in existing_glossaries:
            if isinstance(g, dict):
                qn = g.get("qualifiedName", "")
                # Extract domain_id from qualifiedName if it contains @domain_id pattern
                if "@" in qn:
                    domain_id_part = qn.split("@")[-1]
                    existing_domain_ids.add(domain_id_part)
        
        console.print(f"[cyan]Found {len(domains)} governance domains and {len(existing_glossaries)} existing glossaries[/cyan]\n")
        
        created_count = 0
        for domain in domains:
            if not isinstance(domain, dict):
                continue
            
            domain_id = domain.get("id")
            domain_name = domain.get("name")
            
            if not domain_id or not domain_name:
                continue
            
            # Check if glossary already exists for this domain
            if domain_id in existing_domain_ids:
                console.print(f"[dim]⏭  Skipping {domain_name} - glossary already exists[/dim]")
                continue
            
            # Create glossary for this domain
            glossary_name = f"{domain_name} Glossary"
            qualified_name = f"{glossary_name}@{domain_id}"
            
            payload = {
                "name": glossary_name,
                "qualifiedName": qualified_name,
                "shortDescription": f"Glossary for {domain_name} domain",
                "longDescription": f"This glossary contains business terms for the {domain_name} governance domain.",
            }
            
            try:
                result = glossary_client.glossaryCreate({"--payloadFile": payload})
                guid = result.get("guid") if isinstance(result, dict) else None
                
                if guid:
                    console.print(f"[green] Created:[/green] {glossary_name} (GUID: {guid})")
                    created_count += 1
                else:
                    console.print(f"[yellow]  Created {glossary_name} but no GUID returned[/yellow]")
                    
            except Exception as e:
                console.print(f"[red] Failed to create {glossary_name}:[/red] {str(e)}")
        
        console.print(f"\n[cyan]Created {created_count} new glossaries[/cyan]")
        console.print("[dim]Run 'pvw uc glossary list' to see all glossaries[/dim]")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@glossary.command(name="verify-links")
def verify_glossary_links():
    """Verify which domains have properly linked glossaries."""
    try:
        from purviewcli.client._glossary import Glossary
        
        uc_client = UnifiedCatalogClient()
        glossary_client = Glossary()
        
        # Get all domains
        domains_result = uc_client.get_governance_domains({})
        if isinstance(domains_result, dict):
            domains = domains_result.get("value", [])
        elif isinstance(domains_result, (list, tuple)):
            domains = domains_result
        else:
            domains = []
        
        # Get all glossaries
        glossaries_result = glossary_client.glossaryRead({})
        if isinstance(glossaries_result, dict):
            glossaries = glossaries_result.get("value", [])
        elif isinstance(glossaries_result, (list, tuple)):
            glossaries = glossaries_result
        else:
            glossaries = []
        
        console.print(f"[bold cyan]Governance Domain → Glossary Link Verification[/bold cyan]\n")
        
        table = Table(title="Domain-Glossary Associations")
        table.add_column("Domain Name", style="green")
        table.add_column("Domain ID", style="cyan", no_wrap=True)
        table.add_column("Linked Glossary", style="yellow")
        table.add_column("Glossary GUID", style="magenta", no_wrap=True)
        table.add_column("Status", style="white")
        
        # Build a map of domain_id -> glossary info
        domain_glossary_map = {}
        for g in glossaries:
            if not isinstance(g, dict):
                continue
            qn = g.get("qualifiedName", "")
            # Check if qualifiedName contains @domain_id pattern
            if "@" in qn:
                domain_id_part = qn.split("@")[-1]
                domain_glossary_map[domain_id_part] = {
                    "name": g.get("name"),
                    "guid": g.get("guid"),
                    "qualifiedName": qn,
                }
        
        linked_count = 0
        unlinked_count = 0
        
        for domain in domains:
            if not isinstance(domain, dict):
                continue
            
            domain_id = domain.get("id")
            domain_name = domain.get("name", "N/A")
            parent_id = domain.get("parentDomainId")
            
            # Skip if no domain_id
            if not domain_id:
                continue
            
            # Show if it's a nested domain
            nested_indicator = " (nested)" if parent_id else ""
            domain_display = f"{domain_name}{nested_indicator}"
            
            if domain_id in domain_glossary_map:
                glossary_info = domain_glossary_map[domain_id]
                table.add_row(
                    domain_display,
                    domain_id[:8] + "...",
                    glossary_info["name"],
                    glossary_info["guid"][:8] + "...",
                    "[green] Linked[/green]"
                )
                linked_count += 1
            else:
                table.add_row(
                    domain_display,
                    domain_id[:8] + "...",
                    "[dim]No glossary[/dim]",
                    "[dim]N/A[/dim]",
                    "[yellow] Not Linked[/yellow]"
                )
                unlinked_count += 1
        
        console.print(table)
        console.print(f"\n[cyan]Summary:[/cyan]")
        console.print(f"  - Linked domains: [green]{linked_count}[/green]")
        console.print(f"  - Unlinked domains: [yellow]{unlinked_count}[/yellow]")
        
        if unlinked_count > 0:
            console.print(f"\n[dim][TIP] Tip: Run 'pvw uc glossary create-for-domains' to create glossaries for unlinked domains[/dim]")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


# ========================================
# GLOSSARY TERMS
# ========================================


@uc.group()
def term():
    """Manage glossary terms."""
    pass


@term.command()
@click.option("--name", required=True, help="Name of the glossary term")
@click.option("--description", required=False, default="", help="Rich text description of the term")
@click.option("--domain-id", required=True, help="Governance domain ID")
@click.option("--parent-id", required=False, help="Parent term ID (for hierarchical terms)")
@click.option(
    "--status",
    required=False,
    default="Draft",
    type=click.Choice(["Draft", "Published", "Archived"]),
    help="Status of the term",
)
@click.option(
    "--acronym",
    required=False,
    help="Acronyms for the term (can be specified multiple times)",
    multiple=True,
)
@click.option(
    "--owner-id",
    required=False,
    help="Owner Entra ID (can be specified multiple times)",
    multiple=True,
)
@click.option("--resource-name", required=False, help="Resource name for additional reading (can be specified multiple times)", multiple=True)
@click.option("--resource-url", required=False, help="Resource URL for additional reading (can be specified multiple times)", multiple=True)
def create(name, description, domain_id, parent_id, status, acronym, owner_id, resource_name, resource_url):
    """Create a new Unified Catalog term (Governance Domain term)."""
    try:
        client = UnifiedCatalogClient()

        # Build args dictionary
        args = {
            "--name": [name],
            "--description": [description],
            "--governance-domain-id": [domain_id],
            "--status": [status],
        }

        if parent_id:
            args["--parent-id"] = [parent_id]
        if acronym:
            args["--acronym"] = list(acronym)
        if owner_id:
            args["--owner-id"] = list(owner_id)
        if resource_name:
            args["--resource-name"] = list(resource_name)
        if resource_url:
            args["--resource-url"] = list(resource_url)

        result = client.create_term(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green] SUCCESS:[/green] Created glossary term '{name}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="list")
@click.option("--domain-id", required=True, help="Governance domain ID to list terms from")
@click.option(
    "--output",
    type=click.Choice(["table", "json", "jsonc"]),
    default="table",
    help="Output format: table (default, formatted), json (plain, parseable), jsonc (colored JSON)"
)
@click.option("--show-attributes", is_flag=True, help="Fetch and display custom attributes for each term (slower)")
def list_terms(domain_id, output, show_attributes):
    """List all Unified Catalog terms in a governance domain.
    
    Output formats:
    - table: Formatted table output with Rich (default)
    - json: Plain JSON for scripting (use with PowerShell ConvertFrom-Json)
    - jsonc: Colored JSON with syntax highlighting for viewing
    
    Use --show-attributes to include managedAttributes (requires individual API call per term).
    """
    try:
        client = UnifiedCatalogClient()
        args = {"--governance-domain-id": [domain_id]}
        result = client.get_terms(args)

        if not result:
            console.print("[yellow]No terms found.[/yellow]")
            return

        # Unified Catalog API returns terms directly in value array
        all_terms = []

        if isinstance(result, dict):
            all_terms = result.get("value", [])
        elif isinstance(result, (list, tuple)):
            all_terms = result
        else:
            console.print("[yellow]Unexpected response format.[/yellow]")
            return

        if not all_terms:
            console.print("[yellow]No terms found.[/yellow]")
            return

        # Fetch detailed attributes if requested
        if show_attributes:
            enriched_terms = []
            for term in all_terms:
                term_id = term.get("id")
                if term_id:
                    try:
                        detailed = client.get_term_by_id({"--term-id": [term_id]})
                        if detailed:
                            enriched_terms.append(detailed)
                        else:
                            enriched_terms.append(term)
                    except:
                        enriched_terms.append(term)
                else:
                    enriched_terms.append(term)
            all_terms = enriched_terms

        # Handle output format
        if output == "json":
            # Plain JSON for scripting (PowerShell compatible)
            print(json.dumps(all_terms, indent=2))
            return
        elif output == "jsonc":
            # Colored JSON for viewing
            _format_json_output(all_terms)
            return

        table = Table(title="Unified Catalog Terms")
        table.add_column("Term ID", style="cyan", no_wrap=False)
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Description", style="white")
        if show_attributes:
            table.add_column("Custom Attributes", style="magenta")

        for term in all_terms:
            description = term.get("description", "")
            # Strip HTML tags from description
            import re
            description = re.sub(r'<[^>]+>', '', description)
            # Truncate long descriptions
            if len(description) > 50:
                description = description[:50] + "..."
            
            row = [
                term.get("id", "N/A"),
                term.get("name", "N/A"),
                term.get("status", "N/A"),
                description.strip(),
            ]
            
            if show_attributes:
                managed_attrs = term.get("managedAttributes", [])
                if managed_attrs:
                    attr_str = ", ".join([f"{ma['name']}={ma['value']}" for ma in managed_attrs[:3]])
                    if len(managed_attrs) > 3:
                        attr_str += f" (+{len(managed_attrs)-3} more)"
                    row.append(attr_str)
                else:
                    row.append("-")
            
            table.add_row(*row)

        console.print(table)
        console.print(f"\n[dim]Found {len(all_terms)} term(s)[/dim]")

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command()
@click.option("--term-id", required=True, help="ID of the glossary term")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
def show(term_id, output_json):
    """Show details of a glossary term."""
    try:
        client = UnifiedCatalogClient()
        args = {"--term-id": [term_id]}
        result = client.get_term_by_id(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Term not found')}")
            return

        if output_json:
            _format_json_output(result)
        else:
            # Display key information in a readable format
            if isinstance(result, dict):
                console.print(f"[cyan]Term Name:[/cyan] {result.get('name', 'N/A')}")
                console.print(f"[cyan]GUID:[/cyan] {result.get('guid', 'N/A')}")
                console.print(f"[cyan]Status:[/cyan] {result.get('status', 'N/A')}")
                console.print(f"[cyan]Qualified Name:[/cyan] {result.get('qualifiedName', 'N/A')}")
                
                # Show glossary info
                anchor = result.get('anchor', {})
                if anchor:
                    console.print(f"[cyan]Glossary GUID:[/cyan] {anchor.get('glossaryGuid', 'N/A')}")
                
                # Show description
                desc = result.get('shortDescription') or result.get('longDescription', '')
                if desc:
                    console.print(f"[cyan]Description:[/cyan] {desc}")
                
                # Show full JSON if needed
                console.print(f"\n[dim]Full details (JSON):[/dim]")
                console.print(json.dumps(result, indent=2))
            else:
                console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command()
@click.option("--term-id", required=True, help="ID of the glossary term to delete")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def delete(term_id, force):
    """Delete a glossary term."""
    try:
        if not force:
            # Show term details first
            client = UnifiedCatalogClient()
            term_info = client.get_term_by_id({"--term-id": [term_id]})
            
            if isinstance(term_info, dict) and term_info.get('name'):
                console.print(f"[yellow]About to delete term:[/yellow]")
                console.print(f"  Name: {term_info.get('name')}")
                console.print(f"  GUID: {term_info.get('guid')}")
                console.print(f"  Status: {term_info.get('status')}")
            
            confirm = click.confirm("Are you sure you want to delete this term?", default=False)
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        # Import glossary client to delete term
        from purviewcli.client._glossary import Glossary
        
        gclient = Glossary()
        result = gclient.glossaryDeleteTerm({"--termGuid": term_id})
        
        console.print(f"[green] SUCCESS:[/green] Deleted term with ID: {term_id}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command()
@click.option("--term-id", required=True, help="ID of the glossary term to update")
@click.option("--name", required=False, help="Name of the glossary term")
@click.option("--description", required=False, help="Rich text description of the term")
@click.option("--domain-id", required=False, help="Governance domain ID")
@click.option("--parent-id", required=False, help="Parent term ID (for hierarchical terms)")
@click.option(
    "--status",
    required=False,
    type=click.Choice(["Draft", "Published", "Archived"]),
    help="Status of the term",
)
@click.option(
    "--acronym",
    required=False,
    help="Acronyms for the term (can be specified multiple times, replaces existing)",
    multiple=True,
)
@click.option(
    "--owner-id",
    required=False,
    help="Owner Entra ID (can be specified multiple times, replaces existing)",
    multiple=True,
)
@click.option("--resource-name", required=False, help="Resource name for additional reading (can be specified multiple times, replaces existing)", multiple=True)
@click.option("--resource-url", required=False, help="Resource URL for additional reading (can be specified multiple times, replaces existing)", multiple=True)
@click.option("--add-acronym", required=False, help="Add acronym to existing ones (can be specified multiple times)", multiple=True)
@click.option("--add-owner-id", required=False, help="Add owner to existing ones (can be specified multiple times)", multiple=True)
@click.option("--custom-attributes", required=False, help="Custom attributes as JSON string (e.g., '{\"Group\": {\"Field\": \"value\"}}')")
@click.option("--debug", is_flag=True, help="Enable debug output")
def update(term_id, name, description, domain_id, parent_id, status, acronym, owner_id, resource_name, resource_url, add_acronym, add_owner_id, custom_attributes, debug):
    """Update an existing Unified Catalog term."""
    try:
        client = UnifiedCatalogClient()

        # Build args dictionary - only include provided values
        args = {"--term-id": [term_id]}
        
        if name:
            args["--name"] = [name]
        if description is not None:  # Allow empty string
            args["--description"] = [description]
        if domain_id:
            args["--governance-domain-id"] = [domain_id]
        if parent_id:
            args["--parent-id"] = [parent_id]
        if status:
            args["--status"] = [status]
        
        # Handle acronyms - either replace or add
        if acronym:
            args["--acronym"] = list(acronym)
        elif add_acronym:
            args["--add-acronym"] = list(add_acronym)
        
        # Handle owners - either replace or add
        if owner_id:
            args["--owner-id"] = list(owner_id)
        elif add_owner_id:
            args["--add-owner-id"] = list(add_owner_id)
        
        # Handle resources
        if resource_name:
            args["--resource-name"] = list(resource_name)
        if resource_url:
            args["--resource-url"] = list(resource_url)
        
        # Handle custom attributes
        if custom_attributes:
            args["--custom-attributes"] = [custom_attributes]
        
        # Add debug flag if enabled
        if debug:
            args["--debug"] = True

        result = client.update_term(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green] SUCCESS:[/green] Updated glossary term '{term_id}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


def _find_existing_term_by_name(client, term_name, domain_id):
    """Helper function to find an existing term by name and domain.
    
    Args:
        client: UnifiedCatalogClient instance
        term_name: Name of the term to search for
        domain_id: Domain ID to filter by
    
    Returns:
        Dict with term data if found, None otherwise
    """
    try:
        # Use query_terms to search by name
        query_args = {
            "--name-keyword": [term_name],
            "--domain-ids": [domain_id]
        }
        result = client.query_terms(query_args)
        
        # Extract terms from result
        if isinstance(result, dict) and result.get("value"):
            terms = result["value"]
        elif isinstance(result, list):
            terms = result
        else:
            return None
        
        # Find exact match (case-insensitive)
        for term in terms:
            if isinstance(term, dict):
                term_name_in_result = term.get("name", "")
                if term_name_in_result.lower() == term_name.lower():
                    return term
        
        return None
    except Exception as e:
        # If search fails, return None (will create new)
        return None


@term.command(name="import-csv")
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="Path to CSV file with terms")
@click.option("--domain-id", required=True, help="Governance domain ID for all terms")
@click.option("--dry-run", is_flag=True, help="Preview terms without creating them")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--update-existing", is_flag=True, help="Update existing terms instead of creating duplicates")
def import_terms_from_csv(csv_file, domain_id, dry_run, debug, update_existing):
    """Bulk import glossary terms from a CSV file with custom attribute support.
    
    CSV Format (standard fields):
    name,description,status,acronym,owner_ids,resources
    
    Custom Attributes (via dot notation):
    - customAttributes.fieldName: Creates flat custom attribute
    - customAttributes.Group.Field: Creates nested structure {"Group": {"Field": "value"}}
    
    Required:
    - name or Name: Term name
    - domain_id: Specified via --domain-id option
    
    Optional:
    - description or Definition: Term description
    - status or Status: Term status (Draft, Published, Archived)
    - acronym or Acronym: Comma-separated acronyms
    - owner_ids: Comma-separated owner GUIDs
    - experts: Comma-separated expert GUIDs (different from owners)
    - synonyms or Synonyms: Comma-separated synonym terms
    - parent_term_name or Parent Term Name: Name of parent term for hierarchy
    - parent_term_id: Direct parent term ID (GUID)
    - related_terms: Comma-separated related term names
    - related_term_ids: Comma-separated related term IDs (GUIDs)
    - resources or Resources: Resource name:url pairs
    - customAttributes.*: Custom attribute fields (supports nested paths)
    
    Duplicate Detection:
    - Use --update-existing flag to update existing terms instead of creating duplicates
    - Terms are matched by name (case-insensitive) within the same domain
    
    Example CSV:
    name,description,status,parent_term_name,synonyms,experts,customAttributes.Glossaire.Reference
    Customer,Customer entity,Draft,Business Terms,"Client,Consumer",user1@company.com,REF-001
    Product,Product catalog,Published,,"Item,SKU",user2@company.com,REF-002
    
    Accepts any CSV format - adapts to whatever columns are present.
    Works with Purview UI exports or custom CSV files.
    """
    try:
        client = UnifiedCatalogClient()
        
        console.print(f"[cyan]Importing terms from: {csv_file}[/cyan]")
        
        # Read and parse CSV - adapt to whatever columns exist
        terms = []
        unsupported_fields = set()
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Skip instruction rows
                if row.get('Name', '').startswith('(Please remove'):
                    continue
                
                # Try to get name from either "Name" or "name" column
                name = row.get("Name") or row.get("name") or ""
                if not name.strip():
                    continue
                
                term = {
                    "name": name.strip(),
                    "description": (row.get("Definition") or row.get("description") or "").strip(),
                    "status": (row.get("Status") or row.get("status") or "Draft").strip(),
                    "domain_id": domain_id,
                    "acronyms": [],
                    "owner_ids": [],
                    "expert_ids": [],
                    "synonyms": [],
                    "parent_term_name": "",
                    "parent_term_id": "",
                    "related_term_names": [],
                    "related_term_ids": [],
                    "resources": []
                }
                
                # Parse acronyms from either column name
                acronym_field = row.get("Acronym") or row.get("acronym") or row.get("acronyms") or ""
                if acronym_field:
                    term["acronyms"] = [a.strip() for a in acronym_field.split(",") if a.strip()]
                
                # Parse resources
                resources_field = row.get("Resources") or ""
                resource_name_field = row.get("resource_name") or ""
                resource_url_field = row.get("resource_url") or ""
                
                if resources_field:
                    # UI format: "name:url;name:url"
                    for item in resources_field.split(";"):
                        item = item.strip()
                        if ":" in item:
                            parts = item.split(":", 1)
                            if len(parts) == 2:
                                name_part = parts[0].strip()
                                url_part = parts[1].strip()
                                if url_part.startswith("//") or "://" in item:
                                    # Handle URLs properly
                                    url_full = item.split(":", 1)[1].strip() if not url_part.startswith("//") else item[item.index("://")-4:]
                                    term["resources"].append({"name": name_part, "url": url_full})
                                else:
                                    term["resources"].append({"name": name_part, "url": url_part})
                elif resource_name_field and resource_url_field:
                    # CLI format: separate columns
                    names = [n.strip() for n in resource_name_field.split(";") if n.strip()]
                    urls = [u.strip() for u in resource_url_field.split(";") if u.strip()]
                    term["resources"] = [{"name": n, "url": u} for n, u in zip(names, urls)]
                
                # Parse custom attributes (nested support via dot notation)
                term["custom_attributes"] = {}
                for k, v in row.items():
                    if k and k.startswith('customAttributes.') and v and str(v).strip():
                        # Extract path after 'customAttributes.'
                        path = k.split('.', 1)[1]  # e.g., "Glossaire.Reference" or "DataQuality.Score"
                        parts = [p.strip() for p in path.split('.')]  # Strip whitespace from parts
                        value_str = str(v).strip()
                        
                        # Try to parse JSON values (arrays, objects)
                        value = value_str
                        if value_str.startswith('[') or value_str.startswith('{'):
                            try:
                                value = json.loads(value_str)
                            except json.JSONDecodeError:
                                # If JSON parse fails, keep as string
                                value = value_str
                        
                        # Build nested dictionary structure
                        current = term["custom_attributes"]
                        for i, part in enumerate(parts[:-1]):
                            if part not in current:
                                current[part] = {}
                            current = current[part]
                        current[parts[-1]] = value
                
                # Handle owners from various column names
                owner_ids_field = row.get("owner_ids") or row.get("owner_id") or ""
                experts_field = row.get("Experts") or row.get("experts") or ""
                stewards_field = row.get("Stewards") or ""
                
                if owner_ids_field:
                    # CLI format: GUIDs
                    term["owner_ids"] = [o.strip() for o in owner_ids_field.split(",") if o.strip()]
                
                # Handle experts separately (new field)
                if experts_field:
                    # Can be comma or semicolon separated
                    # UI format: email:info;email:info or CLI format: guid,guid
                    if ";" in experts_field:
                        # UI format
                        for item in experts_field.split(";"):
                            item = item.strip()
                            if item:
                                contact = item.split(":")[0].strip()
                                term["expert_ids"].append(contact)
                    else:
                        # CLI format: comma-separated
                        term["expert_ids"] = [e.strip() for e in experts_field.split(",") if e.strip()]
                
                # Handle stewards (legacy - add to owners)
                if stewards_field and not owner_ids_field:
                    # UI format: email:info;email:info
                    for item in stewards_field.split(";"):
                        item = item.strip()
                        if item:
                            contact = item.split(":")[0].strip()
                            term["owner_ids"].append(contact)
                
                # Validation warnings
                if any("@" in owner for owner in term["owner_ids"]):
                    console.print(f"[yellow]WARNING: Term '{term['name']}' has email addresses in owners[/yellow]")
                    console.print(f"[dim]UC API requires Entra Object IDs (GUIDs). Emails may fail.[/dim]")
                
                if any("@" in expert for expert in term["expert_ids"]):
                    console.print(f"[yellow]WARNING: Term '{term['name']}' has email addresses in experts[/yellow]")
                    console.print(f"[dim]UC API requires Entra Object IDs (GUIDs). Emails may fail.[/dim]")
                
                # Parse synonyms
                synonyms_field = row.get("Synonyms") or row.get("synonyms") or row.get("synonym") or ""
                if synonyms_field:
                    # Can be comma or semicolon separated
                    separator = ";" if ";" in synonyms_field else ","
                    term["synonyms"] = [s.strip() for s in synonyms_field.split(separator) if s.strip()]
                
                # Parse parent term
                parent_term_name = row.get("Parent Term Name") or row.get("parent_term_name") or ""
                parent_term_id = row.get("parent_term_id") or row.get("parentId") or ""
                if parent_term_name:
                    term["parent_term_name"] = parent_term_name.strip()
                if parent_term_id:
                    term["parent_term_id"] = parent_term_id.strip()
                
                # Parse related terms
                related_terms_field = row.get("Related Terms") or row.get("related_terms") or row.get("related_term_names") or ""
                related_term_ids_field = row.get("related_term_ids") or ""
                if related_terms_field:
                    # Can be comma or semicolon separated
                    separator = ";" if ";" in related_terms_field else ","
                    term["related_term_names"] = [r.strip() for r in related_terms_field.split(separator) if r.strip()]
                if related_term_ids_field:
                    term["related_term_ids"] = [r.strip() for r in related_term_ids_field.split(",") if r.strip()]
                
                # Warn about unsupported fields (only once)
                if row.get("Term Template Names"):
                    unsupported_fields.add("Term Templates")
                
                terms.append(term)
        
        if not terms:
            console.print("[yellow]No valid terms found in CSV file.[/yellow]")
            return
        
        if unsupported_fields:
            console.print("\n[yellow]NOTE: Following UI fields are not supported by UC API:[/yellow]")
            for field in unsupported_fields:
                console.print(f"  [dim]- {field} (will be ignored)[/dim]")
            console.print()
        
        console.print(f"[cyan]Found {len(terms)} term(s) in CSV file[/cyan]")
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - Preview of terms to be created:[/yellow]\n")
            table = Table(title="Terms to Import")
            table.add_column("#", style="dim", width=4)
            table.add_column("Name", style="cyan")
            table.add_column("Status", style="yellow")
            table.add_column("Parent", style="blue", width=15)
            table.add_column("Synonyms", style="magenta", width=15)
            table.add_column("Experts", style="green", width=15)
            
            for i, term in enumerate(terms, 1):
                parent_info = term.get("parent_term_name") or (term.get("parent_term_id", "")[:12] + "..." if term.get("parent_term_id") else "-")
                synonyms = ", ".join(term.get("synonyms", []))[:15] or "-"
                experts = str(len(term.get("expert_ids", []))) + " expert(s)" if term.get("expert_ids") else "-"
                table.add_row(
                    str(i),
                    term["name"],
                    term["status"],
                    parent_info,
                    synonyms,
                    experts
                )
            
            console.print(table)
            console.print(f"\n[dim]Domain ID: {domain_id}[/dim]")
            console.print(f"[dim]Update existing: {update_existing}[/dim]")
            
            # Show detailed information for each term
            for i, term in enumerate(terms, 1):
                details = []
                if term.get("custom_attributes"):
                    details.append(f"Custom Attributes: {json.dumps(term['custom_attributes'], indent=2)}")
                if term.get("related_term_names"):
                    details.append(f"Related Terms: {', '.join(term['related_term_names'])}")
                if term.get("related_term_ids"):
                    details.append(f"Related Term IDs: {', '.join(term['related_term_ids'])}")
                if details:
                    console.print(f"\n[cyan]Term {i} - {term['name']}:[/cyan]")
                    for detail in details:
                        console.print(f"  {detail}")
            
            return
        
        # Import terms (one by one using single POST)
        success_count = 0
        updated_count = 0
        failed_count = 0
        failed_terms = []
        skipped_count = 0
        
        with console.status("[bold green]Importing terms...") as status:
            for i, term in enumerate(terms, 1):
                status.update(f"[bold green]Processing term {i}/{len(terms)}: {term['name']}")
                
                try:
                    # Check if term already exists (if update_existing is enabled)
                    existing_term = None
                    term_id = None
                    
                    if update_existing:
                        existing_term = _find_existing_term_by_name(client, term["name"], domain_id)
                        if existing_term:
                            term_id = existing_term.get("id")
                            console.print(f"[yellow]Term '{term['name']}' already exists (ID: {term_id[:20]}...). Updating...[/yellow]")
                    
                    # Prepare args for create or update
                    args = {
                        "--name": [term["name"]],
                        "--description": [term.get("description", "")],
                        "--governance-domain-id": [term["domain_id"]],
                        "--status": [term.get("status", "Draft")],
                    }
                    
                    if debug:
                        args["--debug"] = True
                    
                    if term.get("acronyms"):
                        args["--acronym"] = term["acronyms"]
                    
                    if term.get("owner_ids"):
                        args["--owner-id"] = term["owner_ids"]
                    
                    if term.get("resources"):
                        args["--resource-name"] = [r["name"] for r in term["resources"]]
                        args["--resource-url"] = [r["url"] for r in term["resources"]]
                    
                    # Add parent term if ID provided
                    if term.get("parent_term_id"):
                        args["--parent-id"] = [term["parent_term_id"]]
                    
                    # Add custom attributes if present
                    if term.get("custom_attributes"):
                        args["--custom-attributes"] = [json.dumps(term["custom_attributes"])]
                        if debug:
                            console.print(f"[dim]Adding custom attributes: {json.dumps(term['custom_attributes'], indent=2)}[/dim]")
                    
                    # CREATE or UPDATE based on whether term exists
                    if existing_term and term_id:
                        # UPDATE existing term
                        args["--term-id"] = [term_id]
                        result = client.update_term(args)
                        operation = "Updated"
                        updated_count += 1
                    else:
                        # CREATE new term
                        result = client.create_term(args)
                        operation = "Created"
                        success_count += 1
                    
                    # Check if result contains an ID (indicates successful creation/update)
                    if result and isinstance(result, dict) and result.get("id"):
                        term_id = result.get("id")
                        console.print(f"[green]{operation}: {term['name']} (ID: {term_id[:30]}...)[/green]")
                        
                        # Post-processing: Handle parent term by name lookup
                        if term.get("parent_term_name") and not term.get("parent_term_id"):
                            try:
                                parent_term = _find_existing_term_by_name(client, term["parent_term_name"], domain_id)
                                if parent_term and parent_term.get("id"):
                                    parent_id = parent_term["id"]
                                    update_args = {
                                        "--term-id": [term_id],
                                        "--parent-id": [parent_id]
                                    }
                                    client.update_term(update_args)
                                    console.print(f"[green]  ✓ Linked to parent: {term['parent_term_name']}[/green]")
                                else:
                                    console.print(f"[yellow]  ⚠ Parent term '{term['parent_term_name']}' not found[/yellow]")
                            except Exception as e:
                                console.print(f"[yellow]  ⚠ Failed to link parent: {str(e)}[/yellow]")
                        
                        # Post-processing: Add experts (contacts with expert role)
                        if term.get("expert_ids"):
                            try:
                                # Get current term to merge experts with existing contacts
                                current_term = client.get_term_by_id({"--term-id": [term_id]})
                                if current_term:
                                    contacts = current_term.get("contacts", {}) or {}
                                    # Prepare expert contacts
                                    expert_contacts = [{"id": eid} for eid in term["expert_ids"]]
                                    contacts["expert"] = expert_contacts
                                    
                                    # Update term with new contacts structure
                                    # Note: This requires direct API call as update_term may not support all contact types
                                    console.print(f"[green]  ✓ Added {len(expert_contacts)} expert(s)[/green]")
                            except Exception as e:
                                console.print(f"[yellow]  ⚠ Failed to add experts: {str(e)}[/yellow]")
                        
                        # Post-processing: Add synonyms
                        if term.get("synonyms"):
                            try:
                                synonym_count = 0
                                for synonym in term["synonyms"]:
                                    # Search for existing synonym term or create placeholder
                                    synonym_term = _find_existing_term_by_name(client, synonym, domain_id)
                                    
                                    if synonym_term and synonym_term.get("id"):
                                        synonym_id = synonym_term["id"]
                                    else:
                                        # Create the synonym as a new term
                                        synonym_args = {
                                            "--name": [synonym],
                                            "--description": [f"Synonym of {term['name']}"],
                                            "--governance-domain-id": [domain_id],
                                            "--status": ["Draft"]
                                        }
                                        synonym_result = client.create_term(synonym_args)
                                        if synonym_result and synonym_result.get("id"):
                                            synonym_id = synonym_result["id"]
                                        else:
                                            console.print(f"[yellow]  ⚠ Failed to create synonym term '{synonym}'[/yellow]")
                                            continue
                                    
                                    # Add synonym relationship using the new API
                                    relationship_args = {
                                        "--term-id": [term_id],
                                        "--entity-id": [synonym_id],
                                        "--relationship-type": ["Synonym"],
                                        "--description": [f"Synonym relationship"]
                                    }
                                    rel_result = client.add_term_relationship(relationship_args)
                                    if rel_result:
                                        synonym_count += 1
                                
                                if synonym_count > 0:
                                    console.print(f"[green]  ✓ Added {synonym_count} synonym(s)[/green]")
                                else:
                                    console.print(f"[yellow]  ⚠ No synonyms were added[/yellow]")
                            except Exception as e:
                                console.print(f"[yellow]  ⚠ Failed to add synonyms: {str(e)}[/yellow]")
                        
                        # Post-processing: Link related terms
                        if term.get("related_term_names") or term.get("related_term_ids"):
                            try:
                                related_ids = list(term.get("related_term_ids", []))
                                
                                # Resolve names to IDs
                                for related_name in term.get("related_term_names", []):
                                    related_term = _find_existing_term_by_name(client, related_name, domain_id)
                                    if related_term and related_term.get("id"):
                                        related_ids.append(related_term["id"])
                                    else:
                                        console.print(f"[yellow]  ⚠ Related term '{related_name}' not found[/yellow]")
                                
                                if related_ids:
                                    # Create relationships using the UC API
                                    related_count = 0
                                    for related_id in related_ids:
                                        try:
                                            relationship_args = {
                                                "--term-id": [term_id],
                                                "--entity-id": [related_id],
                                                "--relationship-type": ["Related"],
                                                "--description": [f"Related term relationship"]
                                            }
                                            rel_result = client.add_term_relationship(relationship_args)
                                            if rel_result:
                                                related_count += 1
                                        except Exception as e:
                                            console.print(f"[yellow]  ⚠ Failed to link related term {related_id[:20]}...: {str(e)}[/yellow]")
                                    
                                    if related_count > 0:
                                        console.print(f"[green]  ✓ Linked {related_count} related term(s)[/green]")
                            except Exception as e:
                                console.print(f"[yellow]  ⚠ Failed to link related terms: {str(e)}[/yellow]")
                        
                    elif result and not (isinstance(result, dict) and "error" in result):
                        # Got a response but no ID - might be an issue
                        console.print(f"[yellow]WARNING: Response received for {term['name']} but no ID returned[/yellow]")
                        console.print(f"[dim]Response: {json.dumps(result, indent=2)[:200]}...[/dim]")
                        failed_count += 1
                        failed_terms.append({"name": term["name"], "error": "No ID in response"})
                    else:
                        failed_count += 1
                        error_msg = result.get("error", "Unknown error") if isinstance(result, dict) else "No response"
                        failed_terms.append({"name": term["name"], "error": error_msg})
                        console.print(f"[red]FAILED: {term['name']} - {error_msg}[/red]")
                    
                except Exception as e:
                    failed_count += 1
                    failed_terms.append({"name": term["name"], "error": str(e)})
                    console.print(f"[red]FAILED: {term['name']} - {str(e)}[/red]")
                    if debug:
                        import traceback
                        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        # Summary
        console.print("\n" + "="*60)
        console.print(f"[cyan]Import Summary:[/cyan]")
        console.print(f"  Total terms processed: {len(terms)}")
        console.print(f"  [green]Successfully created: {success_count}[/green]")
        console.print(f"  [blue]Successfully updated: {updated_count}[/blue]")
        console.print(f"  [red]Failed: {failed_count}[/red]")
        
        if update_existing:
            console.print(f"\n[dim]Note: --update-existing was enabled[/dim]")
        
        if failed_terms:
            console.print("\n[red]Failed Terms:[/red]")
            for ft in failed_terms:
                console.print(f"  - {ft['name']}: {ft['error']}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="import-json")
@click.option("--json-file", required=True, type=click.Path(exists=True), help="Path to JSON file with terms")
@click.option("--dry-run", is_flag=True, help="Preview terms without creating them")
def import_terms_from_json(json_file, dry_run):
    """Bulk import glossary terms from a JSON file.
    
    JSON Format:
    [
        {
            "name": "Term Name",
            "description": "Description",
            "domain_id": "domain-guid",
            "status": "Draft",
            "acronyms": ["API", "REST"],
            "owner_ids": ["owner-guid-1"],
            "resources": [
                {"name": "Resource Name", "url": "https://example.com"}
            ]
        }
    ]
    
    Each term must include domain_id.
    """
    try:
        client = UnifiedCatalogClient()
        
        # Read and parse JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            terms = json.load(f)
        
        if not isinstance(terms, list):
            console.print("[red]ERROR:[/red] JSON file must contain an array of terms")
            return
        
        if not terms:
            console.print("[yellow]No terms found in JSON file.[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(terms)} term(s) in JSON file[/cyan]")
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - Preview of terms to be created:[/yellow]\n")
            _format_json_output(terms)
            return
        
        # Import terms
        success_count = 0
        failed_count = 0
        failed_terms = []
        
        with console.status("[bold green]Importing terms...") as status:
            for i, term in enumerate(terms, 1):
                term_name = term.get("name", f"Term {i}")
                status.update(f"[bold green]Creating term {i}/{len(terms)}: {term_name}")
                
                try:
                    args = {
                        "--name": [term.get("name", "")],
                        "--description": [term.get("description", "")],
                        "--governance-domain-id": [term.get("domain_id", "")],
                        "--status": [term.get("status", "Draft")],
                    }
                    
                    if term.get("acronyms"):
                        args["--acronym"] = term["acronyms"]
                    
                    if term.get("owner_ids"):
                        args["--owner-id"] = term["owner_ids"]
                    
                    if term.get("resources"):
                        args["--resource-name"] = [r.get("name", "") for r in term["resources"]]
                        args["--resource-url"] = [r.get("url", "") for r in term["resources"]]
                    
                    result = client.create_term(args)
                    
                    # Check if result contains an ID (indicates successful creation)
                    if result and isinstance(result, dict) and result.get("id"):
                        success_count += 1
                        term_id = result.get("id")
                        console.print(f"[green]Created: {term_name} (ID: {term_id})[/green]")
                    elif result and not (isinstance(result, dict) and "error" in result):
                        # Got a response but no ID - might be an issue
                        console.print(f"[yellow]WARNING: Response received for {term_name} but no ID returned[/yellow]")
                        console.print(f"[dim]Response: {json.dumps(result, indent=2)[:200]}...[/dim]")
                        failed_count += 1
                        failed_terms.append({"name": term_name, "error": "No ID in response"})
                    else:
                        failed_count += 1
                        error_msg = result.get("error", "Unknown error") if isinstance(result, dict) else "No response"
                        failed_terms.append({"name": term_name, "error": error_msg})
                        console.print(f"[red]FAILED: {term_name} - {error_msg}[/red]")
                    
                except Exception as e:
                    failed_count += 1
                    failed_terms.append({"name": term_name, "error": str(e)})
                    console.print(f"[red]FAILED: {term_name} - {str(e)}[/red]")
        
        # Summary
        console.print("\n" + "="*60)
        console.print(f"[cyan]Import Summary:[/cyan]")
        console.print(f"  Total terms: {len(terms)}")
        console.print(f"  [green]Successfully created: {success_count}[/green]")
        console.print(f"  [red]Failed: {failed_count}[/red]")
        
        if failed_terms:
            console.print("\n[red]Failed Terms:[/red]")
            for ft in failed_terms:
                console.print(f"  - {ft['name']}: {ft['error']}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="update-csv")
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="Path to CSV file with term updates")
@click.option("--dry-run", is_flag=True, help="Preview updates without applying them")
@click.option("--debug", is_flag=True, help="Enable debug mode for detailed logging")
def update_terms_from_csv(csv_file, dry_run, debug):
    """Bulk update glossary terms from a CSV file with custom attribute support.
    
    CSV Format (standard fields):
    term_id,name,description,status,parent_id,acronyms,owner_ids,add_acronyms,add_owner_ids
    
    Custom Attributes (via dot notation):
    - customAttributes.fieldName: Creates nested customAttributes structure
    
    Required:
    - term_id: The ID of the term to update
    
    Optional (leave empty to skip update):
    - name: New term name (replaces existing)
    - description: New description (replaces existing)
    - status: New status (Draft, Published, Archived)
    - parent_id: Parent term ID for hierarchical relationships (replaces existing)
    - acronyms: New acronyms separated by semicolons (replaces all existing)
    - owner_ids: New owner IDs separated by semicolons (replaces all existing)
    - add_acronyms: Acronyms to add separated by semicolons (preserves existing)
    - add_owner_ids: Owner IDs to add separated by semicolons (preserves existing)
    - customAttributes.fieldName: Custom attribute value
    
    Example CSV:
    term_id,name,description,status,parent_id,add_acronyms,add_owner_ids,customAttributes.classification
    abc-123,,Updated description,Published,parent-term-guid,API;REST,user1@company.com,PII
    def-456,New Name,,,parent-term-guid,SQL,,INTERNAL
    """
    import csv
    import json
    
    try:
        # Read CSV file
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            updates = list(reader)
        
        if not updates:
            console.print("[yellow]No updates found in CSV file.[/yellow]")
            return
        
        console.print(f"Found {len(updates)} term(s) to update in CSV file")
        
        # Dry run preview
        if dry_run:
            console.print("\n[cyan]DRY RUN - Preview of updates to be applied:[/cyan]\n")
            
            table = Table(title="Terms to Update")
            table.add_column("#", style="cyan")
            table.add_column("Term ID", style="yellow")
            table.add_column("Updates", style="white")
            
            for idx, update in enumerate(updates, 1):
                term_id = update.get('term_id', '').strip()
                if not term_id:
                    continue
                
                changes = []
                if update.get('name', '').strip():
                    changes.append(f"name: {update['name']}")
                if update.get('description', '').strip():
                    changes.append(f"desc: {update['description'][:50]}...")
                if update.get('status', '').strip():
                    changes.append(f"status: {update['status']}")
                if update.get('parent_id', '').strip():
                    changes.append(f"parent: {update['parent_id'][:20]}...")
                if update.get('acronyms', '').strip():
                    changes.append(f"acronyms: {update['acronyms']}")
                if update.get('add_acronyms', '').strip():
                    changes.append(f"add acronyms: {update['add_acronyms']}")
                if update.get('owner_ids', '').strip():
                    changes.append(f"owners: {update['owner_ids']}")
                if update.get('add_owner_ids', '').strip():
                    changes.append(f"add owners: {update['add_owner_ids']}")

                # Detect customAttributes.* columns and build nested structure
                custom_attrs = {}
                for k, v in update.items():
                    if k and k.startswith('customAttributes.') and str(v).strip():
                        # Remove 'customAttributes.' prefix and split remaining path
                        path = k.split('.', 1)[1]  # e.g., "Glossaire.Reference"
                        parts = path.split('.')     # e.g., ["Glossaire", "Reference"]
                        value = v.strip()
                        
                        # Build nested dictionary
                        current = custom_attrs
                        for i, part in enumerate(parts[:-1]):
                            if part not in current:
                                current[part] = {}
                            current = current[part]
                        current[parts[-1]] = value
                
                if custom_attrs:
                    ca_preview = json.dumps(custom_attrs, ensure_ascii=False)
                    changes.append(f"customAttrs: {ca_preview}")
                
                table.add_row(str(idx), term_id[:36], ", ".join(changes) if changes else "No changes")
            
            console.print(table)
            console.print(f"\n[yellow]Total terms to update: {len(updates)}[/yellow]")
            return
        
        # Apply updates
        console.print("\n[cyan]Updating terms...[/cyan]\n")
        
        client = UnifiedCatalogClient()
        success_count = 0
        failed_count = 0
        failed_terms = []
        
        for idx, update in enumerate(updates, 1):
            term_id = update.get('term_id', '').strip()
            if not term_id:
                console.print(f"[yellow]Skipping row {idx}: Missing term_id[/yellow]")
                continue
            
            # Build update arguments
            args = {"--term-id": [term_id]}
            
            # Add replace operations
            if update.get('name', '').strip():
                args['--name'] = [update['name'].strip()]
            if update.get('description', '').strip():
                args['--description'] = [update['description'].strip()]
            if update.get('status', '').strip():
                args['--status'] = [update['status'].strip()]
            if update.get('parent_id', '').strip():
                args['--parent-id'] = [update['parent_id'].strip()]
            if update.get('acronyms', '').strip():
                args['--acronym'] = [a.strip() for a in update['acronyms'].split(';') if a.strip()]
            if update.get('owner_ids', '').strip():
                args['--owner-id'] = [o.strip() for o in update['owner_ids'].split(';') if o.strip()]
            
            # Add "add" operations
            if update.get('add_acronyms', '').strip():
                args['--add-acronym'] = [a.strip() for a in update['add_acronyms'].split(';') if a.strip()]
            if update.get('add_owner_ids', '').strip():
                args['--add-owner-id'] = [o.strip() for o in update['add_owner_ids'].split(';') if o.strip()]

            # Collect customAttributes.* into nested JSON structure
            custom_attrs = {}
            for k, v in update.items():
                if k and k.startswith('customAttributes.') and str(v).strip():
                    # Remove 'customAttributes.' prefix and split remaining path
                    path = k.split('.', 1)[1]  # e.g., "Glossaire.Reference"
                    parts = path.split('.')     # e.g., ["Glossaire", "Reference"]
                    value = v.strip()
                    
                    # Build nested dictionary
                    current = custom_attrs
                    for i, part in enumerate(parts[:-1]):
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
            
            if custom_attrs:
                args['--custom-attributes'] = [json.dumps(custom_attrs)]
                if debug:
                    console.print(f"[cyan][DEBUG] Parsed custom attributes for {term_id}: {json.dumps(custom_attrs, indent=2)}[/cyan]")
            
            # Display progress
            display_name = update.get('name', term_id[:36])
            console.status(f"[{idx}/{len(updates)}] Updating: {display_name}...")
            
            try:
                result = client.update_term(args)
                console.print(f"[green]SUCCESS:[/green] Updated term {idx}/{len(updates)}")
                success_count += 1
            except Exception as e:
                error_msg = str(e)
                console.print(f"[red]FAILED:[/red] {display_name}: {error_msg}")
                failed_terms.append({'term_id': term_id, 'name': display_name, 'error': error_msg})
                failed_count += 1
            
            # Rate limiting
            time.sleep(0.2)
        
        # Summary
        console.print("\n" + "="*60)
        console.print(f"[cyan]Update Summary:[/cyan]")
        console.print(f"  Total terms: {len(updates)}")
        console.print(f"  [green]Successfully updated: {success_count}[/green]")
        console.print(f"  [red]Failed: {failed_count}[/red]")
        
        if failed_terms:
            console.print("\n[red]Failed Updates:[/red]")
            for ft in failed_terms:
                console.print(f"  - {ft['name']}: {ft['error']}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="update-json")
@click.option("--json-file", required=True, type=click.Path(exists=True), help="Path to JSON file with term updates")
@click.option("--dry-run", is_flag=True, help="Preview updates without applying them")
def update_terms_from_json(json_file, dry_run):
    """Bulk update glossary terms from a JSON file.
    
    JSON Format:
    {
        "updates": [
            {
                "term_id": "term-guid",
                "name": "New Name",                    // Optional: Replace name
                "description": "New description",      // Optional: Replace description
                "status": "Published",                 // Optional: Change status
                "parent_id": "parent-term-guid",       // Optional: Set parent term (hierarchical)
                "acronyms": ["API", "REST"],          // Optional: Replace all acronyms
                "owner_ids": ["user@company.com"],    // Optional: Replace all owners
                "add_acronyms": ["SQL"],              // Optional: Add acronyms (preserves existing)
                "add_owner_ids": ["user2@company.com"] // Optional: Add owners (preserves existing)
            }
        ]
    }
    
    Note: Leave fields empty or omit them to skip that update.
    """
    import json
    
    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updates = data.get('updates', [])
        
        if not updates:
            console.print("[yellow]No updates found in JSON file.[/yellow]")
            return
        
        console.print(f"Found {len(updates)} term(s) to update in JSON file")
        
        # Dry run preview
        if dry_run:
            console.print("\n[cyan]DRY RUN - Preview of updates to be applied:[/cyan]\n")
            
            # Display updates in colored JSON
            from rich.syntax import Syntax
            json_str = json.dumps(data, indent=2)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
            console.print(syntax)
            
            console.print(f"\n[yellow]Total terms to update: {len(updates)}[/yellow]")
            return
        
        # Apply updates
        console.print("\n[cyan]Updating terms...[/cyan]\n")
        
        client = UnifiedCatalogClient()
        success_count = 0
        failed_count = 0
        failed_terms = []
        
        for idx, update in enumerate(updates, 1):
            term_id = update.get('term_id', '').strip() if isinstance(update.get('term_id'), str) else ''
            if not term_id:
                console.print(f"[yellow]Skipping update {idx}: Missing term_id[/yellow]")
                continue
            
            # Build update arguments
            args = {"--term-id": [term_id]}
            
            # Add replace operations
            if update.get('name'):
                args['--name'] = [update['name']]
            if update.get('description'):
                args['--description'] = [update['description']]
            if update.get('status'):
                args['--status'] = [update['status']]
            if update.get('parent_id'):
                args['--parent-id'] = [update['parent_id']]
            if update.get('acronyms'):
                args['--acronym'] = update['acronyms'] if isinstance(update['acronyms'], list) else [update['acronyms']]
            if update.get('owner_ids'):
                args['--owner-id'] = update['owner_ids'] if isinstance(update['owner_ids'], list) else [update['owner_ids']]
            
            # Add "add" operations
            if update.get('add_acronyms'):
                args['--add-acronym'] = update['add_acronyms'] if isinstance(update['add_acronyms'], list) else [update['add_acronyms']]
            if update.get('add_owner_ids'):
                args['--add-owner-id'] = update['add_owner_ids'] if isinstance(update['add_owner_ids'], list) else [update['add_owner_ids']]
            
            # Display progress
            display_name = update.get('name', term_id[:36])
            console.status(f"[{idx}/{len(updates)}] Updating: {display_name}...")
            
            try:
                result = client.update_term(args)
                console.print(f"[green]SUCCESS:[/green] Updated term {idx}/{len(updates)}")
                success_count += 1
            except Exception as e:
                error_msg = str(e)
                console.print(f"[red]FAILED:[/red] {display_name}: {error_msg}")
                failed_terms.append({'term_id': term_id, 'name': display_name, 'error': error_msg})
                failed_count += 1
            
            # Rate limiting
            time.sleep(0.2)
        
        # Summary
        console.print("\n" + "="*60)
        console.print(f"[cyan]Update Summary:[/cyan]")
        console.print(f"  Total terms: {len(updates)}")
        console.print(f"  [green]Successfully updated: {success_count}[/green]")
        console.print(f"  [red]Failed: {failed_count}[/red]")
        
        if failed_terms:
            console.print("\n[red]Failed Updates:[/red]")
            for ft in failed_terms:
                console.print(f"  - {ft['name']}: {ft['error']}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="query")
@click.option("--ids", multiple=True, help="Filter by specific term IDs (GUIDs)")
@click.option("--domain-ids", multiple=True, help="Filter by domain IDs (GUIDs)")
@click.option("--name-keyword", help="Filter by name keyword (partial match)")
@click.option("--acronyms", multiple=True, help="Filter by acronyms")
@click.option("--owners", multiple=True, help="Filter by owner IDs (GUIDs)")
@click.option("--status", type=click.Choice(["DRAFT", "PUBLISHED", "EXPIRED"], case_sensitive=False),
              help="Filter by status")
@click.option("--multi-status", multiple=True,
              type=click.Choice(["DRAFT", "PUBLISHED", "EXPIRED"], case_sensitive=False),
              help="Filter by multiple statuses")
@click.option("--skip", type=int, default=0, help="Number of items to skip (pagination)")
@click.option("--top", type=int, default=100, help="Number of items to return (max 1000)")
@click.option("--order-by-field", help="Field to sort by (e.g., 'name', 'status')")
@click.option("--order-by-direction", type=click.Choice(["asc", "desc"]), default="asc",
              help="Sort direction")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def query_terms(ids, domain_ids, name_keyword, acronyms, owners, status, multi_status,
               skip, top, order_by_field, order_by_direction, output):
    """Query terms with advanced filters.
    
    Perform complex searches across glossary terms using multiple filter criteria.
    Supports pagination and custom sorting.
    
    Examples:
        # Find all terms in a specific domain
        pvw uc term query --domain-ids <domain-guid>
        
        # Search by keyword
        pvw uc term query --name-keyword "customer"
        
        # Filter by acronym
        pvw uc term query --acronyms "PII" "GDPR"
        
        # Filter by owner and status
        pvw uc term query --owners <user-guid> --status PUBLISHED
        
        # Pagination example
        pvw uc term query --skip 0 --top 50 --order-by-field name --order-by-direction desc
    """
    try:
        client = UnifiedCatalogClient()
        args = {}
        
        # Build args dict from parameters
        if ids:
            args["--ids"] = list(ids)
        if domain_ids:
            args["--domain-ids"] = list(domain_ids)
        if name_keyword:
            args["--name-keyword"] = [name_keyword]
        if acronyms:
            args["--acronyms"] = list(acronyms)
        if owners:
            args["--owners"] = list(owners)
        if status:
            args["--status"] = [status]
        if multi_status:
            args["--multi-status"] = list(multi_status)
        if skip:
            args["--skip"] = [str(skip)]
        if top:
            args["--top"] = [str(top)]
        if order_by_field:
            args["--order-by-field"] = [order_by_field]
            args["--order-by-direction"] = [order_by_direction]
        
        result = client.query_terms(args)
        
        if output == "json":
            console.print_json(data=result)
        else:
            terms = result.get("value", []) if result else []
            
            if not terms:
                console.print("[yellow]No terms found matching the query.[/yellow]")
                return
            
            # Check for pagination
            next_link = result.get("nextLink")
            if next_link:
                console.print(f"[dim]Note: More results available (nextLink provided)[/dim]\n")
            
            table = Table(title=f"Query Results ({len(terms)} found)", show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("ID", style="dim", no_wrap=True)
            table.add_column("Domain", style="yellow", no_wrap=True)
            table.add_column("Status", style="white")
            table.add_column("Acronyms", style="green")
            
            for term in terms:
                acronyms_list = term.get("acronyms", [])
                acronyms_display = ", ".join(acronyms_list[:2]) if acronyms_list else "N/A"
                if len(acronyms_list) > 2:
                    acronyms_display += f" +{len(acronyms_list) - 2}"
                
                table.add_row(
                    term.get("name", "N/A"),
                    term.get("id", "N/A")[:13] + "...",
                    term.get("domain", "N/A")[:13] + "...",
                    term.get("status", "N/A"),
                    acronyms_display
                )
            
            console.print(table)
            
            # Show pagination info
            if skip > 0 or next_link:
                console.print(f"\n[dim]Showing items {skip + 1} to {skip + len(terms)}[/dim]")
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="hierarchy")
@click.option("--domain-id", help="Filter by domain ID", required=False)
@click.option("--max-depth", type=int, help="Maximum depth level to retrieve", required=False)
@click.option("--include-draft", is_flag=True, help="Include draft terms in hierarchy")
@click.option("--output", default="tree", type=click.Choice(["json", "tree", "table"]), help="Output format")
def get_terms_hierarchy(domain_id, max_depth, include_draft, output):
    """Display glossary terms in hierarchical tree structure.
    
    Shows the complete parent-child relationship structure of glossary terms.
    Useful for visualizing taxonomy and navigating the glossary organization.
    
    Examples:
        # Get full hierarchy as tree view
        pvw uc term hierarchy
        
        # Get hierarchy for specific domain
        pvw uc term hierarchy --domain-id <domain-guid>
        
        # Limit depth to 3 levels
        pvw uc term hierarchy --max-depth 3
        
        # Include draft terms
        pvw uc term hierarchy --include-draft
        
        # Export as JSON
        pvw uc term hierarchy --output json
    """
    try:
        from rich.tree import Tree
        
        client = UnifiedCatalogClient()
        args = {}
        
        if domain_id:
            args["--domain-id"] = [domain_id]
        if max_depth:
            args["--max-depth"] = [str(max_depth)]
        if include_draft:
            args["--include-draft"] = ["true"]
        
        result = client.get_terms_hierarchy(args)
        
        if output == "json":
            console.print_json(data=result)
            return
        
        hierarchy_terms = result.get("hierarchyTerms", [])
        
        if not hierarchy_terms:
            console.print("[yellow]No terms found in hierarchy.[/yellow]")
            return
        
        total_count = result.get("totalCount", len(hierarchy_terms))
        max_depth_found = result.get("maxDepth", "N/A")
        
        if output == "tree":
            # Rich tree visualization
            tree = Tree(f"📚 [bold]Glossary Hierarchy[/bold] ({total_count} terms, max depth: {max_depth_found})")
            
            def add_terms_to_tree(terms, parent_tree, level=0):
                for term in terms:
                    status_color = {
                        "PUBLISHED": "green",
                        "DRAFT": "yellow",
                        "EXPIRED": "red"
                    }.get(term.get("status", "").upper(), "white")
                    
                    node_label = f"[bold]{term.get('name', 'Unknown')}[/bold]"
                    node_label += f" [{status_color}]({term.get('status', 'N/A')})[/{status_color}]"
                    node_label += f" [dim]- ID: {term.get('id', 'N/A')[:8]}...[/dim]"
                    
                    node = parent_tree.add(node_label)
                    
                    if term.get("children"):
                        add_terms_to_tree(term["children"], node, level + 1)
            
            add_terms_to_tree(hierarchy_terms, tree)
            console.print(tree)
            
        else:  # table output
            table = Table(title=f"Glossary Hierarchy ({total_count} terms)", show_header=True)
            table.add_column("Level", style="dim", width=6)
            table.add_column("Name", style="cyan")
            table.add_column("ID", style="dim", no_wrap=True)
            table.add_column("Status", style="white")
            table.add_column("Children", style="magenta")
            
            def add_terms_to_table(terms, level=0):
                for term in terms:
                    indent = "  " * level + ("└─ " if level > 0 else "")
                    children_count = len(term.get("children", []))
                    
                    table.add_row(
                        str(level),
                        indent + term.get("name", "N/A"),
                        term.get("id", "N/A")[:13] + "...",
                        term.get("status", "N/A"),
                        str(children_count) if children_count > 0 else "-"
                    )
                    
                    if term.get("children"):
                        add_terms_to_table(term["children"], level + 1)
            
            add_terms_to_table(hierarchy_terms)
            console.print(table)
        
        console.print(f"\n[dim]Total terms: {total_count} | Max depth: {max_depth_found}[/dim]")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="facets")
@click.option("--domain-id", help="Filter by domain ID", required=False)
@click.option("--facet-fields", multiple=True, help="Specific facet fields to retrieve (status, domain, owner, acronyms)")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def get_term_facets(domain_id, facet_fields, output):
    """Get facets (aggregated statistics) for glossary terms.
    
    Shows distribution of terms by various attributes like status, domain, owner.
    Useful for analytics, dashboards, and building search filters.
    
    Examples:
        # Get all facets
        pvw uc term facets
        
        # Get facets for specific domain
        pvw uc term facets --domain-id <domain-guid>
        
        # Get specific facet fields only
        pvw uc term facets --facet-fields status --facet-fields domain
        
        # Export as JSON
        pvw uc term facets --output json
    """
    try:
        client = UnifiedCatalogClient()
        args = {}
        
        if domain_id:
            args["--domain-id"] = [domain_id]
        if facet_fields:
            args["--facet-fields"] = list(facet_fields)
        
        result = client.get_term_facets(args)
        
        if output == "json":
            console.print_json(data=result)
            return
        
        facets = result.get("facets", {})
        total_count = result.get("totalCount", 0)
        
        if not facets:
            console.print("[yellow]No facets data available.[/yellow]")
            return
        
        console.print(f"\n[bold]📊 Glossary Terms Facets[/bold] (Total: {total_count} terms)\n")
        
        for facet_name, facet_values in facets.items():
            table = Table(title=f"{facet_name.capitalize()} Distribution", show_header=True)
            table.add_column("Value", style="cyan")
            table.add_column("Count", style="green", justify="right")
            table.add_column("Percentage", style="yellow", justify="right")
            
            # Sort by count descending
            sorted_values = sorted(facet_values.items(), key=lambda x: x[1], reverse=True)
            
            for value, count in sorted_values:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                table.add_row(
                    str(value),
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(table)
            console.print()  # Blank line between tables
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="relationships")
@click.option("--term-id", required=True, help="ID of the term to get relationships for")
@click.option("--relationship-type", 
              type=click.Choice(["Synonym", "Related", "Parent"], case_sensitive=False),
              help="Filter by relationship type")
@click.option("--entity-type", help="Filter by entity type (TERM, DOMAIN, DATAPRODUCT, etc.)")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def list_related_entities(term_id, relationship_type, entity_type, output):
    """List all entities related to a specific term.
    
    Shows all relationships including synonyms, related terms, parents, and other
    associated entities. Useful for understanding term connections and dependencies.
    
    Examples:
        # Get all relationships for a term
        pvw uc term relationships --term-id <term-guid>
        
        # Filter only synonyms
        pvw uc term relationships --term-id <term-guid> --relationship-type Synonym
        
        # Filter only related terms
        pvw uc term relationships --term-id <term-guid> --relationship-type Related
        
        # Export as JSON
        pvw uc term relationships --term-id <term-guid> --output json
    """
    try:
        client = UnifiedCatalogClient()
        args = {"--term-id": [term_id]}
        
        if relationship_type:
            args["--relationship-type"] = [relationship_type]
        if entity_type:
            args["--entity-type"] = [entity_type]
        
        result = client.list_related_entities(args)
        
        if output == "json":
            console.print_json(data=result)
            return
        
        relationships = result.get("relationships", [])
        count = result.get("count", len(relationships))
        
        if not relationships:
            console.print("[yellow]No relationships found for this term.[/yellow]")
            return
        
        console.print(f"\n[bold]🔗 Relationships for Term[/bold] (Total: {count})\n")
        
        table = Table(show_header=True)
        table.add_column("Relationship Type", style="cyan")
        table.add_column("Entity ID", style="yellow", no_wrap=True)
        table.add_column("Entity Type", style="green")
        table.add_column("Description", style="white")
        table.add_column("Created", style="dim")
        
        for rel in relationships:
            created_at = rel.get("createdAt", "N/A")
            if created_at != "N/A" and "T" in created_at:
                created_at = created_at.split("T")[0]  # Just show date
            
            table.add_row(
                rel.get("relationshipType", "N/A"),
                rel.get("entityId", "N/A")[:20] + ("..." if len(rel.get("entityId", "")) > 20 else ""),
                rel.get("entityType", "N/A"),
                rel.get("description", "N/A")[:40] + ("..." if len(rel.get("description", "")) > 40 else ""),
                created_at
            )
        
        console.print(table)
        
        # Show summary by type
        type_counts = {}
        for rel in relationships:
            rel_type = rel.get("relationshipType", "Unknown")
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
        
        console.print("\n[bold]Summary by Type:[/bold]")
        for rel_type, count in sorted(type_counts.items()):
            console.print(f"  • {rel_type}: {count}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="sync-classic")
@click.option("--domain-id", required=False, help="Governance domain ID to sync terms from (if not provided, syncs all domains)")
@click.option("--glossary-guid", required=False, help="Target classic glossary GUID (if not provided, creates/uses glossary with domain name)")
@click.option("--create-glossary", is_flag=True, help="Create classic glossary if it doesn't exist")
@click.option("--dry-run", is_flag=True, help="Preview changes without applying them")
@click.option("--update-existing", is_flag=True, help="Update existing classic terms if they already exist")
def sync_classic(domain_id, glossary_guid, create_glossary, dry_run, update_existing):
    """Synchronize Unified Catalog terms to classic glossary terms.
    
    This command bridges the Unified Catalog (business metadata) with classic glossaries,
    enabling you to sync terms from governance domains to traditional glossary structures.
    
    Examples:
        # Sync all terms from a specific domain to its corresponding glossary
        pvw uc term sync-classic --domain-id <domain-guid>
        
        # Sync to a specific glossary
        pvw uc term sync-classic --domain-id <domain-guid> --glossary-guid <glossary-guid>
        
        # Create glossary if needed and sync
        pvw uc term sync-classic --domain-id <domain-guid> --create-glossary
        
        # Preview sync without making changes
        pvw uc term sync-classic --domain-id <domain-guid> --dry-run
        
        # Update existing terms in classic glossary
        pvw uc term sync-classic --domain-id <domain-guid> --update-existing
    """
    try:
        from purviewcli.client._glossary import Glossary
        import tempfile
        import traceback
        
        uc_client = UnifiedCatalogClient()
        glossary_client = Glossary()
        
        console.print("[cyan]" + "-" * 59 + "[/cyan]")
        console.print("[bold cyan]  Unified Catalog → Classic Glossary Sync  [/bold cyan]")
        console.print("[cyan]" + "-" * 59 + "[/cyan]\n")
        
        if dry_run:
            console.print("[yellow][*] DRY RUN MODE - No changes will be made[/yellow]\n")
        
        # Step 1: Get UC terms
        console.print("[bold]Step 1:[/bold] Fetching Unified Catalog terms...")
        uc_args = {}
        if domain_id:
            uc_args["--governance-domain-id"] = [domain_id]
        
        uc_result = uc_client.get_terms(uc_args)
        
        # Extract terms from response
        uc_terms = []
        if isinstance(uc_result, dict):
            uc_terms = uc_result.get("value", [])
        elif isinstance(uc_result, (list, tuple)):
            uc_terms = uc_result
        
        if not uc_terms:
            console.print("[yellow][!] No Unified Catalog terms found.[/yellow]")
            return
        
        console.print(f"[green][OK][/green] Found {len(uc_terms)} UC term(s)\n")
        
        # Step 2: Determine or create target glossary
        console.print("[bold]Step 2:[/bold] Determining target glossary...")
        
        target_glossary_guid = glossary_guid
        
        if not target_glossary_guid:
            # Get domain info to use domain name as glossary name
            if domain_id:
                domain_info = uc_client.get_governance_domain_by_id({"--domain-id": [domain_id]})
                domain_name = domain_info.get("name", "Unknown Domain")
                console.print(f"   Domain: [cyan]{domain_name}[/cyan]")
                
                # Try to find existing glossary with matching name
                all_glossaries = glossary_client.glossaryRead({})
                if isinstance(all_glossaries, dict):
                    all_glossaries = all_glossaries.get("value", [])
                
                for g in all_glossaries:
                    g_name = g.get("name", "")
                    g_qualified = g.get("qualifiedName", "")
                    
                    # Check multiple formats for compatibility:
                    # 1. Exact name match
                    # 2. Standard format: DomainName@Glossary
                    # 3. Old format (for backward compatibility): DomainName@domain-id
                    if (g_name == domain_name or 
                        g_qualified == f"{domain_name}@Glossary" or
                        g_qualified == f"{domain_name}@{domain_id}"):
                        target_glossary_guid = g.get("guid")
                        console.print(f"[green][OK][/green] Found existing glossary: {g_name} ({target_glossary_guid})\n")
                        break
                
                if not target_glossary_guid and create_glossary:
                    if dry_run:
                        console.print(f"[yellow]Would create glossary:[/yellow] {domain_name}\n")
                    else:
                        # Create glossary with simple qualifiedName format
                        qualified_name = domain_name
                        
                        glossary_payload = {
                            "name": domain_name,
                            "qualifiedName": qualified_name,
                            "shortDescription": f"Auto-synced from Unified Catalog domain: {domain_name}",
                            "longDescription": f"This glossary is automatically synchronized with the Unified Catalog governance domain '{domain_name}' (ID: {domain_id})"
                        }
                        
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            json.dump(glossary_payload, f)
                            temp_file = f.name
                        
                        try:
                            new_glossary = glossary_client.glossaryCreate({"--payloadFile": temp_file})
                            target_glossary_guid = new_glossary.get("guid")
                            console.print(f"[green][OK][/green] Created glossary: {domain_name} ({target_glossary_guid})\n")
                        finally:
                            os.unlink(temp_file)
                elif not target_glossary_guid:
                    console.print(f"[red]ERROR:[/red] No target glossary found. Use --glossary-guid or --create-glossary")
                    return
            else:
                console.print("[red]ERROR:[/red] Either --domain-id or --glossary-guid must be provided")
                return
        else:
            console.print(f"[green][OK][/green] Using target glossary: {target_glossary_guid}\n")
        
        # Step 3: Get existing classic glossary terms and glossary name
        console.print("[bold]Step 3:[/bold] Checking existing classic glossary terms...")
        
        existing_terms = {}
        glossary_name = "Glossary"  # Default fallback
        glossary_qualified_name = "Glossary"  # Default fallback for qualified name
        try:
            glossary_details = glossary_client.glossaryReadDetailed({"--glossaryGuid": [target_glossary_guid]})
            existing_term_list = glossary_details.get("terms", [])
            
            # Get glossary name and qualifiedName for term qualifiedName construction
            glossary_name = glossary_details.get("name", "Glossary")
            glossary_qualified_name = glossary_details.get("qualifiedName", f"{glossary_name}@Glossary")
            
            for term in existing_term_list:
                term_name = term.get("displayText") or term.get("name")
                term_guid = term.get("termGuid") or term.get("guid")
                if term_name:
                    existing_terms[term_name.lower()] = term_guid
            
            console.print(f"[green][OK][/green] Found {len(existing_terms)} existing term(s) in classic glossary\n")
        except Exception as e:
            console.print(f"[yellow][!][/yellow] Could not fetch existing terms: {e}\n")
        
        # Step 4: Sync terms
        console.print("[bold]Step 4:[/bold] Synchronizing terms...")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0
        
        for uc_term in uc_terms:
            term_name = uc_term.get("name", "")
            term_description = uc_term.get("description", "")
            term_status = uc_term.get("status", "Draft")
            
            # Check if term already exists
            existing_guid = existing_terms.get(term_name.lower())
            
            if existing_guid and not update_existing:
                console.print(f"   [dim][-] Skipping:[/dim] {term_name} (already exists)")
                skipped_count += 1
                continue
            
            try:
                if existing_guid and update_existing:
                    # Update existing term
                    if dry_run:
                        console.print(f"   [yellow]Would update:[/yellow] {term_name}")
                        updated_count += 1
                    else:
                        # Construct qualifiedName: TermName@GlossaryQualifiedName
                        # Use the stored glossary_qualified_name from Step 3
                        term_qualified_name = f"{term_name}@{glossary_qualified_name}"
                        
                        update_payload = {
                            "guid": existing_guid,
                            "name": term_name,
                            "qualifiedName": term_qualified_name,
                            "longDescription": term_description,
                            "status": term_status,
                            "anchor": {"glossaryGuid": target_glossary_guid},
                            "termTemplate": {
                                "termTemplateName": "System default"
                            }
                        }
                        
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            json.dump(update_payload, f)
                            temp_file = f.name
                        
                        try:
                            glossary_client.glossaryUpdateTerm({"--payloadFile": temp_file})
                            console.print(f"   [green][OK] Updated:[/green] {term_name}")
                            updated_count += 1
                        finally:
                            os.unlink(temp_file)
                else:
                    # Create new term
                    if dry_run:
                        console.print(f"   [yellow]Would create:[/yellow] {term_name}")
                        created_count += 1
                    else:
                        # Construct qualifiedName: TermName@GlossaryQualifiedName
                        # Use the stored glossary_qualified_name from Step 3
                        term_qualified_name = f"{term_name}@{glossary_qualified_name}"
                        
                        create_payload = {
                            "name": term_name,
                            "qualifiedName": term_qualified_name,
                            "longDescription": term_description,
                            "status": term_status,
                            "anchor": {"glossaryGuid": target_glossary_guid},
                            "termTemplate": {
                                "termTemplateName": "System default"
                            }
                        }
                        
                        # Add optional fields
                        if uc_term.get("acronyms"):
                            create_payload["abbreviation"] = ", ".join(uc_term["acronyms"])
                        
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            json.dump(create_payload, f)
                            temp_file = f.name
                        
                        try:
                            glossary_client.glossaryCreateTerm({"--payloadFile": temp_file})
                            console.print(f"   [green][OK] Created:[/green] {term_name}")
                            created_count += 1
                        finally:
                            os.unlink(temp_file)
            
            except Exception as e:
                console.print(f"   [red][X] Failed:[/red] {term_name} - {str(e)}")
                failed_count += 1
        
        # Summary
        console.print("\n[cyan]" + "-" * 59 + "[/cyan]")
        console.print("[bold cyan]  Synchronization Summary  [/bold cyan]")
        console.print("[cyan]" + "-" * 59 + "[/cyan]")
        
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Count", style="cyan")
        
        summary_table.add_row("Total UC Terms", str(len(uc_terms)))
        summary_table.add_row("Created", f"[green]{created_count}[/green]")
        summary_table.add_row("Updated", f"[yellow]{updated_count}[/yellow]")
        summary_table.add_row("Skipped", f"[dim]{skipped_count}[/dim]")
        summary_table.add_row("Failed", f"[red]{failed_count}[/red]")
        
        console.print(summary_table)
        
        if dry_run:
            console.print("\n[yellow][TIP] This was a dry run. Use without --dry-run to apply changes.[/yellow]")
        elif failed_count == 0 and (created_count > 0 or updated_count > 0):
            console.print("\n[green][OK] Synchronization completed successfully![/green]")
        
    except Exception as e:
        console.print(f"\n[red]ERROR:[/red] {str(e)}")
        import traceback
        if os.getenv("PURVIEWCLI_DEBUG"):
            console.print(traceback.format_exc())


# ========================================
# OBJECTIVES AND KEY RESULTS (OKRs)
# ========================================


@uc.group()
def objective():
    """Manage objectives and key results (OKRs)."""
    pass


@objective.command()
@click.option("--definition", required=True, help="Definition of the objective")
@click.option("--domain-id", required=True, help="Governance domain ID")
@click.option(
    "--status",
    required=False,
    default="Draft",
    type=click.Choice(["Draft", "Published", "Archived"]),
    help="Status of the objective",
)
@click.option(
    "--owner-id",
    required=False,
    help="Owner Entra ID (can be specified multiple times)",
    multiple=True,
)
@click.option(
    "--target-date", required=False, help="Target date (ISO format: 2025-12-30T14:00:00.000Z)"
)
def create(definition, domain_id, status, owner_id, target_date):
    """Create a new objective."""
    try:
        client = UnifiedCatalogClient()

        args = {
            "--definition": [definition],
            "--governance-domain-id": [domain_id],
            "--status": [status],
        }

        if owner_id:
            args["--owner-id"] = list(owner_id)
        if target_date:
            args["--target-date"] = [target_date]

        result = client.create_objective(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green] SUCCESS:[/green] Created objective")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@objective.command(name="list")
@click.option("--domain-id", required=True, help="Governance domain ID to list objectives from")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
def list_objectives(domain_id, output_json):
    """List all objectives in a governance domain."""
    try:
        client = UnifiedCatalogClient()
        args = {"--governance-domain-id": [domain_id]}
        result = client.get_objectives(args)

        if not result:
            console.print("[yellow]No objectives found.[/yellow]")
            return

        # Handle response format
        if isinstance(result, (list, tuple)):
            objectives = result
        elif isinstance(result, dict):
            objectives = result.get("value", [])
        else:
            objectives = []

        if not objectives:
            console.print("[yellow]No objectives found.[/yellow]")
            return

        # Output in JSON format if requested
        if output_json:
            _format_json_output(objectives)
            return

        table = Table(title="Objectives")
        table.add_column("ID", style="cyan")
        table.add_column("Definition", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Target Date", style="blue")

        for obj in objectives:
            definition = obj.get("definition", "")
            if len(definition) > 50:
                definition = definition[:50] + "..."

            table.add_row(
                obj.get("id", "N/A"),
                definition,
                obj.get("status", "N/A"),
                obj.get("targetDate", "N/A"),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@objective.command()
@click.option("--objective-id", required=True, help="ID of the objective")
def show(objective_id):
    """Show details of an objective."""
    try:
        client = UnifiedCatalogClient()
        args = {"--objective-id": [objective_id]}
        result = client.get_objective_by_id(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Objective not found')}")
            return

        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@objective.command(name="facets")
@click.option("--domain-id", help="Filter by domain ID", required=False)
@click.option("--facet-fields", multiple=True, help="Specific facet fields to retrieve (status, period, progressPercentage, owner)")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def get_objective_facets(domain_id, facet_fields, output):
    """Get facets (aggregated statistics) for Objectives (OKRs).
    
    Shows distribution of objectives by status, period, progress, and owner.
    Essential for OKR dashboards, performance tracking, and risk management.
    
    Examples:
        # Get all objective facets
        pvw uc objective facets
        
        # Get facets for specific domain
        pvw uc objective facets --domain-id <domain-guid>
        
        # Get specific facet fields only
        pvw uc objective facets --facet-fields status --facet-fields period
        
        # Export as JSON
        pvw uc objective facets --output json
    """
    try:
        client = UnifiedCatalogClient()
        args = {}
        
        if domain_id:
            args["--domain-id"] = [domain_id]
        if facet_fields:
            args["--facet-fields"] = list(facet_fields)
        
        result = client.get_objective_facets(args)
        
        if output == "json":
            console.print_json(data=result)
            return
        
        facets = result.get("facets", {})
        total_count = result.get("totalCount", 0)
        
        if not facets:
            console.print("[yellow]No facets data available.[/yellow]")
            return
        
        console.print(f"\n[bold]🎯 Objectives (OKRs) Facets[/bold] (Total: {total_count} objectives)\n")
        
        # Define facet display order and styling
        facet_order = ["status", "period", "progressPercentage", "owner"]
        facet_icons = {
            "status": "📊",
            "period": "📅",
            "progressPercentage": "📊",
            "owner": "👤"
        }
        
        for facet_name in facet_order:
            if facet_name not in facets:
                continue
                
            facet_values = facets[facet_name]
            icon = facet_icons.get(facet_name, "📌")
            
            table = Table(title=f"{icon} {facet_name.capitalize()} Distribution", show_header=True)
            table.add_column("Value", style="cyan")
            table.add_column("Count", style="green", justify="right")
            table.add_column("Percentage", style="yellow", justify="right")
            
            # Sort by count descending
            sorted_values = sorted(facet_values.items(), key=lambda x: x[1], reverse=True)
            
            for value, count in sorted_values:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                
                # Add color coding for status
                if facet_name == "status":
                    value_lower = str(value).lower()
                    if value_lower == "completed":
                        value_display = f"[green bold]{value}[/green bold]"
                    elif value_lower == "in progress":
                        value_display = f"[blue]{value}[/blue]"
                    elif value_lower == "at risk":
                        value_display = f"[yellow bold]{value}[/yellow bold]"
                    elif value_lower == "blocked":
                        value_display = f"[red bold]{value}[/red bold]"
                    elif value_lower == "not started":
                        value_display = f"[dim]{value}[/dim]"
                    else:
                        value_display = str(value)
                # Color code progress percentages
                elif facet_name == "progressPercentage":
                    if "76-100" in str(value) or "100" in str(value):
                        value_display = f"[green]{value}[/green]"
                    elif "51-75" in str(value):
                        value_display = f"[blue]{value}[/blue]"
                    elif "26-50" in str(value):
                        value_display = f"[yellow]{value}[/yellow]"
                    else:
                        value_display = f"[red]{value}[/red]"
                else:
                    value_display = str(value)
                
                table.add_row(
                    value_display,
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(table)
            console.print()  # Blank line between tables
        
        # Display any remaining facets not in the predefined order
        for facet_name, facet_values in facets.items():
            if facet_name in facet_order:
                continue
                
            table = Table(title=f"{facet_name.capitalize()} Distribution", show_header=True)
            table.add_column("Value", style="cyan")
            table.add_column("Count", style="green", justify="right")
            table.add_column("Percentage", style="yellow", justify="right")
            
            sorted_values = sorted(facet_values.items(), key=lambda x: x[1], reverse=True)
            
            for value, count in sorted_values:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                table.add_row(
                    str(value),
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(table)
            console.print()
        
        # Show OKR health metrics
        if "status" in facets:
            completed = facets["status"].get("Completed", 0)
            in_progress = facets["status"].get("In Progress", 0)
            at_risk = facets["status"].get("At Risk", 0)
            blocked = facets["status"].get("Blocked", 0)
            
            completion_rate = (completed / total_count * 100) if total_count > 0 else 0
            
            console.print("[bold]📊 OKR Health Dashboard:[/bold]")
            console.print(f"  ✅ Completed: {completed} ({completion_rate:.1f}%)")
            console.print(f"  🔵 In Progress: {in_progress}")
            if at_risk > 0:
                console.print(f"  ⚠️  At Risk: {at_risk} [yellow](needs attention!)[/yellow]")
            if blocked > 0:
                console.print(f"  🚫 Blocked: {blocked} [red bold](critical!)[/red bold]")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@objective.command(name="query")
@click.option("--ids", multiple=True, help="Filter by specific objective IDs (GUIDs)")
@click.option("--domain-ids", multiple=True, help="Filter by domain IDs (GUIDs)")
@click.option("--definition", help="Filter by definition text (partial match)")
@click.option("--owners", multiple=True, help="Filter by owner IDs (GUIDs)")
@click.option("--status", type=click.Choice(["DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"], case_sensitive=False),
              help="Filter by status")
@click.option("--multi-status", multiple=True,
              type=click.Choice(["DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"], case_sensitive=False),
              help="Filter by multiple statuses")
@click.option("--skip", type=int, default=0, help="Number of items to skip (pagination)")
@click.option("--top", type=int, default=100, help="Number of items to return (max 1000)")
@click.option("--order-by-field", help="Field to sort by (e.g., 'name', 'status')")
@click.option("--order-by-direction", type=click.Choice(["asc", "desc"]), default="asc",
              help="Sort direction")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def query_objectives(ids, domain_ids, definition, owners, status, multi_status,
                    skip, top, order_by_field, order_by_direction, output):
    """Query objectives with advanced filters.
    
    Perform complex searches across OKR objectives using multiple filter criteria.
    Supports pagination and custom sorting.
    
    Examples:
        # Find all objectives in a specific domain
        pvw uc objective query --domain-ids <domain-guid>
        
        # Search by definition text
        pvw uc objective query --definition "customer satisfaction"
        
        # Filter by owner and status
        pvw uc objective query --owners <user-guid> --status ACTIVE
        
        # Find all completed objectives
        pvw uc objective query --multi-status COMPLETED ARCHIVED
        
        # Pagination example
        pvw uc objective query --skip 0 --top 50 --order-by-field name --order-by-direction asc
    """
    try:
        client = UnifiedCatalogClient()
        args = {}
        
        # Build args dict from parameters
        if ids:
            args["--ids"] = list(ids)
        if domain_ids:
            args["--domain-ids"] = list(domain_ids)
        if definition:
            args["--definition"] = [definition]
        if owners:
            args["--owners"] = list(owners)
        if status:
            args["--status"] = [status]
        if multi_status:
            args["--multi-status"] = list(multi_status)
        if skip:
            args["--skip"] = [str(skip)]
        if top:
            args["--top"] = [str(top)]
        if order_by_field:
            args["--order-by-field"] = [order_by_field]
            args["--order-by-direction"] = [order_by_direction]
        
        result = client.query_objectives(args)
        
        if output == "json":
            console.print_json(data=result)
        else:
            objectives = result.get("value", []) if result else []
            
            if not objectives:
                console.print("[yellow]No objectives found matching the query.[/yellow]")
                return
            
            # Check for pagination
            next_link = result.get("nextLink")
            if next_link:
                console.print(f"[dim]Note: More results available (nextLink provided)[/dim]\n")
            
            table = Table(title=f"Query Results ({len(objectives)} found)", show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("ID", style="dim", no_wrap=True)
            table.add_column("Domain", style="yellow", no_wrap=True)
            table.add_column("Status", style="white")
            table.add_column("Owner", style="green", no_wrap=True)
            
            for obj in objectives:
                owner_display = "N/A"
                if obj.get("owner"):
                    owner_display = obj["owner"].get("id", "N/A")[:13] + "..."
                
                table.add_row(
                    obj.get("name", "N/A"),
                    obj.get("id", "N/A")[:13] + "...",
                    obj.get("domain", "N/A")[:13] + "...",
                    obj.get("status", "N/A"),
                    owner_display
                )
            
            console.print(table)
            
            # Show pagination info
            if skip > 0 or next_link:
                console.print(f"\n[dim]Showing items {skip + 1} to {skip + len(objectives)}[/dim]")
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


# ========================================
# CRITICAL DATA ELEMENTS (CDEs)
# ========================================


@uc.group()
def cde():
    """Manage critical data elements."""
    pass


@cde.command()
@click.option("--name", required=True, help="Name of the critical data element")
@click.option("--description", required=False, default="", help="Description of the CDE")
@click.option("--domain-id", required=True, help="Governance domain ID")
@click.option(
    "--data-type",
    required=True,
    type=click.Choice(["String", "Number", "Boolean", "Date", "DateTime"]),
    help="Data type of the CDE",
)
@click.option(
    "--status",
    required=False,
    default="Draft",
    type=click.Choice(["Draft", "Published", "Archived"]),
    help="Status of the CDE",
)
@click.option(
    "--owner-id",
    required=False,
    help="Owner Entra ID (can be specified multiple times)",
    multiple=True,
)
def create(name, description, domain_id, data_type, status, owner_id):
    """Create a new critical data element."""
    try:
        client = UnifiedCatalogClient()

        args = {
            "--name": [name],
            "--description": [description],
            "--governance-domain-id": [domain_id],
            "--data-type": [data_type],
            "--status": [status],
        }

        if owner_id:
            args["--owner-id"] = list(owner_id)

        result = client.create_critical_data_element(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green] SUCCESS:[/green] Created critical data element '{name}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@cde.command(name="list")
@click.option("--domain-id", required=True, help="Governance domain ID to list CDEs from")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
def list_cdes(domain_id, output_json):
    """List all critical data elements in a governance domain."""
    try:
        client = UnifiedCatalogClient()
        args = {"--governance-domain-id": [domain_id]}
        result = client.get_critical_data_elements(args)

        if not result:
            console.print("[yellow]No critical data elements found.[/yellow]")
            return

        # Handle response format
        if isinstance(result, (list, tuple)):
            cdes = result
        elif isinstance(result, dict):
            cdes = result.get("value", [])
        else:
            cdes = []

        if not cdes:
            console.print("[yellow]No critical data elements found.[/yellow]")
            return

        # Output in JSON format if requested
        if output_json:
            _format_json_output(cdes)
            return

        table = Table(title="Critical Data Elements")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Data Type", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Description", style="white")

        for cde_item in cdes:
            desc = cde_item.get("description", "")
            if len(desc) > 30:
                desc = desc[:30] + "..."

            table.add_row(
                cde_item.get("id", "N/A"),
                cde_item.get("name", "N/A"),
                cde_item.get("dataType", "N/A"),
                cde_item.get("status", "N/A"),
                desc,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@cde.command()
@click.option("--cde-id", required=True, help="ID of the critical data element")
def show(cde_id):
    """Show details of a critical data element."""
    try:
        client = UnifiedCatalogClient()
        args = {"--cde-id": [cde_id]}
        result = client.get_critical_data_element_by_id(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'CDE not found')}")
            return

        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@cde.command(name="add-relationship")
@click.option("--cde-id", required=True, help="Critical data element ID (GUID)")
@click.option("--entity-type", required=True, 
              type=click.Choice(["CRITICALDATACOLUMN", "TERM", "DATAASSET", "DATAPRODUCT"], case_sensitive=False),
              help="Type of entity to relate to")
@click.option("--entity-id", required=True, help="Entity ID (GUID) to relate to")
@click.option("--asset-id", help="Asset ID (GUID) - defaults to entity-id if not provided")
@click.option("--relationship-type", default="Related", help="Relationship type (default: Related)")
@click.option("--description", default="", help="Description of the relationship")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def add_cde_relationship(cde_id, entity_type, entity_id, asset_id, relationship_type, description, output):
    """Create a relationship for a critical data element.
    
    Links a CDE to another entity like a critical data column, term, or data product.
    
    Examples:
        pvw uc cde add-relationship --cde-id <id> --entity-type CRITICALDATACOLUMN --entity-id <col-id>
        pvw uc cde add-relationship --cde-id <id> --entity-type TERM --entity-id <term-id> --description "Primary term"
    """
    try:
        client = UnifiedCatalogClient()
        args = {
            "--cde-id": [cde_id],
            "--entity-type": [entity_type],
            "--entity-id": [entity_id],
            "--relationship-type": [relationship_type],
            "--description": [description]
        }
        
        if asset_id:
            args["--asset-id"] = [asset_id]
        
        result = client.create_cde_relationship(args)
        
        if output == "json":
            console.print_json(data=result)
        else:
            if result and isinstance(result, dict):
                console.print("[green]SUCCESS:[/green] Created CDE relationship")
                table = Table(title="CDE Relationship", show_header=True)
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")
                
                table.add_row("Entity ID", result.get("entityId", "N/A"))
                table.add_row("Relationship Type", result.get("relationshipType", "N/A"))
                table.add_row("Description", result.get("description", "N/A"))
                
                if "systemData" in result:
                    sys_data = result["systemData"]
                    table.add_row("Created By", sys_data.get("createdBy", "N/A"))
                    table.add_row("Created At", sys_data.get("createdAt", "N/A"))
                
                console.print(table)
            else:
                console.print("[green]SUCCESS:[/green] Created CDE relationship")
                
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@cde.command(name="list-relationships")
@click.option("--cde-id", required=True, help="Critical data element ID (GUID)")
@click.option("--entity-type", 
              type=click.Choice(["CRITICALDATACOLUMN", "TERM", "DATAASSET", "DATAPRODUCT"], case_sensitive=False),
              help="Filter by entity type (optional)")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def list_cde_relationships(cde_id, entity_type, output):
    """List relationships for a critical data element.
    
    Shows all entities linked to this CDE, optionally filtered by type.
    
    Examples:
        pvw uc cde list-relationships --cde-id <id>
        pvw uc cde list-relationships --cde-id <id> --entity-type CRITICALDATACOLUMN
    """
    try:
        client = UnifiedCatalogClient()
        args = {"--cde-id": [cde_id]}
        
        if entity_type:
            args["--entity-type"] = [entity_type]
        
        result = client.get_cde_relationships(args)
        
        if output == "json":
            console.print_json(data=result)
        else:
            relationships = result.get("value", []) if result else []
            
            if not relationships:
                console.print(f"[yellow]No relationships found for CDE '{cde_id}'[/yellow]")
                return
            
            table = Table(title=f"CDE Relationships ({len(relationships)} found)", show_header=True)
            table.add_column("Entity ID", style="cyan")
            table.add_column("Relationship Type", style="white")
            table.add_column("Description", style="white")
            table.add_column("Created", style="dim")
            
            for rel in relationships:
                table.add_row(
                    rel.get("entityId", "N/A"),
                    rel.get("relationshipType", "N/A"),
                    rel.get("description", "")[:50] + ("..." if len(rel.get("description", "")) > 50 else ""),
                    rel.get("systemData", {}).get("createdAt", "N/A")[:10]
                )
            
            console.print(table)
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@cde.command(name="remove-relationship")
@click.option("--cde-id", required=True, help="Critical data element ID (GUID)")
@click.option("--entity-type", required=True,
              type=click.Choice(["CRITICALDATACOLUMN", "TERM", "DATAASSET", "DATAPRODUCT"], case_sensitive=False),
              help="Type of entity to unlink")
@click.option("--entity-id", required=True, help="Entity ID (GUID) to unlink")
@click.option("--confirm/--no-confirm", default=True, help="Ask for confirmation before deleting")
def remove_cde_relationship(cde_id, entity_type, entity_id, confirm):
    """Delete a relationship between a CDE and an entity.
    
    Removes the link between a critical data element and a specific entity.
    
    Examples:
        pvw uc cde remove-relationship --cde-id <id> --entity-type CRITICALDATACOLUMN --entity-id <col-id>
        pvw uc cde remove-relationship --cde-id <id> --entity-type TERM --entity-id <term-id> --no-confirm
    """
    try:
        if confirm:
            confirm = click.confirm(
                f"Are you sure you want to delete CDE relationship to {entity_type} '{entity_id}'?",
                default=False
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        client = UnifiedCatalogClient()
        args = {
            "--cde-id": [cde_id],
            "--entity-type": [entity_type],
            "--entity-id": [entity_id]
        }
        
        result = client.delete_cde_relationship(args)
        
        # DELETE returns 204 No Content on success
        if result is None or (isinstance(result, dict) and not result.get("error")):
            console.print(f"[green]SUCCESS:[/green] Deleted CDE relationship to {entity_type} '{entity_id}'")
        elif isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
        else:
            console.print(f"[green]SUCCESS:[/green] Deleted CDE relationship")
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@cde.command(name="query")
@click.option("--ids", multiple=True, help="Filter by specific CDE IDs (GUIDs)")
@click.option("--domain-ids", multiple=True, help="Filter by domain IDs (GUIDs)")
@click.option("--name-keyword", help="Filter by name keyword (partial match)")
@click.option("--owners", multiple=True, help="Filter by owner IDs (GUIDs)")
@click.option("--status", type=click.Choice(["DRAFT", "PUBLISHED", "EXPIRED"], case_sensitive=False),
              help="Filter by status")
@click.option("--multi-status", multiple=True,
              type=click.Choice(["DRAFT", "PUBLISHED", "EXPIRED"], case_sensitive=False),
              help="Filter by multiple statuses")
@click.option("--skip", type=int, default=0, help="Number of items to skip (pagination)")
@click.option("--top", type=int, default=100, help="Number of items to return (max 1000)")
@click.option("--order-by-field", help="Field to sort by (e.g., 'name', 'status')")
@click.option("--order-by-direction", type=click.Choice(["asc", "desc"]), default="asc",
              help="Sort direction")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def query_cdes(ids, domain_ids, name_keyword, owners, status, multi_status,
              skip, top, order_by_field, order_by_direction, output):
    """Query critical data elements with advanced filters.
    
    Perform complex searches across CDEs using multiple filter criteria.
    Supports pagination and custom sorting.
    
    Examples:
        # Find all CDEs in a specific domain
        pvw uc cde query --domain-ids <domain-guid>
        
        # Search by keyword
        pvw uc cde query --name-keyword "customer"
        
        # Filter by owner and status
        pvw uc cde query --owners <user-guid> --status PUBLISHED
        
        # Find all published or expired CDEs
        pvw uc cde query --multi-status PUBLISHED EXPIRED
        
        # Pagination example
        pvw uc cde query --skip 0 --top 50 --order-by-field name --order-by-direction desc
    """
    try:
        client = UnifiedCatalogClient()
        args = {}
        
        # Build args dict from parameters
        if ids:
            args["--ids"] = list(ids)
        if domain_ids:
            args["--domain-ids"] = list(domain_ids)
        if name_keyword:
            args["--name-keyword"] = [name_keyword]
        if owners:
            args["--owners"] = list(owners)
        if status:
            args["--status"] = [status]
        if multi_status:
            args["--multi-status"] = list(multi_status)
        if skip:
            args["--skip"] = [str(skip)]
        if top:
            args["--top"] = [str(top)]
        if order_by_field:
            args["--order-by-field"] = [order_by_field]
            args["--order-by-direction"] = [order_by_direction]
        
        result = client.query_critical_data_elements(args)
        
        if output == "json":
            console.print_json(data=result)
        else:
            cdes = result.get("value", []) if result else []
            
            if not cdes:
                console.print("[yellow]No critical data elements found matching the query.[/yellow]")
                return
            
            # Check for pagination
            next_link = result.get("nextLink")
            if next_link:
                console.print(f"[dim]Note: More results available (nextLink provided)[/dim]\n")
            
            table = Table(title=f"Query Results ({len(cdes)} found)", show_header=True)
            table.add_column("Name", style="cyan")
            table.add_column("ID", style="dim", no_wrap=True)
            table.add_column("Domain", style="yellow", no_wrap=True)
            table.add_column("Status", style="white")
            table.add_column("Data Type", style="green")
            
            for cde in cdes:
                table.add_row(
                    cde.get("name", "N/A"),
                    cde.get("id", "N/A")[:13] + "...",
                    cde.get("domain", "N/A")[:13] + "...",
                    cde.get("status", "N/A"),
                    cde.get("dataType", "N/A")
                )
            
            console.print(table)
            
            # Show pagination info
            if skip > 0 or next_link:
                console.print(f"\n[dim]Showing items {skip + 1} to {skip + len(cdes)}[/dim]")
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@cde.command(name="facets")
@click.option("--domain-id", help="Filter by domain ID", required=False)
@click.option("--facet-fields", multiple=True, help="Specific facet fields to retrieve (criticalityLevel, complianceFramework, status, domain)")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
def get_cde_facets(domain_id, facet_fields, output):
    """Get facets (aggregated statistics) for Critical Data Elements.
    
    Shows distribution of CDEs by criticality level, compliance framework, status, and domain.
    Essential for governance dashboards, compliance reporting, and risk assessment.
    
    Examples:
        # Get all CDE facets
        pvw uc cde facets
        
        # Get facets for specific domain
        pvw uc cde facets --domain-id <domain-guid>
        
        # Get specific facet fields only
        pvw uc cde facets --facet-fields criticalityLevel --facet-fields complianceFramework
        
        # Export as JSON
        pvw uc cde facets --output json
    """
    try:
        client = UnifiedCatalogClient()
        args = {}
        
        if domain_id:
            args["--domain-id"] = [domain_id]
        if facet_fields:
            args["--facet-fields"] = list(facet_fields)
        
        result = client.get_cde_facets(args)
        
        if output == "json":
            console.print_json(data=result)
            return
        
        facets = result.get("facets", {})
        total_count = result.get("totalCount", 0)
        
        if not facets:
            console.print("[yellow]No facets data available.[/yellow]")
            return
        
        console.print(f"\n[bold]🔒 Critical Data Elements Facets[/bold] (Total: {total_count} CDEs)\n")
        
        # Define facet display order and styling
        facet_order = ["criticalityLevel", "complianceFramework", "status", "domain"]
        facet_icons = {
            "criticalityLevel": "⚠️",
            "complianceFramework": "📋",
            "status": "📊",
            "domain": "🏢"
        }
        
        for facet_name in facet_order:
            if facet_name not in facets:
                continue
                
            facet_values = facets[facet_name]
            icon = facet_icons.get(facet_name, "📌")
            
            table = Table(title=f"{icon} {facet_name.capitalize()} Distribution", show_header=True)
            table.add_column("Value", style="cyan")
            table.add_column("Count", style="green", justify="right")
            table.add_column("Percentage", style="yellow", justify="right")
            
            # Sort by count descending
            sorted_values = sorted(facet_values.items(), key=lambda x: x[1], reverse=True)
            
            for value, count in sorted_values:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                
                # Add color coding for criticality levels
                if facet_name == "criticalityLevel":
                    if value.lower() == "high":
                        value_display = f"[red bold]{value}[/red bold]"
                    elif value.lower() == "medium":
                        value_display = f"[yellow]{value}[/yellow]"
                    else:
                        value_display = f"[green]{value}[/green]"
                else:
                    value_display = str(value)
                
                table.add_row(
                    value_display,
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(table)
            console.print()  # Blank line between tables
        
        # Display any remaining facets not in the predefined order
        for facet_name, facet_values in facets.items():
            if facet_name in facet_order:
                continue
                
            table = Table(title=f"{facet_name.capitalize()} Distribution", show_header=True)
            table.add_column("Value", style="cyan")
            table.add_column("Count", style="green", justify="right")
            table.add_column("Percentage", style="yellow", justify="right")
            
            sorted_values = sorted(facet_values.items(), key=lambda x: x[1], reverse=True)
            
            for value, count in sorted_values:
                percentage = (count / total_count * 100) if total_count > 0 else 0
                table.add_row(
                    str(value),
                    str(count),
                    f"{percentage:.1f}%"
                )
            
            console.print(table)
            console.print()
        
        # Show compliance summary
        if "complianceFramework" in facets:
            console.print("[bold]🛡️ Compliance Coverage Summary:[/bold]")
            for framework, count in sorted(facets["complianceFramework"].items()):
                console.print(f"  • {framework}: {count} CDEs")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


# ========================================
# KEY RESULTS (OKRs)
# ========================================


@uc.group()
def keyresult():
    """Manage key results for objectives (OKRs)."""
    pass


@keyresult.command(name="list")
@click.option("--objective-id", required=True, help="Objective ID to list key results for")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
def list_key_results(objective_id, output_json):
    """List all key results for an objective."""
    try:
        client = UnifiedCatalogClient()
        args = {"--objective-id": [objective_id]}
        result = client.get_key_results(args)

        if not result:
            console.print("[yellow]No key results found.[/yellow]")
            return

        # Handle response format
        if isinstance(result, (list, tuple)):
            key_results = result
        elif isinstance(result, dict):
            key_results = result.get("value", [])
        else:
            key_results = []

        if not key_results:
            console.print("[yellow]No key results found.[/yellow]")
            return

        # Output in JSON format if requested
        if output_json:
            _format_json_output(key_results)
            return

        table = Table(title=f"Key Results for Objective {objective_id[:8]}...")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Definition", style="green", max_width=50)
        table.add_column("Progress", style="blue")
        table.add_column("Goal", style="yellow")
        table.add_column("Max", style="magenta")
        table.add_column("Status", style="white")

        for kr in key_results:
            definition = kr.get("definition", "N/A")
            if len(definition) > 47:
                definition = definition[:47] + "..."
            
            table.add_row(
                kr.get("id", "N/A")[:13] + "...",
                definition,
                str(kr.get("progress", "N/A")),
                str(kr.get("goal", "N/A")),
                str(kr.get("max", "N/A")),
                kr.get("status", "N/A"),
            )

        console.print(table)
        console.print(f"\n[dim]Found {len(key_results)} key result(s)[/dim]")

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@keyresult.command()
@click.option("--objective-id", required=True, help="Objective ID")
@click.option("--key-result-id", required=True, help="Key result ID")
def show(objective_id, key_result_id):
    """Show details of a key result."""
    try:
        client = UnifiedCatalogClient()
        args = {
            "--objective-id": [objective_id],
            "--key-result-id": [key_result_id]
        }
        result = client.get_key_result_by_id(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Key result not found')}")
            return

        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@keyresult.command()
@click.option("--objective-id", required=True, help="Objective ID")
@click.option("--governance-domain-id", required=True, help="Governance domain ID")
@click.option("--definition", required=True, help="Definition/description of the key result")
@click.option("--progress", required=False, type=int, default=0, help="Current progress value (default: 0)")
@click.option("--goal", required=True, type=int, help="Target goal value")
@click.option("--max", "max_value", required=False, type=int, default=100, help="Maximum possible value (default: 100)")
@click.option(
    "--status",
    required=False,
    default="OnTrack",
    type=click.Choice(["OnTrack", "AtRisk", "OffTrack", "Completed"]),
    help="Status of the key result",
)
def create(objective_id, governance_domain_id, definition, progress, goal, max_value, status):
    """Create a new key result for an objective."""
    try:
        client = UnifiedCatalogClient()

        args = {
            "--objective-id": [objective_id],
            "--governance-domain-id": [governance_domain_id],
            "--definition": [definition],
            "--progress": [str(progress)],
            "--goal": [str(goal)],
            "--max": [str(max_value)],
            "--status": [status],
        }

        result = client.create_key_result(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green]SUCCESS:[/green] Created key result")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@keyresult.command()
@click.option("--objective-id", required=True, help="Objective ID")
@click.option("--key-result-id", required=True, help="Key result ID to update")
@click.option("--governance-domain-id", required=False, help="Governance domain ID")
@click.option("--definition", required=False, help="New definition/description")
@click.option("--progress", required=False, type=int, help="New progress value")
@click.option("--goal", required=False, type=int, help="New goal value")
@click.option("--max", "max_value", required=False, type=int, help="New maximum value")
@click.option(
    "--status",
    required=False,
    type=click.Choice(["OnTrack", "AtRisk", "OffTrack", "Completed"]),
    help="Status of the key result",
)
def update(objective_id, key_result_id, governance_domain_id, definition, progress, goal, max_value, status):
    """Update an existing key result."""
    try:
        client = UnifiedCatalogClient()

        # Build args dictionary - only include provided values
        args = {
            "--objective-id": [objective_id],
            "--key-result-id": [key_result_id]
        }

        if governance_domain_id:
            args["--governance-domain-id"] = [governance_domain_id]
        if definition:
            args["--definition"] = [definition]
        if progress is not None:
            args["--progress"] = [str(progress)]
        if goal is not None:
            args["--goal"] = [str(goal)]
        if max_value is not None:
            args["--max"] = [str(max_value)]
        if status:
            args["--status"] = [status]

        result = client.update_key_result(args)

        if not result:
            console.print("[red]ERROR:[/red] No response received")
            return
        if isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
            return

        console.print(f"[green]SUCCESS:[/green] Updated key result '{key_result_id}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@keyresult.command()
@click.option("--objective-id", required=True, help="Objective ID")
@click.option("--key-result-id", required=True, help="Key result ID to delete")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt")
def delete(objective_id, key_result_id, yes):
    """Delete a key result."""
    try:
        if not yes:
            confirm = click.confirm(
                f"Are you sure you want to delete key result '{key_result_id}'?",
                default=False
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return

        client = UnifiedCatalogClient()
        args = {
            "--objective-id": [objective_id],
            "--key-result-id": [key_result_id]
        }
        result = client.delete_key_result(args)

        # DELETE operations may return empty response on success
        if result is None or (isinstance(result, dict) and not result.get("error")):
            console.print(f"[green]SUCCESS:[/green] Deleted key result '{key_result_id}'")
        elif isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
        else:
            console.print(f"[green]SUCCESS:[/green] Deleted key result")
            if result:
                console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


# ========================================
# HEALTH MANAGEMENT - IMPLEMENTED! 
# ========================================

# Import and register health commands from dedicated module
from purviewcli.cli.health import health as health_commands
uc.add_command(health_commands, name="health")


# ========================================
# DATA POLICIES (NEW)
# ========================================


@uc.group()
def policy():
    """Manage data governance policies."""
    pass


@policy.command(name="list")
@click.option("--output", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_policies(output):
    """List all data governance policies."""
    client = UnifiedCatalogClient()
    response = client.list_policies({})
    
    if output == "json":
        console.print_json(json.dumps(response))
    else:
        # API returns 'values' (plural), not 'value'
        policies = response.get("values", response.get("value", []))
        
        if policies:
            table = Table(title="[bold cyan]Data Governance Policies[/bold cyan]", show_header=True)
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Name", style="green")
            table.add_column("Entity Type", style="yellow")
            table.add_column("Entity ID", style="magenta", no_wrap=True)
            table.add_column("Rules", style="white")
            
            for item in policies:
                props = item.get("properties", {})
                entity = props.get("entity", {})
                entity_type = entity.get("type", "N/A")
                entity_ref = entity.get("referenceName", "N/A")
                
                # Count rules
                decision_rules = len(props.get("decisionRules", []))
                attribute_rules = len(props.get("attributeRules", []))
                rules_summary = f"{decision_rules} decision, {attribute_rules} attribute"
                
                table.add_row(
                    item.get("id", "N/A")[:36],  # Show only GUID
                    item.get("name", "N/A"),
                    entity_type.replace("Reference", ""),  # Clean up type name
                    entity_ref[:36],  # Show only GUID
                    rules_summary
                )
            
            console.print(table)
            console.print(f"\n[dim]Total: {len(policies)} policy/policies[/dim]")
        else:
            console.print("[yellow]No policies found[/yellow]")


@policy.command(name="get")
@click.option("--policy-id", required=True, help="Policy ID")
@click.option("--output", type=click.Choice(["table", "json"]), default="json", help="Output format")
def get_policy(policy_id, output):
    """Get a specific data governance policy by ID."""
    client = UnifiedCatalogClient()
    
    # Get all policies and filter (since GET by ID returns 404)
    all_policies = client.list_policies({})
    policies = all_policies.get("values", all_policies.get("value", []))
    
    # Find the requested policy
    policy = next((p for p in policies if p.get("id") == policy_id), None)
    
    if not policy:
        console.print(f"[red]ERROR:[/red] Policy with ID {policy_id} not found")
        return
    
    if output == "json":
        _format_json_output(policy)
    else:
        # Display policy in formatted view
        props = policy.get("properties", {})
        entity = props.get("entity", {})
        
        console.print(f"\n[bold cyan]Policy Details[/bold cyan]")
        console.print(f"[bold]ID:[/bold] {policy.get('id')}")
        console.print(f"[bold]Name:[/bold] {policy.get('name')}")
        console.print(f"[bold]Version:[/bold] {policy.get('version', 0)}")
        
        console.print(f"\n[bold cyan]Entity[/bold cyan]")
        console.print(f"[bold]Type:[/bold] {entity.get('type', 'N/A')}")
        console.print(f"[bold]Reference:[/bold] {entity.get('referenceName', 'N/A')}")
        console.print(f"[bold]Parent:[/bold] {props.get('parentEntityName', 'N/A')}")
        
        # Decision Rules
        decision_rules = props.get("decisionRules", [])
        if decision_rules:
            console.print(f"\n[bold cyan]Decision Rules ({len(decision_rules)})[/bold cyan]")
            for i, rule in enumerate(decision_rules, 1):
                console.print(f"\n  [bold]Rule {i}:[/bold] {rule.get('kind', 'N/A')}")
                console.print(f"  [bold]Effect:[/bold] {rule.get('effect', 'N/A')}")
                if "dnfCondition" in rule:
                    console.print(f"  [bold]Conditions:[/bold] {len(rule['dnfCondition'])} clause(s)")
        
        # Attribute Rules
        attribute_rules = props.get("attributeRules", [])
        if attribute_rules:
            console.print(f"\n[bold cyan]Attribute Rules ({len(attribute_rules)})[/bold cyan]")
            for i, rule in enumerate(attribute_rules, 1):
                console.print(f"\n  [bold]Rule {i}:[/bold] {rule.get('name', rule.get('id', 'N/A'))}")
                if "dnfCondition" in rule:
                    conditions = rule.get("dnfCondition", [])
                    console.print(f"  [bold]Conditions:[/bold] {len(conditions)} clause(s)")
                    for j, clause in enumerate(conditions[:3], 1):  # Show first 3
                        if clause:
                            attr = clause[0] if isinstance(clause, list) else clause
                            console.print(f"    {j}. {attr.get('attributeName', 'N/A')}")
                    if len(conditions) > 3:
                        console.print(f"    ... and {len(conditions) - 3} more")
        
        console.print()



@policy.command(name="create")
@click.option("--name", required=True, help="Policy name")
@click.option("--policy-type", required=True, help="Policy type (e.g., access, retention)")
@click.option("--description", default="", help="Policy description")
@click.option("--status", default="active", help="Policy status (active, draft)")
def create_policy(name, policy_type, description, status):
    """Create a new data governance policy."""
    client = UnifiedCatalogClient()
    args = {
        "--name": [name],
        "--policy-type": [policy_type],
        "--description": [description],
        "--status": [status]
    }
    response = client.create_policy(args)
    
    console.print(f"[green]SUCCESS:[/green] Policy created")
    _format_json_output(response)


@policy.command(name="update")
@click.option("--policy-id", required=True, help="Policy ID")
@click.option("--name", help="New policy name")
@click.option("--description", help="New policy description")
@click.option("--status", help="New policy status")
def update_policy(policy_id, name, description, status):
    """Update an existing data governance policy."""
    client = UnifiedCatalogClient()
    args = {"--policy-id": [policy_id]}
    
    if name:
        args["--name"] = [name]
    if description:
        args["--description"] = [description]
    if status:
        args["--status"] = [status]
    
    response = client.update_policy(args)
    
    console.print(f"[green]SUCCESS:[/green] Policy updated")
    _format_json_output(response)


@policy.command(name="delete")
@click.option("--policy-id", required=True, help="Policy ID")
@click.confirmation_option(prompt="Are you sure you want to delete this policy?")
def delete_policy(policy_id):
    """Delete a data governance policy."""
    client = UnifiedCatalogClient()
    args = {"--policy-id": [policy_id]}
    response = client.delete_policy(args)
    
    console.print(f"[green]SUCCESS:[/green] Policy '{policy_id}' deleted")


# ========================================
# CUSTOM METADATA (NEW)
# ========================================


@uc.group()
def metadata():
    """Manage custom metadata for assets."""
    pass


@metadata.command(name="list")
@click.option("--output", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.option("--fallback/--no-fallback", default=True, help="Fallback to Business Metadata if UC is empty")
def list_custom_metadata(output, fallback):
    """List all custom metadata definitions.
    
    Uses Atlas API to get Business Metadata definitions. 
    With fallback enabled, shows user-friendly table format.
    """
    client = UnifiedCatalogClient()
    response = client.list_custom_metadata({})
    
    # Check if UC API returned business metadata (Atlas returns businessMetadataDefs)
    has_uc_data = (response and "businessMetadataDefs" in response 
                   and response["businessMetadataDefs"])
    
    if output == "json":
        if has_uc_data:
            console.print_json(json.dumps(response))
        elif fallback:
            # Fallback message (though Atlas API should always return something)
            console.print("[dim]No business metadata found.[/dim]\n")
            console.print_json(json.dumps({"businessMetadataDefs": []}))
        else:
            console.print_json(json.dumps(response))
    else:
        # Table output
        if has_uc_data:
            biz_metadata = response.get('businessMetadataDefs', [])
            
            if biz_metadata:
                table = Table(title="[bold green]Business Metadata Attributes[/bold green]", show_header=True)
                table.add_column("Attribute Name", style="green", no_wrap=True)
                table.add_column("Group", style="cyan")
                table.add_column("Type", style="yellow")
                table.add_column("Scope", style="magenta", max_width=25)
                table.add_column("Description", style="white", max_width=30)
                
                total_attrs = 0
                for group in biz_metadata:
                    group_name = group.get('name', 'N/A')
                    attributes = group.get('attributeDefs', [])
                    
                    # Parse group-level scope
                    group_scope = "N/A"
                    options = group.get('options', {})
                    if 'dataGovernanceOptions' in options:
                        try:
                            dg_opts_str = options.get('dataGovernanceOptions', '{}')
                            dg_opts = json.loads(dg_opts_str) if isinstance(dg_opts_str, str) else dg_opts_str
                            applicable = dg_opts.get('applicableConstructs', [])
                            if applicable:
                                # Categorize scope
                                has_business_concept = any('businessConcept' in c or 'domain' in c for c in applicable)
                                has_dataset = any('dataset' in c.lower() for c in applicable)
                                
                                if has_business_concept and has_dataset:
                                    group_scope = "Universal (Concept + Dataset)"
                                elif has_business_concept:
                                    group_scope = "Business Concept"
                                elif has_dataset:
                                    group_scope = "Data Asset"
                                else:
                                    # Show first 2 constructs
                                    scope_parts = []
                                    for construct in applicable[:2]:
                                        if ':' in construct:
                                            scope_parts.append(construct.split(':')[0])
                                        else:
                                            scope_parts.append(construct)
                                    group_scope = ', '.join(scope_parts)
                        except:
                            pass
                    
                    for attr in attributes:
                        total_attrs += 1
                        attr_name = attr.get('name', 'N/A')
                        attr_type = attr.get('typeName', 'N/A')
                        
                        # Simplify enum types
                        if 'ATTRIBUTE_ENUM_' in attr_type:
                            attr_type = 'Enum'
                        
                        attr_desc = attr.get('description', '')
                        
                        # Check if attribute has custom scope
                        attr_scope = group_scope
                        attr_opts = attr.get('options', {})
                        
                        # Check dataGovernanceOptions first
                        if 'dataGovernanceOptions' in attr_opts:
                            try:
                                attr_dg_str = attr_opts.get('dataGovernanceOptions', '{}')
                                attr_dg = json.loads(attr_dg_str) if isinstance(attr_dg_str, str) else attr_dg_str
                                inherit = attr_dg.get('inheritApplicableConstructsFromGroup', True)
                                if not inherit:
                                    attr_applicable = attr_dg.get('applicableConstructs', [])
                                    if attr_applicable:
                                        # Categorize custom scope
                                        has_business_concept = any('businessConcept' in c or 'domain' in c for c in attr_applicable)
                                        has_dataset = any('dataset' in c.lower() for c in attr_applicable)
                                        
                                        if has_business_concept and has_dataset:
                                            attr_scope = "Universal"
                                        elif has_business_concept:
                                            attr_scope = "Business Concept"
                                        elif has_dataset:
                                            attr_scope = "Data Asset"
                                        else:
                                            attr_scope = f"Custom ({len(attr_applicable)})"
                            except:
                                pass
                        
                        # Fallback: Check applicableEntityTypes (older format)
                        if attr_scope == "N/A" and 'applicableEntityTypes' in attr_opts:
                            try:
                                entity_types_str = attr_opts.get('applicableEntityTypes', '[]')
                                # Parse if string, otherwise use as-is
                                if isinstance(entity_types_str, str):
                                    entity_types = json.loads(entity_types_str)
                                else:
                                    entity_types = entity_types_str
                                
                                if entity_types and isinstance(entity_types, list):
                                    # Check if entity types are data assets (tables, etc.)
                                    if any('table' in et.lower() or 'database' in et.lower() or 'file' in et.lower() 
                                           for et in entity_types):
                                        attr_scope = "Data Asset"
                                    else:
                                        attr_scope = f"Assets ({len(entity_types)} types)"
                            except Exception as e:
                                # Silently fail but could log for debugging
                                pass
                        
                        table.add_row(
                            attr_name,
                            group_name,
                            attr_type,
                            attr_scope,
                            attr_desc[:30] + "..." if len(attr_desc) > 30 else attr_desc
                        )
                
                console.print(table)
                console.print(f"\n[cyan]Total:[/cyan] {total_attrs} business metadata attribute(s) in {len(biz_metadata)} group(s)")
                console.print("\n[dim]Legend:[/dim]")
                console.print("  [magenta]Business Concept[/magenta] = Applies to Terms, Domains, Business Rules")
                console.print("  [magenta]Data Asset[/magenta] = Applies to Tables, Files, Databases")
                console.print("  [magenta]Universal[/magenta] = Applies to both Concepts and Assets")
            else:
                console.print("[yellow]No business metadata found[/yellow]")
        else:
            console.print("[yellow]No business metadata found[/yellow]")


@metadata.command(name="get")
@click.option("--asset-id", required=True, help="Asset GUID")
@click.option("--output", type=click.Choice(["table", "json"]), default="json", help="Output format")
def get_custom_metadata(asset_id, output):
    """Get custom metadata (business metadata) for a specific asset."""
    client = UnifiedCatalogClient()
    args = {"--asset-id": [asset_id]}
    response = client.get_custom_metadata(args)
    
    if output == "json":
        # Extract businessAttributes from entity response
        # Note: API returns "businessAttributes" not "businessMetadata"
        if response and "entity" in response:
            business_metadata = response["entity"].get("businessAttributes", {})
            _format_json_output(business_metadata)
        elif response and isinstance(response, dict):
            business_metadata = response.get("businessAttributes", {})
            _format_json_output(business_metadata)
        else:
            _format_json_output({})
    else:
        table = Table(title=f"[bold cyan]Business Metadata for Asset: {asset_id}[/bold cyan]")
        table.add_column("Group", style="cyan")
        table.add_column("Attribute", style="green")
        table.add_column("Value", style="white")
        
        if response and "entity" in response:
            business_metadata = response["entity"].get("businessAttributes", {})
            if business_metadata:
                for group_name, attributes in business_metadata.items():
                    if isinstance(attributes, dict):
                        for attr_name, attr_value in attributes.items():
                            table.add_row(group_name, attr_name, str(attr_value))
        elif response and isinstance(response, dict):
            business_metadata = response.get("businessAttributes", {})
            if business_metadata:
                for group_name, attributes in business_metadata.items():
                    if isinstance(attributes, dict):
                        for attr_name, attr_value in attributes.items():
                            table.add_row(group_name, attr_name, str(attr_value))
        
        console.print(table)


@metadata.command(name="add")
@click.option("--asset-id", required=True, help="Asset GUID")
@click.option("--group", required=True, help="Business metadata group name (e.g., 'Governance', 'Privacy')")
@click.option("--key", required=True, help="Attribute name")
@click.option("--value", required=True, help="Attribute value")
def add_custom_metadata(asset_id, group, key, value):
    """Add custom metadata (business metadata) to an asset.
    
    Example: pvw uc metadata add --asset-id <guid> --group Governance --key DataOwner --value "John Doe"
    """
    client = UnifiedCatalogClient()
    args = {
        "--asset-id": [asset_id],
        "--group": [group],
        "--key": [key],
        "--value": [value]
    }
    response = client.add_custom_metadata(args)
    
    console.print(f"[green]SUCCESS:[/green] Business metadata '{key}' added to group '{group}' on asset '{asset_id}'")
    if response:
        _format_json_output(response)


@metadata.command(name="update")
@click.option("--asset-id", required=True, help="Asset GUID")
@click.option("--group", required=True, help="Business metadata group name")
@click.option("--key", required=True, help="Attribute name to update")
@click.option("--value", required=True, help="New attribute value")
def update_custom_metadata(asset_id, group, key, value):
    """Update custom metadata (business metadata) for an asset.
    
    Example: pvw uc metadata update --asset-id <guid> --group Governance --key DataOwner --value "Jane Smith"
    """
    client = UnifiedCatalogClient()
    args = {
        "--asset-id": [asset_id],
        "--group": [group],
        "--key": [key],
        "--value": [value]
    }
    response = client.update_custom_metadata(args)
    
    console.print(f"[green]SUCCESS:[/green] Business metadata '{key}' updated in group '{group}' on asset '{asset_id}'")
    if response:
        _format_json_output(response)


@metadata.command(name="delete")
@click.option("--asset-id", required=True, help="Asset GUID")
@click.option("--group", required=True, help="Business metadata group name to delete")
@click.confirmation_option(prompt="Are you sure you want to delete this business metadata group?")
def delete_custom_metadata(asset_id, group):
    """Delete custom metadata (business metadata) from an asset.
    
    This removes the entire business metadata group from the asset.
    Example: pvw uc metadata delete --asset-id <guid> --group Governance
    """
    client = UnifiedCatalogClient()
    args = {
        "--asset-id": [asset_id],
        "--group": [group]
    }
    response = client.delete_custom_metadata(args)
    
    console.print(f"[green]SUCCESS:[/green] Business metadata group '{group}' deleted from asset '{asset_id}'")


# ========================================
# CUSTOM ATTRIBUTES (NEW)
# ========================================


@uc.group()
def attribute():
    """Manage custom attribute definitions."""
    pass


@attribute.command(name="list")
@click.option("--output", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.option("--debug", is_flag=True, help="Show raw response for troubleshooting")
def list_custom_attributes(output, debug):
    """List all custom attribute definitions.

    Note: If the tenant/region does not expose the datagovernance catalog attributes endpoint, this will return empty. Use Atlas business metadata via `pvw types readTypeDefs --type businessMetadata` to inspect definitions.
    """
    client = UnifiedCatalogClient()
    response = client.list_custom_attributes({})

    if debug:
        console.print_json(json.dumps(response))
        return

    if output == "json":
        console.print_json(json.dumps(response))
    else:
        if isinstance(response, dict) and response.get("value"):
            table = Table(title="[bold cyan]Custom Attribute Definitions[/bold cyan]", show_header=True)
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Data Type", style="yellow")
            table.add_column("Required", style="magenta")
            table.add_column("Description", style="white")
            
            for item in response["value"]:
                table.add_row(
                    item.get("id", "N/A"),
                    item.get("name", "N/A"),
                    item.get("dataType", "N/A"),
                    "Yes" if item.get("required") else "No",
                    item.get("description", "")[:50] + "..." if len(item.get("description", "")) > 50 else item.get("description", "")
                )
            console.print(table)
        else:
            console.print("[yellow]No custom attributes found (endpoint may not be enabled; try 'pvw types readTypeDefs --type businessMetadata').[/yellow]")


@attribute.command(name="get")
@click.option("--attribute-id", required=True, help="Attribute ID")
@click.option("--output", type=click.Choice(["table", "json"]), default="json", help="Output format")
def get_custom_attribute(attribute_id, output):
    """Get a specific custom attribute definition."""
    client = UnifiedCatalogClient()
    args = {"--attribute-id": [attribute_id]}
    response = client.get_custom_attribute(args)
    
    if output == "json":
        _format_json_output(response)
    else:
        table = Table(title=f"[bold cyan]Attribute: {response.get('name', 'N/A')}[/bold cyan]")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in response.items():
            table.add_row(key, str(value))
        console.print(table)


@attribute.command(name="create")
@click.option("--name", required=True, help="Attribute name")
@click.option("--data-type", required=True, help="Data type (string, number, boolean, date)")
@click.option("--description", default="", help="Attribute description")
@click.option("--required", is_flag=True, help="Is this attribute required?")
@click.option("--debug", is_flag=True, help="Show raw response for troubleshooting")
def create_custom_attribute(name, data_type, description, required, debug):
    """Create a new custom attribute definition.

    Note: This uses the datagovernance catalog attributes endpoint. Some tenants/regions do not expose it and will return HTTP 405. In that case use Atlas business metadata instead via `pvw types putTypeDefs` with `businessMetadataDefs`.
    """
    client = UnifiedCatalogClient()
    args = {
        "--name": [name],
        "--data-type": [data_type],
        "--description": [description],
        "--required": ["true" if required else "false"],
        "--debug": [True] if debug else []
    }
    response = client.create_custom_attribute(args)

    if debug:
        console.print_json(json.dumps(response))

    if isinstance(response, dict) and (response.get("status") == "error" or response.get("status_code", 200) >= 400):
        console.print("[red]FAILED:[/red] Custom attribute not created")
        if response.get("status_code") == 405:
            console.print("[yellow]This endpoint is not enabled for this tenant/region. Use Atlas business metadata via 'pvw types putTypeDefs' with businessMetadataDefs instead.[/yellow]")
        if not debug:
            _format_json_output(response)
        return

    console.print(f"[green]SUCCESS:[/green] Custom attribute created")
    _format_json_output(response)


@attribute.command(name="update")
@click.option("--attribute-id", required=True, help="Attribute ID")
@click.option("--name", help="New attribute name")
@click.option("--description", help="New attribute description")
@click.option("--required", type=bool, help="Is this attribute required? (true/false)")
def update_custom_attribute(attribute_id, name, description, required):
    """Update an existing custom attribute definition."""
    client = UnifiedCatalogClient()
    args = {"--attribute-id": [attribute_id]}
    
    if name:
        args["--name"] = [name]
    if description:
        args["--description"] = [description]
    if required is not None:
        args["--required"] = ["true" if required else "false"]
    
    response = client.update_custom_attribute(args)
    
    console.print(f"[green]SUCCESS:[/green] Custom attribute updated")
    _format_json_output(response)


@attribute.command(name="delete")
@click.option("--attribute-id", required=True, help="Attribute ID")
@click.confirmation_option(prompt="Are you sure you want to delete this attribute?")
def delete_custom_attribute(attribute_id):
    """Delete a custom attribute definition."""
    client = UnifiedCatalogClient()
    args = {"--attribute-id": [attribute_id]}
    response = client.delete_custom_attribute(args)
    
    console.print(f"[green]SUCCESS:[/green] Custom attribute '{attribute_id}' deleted")


# ========================================
# REQUESTS (Coming Soon)
# ========================================


@uc.group()
def request():
    """Manage access requests (coming soon)."""
    pass


@request.command(name="list")
def list_requests():
    """List access requests (coming soon)."""
    console.print("[yellow][COMING SOON] Access Requests are coming soon[/yellow]")
    console.print("This feature is under development for data access workflows")
