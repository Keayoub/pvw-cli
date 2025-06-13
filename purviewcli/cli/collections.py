"""
Manage collections in Microsoft Purview using modular Click-based commands.

Usage:
  collections create         Create a new collection
  collections delete         Delete a collection
  collections get            Get a collection by name
  collections list           List all collections
  collections import_csv     Import collections from a CSV file
  collections export_csv     Export collections to a CSV file
  collections --help         Show this help message and exit

Options:
  -h --help                  Show this help message and exit
"""

import click
import json
from purviewcli.client._collections import Collections

@click.group()
def collections():
    """
    Manage collections in Microsoft Purview.
    
    """
    pass

@collections.command()
@click.option('--collection-name', required=True, help='The unique name of the collection')
@click.option('--friendly-name', help='The friendly name of the collection')
@click.option('--description', help='Description of the collection')
@click.option('--parent-collection', default='root', help='The reference name of the parent collection')
@click.option('--payload-file', type=click.Path(exists=True), help='File path to a valid JSON document')
def create(collection_name, friendly_name, description, parent_collection, payload_file):
    """Create a new collection"""
    try:
        args = {
            '--collectionName': collection_name,
            '--friendlyName': friendly_name,
            '--description': description,
            '--parentCollection': parent_collection,
            '--payloadFile': payload_file
        }
        client = Collections()
        result = client.collectionsCreateCollection(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@collections.command()
@click.option('--collection-name', required=True, help='The unique name of the collection')
def delete(collection_name):
    """Delete a collection"""
    try:
        args = {'--collectionName': collection_name}
        client = Collections()
        result = client.collectionsDeleteCollection(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@collections.command()
@click.option('--collection-name', required=True, help='The unique name of the collection')
def get(collection_name):
    """Get a collection by name"""
    try:
        args = {'--collectionName': collection_name}
        client = Collections()
        result = client.collectionsGetCollection(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@collections.command()
def list():
    """List all collections"""
    try:
        client = Collections()
        result = client.collectionsGetCollections({})
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@collections.command()
@click.option('--csv-file', type=click.Path(exists=True), required=True, help='CSV file to import collections from')
def import_csv(csv_file):
    """Import collections from a CSV file"""
    try:
        args = {'--csv-file': csv_file}
        client = Collections()
        # You may need to implement this method in your client
        result = client.importCollectionsFromCSV(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@collections.command()
@click.option('--output-file', type=click.Path(), required=True, help='Output file path for CSV export')
@click.option('--include-hierarchy', is_flag=True, default=True, help='Include collection hierarchy in export')
@click.option('--include-metadata', is_flag=True, default=True, help='Include collection metadata in export')
def export_csv(output_file, include_hierarchy, include_metadata):
    """Export collections to a CSV file"""
    try:
        args = {
            '--output-file': output_file,
            '--include-hierarchy': include_hierarchy,
            '--include-metadata': include_metadata
        }
        client = Collections()
        # You may need to implement this method in your client
        result = client.exportCollectionsToCSV(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

__all__ = ['collections']
