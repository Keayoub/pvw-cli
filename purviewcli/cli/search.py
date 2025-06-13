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
from purviewcli.client._search import Search

@click.group()
def search():
    """Search and discover assets"""
    pass

def _invoke_search_method(method_name, **kwargs):
    search_client = Search()
    method = getattr(search_client, method_name)
    args = {f'--{k}': v for k, v in kwargs.items() if v is not None}
    try:
        result = method(args)
        click.echo(result)
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)

@search.command()
@click.option('--keywords', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--filterFile', required=False, type=click.Path(exists=True))
def autocomplete(keywords, limit, filterfile):
    """Autocomplete search suggestions"""
    _invoke_search_method('searchAutoComplete', keywords=keywords, limit=limit, filterFile=filterfile)

@search.command()
@click.option('--entityType', required=False)
@click.option('--path', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--offset', required=False, type=int, default=0)
def browse(entitytype, path, limit, offset):
    """Browse entities by type or path"""
    _invoke_search_method('searchBrowse', entityType=entitytype, path=path, limit=limit, offset=offset)

@search.command()
@click.option('--keywords', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--offset', required=False, type=int, default=0)
@click.option('--filterFile', required=False, type=click.Path(exists=True))
@click.option('--facets-file', required=False, type=click.Path(exists=True))
def query(keywords, limit, offset, filterfile, facets_file):
    """Run a search query"""
    _invoke_search_method('searchQuery', keywords=keywords, limit=limit, offset=offset, filterFile=filterfile, facets_file=facets_file)

@search.command()
@click.option('--keywords', required=False)
@click.option('--limit', required=False, type=int, default=25)
@click.option('--filterFile', required=False, type=click.Path(exists=True))
def suggest(keywords, limit, filterfile):
    """Get search suggestions"""
    _invoke_search_method('searchSuggest', keywords=keywords, limit=limit, filterFile=filterfile)

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
