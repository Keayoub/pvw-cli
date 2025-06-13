import click
import csv
import json
from rich.console import Console
from purviewcli.client._data_product import DataProduct

console = Console()

@click.group()
def data_product():
    """Manage data products in Microsoft Purview."""
    pass

@data_product.command(name="import")
@click.option('--csv-file', required=True, type=click.Path(exists=True), help="CSV file with data product definitions")
@click.option('--dry-run', is_flag=True, help="Preview data products to be created without making changes")
def import_data_products(csv_file, dry_run):
    """Import data products from a CSV file."""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            products = list(reader)
        if dry_run:
            console.print(f"[yellow]Dry run: {len(products)} data products would be imported.[/yellow]")
            for p in products[:5]:
                console.print(json.dumps(p, indent=2))
            if len(products) > 5:
                console.print(f"...and {len(products)-5} more.")
            return
        data_product_client = DataProduct()
        results = data_product_client.import_from_csv(products)
        for qualified_name, result in results:
            console.print(f"[green]✓ Imported:[/green] {qualified_name}")
    except Exception as e:
        console.print(f"[red]✗ Error importing data products: {str(e)}[/red]")

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
@click.option('--name', required=False, help="Name of the data product")
@click.option('--description', required=False, help="Description of the data product")
def create(qualified_name, name, description):
    """Create a new data product."""
    data_product_client = DataProduct()
    result = data_product_client.create(qualified_name, name, description)
    console.print(f"[green]✓ Created:[/green] {qualified_name}")
    console.print(json.dumps(result, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
def show(qualified_name):
    """Show details of a data product."""
    data_product_client = DataProduct()
    result = data_product_client.show(qualified_name)
    console.print(json.dumps(result, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
def delete(qualified_name):
    """Delete a data product."""
    data_product_client = DataProduct()
    result = data_product_client.delete(qualified_name)
    console.print(f"[green]✓ Deleted:[/green] {qualified_name}")
    console.print(json.dumps(result, indent=2))

@data_product.command()
def list():
    """List all data products."""
    data_product_client = DataProduct()
    results = data_product_client.list()
    console.print(json.dumps(results, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
@click.option('--classification', required=True, help="Classification to add")
def add_classification(qualified_name, classification):
    """Add a classification to a data product."""
    data_product_client = DataProduct()
    result = data_product_client.add_classification(qualified_name, classification)
    console.print(f"[green]✓ Classification added:[/green] {classification} to {qualified_name}")
    console.print(json.dumps(result, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
@click.option('--classification', required=True, help="Classification to remove")
def remove_classification(qualified_name, classification):
    """Remove a classification from a data product."""
    data_product_client = DataProduct()
    result = data_product_client.remove_classification(qualified_name, classification)
    console.print(f"[green]✓ Classification removed:[/green] {classification} from {qualified_name}")
    console.print(json.dumps(result, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
@click.option('--label', required=True, help="Label to add")
def add_label(qualified_name, label):
    """Add a label to a data product."""
    data_product_client = DataProduct()
    result = data_product_client.add_label(qualified_name, label)
    console.print(f"[green]✓ Label added:[/green] {label} to {qualified_name}")
    console.print(json.dumps(result, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
@click.option('--label', required=True, help="Label to remove")
def remove_label(qualified_name, label):
    """Remove a label from a data product."""
    data_product_client = DataProduct()
    result = data_product_client.remove_label(qualified_name, label)
    console.print(f"[green]✓ Label removed:[/green] {label} from {qualified_name}")
    console.print(json.dumps(result, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
@click.option('--term', required=True, help="Glossary term to link")
def link_glossary(qualified_name, term):
    """Link a glossary term to a data product."""
    data_product_client = DataProduct()
    result = data_product_client.link_glossary(qualified_name, term)
    console.print(f"[green]✓ Glossary term linked:[/green] {term} to {qualified_name}")
    console.print(json.dumps(result, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
def show_lineage(qualified_name):
    """Show lineage for a data product."""
    data_product_client = DataProduct()
    result = data_product_client.show_lineage(qualified_name)
    console.print(json.dumps(result, indent=2))

@data_product.command()
@click.option('--qualified-name', required=True, help="Qualified name of the data product")
@click.option('--status', required=True, help="Status to set (e.g., active, deprecated)")
def set_status(qualified_name, status):
    """Set the status of a data product."""
    data_product_client = DataProduct()
    result = data_product_client.set_status(qualified_name, status)
    console.print(f"[green]✓ Status set:[/green] {status} for {qualified_name}")
    console.print(json.dumps(result, indent=2))
