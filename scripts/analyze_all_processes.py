#!/usr/bin/env python3
"""
Analyze all Process entities to identify their lineage source (UI vs API vs Scan).
"""
import json
from purviewcli.client.endpoint import get_data
from purviewcli.client.endpoints import get_api_version_params
from rich.console import Console
from rich.table import Table

console = Console()

def analyze_all_processes():
    """Search and analyze all Process entities."""
    try:
        # Search for all Process entities
        console.print("[cyan]Searching for all Process entities...[/cyan]\n")
        
        result = get_data({
            "app": "catalog",
            "method": "POST",
            "endpoint": "/datamap/api/atlas/v2/search/basic",
            "params": get_api_version_params("datamap"),
            "payload": {
                "query": "*",
                "typeName": "Process",
                "limit": 100,
                "offset": 0
            }
        })
        
        if not result or 'entities' not in result:
            console.print("[yellow]No Process entities found[/yellow]")
            return
        
        entities = result['entities']
        console.print(f"[green]Found {len(entities)} Process entities[/green]\n")
        
        # Analyze each Process
        table = Table(show_header=True, header_style="bold magenta", show_lines=True)
        table.add_column("Name", style="cyan", width=30)
        table.add_column("GUID", style="dim", width=15)
        table.add_column("Inputs", style="green", justify="center")
        table.add_column("Outputs", style="blue", justify="center")
        table.add_column("Has Schema?", justify="center")
        table.add_column("Lineage Type", style="yellow", width=20)
        
        for entity in entities:
            guid = entity.get('guid', 'N/A')
            name = entity.get('attributes', {}).get('name', 'N/A')
            
            # Get full entity details
            detailed = get_process_details(guid)
            if not detailed:
                continue
            
            attrs = detailed.get('attributes', {})
            inputs = attrs.get('inputs', [])
            outputs = attrs.get('outputs', [])
            
            # Determine lineage type based on characteristics
            lineage_type = determine_lineage_type(detailed)
            
            # Check if it has schema (should be N/A for Process)
            has_schema = "Yes" if detailed.get('relationshipAttributes', {}).get('schema') else "No"
            
            # Format display
            guid_short = guid[:13] + "..." if len(guid) > 13 else guid
            
            table.add_row(
                name[:30],
                guid_short,
                str(len(inputs)),
                str(len(outputs)),
                has_schema,
                lineage_type
            )
        
        console.print(table)
        
        # Summary
        console.print(f"\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"  Total Process entities: {len(entities)}")
        
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


def get_process_details(guid):
    """Get detailed Process entity information."""
    try:
        result = get_data({
            "app": "catalog",
            "method": "GET",
            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{guid}",
            "params": get_api_version_params("datamap")
        })
        return result.get('entity') if result else None
    except:
        return None


def determine_lineage_type(entity):
    """Determine the lineage type based on entity characteristics."""
    attrs = entity.get('attributes', {})
    
    # Check for inputs/outputs
    has_inputs = len(attrs.get('inputs', [])) > 0
    has_outputs = len(attrs.get('outputs', [])) > 0
    
    if not has_inputs and not has_outputs:
        return "⚠️ INVALID (No I/O)"
    
    # Check qualified name pattern
    qn = attrs.get('qualifiedName', '')
    name = attrs.get('name', '')
    
    # Check for specific patterns
    if '@default' in qn:
        if has_inputs and has_outputs:
            return "✅ API/CLI Created"
        else:
            return "⚠️ API Incomplete"
    
    # Check for UI patterns (typically simpler names)
    if name in ['Produces', 'Consumes', 'Process']:
        return "🖱️ UI Manual (maybe)"
    
    # Check for scan patterns
    if 'scan' in qn.lower() or 'auto' in qn.lower():
        return "🔍 Auto Scan"
    
    return "❓ Unknown"


if __name__ == "__main__":
    analyze_all_processes()
