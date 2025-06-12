"""
usage: 
    pvw search autoComplete [--keywords=<val> --limit=<val> --filterFile=<val>]
    pvw search browse  (--entityType=<val> | --path=<val>) [--limit=<val> --offset=<val>]
    pvw search query [--keywords=<val> --limit=<val> --offset=<val> --filterFile=<val> --facets-file=<val>]
    pvw search suggest [--keywords=<val> --limit=<val> --filterFile=<val>]

options:
  --purviewName=<val>     [string]  Azure Purview account name.
  --keywords=<val>        [string]  The keywords applied to all searchable fields.
  --entityType=<val>      [string]  The entity type to browse as the root level entry point.
  --path=<val>            [string]  The path to browse the next level child entities.
  --limit=<val>           [integer] By default there is no paging [default: 25].
  --offset=<val>          [integer] Offset for pagination purpose [default: 0].
  --filterFile=<val>      [string]  File path to a filter json file.
  --facets-file=<val>     [string]  File path to a facets json file.

"""
import click
from purviewcli.client._search import Search

@click.group()
def search():
    """
    Search data assets and metadata in Azure Purview.
    All search operations are exposed as modular Click-based commands for full CLI visibility.
    """
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

__all__ = ['search']
