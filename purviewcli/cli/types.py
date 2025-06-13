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

Advanced Workflows & API Mapping:
---------------------------------
- Bulk Operations: Use `create_typedefs`, `put_typedefs`, and `delete_typedefs` to manage multiple type definitions at once via JSON files. These map to Atlas v2 Data Map API bulk endpoints (typesCreateTypeDefs, typesPutTypeDefs, typesDeleteTypeDefs).
- Per-Type Reads: Use `read_classification_def`, `read_entity_def`, `read_enum_def`, `read_relationship_def`, `read_struct_def`, `read_business_metadata_def`, `read_term_template_def` for fine-grained inspection of type definitions. These map to Atlas v2 endpoints for each type.
- Filtering: Use `read_typedefs` and `read_typedefs_headers` with `--type` and `--include-term-template` to filter results, mapping to Atlas v2's flexible type listing APIs.
- Statistics: Use `read_statistics` to get a summary of type system state (maps to typesReadStatistics).
- Error Handling: For bulk operations, errors are reported in the CLI output. For advanced error reporting (e.g., failed items to file), see future roadmap.
- API Coverage: This CLI covers all read operations and bulk create/update/delete. For per-type create/update/delete, use JSON payloads with the bulk endpoints. For advanced features (versioning, validation, dry-run), monitor API updates and CLI roadmap.

Examples:
---------
# Bulk create/update type definitions from a JSON file
pvw types createTypeDefs --payloadFile=types.json

# Delete a single type definition by name
pvw types deleteTypeDef --name=MyEntityType

# Read all entity type definitions
pvw types readTypeDefs --type=entity

# Read a classification definition by GUID
pvw types readClassificationDef --guid=1234-5678

# Read type system statistics
pvw types readStatistics

For more advanced examples and templates, see the documentation in `doc/commands/types/` and sample JSON in `samples/json/`.
"""

import json
import click
from purviewcli.client._types import Types

@click.group()
def types():
    """Manage types (schemas, entity types, relationship types, etc.)"""
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

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def create_business_metadata_def(payload_file):
    """Create business metadata definition from a JSON file"""
    try:
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.createBusinessMetadataDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def update_business_metadata_def(payload_file):
    """Update business metadata definition from a JSON file"""
    try:
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.updateBusinessMetadataDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--name', required=True, help='Name of the business metadata definition to delete')
def delete_business_metadata_def(name):
    """Delete a business metadata definition by name"""
    try:
        args = {'--name': name}
        client = Types()
        result = client.deleteBusinessMetadataDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def create_term_template_def(payload_file):
    """Create term template definition from a JSON file"""
    try:
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.createTermTemplateDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
def update_term_template_def(payload_file):
    """Update term template definition from a JSON file"""
    try:
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.updateTermTemplateDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--name', required=True, help='Name of the term template definition to delete')
def delete_term_template_def(name):
    """Delete a term template definition by name"""
    try:
        args = {'--name': name}
        client = Types()
        result = client.deleteTermTemplateDef(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

__all__ = ['types']
