"""
usage: 
    pvw search autoComplete [--keywords=<val> --limit=<val> --filterFile=<val>]
    pvw search browse  (--entityType=<val> | --path=<val>) [--limit=<val> --offset=<val>]
    pvw search query [--keywords=<val> --limit=<val> --offset=<val> --filterFile=<val> --facets-file=<val>]
    pvw search suggest [--keywords=<val> --limit=<val> --filterFile=<val>]

options:
  --purviewName=<val>     [string]  Microsoft Purview account name.
  --keywords=<val>        [string]  The keywords applied to all searchable fields.
  --entityType=<val>      [string]  The entity type to browse as the root level entry point.
  --path=<val>            [string]  The path to browse the next level child entities.
  --limit=<val>           [integer] By default there is no paging [default: 25].
  --offset=<val>          [integer] Offset for pagination purpose [default: 0].
  --filterFile=<val>      [string]  File path to a filter json file.
  --facets-file=<val>     [string]  File path to a facets json file.

"""
# Search CLI for Purview Data Map API (Atlas v2)
"""
CLI for advanced search and discovery
"""
import click
import json
from rich.console import Console
from rich.table import Table
from purviewcli.client._search import Search

console = Console()

@click.group()
def search():
    """Search and discover assets"""
    pass

def _format_json_output(data):
    """Format JSON output with syntax highlighting using Rich"""
    from rich.console import Console
    from rich.syntax import Syntax
    import json
    
    console = Console()
    
    # Pretty print JSON with syntax highlighting
    json_str = json.dumps(data, indent=2)
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(syntax)

def _format_detailed_output(data):
    """Format search results with detailed information in readable format"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    
    console = Console()
    
    # Extract results data
    count = data.get('@search.count', 0)
    items = data.get('value', [])
    
    if not items:
        console.print("[yellow]No results found[/yellow]")
        return
    
    console.print(f"\n[bold cyan]Search Results: {len(items)} of {count} total[/bold cyan]\n")
    
    for i, item in enumerate(items, 1):
        # Create a panel for each result
        details = []
        
        # Basic information
        details.append(f"[bold cyan]Name:[/bold cyan] {item.get('name', 'N/A')}")
        details.append(f"[bold green]Type:[/bold green] {item.get('entityType', 'N/A')}")
        details.append(f"[bold yellow]ID:[/bold yellow] {item.get('id', 'N/A')}")
        
        # Collection
        if 'collection' in item and item['collection']:
            collection_name = item['collection'].get('name', 'N/A')
        else:
            collection_name = item.get('collectionId', 'N/A')
        details.append(f"[bold blue]Collection:[/bold blue] {collection_name}")
        
        # Qualified Name
        details.append(f"[bold white]Qualified Name:[/bold white] {item.get('qualifiedName', 'N/A')}")
        
        # Classifications
        if 'classification' in item and item['classification']:
            classifications = []
            for cls in item['classification']:
                if isinstance(cls, dict):
                    classifications.append(cls.get('typeName', str(cls)))
                else:
                    classifications.append(str(cls))
            details.append(f"[bold magenta]Classifications:[/bold magenta] {', '.join(classifications)}")
        
        # Additional metadata
        if 'updateTime' in item:
            details.append(f"[bold dim]Last Updated:[/bold dim] {item.get('updateTime')}")
        if 'createTime' in item:
            details.append(f"[bold dim]Created:[/bold dim] {item.get('createTime')}")
        if 'updateBy' in item:
            details.append(f"[bold dim]Updated By:[/bold dim] {item.get('updateBy')}")
        
        # Search score
        if '@search.score' in item:
            details.append(f"[bold dim]Search Score:[/bold dim] {item.get('@search.score'):.2f}")
        
        # Create panel
        panel_content = "\n".join(details)
        panel = Panel(
            panel_content,
            title=f"[bold]{i}. {item.get('name', 'Unknown')}[/bold]",
            border_style="blue"
        )
        console.print(panel)
    
    # Add pagination hint if there are more results
    if len(items) < count:
        console.print(f"\n💡 [dim]More results available. Use --offset to paginate.[/dim]")
    
    return

def _format_search_results(data, show_ids=False):
    """Format search results as a nice table using Rich"""
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    # Extract results data
    count = data.get('@search.count', 0)
    items = data.get('value', [])
    
    if not items:
        console.print("[yellow]No results found[/yellow]")
        return
    
    # Create table
    table = Table(title=f"Search Results ({len(items)} of {count} total)")
    table.add_column("Name", style="cyan", min_width=15, max_width=25)
    table.add_column("Type", style="green", min_width=15, max_width=20)
    table.add_column("Collection", style="blue", min_width=12, max_width=20)
    table.add_column("Classifications", style="magenta", min_width=15, max_width=30)
    
    if show_ids:
        table.add_column("ID", style="yellow", min_width=36, max_width=36)
    
    table.add_column("Qualified Name", style="white", min_width=30)
    
    for item in items:
        # Extract entity information
        name = item.get('name', 'N/A')
        entity_type = item.get('entityType', 'N/A')
        entity_id = item.get('id', 'N/A')
        qualified_name = item.get('qualifiedName', 'N/A')
        
        # Truncate long qualified names for better display
        if len(qualified_name) > 60:
            qualified_name = qualified_name[:57] + "..."
        
        # Handle collection
        collection = 'N/A'
        if 'collection' in item and item['collection']:
            collection = item['collection'].get('name', 'N/A')
        
        # Handle classifications - truncate long classification lists
        classifications = []
        if 'classification' in item and item['classification']:
            for cls in item['classification']:
                if isinstance(cls, dict):
                    cls_name = cls.get('typeName', str(cls))
                    # Simplify Microsoft classifications for display
                    if cls_name.startswith('MICROSOFT.'):
                        cls_name = cls_name.replace('MICROSOFT.', 'MS.')
                    classifications.append(cls_name)
                else:
                    classifications.append(str(cls))
        
        # Truncate classifications if too long
        cls_display = ", ".join(classifications) if classifications else ""
        if len(cls_display) > 40:
            cls_display = cls_display[:37] + "..."
        
        # Build row data
        row_data = [name, entity_type, collection, cls_display]
        if show_ids:
            row_data.append(entity_id)
        row_data.append(qualified_name)
        
        # Add row to table
        table.add_row(*row_data)
    
    # Print the table
    console.print(table)
    
    # Add pagination hint if there are more results
    if len(items) < count:
        console.print(f"\n💡 More results available. Use --offset to paginate.")
    
    return

def _invoke_search_method(method_name, **kwargs):
    search_client = Search()
    method = getattr(search_client, method_name)
    
    # Extract formatting options, don't pass to API
    show_ids = kwargs.pop('show_ids', False)
    output_json = kwargs.pop('output_json', False)
    detailed = kwargs.pop('detailed', False)
    
    args = {f'--{k}': v for k, v in kwargs.items() if v is not None}
    try:
        result = method(args)
        # Choose output format
        if output_json:
            _format_json_output(result)
        elif detailed and method_name in ['searchQuery', 'searchBrowse', 'searchSuggest', 'searchAutoComplete']:
            _format_detailed_output(result)
        elif method_name in ['searchQuery', 'searchBrowse', 'searchSuggest', 'searchAutoComplete']:
            _format_search_results(result, show_ids=show_ids)
        else:
            _format_json_output(result)
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")

@search.command()
@click.option('--keywords', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--filterFile', required=False, type=click.Path(exists=True))
@click.option('--json', 'output_json', is_flag=True, help='Show full JSON details instead of table')
def autocomplete(keywords, limit, filterfile, output_json):
    """Autocomplete search suggestions"""
    _invoke_search_method('searchAutoComplete', keywords=keywords, limit=limit, filterFile=filterfile, output_json=output_json)

@search.command()
@click.option('--entityType', required=False)
@click.option('--path', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--offset', required=False, type=int, default=0)
@click.option('--json', 'output_json', is_flag=True, help='Show full JSON details instead of table')
def browse(entitytype, path, limit, offset, output_json):
    """Browse entities by type or path"""
    _invoke_search_method('searchBrowse', entityType=entitytype, path=path, limit=limit, offset=offset, output_json=output_json)

@search.command()
@click.option('--keywords', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--offset', required=False, type=int, default=0)
@click.option('--filterFile', required=False, type=click.Path(exists=True))
@click.option('--facets-file', required=False, type=click.Path(exists=True))
@click.option('--show-ids', is_flag=True, help='Show entity IDs in the results')
@click.option('--json', 'output_json', is_flag=True, help='Show full JSON details instead of table')
@click.option('--detailed', is_flag=True, help='Show detailed information in readable format')
def query(keywords, limit, offset, filterfile, facets_file, show_ids, output_json, detailed):
    """Run a search query"""
    _invoke_search_method('searchQuery', keywords=keywords, limit=limit, offset=offset, filterFile=filterfile, facets_file=facets_file, show_ids=show_ids, output_json=output_json, detailed=detailed)

@search.command()
@click.option('--keywords', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--filterFile', required=False, type=click.Path(exists=True))
@click.option('--json', 'output_json', is_flag=True, help='Show full JSON details instead of table')
def suggest(keywords, limit, filterfile, output_json):
    """Get search suggestions"""
    _invoke_search_method('searchSuggest', keywords=keywords, limit=limit, filterFile=filterfile, output_json=output_json)

@search.command()
@click.option('--keywords', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--offset', required=False, type=int, default=0)
@click.option('--filterFile', required=False, type=click.Path(exists=True))
@click.option('--facets-file', required=False, type=click.Path(exists=True))
@click.option('--facetFields', required=False, help='Comma-separated facet fields (e.g., objectType,classification)')
@click.option('--facetCount', required=False, type=int, help='Facet count per field')
@click.option('--facetSort', required=False, type=str, help='Facet sort order (e.g., count, value)')
def faceted(keywords, limit, offset, filterfile, facets_file, facetfields, facetcount, facetsort):
    """Run a faceted search"""
    _invoke_search_method(
        'searchFaceted',
        keywords=keywords,
        limit=limit,
        offset=offset,
        filterFile=filterfile,
        facets_file=facets_file,
        facetFields=facetfields,
        facetCount=facetcount,
        facetSort=facetsort
    )

@search.command()
@click.option('--keywords', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--offset', required=False, type=int, default=0)
@click.option('--filterFile', required=False, type=click.Path(exists=True))
@click.option('--facets-file', required=False, type=click.Path(exists=True))
@click.option('--businessMetadata', required=False, type=click.Path(exists=True), help='Path to business metadata JSON file')
@click.option('--classifications', required=False, help='Comma-separated classifications')
@click.option('--termAssignments', required=False, help='Comma-separated term assignments')
def advanced(keywords, limit, offset, filterfile, facets_file, businessmetadata, classifications, termassignments):
    """Run an advanced search query"""
    # Load business metadata JSON if provided
    business_metadata_content = None
    if businessmetadata:
        import json
        with open(businessmetadata, 'r', encoding='utf-8') as f:
            business_metadata_content = json.load(f)
    _invoke_search_method(
        'searchAdvancedQuery',
        keywords=keywords,
        limit=limit,
        offset=offset,
        filterFile=filterfile,
        facets_file=facets_file,
        businessMetadata=business_metadata_content,
        classifications=classifications,
        termAssignments=termassignments
    )

__all__ = ['search']
