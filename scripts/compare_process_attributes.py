#!/usr/bin/env python3
"""
Compare Process entities to identify differences between UI-created and API-created lineages.
"""
import sys
import json
from purviewcli.client.endpoint import get_data
from purviewcli.client.endpoints import get_api_version_params
from rich.console import Console
from rich.table import Table
from rich.json import JSON

console = Console()

def get_full_process_details(process_guid):
    """Get complete Process entity details including all attributes."""
    try:
        result = get_data({
            "app": "catalog",
            "method": "GET",
            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{process_guid}",
            "params": get_api_version_params("datamap")
        })
        
        if not result or 'entity' not in result:
            return None
        
        return result['entity']
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")
        return None


def compare_processes(guid1, guid2):
    """Compare two Process entities."""
    
    console.print(f"\n[cyan]Fetching Process 1: {guid1}...[/cyan]")
    process1 = get_full_process_details(guid1)
    
    console.print(f"[cyan]Fetching Process 2: {guid2}...[/cyan]")
    process2 = get_full_process_details(guid2)
    
    if not process1 or not process2:
        console.print("[red]ERROR: Could not fetch one or both Process entities[/red]")
        return
    
    # Display comparison table
    console.print("\n[bold cyan]═══ PROCESS COMPARISON ═══[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Attribute", style="cyan", width=30)
    table.add_column("Process 1", style="yellow", width=40)
    table.add_column("Process 2", style="green", width=40)
    
    # Compare key attributes
    attrs_to_compare = [
        ('Name', 'attributes.name'),
        ('TypeName', 'typeName'),
        ('QualifiedName', 'attributes.qualifiedName'),
        ('Status', 'status'),
        ('Owner', 'attributes.owner'),
        ('Description', 'attributes.description'),
        ('CreateTime', 'createTime'),
        ('UpdateTime', 'updateTime'),
        ('CreatedBy', 'createdBy'),
        ('UpdatedBy', 'updatedBy'),
    ]
    
    for attr_name, attr_path in attrs_to_compare:
        val1 = get_nested_value(process1, attr_path)
        val2 = get_nested_value(process2, attr_path)
        
        # Highlight differences
        style1 = "red" if val1 != val2 else "white"
        style2 = "red" if val1 != val2 else "white"
        
        table.add_row(
            attr_name,
            f"[{style1}]{str(val1)[:40]}[/{style1}]",
            f"[{style2}]{str(val2)[:40]}[/{style2}]"
        )
    
    console.print(table)
    
    # Display full attributes for detailed inspection
    console.print("\n[bold cyan]═══ PROCESS 1 FULL ATTRIBUTES ═══[/bold cyan]")
    console.print(f"Name: {process1.get('attributes', {}).get('name')}")
    console.print(JSON(json.dumps(process1.get('attributes', {}), indent=2)))
    
    console.print("\n[bold cyan]═══ PROCESS 2 FULL ATTRIBUTES ═══[/bold cyan]")
    console.print(f"Name: {process2.get('attributes', {}).get('name')}")
    console.print(JSON(json.dumps(process2.get('attributes', {}), indent=2)))
    
    # Check for special attributes that might indicate UI vs API creation
    console.print("\n[bold cyan]═══ SPECIAL ATTRIBUTES CHECK ═══[/bold cyan]")
    
    special_attrs = ['__purview_lineage_source', 'lineageSource', 'lineageType', 
                     'manualLineage', 'isManual', '__ui_created', 'createMethod']
    
    for attr in special_attrs:
        val1 = process1.get('attributes', {}).get(attr)
        val2 = process2.get('attributes', {}).get(attr)
        if val1 or val2:
            console.print(f"  {attr}:")
            console.print(f"    Process 1: {val1}")
            console.print(f"    Process 2: {val2}")


def get_nested_value(obj, path):
    """Get nested dictionary value using dot notation."""
    keys = path.split('.')
    value = obj
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, 'N/A')
        else:
            return 'N/A'
    return value if value is not None else 'N/A'


if __name__ == "__main__":
    if len(sys.argv) < 3:
        console.print("[red]Usage: python compare_process_attributes.py <process_guid_1> <process_guid_2>[/red]")
        console.print("\nExample:")
        console.print("  python compare_process_attributes.py f7dca53a-14a6-4113-8c71-51ec95ab3f2e 45396eb5-a21f-452d-a2b5-9ed608782b58")
        sys.exit(1)
    
    guid1 = sys.argv[1]
    guid2 = sys.argv[2]
    compare_processes(guid1, guid2)
