"""
Explore Quality API endpoints in detail
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


def test_quality_endpoint(client, endpoint, params=None, description=""):
    """Test a quality API endpoint."""
    console.print(f"\n[bold cyan]{description}[/bold cyan]")
    console.print(f"[dim]GET {endpoint}[/dim]")
    if params:
        console.print(f"[dim]Params: {params}[/dim]")
    
    try:
        result = client.make_request(
            method="GET",
            endpoint=endpoint,
            params=params or {}
        )
        
        status = result.get("status_code", 0)
        data = result.get("data")
        
        if status == 200:
            console.print(f"[green]✓[/green] Status: {status} OK")
            
            if data:
                console.print(JSON(json.dumps(data, indent=2)))
            else:
                console.print("[yellow]Empty response[/yellow]")
                
        elif status == 404:
            console.print(f"[red]✗[/red] Status: {status} Not Found")
        elif status == 400:
            console.print(f"[yellow]⚠[/yellow] Status: {status} Bad Request")
            if data:
                console.print(f"[dim]{data}[/dim]")
        else:
            console.print(f"[yellow]⚠[/yellow] Status: {status}")
            if data:
                console.print(f"[dim]{data}[/dim]")
                
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {str(e)[:200]}")


def main():
    console.print("[bold cyan]🔍 Quality API Exploration[/bold cyan]\n")
    
    # Initialize client
    account_name = os.getenv("PURVIEW_NAME", "kaydemopurview")
    config = SyncPurviewConfig(account_name=account_name, azure_region="public")
    client = SyncPurviewClient(config)
    
    console.print(f"[green]✓[/green] Connected to: {config.account_name}\n")
    
    # Test domains
    domains = {
        "HR": "d4cdd762-eeca-4401-81b1-e93d8aff3fe4",
        "Finance": "d8209808-ae13-47cd-8e38-4e2932dce8a7",
        "Marketing": "abdeda41-27b7-4f50-ae71-ea7e99b9a43e",
        "Sales & Partner": "92624714-329e-4544-ab7e-9610077df500"
    }
    
    api_version = "2023-10-01-preview"
    
    console.print("[bold yellow]═══ Domain Quality Reports ═══[/bold yellow]")
    
    # Test each domain
    for domain_name, domain_id in domains.items():
        test_quality_endpoint(
            client,
            f"/datagovernance/quality/business-domains/{domain_id}/report",
            params={"api-version": api_version},
            description=f"Quality Report - {domain_name}"
        )
    
    console.print("\n[bold yellow]═══ Exploring Other Quality Endpoints ═══[/bold yellow]")
    
    # Test potential quality endpoints
    hr_domain = domains["HR"]
    
    quality_endpoints = [
        (f"/datagovernance/quality/business-domains/{hr_domain}/metrics", "Domain Metrics"),
        (f"/datagovernance/quality/business-domains/{hr_domain}/score", "Domain Score"),
        (f"/datagovernance/quality/business-domains/{hr_domain}/scores", "Domain Scores (plural)"),
        (f"/datagovernance/quality/business-domains/{hr_domain}/summary", "Domain Summary"),
        (f"/datagovernance/quality/business-domains/{hr_domain}/health", "Domain Health"),
        (f"/datagovernance/quality/business-domains/{hr_domain}", "Domain Quality Info"),
        ("/datagovernance/quality/business-domains", "All Domains"),
        ("/datagovernance/quality/metrics", "Quality Metrics"),
        ("/datagovernance/quality/reports", "Quality Reports"),
        ("/datagovernance/quality/scores", "Quality Scores"),
    ]
    
    for endpoint, description in quality_endpoints:
        test_quality_endpoint(
            client,
            endpoint,
            params={"api-version": api_version},
            description=description
        )
    
    console.print("\n[bold yellow]═══ Testing Different API Versions ═══[/bold yellow]")
    
    # Test with different API versions
    versions = [
        "2023-10-01-preview",
        "2024-02-01-preview",
        "2024-07-01-preview",
        "2025-01-01-preview",
    ]
    
    for version in versions:
        test_quality_endpoint(
            client,
            f"/datagovernance/quality/business-domains/{hr_domain}/report",
            params={"api-version": version},
            description=f"Quality Report with api-version={version}"
        )
    
    console.print("\n[bold yellow]═══ Testing Entity-Level Quality ═══[/bold yellow]")
    
    # Test if we can get quality for specific entities
    term_id = "73f22182-021e-469f-9c8b-348c2ee0f213"  # Salary term
    
    entity_quality_endpoints = [
        (f"/datagovernance/quality/terms/{term_id}", "Term Quality"),
        (f"/datagovernance/quality/terms/{term_id}/report", "Term Quality Report"),
        (f"/datagovernance/quality/terms/{term_id}/score", "Term Quality Score"),
    ]
    
    for endpoint, description in entity_quality_endpoints:
        test_quality_endpoint(
            client,
            endpoint,
            params={"api-version": api_version},
            description=description
        )


if __name__ == "__main__":
    main()
