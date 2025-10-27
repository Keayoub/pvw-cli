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
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich.syntax import Syntax
from purviewcli.client._unified_catalog import UnifiedCatalogClient

console = Console()


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
        console.print(f"  • Linked domains: [green]{linked_count}[/green]")
        console.print(f"  • Unlinked domains: [yellow]{unlinked_count}[/yellow]")
        
        if unlinked_count > 0:
            console.print(f"\n[dim]💡 Tip: Run 'pvw uc glossary create-for-domains' to create glossaries for unlinked domains[/dim]")
        
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
def list_terms(domain_id, output):
    """List all Unified Catalog terms in a governance domain.
    
    Output formats:
    - table: Formatted table output with Rich (default)
    - json: Plain JSON for scripting (use with PowerShell ConvertFrom-Json)
    - jsonc: Colored JSON with syntax highlighting for viewing
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

        for term in all_terms:
            description = term.get("description", "")
            # Strip HTML tags from description
            import re
            description = re.sub(r'<[^>]+>', '', description)
            # Truncate long descriptions
            if len(description) > 50:
                description = description[:50] + "..."
            
            table.add_row(
                term.get("id", "N/A"),
                term.get("name", "N/A"),
                term.get("status", "N/A"),
                description.strip(),
            )

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
def update(term_id, name, description, domain_id, parent_id, status, acronym, owner_id, resource_name, resource_url, add_acronym, add_owner_id):
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


@term.command(name="import-csv")
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="Path to CSV file with terms")
@click.option("--domain-id", required=True, help="Governance domain ID for all terms")
@click.option("--dry-run", is_flag=True, help="Preview terms without creating them")
def import_terms_from_csv(csv_file, domain_id, dry_run):
    """Bulk import glossary terms from a CSV file.
    
    CSV Format:
    name,description,status,acronyms,owner_ids,resource_name,resource_url
    
    - name: Required term name
    - description: Optional description
    - status: Draft, Published, or Archived (default: Draft)
    - acronyms: Comma-separated list (e.g., "API,REST")
    - owner_ids: Comma-separated list of Entra Object IDs
    - resource_name: Name of related resource
    - resource_url: URL of related resource
    
    Multiple resources can be specified by separating with semicolons.
    """
    try:
        client = UnifiedCatalogClient()
        
        # Read and parse CSV
        terms = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                term = {
                    "name": row.get("name", "").strip(),
                    "description": row.get("description", "").strip(),
                    "status": row.get("status", "Draft").strip(),
                    "domain_id": domain_id,
                    "acronyms": [],
                    "owner_ids": [],
                    "resources": []
                }
                
                # Parse acronyms
                if row.get("acronyms"):
                    term["acronyms"] = [a.strip() for a in row["acronyms"].split(",") if a.strip()]
                
                # Parse owner IDs
                if row.get("owner_ids"):
                    term["owner_ids"] = [o.strip() for o in row["owner_ids"].split(",") if o.strip()]
                
                # Parse resources
                resource_names = row.get("resource_name", "").strip()
                resource_urls = row.get("resource_url", "").strip()
                
                if resource_names and resource_urls:
                    names = [n.strip() for n in resource_names.split(";") if n.strip()]
                    urls = [u.strip() for u in resource_urls.split(";") if u.strip()]
                    term["resources"] = [{"name": n, "url": u} for n, u in zip(names, urls)]
                
                if term["name"]:  # Only add if name is present
                    terms.append(term)
        
        if not terms:
            console.print("[yellow]No valid terms found in CSV file.[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(terms)} term(s) in CSV file[/cyan]")
        
        if dry_run:
            console.print("\n[yellow]DRY RUN - Preview of terms to be created:[/yellow]\n")
            table = Table(title="Terms to Import")
            table.add_column("#", style="dim", width=4)
            table.add_column("Name", style="cyan")
            table.add_column("Status", style="yellow")
            table.add_column("Acronyms", style="magenta")
            table.add_column("Owners", style="green")
            
            for i, term in enumerate(terms, 1):
                acronyms = ", ".join(term.get("acronyms", []))
                owners = ", ".join(term.get("owner_ids", []))
                table.add_row(
                    str(i),
                    term["name"],
                    term["status"],
                    acronyms or "-",
                    owners or "-"
                )
            
            console.print(table)
            console.print(f"\n[dim]Domain ID: {domain_id}[/dim]")
            return
        
        # Import terms (one by one using single POST)
        success_count = 0
        failed_count = 0
        failed_terms = []
        
        with console.status("[bold green]Importing terms...") as status:
            for i, term in enumerate(terms, 1):
                status.update(f"[bold green]Creating term {i}/{len(terms)}: {term['name']}")
                
                try:
                    # Create individual term
                    args = {
                        "--name": [term["name"]],
                        "--description": [term.get("description", "")],
                        "--governance-domain-id": [term["domain_id"]],
                        "--status": [term.get("status", "Draft")],
                    }
                    
                    if term.get("acronyms"):
                        args["--acronym"] = term["acronyms"]
                    
                    if term.get("owner_ids"):
                        args["--owner-id"] = term["owner_ids"]
                    
                    if term.get("resources"):
                        args["--resource-name"] = [r["name"] for r in term["resources"]]
                        args["--resource-url"] = [r["url"] for r in term["resources"]]
                    
                    result = client.create_term(args)
                    
                    # Check if result contains an ID (indicates successful creation)
                    if result and isinstance(result, dict) and result.get("id"):
                        success_count += 1
                        term_id = result.get("id")
                        console.print(f"[green]Created: {term['name']} (ID: {term_id})[/green]")
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
        
        # Summary
        console.print("\n" + "="*60)
        console.print(f"[cyan]Import Summary:[/cyan]")
        console.print(f"  Total terms: {len(terms)}")
        console.print(f"  [green]Successfully created: {success_count}[/green]")
        console.print(f"  [red]Failed: {failed_count}[/red]")
        
        if failed_terms:
            console.print("\n[red]Failed Terms:[/red]")
            for ft in failed_terms:
                console.print(f"  • {ft['name']}: {ft['error']}")
        
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
                console.print(f"  • {ft['name']}: {ft['error']}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="update-csv")
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="Path to CSV file with term updates")
@click.option("--dry-run", is_flag=True, help="Preview updates without applying them")
def update_terms_from_csv(csv_file, dry_run):
    """Bulk update glossary terms from a CSV file.
    
    CSV Format:
    term_id,name,description,status,parent_id,acronyms,owner_ids,add_acronyms,add_owner_ids
    
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
    
    Example CSV:
    term_id,name,description,status,parent_id,add_acronyms,add_owner_ids
    abc-123,,Updated description,Published,parent-term-guid,API;REST,user1@company.com
    def-456,New Name,,,parent-term-guid,SQL,
    """
    import csv
    
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
                console.print(f"  • {ft['name']}: {ft['error']}")
        
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
                console.print(f"  • {ft['name']}: {ft['error']}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")



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
        if "value" in response and response["value"]:
            table = Table(title="[bold cyan]Data Governance Policies[/bold cyan]", show_header=True)
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Status", style="magenta")
            table.add_column("Description", style="white")
            
            for item in response["value"]:
                table.add_row(
                    item.get("id", "N/A"),
                    item.get("name", "N/A"),
                    item.get("policyType", "N/A"),
                    item.get("status", "N/A"),
                    item.get("description", "")[:50] + "..." if len(item.get("description", "")) > 50 else item.get("description", "")
                )
            console.print(table)
        else:
            console.print("[yellow]No policies found[/yellow]")


@policy.command(name="get")
@click.option("--policy-id", required=True, help="Policy ID")
@click.option("--output", type=click.Choice(["table", "json"]), default="json", help="Output format")
def get_policy(policy_id, output):
    """Get a specific data governance policy."""
    client = UnifiedCatalogClient()
    args = {"--policy-id": [policy_id]}
    response = client.get_policy(args)
    
    if output == "json":
        _format_json_output(response)
    else:
        table = Table(title=f"[bold cyan]Policy: {response.get('name', 'N/A')}[/bold cyan]")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")
        
        for key, value in response.items():
            table.add_row(key, str(value))
        console.print(table)


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
    
    First tries UC Custom Metadata API. If empty and fallback is enabled,
    automatically shows Business Metadata from Data Map API instead.
    """
    client = UnifiedCatalogClient()
    response = client.list_custom_metadata({})
    
    # Check if UC API returned data
    has_uc_data = response and "value" in response and response["value"]
    
    if output == "json":
        if has_uc_data:
            console.print_json(json.dumps(response))
        elif fallback:
            # Fallback to Business Metadata
            console.print("[dim]UC Custom Metadata is empty. Showing Business Metadata from Data Map API...[/dim]\n")
            from purviewcli.client._types import Types
            types_client = Types()
            types_result = types_client.typesRead({})
            
            if types_result:
                biz_metadata = types_result.get('businessMetadataDefs', [])
                
                # Format as attribute list
                attributes_list = []
                for group in biz_metadata:
                    group_name = group.get('name', 'N/A')
                    group_guid = group.get('guid', 'N/A')
                    
                    for attr in group.get('attributeDefs', []):
                        attributes_list.append({
                            'source': 'DataMap.BusinessMetadata',
                            'attributeName': attr.get('name'),
                            'group': group_name,
                            'groupGuid': group_guid,
                            'type': attr.get('typeName'),
                            'description': attr.get('description', ''),
                            'isOptional': attr.get('isOptional', True),
                            'isIndexable': attr.get('isIndexable', False)
                        })
                
                console.print_json(json.dumps(attributes_list))
            else:
                console.print_json(json.dumps({"value": [], "message": "No UC or Business Metadata found"}))
        else:
            console.print_json(json.dumps(response))
    else:
        # Table output
        if has_uc_data:
            table = Table(title="[bold cyan]UC Custom Metadata Definitions[/bold cyan]", show_header=True)
            table.add_column("Key", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Description", style="white")
            
            for item in response["value"]:
                table.add_row(
                    item.get("key", "N/A"),
                    item.get("type", "N/A"),
                    item.get("description", "")[:60] + "..." if len(item.get("description", "")) > 60 else item.get("description", "")
                )
            console.print(table)
        elif fallback:
            # Fallback to Business Metadata
            console.print("[yellow]INFO:[/yellow] UC Custom Metadata is empty.")
            console.print("[dim]Falling back to Business Metadata (Data Map API)...[/dim]\n")
            
            from purviewcli.client._types import Types
            types_client = Types()
            types_result = types_client.typesRead({})
            
            if types_result:
                biz_metadata = types_result.get('businessMetadataDefs', [])
                
                if biz_metadata:
                    table = Table(title="[bold green]Business Metadata Attributes (Data Map)[/bold green]", show_header=True)
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
                    console.print("\n[dim]Tip: Use 'pvw types list-business-attributes' for detailed business metadata view[/dim]")
                    console.print("[dim]Tip: Use 'pvw uc metadata list --no-fallback' to see only UC metadata[/dim]")
                else:
                    console.print("[yellow]No business metadata found either[/yellow]")
            else:
                console.print("[red]ERROR:[/red] Failed to retrieve business metadata")
        else:
            console.print("[yellow]No custom metadata found[/yellow]")
            console.print("[dim]Tip: Use --fallback to also check Business Metadata from Data Map API[/dim]")


@metadata.command(name="get")
@click.option("--asset-id", required=True, help="Asset ID")
@click.option("--output", type=click.Choice(["table", "json"]), default="json", help="Output format")
def get_custom_metadata(asset_id, output):
    """Get custom metadata for a specific asset."""
    client = UnifiedCatalogClient()
    args = {"--asset-id": [asset_id]}
    response = client.get_custom_metadata(args)
    
    if output == "json":
        _format_json_output(response)
    else:
        table = Table(title=f"[bold cyan]Custom Metadata for Asset: {asset_id}[/bold cyan]")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Type", style="yellow")
        
        if "metadata" in response:
            for key, value in response["metadata"].items():
                table.add_row(key, str(value.get("value", "N/A")), value.get("type", "N/A"))
        console.print(table)


@metadata.command(name="add")
@click.option("--asset-id", required=True, help="Asset ID")
@click.option("--key", required=True, help="Metadata key")
@click.option("--value", required=True, help="Metadata value")
@click.option("--type", default="string", help="Metadata type (string, number, boolean)")
def add_custom_metadata(asset_id, key, value, type):
    """Add custom metadata to an asset."""
    client = UnifiedCatalogClient()
    args = {
        "--asset-id": [asset_id],
        "--key": [key],
        "--value": [value],
        "--type": [type]
    }
    response = client.add_custom_metadata(args)
    
    console.print(f"[green]SUCCESS:[/green] Custom metadata added to asset '{asset_id}'")
    _format_json_output(response)


@metadata.command(name="update")
@click.option("--asset-id", required=True, help="Asset ID")
@click.option("--key", required=True, help="Metadata key to update")
@click.option("--value", required=True, help="New metadata value")
def update_custom_metadata(asset_id, key, value):
    """Update custom metadata for an asset."""
    client = UnifiedCatalogClient()
    args = {
        "--asset-id": [asset_id],
        "--key": [key],
        "--value": [value]
    }
    response = client.update_custom_metadata(args)
    
    console.print(f"[green]SUCCESS:[/green] Custom metadata updated for asset '{asset_id}'")
    _format_json_output(response)


@metadata.command(name="delete")
@click.option("--asset-id", required=True, help="Asset ID")
@click.option("--key", required=True, help="Metadata key to delete")
@click.confirmation_option(prompt="Are you sure you want to delete this metadata?")
def delete_custom_metadata(asset_id, key):
    """Delete custom metadata from an asset."""
    client = UnifiedCatalogClient()
    args = {
        "--asset-id": [asset_id],
        "--key": [key]
    }
    response = client.delete_custom_metadata(args)
    
    console.print(f"[green]SUCCESS:[/green] Custom metadata '{key}' deleted from asset '{asset_id}'")


# ========================================
# CUSTOM ATTRIBUTES (NEW)
# ========================================


@uc.group()
def attribute():
    """Manage custom attribute definitions."""
    pass


@attribute.command(name="list")
@click.option("--output", type=click.Choice(["table", "json"]), default="table", help="Output format")
def list_custom_attributes(output):
    """List all custom attribute definitions."""
    client = UnifiedCatalogClient()
    response = client.list_custom_attributes({})
    
    if output == "json":
        console.print_json(json.dumps(response))
    else:
        if "value" in response and response["value"]:
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
            console.print("[yellow]No custom attributes found[/yellow]")


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
def create_custom_attribute(name, data_type, description, required):
    """Create a new custom attribute definition."""
    client = UnifiedCatalogClient()
    args = {
        "--name": [name],
        "--data-type": [data_type],
        "--description": [description],
        "--required": ["true" if required else "false"]
    }
    response = client.create_custom_attribute(args)
    
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
    console.print("[yellow]🚧 Access Requests are coming soon[/yellow]")
    console.print("This feature is under development for data access workflows")
