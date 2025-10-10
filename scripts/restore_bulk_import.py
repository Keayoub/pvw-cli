"""
Script to restore bulk import functionality to unified_catalog.py
"""

# The bulk import code to insert after the term update command

BULK_IMPORT_CODE = '''

@term.command(name="bulk-import-csv")
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="Path to CSV file with terms")
@click.option("--domain-id", required=True, help="Governance domain ID for all terms")
@click.option("--dry-run", is_flag=True, help="Preview terms without creating them")
def import_terms_from_csv(csv_file, domain_id, dry_run):
    """Bulk import glossary terms from a CSV file.
    
    CSV Format:
    name,description,status,acronyms,owner_ids,resource_name,resource_url
    
    - name: Required term name
    - description: Optional description
    - status: Draft, Published, or Archived (default: Draft)
    - acronyms: Comma-separated list (e.g., "API,REST")
    - owner_ids: Comma-separated list of Entra Object IDs
    - resource_name: Name of related resource
    - resource_url: URL of related resource
    
    Multiple resources can be specified by separating with semicolons.
    """
    try:
        client = UnifiedCatalogClient()
        
        # Read and parse CSV
        terms = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                term = {
                    "name": row.get("name", "").strip(),
                    "description": row.get("description", "").strip(),
                    "status": row.get("status", "Draft").strip(),
                    "domain_id": domain_id,
                    "acronyms": [],
                    "owner_ids": [],
                    "resources": []
                }
                
                # Parse acronyms
                if row.get("acronyms"):
                    term["acronyms"] = [a.strip() for a in row["acronyms"].split(",") if a.strip()]
                
                # Parse owner IDs
                if row.get("owner_ids"):
                    term["owner_ids"] = [o.strip() for o in row["owner_ids"].split(",") if o.strip()]
                
                # Parse resources
                resource_names = row.get("resource_name", "").strip()
                resource_urls = row.get("resource_url", "").strip()
                
                if resource_names and resource_urls:
                    names = [n.strip() for n in resource_names.split(";") if n.strip()]
                    urls = [u.strip() for u in resource_urls.split(";") if u.strip()]
                    term["resources"] = [{"name": n, "url": u} for n, u in zip(names, urls)]
                
                if term["name"]:  # Only add if name is present
                    terms.append(term)
        
        if not terms:
            console.print("[yellow]No valid terms found in CSV file.[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(terms)} term(s) in CSV file[/cyan]")
        
        if dry_run:
            console.print("\\n[yellow]DRY RUN - Preview of terms to be created:[/yellow]\\n")
            table = Table(title="Terms to Import")
            table.add_column("#", style="dim", width=4)
            table.add_column("Name", style="cyan")
            table.add_column("Status", style="yellow")
            table.add_column("Acronyms", style="magenta")
            table.add_column("Owners", style="green")
            
            for i, term in enumerate(terms, 1):
                acronyms = ", ".join(term.get("acronyms", []))
                owners = ", ".join(term.get("owner_ids", []))
                table.add_row(
                    str(i),
                    term["name"],
                    term["status"],
                    acronyms or "-",
                    owners or "-"
                )
            
            console.print(table)
            console.print(f"\\n[dim]Domain ID: {domain_id}[/dim]")
            return
        
        # Import terms (one by one using single POST)
        success_count = 0
        failed_count = 0
        failed_terms = []
        
        with console.status("[bold green]Importing terms...") as status:
            for i, term in enumerate(terms, 1):
                status.update(f"[bold green]Creating term {i}/{len(terms)}: {term['name']}")
                
                try:
                    # Create individual term
                    args = {
                        "--name": [term["name"]],
                        "--description": [term.get("description", "")],
                        "--governance-domain-id": [term["domain_id"]],
                        "--status": [term.get("status", "Draft")],
                    }
                    
                    if term.get("acronyms"):
                        args["--acronym"] = term["acronyms"]
                    
                    if term.get("owner_ids"):
                        args["--owner-id"] = term["owner_ids"]
                    
                    if term.get("resources"):
                        args["--resource-name"] = [r["name"] for r in term["resources"]]
                        args["--resource-url"] = [r["url"] for r in term["resources"]]
                    
                    result = client.create_term(args)
                    
                    # Check if result contains an ID (indicates successful creation)
                    if result and isinstance(result, dict) and result.get("id"):
                        success_count += 1
                        term_id = result.get("id")
                        console.print(f"[green]Created: {term['name']} (ID: {term_id})[/green]")
                    elif result and not (isinstance(result, dict) and "error" in result):
                        # Got a response but no ID - might be an issue
                        console.print(f"[yellow]WARNING: Response received for {term['name']} but no ID returned[/yellow]")
                        console.print(f"[dim]Response: {json.dumps(result, indent=2)[:200]}...[/dim]")
                        failed_count += 1
                        failed_terms.append({"name": term["name"], "error": "No ID in response"})
                    else:
                        failed_count += 1
                        error_msg = result.get("error", "Unknown error") if isinstance(result, dict) else "No response"
                        failed_terms.append({"name": term["name"], "error": error_msg})
                        console.print(f"[red]FAILED: {term['name']} - {error_msg}[/red]")
                    
                except Exception as e:
                    failed_count += 1
                    failed_terms.append({"name": term["name"], "error": str(e)})
                    console.print(f"[red]FAILED: {term['name']} - {str(e)}[/red]")
        
        # Summary
        console.print("\\n" + "="*60)
        console.print(f"[cyan]Import Summary:[/cyan]")
        console.print(f"  Total terms: {len(terms)}")
        console.print(f"  [green]Successfully created: {success_count}[/green]")
        console.print(f"  [red]Failed: {failed_count}[/red]")
        
        if failed_terms:
            console.print("\\n[red]Failed Terms:[/red]")
            for ft in failed_terms:
                console.print(f"  • {ft['name']}: {ft['error']}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@term.command(name="bulk-import-json")
@click.option("--json-file", required=True, type=click.Path(exists=True), help="Path to JSON file with terms")
@click.option("--dry-run", is_flag=True, help="Preview terms without creating them")
def import_terms_from_json(json_file, dry_run):
    """Bulk import glossary terms from a JSON file.
    
    JSON Format:
    [
        {
            "name": "Term Name",
            "description": "Description",
            "domain_id": "domain-guid",
            "status": "Draft",
            "acronyms": ["API", "REST"],
            "owner_ids": ["owner-guid-1"],
            "resources": [
                {"name": "Resource Name", "url": "https://example.com"}
            ]
        }
    ]
    
    Each term must include domain_id.
    """
    try:
        client = UnifiedCatalogClient()
        
        # Read and parse JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            terms = json.load(f)
        
        if not isinstance(terms, list):
            console.print("[red]ERROR:[/red] JSON file must contain an array of terms")
            return
        
        if not terms:
            console.print("[yellow]No terms found in JSON file.[/yellow]")
            return
        
        console.print(f"[cyan]Found {len(terms)} term(s) in JSON file[/cyan]")
        
        if dry_run:
            console.print("\\n[yellow]DRY RUN - Preview of terms to be created:[/yellow]\\n")
            _format_json_output(terms)
            return
        
        # Import terms
        success_count = 0
        failed_count = 0
        failed_terms = []
        
        with console.status("[bold green]Importing terms...") as status:
            for i, term in enumerate(terms, 1):
                term_name = term.get("name", f"Term {i}")
                status.update(f"[bold green]Creating term {i}/{len(terms)}: {term_name}")
                
                try:
                    args = {
                        "--name": [term.get("name", "")],
                        "--description": [term.get("description", "")],
                        "--governance-domain-id": [term.get("domain_id", "")],
                        "--status": [term.get("status", "Draft")],
                    }
                    
                    if term.get("acronyms"):
                        args["--acronym"] = term["acronyms"]
                    
                    if term.get("owner_ids"):
                        args["--owner-id"] = term["owner_ids"]
                    
                    if term.get("resources"):
                        args["--resource-name"] = [r.get("name", "") for r in term["resources"]]
                        args["--resource-url"] = [r.get("url", "") for r in term["resources"]]
                    
                    result = client.create_term(args)
                    
                    # Check if result contains an ID (indicates successful creation)
                    if result and isinstance(result, dict) and result.get("id"):
                        success_count += 1
                        term_id = result.get("id")
                        console.print(f"[green]Created: {term_name} (ID: {term_id})[/green]")
                    elif result and not (isinstance(result, dict) and "error" in result):
                        # Got a response but no ID - might be an issue
                        console.print(f"[yellow]WARNING: Response received for {term_name} but no ID returned[/yellow]")
                        console.print(f"[dim]Response: {json.dumps(result, indent=2)[:200]}...[/dim]")
                        failed_count += 1
                        failed_terms.append({"name": term_name, "error": "No ID in response"})
                    else:
                        failed_count += 1
                        error_msg = result.get("error", "Unknown error") if isinstance(result, dict) else "No response"
                        failed_terms.append({"name": term_name, "error": error_msg})
                        console.print(f"[red]FAILED: {term_name} - {error_msg}[/red]")
                    
                except Exception as e:
                    failed_count += 1
                    failed_terms.append({"name": term_name, "error": str(e)})
                    console.print(f"[red]FAILED: {term_name} - {str(e)}[/red]")
        
        # Summary
        console.print("\\n" + "="*60)
        console.print(f"[cyan]Import Summary:[/cyan]")
        console.print(f"  Total terms: {len(terms)}")
        console.print(f"  [green]Successfully created: {success_count}[/green]")
        console.print(f"  [red]Failed: {failed_count}[/red]")
        
        if failed_terms:
            console.print("\\n[red]Failed Terms:[/red]")
            for ft in failed_terms:
                console.print(f"  • {ft['name']}: {ft['error']}")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

'''

def main():
    filepath = 'purviewcli/cli/unified_catalog.py'
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the position to insert (after term update command, before OKRs section)
    marker = '''    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


# ========================================
# OBJECTIVES AND KEY RESULTS (OKRs)
# ========================================'''
    
    if marker in content:
        # Insert bulk import code before the marker
        insertion_point = content.index(marker)
        new_content = content[:insertion_point] + '''    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")
''' + BULK_IMPORT_CODE + '''

# ========================================
# OBJECTIVES AND KEY RESULTS (OKRs)
# ========================================''' + content[insertion_point + len(marker):]
        
        # Remove emoji
        emoji_replacements = {
            '✅': '',
            '❌': '',
            '⚠️': '',
            '⚠': ''
        }
        
        for emoji, replacement in emoji_replacements.items():
            new_content = new_content.replace(emoji, replacement)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✓ Bulk import functionality restored!")
        print("✓ Emoji removed for Windows compatibility!")
        print(f"  File now has {len(new_content.splitlines())} lines")
    else:
        print("✗ Could not find insertion point in file")

if __name__ == '__main__':
    main()
