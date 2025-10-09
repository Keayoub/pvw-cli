"""
Microsoft Purview Unified Catalog CLI Commands
Replaces data_product functionality with comprehensive Unified Catalog operations
"""

import click
import csv
import json
import tempfile
import os
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

        console.print(f"[green]✅ SUCCESS:[/green] Created governance domain '{name}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@domain.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
def list_domains(output_json):
    """List all governance domains."""
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

        # Output in JSON format if requested
        if output_json:
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

        console.print(f"[green]✅ SUCCESS:[/green] Created data product '{name}'")
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

        console.print(f"[green]✅ SUCCESS:[/green] Updated data product '{product_id}'")
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
            console.print(f"[green]✅ SUCCESS:[/green] Deleted data product '{product_id}'")
        elif isinstance(result, dict) and "error" in result:
            console.print(f"[red]ERROR:[/red] {result.get('error', 'Unknown error')}")
        else:
            console.print(f"[green]✅ SUCCESS:[/green] Deleted data product '{product_id}'")
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
        console.print(f"[green]✅ SUCCESS:[/green] Created glossary '{name}'")
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
                    console.print(f"[green]✅ Created:[/green] {glossary_name} (GUID: {guid})")
                    created_count += 1
                else:
                    console.print(f"[yellow]⚠  Created {glossary_name} but no GUID returned[/yellow]")
                    
            except Exception as e:
                console.print(f"[red]❌ Failed to create {glossary_name}:[/red] {str(e)}")
        
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
                    "[green]✅ Linked[/green]"
                )
                linked_count += 1
            else:
                table.add_row(
                    domain_display,
                    domain_id[:8] + "...",
                    "[dim]No glossary[/dim]",
                    "[dim]N/A[/dim]",
                    "[yellow]⚠ Not Linked[/yellow]"
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
def create(name, description, domain_id, status, acronym, owner_id, resource_name, resource_url):
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

        console.print(f"[green]✅ SUCCESS:[/green] Created glossary term '{name}'")
        console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="list")
@click.option("--domain-id", required=True, help="Governance domain ID to list terms from")
@click.option("--json", "output_json", is_flag=True, help="Output results in JSON format")
def list_terms(domain_id, output_json):
    """List all Unified Catalog terms in a governance domain."""
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

        # Output in JSON format if requested
        if output_json:
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
        
        console.print(f"[green]✅ SUCCESS:[/green] Deleted term with ID: {term_id}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command()
@click.option("--term-id", required=True, help="ID of the glossary term to update")
@click.option("--name", required=False, help="Name of the glossary term")
@click.option("--description", required=False, help="Rich text description of the term")
@click.option("--domain-id", required=False, help="Governance domain ID")
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
def update(term_id, name, description, domain_id, status, acronym, owner_id, resource_name, resource_url, add_acronym, add_owner_id):
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

        console.print(f"[green]✅ SUCCESS:[/green] Updated glossary term '{term_id}'")
        console.print(json.dumps(result, indent=2))

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

        console.print(f"[green]✅ SUCCESS:[/green] Created objective")
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

        console.print(f"[green]✅ SUCCESS:[/green] Created critical data element '{name}'")
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
# HEALTH MANAGEMENT - IMPLEMENTED! ✅
# ========================================

# Import and register health commands from dedicated module
from purviewcli.cli.health import health as health_commands
uc.add_command(health_commands, name="health")


# ========================================
# CUSTOM ATTRIBUTES (Coming Soon)
# ========================================


@uc.group()
def attribute():
    """Manage custom attributes (coming soon)."""
    pass


@attribute.command(name="list")
def list_attributes():
    """List custom attributes (coming soon)."""
    console.print("[yellow]🚧 Custom Attributes are coming soon[/yellow]")
    console.print("This feature is under development in Microsoft Purview")


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
