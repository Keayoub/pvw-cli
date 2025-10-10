#!/usr/bin/env python3
"""
Delete all Unified Catalog terms in a domain - Enhanced Version

Usage:
    python scripts/delete_all_uc_terms_v2.py --domain-id <domain-id>
    python scripts/delete_all_uc_terms_v2.py --domain-id <domain-id> --force
"""

import subprocess
import json
import sys
import argparse
import time
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()


def run_cli_command(args):
    """Run a purviewcli command and return result"""
    try:
        result = subprocess.run(
            ["python", "-m", "purviewcli"] + args,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout, result.returncode
    except Exception as e:
        console.print(f"[red]Error running command: {e}[/red]")
        return None, 1


def get_all_terms(domain_id):
    """Get all terms in a domain using --output json"""
    console.print(f"[cyan]🔍 Fetching terms from domain: {domain_id}[/cyan]")
    
    output, code = run_cli_command([
        "uc", "term", "list",
        "--domain-id", domain_id,
        "--output", "json"
    ])
    
    if code != 0 or not output:
        console.print("[red]❌ Failed to fetch terms[/red]")
        return []
    
    try:
        terms = json.loads(output)
        return terms
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Failed to parse JSON: {e}[/red]")
        return []


def delete_term(term_id):
    """Delete a single term"""
    output, code = run_cli_command([
        "uc", "term", "delete",
        "--term-id", term_id,
        "--confirm"
    ])
    return code == 0


def display_terms_table(terms):
    """Display terms in a Rich table"""
    table = Table(title="Terms to be Deleted", show_lines=True)
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("ID (short)", style="blue", no_wrap=True)
    
    for i, term in enumerate(terms, 1):
        term_id_short = term.get('id', 'N/A')[:20] + "..."
        table.add_row(
            str(i),
            term.get('name', 'N/A'),
            term.get('status', 'N/A'),
            term_id_short
        )
    
    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="Delete all Unified Catalog terms in a domain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/delete_all_uc_terms_v2.py --domain-id "59ae27b5-40bc-4c90-abfe-fe1a0638fe3a"
    python scripts/delete_all_uc_terms_v2.py --domain-id "59ae27b5-40bc-4c90-abfe-fe1a0638fe3a" --force
        """
    )
    parser.add_argument("--domain-id", required=True, help="Domain ID to delete terms from")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    
    # Header
    console.print("\n[bold cyan]╔════════════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║  Unified Catalog - Bulk Term Deletion                         ║[/bold cyan]")
    console.print("[bold cyan]╚════════════════════════════════════════════════════════════════╝[/bold cyan]\n")
    
    # Get all terms
    terms = get_all_terms(args.domain_id)
    
    if not terms:
        console.print("[yellow]⚠️  No terms found in this domain.[/yellow]")
        return 0
    
    total_terms = len(terms)
    console.print(f"[green]✅ Found {total_terms} term(s)[/green]\n")
    
    # Display terms
    display_terms_table(terms)
    
    # Confirmation
    if not args.force:
        console.print(f"\n[red bold]⚠️  WARNING: This will permanently delete all {total_terms} terms![/red bold]")
        if not Confirm.ask("\n[yellow]Are you sure you want to proceed?[/yellow]", default=False):
            console.print("[yellow]❌ Operation cancelled by user.[/yellow]")
            return 0
    
    # Delete terms with progress bar
    console.print("\n[cyan]🗑️  Starting deletion...[/cyan]\n")
    
    success_count = 0
    failed_count = 0
    failed_terms = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Deleting terms...", total=total_terms)
        
        for i, term in enumerate(terms, 1):
            term_id = term.get('id')
            term_name = term.get('name')
            
            progress.update(task, description=f"[cyan]Deleting: {term_name}")
            
            if delete_term(term_id):
                success_count += 1
                progress.console.print(f"[{i}/{total_terms}] ✅ {term_name}", style="green")
            else:
                failed_count += 1
                failed_terms.append({
                    'name': term_name,
                    'id': term_id
                })
                progress.console.print(f"[{i}/{total_terms}] ❌ {term_name}", style="red")
            
            progress.advance(task)
            
            # Small delay to avoid rate limiting
            time.sleep(0.2)
    
    # Summary
    console.print("\n" + "="*70)
    console.print("[cyan bold]📊 Deletion Summary[/cyan bold]")
    console.print("="*70 + "\n")
    
    console.print(f"  Total terms:             [cyan]{total_terms}[/cyan]")
    console.print(f"  [green]✅ Successfully deleted:[/green] [white]{success_count}[/white]")
    console.print(f"  [red]❌ Failed:[/red]               [white]{failed_count}[/white]")
    
    # Show failed terms if any
    if failed_terms:
        console.print("\n[red bold]⚠️  Failed Terms:[/red bold]")
        fail_table = Table()
        fail_table.add_column("Name", style="yellow")
        fail_table.add_column("ID", style="red")
        
        for term in failed_terms:
            fail_table.add_row(term['name'], term['id'])
        
        console.print(fail_table)
    
    # Final status
    console.print()
    if failed_count == 0:
        console.print("[bold green]🎉 All terms deleted successfully![/bold green]")
        return 0
    else:
        console.print(f"[yellow]⚠️  Deletion completed with {failed_count} error(s)[/yellow]")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]❌ Operation cancelled by user (Ctrl+C)[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[red bold]❌ Unexpected error: {e}[/red bold]")
        sys.exit(1)
