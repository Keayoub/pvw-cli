"""
Manage lineage operations in Azure Purview using modular Click-based commands.

All lineage operations are exposed as modular Click-based commands for full CLI visibility and maintainability.

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


@click.group()
@click.pass_context
def lineage(ctx):
    """
    Manage lineage in Azure Purview.
    All lineage operations are exposed as modular Click-based commands for full CLI visibility.
    """
    pass


@lineage.command(name="import")
@click.argument('csv_file', type=click.Path(exists=True))
@click.pass_context
def import_cmd(ctx, csv_file):
    """Import lineage relationships from CSV file (calls client lineageCSVProcess)."""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: lineage import command[/yellow]")
            console.print(f"[dim]File: {csv_file}[/dim]")
            console.print("[green]✓ Mock lineage import completed successfully[/green]")
            return

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        args = {"csv_file": csv_file}
        result = lineage_client.lineageCSVProcess(args)
        console.print("[green]✓ Lineage import completed successfully[/green]")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]✗ Error executing lineage import: {str(e)}[/red]")


@lineage.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.pass_context
def validate(ctx, csv_file):
    """Validate CSV lineage file format and content"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: lineage validate command[/yellow]")
            console.print(f"[dim]File: {csv_file}[/dim]")
            console.print("[green]✓ Mock lineage validate completed successfully[/green]")
            return

        args = {"csv_file": csv_file}

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageCSVValidate(args)

        if result:
            console.print("[green]✓ Lineage validation completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Lineage validation completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing lineage validate: {str(e)}[/red]")


@lineage.command()
@click.argument('output_file', type=click.Path())
@click.option('--num-samples', type=int, default=10,
              help='Number of sample rows to generate')
@click.option('--template', default='basic',
              help='Template type: basic, etl, column-mapping')
@click.pass_context
def sample(ctx, output_file, num_samples, template):
    """Generate sample CSV lineage file"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: lineage sample command[/yellow]")
            console.print(f"[dim]Output File: {output_file}[/dim]")
            console.print(f"[dim]Samples: {num_samples}[/dim]")
            console.print(f"[dim]Template: {template}[/dim]")
            console.print("[green]✓ Mock lineage sample completed successfully[/green]")
            return

        args = {
            "--output-file": output_file,
            "--num-samples": num_samples,
            "--template": template,
        }

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageCSVSample(args)

        if result:
            console.print("[green]✓ Lineage sample generation completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Lineage sample generation completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing lineage sample: {str(e)}[/red]")


@lineage.command()
@click.pass_context
def templates(ctx):
    """Get available CSV lineage templates"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: lineage templates command[/yellow]")
            console.print("[green]✓ Mock lineage templates completed successfully[/green]")
            return

        args = {}

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageCSVTemplates(args)

        if result:
            console.print("[green]✓ Lineage templates retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Lineage templates completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing lineage templates: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: lineage read command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(f"[dim]Depth: {depth}, Width: {width}, Direction: {direction}[/dim]")
            console.print("[green]✓ Mock lineage read completed successfully[/green]")
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
            console.print("[green]✓ Lineage read completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Lineage read completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing lineage read: {str(e)}[/red]")


@lineage.command()
@click.option('--entity-guid', required=True, help='Entity GUID for impact analysis')
@click.option('--output-file', help='Export results to file')
@click.pass_context
def impact(ctx, entity_guid, output_file):
    """Analyze lineage impact for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: lineage impact command[/yellow]")
            console.print(f"[dim]Entity GUID: {entity_guid}[/dim]")
            console.print(f"[dim]Output File: {output_file}[/dim]")
            console.print("[green]✓ Mock lineage impact completed successfully[/green]")
            return

        args = {
            "--entity-guid": entity_guid,
            "--output-file": output_file,
        }

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        result = lineage_client.lineageImpact(args)

        if result:
            console.print("[green]✓ Lineage impact analysis completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Lineage impact analysis completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing lineage impact: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: lineage analyze command[/yellow]")
            console.print(f"[dim]Entity GUID: {entity_guid}[/dim]")
            console.print(f"[dim]Direction: {direction}, Depth: {depth}[/dim]")
            console.print(f"[dim]Output File: {output_file}[/dim]")
            console.print("[green]✓ Mock lineage analyze completed successfully[/green]")
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
            console.print("[green]✓ Lineage analysis completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Lineage analysis completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing lineage analyze: {str(e)}[/red]")


@lineage.command(name="create-bulk")
@click.argument('json_file', type=click.Path(exists=True))
@click.pass_context
def create_bulk(ctx, json_file):
    """Create lineage relationships in bulk from a JSON file (official API)."""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: lineage create-bulk command[/yellow]")
            console.print(f"[dim]File: {json_file}[/dim]")
            console.print("[green]✓ Mock lineage create-bulk completed successfully[/green]")
            return

        from purviewcli.client._lineage import Lineage
        lineage_client = Lineage()
        args = {'--payloadFile': json_file}
        result = lineage_client.lineageBulkCreate(args)
        console.print("[green]✓ Bulk lineage creation completed successfully[/green]")
        console.print(json.dumps(result, indent=2))
    except Exception as e:
        console.print(f"[red]✗ Error executing lineage create-bulk: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: lineage analyze-column command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Column: {column_name}, Direction: {direction}, Depth: {depth}[/dim]")
            console.print("[green]✓ Mock lineage analyze-column completed successfully[/green]")
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
            console.print("[green]✓ Column-level lineage analysis completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Column-level lineage analysis completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing lineage analyze-column: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: lineage partial command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Columns: {columns}, Types: {relationship_types}, Depth: {depth}, Direction: {direction}[/dim]")
            console.print("[green]✓ Mock lineage partial completed successfully[/green]")
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
            console.print("[green]✓ Partial lineage query completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Partial lineage query completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing lineage partial: {str(e)}[/red]")


@lineage.command(name="impact-report")
@click.option('--entity-guid', required=True, help='Entity GUID for impact analysis')
@click.option('--output-file', help='Export impact report to file (JSON)')
@click.pass_context
def impact_report(ctx, entity_guid, output_file):
    """Generate and export a detailed lineage impact analysis report"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: lineage impact-report command[/yellow]")
            console.print(f"[dim]Entity GUID: {entity_guid}, Output File: {output_file}[/dim]")
            console.print("[green]✓ Mock lineage impact-report completed successfully[/green]")
            return
        from purviewcli.client.lineage_visualization import LineageReporting, AdvancedLineageAnalyzer
        from purviewcli.client.api_client import PurviewClient
        analyzer = AdvancedLineageAnalyzer(PurviewClient())
        reporting = LineageReporting(analyzer)
        import asyncio
        report = asyncio.run(reporting.generate_impact_report(entity_guid, output_file or f"impact_report_{entity_guid}.json"))
        console.print("[green]✓ Impact analysis report generated successfully[/green]")
        if output_file:
            console.print(f"[cyan]Report saved to {output_file}[/cyan]")
        else:
            console.print(json.dumps(report, indent=2))
    except Exception as e:
        console.print(f"[red]✗ Error executing lineage impact-report: {str(e)}[/red]")


# Remove the duplicate registration and ensure only one 'import' command is registered
# lineage.add_command(import_cmd, name='import')


# Make the lineage group available for import
__all__ = ['lineage']
