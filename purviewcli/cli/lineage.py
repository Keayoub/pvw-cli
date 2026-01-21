"""
Manage lineage operations in Microsoft Purview using modular Click-based commands.

Usage:
  lineage read                  Read lineage information for an entity
  lineage impact                Analyze impact of changes to an entity
  lineage analyze-column        Analyze column-level lineage
  lineage get-metrics           Get lineage metrics and statistics
  lineage csv-process           Process CSV lineage relationships
  lineage csv-validate          Validate CSV lineage file format
  lineage csv-sample            Generate sample CSV lineage file
  lineage csv-templates         Get available CSV lineage templates
  lineage --help                Show this help message and exit

Options:
  -h --help                     Show this help message and exit
"""

import json
import click
from .console_utils import get_console
from typing import Optional
from purviewcli.client._lineage import Lineage

console = get_console()


@click.group(help="""
Manage lineage in Microsoft Purview.

Examples:
  lineage read --guid <entity_guid> [--direction INPUT|OUTPUT|BOTH] [--depth N]
  lineage import <csv_file>
  lineage impact --guid <entity_guid>
  lineage analyze-column --guid <entity_guid> --column <column_name>
  lineage get-metrics
  lineage csv-process <csv_file>
  lineage csv-validate <csv_file>
  lineage csv-sample
  lineage csv-templates

Use 'lineage <command> --help' for more details on each command.
""")
@click.pass_context
def lineage(ctx):
    """
    Manage lineage in Microsoft Purview.
    """
    pass


@lineage.command(name="import")
@click.argument('csv_file', type=click.Path(exists=True))
@click.pass_context
def import_cmd(ctx, csv_file):
    """Import lineage relationships from CSV file (calls client lineageCSVProcess)."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage import command[/yellow]")
            console.print(f"[dim]File: {csv_file}[/dim]")
            console.print("[green]MOCK lineage import completed successfully[/green]")
            return

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        args = {"csv_file": csv_file}
        result = lineage_client.lineageCSVProcess(args)
        console.print("[green]SUCCESS: Lineage import completed successfully[/green]")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage import: {str(e)}[/red]")
        import traceback
        if ctx.obj and ctx.obj.get("debug"):
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


@lineage.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.pass_context
def validate(ctx, csv_file):
    """Validate CSV lineage file format and content locally (no API call)"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage validate command[/yellow]")
            console.print(f"[dim]File: {csv_file}[/dim]")
            console.print("[green]MOCK lineage validate completed successfully[/green]")
            return

        args = {"csv_file": csv_file}

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageCSVValidate(args)

        if isinstance(result, dict) and result.get("success"):
            console.print(f"[green]SUCCESS: Lineage validation passed: {csv_file} ({result['rows']} rows, columns: {', '.join(result['columns'])})[/green]")
        else:
            error_msg = result.get('error') if isinstance(result, dict) else str(result)
            console.print(f"[red]ERROR: Lineage validation failed: {error_msg}[/red]")

    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage validate: {str(e)}[/red]")


@lineage.command()
@click.argument('output_file', type=click.Path())
@click.option('--num-samples', type=int, default=10,
              help='Number of sample rows to generate')
@click.option('--template', default='basic',
              help='Template type: basic, etl, column-mapping')
@click.pass_context
def sample(ctx, output_file, num_samples, template):
    """Generate sample CSV lineage file locally (no API call)"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage sample command[/yellow]")
            console.print(f"[dim]Output File: {output_file}[/dim]")
            console.print(f"[dim]Samples: {num_samples}[/dim]")
            console.print(f"[dim]Template: {template}[/dim]")
            console.print("[green]MOCK lineage sample completed successfully[/green]")
            return

        args = {
            "--output-file": output_file,
            "--num-samples": num_samples,
            "--template": template,
        }

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageCSVSample(args)

        if isinstance(result, dict) and result.get("success"):
            console.print(f"[green]SUCCESS: Sample lineage CSV generated: {output_file} ({num_samples} rows, template: {template})[/green]")
        else:
            error_msg = result.get('error') if isinstance(result, dict) else str(result)
            console.print(f"[red]ERROR: Failed to generate sample lineage CSV: {error_msg}[/red]")

    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage sample: {str(e)}[/red]")


@lineage.command()
@click.pass_context
def templates(ctx):
    """Get available CSV lineage templates"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage templates command[/yellow]")
            console.print("[green]MOCK lineage templates completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageCSVTemplates(args)

        if result:
            console.print("[green]SUCCESS: Lineage templates retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Lineage templates completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage templates: {str(e)}[/red]")


@lineage.command()
@click.option('--guid', required=True, help='The globally unique identifier of the entity')
@click.option('--depth', type=int, default=3, help='The number of hops for lineage')
@click.option('--width', type=int, default=6, help='The number of max expanding width in lineage')
@click.option('--direction', default='BOTH', 
              help='The direction of the lineage: INPUT, OUTPUT or BOTH')
@click.option('--output', default='json', help='Output format: json, table')
@click.pass_context
def read(ctx, guid, depth, width, direction, output):
    """Read lineage for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage read command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(f"[dim]Depth: {depth}, Width: {width}, Direction: {direction}[/dim]")
            console.print("[green]MOCK lineage read completed successfully[/green]")
            return

        args = {
            "--guid": guid,
            "--depth": depth,
            "--width": width,
            "--direction": direction,
            "--output": output,
        }

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageRead(args)

        if result:
            console.print("[green]SUCCESS: Lineage read completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Lineage read completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage read: {str(e)}[/red]")


@lineage.command()
@click.option('--entity-guid', required=True, help='Entity GUID for impact analysis')
@click.option('--output-file', help='Export results to file')
@click.pass_context
def impact(ctx, entity_guid, output_file):
    """Analyze lineage impact for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage impact command[/yellow]")
            console.print(f"[dim]Entity GUID: {entity_guid}[/dim]")
            console.print(f"[dim]Output File: {output_file}[/dim]")
            console.print("[green]MOCK lineage impact completed successfully[/green]")
            return

        args = {
            "--entity-guid": entity_guid,
            "--output-file": output_file,
        }

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageImpact(args)

        if result:
            console.print("[green]SUCCESS: Lineage impact analysis completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Lineage impact analysis completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage impact: {str(e)}[/red]")


@lineage.command()
@click.option('--entity-guid', required=True, help='Entity GUID for advanced lineage operations')
@click.option('--direction', default='BOTH', help='Analysis direction: INPUT, OUTPUT, or BOTH')
@click.option('--depth', type=int, default=3, help='Analysis depth')
@click.option('--output-file', help='Export results to file')
@click.pass_context
def analyze(ctx, entity_guid, direction, depth, output_file):
    """Perform advanced lineage analysis"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage analyze command[/yellow]")
            console.print(f"[dim]Entity GUID: {entity_guid}[/dim]")
            console.print(f"[dim]Direction: {direction}, Depth: {depth}[/dim]")
            console.print(f"[dim]Output File: {output_file}[/dim]")
            console.print("[green]MOCK lineage analyze completed successfully[/green]")
            return

        args = {
            "--entity-guid": entity_guid,
            "--direction": direction,
            "--depth": depth,
            "--output-file": output_file,
        }

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageAnalyze(args)

        if result:
            console.print("[green]SUCCESS: Lineage analysis completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Lineage analysis completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage analyze: {str(e)}[/red]")


@lineage.command(name="create-bulk")
@click.argument('json_file', type=click.Path(exists=True))
@click.pass_context
def create_bulk(ctx, json_file):
    """Create lineage relationships in bulk from a JSON file (official API)."""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage create-bulk command[/yellow]")
            console.print(f"[dim]File: {json_file}[/dim]")
            console.print("[green]MOCK lineage create-bulk completed successfully[/green]")
            return

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        args = {'--payloadFile': json_file}
        result = lineage_client.lineageBulkCreate(args)
        console.print("[green][OK] Bulk lineage creation completed successfully[/green]")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage create-bulk: {str(e)}[/red]")


@lineage.command(name="analyze-column")
@click.option('--guid', required=True, help='The globally unique identifier of the entity')
@click.option('--column-name', required=True, help='The name of the column to analyze')
@click.option('--direction', default='BOTH', help='The direction of the lineage: INPUT, OUTPUT or BOTH')
@click.option('--depth', type=int, default=3, help='The number of hops for lineage')
@click.option('--output', default='json', help='Output format: json, table')
@click.pass_context
def analyze_column(ctx, guid, column_name, direction, depth, output):
    """Analyze column-level lineage for a specific entity and column"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage analyze-column command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Column: {column_name}, Direction: {direction}, Depth: {depth}[/dim]")
            console.print("[green]MOCK lineage analyze-column completed successfully[/green]")
            return

        args = {
            "--guid": guid,
            "--columnName": column_name,
            "--direction": direction,
            "--depth": depth,
            "--output": output,
        }

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageAnalyzeColumn(args)

        if result:
            console.print("[green]SUCCESS: Column-level lineage analysis completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Column-level lineage analysis completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage analyze-column: {str(e)}[/red]")


@lineage.command(name="partial")
@click.option('--guid', required=True, help='The globally unique identifier of the entity')
@click.option('--columns', help='Comma-separated list of columns to restrict lineage to (optional)')
@click.option('--relationship-types', help='Comma-separated list of relationship types to include (optional)')
@click.option('--depth', type=int, default=3, help='The number of hops for lineage')
@click.option('--direction', default='BOTH', help='The direction of the lineage: INPUT, OUTPUT or BOTH')
@click.option('--output', default='json', help='Output format: json, table')
@click.pass_context
def partial_lineage(ctx, guid, columns, relationship_types, depth, direction, output):
    """Query partial lineage for an entity (filter by columns/relationship types)"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage partial command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Columns: {columns}, Types: {relationship_types}, Depth: {depth}, Direction: {direction}[/dim]")
            console.print("[green]MOCK lineage partial completed successfully[/green]")
            return

        args = {
            "--guid": guid,
            "--columns": columns,
            "--relationshipTypes": relationship_types,
            "--depth": depth,
            "--direction": direction,
            "--output": output,
        }

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        # Assume backend supports filtering; if not, filter result in CLI
        result = lineage_client.lineageRead(args)
        if columns or relationship_types:
            # Filter result in CLI if backend does not support
            def filter_fn(rel):
                col_ok = True
                type_ok = True
                if columns:
                    col_list = [c.strip() for c in columns.split(",") if c.strip()]
                    col_ok = any(
                        (rel.get("source_column") in col_list or rel.get("target_column") in col_list)
                        for rel in result.get("relations", [])
                    )
                if relationship_types:
                    type_list = [t.strip() for t in relationship_types.split(",") if t.strip()]
                    type_ok = rel.get("relationship_type") in type_list
                return col_ok and type_ok
            if "relations" in result:
                result["relations"] = [rel for rel in result["relations"] if filter_fn(rel)]
        if result:
            console.print("[green]SUCCESS: Partial lineage query completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Partial lineage query completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage partial: {str(e)}[/red]")


@lineage.command(name="impact-report")
@click.option('--entity-guid', required=True, help='Entity GUID for impact analysis')
@click.option('--output-file', help='Export impact report to file (JSON)')
@click.pass_context
def impact_report(ctx, entity_guid, output_file):
    """Generate and export a detailed lineage impact analysis report"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage impact-report command[/yellow]")
            console.print(f"[dim]Entity GUID: {entity_guid}, Output File: {output_file}[/dim]")
            console.print("[green]MOCK lineage impact-report completed successfully[/green]")
            return
        from purviewcli.client.lineage_visualization import LineageReporting, AdvancedLineageAnalyzer
        from purviewcli.client.api_client import PurviewClient
        analyzer = AdvancedLineageAnalyzer(PurviewClient())
        reporting = LineageReporting(analyzer)
        import asyncio
        report = asyncio.run(reporting.generate_impact_report(entity_guid, output_file or f"impact_report_{entity_guid}.json"))
        console.print("[green][OK] Impact analysis report generated successfully[/green]")
        if output_file:
            console.print(f"[cyan]Report saved to {output_file}[/cyan]")
        else:
            console.print(json.dumps(report, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage impact-report: {str(e)}[/red]")


@lineage.command(name="read-by-attribute")
@click.option('--type-name', required=True, help='The name of the entity type')
@click.option('--qualified-name', required=True, help='The qualified name of the entity')
@click.option('--depth', type=int, default=3, help='The number of hops for lineage')
@click.option('--width', type=int, default=6, help='The number of max expanding width in lineage')
@click.option('--direction', default='BOTH', help='The direction of the lineage: INPUT, OUTPUT or BOTH')
@click.option('--offset', type=int, default=0, help='Offset for paginated traversal (if supported)')
@click.option('--limit', type=int, default=100, help='Limit for paginated traversal (if supported)')
@click.option('--output', default='json', help='Output format: json, table')
@click.pass_context
def read_by_attribute(ctx, type_name, qualified_name, depth, width, direction, offset, limit, output):
    """Read lineage for an entity by unique attribute (type and qualified name)"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage read-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}, Depth: {depth}, Direction: {direction}[/dim]")
            console.print("[green]MOCK lineage read-by-attribute completed successfully[/green]")
            return
        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--depth": depth,
            "--width": width,
            "--direction": direction,
            "--offset": offset,
            "--limit": limit,
            "--output": output,
        }
        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageReadUniqueAttribute(args)
        if result:
            console.print("[green][OK] Lineage by attribute read completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Lineage by attribute read completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage read-by-attribute: {str(e)}[/red]")


@lineage.command(name="read")
@click.option('--guid', required=True, help='The GUID of the entity to get lineage for')
@click.option('--direction', required=False, type=click.Choice(['INPUT', 'OUTPUT', 'BOTH'], case_sensitive=False), default='BOTH', help='Lineage direction')
@click.option('--depth', required=False, type=int, default=3, help='Depth of lineage traversal')
@click.pass_context
def read_lineage(ctx, guid, direction, depth):
    """Read lineage information for an entity by GUID"""
    try:
        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        args = {"--guid": guid, "--direction": direction, "--depth": depth}
        result = lineage_client.lineageReadByGuid(args)
        console.print("[green][OK] Lineage read completed successfully[/green]")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage read: {str(e)}[/red]")


@lineage.command(name="create-column")
@click.option('--source-table-guid', required=True, help='GUID of the source table')
@click.option('--target-table-guid', required=True, multiple=True, help='GUID of the target table(s) - can be specified multiple times')
@click.option('--source-column', required=True, help='Name of the source column')
@click.option('--target-column', required=True, multiple=True, help='Name of the target column(s) - can be specified multiple times')
@click.option('--process-name', required=False, help='Name of the transformation process')
@click.option('--description', required=False, help='Description of the column lineage')
@click.option('--owner', required=False, default='data-engineering', help='Owner of the lineage')
@click.option('--validate-types', is_flag=True, default=False, help='Validate column type compatibility')
@click.pass_context
def create_column_lineage(ctx, source_table_guid, target_table_guid, source_column, target_column, process_name, description, owner, validate_types):
    """Create column-level lineage between tables (supports 1 source → N targets)
    
    Examples:
      # Single source to single target
      pvw lineage create-column \\
        --source-table-guid 4abfa830-7f67-4669-a9c9-0ef6f6f60000 \\
        --target-table-guid 3c1d655c-ac7a-4011-8f9e-65f6f6f60000 \\
        --source-column CityKey \\
        --target-column CityKey
      
      # Single source to multiple targets
      pvw lineage create-column \\
        --source-table-guid <source-guid> \\
        --target-table-guid <target1-guid> \\
        --target-table-guid <target2-guid> \\
        --source-column CityKey \\
        --target-column CityKey \\
        --target-column City_ID \\
        --validate-types
    """
    try:
        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        
        # Convert tuples to lists
        target_table_guids = list(target_table_guid)
        target_columns = list(target_column)
        
        # Validate that we have matching number of targets
        if len(target_table_guids) != len(target_columns):
            console.print("[red]ERROR: Number of target tables must match number of target columns[/red]")
            console.print(f"  Target tables: {len(target_table_guids)}")
            console.print(f"  Target columns: {len(target_columns)}")
            return
        
        args = {
            "--source-table-guid": source_table_guid,
            "--target-table-guids": target_table_guids,
            "--source-column": source_column,
            "--target-columns": target_columns,
            "--process-name": process_name or f"{source_column}_Multi_Mapping",
            "--description": description or f"Column-level lineage: {source_column} -> {', '.join(target_columns)}",
            "--owner": owner,
            "--validate-types": validate_types
        }
        
        result = lineage_client.lineageCreateColumnLevel(args)
        
        if result.get("status") == "success":
            console.print("[green]SUCCESS: Column-level lineage created successfully[/green]")
            data = result.get("data", {})
            created = data.get("mutatedEntities", {}).get("CREATE", [])
            if created:
                console.print(f"\n[cyan]Processes created: {len(created)}[/cyan]")
                for i, process in enumerate(created, 1):
                    console.print(f"\n  {i}. {process.get('displayText')}")
                    console.print(f"     GUID: {process.get('guid')}")
                    console.print(f"     Description: {process.get('attributes', {}).get('description')}")
        else:
            console.print(f"[red]ERROR: {result.get('message', 'Unknown error')}[/red]")
            
    except Exception as e:
        console.print(f"[red]ERROR: Error creating column lineage: {str(e)}[/red]")


@lineage.command(name="import-column-csv", help="Batch import column lineage from CSV file")
@click.argument("csv_file", type=click.Path(exists=True))
@click.option("--validate-types", is_flag=True, default=False, help="Validate column type compatibility")
@click.option("--dry-run", is_flag=True, default=False, help="Validate CSV without creating lineage")
def import_column_csv(csv_file, validate_types, dry_run):
    """
    Import column-level lineage from CSV file in batch.
    
    CSV Format:
    source_table_guid,source_column,target_table_guid,target_column,process_name,description,owner
    
    Example CSV content:
    4abfa830-7f67-4669-a9c9-0ef6f6f60000,CityKey,3c1d655c-ac7a-4011-8f9e-65f6f6f60000,CityKey,City_ETL,Map city dimension to sales,data-engineering
    4abfa830-7f67-4669-a9c9-0ef6f6f60000,CityName,21ceaca7-a8eb-4085-afed-335e84241d51,city_name,City_Name_ETL,Map city names,etl-team
    """
    import csv
    from rich.table import Table
    
    try:
        console.print(f"\n[cyan]Reading CSV file: {csv_file}[/cyan]")
        
        # Read CSV file
        rows = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = ['source_table_guid', 'source_column', 'target_table_guid', 'target_column']
            
            # Validate CSV headers
            fieldnames = reader.fieldnames or []
            if not all(col in fieldnames for col in required_columns):
                missing = [col for col in required_columns if col not in fieldnames]
                console.print(f"[red]ERROR: Missing required columns: {', '.join(missing)}[/red]")
                console.print(f"Required: {', '.join(required_columns)}")
                console.print(f"Found: {', '.join(fieldnames)}")
                return
            
            for row in reader:
                rows.append(row)
        
        if not rows:
            console.print("[yellow]WARNING: No data rows found in CSV file[/yellow]")
            return
        
        console.print(f"Found {len(rows)} lineage(s) to create")
        
        # Validation phase
        validation_errors = []
        for idx, row in enumerate(rows, 1):
            # Check required fields
            for field in required_columns:
                if not row.get(field) or row.get(field).strip() == '':
                    validation_errors.append(f"Row {idx}: Missing value for '{field}'")
            
            # Validate GUID format (basic check)
            for guid_field in ['source_table_guid', 'target_table_guid']:
                guid_value = row.get(guid_field, '').strip()
                if guid_value and len(guid_value) != 36:
                    validation_errors.append(f"Row {idx}: Invalid GUID format for '{guid_field}': {guid_value}")
        
        if validation_errors:
            console.print("\n[red]Validation Errors:[/red]")
            for error in validation_errors:
                console.print(f"  - {error}")
            return
        
        console.print("[green]Validation: OK[/green]")
        
        if dry_run:
            console.print("\n[yellow]DRY-RUN mode: No lineages will be created[/yellow]")
            
            # Show preview table
            table = Table(title="Preview: Column Lineages to Create")
            table.add_column("#", style="cyan")
            table.add_column("Source Column", style="green")
            table.add_column("Target Column", style="yellow")
            table.add_column("Process Name", style="magenta")
            
            for idx, row in enumerate(rows, 1):
                table.add_row(
                    str(idx),
                    f"{row['source_column']}",
                    f"{row['target_column']}",
                    row.get('process_name', 'Auto-generated')
                )
            
            console.print(table)
            return
        
        # Creation phase
        console.print("\n[cyan]Creating column lineages...[/cyan]")
        client = Lineage()
        
        success_count = 0
        error_count = 0
        
        for idx, row in enumerate(rows, 1):
            try:
                console.print(f"\n[{idx}/{len(rows)}] {row['source_column']} -> {row['target_column']}...")
                
                args = {
                    "--source-table-guid": row['source_table_guid'].strip(),
                    "--target-table-guids": [row['target_table_guid'].strip()],
                    "--source-column": row['source_column'].strip(),
                    "--target-columns": [row['target_column'].strip()],
                    "--process-name": row.get('process_name', '').strip() or None,
                    "--description": row.get('description', '').strip() or None,
                    "--owner": row.get('owner', 'data-engineering').strip(),
                    "--validate-types": validate_types
                }
                
                result = client.lineageCreateColumnLevel(args)
                
                if result.get('status') == 'success':
                    console.print("  [green]SUCCESS[/green]")
                    success_count += 1
                else:
                    console.print(f"  [red]FAILED: {result.get('message', 'Unknown error')}[/red]")
                    error_count += 1
                
                # Rate limiting: small delay between requests
                import time
                time.sleep(0.2)
                
            except Exception as e:
                console.print(f"  [red]ERROR: {str(e)}[/red]")
                error_count += 1
        
        # Summary
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  [green]SUCCESS: {success_count}[/green]")
        console.print(f"  [red]FAILED: {error_count}[/red]")
        console.print(f"  Total: {len(rows)}")
        
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")


@lineage.command(name="list-column", help="List existing column-level lineage")
@click.option("--source-table-guid", help="Filter by source table GUID")
@click.option("--target-table-guid", help="Filter by target table GUID")
@click.option("--format", "output_format", type=click.Choice(['table', 'json']), default='table', help="Output format")
def list_column_lineage(source_table_guid, target_table_guid, output_format):
    """
    List existing column-level lineage relationships.
    
    This command queries for Process entities that have column-type inputs and outputs,
    representing column-level lineage mappings.
    
    Examples:
      pvw lineage list-column
      pvw lineage list-column --source-table-guid <guid>
      pvw lineage list-column --format json
    """
    from rich.table import Table
    
    try:
        client = Lineage()
        
        # Search for Process entities with column inputs/outputs
        # We'll use the search endpoint to find all Process entities
        from purviewcli.client.endpoint import get_data
        from purviewcli.client.endpoints import get_api_version_params
        
        console.print("\n[cyan]Searching for column-level lineage...[/cyan]")
        
        # Build search query for Process entities
        search_payload = {
            "keywords": "*",
            "filter": {
                "typeName": "Process"
            },
            "limit": 1000
        }
        
        search_result = get_data({
            "app": "catalog",
            "method": "POST",
            "endpoint": "/datamap/api/atlas/v2/search/basic",
            "params": get_api_version_params("datamap"),
            "payload": search_payload
        })
        
        if not search_result or search_result.get('value', []) == []:
            console.print("[yellow]No column lineages found[/yellow]")
            return
        
        entities = search_result.get('value', [])
        console.print(f"Found {len(entities)} Process entities")
        
        # Filter for column-level lineage and apply filters
        column_lineages = []
        
        for entity in entities:
            entity_guid = entity.get('id')
            
            # Get full entity details to check inputs/outputs
            full_entity = get_data({
                "app": "catalog",
                "method": "GET",
                "endpoint": f"/datamap/api/atlas/v2/entity/guid/{entity_guid}",
                "params": get_api_version_params("datamap")
            })
            
            if not full_entity:
                continue
            
            entity_data = full_entity.get('entity', {})
            inputs = entity_data.get('relationshipAttributes', {}).get('inputs', [])
            outputs = entity_data.get('relationshipAttributes', {}).get('outputs', [])
            
            # Check if inputs/outputs are columns (not tables)
            has_column_inputs = any(inp.get('typeName') == 'column' for inp in inputs)
            has_column_outputs = any(out.get('typeName') == 'column' for out in outputs)
            
            if not (has_column_inputs and has_column_outputs):
                continue
            
            # Extract column information
            for inp in inputs:
                if inp.get('typeName') != 'column':
                    continue
                
                for out in outputs:
                    if out.get('typeName') != 'column':
                        continue
                    
                    # Get parent table GUIDs from column qualified names
                    source_qualified_name = inp.get('attributes', {}).get('qualifiedName', '')
                    target_qualified_name = out.get('attributes', {}).get('qualifiedName', '')
                    
                    # Apply filters if provided
                    if source_table_guid or target_table_guid:
                        # Get column details to find parent table
                        source_col = get_data({
                            "app": "catalog",
                            "method": "GET",
                            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{inp.get('guid')}",
                            "params": get_api_version_params("datamap")
                        })
                        
                        target_col = get_data({
                            "app": "catalog",
                            "method": "GET",
                            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{out.get('guid')}",
                            "params": get_api_version_params("datamap")
                        })
                        
                        source_table = source_col.get('entity', {}).get('relationshipAttributes', {}).get('table', {}).get('guid', '')
                        target_table = target_col.get('entity', {}).get('relationshipAttributes', {}).get('table', {}).get('guid', '')
                        
                        if source_table_guid and source_table != source_table_guid:
                            continue
                        if target_table_guid and target_table != target_table_guid:
                            continue
                    
                    column_lineages.append({
                        'process_guid': entity_guid,
                        'process_name': entity_data.get('attributes', {}).get('name', 'N/A'),
                        'description': entity_data.get('attributes', {}).get('description', ''),
                        'source_column': inp.get('displayText', 'N/A'),
                        'source_guid': inp.get('guid', ''),
                        'target_column': out.get('displayText', 'N/A'),
                        'target_guid': out.get('guid', ''),
                        'owner': entity_data.get('attributes', {}).get('owner', 'N/A')
                    })
        
        if not column_lineages:
            console.print("[yellow]No column-level lineages found matching the criteria[/yellow]")
            return
        
        # Output results
        if output_format == 'json':
            import json
            console.print(json.dumps(column_lineages, indent=2))
        else:
            table = Table(title=f"Column Lineages ({len(column_lineages)} found)")
            table.add_column("Process Name", style="cyan", no_wrap=False)
            table.add_column("Source Column", style="green")
            table.add_column("Target Column", style="yellow")
            table.add_column("Owner", style="magenta")
            table.add_column("Process GUID", style="dim")
            
            for lineage in column_lineages:
                table.add_row(
                    lineage['process_name'][:40],
                    lineage['source_column'],
                    lineage['target_column'],
                    lineage['owner'],
                    lineage['process_guid'][:8] + "..."
                )
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")


@lineage.command(name="delete-column", help="Delete a column-level lineage by Process GUID")
@click.option("--process-guid", required=True, help="GUID of the Process entity to delete")
@click.option("--force", is_flag=True, default=False, help="Skip confirmation prompt")
def delete_column_lineage(process_guid, force):
    """
    Delete a column-level lineage Process entity.
    
    This removes the Process entity that represents the column-level lineage mapping,
    which will also remove the associated relationships.
    
    Examples:
      pvw lineage delete-column --process-guid <guid>
      pvw lineage delete-column --process-guid <guid> --force
    """
    from purviewcli.client.endpoint import get_data
    from purviewcli.client.endpoints import get_api_version_params
    
    try:
        # First, get the Process entity details to show what will be deleted
        console.print(f"\n[cyan]Fetching Process entity details...[/cyan]")
        
        entity_details = get_data({
            "app": "catalog",
            "method": "GET",
            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{process_guid}",
            "params": get_api_version_params("datamap")
        })
        
        if not entity_details:
            console.print(f"[red]ERROR: Process entity not found with GUID: {process_guid}[/red]")
            return
        
        entity_data = entity_details.get('entity', {})
        process_name = entity_data.get('attributes', {}).get('name', 'N/A')
        description = entity_data.get('attributes', {}).get('description', 'N/A')
        inputs = entity_data.get('relationshipAttributes', {}).get('inputs', [])
        outputs = entity_data.get('relationshipAttributes', {}).get('outputs', [])
        
        # Display what will be deleted
        console.print(f"\n[bold]Process to delete:[/bold]")
        console.print(f"  Name: {process_name}")
        console.print(f"  Description: {description}")
        console.print(f"  GUID: {process_guid}")
        
        if inputs:
            console.print(f"\n  [green]Inputs ({len(inputs)}):[/green]")
            for inp in inputs:
                console.print(f"    - {inp.get('displayText', 'N/A')} ({inp.get('typeName', 'N/A')})")
        
        if outputs:
            console.print(f"\n  [yellow]Outputs ({len(outputs)}):[/yellow]")
            for out in outputs:
                console.print(f"    - {out.get('displayText', 'N/A')} ({out.get('typeName', 'N/A')})")
        
        # Confirmation unless --force
        if not force:
            console.print(f"\n[bold red]WARNING: This action cannot be undone![/bold red]")
            confirm = input("Type 'yes' to confirm deletion: ")
            if confirm.lower() != 'yes':
                console.print("[yellow]Deletion cancelled[/yellow]")
                return
        
        # Delete the Process entity
        console.print(f"\n[cyan]Deleting Process entity...[/cyan]")
        
        delete_result = get_data({
            "app": "catalog",
            "method": "DELETE",
            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{process_guid}",
            "params": get_api_version_params("datamap")
        })
        
        if delete_result:
            console.print(f"[green]SUCCESS: Column lineage deleted[/green]")
            console.print(f"Process GUID: {process_guid}")
            
            # Show deleted entities
            if isinstance(delete_result, dict):
                deleted = delete_result.get('mutatedEntities', {}).get('DELETE', [])
                if deleted:
                    console.print(f"\nDeleted {len(deleted)} entity(ies):")
                    for entity in deleted:
                        console.print(f"  - {entity.get('displayText', 'N/A')} ({entity.get('guid', 'N/A')[:8]}...)")
        else:
            console.print(f"[red]ERROR: Failed to delete Process entity[/red]")
            
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")


@lineage.command()
@click.option('--source-guid', required=True, help='Source entity GUID')
@click.option('--target-guid', required=True, help='Target entity GUID')
@click.option('--source-type', default='azure_sql_table', help='Source entity type (default: azure_sql_table)')
@click.option('--target-type', default='azure_sql_table', help='Target entity type (default: azure_sql_table)')
@click.option('--column-mapping', default='', help='Optional column mapping JSON')
@click.pass_context
def create_direct(ctx, source_guid, target_guid, source_type, target_type, column_mapping):
    """
    Create direct lineage between two datasets (UI-style, Process hidden).
    
    This creates the same type of lineage as the Purview UI manual lineage,
    where the Process entity exists but is not displayed as a visible box.
    
    Examples:
      pvw lineage create-direct --source-guid <guid1> --target-guid <guid2>
      pvw lineage create-direct --source-guid <guid1> --target-guid <guid2> --source-type azure_sql_view
    """
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage create-direct command[/yellow]")
            return
        
        from purviewcli.client._lineage import Lineage
        
        console.print(f"[cyan]Creating direct lineage...[/cyan]")
        console.print(f"  Source: {source_guid} ({source_type})")
        console.print(f"  Target: {target_guid} ({target_type})")
        
        lineage_client = Lineage()
        args = {
            "--source-guid": source_guid,
            "--target-guid": target_guid,
            "--source-type": source_type,
            "--target-type": target_type,
            "--column-mapping": column_mapping
        }
        
        result = lineage_client.lineageCreateDirect(args)
        
        if result:
            console.print("[green]SUCCESS: Direct lineage created[/green]")
            console.print(json.dumps(result, indent=2))
            
            # Extract relationship GUID if present
            if isinstance(result, dict) and 'guid' in result:
                console.print(f"\n[bold]Relationship GUID:[/bold] {result['guid']}")
        else:
            console.print("[yellow]Direct lineage creation completed (no result returned)[/yellow]")
            
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")
        import traceback
        if ctx.obj and ctx.obj.get("debug"):
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


@lineage.command()
@click.option('--process-guid', required=True, help='GUID of the Process entity')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']), 
              help='Output format')
@click.pass_context
def show_relationships(ctx, process_guid, output_format):
    """Show all relationships for a Process entity."""
    try:
        if ctx.obj and ctx.obj.get("mock"):
            console.print("[yellow][MOCK] lineage show-relationships command[/yellow]")
            return
        
        from purviewcli.client.endpoint import get_data
        from purviewcli.client.endpoints import get_api_version_params
        from rich.table import Table
        
        console.print(f"[cyan]Fetching Process entity: {process_guid}...[/cyan]")
        
        # Read the Process entity
        result = get_data({
            "app": "catalog",
            "method": "GET",
            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{process_guid}",
            "params": get_api_version_params("datamap")
        })
        
        if not result or 'entity' not in result:
            console.print(f"[red]ERROR: Process entity not found[/red]")
            return
        
        entity = result['entity']
        
        # Extract relationship information
        relationships = entity.get('relationshipAttributes', {})
        
        if output_format == 'json':
            console.print(json.dumps(relationships, indent=2))
            return
        
        # Table format
        console.print(f"\n[bold]Process: {entity.get('attributes', {}).get('name', 'N/A')}[/bold]")
        console.print(f"GUID: {process_guid}")
        console.print(f"Type: {entity.get('typeName', 'N/A')}")
        
        # Inputs
        inputs = relationships.get('inputs', [])
        if inputs:
            console.print(f"\n[green]Inputs ({len(inputs)}):[/green]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("GUID", style="dim")
            table.add_column("Qualified Name", style="dim")
            
            for inp in inputs:
                table.add_row(
                    inp.get('displayText', 'N/A'),
                    inp.get('typeName', 'N/A'),
                    inp.get('guid', 'N/A')[:8] + '...' if inp.get('guid') else 'N/A',
                    inp.get('attributes', {}).get('qualifiedName', 'N/A')[:50] + '...' if len(inp.get('attributes', {}).get('qualifiedName', '')) > 50 else inp.get('attributes', {}).get('qualifiedName', 'N/A')
                )
            
            console.print(table)
        
        # Outputs
        outputs = relationships.get('outputs', [])
        if outputs:
            console.print(f"\n[blue]Outputs ({len(outputs)}):[/blue]")
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("GUID", style="dim")
            table.add_column("Qualified Name", style="dim")
            
            for out in outputs:
                table.add_row(
                    out.get('displayText', 'N/A'),
                    out.get('typeName', 'N/A'),
                    out.get('guid', 'N/A')[:8] + '...' if out.get('guid') else 'N/A',
                    out.get('attributes', {}).get('qualifiedName', 'N/A')[:50] + '...' if len(out.get('attributes', {}).get('qualifiedName', '')) > 50 else out.get('attributes', {}).get('qualifiedName', 'N/A')
                )
            
            console.print(table)
        
        # Relationship metadata
        console.print(f"\n[dim]Relationship Types:[/dim]")
        for rel_type, rel_data in relationships.items():
            if rel_type not in ['inputs', 'outputs']:
                console.print(f"  {rel_type}: {type(rel_data).__name__}")
        
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")
        import traceback
        if ctx.obj and ctx.obj.get("debug"):
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


# Remove the duplicate registration and ensure only one 'import' command is registered
# lineage.add_command(import_cmd, name='import')


# Make the lineage group available for import
__all__ = ['lineage']
