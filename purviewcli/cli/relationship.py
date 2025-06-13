"""
usage: 
    pvw relationship create --payloadFile=<val>
    pvw relationship delete --guid=<val>
    pvw relationship put --payloadFile=<val>
    pvw relationship read --guid=<val> [--extendedInfo]

options:
    --purviewName=<val>           [string]  Microsoft Purview account name.
    --extendedInfo                [boolean] Limits whether includes extended information [default: false].
    --guid=<val>                  [string]  The globally unique identifier of the relationship.
    --payloadFile=<val>           [string]  File path to a valid JSON document.

"""
import click
import json
from purviewcli.client._relationship import Relationship

@click.group()
def relationship():
    """
    Manage entity relationships in Microsoft Purview.
    """
    pass

@relationship.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def create(payload_file):
    """Create a new relationship"""
    try:
        args = {'--payloadFile': payload_file}
        client = Relationship()
        result = client.relationshipCreate(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@relationship.command()
@click.option('--guid', required=True, help='The globally unique identifier of the relationship')
def delete(guid):
    """Delete a relationship by GUID"""
    try:
        args = {'--guid': guid}
        client = Relationship()
        result = client.relationshipDelete(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@relationship.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def put(payload_file):
    """Update or create a relationship (PUT)"""
    try:
        args = {'--payloadFile': payload_file}
        client = Relationship()
        result = client.relationshipPut(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@relationship.command()
@click.option('--guid', required=True, help='The globally unique identifier of the relationship')
@click.option('--extended-info', is_flag=True, default=False, help='Include extended information')
def read(guid, extended_info):
    """Read a relationship by GUID"""
    try:
        args = {'--guid': guid, '--extendedInfo': extended_info}
        client = Relationship()
        result = client.relationshipRead(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

__all__ = ['relationship']
