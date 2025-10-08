"""
Test newly discovered endpoints from browser DevTools
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from purviewcli.client.sync_client import SyncPurviewClient, SyncPurviewConfig
from rich.console import Console
from rich.json import JSON
from rich.table import Table
import json

console = Console()


def test_endpoint(client, endpoint, method="GET", params=None, payload=None, description=""):
    """Test an endpoint and display results."""
    console.print(f"\n[bold cyan]{description}[/bold cyan]")
    console.print(f"[dim]{method} {endpoint}[/dim]")
    if params:
        console.print(f"[dim]Params: {params}[/dim]")
    
    try:
        result = client.make_request(
            method=method,
            endpoint=endpoint,
            params=params or {},
            json=payload
        )
        
        status = result.get("status_code", 0)
        if status == 200:
            console.print(f"[green]✓[/green] Status: {status} OK")
            data = result.get("data", {})
            
            # Show data summary
            if isinstance(data, dict):
                if "value" in data:
                    console.print(f"[green]✓[/green] Response contains {len(data.get('value', []))} items")
                    if data.get('value'):
                        console.print(f"[dim]First item keys: {list(data['value'][0].keys())}[/dim]")
                else:
                    console.print(f"[green]✓[/green] Response keys: {list(data.keys())}")
            
            # Show full response if small
            if len(str(data)) < 1000:
                console.print(JSON(json.dumps(data, indent=2)))
            
        elif status == 400:
            console.print(f"[yellow]⚠[/yellow] Status: {status} Bad Request")
            console.print(f"[dim]Message: {result.get('data')}[/dim]")
        elif status == 404:
            console.print(f"[red]✗[/red] Status: {status} Not Found")
        elif status == 405:
            console.print(f"[yellow]⚠[/yellow] Status: {status} Method Not Allowed")
        else:
            console.print(f"[yellow]⚠[/yellow] Status: {status}")
            console.print(f"[dim]Data: {result.get('data')}[/dim]")
            
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)[:200]}")


def main():
    console.print("[bold cyan]🔍 Testing Newly Discovered Endpoints[/bold cyan]\n")
    
    # Initialize client
    account_name = os.getenv("PURVIEW_NAME", "kaydemopurview")
    config = SyncPurviewConfig(account_name=account_name, azure_region="public")
    client = SyncPurviewClient(config)
    
    console.print(f"[green]✓[/green] Connected to: {config.account_name}\n")
    
    # Test domain ID
    domain_id = "d8209808-ae13-47cd-8e38-4e2932dce8a7"
    
    # ========================================
    # QUERY ENDPOINTS (POST with query body)
    # ========================================
    
    console.print("[bold yellow]═══ QUERY ENDPOINTS ═══[/bold yellow]\n")
    
    # 1. Terms Query
    test_endpoint(
        client,
        "/datagovernance/catalog/terms/query",
        method="POST",
        payload={"domainId": domain_id},
        description="1. Terms Query Endpoint"
    )
    
    # 2. Data Products Query
    test_endpoint(
        client,
        "/datagovernance/catalog/dataproducts/query",
        method="POST",
        payload={"domainId": domain_id},
        description="2. Data Products Query Endpoint"
    )
    
    # 3. Objectives Query
    test_endpoint(
        client,
        "/datagovernance/catalog/objectives/query",
        method="POST",
        payload={"domainId": domain_id},
        description="3. Objectives Query Endpoint"
    )
    
    # ========================================
    # CUSTOM METADATA WITH DOMAIN FILTER
    # ========================================
    
    console.print("\n[bold yellow]═══ CUSTOM METADATA ═══[/bold yellow]\n")
    
    test_endpoint(
        client,
        "/datagovernance/catalog/customMetadata",
        method="GET",
        params={"domainId": domain_id},
        description="4. Custom Metadata by Domain"
    )
    
    # ========================================
    # HEALTH API (separate namespace!)
    # ========================================
    
    console.print("\n[bold yellow]═══ HEALTH API ═══[/bold yellow]\n")
    
    test_endpoint(
        client,
        "/datagovernance/health/actions/query",
        method="POST",
        params={"api-version": "2024-02-01-preview"},
        payload={},
        description="5. Health Actions Query"
    )
    
    # ========================================
    # QUALITY API (separate namespace!)
    # ========================================
    
    console.print("\n[bold yellow]═══ QUALITY API ═══[/bold yellow]\n")
    
    test_endpoint(
        client,
        f"/datagovernance/quality/business-domains/{domain_id}/report",
        method="GET",
        params={"api-version": "2023-10-01-preview"},
        description="6. Quality Report by Domain"
    )
    
    # ========================================
    # ADDITIONAL TESTS
    # ========================================
    
    console.print("\n[bold yellow]═══ ADDITIONAL EXPLORATIONS ═══[/bold yellow]\n")
    
    # Test if there are other health endpoints
    test_endpoint(
        client,
        "/datagovernance/health/actions",
        method="GET",
        params={"api-version": "2024-02-01-preview"},
        description="7. Health Actions List"
    )
    
    # Test quality root
    test_endpoint(
        client,
        "/datagovernance/quality/business-domains",
        method="GET",
        params={"api-version": "2023-10-01-preview"},
        description="8. Quality Business Domains"
    )
    
    # Test if policies support query
    test_endpoint(
        client,
        "/datagovernance/catalog/policies/query",
        method="POST",
        payload={"domainId": domain_id},
        description="9. Policies Query Endpoint"
    )
    
    # Summary
    console.print("\n[bold cyan]═══════════════════════════════════[/bold cyan]")
    console.print("[bold]Key Discoveries:[/bold]")
    console.print("• /catalog/{entity}/query endpoints support POST with filters")
    console.print("• /datagovernance/health/* - Separate Health API with api-version param")
    console.print("• /datagovernance/quality/* - Separate Quality API with api-version param")
    console.print("• customMetadata supports domainId query parameter")


if __name__ == "__main__":
    main()
