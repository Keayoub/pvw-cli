"""
Manage Purview glossaries, categories, and terms using modular Click-based commands.

Usage:
  glossary create                  Create a new glossary
  glossary create-categories       Create multiple glossary categories
  glossary create-category         Create a glossary category
  glossary create-term             Create a glossary term
  glossary create-terms            Create multiple glossary terms
  glossary delete                  Delete a glossary
  glossary delete-category         Delete a glossary category
  glossary delete-term             Delete a glossary term
  glossary put                     Update a glossary
  glossary put-category            Update a glossary category
  glossary put-term                Update a glossary term
  glossary read or list            Read glossaries
  glossary read-categories         Read glossary categories
  glossary read-category           Read a glossary category
  glossary read-term               Read a glossary term
  glossary read-terms              Read all terms in a glossary
  glossary list-terms              List all terms in a glossary (alias)
  glossary --help                  Show this help message and exit

Options:
  -h --help                        Show this help message and exit
"""
import click
import json
from rich.console import Console
from purviewcli.client._glossary import Glossary

console = Console()

@click.group()
def glossary():
    """Manage Purview glossaries, categories, and terms
    """
    pass

# === CREATE OPERATIONS ===

@glossary.command()
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with glossary data')
def create(payload_file):
    """Create a new glossary"""
    try:
        client = Glossary()
        args = {'--payloadFile': payload_file}
        result = client.glossaryCreate(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with categories data')
def create_categories(payload_file):
    """Create multiple glossary categories"""
    try:
        client = Glossary()
        args = {'--payloadFile': payload_file}
        result = client.glossaryCreateCategories(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with category data')
def create_category(payload_file):
    """Create a single glossary category"""
    try:
        client = Glossary()
        args = {'--payloadFile': payload_file}
        result = client.glossaryCreateCategory(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with term data')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in creation')
def create_term(payload_file, include_term_hierarchy):
    """Create a single glossary term"""
    try:
        client = Glossary()
        args = {'--payloadFile': payload_file, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryCreateTerm(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with terms data')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in creation')
def create_terms(payload_file, include_term_hierarchy):
    """Create multiple glossary terms"""
    try:
        client = Glossary()
        args = {'--payloadFile': payload_file, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryCreateTerms(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

# === DELETE OPERATIONS ===

@glossary.command()
@click.option('--glossary-guid', required=True, help='The globally unique identifier for glossary')
def delete(glossary_guid):
    """Delete a glossary"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid}
        result = client.glossaryDelete(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--category-guid', required=True, help='The globally unique identifier of the category')
def delete_category(category_guid):
    """Delete a glossary category"""
    try:
        client = Glossary()
        args = {'--categoryGuid': category_guid}
        result = client.glossaryDeleteCategory(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--term-guid', required=True, help='The globally unique identifier for glossary term')
def delete_term(term_guid):
    """Delete a glossary term"""
    try:
        client = Glossary()
        args = {'--termGuid': term_guid}
        result = client.glossaryDeleteTerm(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

# === PUT OPERATIONS ===

@glossary.command()
@click.option('--glossary-guid', required=True, help='The globally unique identifier for glossary')
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with updated glossary data')
def put(glossary_guid, payload_file):
    """Update a glossary"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid, '--payloadFile': payload_file}
        result = client.glossaryPut(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--category-guid', required=True, help='The globally unique identifier of the category')
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with updated category data')
def put_category(category_guid, payload_file):
    """Update a glossary category"""
    try:
        client = Glossary()
        args = {'--categoryGuid': category_guid, '--payloadFile': payload_file}
        result = client.glossaryPutCategory(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--category-guid', required=True, help='The globally unique identifier of the category')
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with partial updated category data')
def put_category_partial(category_guid, payload_file):
    """Partially update a glossary category"""
    try:
        client = Glossary()
        args = {'--categoryGuid': category_guid, '--payloadFile': payload_file}
        result = client.glossaryPutCategoryPartial(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--glossary-guid', required=True, help='The globally unique identifier for glossary')
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with partial updated glossary data')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in update')
def put_partial(glossary_guid, payload_file, include_term_hierarchy):
    """Partially update a glossary"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid, '--payloadFile': payload_file, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryPutPartial(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--term-guid', required=True, help='The globally unique identifier for glossary term')
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with updated term data')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in update')
def put_term(term_guid, payload_file, include_term_hierarchy):
    """Update a glossary term"""
    try:
        client = Glossary()
        args = {'--termGuid': term_guid, '--payloadFile': payload_file, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryPutTerm(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--term-guid', required=True, help='The globally unique identifier for glossary term')
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with partial updated term data')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in update')
def put_term_partial(term_guid, payload_file, include_term_hierarchy):
    """Partially update a glossary term"""
    try:
        client = Glossary()
        args = {'--termGuid': term_guid, '--payloadFile': payload_file, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryPutTermPartial(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--term-guid', required=True, help='The globally unique identifier for glossary term')
@click.option('--payload-file', required=True, type=click.Path(exists=True), help='Path to JSON file with terms assigned entities data')
def put_terms_assigned_entities(term_guid, payload_file):
    """Assign entities to a glossary term"""
    try:
        client = Glossary()
        args = {'--termGuid': term_guid, '--payloadFile': payload_file}
        result = client.glossaryPutTermsAssignedEntities(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

# === READ OPERATIONS ===


def _read_glossaries_impl(glossary_guid, limit, offset, sort, ignore_terms_and_categories):
    try:
        client = Glossary()
        args = {
            '--glossaryGuid': glossary_guid,
            '--limit': limit,
            '--offset': offset,
            '--sort': sort,
            '--ignoreTermsAndCategories': ignore_terms_and_categories
        }
        result = client.glossaryRead(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command(name="read", help="Read glossaries and list all glossaries")
@click.option("--glossary-guid", help="The globally unique identifier for glossary")
@click.option("--limit", type=int, default=1000, help="The page size - by default there is no paging")
@click.option("--offset", type=int, default=0, help="Offset for pagination purpose")
@click.option("--sort", default="ASC", help="Sort order: ASC or DESC")
@click.option("--ignore-terms-and-categories", is_flag=True, help="Whether to ignore terms and categories")
def read(glossary_guid, limit, offset, sort, ignore_terms_and_categories):
    """Read glossaries"""
    _read_glossaries_impl(glossary_guid, limit, offset, sort, ignore_terms_and_categories)

@glossary.command(name="list", help="List all glossaries")
@click.option("--limit", type=int, default=1000, help="The page size - by default there is no paging")
@click.option("--offset", type=int, default=0, help="Offset for pagination purpose")
@click.option("--sort", default="ASC", help="Sort order: ASC or DESC")
@click.option("--ignore-terms-and-categories", is_flag=True, help="Whether to ignore terms and categories")
def list_glossaries(limit, offset, sort, ignore_terms_and_categories):
    """List all glossaries (alias for 'read')"""
    _read_glossaries_impl('', limit, offset, sort, ignore_terms_and_categories)


@glossary.command()
@click.option('--glossary-guid', help='The globally unique identifier for glossary')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
def read_categories(glossary_guid, limit, offset, sort):
    """Read glossary categories"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid, '--limit': limit, '--offset': offset, '--sort': sort}
        result = client.glossaryReadCategories(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--glossary-guid', help='The globally unique identifier for glossary')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
def read_categories_headers(glossary_guid, limit, offset, sort):
    """Read glossary categories headers"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid, '--limit': limit, '--offset': offset, '--sort': sort}
        result = client.glossaryReadCategoriesHeaders(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--category-guid', help='The globally unique identifier of the category')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
def read_category(category_guid, limit, offset, sort):
    """Read a glossary category"""
    try:
        client = Glossary()
        args = {'--categoryGuid': category_guid, '--limit': limit, '--offset': offset, '--sort': sort}
        result = client.glossaryReadCategory(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--category-guid', help='The globally unique identifier of the category')
def read_category_related(category_guid):
    """Read related terms of a glossary category"""
    try:
        client = Glossary()
        args = {'--categoryGuid': category_guid}
        result = client.glossaryReadCategoryRelated(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--category-guid', help='The globally unique identifier of the category')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
def read_category_terms(category_guid, limit, offset, sort):
    """Read terms of a glossary category"""
    try:
        client = Glossary()
        args = {'--categoryGuid': category_guid, '--limit': limit, '--offset': offset, '--sort': sort}
        result = client.glossaryReadCategoryTerms(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--glossary-guid', help='The globally unique identifier for glossary')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in retrieval')
def read_detailed(glossary_guid, include_term_hierarchy):
    """Read detailed information of a glossary"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryReadDetailed(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--term-guid', help='The globally unique identifier for glossary term')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in retrieval')
def read_term(term_guid, include_term_hierarchy):
    """Read a glossary term"""
    try:
        client = Glossary()
        args = {'--termGuid': term_guid, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryReadTerm(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--glossary-guid', help='The globally unique identifier for glossary')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
@click.option('--ext-info', is_flag=True, help='Include extended information')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in retrieval')
def read_terms(glossary_guid, limit, offset, sort, ext_info, include_term_hierarchy):
    """Read glossary terms"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid, '--limit': limit, '--offset': offset, '--sort': sort, '--extInfo': ext_info, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryReadTerms(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command(name="list-terms", help="List all terms in a glossary (alias for read-terms)")
@click.option('--glossary-guid', help='The globally unique identifier for glossary')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
@click.option('--ext-info', is_flag=True, help='Include extended information')
@click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy in retrieval')
def list_terms(glossary_guid, limit, offset, sort, ext_info, include_term_hierarchy):
    """List all terms in a glossary (user-friendly alias for read-terms)"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid, '--limit': limit, '--offset': offset, '--sort': sort, '--extInfo': ext_info, '--includeTermHierarchy': include_term_hierarchy}
        result = client.glossaryReadTerms(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--term-guid', help='The globally unique identifier for glossary term')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
def read_terms_assigned_entities(term_guid, limit, offset, sort):
    """Read assigned entities of a glossary term"""
    try:
        client = Glossary()
        args = {'--termGuid': term_guid, '--limit': limit, '--offset': offset, '--sort': sort}
        result = client.glossaryReadTermsAssignedEntities(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--glossary-guid', help='The globally unique identifier for glossary')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
def read_terms_headers(glossary_guid, limit, offset, sort):
    """Read glossary terms headers"""
    try:
        client = Glossary()
        args = {'--glossaryGuid': glossary_guid, '--limit': limit, '--offset': offset, '--sort': sort}
        result = client.glossaryReadTermsHeaders(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--operation-guid', help='The globally unique identifier for async operation/job')
def read_terms_import(operation_guid):
    """Read the result of a terms import operation"""
    try:
        client = Glossary()
        args = {'--operationGuid': operation_guid}
        result = client.glossaryReadTermsImport(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command()
@click.option('--term-guid', help='The globally unique identifier for glossary term')
@click.option('--limit', type=int, default=1000, help='The page size - by default there is no paging')
@click.option('--offset', type=int, default=0, help='Offset for pagination purpose')
@click.option('--sort', default='ASC', help='Sort order: ASC or DESC')
def read_terms_related(term_guid, limit, offset, sort):
    """Read related terms of a glossary term"""
    try:
        client = Glossary()
        args = {'--termGuid': term_guid, '--limit': limit, '--offset': offset, '--sort': sort}
        result = client.glossaryReadTermsRelated(args)
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red][X] Error: {e}[/red]")

@glossary.command(name="import-terms")
@click.option('--csv-file', required=False, type=click.Path(exists=True), help='CSV file with glossary terms')
@click.option('--json-file', required=False, type=click.Path(exists=True), help='JSON file with glossary terms')
@click.option('--glossary-guid', required=True, help='The globally unique identifier for glossary')
@click.option('--include-term-hierarchy', is_flag=True, default=True, help='Include term hierarchy (default: True)')
def import_terms_csv(csv_file, json_file, glossary_guid, include_term_hierarchy):
    """Import glossary terms from a CSV or JSON file.
    
    Accepts any CSV format - the API handles Purview UI exports directly.
    """
    try:
        if not csv_file and not json_file:
            console.print("[red]Error: Either --csv-file or --json-file must be provided[/red]")
            return
            
        if csv_file and json_file:
            console.print("[red]Error: Provide either --csv-file or --json-file, not both[/red]")
            return
            
        from purviewcli.client._glossary import Glossary
        import csv
        import json
        
        client = Glossary()
        
        if csv_file:
            console.print(f"[cyan]Importing terms from: {csv_file}[/cyan]")
            
            # Check if it's a Purview UI export (has capital "Name" column)
            # If so, upload directly to API which handles all the parsing
            with open(csv_file, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                has_ui_columns = "Name" in first_line and "Definition" in first_line
            
            if has_ui_columns:
                # Upload CSV directly - API handles everything
                args = {
                    '--csvFile': csv_file,
                    '--glossaryGuid': glossary_guid,
                    '--includeTermHierarchy': include_term_hierarchy
                }
                result = client.glossaryImportTerms(args)
            else:
                # Simple format - convert to JSON for API
                terms = []
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        term = {
                            "name": row.get("name", ""),
                            "definition": row.get("definition", ""),
                            "status": row.get("status", "Draft"),
                            "nickName": row.get("nickName", ""),
                            "abbreviation": row.get("abbreviation", "")
                        }
                        term = {k: v for k, v in term.items() if v}
                        terms.append(term)
                
                args = {
                    '--payloadFile': None,
                    '--glossaryGuid': glossary_guid,
                    '--includeTermHierarchy': include_term_hierarchy
                }
                client.glossaryImportTerms(args)
                client.payload = terms
                result = client.call_api()
        else:
            # For JSON files, use the existing method
            args = {
                '--payloadFile': json_file,
                '--glossaryGuid': glossary_guid,
                '--includeTermHierarchy': include_term_hierarchy
            }
            result = client.glossaryImportTerms(args)
        
        if isinstance(result, dict) and result.get('status') == 'success':
            console.print("[green]SUCCESS:[/green] Terms import initiated")
            if result.get('data'):
                console.print(json.dumps(result['data'], indent=2))
        else:
            console.print(json.dumps(result, indent=2))
            
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")

# Make the glossary group available for import
__all__ = ['glossary']
