"""
 Scanning Operations Module for Microsoft Purview
Provides comprehensive scanning automation and management capabilities
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID

# Optional pandas dependency for report generation
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Report generation features will be limited.")

from .api_client import PurviewClient

console = Console()

class ScanningManager:
    """Advanced scanning operations and automation"""
    
    def __init__(self, client: PurviewClient):
        self.client = client
        self.console = Console()
    
    async def create_data_source(self, data_source_config: Dict) -> Dict:
        """Create a new data source"""
        endpoint = "/scan/datasources"
        return await self.client._make_request('PUT', endpoint, json=data_source_config)
    
    async def get_data_sources(self) -> List[Dict]:
        """Get all data sources"""
        endpoint = "/scan/datasources"
        response = await self.client._make_request('GET', endpoint)
        return response.get('value', [])
    
    async def create_scan(self, data_source_name: str, scan_config: Dict) -> Dict:
        """Create a new scan for a data source"""
        endpoint = f"/scan/datasources/{data_source_name}/scans/{scan_config['name']}"
        return await self.client._make_request('PUT', endpoint, json=scan_config)
    
    async def run_scan(self, data_source_name: str, scan_name: str) -> Dict:
        """Start a scan"""
        endpoint = f"/scan/datasources/{data_source_name}/scans/{scan_name}/run"
        return await self.client._make_request('POST', endpoint)
    
    async def get_scan_status(self, data_source_name: str, scan_name: str, run_id: str) -> Dict:
        """Get scan status"""
        endpoint = f"/scan/datasources/{data_source_name}/scans/{scan_name}/runs/{run_id}"
        return await self.client._make_request('GET', endpoint)
    
    async def get_scan_history(self, data_source_name: str, scan_name: str) -> List[Dict]:
        """Get scan run history"""
        endpoint = f"/scan/datasources/{data_source_name}/scans/{scan_name}/runs"
        response = await self.client._make_request('GET', endpoint)
        return response.get('value', [])
    
    async def bulk_create_data_sources(self, sources_config: List[Dict], 
                                     progress_callback: Optional[Callable] = None) -> Dict:
        """Create multiple data sources from configuration"""
        results = {'created': [], 'failed': [], 'errors': []}
        
        with Progress() as progress:
            task = progress.add_task("Creating data sources...", total=len(sources_config))
            
            for i, source_config in enumerate(sources_config):
                try:
                    result = await self.create_data_source(source_config)
                    results['created'].append({
                        'name': source_config.get('name'),
                        'type': source_config.get('kind'),
                        'result': result
                    })
                    
                except Exception as e:
                    error_msg = f"Failed to create {source_config.get('name', 'unknown')}: {str(e)}"
                    results['failed'].append(source_config.get('name', 'unknown'))
                    results['errors'].append(error_msg)
                
                progress.update(task, advance=1)
                if progress_callback:
                    progress_callback(i + 1, len(sources_config))
        
        return results
    
    async def bulk_run_scans(self, scan_configs: List[Dict],
                           monitor_progress: bool = True) -> Dict:
        """Run multiple scans and optionally monitor their progress"""
        results = {'started': [], 'failed': [], 'completed': [], 'errors': []}
        
        # Start all scans
        scan_runs = []
        for scan_config in scan_configs:
            try:
                data_source = scan_config['data_source']
                scan_name = scan_config['scan_name']
                
                result = await self.run_scan(data_source, scan_name)
                run_id = result.get('runId')
                
                if run_id:
                    scan_runs.append({
                        'data_source': data_source,
                        'scan_name': scan_name,
                        'run_id': run_id,
                        'started_at': datetime.now()
                    })
                    results['started'].append(f"{data_source}/{scan_name}")
                
            except Exception as e:
                error_msg = f"Failed to start scan {scan_config}: {str(e)}"
                results['failed'].append(str(scan_config))
                results['errors'].append(error_msg)
        
        # Monitor progress if requested
        if monitor_progress and scan_runs:
            await self._monitor_scan_progress(scan_runs, results)
        
        return results
    
    async def _monitor_scan_progress(self, scan_runs: List[Dict], results: Dict):
        """Monitor the progress of running scans"""
        pending_scans = scan_runs.copy()
        
        with Progress() as progress:
            # Create progress bars for each scan
            scan_tasks = {}
            for scan in pending_scans:
                scan_id = f"{scan['data_source']}/{scan['scan_name']}"
                task_id = progress.add_task(f"Scanning {scan_id}", total=100)
                scan_tasks[scan_id] = task_id
            
            while pending_scans:
                completed_scans = []
                
                for scan in pending_scans:
                    try:
                        status = await self.get_scan_status(
                            scan['data_source'], 
                            scan['scan_name'], 
                            scan['run_id']
                        )
                        
                        scan_state = status.get('status', 'Unknown')
                        scan_id = f"{scan['data_source']}/{scan['scan_name']}"
                        
                        if scan_state in ['Succeeded', 'Failed', 'Canceled']:
                            completed_scans.append(scan)
                            progress.update(scan_tasks[scan_id], completed=100)
                            
                            if scan_state == 'Succeeded':
                                results['completed'].append(scan_id)
                            else:
                                results['failed'].append(scan_id)
                                results['errors'].append(f"Scan {scan_id} {scan_state}")
                        
                        elif scan_state == 'Running':
                            # Update progress based on scan metrics if available
                            scan_result = status.get('scanResultMetrics', {})
                            if scan_result:
                                processed = scan_result.get('processedCount', 0)
                                total = scan_result.get('totalCount', 1)
                                percentage = min((processed / total) * 100, 99) if total > 0 else 50
                                progress.update(scan_tasks[scan_id], completed=percentage)
                    
                    except Exception as e:
                        console.print(f"[red]Error monitoring scan {scan}: {str(e)}[/red]")
                
                # Remove completed scans
                for completed in completed_scans:
                    pending_scans.remove(completed)
                
                if pending_scans:
                    await asyncio.sleep(30)  # Check every 30 seconds
    
    async def generate_scan_report(self, output_file: str, days_back: int = 30) -> Dict:
        """Generate comprehensive scanning report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        console.print(f"[blue]Generating scan report for last {days_back} days...[/blue]")
        
        # Get all data sources
        data_sources = await self.get_data_sources()
        
        report_data = []
        summary_stats = {
            'total_sources': len(data_sources),
            'scanned_sources': 0,
            'successful_scans': 0,
            'failed_scans': 0,
            'total_assets_discovered': 0
        }
        
        for source in data_sources:
            source_name = source.get('name')
            source_type = source.get('kind')
            
            try:
                # Get scans for this data source
                scans_endpoint = f"/scan/datasources/{source_name}/scans"
                scans_response = await self.client._make_request('GET', scans_endpoint)
                scans = scans_response.get('value', [])
                
                for scan in scans:
                    scan_name = scan.get('name')
                    
                    # Get scan history
                    history = await self.get_scan_history(source_name, scan_name)
                    
                    for run in history:
                        run_date = datetime.fromisoformat(run.get('startTime', '').replace('Z', '+00:00'))
                        
                        if start_date <= run_date <= end_date:
                            summary_stats['scanned_sources'] += 1
                            
                            status = run.get('status', 'Unknown')
                            if status == 'Succeeded':
                                summary_stats['successful_scans'] += 1
                            elif status == 'Failed':
                                summary_stats['failed_scans'] += 1
                            
                            # Extract metrics
                            metrics = run.get('scanResultMetrics', {})
                            assets_discovered = metrics.get('processedCount', 0)
                            summary_stats['total_assets_discovered'] += assets_discovered
                            
                            report_data.append({
                                'data_source': source_name,
                                'source_type': source_type,
                                'scan_name': scan_name,
                                'run_id': run.get('runId'),
                                'status': status,
                                'start_time': run.get('startTime'),
                                'end_time': run.get('endTime'),
                                'duration_minutes': self._calculate_duration(
                                    run.get('startTime'), run.get('endTime')
                                ),
                                'assets_discovered': assets_discovered,
                                'assets_classified': metrics.get('classifiedCount', 0),
                                'error_message': run.get('error', {}).get('message', '')
                            })
            
            except Exception as e:
                console.print(f"[yellow]Warning: Could not get scan data for {source_name}: {e}[/yellow]")
        
        # Save report to CSV
        df = pd.DataFrame(report_data)
        df.to_csv(output_file, index=False)
        
        # Generate summary
        summary = {
            'report_file': output_file,
            'report_period': f"{start_date.date()} to {end_date.date()}",
            'statistics': summary_stats,
            'total_scan_runs': len(report_data)
        }
        
        console.print(f"[green]✓ Scan report saved to {output_file}[/green]")
        console.print(f"[green]✓ Found {len(report_data)} scan runs across {summary_stats['total_sources']} data sources[/green]")
        
        return summary
    
    def _calculate_duration(self, start_time: str, end_time: str) -> float:
        """Calculate scan duration in minutes"""
        try:
            if not start_time or not end_time:
                return 0.0
            
            start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            duration = end - start
            return duration.total_seconds() / 60
        
        except Exception:
            return 0.0
    
    async def optimize_scan_schedules(self) -> Dict:
        """Analyze scan patterns and suggest optimizations"""
        console.print("[blue]Analyzing scan patterns for optimization recommendations...[/blue]")
        
        # Get all data sources and their scan history
        data_sources = await self.get_data_sources()
        optimization_report = {
            'recommendations': [],
            'statistics': {},
            'potential_savings': {}
        }
        
        for source in data_sources:
            source_name = source.get('name')
            
            try:
                # Analyze scan frequency and success rates
                scans_endpoint = f"/scan/datasources/{source_name}/scans"
                scans_response = await self.client._make_request('GET', scans_endpoint)
                scans = scans_response.get('value', [])
                
                for scan in scans:
                    scan_name = scan.get('name')
                    history = await self.get_scan_history(source_name, scan_name)
                    
                    if len(history) >= 5:  # Need some history for analysis
                        analysis = self._analyze_scan_pattern(history)
                        
                        if analysis['recommendations']:
                            optimization_report['recommendations'].extend([
                                {
                                    'data_source': source_name,
                                    'scan_name': scan_name,
                                    'recommendation': rec
                                }
                                for rec in analysis['recommendations']
                            ])
            
            except Exception as e:
                console.print(f"[yellow]Warning: Could not analyze {source_name}: {e}[/yellow]")
        
        return optimization_report
    
    def _analyze_scan_pattern(self, scan_history: List[Dict]) -> Dict:
        """Analyze scan history to identify optimization opportunities"""
        recommendations = []
        
        # Calculate success rate
        total_scans = len(scan_history)
        successful_scans = sum(1 for run in scan_history if run.get('status') == 'Succeeded')
        success_rate = successful_scans / total_scans if total_scans > 0 else 0
        
        # Analyze scan frequency
        scan_times = [
            datetime.fromisoformat(run.get('startTime', '').replace('Z', '+00:00'))
            for run in scan_history
            if run.get('startTime')
        ]
        
        if len(scan_times) >= 2:
            scan_times.sort()
            intervals = [
                (scan_times[i] - scan_times[i-1]).total_seconds() / 3600  # Hours
                for i in range(1, len(scan_times))
            ]
            avg_interval = sum(intervals) / len(intervals) if intervals else 0
            
            # Generate recommendations
            if success_rate < 0.8:
                recommendations.append(f"Low success rate ({success_rate:.1%}). Review scan configuration and data source connectivity.")
            
            if avg_interval < 6:  # Less than 6 hours between scans
                recommendations.append(f"Very frequent scanning (avg {avg_interval:.1f}h intervals). Consider reducing frequency if data doesn't change often.")
            
            if avg_interval > 168:  # More than a week between scans
                recommendations.append(f"Infrequent scanning (avg {avg_interval:.1f}h intervals). Consider more frequent scans for better data freshness.")
        
        return {'recommendations': recommendations}

class ScanTemplateManager:
    """Manage scanning templates and configurations"""
    
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict:
        """Load default scanning templates"""
        return {
            'azure_storage': {
                'kind': 'AdlsGen2',
                'properties': {
                    'subscriptionId': '',
                    'resourceGroup': '',
                    'location': '',
                    'endpoint': '',
                    'collection': {
                        'referenceName': 'default'
                    }
                }
            },
            'sql_database': {
                'kind': 'AzureSqlDatabase',
                'properties': {
                    'serverEndpoint': '',
                    'databaseName': '',
                    'collection': {
                        'referenceName': 'default'
                    }
                }
            },
            'synapse_workspace': {
                'kind': 'AzureSynapseWorkspace',
                'properties': {
                    'dedicatedSqlEndpoint': '',
                    'serverlessSqlEndpoint': '',
                    'collection': {
                        'referenceName': 'default'
                    }
                }
            }
        }
    
    def create_data_source_config(self, template_name: str, **kwargs) -> Dict:
        """Create data source configuration from template"""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        config = self.templates[template_name].copy()
        
        # Update properties with provided values
        for key, value in kwargs.items():
            if '.' in key:
                # Handle nested properties like 'properties.endpoint'
                parts = key.split('.')
                current = config
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = value
            else:
                config[key] = value
        
        return config
    
    def create_scan_config(self, scan_name: str, scan_ruleset: str = None) -> Dict:
        """Create scan configuration"""
        config = {
            'name': scan_name,
            'kind': 'AzureSqlDatabaseCredential',
            'properties': {
                'scanRulesetName': scan_ruleset or 'AzureSqlDatabase',
                'scanRulesetType': 'System',
                'collection': {
                    'referenceName': 'default'
                }
            }
        }
        
        return config
    
    def save_template(self, name: str, template: Dict, file_path: str = None):
        """Save custom template"""
        self.templates[name] = template
        
        if file_path:
            with open(file_path, 'w') as f:
                json.dump({name: template}, f, indent=2)
    
    def load_template_from_file(self, file_path: str) -> Dict:
        """Load template from file"""
        with open(file_path, 'r') as f:
            return json.load(f)

# CLI Integration Functions
async def create_scanning_cli_commands():
    """Create CLI commands for scanning operations"""
    # This would integrate with the enhanced_cli.py
    # Example implementation for demonstration
    
    @click.group()
    def scanning():
        """Advanced scanning operations and automation"""
        pass
    
    @scanning.command()
    @click.option('--config-file', required=True, help='Data source configuration file')
    @click.option('--profile', default='default', help='Configuration profile')
    async def create_sources(config_file, profile):
        """Create multiple data sources from configuration file"""
        config = PurviewConfig.load_profile(profile)
        
        with open(config_file, 'r') as f:
            sources_config = json.load(f)
        
        async with PurviewClient(config) as client:
            manager = ScanningManager(client)
            results = await manager.bulk_create_data_sources(sources_config)
            
            console.print(f"[green]✓ Created {len(results['created'])} data sources[/green]")
            if results['failed']:
                console.print(f"[red]✗ Failed to create {len(results['failed'])} data sources[/red]")
    
    @scanning.command()
    @click.option('--output-file', required=True, help='Output file for scan report')
    @click.option('--days', default=30, help='Number of days to include in report')
    @click.option('--profile', default='default', help='Configuration profile')
    async def report(output_file, days, profile):
        """Generate comprehensive scanning report"""
        config = PurviewConfig.load_profile(profile)
        
        async with PurviewClient(config) as client:
            manager = ScanningManager(client)
            report = await manager.generate_scan_report(output_file, days)
            
            # Display summary
            stats = report['statistics']
            table = Table(title="Scan Report Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Data Sources", str(stats['total_sources']))
            table.add_row("Successful Scans", str(stats['successful_scans']))
            table.add_row("Failed Scans", str(stats['failed_scans']))
            table.add_row("Assets Discovered", str(stats['total_assets_discovered']))
            
            console.print(table)
    
    return scanning

# Export the main classes and functions
__all__ = [
    'ScanningManager',
    'ScanTemplateManager',
    'create_scanning_cli_commands'
]
