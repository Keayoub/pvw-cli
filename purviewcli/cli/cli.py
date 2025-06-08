"""
Purview CLI (pvw)
=================

A comprehensive, automation-friendly command-line interface for Microsoft Purview.

Features:
---------
- Manage and automate Azure Purview data catalog, lineage, glossary, scanning, and more.
- Supports bulk operations, advanced CSV import/export, and validation.
- Integrates with CI/CD, scripting, and data engineering workflows.
- Extensible via plugin system for custom commands and integrations.
- Rich output, progress tracking, and error reporting using 'rich'.

Usage:
------
    pvw [--version] [--help] <command> [<args>...]

Options:
    -v, --version         Show version and exit
    -h, --help            Show help message and exit

Main Command Groups:
--------------------
    entity         Manage Atlas entities (assets, attributes, etc.)
    glossary       Business glossary and vocabulary management
    lineage        Data lineage and impact analysis
    relationship   Define and manage entity relationships
    types          Manage Atlas type definitions
    management     Control plane operations (resource management)
    account        Data plane account and collection management
    insight        Data estate insights and analytics
    policystore    Metadata policies and roles
    scan           Scanning, sources, classification rules, credentials
    search         Search data assets and metadata
    share          Data sharing operations

See 'pvw <command> --help' for details on a specific command.

Authentication:
---------------
- Supports Azure CLI, Managed Identity, Service Principal, and environment variable authentication.
- Set 'PURVIEW_NAME' (account name) via environment variable or command option.

Documentation:
--------------
- For full documentation, see the README or run 'pvw --help'.
- Example: 'pvw glossary readTerm --termGuid <GUID>'

"""

import asyncio
import json
import sys
from docopt import docopt
from pathlib import Path
from typing import Dict, List, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich import print as rprint

from ..client.api_client import PurviewClient, PurviewConfig, BatchOperationProgress
from ..client.csv_operations import CSVBatchProcessor, CSVExporter, ENTITY_TEMPLATES, ColumnMapping, EntityTemplate
from ..client.scanning_operations import ScanningManager, ScanTemplateManager
from ..client.business_rules import BusinessRulesEngine, RuleType, RuleSeverity
from ..client.monitoring_dashboard import MonitoringDashboard, MetricType, AlertSeverity
from ..client.ml_integration import IntelligentDataDiscovery, MLRecommendationEngine, PredictiveAnalytics, MLTaskType
from ..client.lineage_visualization import AdvancedLineageAnalyzer, LineageDirection, LineageDepth, ImpactLevel
from ..plugins.plugin_system import PluginManager, PluginRegistry, PluginType
from ..client.config import config_manager, PurviewProfile, EnvironmentHelper
from ..client.data_quality import DataQualityValidator, DataQualityReport, ENTITY_VALIDATION_RULES
from ..client.csv_lineage_processor import CSVLineageProcessor, LineageCSVTemplates

console = Console()

class PurviewCLI:
    """ Purview CLI with comprehensive automation support"""
    
    def __init__(self, config: PurviewConfig):
        self.config = config
        self.client = None
        self.csv_processor = None
        self.csv_exporter = None
        # Initialize new modules
        self.scanning_manager = None
        self.business_rules_engine = None
        self.monitoring_dashboard = None
        self.ml_discovery_engine = None
        self.ml_recommendation_engine = None
        self.lineage_analyzer = None
        self.plugin_manager = None
    
    async def __aenter__(self):
        """Initialize async resources"""
        self.client = PurviewClient(self.config)
        await self.client.__aenter__()
        self.csv_processor = CSVBatchProcessor(self.client)
        self.csv_exporter = CSVExporter(self.client)
        
        # Initialize advanced modules
        self.scanning_manager = ScanningManager(self.client)
        self.business_rules_engine = BusinessRulesEngine(self.client)
        self.monitoring_dashboard = MonitoringDashboard(self.client)
        self.ml_discovery_engine = IntelligentDataDiscovery(self.client)
        self.ml_recommendation_engine = MLRecommendationEngine(self.client)
        self.lineage_analyzer = AdvancedLineageAnalyzer(self.client)
        self.plugin_manager = PluginManager()
        
        # Load plugins
        await self.plugin_manager.load_plugins()
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup async resources"""
        if self.plugin_manager:
            await self.plugin_manager.cleanup_all_plugins()
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

@click.group()
@click.option('--profile', help='Configuration profile to use')
@click.option('--account-name', help='Override Purview account name')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def main(ctx, profile, account_name, debug):
    """Purview CLI with profile management and automation"""
    ctx.ensure_object(dict)
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        config_manager.set_config('debug', True)
    resolved_profile = None
    if profile:
        resolved_profile = config_manager.get_profile(profile)
        if not resolved_profile:
            console.print(f"[red]Profile '{profile}' not found[/red]")
            sys.exit(1)
    elif account_name:
        resolved_profile = PurviewProfile(
            name='temp',
            account_name=account_name
        )
    else:
        resolved_profile = config_manager.get_profile()
        if not resolved_profile:
            resolved_profile = config_manager.create_profile_from_env()
    if not resolved_profile:
        console.print("[red]No Purview account configured. Use 'pvw profile add' to configure or set PURVIEW_NAME environment variable[/red]")
        sys.exit(1)
    EnvironmentHelper.setup_environment(resolved_profile)
    purview_config = PurviewConfig(
        account_name=resolved_profile.account_name,
        tenant_id=resolved_profile.tenant_id,
        azure_region=resolved_profile.azure_region,
        batch_size=resolved_profile.batch_size,
        max_retries=resolved_profile.max_retries,
        timeout=resolved_profile.timeout
    )
    ctx.obj['config'] = purview_config
    ctx.obj['profile'] = resolved_profile

@main.group()
def profile():
    """Manage connection profiles"""
    pass

@profile.command()
@click.option('--name', required=True, help='Profile name')
@click.option('--account-name', required=True, help='Purview account name')
@click.option('--tenant-id', help='Azure tenant ID')
@click.option('--region', type=click.Choice(['china', 'usgov']), help='Azure region')
@click.option('--batch-size', default=100, help='Default batch size')
@click.option('--set-default', is_flag=True, help='Set as default profile')
def add(name, account_name, tenant_id, region, batch_size, set_default):
    """Add a new connection profile"""
    profile = PurviewProfile(
        name=name,
        account_name=account_name,
        tenant_id=tenant_id,
        azure_region=region,
        batch_size=batch_size
    )
    if config_manager.add_profile(profile):
        console.print(f"[green]✓ Added profile '{name}'[/green]")
        if set_default:
            config_manager.set_default_profile(name)
            console.print(f"[green]✓ Set '{name}' as default profile[/green]")
    else:
        console.print(f"[red]✗ Failed to add profile '{name}'[/red]")

@profile.command()
@click.argument('name')
def remove(name):
    """Remove a connection profile"""
    if config_manager.remove_profile(name):
        console.print(f"[green]✓ Removed profile '{name}'[/green]")
    else:
        console.print(f"[red]✗ Profile '{name}' not found[/red]")

@profile.command('list')
def list_profiles():
    """List all connection profiles"""
    profiles = config_manager.list_profiles()
    default_profile = config_manager.get_config('default_profile')
    if not profiles:
        console.print("[yellow]No profiles configured[/yellow]")
        return
    table = Table(title="Connection Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Account", style="green")
    table.add_column("Region", style="blue")
    table.add_column("Default", style="yellow")
    for name, profile in profiles.items():
        is_default = "✓" if name == default_profile else ""
        region = profile.azure_region or "public"
        table.add_row(name, profile.account_name, region, is_default)
    console.print(table)

@profile.command()
@click.argument('name')
def set_default(name):
    """Set default profile"""
    if config_manager.set_default_profile(name):
        console.print(f"[green]✓ Set '{name}' as default profile[/green]")
    else:
        console.print(f"[red]✗ Profile '{name}' not found[/red]")

@profile.command()
def status():
    """Show current authentication status"""
    auth_info = EnvironmentHelper.get_auth_info()
    table = Table(title="Authentication Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    for key, value in auth_info.items():
        table.add_row(key.replace('_', ' ').title(), value)
    console.print(table)

@main.group()
def config():
    """Configuration management"""
    pass

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set configuration value"""
    if value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
    elif value.isdigit():
        value = int(value)
    config_manager.set_config(key, value)
    console.print(f"[green]✓ Set {key} = {value}[/green]")

@config.command()
@click.argument('key', required=False)
def get(key):
    """Get configuration value(s)"""
    if key:
        value = config_manager.get_config(key)
        console.print(f"{key}: {value}")
    else:
        all_config = config_manager._config
        table = Table(title="Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        for k, v in all_config.items():
            table.add_row(k, str(v))
        console.print(table)

@main.group()
def validate():
    """Data validation commands"""
    pass

@validate.command()
@click.option('--csv-file', required=True, type=click.Path(exists=True), help='CSV file to validate')
@click.option('--template', type=click.Choice(list(ENTITY_TEMPLATES.keys())), help='Entity template for validation')
@click.option('--output', help='Output file for validation report')
@click.option('--format', type=click.Choice(['table', 'csv', 'json']), default='table', help='Output format')
def csv(csv_file, template, output, format):
    """Validate CSV file for entity import"""
    import pandas as pd
    try:
        df = pd.read_csv(csv_file)
        validator = DataQualityValidator()
        validation_rules = ENTITY_VALIDATION_RULES if template else {}
        validation_results = validator.validate_dataframe(df, validation_rules)
        report = DataQualityReport.generate_report(validation_results)
        if format == 'table':
            console.print(json.dumps(report, indent=2))
        elif format == 'json':
            output_data = json.dumps(report, indent=2)
            if output:
                with open(output, 'w') as f:
                    f.write(output_data)
                console.print(f"[green]✓ Report saved to {output}[/green]")
            else:
                rprint(output_data)
        elif format == 'csv' and output:
            DataQualityReport.export_report_to_csv(report, output)
            console.print(f"[green]✓ Report saved to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Error validating CSV: {e}[/red]")

@main.group()
def lineage_csv():
    """CSV-based lineage operations"""
    pass

@lineage_csv.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--batch-size', default=100, type=int, help='Number of relationships to process per batch')
@click.option('--validate-entities', is_flag=True, help='Validate that entities exist before creating lineage')
@click.option('--create-missing-entities', is_flag=True, help='Create placeholder entities if they don\'t exist')
@click.option('--progress', is_flag=True, help='Show detailed progress during processing')
@click.pass_context
def process(ctx, csv_file, batch_size, validate_entities, create_missing_entities, progress):
    """Process lineage relationships from CSV file"""
    async def _process_lineage():
        try:
            client_config = ctx.obj.get('config') or ctx.obj.get('resolved_profile')
            if not client_config:
                console.print("[red]Error: No active configuration found[/red]")
                return
            async with PurviewClient(client_config.account_name, client_config.get_credential()) as client:
                processor = CSVLineageProcessor(client)
                console.print(f"[blue]Processing lineage from: {csv_file}[/blue]")
                console.print(f"[dim]Batch size: {batch_size}, Validate: {validate_entities}, Create missing: {create_missing_entities}[/dim]")
                def progress_callback(percent, processed, failed):
                    if progress:
                        console.print(f"[green]Progress: {percent:.1f}% - Processed: {processed}, Failed: {failed}[/green]")
                with console.status("[bold green]Processing lineage relationships..."):
                    result = await processor.process_lineage_csv(
                        csv_file_path=csv_file,
                        batch_size=batch_size,
                        validate_entities=validate_entities,
                        create_missing_entities=create_missing_entities,
                        progress_callback=progress_callback if progress else None
                    )
                if result.success:
                    console.print("\n[bold green]✅ Lineage processing completed![bold green]")
                    table = Table(title="Processing Results")
                    table.add_column("Metric", style="cyan")
                    table.add_column("Value", style="magenta")
                    table.add_row("Total Relationships", str(result.total_rows))
                    table.add_row("Successfully Processed", str(result.processed))
                    table.add_row("Failed", str(result.failed))
                    table.add_row("Success Rate", f"{result.success_rate:.1f}%")
                    table.add_row("Processing Time", f"{result.processing_time:.2f} seconds")
                    console.print(table)
                    if result.errors:
                        console.print(f"\n[yellow]⚠️ {len(result.errors)} errors encountered:[/yellow]")
                        for i, error in enumerate(result.errors[:5], 1):
                            console.print(f"   {i}. {error}")
                        if len(result.errors) > 5:
                            console.print(f"   ... and {len(result.errors) - 5} more errors")
                else:
                    console.print("[bold red]❌ Lineage processing failed![bold red]")
                    for error in result.errors:
                        console.print(f"[red]Error: {error}[/red]")
        except Exception as e:
            console.print(f"[red]Error processing lineage CSV: {str(e)}[/red]")
    asyncio.run(_process_lineage())

@lineage_csv.command('generate-sample')
@click.argument('output_file', type=click.Path())
@click.option('--num-samples', default=10, type=int, help='Number of sample relationships to generate')
@click.option('--template', type=click.Choice(['basic', 'etl', 'column-mapping']), default='basic', help='Template type')
@click.pass_context
def generate_sample(ctx, output_file, num_samples, template):
    """Generate sample CSV file for lineage"""
    async def _generate_sample():
        try:
            client_config = ctx.obj.get('config') or ctx.obj.get('resolved_profile')
            if not client_config:
                console.print("[red]Error: No active configuration found[/red]")
                return
            async with PurviewClient(client_config.account_name, client_config.get_credential()) as client:
                processor = CSVLineageProcessor(client)
                console.print(f"[blue]Generating sample CSV: {output_file}[/blue]")
                console.print(f"[dim]Template: {template}, Samples: {num_samples}[/dim]")
                output_path = processor.generate_sample_csv(output_file, num_samples)
                console.print(f"[green]✅ Sample CSV generated: {output_path}[green]")
                templates = LineageCSVTemplates()
                if template == 'basic':
                    template_info = templates.get_basic_template()
                elif template == 'etl':
                    template_info = templates.get_etl_template()
                elif template == 'column-mapping':
                    template_info = templates.get_column_mapping_template()
                else:
                    template_info = templates.get_basic_template()
                console.print(f"\n[cyan]Template: {template_info['name']}[cyan]")
                console.print(f"[dim]{template_info['description']}[dim]")
        except Exception as e:
            console.print(f"[red]Error generating sample CSV: {str(e)}[/red]")
    asyncio.run(_generate_sample())

@lineage_csv.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.pass_context  
def validate(ctx, csv_file):
    """Validate CSV file format for lineage"""
    async def _validate_csv():
        try:
            client_config = ctx.obj.get('config') or ctx.obj.get('resolved_profile')
            if not client_config:
                console.print("[red]Error: No active configuration found[/red]")
                return
            async with PurviewClient(client_config.account_name, client_config.get_credential()) as client:
                processor = CSVLineageProcessor(client)
                console.print(f"[blue]Validating CSV file: {csv_file}[blue]")
                validation_result = processor.validate_csv_file(csv_file)
                if validation_result['is_valid']:
                    console.print("[bold green]✅ CSV file is valid![bold green]")
                    table = Table(title="Validation Details")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="magenta")
                    table.add_row("Total Rows", str(validation_result['total_rows']))
                    table.add_row("File Size (MB)", f"{validation_result['file_size_mb']:.2f}")
                    table.add_row("Columns Found", str(len(validation_result['columns_found'])))
                    if validation_result['relationship_types_found']:
                        table.add_row("Relationship Types", ', '.join(validation_result['relationship_types_found']))
                    console.print(table)
                    if validation_result['preview_rows']:
                        console.print("\n[cyan]Preview (first 3 rows):[cyan]")
                        preview_table = Table()
                        if validation_result['preview_rows']:
                            for col in validation_result['preview_rows'][0].keys():
                                preview_table.add_column(col[:20], overflow="ellipsis")
                        for row in validation_result['preview_rows']:
                            preview_table.add_row(*[str(v)[:50] for v in row.values()])
                        console.print(preview_table)
                else:
                    console.print("[bold red]❌ CSV validation failed![bold red]")
                    for error in validation_result['errors']:
                        console.print(f"[red]• {error}[/red]")
        except Exception as e:
            console.print(f"[red]Error validating CSV file: {str(e)}[/red]")
    asyncio.run(_validate_csv())

@lineage_csv.command()
def templates():
    """Show available CSV lineage templates"""
    templates = LineageCSVTemplates()
    console.print("[bold blue]Available CSV Lineage Templates[bold blue]\n")
    template_info = [
        templates.get_basic_template(),
        templates.get_etl_template(), 
        templates.get_column_mapping_template()
    ]
    for template in template_info:
        console.print(f"[bold cyan]{template['name']}[bold cyan]")
        console.print(f"[dim]{template['description']}[dim]")
        console.print(f"[green]Columns: {', '.join(template['columns'])}[green]")
        console.print()

@main.group()
@click.pass_context
def entity(ctx):
    """Entity management operations"""
    pass

@entity.command()
@click.option('--guid', required=True, help='Entity GUID')
@click.option('--include-relationships', is_flag=True, help='Include entity relationships')
@click.option('--output', type=click.Choice(['json', 'table']), default='json', help='Output format')
@click.pass_context
def get(ctx, guid, include_relationships, output):
    """Get entity by GUID"""
    
    async def _get_entity():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                entity = await cli.client.get_entity(
                    guid, 
                    minExtInfo=True,
                    ignoreRelationships=not include_relationships
                )
                
                if output == 'table':
                    _display_entity_table(entity)
                else:
                    rprint(json.dumps(entity, indent=2))
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_get_entity())

@entity.command()
@click.option('--csv-file', required=True, type=click.Path(exists=True), help='CSV file with entity data')
@click.option('--template', type=click.Choice(list(ENTITY_TEMPLATES.keys())), help='Predefined entity template')
@click.option('--config-file', type=click.Path(exists=True), help='Custom mapping configuration file')
@click.option('--dry-run', is_flag=True, help='Validate data without creating entities')
@click.pass_context
def import_csv(ctx, csv_file, template, config_file, dry_run):
    """Import entities from CSV file"""
    
    async def _import_entities():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Load template or configuration
                if config_file:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                        entity_template = _create_template_from_config(config_data)
                elif template:
                    entity_template = ENTITY_TEMPLATES[template]
                else:
                    console.print("[red]Error: Either --template or --config-file must be specified[/red]")
                    return
                
                # Show progress
                progress = Progress(console=console)
                task = progress.add_task("[green]Processing entities...", total=100)
                
                def progress_callback(current, total):
                    percentage = (current / total) * 100
                    progress.update(task, completed=percentage)
                
                with progress:
                    if dry_run:
                        # Validate only
                        import pandas as pd
                        df = pd.read_csv(csv_file)
                        validation_errors = cli.csv_processor._validate_csv_structure(df, entity_template)
                        
                        if validation_errors:
                            console.print("[red]Validation errors:[/red]")
                            for error in validation_errors:
                                console.print(f"  - {error}")
                        else:
                            console.print(f"[green]✓ CSV validation passed. {len(df)} entities ready for import.[/green]")
                    else:
                        # Import entities
                        results = await cli.csv_processor.process_csv_file(
                            csv_file, 
                            'create_entities', 
                            entity_template,
                            progress_callback
                        )
                        
                        _display_operation_results(results, 'Entity Import')
                        
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_import_entities())

@entity.command()
@click.option('--csv-file', required=True, type=click.Path(exists=True), help='CSV file with entity updates')
@click.option('--template', type=click.Choice(list(ENTITY_TEMPLATES.keys())), help='Predefined entity template')
@click.option('--config-file', type=click.Path(exists=True), help='Custom mapping configuration file')
@click.pass_context
def update_csv(ctx, csv_file, template, config_file):
    """Update entities from CSV file"""
    
    async def _update_entities():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Load template or configuration
                if config_file:
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)
                        entity_template = _create_template_from_config(config_data)
                elif template:
                    entity_template = ENTITY_TEMPLATES[template]
                else:
                    console.print("[red]Error: Either --template or --config-file must be specified[/red]")
                    return
                
                # Show progress
                progress = Progress(console=console)
                task = progress.add_task("[green]Updating entities...", total=100)
                
                def progress_callback(current, total):
                    percentage = (current / total) * 100
                    progress.update(task, completed=percentage)
                
                with progress:
                    results = await cli.csv_processor.process_csv_file(
                        csv_file, 
                        'update_entities', 
                        entity_template,
                        progress_callback
                    )
                    
                    _display_operation_results(results, 'Entity Update')
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_update_entities())

@entity.command()
@click.option('--query', required=True, help='Search query for entities')
@click.option('--output-file', required=True, help='Output CSV file path')
@click.option('--columns', help='Comma-separated list of columns to export')
@click.option('--limit', default=1000, help='Maximum number of entities to export')
@click.pass_context
def export_csv(ctx, query, output_file, columns, limit):
    """Export entities to CSV file"""
    
    async def _export_entities():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                column_list = columns.split(',') if columns else None
                
                # Update search with limit
                search_results = await cli.client.search_entities(query, limit=limit)
                
                result = await cli.csv_exporter.export_entities(
                    query,
                    output_file,
                    column_list
                )
                
                if result['status'] == 'success':
                    console.print(f"[green]✓ {result['message']}[/green]")
                    console.print(f"Columns: {', '.join(result.get('columns', []))}")
                else:
                    console.print(f"[red]Error: {result['message']}[/red]")
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_export_entities())

@main.group()
@click.pass_context
def glossary(ctx):
    """Glossary management operations"""
    pass

@glossary.command()
@click.option('--csv-file', required=True, type=click.Path(exists=True), help='CSV file with glossary terms')
@click.option('--glossary-guid', required=True, help='Target glossary GUID')
@click.pass_context
def import_terms(ctx, csv_file, glossary_guid):
    """Import glossary terms from CSV"""
    
    async def _import_terms():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Create a simple template for glossary terms
                template = EntityTemplate(
                    type_name='AtlasGlossaryTerm',
                    default_attributes={'glossaryGuid': glossary_guid}
                )
                
                progress = Progress(console=console)
                task = progress.add_task("[green]Creating glossary terms...", total=100)
                
                def progress_callback(current, total):
                    percentage = (current / total) * 100
                    progress.update(task, completed=percentage)
                
                with progress:
                    results = await cli.csv_processor.process_csv_file(
                        csv_file,
                        'create_glossary_terms',
                        template,
                        progress_callback
                    )
                    
                    _display_operation_results(results, 'Glossary Terms Import')
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_import_terms())

@glossary.command()
@click.option('--csv-file', required=True, type=click.Path(exists=True), help='CSV file with term assignments')
@click.pass_context
def assign_terms(ctx, csv_file):
    """Assign glossary terms to entities from CSV"""
    
    async def _assign_terms():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                template = EntityTemplate(type_name='assignment')  # Placeholder template
                
                progress = Progress(console=console)
                task = progress.add_task("[green]Assigning terms...", total=100)
                
                def progress_callback(current, total):
                    percentage = (current / total) * 100
                    progress.update(task, completed=percentage)
                
                with progress:
                    results = await cli.csv_processor.process_csv_file(
                        csv_file,
                        'assign_glossary_terms',
                        template,
                        progress_callback
                    )
                    
                    _display_operation_results(results, 'Glossary Term Assignment')
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_assign_terms())

@main.group()
@click.pass_context
def scanning(ctx):
    """Advanced scanning operations and automation"""
    pass

@scanning.command()
@click.option('--data-source', required=True, help='Data source name')
@click.option('--scan-name', required=True, help='Scan name')
@click.option('--wait', is_flag=True, help='Wait for scan completion')
@click.option('--output', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def run_scan(ctx, data_source, scan_name, wait, output):
    """Run a scan and optionally wait for completion"""
    
    async def _run_scan():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Start scan
                result = await cli.scanning_manager.run_scan(data_source, scan_name)
                run_id = result.get('runId')
                
                console.print(f"[green]Scan started with ID: {run_id}[/green]")
                
                if wait and run_id:
                    # Wait for completion
                    console.print("[cyan]Waiting for scan completion...[/cyan]")
                    final_status = await cli.scanning_manager.wait_for_scan_completion(
                        data_source, scan_name, run_id
                    )
                    
                    if output == 'table':
                        table = Table(title="Scan Results")
                        table.add_column("Status", style="green")
                        table.add_column("Details")
                        table.add_row(final_status.get('status', 'Unknown'), str(final_status))
                        console.print(table)
                    else:
                        rprint(json.dumps(final_status, indent=2))
                else:
                    if output == 'json':
                        rprint(json.dumps(result, indent=2))
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_run_scan())

@scanning.command()
@click.option('--output-file', required=True, help='Output file path for scan report')
@click.option('--include-failed', is_flag=True, help='Include failed scans in report')
@click.pass_context
def generate_report(ctx, output_file, include_failed):
    """Generate comprehensive scanning report"""
    
    async def _generate_report():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                report = await cli.scanning_manager.generate_scan_report(
                    include_failed_scans=include_failed
                )
                
                # Save report
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                console.print(f"[green]Scan report generated: {output_file}[/green]")
                
                # Display summary
                summary = report.get('summary', {})
                table = Table(title="Scan Report Summary")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                for key, value in summary.items():
                    table.add_row(key.replace('_', ' ').title(), str(value))
                
                console.print(table)
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_generate_report())

@main.group()
@click.pass_context
def governance(ctx):
    """Business rules and governance operations"""
    pass

@governance.command()
@click.option('--entity-guid', required=True, help='Entity GUID to check')
@click.option('--rule-types', multiple=True, help='Specific rule types to check')
@click.option('--output', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def check_compliance(ctx, entity_guid, rule_types, output):
    """Check entity compliance against business rules"""
    
    async def _check_compliance():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Get entity
                entity = await cli.client.get_entity(entity_guid)
                
                # Run compliance check
                violations = await cli.business_rules_engine.check_entity_compliance(entity)
                
                if output == 'table':
                    table = Table(title=f"Compliance Check: {entity.get('attributes', {}).get('name', 'Unknown')}")
                    table.add_column("Rule", style="cyan")
                    table.add_column("Severity", style="red")
                    table.add_column("Description", style="yellow")
                    table.add_column("Action Required")
                    
                    for violation in violations:
                        severity_color = {
                            'critical': 'red',
                            'error': 'red',
                            'warning': 'yellow',
                            'info': 'blue'
                        }.get(violation.severity.value, 'white')
                        
                        table.add_row(
                            violation.rule_name,
                            f"[{severity_color}]{violation.severity.value.upper()}[/{severity_color}]",
                            violation.description,
                            violation.recommended_action
                        )
                    
                    console.print(table)
                    
                    if not violations:
                        console.print("[green]✓ No compliance violations found[/green]")
                else:
                    violation_data = [
                        {
                            'rule_name': v.rule_name,
                            'severity': v.severity.value,
                            'description': v.description,
                            'recommended_action': v.recommended_action,
                            'timestamp': v.timestamp.isoformat()
                        }
                        for v in violations
                    ]
                    rprint(json.dumps(violation_data, indent=2))
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_check_compliance())

@governance.command()
@click.option('--output-file', required=True, help='Output file for compliance report')
@click.option('--entity-type', help='Filter by entity type')
@click.pass_context
def compliance_report(ctx, output_file, entity_type):
    """Generate comprehensive compliance report"""
    
    async def _compliance_report():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                report = await cli.business_rules_engine.generate_compliance_report(
                    entity_type_filter=entity_type
                )
                
                # Save report
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2)
                
                console.print(f"[green]Compliance report generated: {output_file}[/green]")
                
                # Display summary
                summary = report.get('summary', {})
                table = Table(title="Compliance Report Summary")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Total Entities Checked", str(summary.get('total_entities_checked', 0)))
                table.add_row("Compliant Entities", str(summary.get('compliant_entities', 0)))
                table.add_row("Total Violations", str(summary.get('total_violations', 0)))
                table.add_row("Critical Violations", str(summary.get('critical_violations', 0)))
                
                console.print(table)
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_compliance_report())

@main.group()
@click.pass_context
def monitoring(ctx):
    """Real-time monitoring and alerting"""
    pass

@monitoring.command()
@click.option('--refresh-interval', default=30, help='Refresh interval in seconds')
@click.pass_context
def dashboard(ctx, refresh_interval):
    """Start real-time monitoring dashboard"""
    
    async def _start_dashboard():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                console.print("[cyan]Starting monitoring dashboard...[/cyan]")
                console.print("[yellow]Press Ctrl+C to stop[/yellow]")
                
                await cli.monitoring_dashboard.start_monitoring(refresh_interval)
                
            except KeyboardInterrupt:
                console.print("[green]Dashboard stopped[/green]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_start_dashboard())

@monitoring.command()
@click.option('--output-file', required=True, help='Output file for metrics')
@click.option('--format', type=click.Choice(['json', 'csv']), default='json', help='Export format')
@click.pass_context
def export_metrics(ctx, output_file, format):
    """Export collected metrics"""
    
    async def _export_metrics():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Collect current metrics
                await cli.monitoring_dashboard.collect_metrics()
                
                # Export metrics
                cli.monitoring_dashboard.export_metrics(output_file, format)
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_export_metrics())

@main.group()
@click.pass_context
def ml(ctx):
    """Machine learning powered analysis"""
    pass

@ml.command()
@click.option('--entity-guid', required=True, help='Entity GUID for similarity search')
@click.option('--threshold', default=0.7, help='Similarity threshold (0.0-1.0)')
@click.option('--output', type=click.Choice(['json', 'table']), default='table', help='Output format')
@click.pass_context
def find_similar(ctx, entity_guid, threshold, output):
    """Find similar datasets using ML"""
    pass

@ml.command()
@click.option('--entity-guid', required=True, help='Entity GUID for recommendations')
@click.option('--output-file', help='Output file for detailed recommendations')
@click.pass_context
def recommendations(ctx, entity_guid, output_file):
    """Generate ML-powered governance recommendations"""
    pass

@main.group()
@click.pass_context
def lineage(ctx):
    """Advanced lineage analysis and visualization"""
    pass

@lineage.command()
@click.option('--entity-guid', required=True, help='Entity GUID for lineage analysis')
@click.option('--direction', type=click.Choice(['input', 'output', 'both']), default='both', help='Lineage direction')
@click.option('--depth', type=click.Choice(['1', '3', '5', 'complete']), default='3', help='Analysis depth')
@click.option('--output-file', help='Export lineage graph to file')
@click.pass_context
def analyze(ctx, entity_guid, direction, depth, output_file):
    """Analyze comprehensive lineage for an entity"""
    pass

@lineage.command()
@click.option('--entity-guid', required=True, help='Entity GUID for impact analysis')
@click.option('--output-file', help='Export impact report to file')
@click.pass_context
def impact(ctx, entity_guid, output_file):
    """Perform impact analysis for an entity"""
    pass

@main.group()
@click.pass_context
def plugins(ctx):
    """Plugin management and operations"""
    pass

@plugins.command('list')
@click.pass_context
def list_plugins(ctx):
    """List all available plugins"""
    
    async def _list_plugins():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                plugin_table = cli.plugin_manager.list_plugins()
                console.print(plugin_table)
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_list_plugins())

@plugins.command()
@click.option('--plugin-name', required=True, help='Plugin name')
@click.pass_context
def info(ctx, plugin_name):
    """Get detailed information about a plugin"""
    
    async def _plugin_info():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                info = cli.plugin_manager.get_plugin_info(plugin_name)
                
                if info:
                    table = Table(title=f"Plugin Info: {plugin_name}")
                    table.add_column("Property", style="cyan")
                    table.add_column("Value", style="green")
                    
                    for key, value in info.items():
                        if isinstance(value, list):
                            value = ', '.join(value)
                        elif isinstance(value, dict):
                            value = json.dumps(value, indent=2)
                        table.add_row(key.replace('_', ' ').title(), str(value))
                    
                    console.print(table)
                else:
                    console.print(f"[red]Plugin '{plugin_name}' not found[/red]")
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_plugin_info())

@plugins.command()
@click.option('--plugin-name', required=True, help='Plugin name')
@click.option('--operation', required=True, help='Operation to execute')
@click.option('--params', help='JSON parameters for the operation')
@click.pass_context
def execute(ctx, plugin_name, operation, params):
    """Execute a plugin operation"""
    
    async def _execute_plugin():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Parse parameters
                kwargs = {}
                if params:
                    kwargs = json.loads(params)
                
                # Execute operation
                result = await cli.plugin_manager.execute_plugin_operation(
                    plugin_name, operation, **kwargs
                )
                
                console.print(f"[green]Operation '{operation}' completed successfully[/green]")
                rprint(json.dumps(result, indent=2))
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_execute_plugin())

# Helper functions
def _create_template_from_config(config_data: Dict) -> EntityTemplate:
    """Create EntityTemplate from configuration dictionary"""
    
    mappings = []
    for mapping_data in config_data.get('attribute_mappings', []):
        mappings.append(ColumnMapping(
            csv_column=mapping_data['csv_column'],
            purview_attribute=mapping_data['purview_attribute'],
            data_type=mapping_data.get('data_type', 'string'),
            required=mapping_data.get('required', False),
            default_value=mapping_data.get('default_value')
        ))
    
    return EntityTemplate(
        type_name=config_data['type_name'],
        attribute_mappings=mappings,
        qualified_name_template=config_data.get('qualified_name_template', '{name}@{account_name}'),
        collection_name=config_data.get('collection_name'),
        default_attributes=config_data.get('default_attributes', {})
    )

def _display_entity_table(entity: Dict):
    """Display entity information in table format"""
    
    table = Table(title="Entity Details")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("GUID", entity.get('guid', 'N/A'))
    table.add_row("Type", entity.get('typeName', 'N/A'))
    table.add_row("Status", entity.get('status', 'N/A'))
    table.add_row("Created By", entity.get('createdBy', 'N/A'))
    table.add_row("Updated By", entity.get('updatedBy', 'N/A'))
    
    # Show key attributes
    attributes = entity.get('attributes', {})
    for key in ['name', 'qualifiedName', 'owner', 'description']:
        if key in attributes:
            table.add_row(key.title(), str(attributes[key]))
    
    console.print(table)

def _display_operation_results(results: Dict, operation_name: str):
    """Display operation results in a formatted way"""
    
    summary = results.get('summary', {})
    
    console.print(f"\n[bold blue]{operation_name} Results[/bold blue]")
    console.print(f"Total processed: {summary.get('total', 0)}")
    console.print(f"[green]Successful: {summary.get('created', summary.get('updated', summary.get('successful_assignments', 0)))}[/green]")
    console.print(f"[red]Failed: {summary.get('failed', summary.get('failed_assignments', len(results.get('errors', []))))}[/red]")
    
    # Show errors if any
    errors = results.get('errors', [])
    if errors:
        console.print(f"\n[red]Errors ({len(errors)}):[/red]")
        for error in errors[:10]:  # Show first 10 errors
            console.print(f"  - {error}")
        if len(errors) > 10:
            console.print(f"  ... and {len(errors) - 10} more errors")

def _display_lineage_graph(lineage: Dict):
    """Display lineage in a simple graph format"""
    # This would need a more sophisticated graph visualization library
    # For now, just show the structure
    console.print("[bold blue]Lineage Structure[/bold blue]")
    
    relations = lineage.get('relations', [])
    for relation in relations:
        from_entity = relation.get('fromEntityId', 'Unknown')
        to_entity = relation.get('toEntityId', 'Unknown')
        console.print(f"{from_entity} → {to_entity}")

def _display_insights_table(insights: Dict):
    """Display insights in table format"""
    
    table = Table(title="Asset Distribution")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    # This would depend on the actual structure of insights data
    for key, value in insights.items():
        if isinstance(value, (str, int, float)):
            table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(table)


if __name__ == '__main__':
    main()
