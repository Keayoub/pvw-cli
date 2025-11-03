#!/usr/bin/env python3
"""
Show relationships for a Process entity.
"""
import sys
import json
from purviewcli.client.endpoint import get_data
from purviewcli.client.endpoints import get_api_version_params
from rich.console import Console
from rich.table import Table

console = Console()

def show_process_relationships(process_guid):
    """Show all relationships for a Process entity."""
    try:
        console.print(f"[cyan]Fetching Process entity: {process_guid}...[/cyan]")
        
        # Read the Process entity
        result = get_data({
            "app": "catalog",
            "method": "GET",
            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{process_guid}",
            "params": get_api_version_params("datamap")
        })
        
        if not result or 'entity' not in result:
            console.print(f"[red]ERROR: Process entity not found[/red]")
            return
        
        entity = result['entity']
        
        # Extract relationship information
        relationships = entity.get('relationshipAttributes', {})
        
        # Display Process info
        console.print(f"\n[bold]Process: {entity.get('attributes', {}).get('name', 'N/A')}[/bold]")
        console.print(f"GUID: {process_guid}")
        console.print(f"Type: {entity.get('typeName', 'N/A')}")
        
        # Inputs
        inputs = relationships.get('inputs', [])
        if inputs:
            console.print(f"\n[green bold]Inputs ({len(inputs)}):[/green bold]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan", no_wrap=False)
            table.add_column("Type", style="yellow")
            table.add_column("GUID", style="dim")
            
            for inp in inputs:
                guid_short = inp.get('guid', 'N/A')[:13] + '...' if inp.get('guid') and len(inp.get('guid', '')) > 13 else inp.get('guid', 'N/A')
                table.add_row(
                    inp.get('displayText', 'N/A'),
                    inp.get('typeName', 'N/A'),
                    guid_short
                )
            
            console.print(table)
            
            # Show relationship types for inputs
            console.print(f"\n[dim]Input Relationship Types:[/dim]")
            for inp in inputs:
                rel_guid = inp.get('relationshipGuid', 'N/A')
                rel_type = inp.get('relationshipType', 'N/A')
                console.print(f"  - {inp.get('displayText', 'N/A')}: [yellow]{rel_type}[/yellow] (GUID: {rel_guid[:13]}...)")
        
        # Outputs
        outputs = relationships.get('outputs', [])
        if outputs:
            console.print(f"\n[blue bold]Outputs ({len(outputs)}):[/blue bold]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan", no_wrap=False)
            table.add_column("Type", style="yellow")
            table.add_column("GUID", style="dim")
            
            for out in outputs:
                guid_short = out.get('guid', 'N/A')[:13] + '...' if out.get('guid') and len(out.get('guid', '')) > 13 else out.get('guid', 'N/A')
                table.add_row(
                    out.get('displayText', 'N/A'),
                    out.get('typeName', 'N/A'),
                    guid_short
                )
            
            console.print(table)
            
            # Show relationship types for outputs
            console.print(f"\n[dim]Output Relationship Types:[/dim]")
            for out in outputs:
                rel_guid = out.get('relationshipGuid', 'N/A')
                rel_type = out.get('relationshipType', 'N/A')
                console.print(f"  - {out.get('displayText', 'N/A')}: [yellow]{rel_type}[/yellow] (GUID: {rel_guid[:13]}...)")
        
        # All relationships
        console.print(f"\n[dim]All Relationship Attributes:[/dim]")
        for rel_name, rel_value in relationships.items():
            if isinstance(rel_value, list):
                console.print(f"  {rel_name}: [{len(rel_value)} items]")
            else:
                console.print(f"  {rel_name}: {type(rel_value).__name__}")
        
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        console.print("[red]Usage: python show_process_relationships.py <process_guid>[/red]")
        sys.exit(1)
    
    process_guid = sys.argv[1]
    show_process_relationships(process_guid)
