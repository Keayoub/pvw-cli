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
from rich.console import Console
from typing import Optional

console = Console()


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
        result = lineage_client.get_lineage_by_guid(args)
        console.print("[green][OK] Lineage read completed successfully[/green]")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]ERROR: Error executing lineage read: {str(e)}[/red]")


# Remove the duplicate registration and ensure only one 'import' command is registered
# lineage.add_command(import_cmd, name='import')


# Make the lineage group available for import
__all__ = ['lineage']
