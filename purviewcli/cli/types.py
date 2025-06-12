"""
usage: 
    pvw types createTypeDefs --payloadFile=<val>
    pvw types deleteTypeDef --name=<val>
    pvw types deleteTypeDefs --payloadFile=<val>
    pvw types putTypeDefs --payloadFile=<val>
    pvw types readClassificationDef (--guid=<val> | --name=<val>)
    pvw types readEntityDef (--guid=<val> | --name=<val>)
    pvw types readEnumDef (--guid=<val> | --name=<val>)
    pvw types readRelationshipDef (--guid=<val> | --name=<val>)
    pvw types readStatistics
    pvw types readStructDef (--guid=<val> | --name=<val>)
    pvw types readBusinessMetadataDef (--guid=<val> | --name=<val>)
    pvw types readTermTemplateDef (--guid=<val> | --name=<val>)
    pvw types readTypeDef (--guid=<val> | --name=<val>)
    pvw types readTypeDefs [--includeTermTemplate --type=<val>]
    pvw types readTypeDefsHeaders [--includeTermTemplate --type=<val>]

options:
  --purviewName=<val>     [string]  Azure Purview account name.
  --guid=<val>            [string]  The globally unique identifier.
  --includeTermTemplate   [boolean] Whether to include termtemplatedef [default: false].
  --name=<val>            [string]  The name of the definition.
  --payloadFile=<val>     [string]  File path to a valid JSON document.
  --type=<val>            [string]  Typedef name as search filter (classification | entity | enum | relationship | struct).

"""
import json
import click
from purviewcli.client._types import Types

@click.group()
def types():
    """
    Manage type definitions in Azure Purview.
    All type operations are exposed as modular Click-based commands for full CLI visibility.
    """
    pass

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def create_typedefs(payload_file):
    """Create type definitions from a JSON file"""
    try:
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.typesCreateTypeDefs(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--name', required=True, help='Name of the type definition to delete')
def delete_typedef(name):
    """Delete a type definition by name"""
    try:
        args = {'--name': name}
        client = Types()
        result = client.typesDeleteTypeDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def delete_typedefs(payload_file):
    """Delete multiple type definitions from a JSON file"""
    try:
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.typesDeleteTypeDefs(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def put_typedefs(payload_file):
    """Update or create type definitions from a JSON file"""
    try:
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.typesPutTypeDefs(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--guid', required=False, help='The globally unique identifier')
@click.option('--name', required=False, help='The name of the classification definition')
def read_classification_def(guid, name):
    """Read a classification definition by GUID or name"""
    try:
        args = {'--guid': guid, '--name': name}
        client = Types()
        result = client.typesReadClassificationDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--guid', required=False, help='The globally unique identifier')
@click.option('--name', required=False, help='The name of the entity definition')
def read_entity_def(guid, name):
    """Read an entity definition by GUID or name"""
    try:
        args = {'--guid': guid, '--name': name}
        client = Types()
        result = client.typesReadEntityDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--guid', required=False, help='The globally unique identifier')
@click.option('--name', required=False, help='The name of the enum definition')
def read_enum_def(guid, name):
    """Read an enum definition by GUID or name"""
    try:
        args = {'--guid': guid, '--name': name}
        client = Types()
        result = client.typesReadEnumDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--guid', required=False, help='The globally unique identifier')
@click.option('--name', required=False, help='The name of the relationship definition')
def read_relationship_def(guid, name):
    """Read a relationship definition by GUID or name"""
    try:
        args = {'--guid': guid, '--name': name}
        client = Types()
        result = client.typesReadRelationshipDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
def read_statistics():
    """Read type statistics"""
    try:
        args = {}
        client = Types()
        result = client.typesReadStatistics(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--guid', required=False, help='The globally unique identifier')
@click.option('--name', required=False, help='The name of the struct definition')
def read_struct_def(guid, name):
    """Read a struct definition by GUID or name"""
    try:
        args = {'--guid': guid, '--name': name}
        client = Types()
        result = client.typesReadStructDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--guid', required=False, help='The globally unique identifier')
@click.option('--name', required=False, help='The name of the business metadata definition')
def read_business_metadata_def(guid, name):
    """Read a business metadata definition by GUID or name"""
    try:
        args = {'--guid': guid, '--name': name}
        client = Types()
        result = client.typesReadBusinessMetadataDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--guid', required=False, help='The globally unique identifier')
@click.option('--name', required=False, help='The name of the term template definition')
def read_term_template_def(guid, name):
    """Read a term template definition by GUID or name"""
    try:
        args = {'--guid': guid, '--name': name}
        client = Types()
        result = client.typesReadTermTemplateDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--guid', required=False, help='The globally unique identifier')
@click.option('--name', required=False, help='The name of the type definition')
def read_typedef(guid, name):
    """Read a type definition by GUID or name"""
    try:
        args = {'--guid': guid, '--name': name}
        client = Types()
        result = client.typesReadTypeDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--include-term-template', is_flag=True, default=False, help='Include term template definitions')
@click.option('--type', 'type_', required=False, help='Typedef name as search filter (classification | entity | enum | relationship | struct)')
def read_typedefs(include_term_template, type_):
    """Read all type definitions, optionally filtered by type or including term templates"""
    try:
        args = {'--includeTermTemplate': include_term_template, '--type': type_}
        client = Types()
        result = client.typesReadTypeDefs(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--include-term-template', is_flag=True, default=False, help='Include term template definitions')
@click.option('--type', 'type_', required=False, help='Typedef name as search filter (classification | entity | enum | relationship | struct)')
def read_typedefs_headers(include_term_template, type_):
    """Read type definition headers, optionally filtered by type or including term templates"""
    try:
        args = {'--includeTermTemplate': include_term_template, '--type': type_}
        client = Types()
        result = client.typesReadTypeDefsHeaders(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

__all__ = ['types']
