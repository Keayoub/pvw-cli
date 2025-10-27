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
  --purviewName=<val>     [string]  Microsoft Purview account name.
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
@click.option('--output-file', type=click.Path(), required=False, help='Write result to this file instead of stdout')
@click.option('--error-file', type=click.Path(), required=False, help='Write errors to this file instead of stdout')
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
@click.option('--validate/--no-validate', default=False, help='Validate the payload without making changes')
def create_typedefs(payload_file, dry_run, validate, output_file, error_file):
    """Create type definitions from a JSON file"""
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        if validate:
            click.echo('[VALIDATION] Payload is valid JSON.')
        if dry_run:
            click.echo('[DRY-RUN] Would send the following payload:')
            click.echo(json.dumps(payload, indent=2))
            return
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.typesCreateTypeDefs(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
            click.echo(f"Error: {e}")

@types.command()
@click.option('--output-file', type=click.Path(), required=False, help='Write result to this file instead of stdout')
@click.option('--error-file', type=click.Path(), required=False, help='Write errors to this file instead of stdout')
@click.option('--name', required=True, help='Name of the type definition to delete')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
def delete_typedef(name, dry_run, output_file, error_file):
    """Delete a type definition by name"""
    try:
        if dry_run:
            click.echo(f'[DRY-RUN] Would delete type definition with name: {name}')
            return
        args = {'--name': name}
        client = Types()
        result = client.typesDeleteTypeDef(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
            click.echo(f"Error: {e}")

@types.command()
@click.option('--output-file', type=click.Path(), required=False, help='Write result to this file instead of stdout')
@click.option('--error-file', type=click.Path(), required=False, help='Write errors to this file instead of stdout')
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
@click.option('--validate/--no-validate', default=False, help='Validate the payload without making changes')
def put_typedefs(payload_file, dry_run, validate, output_file, error_file):
    """Update or create type definitions from a JSON file"""
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        if validate:
            click.echo('[VALIDATION] Payload is valid JSON.')
        if dry_run:
            click.echo('[DRY-RUN] Would send the following payload:')
            click.echo(json.dumps(payload, indent=2))
            return
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.typesPutTypeDefs(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
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
        result = client.typesRead(args)
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
        result = client.typesReadHeaders(args)
        click.echo(json.dumps(result, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}")

@types.command()
@click.option('--output-file', type=click.Path(), required=False, help='Write result to this file instead of stdout')
@click.option('--error-file', type=click.Path(), required=False, help='Write errors to this file instead of stdout')
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
@click.option('--validate/--no-validate', default=False, help='Validate the payload without making changes')
def create_business_metadata_def(payload_file, dry_run, validate, output_file, error_file):
    """Create business metadata definition from a JSON file"""
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        if validate:
            click.echo('[VALIDATION] Payload is valid JSON.')
            # Optionally, add more schema validation here
        if dry_run:
            click.echo('[DRY-RUN] Would send the following payload:')
            click.echo(json.dumps(payload, indent=2))
            return
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.createBusinessMetadataDef(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
            click.echo(f"Error: {e}")

@types.command()
@click.option('--output-file', type=click.Path(), required=False, help='Write result to this file instead of stdout')
@click.option('--error-file', type=click.Path(), required=False, help='Write errors to this file instead of stdout')
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
@click.option('--validate/--no-validate', default=False, help='Validate the payload without making changes')
def update_business_metadata_def(payload_file, dry_run, validate, output_file, error_file):
    """Update business metadata definition from a JSON file"""
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        if validate:
            click.echo('[VALIDATION] Payload is valid JSON.')
            # Optionally, add more schema validation here
        if dry_run:
            click.echo('[DRY-RUN] Would send the following payload:')
            click.echo(json.dumps(payload, indent=2))
            return
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.updateBusinessMetadataDef(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
            click.echo(f"Error: {e}")

@types.command()
@click.option('--name', required=True, help='Name of the business metadata definition to delete')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
@click.option('--output-file', type=click.Path(), required=False, help='Write result to this file instead of stdout')
@click.option('--error-file', type=click.Path(), required=False, help='Write errors to this file instead of stdout')
def delete_business_metadata_def(name, dry_run, output_file, error_file):
    """Delete a business metadata definition by name"""
    try:
        if dry_run:
            click.echo(f'[DRY-RUN] Would delete business metadata definition with name: {name}')
            return
        args = {'--name': name}
        client = Types()
        result = client.deleteBusinessMetadataDef(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
            click.echo(f"Error: {e}")

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
@click.option('--validate/--no-validate', default=False, help='Validate the payload without making changes')
def create_term_template_def(payload_file, dry_run, validate, output_file, error_file):
    """Create term template definition from a JSON file"""
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        if validate:
            click.echo('[VALIDATION] Payload is valid JSON.')
            # Optionally, add more schema validation here
        if dry_run:
            click.echo('[DRY-RUN] Would send the following payload:')
            click.echo(json.dumps(payload, indent=2))
            return
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.createTermTemplateDef(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
            click.echo(f"Error: {e}")

@types.command()
@click.option('--output-file', type=click.Path(), required=False, help='Write result to this file instead of stdout')
@click.option('--error-file', type=click.Path(), required=False, help='Write errors to this file instead of stdout')
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
@click.option('--validate/--no-validate', default=False, help='Validate the payload without making changes')
def update_term_template_def(payload_file, dry_run, validate, output_file, error_file):
    """Update term template definition from a JSON file"""
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        if validate:
            click.echo('[VALIDATION] Payload is valid JSON.')
            # Optionally, add more schema validation here
        if dry_run:
            click.echo('[DRY-RUN] Would send the following payload:')
            click.echo(json.dumps(payload, indent=2))
            return
        args = {'--payloadFile': payload_file}
        client = Types()
        result = client.updateTermTemplateDef(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
            click.echo(f"Error: {e}")

@types.command()
@click.option('--output-file', type=click.Path(), required=False, help='Write result to this file instead of stdout')
@click.option('--error-file', type=click.Path(), required=False, help='Write errors to this file instead of stdout')
@click.option('--name', required=True, help='Name of the term template definition to delete')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
def delete_term_template_def(name, dry_run, output_file, error_file):
    """Delete a term template definition by name"""
    try:
        if dry_run:
            click.echo(f'[DRY-RUN] Would delete term template definition with name: {name}')
            return
        args = {'--name': name}
        client = Types()
        result = client.deleteTermTemplateDef(args)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as outf:
                outf.write(json.dumps(result, indent=2))
        else:
            click.echo(json.dumps(result, indent=2))
    except Exception as e:
        if error_file:
            with open(error_file, 'w', encoding='utf-8') as errf:
                errf.write(str(e))
        else:
            click.echo(f"Error: {e}")

@types.command()
@click.option('--payload-file', type=click.Path(exists=True), required=True, help='File path to a valid JSON document')
@click.option('--dry-run/--no-dry-run', default=False, help='Simulate the operation without making changes')
@click.option('--validate/--no-validate', default=False, help='Validate the payload without making changes')
def update_enum_def(payload_file, dry_run, validate):
    """Update enum definition from a JSON file (example for extensibility)"""
    try:
        with open(payload_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        if validate:
            click.echo('[VALIDATION] Payload is valid JSON.')
        if dry_run:
            click.echo('[DRY-RUN] Would send the following payload:')
            click.echo(json.dumps(payload, indent=2))
            return
        # args and client logic would go here
        click.echo('[NOT IMPLEMENTED] This is a placeholder for extensibility.')
    except Exception as e:
        click.echo(f"Error: {e}")


@types.command(name="list-business-attributes")
@click.option('--output', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--show-empty-groups/--hide-empty-groups', default=True, help='Show groups with no attributes')
def list_business_attributes(output, show_empty_groups):
    """List all business metadata attributes (Custom metadata in Purview UI)
    
    This command displays individual attributes organized by their parent groups,
    matching what you see in the Purview "Custom metadata (preview)" interface
    under "Business concept attributes" tab.
    
    Examples:
        pvw types list-business-attributes
        pvw types list-business-attributes --output json
        pvw types list-business-attributes --hide-empty-groups
    """
    from rich.console import Console
    from rich.table import Table
    
    console = Console()
    
    try:
        client = Types()
        result = client.typesRead({})
        
        if not result:
            console.print("[red]ERROR:[/red] Failed to retrieve type definitions")
            return
        
        biz = result.get('businessMetadataDefs', [])
        
        if not biz:
            console.print("[yellow]No business metadata found[/yellow]")
            return
        
        if output == 'json':
            # JSON output: list of attributes with their group info
            attributes_list = []
            for group in biz:
                group_name = group.get('name', 'N/A')
                group_guid = group.get('guid', 'N/A')
                
                attributes = group.get('attributeDefs', [])
                if not attributes and not show_empty_groups:
                    continue
                
                for attr in attributes:
                    attributes_list.append({
                        'attributeName': attr.get('name'),
                        'group': group_name,
                        'groupGuid': group_guid,
                        'type': attr.get('typeName'),
                        'description': attr.get('description', ''),
                        'isOptional': attr.get('isOptional', True),
                        'isIndexable': attr.get('isIndexable', False)
                    })
            
            click.echo(json.dumps(attributes_list, indent=2))
            return
        
        # Table output
        table = Table(title="[bold cyan]Business Concept Attributes (Custom Metadata)[/bold cyan]")
        table.add_column("Attribute Name", style="green", no_wrap=True)
        table.add_column("Group", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Description", style="white", max_width=40)
        table.add_column("Scope", style="magenta")
        
        total_attributes = 0
        
        for group in biz:
            group_name = group.get('name', 'N/A')
            
            # Parse data governance options for scope
            scope_info = "N/A"
            options = group.get('options', {})
            if 'dataGovernanceOptions' in options:
                try:
                    dg_opts_str = options.get('dataGovernanceOptions', '{}')
                    dg_opts = json.loads(dg_opts_str) if isinstance(dg_opts_str, str) else dg_opts_str
                    applicable = dg_opts.get('applicableConstructs', [])
                    if applicable:
                        # Extract construct types (domain, businessConcept, etc.)
                        scope_parts = []
                        for construct in applicable[:2]:  # Show first 2
                            if ':' in construct:
                                scope_parts.append(construct.split(':')[0])
                            else:
                                scope_parts.append(construct)
                        scope_info = ', '.join(scope_parts)
                        if len(applicable) > 2:
                            scope_info += f", +{len(applicable)-2} more"
                except:
                    pass
            
            # List all attributes in this group
            attributes = group.get('attributeDefs', [])
            
            if attributes:
                for attr in attributes:
                    total_attributes += 1
                    attr_name = attr.get('name', 'N/A')
                    attr_type = attr.get('typeName', 'N/A')
                    
                    # Simplify enum types for display
                    if 'ATTRIBUTE_ENUM_' in attr_type:
                        attr_type = 'Enum (Single choice)'
                    
                    attr_desc = attr.get('description', '')
                    
                    # Get scope from attribute if it overrides group
                    attr_scope = scope_info
                    attr_opts = attr.get('options', {})
                    if 'dataGovernanceOptions' in attr_opts:
                        try:
                            attr_dg_str = attr_opts.get('dataGovernanceOptions', '{}')
                            attr_dg = json.loads(attr_dg_str) if isinstance(attr_dg_str, str) else attr_dg_str
                            inherit = attr_dg.get('inheritApplicableConstructsFromGroup', True)
                            if not inherit:
                                attr_applicable = attr_dg.get('applicableConstructs', [])
                                if attr_applicable:
                                    attr_scope = f"{len(attr_applicable)} custom scope(s)"
                        except:
                            pass
                    
                    table.add_row(
                        attr_name,
                        group_name,
                        attr_type,
                        attr_desc[:40] + "..." if len(attr_desc) > 40 else attr_desc,
                        attr_scope
                    )
            elif show_empty_groups:
                # Show group with no attributes
                table.add_row(
                    f"[dim](no attributes)[/dim]",
                    group_name,
                    "-",
                    f"[dim]Empty group[/dim]",
                    scope_info
                )
        
        console.print(table)
        console.print(f"\n[cyan]Total:[/cyan] {total_attributes} attribute(s) in {len(biz)} group(s)")
        
        if total_attributes > 0:
            console.print("\n[dim]Tip: Use 'pvw types read-business-metadata-def --name <GroupName>' for details[/dim]")
            console.print("[dim]Tip: Use 'pvw types list-business-metadata-groups' to see group-level summary[/dim]")
    
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


@types.command(name="list-business-metadata-groups")
@click.option('--output', type=click.Choice(['table', 'json']), default='table', help='Output format')
def list_business_metadata_groups(output):
    """List business metadata groups with their scope (Business Concept vs Data Asset).
    
    Shows a summary view of metadata groups to distinguish which apply to:
    - Business Concepts (Terms, Domains, Business Rules)
    - Data Assets (Tables, Files, Databases)
    - Universal (Both)
    
    Examples:
        pvw types list-business-metadata-groups
        pvw types list-business-metadata-groups --output json
    """
    from rich.console import Console
    from rich.table import Table
    import json
    
    console = Console()
    
    try:
        client = Types()
        result = client.typesRead({})
        
        if not result:
            console.print("[red]ERROR:[/red] Failed to retrieve type definitions")
            return
        
        biz = result.get('businessMetadataDefs', [])
        
        if not biz:
            console.print("[yellow]No business metadata groups found[/yellow]")
            return
        
        if output == 'json':
            # JSON output
            groups_list = []
            for group in biz:
                group_name = group.get('name', 'N/A')
                group_guid = group.get('guid', 'N/A')
                attr_count = len(group.get('attributeDefs', []))
                
                # Determine scope
                scope = "N/A"
                scope_type = "unknown"
                options = group.get('options', {})
                
                if 'dataGovernanceOptions' in options:
                    try:
                        dg_opts_str = options.get('dataGovernanceOptions', '{}')
                        dg_opts = json.loads(dg_opts_str) if isinstance(dg_opts_str, str) else dg_opts_str
                        applicable = dg_opts.get('applicableConstructs', [])
                        
                        if applicable:
                            has_business_concept = any('businessConcept' in c or 'domain' in c for c in applicable)
                            has_dataset = any('dataset' in c.lower() for c in applicable)
                            
                            if has_business_concept and has_dataset:
                                scope = "Universal (Concept + Dataset)"
                                scope_type = "universal"
                            elif has_business_concept:
                                scope = "Business Concept"
                                scope_type = "business_concept"
                            elif has_dataset:
                                scope = "Data Asset"
                                scope_type = "data_asset"
                            else:
                                scope = ', '.join([c.split(':')[0] if ':' in c else c for c in applicable[:3]])
                                scope_type = "custom"
                    except:
                        pass
                
                # Check for legacy applicableEntityTypes in attributes
                if scope == "N/A":
                    for attr in group.get('attributeDefs', []):
                        attr_opts = attr.get('options', {})
                        if 'applicableEntityTypes' in attr_opts:
                            try:
                                entity_types_str = attr_opts.get('applicableEntityTypes', '[]')
                                entity_types = json.loads(entity_types_str) if isinstance(entity_types_str, str) else entity_types_str
                                if entity_types and isinstance(entity_types, list):
                                    if any('table' in et.lower() or 'database' in et.lower() for et in entity_types):
                                        scope = "Data Asset (Legacy)"
                                        scope_type = "data_asset_legacy"
                                        break
                            except:
                                pass
                
                groups_list.append({
                    'groupName': group_name,
                    'groupGuid': group_guid,
                    'scope': scope,
                    'scopeType': scope_type,
                    'attributeCount': attr_count,
                    'description': group.get('description', '')
                })
            
            click.echo(json.dumps(groups_list, indent=2))
            return
        
        # Table output
        table = Table(title="[bold cyan]Business Metadata Groups[/bold cyan]", show_header=True)
        table.add_column("Group Name", style="cyan", no_wrap=True)
        table.add_column("Scope", style="magenta", max_width=30)
        table.add_column("Attributes", style="yellow", justify="center")
        table.add_column("Description", style="white", max_width=40)
        
        for group in biz:
            group_name = group.get('name', 'N/A')
            attr_count = len(group.get('attributeDefs', []))
            group_desc = group.get('description', '')
            
            # Determine scope
            scope = "N/A"
            scope_style = "white"
            options = group.get('options', {})
            
            if 'dataGovernanceOptions' in options:
                try:
                    dg_opts_str = options.get('dataGovernanceOptions', '{}')
                    dg_opts = json.loads(dg_opts_str) if isinstance(dg_opts_str, str) else dg_opts_str
                    applicable = dg_opts.get('applicableConstructs', [])
                    
                    if applicable:
                        has_business_concept = any('businessConcept' in c or 'domain' in c for c in applicable)
                        has_dataset = any('dataset' in c.lower() for c in applicable)
                        
                        if has_business_concept and has_dataset:
                            scope = "Universal"
                            scope_style = "magenta bold"
                        elif has_business_concept:
                            scope = "Business Concept"
                            scope_style = "green"
                        elif has_dataset:
                            scope = "Data Asset"
                            scope_style = "blue"
                        else:
                            scope = ', '.join([c.split(':')[0] if ':' in c else c for c in applicable[:2]])
                            scope_style = "yellow"
                except:
                    pass
            
            # Check for legacy applicableEntityTypes
            if scope == "N/A":
                for attr in group.get('attributeDefs', []):
                    attr_opts = attr.get('options', {})
                    if 'applicableEntityTypes' in attr_opts:
                        try:
                            entity_types_str = attr_opts.get('applicableEntityTypes', '[]')
                            entity_types = json.loads(entity_types_str) if isinstance(entity_types_str, str) else entity_types_str
                            if entity_types and isinstance(entity_types, list):
                                if any('table' in et.lower() or 'database' in et.lower() for et in entity_types):
                                    scope = "Data Asset (Legacy)"
                                    scope_style = "blue dim"
                                    break
                        except:
                            pass
            
            table.add_row(
                group_name,
                f"[{scope_style}]{scope}[/{scope_style}]",
                str(attr_count),
                group_desc[:40] + "..." if len(group_desc) > 40 else group_desc
            )
        
        console.print(table)
        console.print(f"\n[cyan]Total:[/cyan] {len(biz)} group(s)")
        
        console.print("\n[bold]Legend:[/bold]")
        console.print("  [green]Business Concept[/green] = Applies to Glossary Terms, Domains, Business Rules")
        console.print("  [blue]Data Asset[/blue] = Applies to Tables, Files, Databases, etc.")
        console.print("  [magenta bold]Universal[/magenta bold] = Applies to both Concepts and Assets")
        
        console.print("\n[dim]Tip: Use 'pvw types list-business-attributes' to see individual attributes[/dim]")
        console.print("[dim]Tip: Use 'pvw types read-business-metadata-def --name <GroupName>' for full details[/dim]")
    
    except Exception as e:
        console.print(f"[red]ERROR:[/red] {str(e)}")


__all__ = ['types']
