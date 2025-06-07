"""
Enhanced CLI Commands with Profile Management
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from ..client.config import config_manager, PurviewProfile, EnvironmentHelper
from ..client.api_client import EnhancedPurviewClient, PurviewConfig
from ..client.csv_operations import CSVBatchProcessor, CSVExporter, ENTITY_TEMPLATES
from ..client.data_quality import DataQualityValidator, DataQualityReport, ENTITY_VALIDATION_RULES

console = Console()

@click.group()
@click.option('--profile', help='Configuration profile to use')
@click.option('--account-name', help='Override Purview account name')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.pass_context
def pv(ctx, profile, account_name, debug):
    """Enhanced Purview CLI with profile management and automation"""
    
    ctx.ensure_object(dict)
    
    # Setup debug mode
    if debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        config_manager.set_config('debug', True)
    
    # Resolve configuration
    resolved_profile = None
    if profile:
        resolved_profile = config_manager.get_profile(profile)
        if not resolved_profile:
            console.print(f"[red]Profile '{profile}' not found[/red]")
            sys.exit(1)
    elif account_name:
        # Create temporary profile from account name
        resolved_profile = PurviewProfile(
            name='temp',
            account_name=account_name
        )
    else:
        # Try to get default profile
        resolved_profile = config_manager.get_profile()
        if not resolved_profile:
            # Try to create from environment
            resolved_profile = config_manager.create_profile_from_env()
    
    if not resolved_profile:
        console.print("[red]No Purview account configured. Use 'pv profile add' to configure or set PURVIEW_NAME environment variable[/red]")
        sys.exit(1)
    
    # Setup environment from profile
    EnvironmentHelper.setup_environment(resolved_profile)
    
    # Create Purview config
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

@pv.group()
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

@pv.group()
def entity():
    """Entity management with validation"""
    pass

@entity.command()
@click.option('--csv-file', required=True, type=click.Path(exists=True), help='CSV file with entity data')
@click.option('--template', type=click.Choice(list(ENTITY_TEMPLATES.keys())), help='Predefined entity template')
@click.option('--config-file', type=click.Path(exists=True), help='Custom mapping configuration file')
@click.option('--validate-only', is_flag=True, help='Only validate data without importing')
@click.option('--quality-report', help='Output file for data quality report')
@click.pass_context
def import_csv(ctx, csv_file, template, config_file, validate_only, quality_report):
    """Import entities from CSV with data quality validation"""
    
    async def _import_with_validation():
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
        
        # Validate data quality
        import pandas as pd
        df = pd.read_csv(csv_file)
        
        validator = DataQualityValidator()
        validation_results = validator.validate_dataframe(df, ENTITY_VALIDATION_RULES)
        
        # Generate quality report
        report = DataQualityReport.generate_report(validation_results)
        
        console.print(f"\n[bold blue]Data Quality Report[/bold blue]")
        console.print(f"Quality Score: {report['summary']['data_quality_score']}/100")
        console.print(f"Total Issues: {report['summary']['total_issues']}")
        console.print(f"  - Errors: {report['summary']['errors']}")
        console.print(f"  - Warnings: {report['summary']['warnings']}")
        
        # Save quality report if requested
        if quality_report:
            DataQualityReport.export_report_to_csv(report, quality_report)
            console.print(f"[green]✓ Quality report saved to {quality_report}[/green]")
        
        # Stop if validation only or if there are errors
        if validate_only:
            console.print("[blue]Validation complete (no import performed)[/blue]")
            return
        
        if report['summary']['errors'] > 0:
            console.print("[red]Cannot proceed with import due to validation errors[/red]")
            return
        
        # Proceed with import
        async with EnhancedPurviewClient(ctx.obj['config']) as client:
            processor = CSVBatchProcessor(client)
            
            def progress_callback(current, total):
                percentage = (current / total) * 100
                console.print(f"Progress: {current}/{total} ({percentage:.1f}%)")
            
            console.print(f"\n[green]Starting import...[/green]")
            results = await processor.process_csv_file(
                csv_file,
                'create_entities',
                entity_template,
                progress_callback
            )
            
            _display_operation_results(results, 'Entity Import')
    
    asyncio.run(_import_with_validation())

@pv.group()
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
            _display_validation_report(report)
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

@pv.group()
def config():
    """Configuration management"""
    pass

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set configuration value"""
    
    # Parse boolean and numeric values
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
        # Show all configuration
        all_config = config_manager._config
        
        table = Table(title="Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        
        for k, v in all_config.items():
            table.add_row(k, str(v))
        
        console.print(table)

# Helper functions
def _create_template_from_config(config_data: Dict) -> 'EntityTemplate':
    """Create EntityTemplate from configuration dictionary"""
    from ..client.csv_operations import ColumnMapping, EntityTemplate
    
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

def _display_validation_report(report: Dict):
    """Display validation report in table format"""
    
    # Summary table
    summary_table = Table(title="Data Quality Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary = report['summary']
    summary_table.add_row("Quality Score", f"{summary['data_quality_score']}/100")
    summary_table.add_row("Total Issues", str(summary['total_issues']))
    summary_table.add_row("Errors", str(summary['errors']))
    summary_table.add_row("Warnings", str(summary['warnings']))
    
    console.print(summary_table)
    
    # Issues by rule
    if report['issues_by_rule']:
        rule_table = Table(title="Issues by Rule")
        rule_table.add_column("Rule", style="cyan")
        rule_table.add_column("Count", style="red")
        
        for rule, count in report['issues_by_rule'].items():
            rule_table.add_row(rule, str(count))
        
        console.print(rule_table)
    
    # Show first few errors
    if report['error_details']:
        console.print(f"\n[red]First {min(5, len(report['error_details']))} Errors:[/red]")
        for error in report['error_details'][:5]:
            console.print(f"  Row {error['row']}: {error['message']}")

if __name__ == '__main__':
    pv()
