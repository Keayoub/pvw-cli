"""
Health CLI commands for Microsoft Purview Unified Catalog
"""

import click
from rich.table import Table
from .console_utils import get_console
from purviewcli.client._health import Health
import re

console = get_console()


@click.group()
def health():
    """Health monitoring and governance recommendations."""
    pass


@health.command()
@click.option("--domain-id", help="Filter by governance domain ID")
@click.option("--severity", help="Filter by severity: High, Medium, Low")
@click.option("--status", help="Filter by status: NotStarted, InProgress, Resolved, Dismissed")
@click.option("--finding-type", help="Filter by finding type (e.g., 'Estate Curation')")
@click.option("--target-entity-type", help="Filter by target entity type (e.g., DataProduct, Term)")
def query(domain_id, severity, status, finding_type, target_entity_type):
    """Query health actions (findings and recommendations)."""
    client = Health()
    
    args = {
        "--domain-id": [domain_id] if domain_id else [""],
        "--severity": [severity] if severity else [""],
        "--status": [status] if status else [""],
        "--finding-type": [finding_type] if finding_type else [""],
        "--target-entity-type": [target_entity_type] if target_entity_type else [""]
    }
    
    result = client.query_health_actions(args)
    
    # get_data() in endpoint.py returns just the data part
    if result and isinstance(result, dict):
        actions = result.get("value", [])
        
        if not actions:
            console.print("[yellow]No health actions found matching the filters.[/yellow]")
            return
        
        # Create summary table
        table = Table(title=f"Health Actions ({len(actions)} found)", show_lines=True)
        table.add_column("ID", style="cyan", no_wrap=False)
        table.add_column("Finding", style="white", no_wrap=False)
        table.add_column("Severity", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Target", style="magenta", no_wrap=False)
        table.add_column("Domain", style="blue", no_wrap=False)
        
        for action in actions:
            # Color severity
            severity_text = action.get("severity", "N/A")
            if severity_text == "High":
                severity_style = "[red]High[/red]"
            elif severity_text == "Medium":
                severity_style = "[yellow]Medium[/yellow]"
            else:
                severity_style = "[green]Low[/green]"
            
            # Color status
            status_text = action.get("status", "N/A")
            if status_text == "NotStarted":
                status_style = "[red]Not Started[/red]"
            elif status_text == "InProgress":
                status_style = "[yellow]In Progress[/yellow]"
            elif status_text == "Resolved":
                status_style = "[green]Resolved[/green]"
            else:
                status_style = status_text
            
            # Truncate IDs for display
            action_id = action.get("id", "N/A")
            short_id = action_id[:13] + "..." if len(action_id) > 16 else action_id
            
            domain_id_val = action.get("domainId", "N/A")
            short_domain = domain_id_val[:13] + "..." if len(domain_id_val) > 16 else domain_id_val
            
            table.add_row(
                short_id,
                action.get("findingName", "N/A"),
                severity_style,
                status_style,
                action.get("targetEntityType", "N/A"),
                short_domain
            )
        
        console.print(table)
        console.print(f"\n[dim]Showing {len(actions)} health action(s)[/dim]")
        console.print("[dim]Use 'pvcli uc health show --action-id <id>' for details[/dim]")
    else:
        console.print("[red]Failed to retrieve health actions.[/red]")


@health.command()
@click.option("--action-id", required=True, help="Health action ID")
def show(action_id):
    """Show detailed information about a health action."""
    client = Health()
    args = {"--action-id": [action_id]}
    
    result = client.get_health_action(args)
    
    # get_data() returns just the data part
    if result and isinstance(result, dict) and "id" in result:
        action = result
        
        console.print(f"\n[bold cyan]Health Action Details[/bold cyan]\n")
        
        # Basic info
        console.print(f"[bold]ID:[/bold] {action.get('id', 'N/A')}")
        console.print(f"[bold]Finding ID:[/bold] {action.get('findingId', 'N/A')}")
        console.print(f"[bold]Name:[/bold] {action.get('findingName', 'N/A')}")
        
        # Severity with color
        severity = action.get("severity", "N/A")
        severity_color = "red" if severity == "High" else "yellow" if severity == "Medium" else "green"
        console.print(f"[bold]Severity:[/bold] [{severity_color}]{severity}[/{severity_color}]")
        
        # Status with color
        status = action.get("status", "N/A")
        status_color = "red" if status == "NotStarted" else "yellow" if status == "InProgress" else "green"
        console.print(f"[bold]Status:[/bold] [{status_color}]{status}[/{status_color}]")
        
        # Category and types
        console.print(f"\n[bold]Category:[/bold] {action.get('category', 'N/A')}")
        console.print(f"[bold]Finding Type:[/bold] {action.get('findingType', 'N/A')}")
        console.print(f"[bold]Finding SubType:[/bold] {action.get('findingSubType', 'N/A')}")
        
        # Target
        console.print(f"\n[bold]Target Entity Type:[/bold] {action.get('targetEntityType', 'N/A')}")
        console.print(f"[bold]Target Entity ID:[/bold] {action.get('targetEntityId', 'N/A')}")
        console.print(f"[bold]Domain ID:[/bold] {action.get('domainId', 'N/A')}")
        
        # Recommendation
        recommendation = action.get("recommendation", "")
        if recommendation:
            console.print(f"\n[bold]Recommendation:[/bold]\n{recommendation}")
        
        # Reason
        reason = action.get("reason", "")
        if reason:
            console.print(f"\n[bold]Reason:[/bold]\n{reason}")
        
        # Assignment
        assigned_to = action.get("assignedTo", [])
        if assigned_to:
            console.print(f"\n[bold]Assigned To:[/bold]")
            for user_id in assigned_to:
                console.print(f"  • {user_id}")
        else:
            console.print(f"\n[bold]Assigned To:[/bold] [yellow]Not assigned[/yellow]")
        
        # System data
        system_data = action.get("systemData", {})
        if system_data:
            console.print(f"\n[bold]System Information:[/bold]")
            console.print(f"  Created At: {system_data.get('createdAt', 'N/A')}")
            console.print(f"  Created By: {system_data.get('createdBy', 'N/A')}")
            console.print(f"  Last Modified: {system_data.get('lastModifiedAt', 'N/A')}")
            console.print(f"  Last Modified By: {system_data.get('lastModifiedBy', 'N/A')}")
            console.print(f"  Last Hint At: {system_data.get('lastHintAt', 'N/A')}")
        
        console.print()
    else:
        console.print(f"[red]Failed to retrieve health action: {action_id}[/red]")


@health.command()
@click.option("--action-id", required=True, help="Health action ID")
@click.option("--status", help="New status: NotStarted, InProgress, Resolved, Dismissed")
@click.option("--assigned-to", help="User ID or email to assign to")
@click.option("--reason", help="Reason for the update")
def update(action_id, status, assigned_to, reason):
    """Update a health action (status, assignment, etc.)."""
    if not status and not assigned_to and not reason:
        console.print("[red]Error: At least one of --status, --assigned-to, or --reason must be provided.[/red]")
        return
    
    client = Health()
    args = {
        "--action-id": [action_id],
        "--status": [status] if status else [""],
        "--assigned-to": [assigned_to] if assigned_to else [""],
        "--reason": [reason] if reason else [""]
    }
    
    result = client.update_health_action(args)
    
    if result and result.get("status") == "success":
        console.print(f"[green][OK][/green] Health action updated successfully: {action_id}")
        if status:
            console.print(f"  Status: {status}")
        if assigned_to:
            console.print(f"  Assigned to: {assigned_to}")
        if reason:
            console.print(f"  Reason: {reason}")
    else:
        console.print(f"[red]Failed to update health action: {action_id}[/red]")


@health.command()
@click.option("--action-id", required=True, help="Health action ID")
@click.confirmation_option(prompt="Are you sure you want to delete this health action?")
def delete(action_id):
    """Delete a health action."""
    client = Health()
    args = {"--action-id": [action_id]}
    
    result = client.delete_health_action(args)
    
    if result and result.get("status") == "success":
        console.print(f"[green][OK][/green] Health action deleted successfully: {action_id}")
    else:
        console.print(f"[red]Failed to delete health action: {action_id}[/red]")


@health.command()
@click.option("--domain-id", help="Get summary for specific domain")
def summary(domain_id):
    """Get health summary statistics."""
    client = Health()
    args = {"--domain-id": [domain_id] if domain_id else [""]}
    
    result = client.get_health_summary(args)
    
    if result and result.get("data"):
        summary_data = result["data"]
        
        console.print("\n[bold cyan]Health Summary[/bold cyan]\n")
        
        # Display summary statistics
        console.print(f"Total Actions: {summary_data.get('total', 'N/A')}")
        console.print(f"High Severity: [red]{summary_data.get('high', 'N/A')}[/red]")
        console.print(f"Medium Severity: [yellow]{summary_data.get('medium', 'N/A')}[/yellow]")
        console.print(f"Low Severity: [green]{summary_data.get('low', 'N/A')}[/green]")
        console.print(f"\nNot Started: [red]{summary_data.get('notStarted', 'N/A')}[/red]")
        console.print(f"In Progress: [yellow]{summary_data.get('inProgress', 'N/A')}[/yellow]")
        console.print(f"Resolved: [green]{summary_data.get('resolved', 'N/A')}[/green]")
        
        console.print()
    else:
        console.print("[yellow]Summary endpoint may not be available or no data returned.[/yellow]")
        console.print("[dim]Try using 'pvcli uc health query' to see all actions.[/dim]")
