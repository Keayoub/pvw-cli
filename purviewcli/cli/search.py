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
    count = data.get("@search.count", 0)
    items = data.get("value", [])

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
        if "collection" in item and item["collection"]:
            collection_name = item["collection"].get("name", "N/A")
        else:
            collection_name = item.get("collectionId", "N/A")
        details.append(f"[bold blue]Collection:[/bold blue] {collection_name}")

        # Qualified Name
        details.append(
            f"[bold white]Qualified Name:[/bold white] {item.get('qualifiedName', 'N/A')}"
        )

        # Classifications
        if "classification" in item and item["classification"]:
            classifications = []
            for cls in item["classification"]:
                if isinstance(cls, dict):
                    classifications.append(cls.get("typeName", str(cls)))
                else:
                    classifications.append(str(cls))
            details.append(
                f"[bold magenta]Classifications:[/bold magenta] {', '.join(classifications)}"
            )

        # Additional metadata
        if "updateTime" in item:
            details.append(f"[bold dim]Last Updated:[/bold dim] {item.get('updateTime')}")
        if "createTime" in item:
            details.append(f"[bold dim]Created:[/bold dim] {item.get('createTime')}")
        if "updateBy" in item:
            details.append(f"[bold dim]Updated By:[/bold dim] {item.get('updateBy')}")

        # Search score
        if "@search.score" in item:
            details.append(f"[bold dim]Search Score:[/bold dim] {item.get('@search.score'):.2f}")

        # Create panel
        panel_content = "\n".join(details)
        panel = Panel(
            panel_content,
            title=f"[bold]{i}. {item.get('name', 'Unknown')}[/bold]",
            border_style="blue",
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
    count = data.get("@search.count", 0)
    items = data.get("value", [])

    if not items:
        console.print("[yellow]No results found[/yellow]")
        return

    # Create table
    table = Table(title=f"Search Results ({len(items)} of {count} total)")
    table.add_column("Name", style="cyan", min_width=15, max_width=40)
    table.add_column("Type", style="green", min_width=15, max_width=25)
    table.add_column("ID", style="yellow", min_width=36, max_width=36)
    table.add_column("Collection", style="blue", min_width=12, max_width=30)

    for item in items:
        # Extract entity information
        name = item.get("name", "N/A")
        entity_type = item.get("entityType", "N/A")
        entity_id = item.get("id", "N/A")

        # Handle collection - try multiple sources
        collection = "N/A"
        if "collection" in item and item["collection"]:
            if isinstance(item["collection"], dict):
                collection = item["collection"].get("name", "N/A")
            else:
                collection = str(item["collection"])
        elif "collectionId" in item and item["collectionId"]:
            collection = item.get("collectionId", "N/A")
        elif "assetName" in item and item["assetName"]:
            # Try to extract collection from asset name
            asset_name = item.get("assetName", "")
            if asset_name and asset_name != "N/A":
                collection = asset_name

        # Build row data with ID always shown
        row_data = [name, entity_type, entity_id, collection]

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
    show_ids = kwargs.pop("show_ids", False)
    output_json = kwargs.pop("output_json", False)
    detailed = kwargs.pop("detailed", False)

    args = {f"--{k}": v for k, v in kwargs.items() if v is not None}
    try:
        result = method(args)
        # Choose output format
        if output_json:
            _format_json_output(result)
        elif detailed and method_name in [
            "searchQuery",
            "searchBrowse",
            "searchSuggest",
            "searchAutocomplete",
            "searchFaceted",
        ]:
            _format_detailed_output(result)
        elif method_name in [
            "searchQuery",
            "searchBrowse",
            "searchSuggest",
            "searchAutocomplete",
            "searchFaceted",
        ]:
            _format_search_results(result, show_ids=show_ids)
        else:
            _format_json_output(result)
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@search.command()
@click.option("--keywords", required=False)
@click.option("--limit", required=False, type=int, default=25)
@click.option("--filterFile", required=False, type=click.Path(exists=True))
@click.option("--json", "output_json", is_flag=True, help="Show full JSON details instead of table")
def autocomplete(keywords, limit, filterfile, output_json):
    """Autocomplete search suggestions"""
    _invoke_search_method(
        "searchAutocomplete",
        keywords=keywords,
        limit=limit,
        filterFile=filterfile,
        output_json=output_json,
    )


@search.command()
@click.option("--entityType", required=False)
@click.option("--path", required=False)
@click.option("--limit", required=False, type=int, default=25)
@click.option("--offset", required=False, type=int, default=0)
@click.option("--json", "output_json", is_flag=True, help="Show full JSON details instead of table")
def browse(entitytype, path, limit, offset, output_json):
    """Browse entities by type or path"""
    _invoke_search_method(
        "searchBrowse",
        entityType=entitytype,
        path=path,
        limit=limit,
        offset=offset,
        output_json=output_json,
    )


@search.command()
@click.option("--keywords", required=False)
@click.option("--limit", required=False, type=int, default=25)
@click.option("--offset", required=False, type=int, default=0)
@click.option("--filterFile", required=False, type=click.Path(exists=True))
@click.option("--facets-file", required=False, type=click.Path(exists=True))
@click.option("--show-ids", is_flag=True, help="Show entity IDs in the results")
@click.option("--json", "output_json", is_flag=True, help="Show full JSON details instead of table")
@click.option("--detailed", is_flag=True, help="Show detailed information in readable format")
def query(keywords, limit, offset, filterfile, facets_file, show_ids, output_json, detailed):
    """Run a search query"""
    _invoke_search_method(
        "searchQuery",
        keywords=keywords,
        limit=limit,
        offset=offset,
        filterFile=filterfile,
        facets_file=facets_file,
        show_ids=show_ids,
        output_json=output_json,
        detailed=detailed,
    )


@search.command()
@click.option("--keywords", required=False)
@click.option("--limit", required=False, type=int, default=25)
@click.option("--filterFile", required=False, type=click.Path(exists=True))
@click.option("--json", "output_json", is_flag=True, help="Show full JSON details instead of table")
def suggest(keywords, limit, filterfile, output_json):
    """Get search suggestions"""
    _invoke_search_method(
        "searchSuggest",
        keywords=keywords,
        limit=limit,
        filterFile=filterfile,
        output_json=output_json,
    )


@search.command()
@click.option("--keywords", required=False)
@click.option("--limit", required=False, type=int, default=25)
@click.option("--offset", required=False, type=int, default=0)
@click.option("--filterFile", required=False, type=click.Path(exists=True))
@click.option("--facets-file", required=False, type=click.Path(exists=True))
@click.option(
    "--facetFields",
    required=False,
    help="Comma-separated facet fields (e.g., objectType,classification)",
)
@click.option("--facetCount", required=False, type=int, help="Facet count per field")
@click.option("--facetSort", required=False, type=str, help="Facet sort order (e.g., count, value)")
def faceted(keywords, limit, offset, filterfile, facets_file, facetfields, facetcount, facetsort):
    """Run a faceted search"""
    _invoke_search_method(
        "searchFaceted",
        keywords=keywords,
        limit=limit,
        offset=offset,
        filterFile=filterfile,
        facets_file=facets_file,
        facetFields=facetfields,
        facetCount=facetcount,
        facetSort=facetsort,
    )


@search.command()
@click.option("--keywords", required=False)
@click.option("--limit", required=False, type=int, default=25)
@click.option("--offset", required=False, type=int, default=0)
@click.option("--filterFile", required=False, type=click.Path(exists=True))
@click.option("--facets-file", required=False, type=click.Path(exists=True))
@click.option(
    "--businessMetadata",
    required=False,
    type=click.Path(exists=True),
    help="Path to business metadata JSON file",
)
@click.option("--classifications", required=False, help="Comma-separated classifications")
@click.option("--termAssignments", required=False, help="Comma-separated term assignments")
def advanced(
    keywords,
    limit,
    offset,
    filterfile,
    facets_file,
    businessmetadata,
    classifications,
    termassignments,
):
    """Run an advanced search query"""
    # Load business metadata JSON if provided
    business_metadata_content = None
    if businessmetadata:
        import json

        with open(businessmetadata, "r", encoding="utf-8") as f:
            business_metadata_content = json.load(f)
    _invoke_search_method(
        "searchAdvanced",
        keywords=keywords,
        limit=limit,
        offset=offset,
        filterFile=filterfile,
        facets_file=facets_file,
        businessMetadata=business_metadata_content,
        classifications=classifications,
        termAssignments=termassignments,
    )


@search.command("find-table")
@click.option("--name", required=False, help="Table name (exact or pattern with *)")
@click.option("--schema", required=False, help="Schema name (e.g., SalesLT, dbo)")
@click.option("--database", required=False, help="Database name (e.g., Adventureworks, pgisCBL)")
@click.option(
    "--server", required=False, help="Server name (e.g., fabricdemos001.database.windows.net)"
)
@click.option("--entity-type", required=False, help="Entity type filter (default: all table types)")
@click.option(
    "--tables-only",
    is_flag=True,
    default=True,
    help="Exclude views, schemas, and stored procedures (default: True)",
)
@click.option(
    "--limit",
    required=False,
    type=int,
    default=1000,
    help="Maximum number of results (default: 1000)",
)
@click.option("--show-ids", is_flag=True, help="Show entity IDs in the results")
@click.option("--json", "output_json", is_flag=True, help="Show full JSON details")
@click.option("--id-only", is_flag=True, help="Output only GUIDs for scripting")
def find_table(
    name, schema, database, server, entity_type, tables_only, limit, show_ids, output_json, id_only
):
    """Find tables by name, schema, database using advanced search with filters.

    Uses Purview's advanced search API for reliable results with high limits.
    Perfect for getting table GUIDs and finding all tables in a schema/database.

    \b
    EXAMPLES:
      # Get all tables in a specific schema/database
      pvw search find-table --schema dbo --database pgisCBL
      pvw search find-table --schema SalesLT --database Adventureworks

      # Find a specific table
      pvw search find-table --name Address --schema SalesLT --database Adventureworks

      # Include views and stored procedures
      pvw search find-table --schema dbo --database pgisCBL --no-tables-only

      # Filter by specific entity type
      pvw search find-table --schema dbo --database pgisCBL --entity-type mssql_table

      # Get GUIDs for scripting
      pvw search find-table --schema dbo --database pgisCBL --id-only

    \b
    USE IN SCRIPTS (PowerShell):
      $guid = pvw search find-table --name Address --schema SalesLT --database Adventureworks --id-only
      pvw entity update --guid $guid --payload update.json

      $guids = pvw search find-table --schema SalesLT --database Adventureworks --id-only
      foreach ($guid in $guids) { pvw entity update --guid $guid --payload update.json }
    """
    from purviewcli.client._search import Search
    import tempfile
    import json
    import os

    search_client = Search()

    # Validate input
    if not name and not schema and not database:
        console.print("[red]ERROR:[/red] You must provide at least --name, --schema, or --database")
        return

    # Build search filter object
    filter_obj = {}
    and_filters = []
    or_filters = []

    # Entity type filter - default to table types if tables_only is True
    if tables_only and not entity_type:
        # Include all table types but exclude views, schemas, stored procs
        table_types = [
            "azure_sql_table",
            "mssql_table",
            "azure_datalake_gen2_resource_set",
            "azure_datalake_gen2_path",
            "fabric_lakehouse_table",
        ]
        or_filters.append({"or": [{"entityType": t} for t in table_types]})
    elif entity_type:
        and_filters.append({"entityType": entity_type})

    # Build qualified name pattern for filtering
    qn_patterns = []

    if database and schema:
        # Most specific: database/schema pattern
        qn_patterns.append(f"*/{database}/{schema}/*")
        qn_patterns.append(f"*{database}*{schema}*")
    elif database:
        qn_patterns.append(f"*/{database}/*")
        qn_patterns.append(f"*{database}*")
    elif schema:
        qn_patterns.append(f"*/{schema}/*")
        qn_patterns.append(f"*{schema}*")

    # Use multiple search strategies and combine results
    all_results = []
    seen_ids = set()

    # Strategy 1: Use keywords with filters
    keywords_to_try = []
    if name:
        keywords_to_try.append(name)
    if schema:
        keywords_to_try.append(schema)
    if database:
        keywords_to_try.append(database)

    if not keywords_to_try:
        keywords_to_try.append("*")

    for keyword in keywords_to_try:
        try:
            # Prepare filter file
            temp_filter_file = None
            if and_filters or or_filters:
                combined_filter = {}
                if and_filters and or_filters:
                    combined_filter["and"] = and_filters + or_filters
                elif and_filters:
                    combined_filter["and"] = and_filters
                elif or_filters:
                    if len(or_filters) == 1 and "or" in or_filters[0]:
                        combined_filter = or_filters[0]
                    else:
                        combined_filter["or"] = or_filters

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False, encoding="utf-8"
                ) as f:
                    json.dump(combined_filter, f)
                    temp_filter_file = f.name

            # Execute search
            args = {"--keywords": keyword, "--limit": limit, "--offset": 0}

            if temp_filter_file:
                args["--filterFile"] = temp_filter_file

            result = search_client.searchQuery(args)

            # Clean up temp file
            if temp_filter_file:
                os.unlink(temp_filter_file)

            if result and "value" in result:
                for item in result["value"]:
                    item_id = item.get("id")
                    if item_id and item_id not in seen_ids:
                        item_qn = item.get("qualifiedName", "").lower()
                        item_name = item.get("name", "").lower()

                        # Apply additional filtering based on criteria (case-insensitive)
                        matches = True

                        # Filter by name if specified (case-insensitive)
                        if name and name.lower() not in item_name.lower():
                            matches = False

                        # Filter by schema (case-insensitive)
                        if schema and schema.lower() not in item_qn.lower():
                            matches = False

                        # Filter by database (case-insensitive)
                        if database and database.lower() not in item_qn.lower():
                            matches = False

                        # Filter by server (case-insensitive)
                        if server and server.lower() not in item_qn.lower():
                            matches = False

                        if matches:
                            seen_ids.add(item_id)
                            all_results.append(item)

        except Exception as e:
            console.print(f"[yellow]Warning: Search with keyword '{keyword}' failed: {e}[/yellow]")
            continue

    # Check if we have results
    if not all_results:
        console.print(f"[yellow]No results found[/yellow]")
        if database and schema:
            console.print(f"[dim]Searched for: database={database}, schema={schema}[/dim]")
        return

    # Sort results by name
    all_results.sort(key=lambda x: x.get("name", ""))

    # Display warning if we hit the limit
    if len(all_results) >= limit * 0.9:  # 90% of limit
        console.print(
            f"[yellow]WARNING: Found {len(all_results)} results, approaching limit ({limit})[/yellow]"
        )
        console.print(f"[yellow]Consider increasing --limit if you expect more results[/yellow]\n")

    # Format results
    result_obj = {"value": all_results, "@search.count": len(all_results)}

    # Display results
    if id_only:
        for item in all_results:
            print(item.get("id", ""))
    elif output_json:
        _format_json_output(result_obj)
    else:
        _format_search_results(result_obj, show_ids=show_ids)


__all__ = ["search"]
