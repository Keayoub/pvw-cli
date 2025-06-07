"""
Enhanced CLI Command Handler
Provides comprehensive command-line interface for Purview operations
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich import print as rprint

from ..client.api_client import EnhancedPurviewClient, PurviewConfig, BatchOperationProgress
from ..client.csv_operations import CSVBatchProcessor, CSVExporter, ENTITY_TEMPLATES, ColumnMapping, EntityTemplate
from ..client.scanning_operations import ScanningManager, ScanTemplateManager
from ..client.business_rules import BusinessRulesEngine, RuleType, RuleSeverity
from ..client.monitoring_dashboard import MonitoringDashboard, MetricType, AlertSeverity
from ..client.ml_integration import IntelligentDataDiscovery, MLRecommendationEngine, PredictiveAnalytics, MLTaskType
from ..client.lineage_visualization import AdvancedLineageAnalyzer, LineageDirection, LineageDepth, ImpactLevel
from ..plugins.plugin_system import PluginManager, PluginRegistry, PluginType

console = Console()

class PurviewCLI:
    """Enhanced Purview CLI with comprehensive automation support"""
    
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
        self.client = EnhancedPurviewClient(self.config)
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
@click.option('--account-name', required=True, help='Purview account name')
@click.option('--tenant-id', help='Azure tenant ID')
@click.option('--region', help='Azure region (china, usgov, or leave empty for public)')
@click.option('--batch-size', default=100, help='Batch size for bulk operations')
@click.option('--max-retries', default=3, help='Maximum retry attempts')
@click.option('--timeout', default=30, help='Request timeout in seconds')
@click.pass_context
def cli(ctx, account_name, tenant_id, region, batch_size, max_retries, timeout):
    """Enhanced Purview CLI for comprehensive data catalog management"""
    
    config = PurviewConfig(
        account_name=account_name,
        tenant_id=tenant_id,
        azure_region=region,
        batch_size=batch_size,
        max_retries=max_retries,
        timeout=timeout
    )
    
    ctx.ensure_object(dict)
    ctx.obj['config'] = config

@cli.group()
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

@cli.group()
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

@cli.group()
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

@cli.group()
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

@cli.group()
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

@cli.group()
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
    
    async def _find_similar():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                similar_datasets = await cli.ml_discovery_engine.discover_similar_datasets(
                    entity_guid, threshold
                )
                
                if output == 'table':
                    table = Table(title="Similar Datasets")
                    table.add_column("Name", style="cyan")
                    table.add_column("Type", style="yellow")
                    table.add_column("Similarity", style="green")
                    table.add_column("GUID", style="blue")
                    
                    for dataset in similar_datasets:
                        table.add_row(
                            dataset['name'],
                            dataset['entity'].get('typeName', 'Unknown'),
                            f"{dataset['similarity_score']:.3f}",
                            dataset['guid']
                        )
                    
                    console.print(table)
                else:
                    rprint(json.dumps(similar_datasets, indent=2))
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_find_similar())

@ml.command()
@click.option('--entity-guid', required=True, help='Entity GUID for recommendations')
@click.option('--output-file', help='Output file for detailed recommendations')
@click.pass_context
def recommendations(ctx, entity_guid, output_file):
    """Generate ML-powered governance recommendations"""
    
    async def _generate_recommendations():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                insights = await cli.ml_recommendation_engine.generate_governance_recommendations(
                    entity_guid
                )
                
                # Display summary
                table = Table(title="ML Recommendations")
                table.add_column("Type", style="cyan")
                table.add_column("Title", style="yellow")
                table.add_column("Confidence", style="green")
                table.add_column("Description")
                
                for insight in insights:
                    confidence_color = {
                        'very_high': 'green',
                        'high': 'green',
                        'medium': 'yellow',
                        'low': 'red'
                    }.get(insight.confidence.value, 'white')
                    
                    table.add_row(
                        insight.task_type.value,
                        insight.title,
                        f"[{confidence_color}]{insight.confidence.value}[/{confidence_color}]",
                        insight.description[:50] + "..." if len(insight.description) > 50 else insight.description
                    )
                
                console.print(table)
                
                # Export detailed recommendations if requested
                if output_file:
                    cli.ml_recommendation_engine.export_insights(insights, output_file)
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_generate_recommendations())

@cli.group()
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
    
    async def _analyze_lineage():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Convert string parameters to enums
                lineage_direction = {
                    'input': LineageDirection.INPUT,
                    'output': LineageDirection.OUTPUT,
                    'both': LineageDirection.BOTH
                }[direction]
                
                lineage_depth = {
                    '1': LineageDepth.IMMEDIATE,
                    '3': LineageDepth.EXTENDED,
                    '5': LineageDepth.DEEP,
                    'complete': LineageDepth.COMPLETE
                }[depth]
                
                # Get comprehensive lineage
                lineage_graph = await cli.lineage_analyzer.get_comprehensive_lineage(
                    entity_guid, lineage_direction, lineage_depth
                )
                
                # Display summary
                summary_table = cli.lineage_analyzer.create_lineage_summary_table(lineage_graph)
                console.print(summary_table)
                
                # Display tree visualization
                lineage_tree = cli.lineage_analyzer.visualize_lineage_tree(lineage_graph)
                console.print(lineage_tree)
                
                # Export if requested
                if output_file:
                    await cli.lineage_analyzer.export_lineage_graph(lineage_graph, output_file)
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_analyze_lineage())

@lineage.command()
@click.option('--entity-guid', required=True, help='Entity GUID for impact analysis')
@click.option('--output-file', help='Export impact report to file')
@click.pass_context
def impact(ctx, entity_guid, output_file):
    """Analyze impact of changes to an entity"""
    
    async def _analyze_impact():
        async with PurviewCLI(ctx.obj['config']) as cli:
            try:
                # Get lineage graph
                lineage_graph = await cli.lineage_analyzer.get_comprehensive_lineage(
                    entity_guid, LineageDirection.BOTH, LineageDepth.DEEP
                )
                
                # Analyze impact
                impact_analysis = cli.lineage_analyzer.analyze_lineage_impact(
                    lineage_graph, entity_guid
                )
                
                # Display results
                table = Table(title="Impact Analysis")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                impact_color = {
                    'critical': 'red',
                    'high': 'red',
                    'medium': 'yellow',
                    'low': 'green'
                }.get(impact_analysis.impact_level.value, 'white')
                
                table.add_row("Impact Level", f"[{impact_color}]{impact_analysis.impact_level.value.upper()}[/{impact_color}]")
                table.add_row("Impact Score", f"{impact_analysis.impact_score:.1f}/100")
                table.add_row("Downstream Entities", str(impact_analysis.downstream_count))
                table.add_row("Upstream Entities", str(impact_analysis.upstream_count))
                table.add_row("Critical Paths", str(len(impact_analysis.critical_paths)))
                
                console.print(table)
                
                # Display recommendations
                if impact_analysis.recommendations:
                    console.print("\n[bold yellow]Recommendations:[/bold yellow]")
                    for i, rec in enumerate(impact_analysis.recommendations, 1):
                        console.print(f"{i}. {rec}")
                
                # Export if requested
                if output_file:
                    from ..client.lineage_visualization import LineageReporting
                    reporting = LineageReporting(cli.lineage_analyzer)
                    await reporting.generate_impact_report(entity_guid, output_file)
                    
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)
    
    asyncio.run(_analyze_impact())

@cli.group()
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
    cli()
