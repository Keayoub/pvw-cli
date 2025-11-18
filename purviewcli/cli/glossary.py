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


@glossary.command(name="sync-uc")
@click.option("--glossary-guid", required=True, help="Source classic glossary GUID to sync from")
@click.option("--domain-id", required=False, help="Target UC governance domain ID (if not provided, creates/uses domain with glossary name)")
@click.option("--create-domain", is_flag=True, help="Create UC domain if it doesn't exist")
@click.option("--dry-run", is_flag=True, help="Preview changes without applying them")
@click.option("--update-existing", is_flag=True, help="Update existing UC terms if they already exist")
def sync_uc(glossary_guid, domain_id, create_domain, dry_run, update_existing):
    """Synchronize classic glossary terms to Unified Catalog.
    
    This command enables migration from classic glossaries to the Unified Catalog,
    syncing terms from traditional glossary structures to governance domains.
    
    Examples:
        # Sync classic glossary to its corresponding domain
        pvw glossary sync-uc --glossary-guid <glossary-guid>
        
        # Sync to a specific domain
        pvw glossary sync-uc --glossary-guid <glossary-guid> --domain-id <domain-guid>
        
        # Create domain if needed and sync
        pvw glossary sync-uc --glossary-guid <glossary-guid> --create-domain
        
        # Preview sync without making changes
        pvw glossary sync-uc --glossary-guid <glossary-guid> --dry-run
        
        # Update existing terms in UC domain
        pvw glossary sync-uc --glossary-guid <glossary-guid> --update-existing
    """
    try:
        from purviewcli.client._glossary import Glossary
        from purviewcli.client._unified_catalog import UnifiedCatalogClient
        import tempfile
        import os
        
        glossary_client = Glossary()
        uc_client = UnifiedCatalogClient()
        
        console.print("[cyan]" + "-" * 59 + "[/cyan]")
        console.print("[bold cyan]  Classic Glossary → Unified Catalog Sync  [/bold cyan]")
        console.print("[cyan]" + "-" * 59 + "[/cyan]\n")
        
        if dry_run:
            console.print("[yellow][*] DRY RUN MODE - No changes will be made[/yellow]\n")
        
        # Step 1: Get classic glossary terms
        console.print("[bold]Step 1:[/bold] Fetching classic glossary terms...")
        glossary_details = glossary_client.glossaryReadDetailed({"--glossaryGuid": [glossary_guid]})
        
        glossary_name = glossary_details.get("name", "Unknown Glossary")
        classic_terms = glossary_details.get("terms", [])
        
        if not classic_terms:
            console.print("[yellow][!] No terms found in classic glossary.[/yellow]")
            return
        
        console.print(f"[green][OK][/green] Found {len(classic_terms)} classic term(s) from glossary: {glossary_name}\n")
        
        # Step 2: Determine or create target domain
        console.print("[bold]Step 2:[/bold] Determining target UC domain...")
        
        target_domain_id = domain_id
        
        if not target_domain_id:
            # Try to find existing domain with matching name
            all_domains = uc_client.list_governance_domains({})
            
            if isinstance(all_domains, dict):
                all_domains = all_domains.get("value", [])
            
            for d in all_domains:
                d_name = d.get("name", "")
                if d_name == glossary_name:
                    target_domain_id = d.get("id")
                    console.print(f"[green][OK][/green] Found existing domain: {d_name} ({target_domain_id})\n")
                    break
            
            if not target_domain_id and create_domain:
                if dry_run:
                    console.print(f"[yellow]Would create domain:[/yellow] {glossary_name}\n")
                    target_domain_id = "dry-run-domain-id"
                else:
                    # Create domain
                    domain_payload = {
                        "name": glossary_name,
                        "description": f"Auto-synced from classic glossary: {glossary_name}",
                        "status": "Published"
                    }
                    
                    create_args = {
                        "--name": glossary_name,
                        "--description": domain_payload["description"],
                        "--status": "Published"
                    }
                    
                    new_domain = uc_client.create_governance_domain(create_args)
                    target_domain_id = new_domain.get("id")
                    console.print(f"[green][OK][/green] Created domain: {glossary_name} ({target_domain_id})\n")
            elif not target_domain_id:
                console.print(f"[red]ERROR:[/red] No target domain found. Use --domain-id or --create-domain")
                return
        else:
            domain_info = uc_client.get_governance_domain_by_id({"--domain-id": [target_domain_id]})
            domain_name = domain_info.get("name", "Unknown Domain")
            console.print(f"[green][OK][/green] Using target domain: {domain_name} ({target_domain_id})\n")
        
        # Step 3: Get existing UC terms
        console.print("[bold]Step 3:[/bold] Checking existing UC terms...")
        
        existing_terms = {}
        try:
            uc_args = {"--governance-domain-id": [target_domain_id]}
            uc_result = uc_client.get_terms(uc_args)
            
            uc_terms = []
            if isinstance(uc_result, dict):
                uc_terms = uc_result.get("value", [])
            elif isinstance(uc_result, (list, tuple)):
                uc_terms = uc_result
            
            for term in uc_terms:
                term_name = term.get("name", "")
                term_id = term.get("id", "")
                if term_name:
                    existing_terms[term_name.lower()] = term_id
            
            console.print(f"[green][OK][/green] Found {len(existing_terms)} existing term(s) in UC domain\n")
        except Exception as e:
            console.print(f"[yellow][!][/yellow] Could not fetch existing terms: {e}\n")
        
        # Step 4: Sync terms
        console.print("[bold]Step 4:[/bold] Synchronizing terms...")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0
        
        for classic_term in classic_terms:
            term_name = classic_term.get("displayText") or classic_term.get("name", "")
            
            # Get full term details
            term_guid = classic_term.get("termGuid") or classic_term.get("guid")
            
            try:
                term_details = glossary_client.glossaryReadTerm({"--termGuid": [term_guid]})
                
                term_description = term_details.get("longDescription") or term_details.get("shortDescription", "")
                term_status = term_details.get("status", "Draft")
                term_abbreviation = term_details.get("abbreviation", "")
                
                # Check if term already exists
                existing_id = existing_terms.get(term_name.lower())
                
                if existing_id and not update_existing:
                    console.print(f"   [dim][-] Skipping:[/dim] {term_name} (already exists)")
                    skipped_count += 1
                    continue
                
                if existing_id and update_existing:
                    # Update existing term
                    if dry_run:
                        console.print(f"   [yellow]Would update:[/yellow] {term_name}")
                        updated_count += 1
                    else:
                        update_payload = {
                            "name": term_name,
                            "description": term_description,
                            "status": term_status,
                            "domain_id": target_domain_id
                        }
                        
                        if term_abbreviation:
                            update_payload["acronyms"] = [term_abbreviation]
                        
                        update_args = {
                            "--term-id": existing_id,
                            "--name": term_name,
                            "--description": term_description,
                            "--status": term_status
                        }
                        
                        uc_client.update_term(update_args)
                        console.print(f"   [green][OK] Updated:[/green] {term_name}")
                        updated_count += 1
                else:
                    # Create new term
                    if dry_run:
                        console.print(f"   [yellow]Would create:[/yellow] {term_name}")
                        created_count += 1
                    else:
                        create_payload = {
                            "name": term_name,
                            "description": term_description,
                            "status": term_status,
                            "domain_id": target_domain_id
                        }
                        
                        if term_abbreviation:
                            create_payload["acronyms"] = [term_abbreviation]
                        
                        create_args = {
                            "--name": term_name,
                            "--description": term_description,
                            "--domain-id": target_domain_id,
                            "--status": term_status
                        }
                        
                        uc_client.create_term(create_args)
                        console.print(f"   [green][OK] Created:[/green] {term_name}")
                        created_count += 1
            
            except Exception as e:
                console.print(f"   [red][X] Failed:[/red] {term_name} - {str(e)}")
                failed_count += 1
        
        # Summary
        console.print("\n[cyan]" + "-" * 59 + "[/cyan]")
        console.print("[bold cyan]  Synchronization Summary  [/bold cyan]")
        console.print("[cyan]" + "-" * 59 + "[/cyan]")
        
        from rich.table import Table
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="bold")
        summary_table.add_column("Count", style="cyan")
        
        summary_table.add_row("Total Classic Terms", str(len(classic_terms)))
        summary_table.add_row("Created", f"[green]{created_count}[/green]")
        summary_table.add_row("Updated", f"[yellow]{updated_count}[/yellow]")
        summary_table.add_row("Skipped", f"[dim]{skipped_count}[/dim]")
        summary_table.add_row("Failed", f"[red]{failed_count}[/red]")
        
        console.print(summary_table)
        
        if dry_run:
            console.print("\n[yellow][TIP] This was a dry run. Use without --dry-run to apply changes.[/yellow]")
        elif failed_count == 0 and (created_count > 0 or updated_count > 0):
            console.print("\n[green][OK] Synchronization completed successfully![/green]")
        
    except Exception as e:
        console.print(f"\n[red]ERROR:[/red] {str(e)}")
        import traceback
        if os.getenv("PURVIEWCLI_DEBUG"):
            console.print(traceback.format_exc())


# Make the glossary group available for import
__all__ = ['glossary']

