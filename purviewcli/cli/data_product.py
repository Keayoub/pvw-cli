import click
import csv
import json
import tempfile
import os
from rich.console import Console
from purviewcli.client._unified_catalog import UnifiedCatalogDataProduct

console = Console()

@click.group()
def data_product():
    """Manage data products in Microsoft Purview using Unified Catalog API."""
    pass

@data_product.command()
@click.option('--name', required=True, help="Name of the data product")
@click.option('--description', required=False, help="Description of the data product")
@click.option('--domain-guid', required=False, help="GUID of the domain to associate with")
def create(name, description, domain_guid):
    """Create a new data product using Unified Catalog API."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.create_data_product(
            name=name,
            description=description,
            domain_guid=domain_guid
        )
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(f"[green]SUCCESS:[/green] Created data product '{name}'")
        console.print(json.dumps(result, indent=2))
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--data-product-id', required=True, help="ID of the data product")
def show(data_product_id):
    """Show details of a data product using Unified Catalog API."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.get_data_product(data_product_id)
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--data-product-id', required=True, help="ID of the data product")
@click.option('--name', required=False, help="New name for the data product")
@click.option('--description', required=False, help="New description for the data product")
def update(data_product_id, name, description):
    """Update a data product using Unified Catalog API."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        updates = {}
        if name:
            updates['name'] = name
        if description:
            updates['description'] = description
        
        if not updates:
            console.print("[yellow]WARNING:[/yellow] No updates specified")
            return
        
        result = data_product_client.update_data_product(data_product_id, updates)
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(f"[green]SUCCESS:[/green] Updated data product '{data_product_id}'")
        console.print(json.dumps(result, indent=2))
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--data-product-id', required=True, help="ID of the data product")
def delete(data_product_id):
    """Delete a data product using Unified Catalog API."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.delete_data_product(data_product_id)
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(f"[green]SUCCESS:[/green] Deleted data product '{data_product_id}'")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--limit', default=50, help="Maximum number of data products to list")
@click.option('--skip', default=0, help="Number of data products to skip")
@click.option('--domain-id', required=False, help="Filter by governance domain ID")
def list(limit, skip, domain_id):
    """List data products using Unified Catalog API."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.list_data_products(
            limit=limit,
            offset=skip,
            domain_id=domain_id
        )
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--data-product-id', required=True, help="ID of the data product")
def publish(data_product_id):
    """Publish a data product using Unified Catalog API."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.update_data_product(data_product_id, {"status": "Published"})
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(f"[green]SUCCESS:[/green] Published data product '{data_product_id}'")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--data-product-id', required=True, help="ID of the data product")
def unpublish(data_product_id):
    """Unpublish a data product using Unified Catalog API."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.update_data_product(data_product_id, {"status": "Draft"})
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(f"[green]SUCCESS:[/green] Unpublished data product '{data_product_id}'")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

# === BUSINESS DOMAIN COMMANDS ===
# Business domains are required for data product creation

@data_product.command()
def list_domains():
    """List all business domains."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.businessDomainList({})
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--name', required=True, help="Name of the business domain")
@click.option('--description', required=False, help="Description of the business domain")
@click.option('--type', default="DataDomain", help="Type of the business domain (DataDomain, LineOfBusiness, etc.)")
def create_domain(name, description, type):
    """Create a new business domain."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        args = {
            "--name": name,
            "--description": description or "",
            "--type": type,
            "--status": "Draft"
        }
        result = data_product_client.businessDomainCreate(args)
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(f"[green]SUCCESS:[/green] Created business domain '{name}'")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--domain-id', required=True, help="ID of the business domain")
def show_domain(domain_id):
    """Show details of a business domain."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.businessDomainRead({"--domainId": domain_id})
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

# === GLOSSARY TERM COMMANDS ===

@data_product.command()
@click.option('--domain-id', required=False, help="Filter by governance domain ID")
def list_terms(domain_id):
    """List glossary terms."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        args = {}
        if domain_id:
            args["--governanceDomain"] = domain_id
        result = data_product_client.glossaryTermsList(args)
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--name', required=True, help="Name of the glossary term")
@click.option('--description', required=False, help="Description of the glossary term")
@click.option('--domain-id', required=True, help="ID of the governance domain")
def create_term(name, description, domain_id):
    """Create a new glossary term."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.create_glossary_term(
            name=name,
            description=description or "",
            domain_id=domain_id
        )
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(f"[green]SUCCESS:[/green] Created glossary term '{name}'")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@data_product.command()
@click.option('--data-product-id', required=True, help="ID of the data product")
@click.option('--term-id', required=True, help="ID of the glossary term")
def link_term(data_product_id, term_id):
    """Link a glossary term to a data product."""
    try:
        data_product_client = UnifiedCatalogDataProduct()
        result = data_product_client.link_term_to_data_product(data_product_id, term_id)
        
        if result.get("status") == "error":
            console.print(f"[red]ERROR:[/red] {result.get('message', 'Unknown error')}")
            return
            
        console.print(f"[green]SUCCESS:[/green] Linked term '{term_id}' to data product '{data_product_id}'")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
