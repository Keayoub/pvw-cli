import click
import json
from purviewcli.client._domain import Domain
from .console_utils import get_console

console = get_console()

@click.group(help="Governance domain management (Limited functionality - see individual commands for details). Governance domains are currently not fully available in the public Microsoft Purview REST API. Consider using collections as an alternative organizational structure.")
def domain():
    pass

@domain.command(help="Create a new governance domain. NOTE: This feature is not currently available in the public API. Use collections instead.")
@click.option("--name", required=True, help="The unique name of the governance domain")
@click.option("--friendly-name", help="A user-friendly display name for the domain")
@click.option("--description", help="Description of the governance domain")
@click.option("--payload-file", type=click.Path(exists=True), help="File path to a valid JSON document")
def create(name, friendly_name, description, payload_file):
    """Create a new governance domain."""
    import tempfile
    import os
    
    temp_file = None
    try:
        # If no payload file provided, create one from CLI options
        if not payload_file:
            payload = {
                "name": name,
                "friendlyName": friendly_name or name,
                "description": description or ""
            }
            
            # Create temporary payload file
            fd, temp_file = tempfile.mkstemp(suffix='.json', text=True)
            try:
                with os.fdopen(fd, 'w') as f:
                    json.dump(payload, f, indent=2)
                payload_file = temp_file
            except:
                os.close(fd)
                raise
        
        args = {
            '--name': name,
            '--payloadFile': payload_file
        }
        client = Domain()
        result = client.domainsCreate(args)
        
        if result.get("status") == "not_available":
            console.print(f"[yellow]LIMITATION:[/yellow] {result['message']}")
            if result.get("suggested_action"):
                console.print(f"[cyan]SUGGESTION:[/cyan] {result['suggested_action']}")
        else:
            console.print(f"[green]SUCCESS:[/green] Governance domain created: {name}")
            console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to create governance domain: {e}")
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass

@domain.command(help="List all governance domains. NOTE: This feature is not currently available in the public API.")
def list():
    """List all governance domains."""
    try:
        client = Domain()
        result = client.domainsList({})
        
        if result.get("status") == "not_available":
            console.print(f"[yellow]LIMITATION:[/yellow] {result['message']}")
            console.print("\n[cyan]ALTERNATIVES:[/cyan]")
            for alt in result.get("alternatives", []):
                console.print(f"  • {alt}")
            console.print("\n[cyan]TRY INSTEAD:[/cyan] pvw collections list")
        else:
            console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to list governance domains: {e}")

@domain.command(help="Get a governance domain by name. NOTE: This feature is not currently available in the public API.")
@click.option("--domain-name", required=True, help="The name of the governance domain")
def get(domain_name):
    """Get a governance domain by name."""
    try:
        args = {'--domainName': domain_name}
        client = Domain()
        result = client.domainsGet(args)
        
        if result.get("status") == "not_available":
            console.print(f"[yellow]LIMITATION:[/yellow] {result['message']}")
            if result.get("suggested_action"):
                console.print(f"[cyan]TRY INSTEAD:[/cyan] {result['suggested_action']}")
        else:
            console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to get governance domain: {e}")

@domain.command(help="Update a governance domain's friendly name and/or description. NOTE: This feature is not currently available in the public API.")
@click.option("--domain-name", required=True, help="The name of the governance domain")
@click.option("--friendly-name", help="A new user-friendly display name for the domain")
@click.option("--description", help="A new description for the domain")
@click.option("--payload-file", type=click.Path(exists=True), help="File path to a valid JSON document")
def update(domain_name, friendly_name, description, payload_file):
    """Update a governance domain's friendly name and/or description."""
    import tempfile
    import os
    
    temp_file = None
    try:
        # If no payload file provided, create one from CLI options
        if not payload_file:
            payload = {}
            if friendly_name:
                payload["friendlyName"] = friendly_name
            if description:
                payload["description"] = description
            
            if not payload:
                console.print("[yellow]WARNING:[/yellow] No updates specified. Provide --friendly-name, --description, or --payload-file")
                return
            
            # Create temporary payload file
            fd, temp_file = tempfile.mkstemp(suffix='.json', text=True)
            try:
                with os.fdopen(fd, 'w') as f:
                    json.dump(payload, f, indent=2)
                payload_file = temp_file
            except:
                os.close(fd)
                raise
        
        args = {
            '--domainName': domain_name,
            '--payloadFile': payload_file
        }
        client = Domain()
        result = client.domainsUpdate(args)
        
        if result.get("status") == "not_available":
            console.print(f"[yellow]LIMITATION:[/yellow] {result['message']}")
        else:
            console.print(f"[green]SUCCESS:[/green] Updated governance domain: {domain_name}")
            console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to update governance domain: {e}")
    finally:
        # Clean up temp file
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
            except:
                pass

@domain.command(help="Delete a governance domain by name. NOTE: This feature is not currently available in the public API.")
@click.option("--domain-name", required=True, help="The name of the governance domain")
@click.option("--force", is_flag=True, help="Force deletion without confirmation")
def delete(domain_name, force):
    """Delete a governance domain by name."""
    try:
        if not force and not click.confirm(f"Are you sure you want to delete domain '{domain_name}'?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
            
        args = {'--domainName': domain_name}
        client = Domain()
        result = client.domainsDelete(args)
        
        if result.get("status") == "not_available":
            console.print(f"[yellow]LIMITATION:[/yellow] {result['message']}")
        else:
            console.print(f"[green]SUCCESS:[/green] Deleted governance domain: {domain_name}")
            console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to delete governance domain: {e}")

@domain.command(help="Search for assets that might be related to governance domains using keywords like 'domain', entity attributes, or collections.")
@click.option("--keywords", help="Search keywords (e.g., 'finance domain', 'hr domain')")
@click.option("--entity-type", help="Entity type to search (e.g., 'DataSet', 'Table')")
@click.option("--collection", help="Search within a specific collection")
@click.option("--limit", type=int, default=25, help="Number of results to return")
def search(keywords, entity_type, collection, limit):
    """Search for assets that might contain domain-related information."""
    try:
        from purviewcli.client._search import Search
        search_client = Search()
        
        # Build search parameters
        search_args = {}
        
        # Build search keywords
        search_terms = []
        if keywords:
            search_terms.append(keywords)
        else:
            # Default domain-related search terms
            search_terms.append("domain governance business")
            
        search_args['--keywords'] = ' '.join(search_terms)
        search_args['--limit'] = limit
        
        # Add filters if specified
        filters = []
        if entity_type:
            filters.append(f'"objectType":"{entity_type}"')
        if collection:
            filters.append(f'"collection":"{collection}"')
            
        if filters:
            # Create a simple filter file content
            filter_content = '{"and":[' + ','.join(['{' + f + '}' for f in filters]) + ']}'
            console.print(f"[cyan]Search filters:[/cyan] {filter_content}")
        
        console.print(f"[cyan]Searching for:[/cyan] {search_args['--keywords']}")
        console.print("[yellow]Note:[/yellow] Looking for assets that might contain domain-related information...")
        
        result = search_client.searchQuery(search_args)
        
        if isinstance(result, dict) and result.get('value'):
            console.print(f"\n[green]Found {len(result['value'])} potential results:[/green]")
            for i, asset in enumerate(result['value'][:10]):  # Show first 10 results
                name = asset.get('name', 'Unknown')
                asset_type = asset.get('assetType', ['Unknown'])[0] if asset.get('assetType') else 'Unknown'
                qualified_name = asset.get('qualifiedName', 'N/A')
                
                console.print(f"\n{i+1}. [bold]{name}[/bold] ({asset_type})")
                console.print(f"   Qualified Name: {qualified_name}")
                
                # Look for domain-related attributes
                if asset.get('description') and 'domain' in asset.get('description', '').lower():
                    console.print(f"   [yellow]Description contains 'domain':[/yellow] {asset.get('description')}")
                
                # Check for custom attributes that might contain domain info
                if asset.get('businessAttributes'):
                    console.print(f"   [cyan]Has business attributes that might contain domain info[/cyan]")
                    
            if len(result['value']) > 10:
                console.print(f"\n[yellow]... and {len(result['value']) - 10} more results[/yellow]")
                
            console.print(f"\n[cyan]Suggestions:[/cyan]")
            console.print("• Look for assets with 'domain' in their description or business attributes")
            console.print("• Use collections to organize assets by business domain")
            console.print("• Consider adding custom entity attributes to track domain association")
            
        else:
            console.print("[yellow]No results found.[/yellow]")
            console.print("\n[cyan]Try instead:[/cyan]")
            console.print("• pvw search query --keywords 'your-domain-name'")
            console.print("• pvw collections list  # to see organizational structure")
            console.print("• pvw entity read --guid <entity-guid>  # to check specific entity attributes")
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to search for domain-related assets: {e}")
        console.print("\n[cyan]Alternative commands:[/cyan]")
        console.print("• pvw search query --keywords 'domain business'")
        console.print("• pvw collections list")
        
@domain.command(name="check-attributes", help="Check existing entity types for domain-related attributes or see how to add domain tracking.")
def check_attributes():
    """Check what domain-related attributes might be available in entity types."""
    try:
        from purviewcli.client._types import Types
        types_client = Types()
        
        console.print("[cyan]Checking for domain-related capabilities...[/cyan]")
        
        # Get entity type definitions to see if any have domain attributes
        args = {'--typeName': 'DataSet'}  # Check common entity type
        result = types_client.typesRead(args)
        
        console.print("\n[green]Current Options for Domain Organization:[/green]")
        console.print("\n1. [bold]Collections[/bold] - Use as domain containers:")
        console.print("   • pvw collections create --collection-name 'finance-domain'")
        console.print("   • pvw collections create --collection-name 'hr-domain'")
        
        console.print("\n2. [bold]Custom Attributes[/bold] - Add domain field to entities:")
        console.print("   • Modify entity definitions to include 'domain' attribute")
        console.print("   • Use business metadata to track domain association")
        
        console.print("\n3. [bold]Glossary Terms[/bold] - Create domain vocabulary:")
        console.print("   • pvw glossary createTerms --name 'Finance Domain'")
        console.print("   • Assign domain terms to relevant assets")
        
        console.print("\n4. [bold]Classifications[/bold] - Tag assets by domain:")
        console.print("   • Create domain-specific classifications")
        console.print("   • Apply to assets for domain grouping")
        
        console.print("\n[yellow]Recommended Approach:[/yellow]")
        console.print("Use collections as your primary domain organization structure:")
        console.print("• Create a collection per business domain")
        console.print("• Move/assign assets to appropriate domain collections")
        console.print("• Use naming conventions like 'finance-domain', 'hr-domain'")
        
    except Exception as e:
        console.print(f"[yellow]INFO:[/yellow] Could not check entity types: {e}")
        console.print("\n[green]Manual Domain Organization Options:[/green]")
        console.print("1. Use collections as domain containers")
        console.print("2. Add custom entity attributes for domain tracking")
        console.print("3. Use glossary terms for domain vocabulary")
        console.print("4. Apply domain-specific classifications")

@domain.command(help="Guide for creating domain-like structures using collections API")
@click.option("--domain-name", help="Suggested name for your domain-like collection")
@click.option("--show-examples", is_flag=True, help="Show detailed examples of domain patterns")
def create_using_collections(domain_name, show_examples):
    """Provides a step-by-step guide to create domain-like structures using collections."""
    try:
        console.print("\n[bold blue][INFO] Creating Domain-like Structures with Microsoft Purview Collections[/bold blue]")
        console.print("\n[yellow]OVERVIEW:[/yellow] Since governance domains are not available in the public API, you can use collections to create hierarchical, domain-like organizational structures.")
        
        console.print("\n[cyan][*]  COLLECTIONS AS DOMAINS - KEY CAPABILITIES:[/cyan]")
        console.print("[OK] [green]Hierarchical Organization:[/green] Create nested collections up to 8 levels deep")
        console.print("[OK] [green]Custom Naming:[/green] Use friendly names (up to 100 chars) and descriptions")
        console.print("[OK] [green]Security Boundaries:[/green] Role-based access control per collection")
        console.print("[OK] [green]Asset Organization:[/green] Group data sources, scans, and assets by business unit")
        console.print("[OK] [green]Metadata Management:[/green] Organize metadata within business contexts")
        
        if domain_name:
            console.print(f"\n[cyan][START] CREATING DOMAIN-LIKE COLLECTION: '{domain_name}'[/cyan]")
            console.print(f"1. [bold]Create top-level collection:[/bold]")
            console.print(f"   pvw collections create --collection-name {domain_name.lower().replace(' ', '-')} --friendly-name \"{domain_name}\" --description \"Top-level domain collection for {domain_name}\"")
            
            console.print(f"\n2. [bold]Create sub-collections (departments/teams):[/bold]")
            console.print(f"   pvw collections create --collection-name {domain_name.lower().replace(' ', '-')}-finance --friendly-name \"{domain_name} Finance\" --parent-collection {domain_name.lower().replace(' ', '-')}")
            console.print(f"   pvw collections create --collection-name {domain_name.lower().replace(' ', '-')}-operations --friendly-name \"{domain_name} Operations\" --parent-collection {domain_name.lower().replace(' ', '-')}")
            
        console.print("\n[cyan][GUIDE] STEP-BY-STEP GUIDE:[/cyan]")
        console.print("1. [bold]Plan Your Hierarchy:[/bold]")
        console.print("   • Design your domain structure (departments, teams, projects)")
        console.print("   • Consider security boundaries and access requirements")
        console.print("   • Maximum 8 levels deep, up to 1000 collections total")
        
        console.print("\n2. [bold]Create Root Domain Collection:[/bold]")
        console.print("   pvw collections create --collection-name my-domain --friendly-name \"My Business Domain\" --description \"Root collection for business domain\"")
        
        console.print("\n3. [bold]Create Department Sub-Collections:[/bold]")
        console.print("   pvw collections create --collection-name my-domain-hr --friendly-name \"Human Resources\" --parent-collection my-domain")
        console.print("   pvw collections create --collection-name my-domain-finance --friendly-name \"Finance Department\" --parent-collection my-domain")
        
        console.print("\n4. [bold]Create Team/Project Collections:[/bold]")
        console.print("   pvw collections create --collection-name my-domain-hr-payroll --friendly-name \"Payroll Team\" --parent-collection my-domain-hr")
        
        if show_examples:
            console.print("\n[cyan][TIP] DOMAIN ORGANIZATION PATTERNS:[/cyan]")
            
            console.print("\n[bold][PATTERN] Pattern 1: Business Unit Domains[/bold]")
            console.print("```")
            console.print("Healthcare-Organization (Root)")
            console.print("├── Hospitals-Domain")
            console.print("│   ├── Emergency-Services")
            console.print("│   ├── Inpatient-Care")
            console.print("│   └── Outpatient-Services")
            console.print("├── Research-Domain")
            console.print("│   ├── Clinical-Trials")
            console.print("│   └── Medical-Research")
            console.print("└── Administration-Domain")
            console.print("    ├── HR-Systems")
            console.print("    └── Finance-Systems")
            console.print("```")
            
            console.print("\n[bold][PATTERN] Pattern 2: Geographic Domains[/bold]")
            console.print("```")
            console.print("Global-Corporation (Root)")
            console.print("├── North-America")
            console.print("│   ├── US-Operations")
            console.print("│   └── Canada-Operations")
            console.print("├── Europe")
            console.print("│   ├── UK-Operations")
            console.print("│   └── Germany-Operations")
            console.print("└── Asia-Pacific")
            console.print("    ├── Japan-Operations")
            console.print("    └── Australia-Operations")
            console.print("```")
            
            console.print("\n[bold][PATTERN] Pattern 3: Lifecycle/Environment Domains[/bold]")
            console.print("```")
            console.print("Data-Platform (Root)")
            console.print("├── Development")
            console.print("│   ├── Raw-Data")
            console.print("│   ├── Processed-Data")
            console.print("│   └── Analytics-Data")
            console.print("├── Staging")
            console.print("│   ├── Raw-Data")
            console.print("│   └── Processed-Data")
            console.print("└── Production")
            console.print("    ├── Raw-Data")
            console.print("    ├── Processed-Data")
            console.print("    └── Analytics-Data")
            console.print("```")
        
        console.print("\n[cyan][SECURITY] ACCESS CONTROL & SECURITY:[/cyan]")
        console.print("• Assign Collection Admin role for domain managers")
        console.print("• Use Data Reader role for read-only access")
        console.print("• Set Data Curator role for metadata management")
        console.print("• Implement least-privilege access model")
        
        console.print("\n[cyan][*]  ADDITIONAL ORGANIZATION METHODS:[/cyan]")
        console.print("• [bold]Custom Attributes:[/bold] Tag assets with domain information")
        console.print("• [bold]Glossary Terms:[/bold] Create domain-specific business vocabularies")
        console.print("• [bold]Classifications:[/bold] Apply domain-based data classifications")
        
        console.print("\n[cyan][COMMANDS] USEFUL COMMANDS:[/cyan]")
        console.print("• List all collections: [bold]pvw collections list[/bold]")
        console.print("• Get collection details: [bold]pvw collections get --collection-name <name>[/bold]")
        console.print("• Search domain assets: [bold]pvw domain search-assets --domain <domain-name>[/bold]")
        console.print("• Check organization options: [bold]pvw domain check-attributes[/bold]")
        
        console.print("\n[green][OK] NEXT STEPS:[/green]")
        console.print("1. Plan your domain hierarchy based on your organization structure")
        console.print("2. Create your root domain collection")
        console.print("3. Add department and team sub-collections")
        console.print("4. Set up appropriate access controls")
        console.print("5. Register data sources under appropriate collections")
        
    except Exception as e:
        console.print(f"[red]ERROR:[/red] Failed to generate domain creation guide: {e}")
