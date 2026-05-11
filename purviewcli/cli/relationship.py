"""
usage: 
    pvw relationship create --payloadFile=<val>
    pvw relationship delete --guid=<val>
    pvw relationship put --payloadFile=<val>
    pvw relationship read --guid=<val> [--extendedInfo]
    pvw relationship bulk-create-csv --csv-file=<val> [--output-json=<val>]

options:
    --purviewName=<val>           [string]  Microsoft Purview account name.
    --extendedInfo                [boolean] Limits whether includes extended information [default: false].
    --guid=<val>                  [string]  The globally unique identifier of the relationship.
    --payloadFile=<val>           [string]  File path to a valid JSON document.
    --csv-file=<val>              [string]  File path to a CSV file for bulk creation.
    --output-json=<val>           [string]  Optional: Output JSON file to save generated relationships.

"""
import click
import json
import csv
from pathlib import Path
from purviewcli.client._relationship import Relationship
from rich.console import Console

console = Console()

@click.group()
def relationship():
    """
    Manage entity relationships in Microsoft Purview.
    """
    pass

@relationship.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def create(payload_file):
    """Create a new relationship"""
    try:
        args = {'--payloadFile': payload_file}
        client = Relationship()
        result = client.relationshipCreate(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@relationship.command()
@click.option('--guid', required=True, help='The globally unique identifier of the relationship')
def delete(guid):
    """Delete a relationship by GUID"""
    try:
        args = {'--guid': guid}
        client = Relationship()
        result = client.relationshipDelete(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@relationship.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def put(payload_file):
    """Update or create a relationship (PUT)"""
    try:
        args = {'--payloadFile': payload_file}
        client = Relationship()
        result = client.relationshipPut(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@relationship.command()
@click.option('--guid', required=True, help='The globally unique identifier of the relationship')
@click.option('--extended-info', is_flag=True, default=False, help='Include extended information')
def read(guid, extended_info):
    """Read a relationship by GUID"""
    try:
        args = {'--guid': guid, '--extendedInfo': extended_info}
        client = Relationship()
        result = client.relationshipRead(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@relationship.command(name='bulk-create-csv')
@click.option('--csv-file', type=click.Path(exists=True), required=True, help='Path to CSV file with relationship mappings')
@click.option('--output-json', type=click.Path(), default=None, help='Optional: Save generated JSON to this file')
@click.option('--dry-run', is_flag=True, default=False, help='Preview relationships without creating them')
def bulk_create_csv(csv_file, output_json, dry_run):
    """Create relationships from CSV file
    
    CSV format required:
    info_object_guid,target_entity_guid,target_entity_type,relationship_type
    
    Example:
    d286692e-30bb-48ba-ac49-f7372b12d225,90d14acb-cf75-4729-9245-68f6f6f60000,mssql_table,Objet Information_Table_Has
    """
    try:
        console.print("[bold cyan]🔗 Bulk Create Relationships from CSV[/bold cyan]")
        console.print(f"[dim]CSV File: {csv_file}[/dim]\n")
        
        # Read CSV and generate relationships
        relationships = _read_csv_and_generate_relationships(csv_file)
        
        if not relationships:
            console.print("[yellow]⚠ No valid relationships found in CSV[/yellow]")
            return
        
        console.print(f"[green]✓ Generated {len(relationships)} relationship(s)[/green]")
        
        # Preview relationships
        _preview_relationships(relationships)
        
        # Save JSON if requested
        if output_json:
            _save_relationships_json(relationships, output_json)
        
        # Create relationships if not dry-run
        if not dry_run:
            console.print("\n[bold blue]Creating relationships...[/bold blue]")
            _create_relationships_bulk(relationships)
        else:
            console.print("\n[dim][DRY RUN] Relationships would be created with the above data[/dim]")
            
    except Exception as e:
        console.print(f"[red]✗ Error: {e}[/red]")

def _read_csv_and_generate_relationships(csv_file):
    """Read CSV file and generate relationship objects"""
    relationships = []
    required_columns = {'info_object_guid', 'target_entity_guid', 'target_entity_type', 'relationship_type'}
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate header
            if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
                console.print(f"[red]✗ CSV must contain columns: {', '.join(required_columns)}[/red]")
                return []
            
            for row_idx, row in enumerate(reader, start=2):
                try:
                    # Validate GUIDs and generate relationship
                    info_guid = row['info_object_guid'].strip()
                    target_guid = row['target_entity_guid'].strip()
                    target_type = row['target_entity_type'].strip()
                    rel_type = row['relationship_type'].strip()
                    
                    if not all([info_guid, target_guid, target_type, rel_type]):
                        console.print(f"[yellow]⚠ Row {row_idx}: Skipping due to empty fields[/yellow]")
                        continue
                    
                    relationship = {
                        "typeName": rel_type,
                        "end1": {
                            "guid": info_guid,
                            "typeName": "Objet Information"
                        },
                        "end2": {
                            "guid": target_guid,
                            "typeName": target_type
                        }
                    }
                    relationships.append(relationship)
                    
                except Exception as e:
                    console.print(f"[yellow]⚠ Row {row_idx}: {e}[/yellow]")
                    continue
        
        return relationships
        
    except FileNotFoundError:
        console.print(f"[red]✗ File not found: {csv_file}[/red]")
        return []
    except Exception as e:
        console.print(f"[red]✗ Error reading CSV: {e}[/red]")
        return []

def _preview_relationships(relationships, max_preview=5):
    """Display a preview of the relationships"""
    console.print("\n[bold blue]Preview:[/bold blue]")
    for idx, rel in enumerate(relationships[:max_preview], 1):
        console.print(f"  {idx}. {rel['end1']['guid'][:8]}... → {rel['end2']['guid'][:8]}... ({rel['typeName']})")
    
    if len(relationships) > max_preview:
        console.print(f"  ... and {len(relationships) - max_preview} more")

def _save_relationships_json(relationships, output_file):
    """Save relationships to JSON file"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(relationships, f, indent=2, ensure_ascii=False)
        console.print(f"[green]✓ Saved to: {output_file}[/green]")
    except Exception as e:
        console.print(f"[red]✗ Error saving JSON: {e}[/red]")

def _create_relationships_bulk(relationships):
    """Create relationships using the API"""
    try:
        client = Relationship()
        
        # Prepare payload - the API can accept an array of relationships
        args = {'--payloadFile': None}  # We'll set payload directly
        
        # For bulk operations, we need to call the endpoint multiple times
        # or use the bulk endpoint if available
        created = 0
        failed = 0
        
        for rel in relationships:
            try:
                # Create individual relationship
                from purviewcli.client.endpoint import get_json_from_dict
                
                # Temporarily set payload
                client.payload = rel
                client.method = "POST"
                from purviewcli.client.endpoints import ENDPOINTS, get_api_version_params
                client.endpoint = ENDPOINTS["relationship"]["create"]
                client.params = get_api_version_params("datamap")
                
                # Make the request
                result = client.make_request()
                
                if result:
                    created += 1
                    console.print(f"  [green]✓[/green] Created: {rel['typeName']}")
                    
            except Exception as e:
                failed += 1
                console.print(f"  [red]✗[/red] Failed: {rel['typeName']} - {str(e)[:50]}")
        
        console.print(f"\n[bold green]Summary:[/bold green]")
        console.print(f"  Created: {created}/{len(relationships)}")
        if failed > 0:
            console.print(f"  [red]Failed: {failed}[/red]")
            
    except Exception as e:
        console.print(f"[red]✗ Error creating relationships: {e}[/red]")

__all__ = ['relationship']
