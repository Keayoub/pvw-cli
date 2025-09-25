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
    type=click.Choice(["FunctionalUnit", "BusinessUnit", "Department"]),
    help="Type of governance domain",
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
def create(name, description, type, owner_id, status):
    """Create a new governance domain."""
    try:
        client = UnifiedCatalogClient()

        # Build args dictionary in Purview CLI format
        args = {
            "--name": [name],
            "--description": [description],
            "--type": [type],
            "--status": [status],
        }

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
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Domain ID", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Description", style="white")

        for product in products:
            table.add_row(
                product.get("id", "N/A"),
                product.get("name", "N/A"),
                product.get("domainId", "N/A"),
                product.get("status", "N/A"),
                (
                    (product.get("description", "")[:50] + "...")
                    if len(product.get("description", "")) > 50
                    else product.get("description", "")
                ),
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
@click.option("--resource-name", required=False, help="Resource name for additional reading")
@click.option("--resource-url", required=False, help="Resource URL for additional reading")
def create(name, description, domain_id, status, acronym, owner_id, resource_name, resource_url):
    """Create a new glossary term."""
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
            args["--acronyms"] = list(acronym)
        if owner_id:
            args["--owner-id"] = list(owner_id)
        if resource_name and resource_url:
            args["--resource-name"] = [resource_name]
            args["--resource-url"] = [resource_url]

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
    """List all glossary terms in a governance domain."""
    try:
        client = UnifiedCatalogClient()
        args = {"--governance-domain-id": [domain_id]}
        result = client.get_terms(args)

        if not result:
            console.print("[yellow]No glossary terms found.[/yellow]")
            return

        # The API returns glossaries with terms nested inside
        # Extract all terms from all glossaries
        all_terms = []

        if isinstance(result, (list, tuple)):
            glossaries = result
        elif isinstance(result, dict):
            glossaries = result.get("value", [])
        else:
            glossaries = []

        # Extract terms from glossaries
        for glossary in glossaries:
            if isinstance(glossary, dict) and "terms" in glossary:
                for term in glossary["terms"]:
                    all_terms.append(
                        {
                            "id": term.get("termGuid"),
                            "name": term.get("displayText"),
                            "glossary": glossary.get("name"),
                            "glossary_id": glossary.get("guid"),
                        }
                    )

        if not all_terms:
            console.print("[yellow]No glossary terms found.[/yellow]")
            return

        # Output in JSON format if requested
        if output_json:
            _format_json_output(all_terms)
            return

        table = Table(title="Glossary Terms")
        table.add_column("Term ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Glossary", style="yellow")
        table.add_column("Glossary ID", style="blue")

        for term in all_terms:
            table.add_row(
                term.get("id", "N/A"),
                term.get("name", "N/A"),
                term.get("glossary", "N/A"),
                term.get("glossary_id", "N/A"),
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command()
@click.option("--term-id", required=True, help="ID of the glossary term")
def show(term_id):
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
# HEALTH MANAGEMENT (Preview)
# ========================================


@uc.group()
def health():
    """Manage health controls and actions (preview)."""
    pass


@health.command(name="controls")
def list_controls():
    """List health controls (preview - not yet implemented)."""
    console.print("[yellow]🚧 Health Controls are not yet implemented in the API[/yellow]")
    console.print("This feature is coming soon to Microsoft Purview Unified Catalog")


@health.command(name="actions")
def list_actions():
    """List health actions (preview - not yet implemented)."""
    console.print("[yellow]🚧 Health Actions are not yet implemented in the API[/yellow]")
    console.print("This feature is coming soon to Microsoft Purview Unified Catalog")


@health.command(name="quality")
def data_quality():
    """Data quality management (not yet supported by API)."""
    console.print("[yellow]🚧 Data Quality management is not yet supported by the API[/yellow]")
    console.print("This feature requires complex API interactions not yet available")


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
