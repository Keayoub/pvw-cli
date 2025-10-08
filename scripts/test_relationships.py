"""
Test relationship endpoints with entity type parameters
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from purviewcli.client.sync_client import SyncPurviewClient, SyncPurviewConfig
from rich.console import Console
from rich.json import JSON
import json

console = Console()

def test_relationship_endpoint(client, term_id, entity_type):
    """Test a specific relationship endpoint"""
    console.print(f"\n[bold cyan]Testing: {entity_type}[/bold cyan]")
    
    endpoint = f"/datagovernance/catalog/terms/{term_id}/relationships"
    params = {"entityType": entity_type}
    
    try:
        result = client.make_request(
            method="GET",
            endpoint=endpoint,
            params=params
        )
        
        if result.get("status_code") == 200:
            data = result.get("data", {})
            console.print(f"[green]✓[/green] Status: 200 OK")
            console.print(f"[green]✓[/green] Response structure:")
            console.print(JSON(json.dumps(data, indent=2)))
        else:
            console.print(f"[yellow]⚠[/yellow] Status: {result.get('status_code')}")
            console.print(f"Data: {result.get('data')}")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")


def main():
    console.print("[bold cyan]🔗 Testing UC Relationship Entity Types[/bold cyan]\n")
    
    # Initialize client
    account_name = os.getenv("PURVIEW_NAME", "kaydemopurview")
    config = SyncPurviewConfig(account_name=account_name, azure_region="public")
    client = SyncPurviewClient(config)
    
    console.print(f"[green]✓[/green] Connected to: {config.account_name}\n")
    
    # Test term ID from the screenshot
    term_id = "73f22182-021e-469f-9c8b-348c2ee0f213"
    
    # Entity types discovered in the URLs
    entity_types = [
        "CustomMetadata",
        "DataAsset",
        "DataProduct",
        "CriticalDataColumn",
        "CriticalDataElement",  # Also try singular form
        "Term",                 # Terms can relate to terms
        "Objective",            # Test if terms relate to objectives
    ]
    
    for entity_type in entity_types:
        test_relationship_endpoint(client, term_id, entity_type)
    
    # Also test without entityType param (get all relationships)
    console.print(f"\n[bold cyan]Testing: All Relationships (no filter)[/bold cyan]")
    try:
        result = client.make_request(
            method="GET",
            endpoint=f"/datagovernance/catalog/terms/{term_id}/relationships",
            params={}
        )
        if result.get("status_code") == 200:
            console.print(f"[green]✓[/green] Status: 200 OK")
            data = result.get("data", {})
            console.print(JSON(json.dumps(data, indent=2)))
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}")


if __name__ == "__main__":
    main()
