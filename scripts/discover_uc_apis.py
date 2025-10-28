"""
Unified Catalog API Discovery Script
Tests potential API endpoints to discover new/upcoming features

This script tests both:
1. Current API: /datagovernance/catalog/* (working)
2. New UC API (2024-03-01-preview): TBD base path (announced Oct 2025)

See doc/UC_API_MIGRATION.md for migration plan.
"""

import sys
import os

# Add parent directory to path to import purviewcli modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from purviewcli.client.sync_client import SyncPurviewClient
from rich.console import Console
from rich.table import Table

console = Console()

def test_endpoint(client, endpoint, method="GET", app="datagovernance", api_version=None):
    """Test if an endpoint exists and returns data."""
    try:
        params = {}
        if api_version:
            params["api-version"] = api_version
            
        response = client.make_request(
            method=method,
            endpoint=endpoint,
            params=params,
            payload=None,
            app=app
        )
        
        if response and response.get("status_code") in [200, 201]:
            return {
                "status": "✅ Available",
                "code": response.get("status_code"),
                "has_data": bool(response.get("data"))
            }
        elif response and response.get("status_code") == 404:
            return {
                "status": "❌ Not Found",
                "code": 404,
                "has_data": False
            }
        elif response and response.get("status_code") == 403:
            return {
                "status": "🔒 Forbidden",
                "code": 403,
                "has_data": False
            }
        elif response and response.get("status_code") == 501:
            return {
                "status": "🚧 Not Implemented",
                "code": 501,
                "has_data": False
            }
        else:
            return {
                "status": f"⚠️ {response.get('status_code', 'Unknown')}",
                "code": response.get("status_code", 0),
                "has_data": False
            }
    except Exception as e:
        return {
            "status": f"❌ Error",
            "code": 0,
            "has_data": False,
            "error": str(e)
        }


def main():
    console.print("[bold cyan]🔍 Microsoft Purview Unified Catalog API Discovery[/bold cyan]\n")
    
    # Initialize client
    try:
        from purviewcli.client.sync_client import SyncPurviewConfig
        
        # Get account name from environment or default
        account_name = os.getenv("PURVIEW_NAME", "kaydemopurview")
        account_id = os.getenv("PURVIEW_ACCOUNT_ID")  # Tenant ID for UC
        
        config = SyncPurviewConfig(
            account_name=account_name,
            azure_region="public",
            account_id=account_id
        )
        
        client = SyncPurviewClient(config)
        console.print(f"[green]✓[/green] Connected to: {config.account_name}")
        console.print(f"[green]✓[/green] Base URL: {client.base_url}")
        console.print(f"[green]✓[/green] UC Base URL: {client.uc_base_url}\n")
    except Exception as e:
        console.print(f"[red]Failed to connect:[/red] {e}")
        return
    
    # Known implemented endpoints (Current API)
    known_endpoints = {
        "/datagovernance/catalog/businessdomains": "Governance Domains",
        "/datagovernance/catalog/dataproducts": "Data Products",
        "/datagovernance/catalog/terms": "Terms",
        "/datagovernance/catalog/objectives": "Objectives (OKRs)",
        "/datagovernance/catalog/criticalDataElements": "Critical Data Elements",
    }
    
    # New Unified Catalog API endpoints (2024-03-01-preview)
    # Base path unknown - trying multiple possibilities
    new_uc_api_candidates = [
        "/datamap/api/unifiedcatalog/v1",
        "/datagovernance/unifiedcatalog/v1", 
        "/unifiedcatalog/v1",
        "/catalog/unifiedcatalog/v1",
        "/api/unifiedcatalog/v1"
    ]
    
    new_uc_operations = {
        "/businessdomains": "Business Domains",
        "/dataproducts": "Data Products",
        "/terms": "Terms",
        "/objectives": "Objectives",
        "/criticalDataElements": "Critical Data Elements",
        "/policies": "Policies"
    }
    
    # Potential new endpoints to discover
    potential_endpoints = {
        # Policy & Governance
        "/datagovernance/catalog/policies": "Data Policies",
        "/datagovernance/catalog/policy": "Data Policy (singular)",
        "/datagovernance/catalog/rules": "Business Rules",
        "/datagovernance/catalog/compliance": "Compliance Items",
        
        # Workflow & Approval
        "/datagovernance/catalog/workflows": "Workflows",
        "/datagovernance/catalog/approvals": "Approvals",
        "/datagovernance/catalog/requests": "Access Requests",
        
        # Metadata & Attributes
        "/datagovernance/catalog/custommetadata": "Custom Metadata",
        "/datagovernance/catalog/attributes": "Custom Attributes",
        "/datagovernance/catalog/tags": "Business Tags",
        "/datagovernance/catalog/labels": "Labels",
        
        # People & Roles
        "/datagovernance/catalog/stewards": "Data Stewards",
        "/datagovernance/catalog/owners": "Data Owners",
        "/datagovernance/catalog/experts": "Subject Matter Experts",
        "/datagovernance/catalog/contacts": "Contacts",
        
        # Assets & Lineage
        "/datagovernance/catalog/assets": "Business Assets",
        "/datagovernance/catalog/lineage": "Lineage",
        "/datagovernance/catalog/relationships": "Relationships",
        "/datagovernance/catalog/connections": "Connections",
        
        # Quality & Health
        "/datagovernance/catalog/quality": "Data Quality",
        "/datagovernance/catalog/health": "Health Checks",
        "/datagovernance/catalog/metrics": "Metrics",
        "/datagovernance/catalog/scores": "Quality Scores",
        
        # Collections & Organization
        "/datagovernance/catalog/collections": "Collections",
        "/datagovernance/catalog/categories": "Categories",
        "/datagovernance/catalog/hierarchies": "Hierarchies",
        
        # Documentation
        "/datagovernance/catalog/documentation": "Documentation",
        "/datagovernance/catalog/resources": "Resources",
        "/datagovernance/catalog/links": "External Links",
        
        # Search & Discovery
        "/datagovernance/catalog/search": "Search",
        "/datagovernance/catalog/recommendations": "Recommendations",
        "/datagovernance/catalog/insights": "Insights",
        
        # Notifications & Events
        "/datagovernance/catalog/notifications": "Notifications",
        "/datagovernance/catalog/events": "Events",
        "/datagovernance/catalog/alerts": "Alerts",
    }
    
    # Test known endpoints
    console.print("[bold]Known Implemented Endpoints:[/bold]")
    table1 = Table(show_header=True)
    table1.add_column("Endpoint", style="cyan")
    table1.add_column("Description", style="white")
    table1.add_column("Status", style="green")
    table1.add_column("Code", style="yellow")
    
    for endpoint, description in known_endpoints.items():
        result = test_endpoint(client, endpoint)
        table1.add_row(
            endpoint,
            description,
            result["status"],
            str(result["code"])
        )
    
    console.print(table1)
    console.print()
    
    # Test New Unified Catalog API (2024-03-01-preview)
    console.print("[bold magenta]🔮 Testing New Unified Catalog API (2024-03-01-preview):[/bold magenta]")
    console.print("[dim]Trying to discover base path...[/dim]\n")
    
    new_api_found = False
    new_api_base = None
    
    for base_path in new_uc_api_candidates:
        console.print(f"[cyan]Testing base: {base_path}[/cyan]")
        
        # Try with different app contexts
        for app in ["datagovernance", "datamap", None]:
            for operation, description in new_uc_operations.items():
                endpoint = base_path + operation
                result = test_endpoint(
                    client, 
                    endpoint, 
                    app=app if app else "datagovernance",
                    api_version="2024-03-01-preview"
                )
                
                if result["code"] in [200, 201]:
                    console.print(f"  [green]SUCCESS:[/green] {endpoint} (app={app}) - {description}")
                    new_api_found = True
                    new_api_base = base_path
                    break
                elif result["code"] == 401:
                    console.print(f"  [yellow]FOUND (401 Unauthorized):[/yellow] {endpoint} (app={app})")
                    console.print(f"    [dim]Endpoint exists but may require special permissions or different auth[/dim]")
                    new_api_found = True
                    new_api_base = base_path
                    break
                elif result["code"] not in [404]:
                    console.print(f"  [yellow]INTERESTING:[/yellow] {endpoint} (app={app}) - Code {result['code']}")
            
            if new_api_found:
                break
        
        if new_api_found:
            console.print(f"\n[bold yellow]� NEW API BASE PATH DETECTED: {new_api_base}[/bold yellow]")
            console.print(f"[dim]Status: Endpoint exists but returns 401 (authentication/permission issue)[/dim]\n")
            break
        else:
            console.print(f"  [red]Not found[/red] at {base_path}\n")
    
    if not new_api_found:
        console.print("[yellow]⚠️ New Unified Catalog API not yet accessible[/yellow]")
        console.print("[dim]Documentation may still be incomplete. Check again later.[/dim]\n")
    elif new_api_base:
        # Test all operations with discovered base path
        console.print("[bold]New UC API Endpoints (Testing with 2024-03-01-preview):[/bold]")
        table_new = Table(show_header=True)
        table_new.add_column("Endpoint", style="cyan")
        table_new.add_column("Description", style="white")
        table_new.add_column("Status", style="yellow")
        table_new.add_column("Code", style="yellow")
        
        for operation, description in new_uc_operations.items():
            endpoint = new_api_base + operation
            result = test_endpoint(
                client, 
                endpoint,
                api_version="2024-03-01-preview"
            )
            table_new.add_row(
                endpoint,
                description,
                result["status"],
                str(result["code"])
            )
        
        console.print(table_new)
        console.print("\n[yellow]Note:[/yellow] 401 errors indicate endpoints exist but may require:")
        console.print("  • Preview feature flags enabled in Azure Portal")
        console.print("  • Additional RBAC permissions")
        console.print("  • Different authentication scope/token")
        console.print("  • API to be fully released (currently in preview)\n")
    
    # Test potential new endpoints (Current API)
    console.print("[bold]🔍 Discovering New Endpoints (Current API):[/bold]")
    table2 = Table(show_header=True)
    table2.add_column("Endpoint", style="cyan")
    table2.add_column("Description", style="white")
    table2.add_column("Status", style="yellow")
    table2.add_column("Code", style="magenta")
    
    available_new = []
    not_found = []
    forbidden = []
    not_implemented = []
    
    for endpoint, description in potential_endpoints.items():
        result = test_endpoint(client, endpoint)
        
        table2.add_row(
            endpoint,
            description,
            result["status"],
            str(result["code"])
        )
        
        if result["code"] == 200:
            available_new.append((endpoint, description))
        elif result["code"] == 404:
            not_found.append((endpoint, description))
        elif result["code"] == 403:
            forbidden.append((endpoint, description))
        elif result["code"] == 501:
            not_implemented.append((endpoint, description))
    
    console.print(table2)
    console.print()
    
    # Summary
    console.print("[bold cyan]📊 Discovery Summary:[/bold cyan]")
    console.print(f"[bold]Current API (/datagovernance/catalog/*):[/bold]")
    console.print(f"  ✅ Known working: [green]{len(known_endpoints)}[/green]")
    console.print(f"  ✅ Available (NEW): [green]{len(available_new)}[/green]")
    console.print(f"  🔒 Forbidden: [yellow]{len(forbidden)}[/yellow]")
    console.print(f"  🚧 Not Implemented: [yellow]{len(not_implemented)}[/yellow]")
    console.print(f"  ❌ Not Found: [red]{len(not_found)}[/red]")
    
    if new_api_found and new_api_base:
        console.print(f"\n[bold]New UC API (2024-03-01-preview):[/bold]")
        console.print(f"  � Base path detected: [yellow]{new_api_base}[/yellow]")
        console.print(f"  ⚠️ Status: Exists but 401 (auth/permission required)")
        console.print(f"  ⏳ Likely needs preview feature flag or special permissions")
    else:
        console.print(f"\n[bold]New UC API (2024-03-01-preview):[/bold]")
        console.print(f"  ⏳ Not yet accessible - documentation incomplete")
    
    console.print()
    
    if available_new:
        console.print("[bold green]🎉 NEW ENDPOINTS DISCOVERED:[/bold green]")
        for endpoint, description in available_new:
            console.print(f"  • {endpoint} - {description}")
        console.print()
    
    if forbidden:
        console.print("[bold yellow]🔒 ENDPOINTS REQUIRING PERMISSIONS:[/bold yellow]")
        for endpoint, description in forbidden:
            console.print(f"  • {endpoint} - {description}")
        console.print()
    
    if not_implemented:
        console.print("[bold yellow]🚧 ENDPOINTS COMING SOON (501 Not Implemented):[/bold yellow]")
        for endpoint, description in not_implemented:
            console.print(f"  • {endpoint} - {description}")
        console.print()


if __name__ == "__main__":
    main()
