"""
Real-time Monitoring Dashboard for Azure Purview
Provides live monitoring, metrics collection, and alerting capabilities
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from rich.console import Console
from rich.table import Table

# Optional pandas dependency for report generation
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    pd = None
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available. Metrics export features will be limited.")
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.align import Align
import threading

from .api_client import EnhancedPurviewClient
from .config import PurviewConfig

console = Console()

class MetricType(Enum):
    """Types of metrics to monitor"""
    SCAN_STATUS = "scan_status"
    ENTITY_COUNT = "entity_count"
    API_PERFORMANCE = "api_performance"
    DATA_QUALITY = "data_quality"
    CLASSIFICATION_COVERAGE = "classification_coverage"
    LINEAGE_COMPLETENESS = "lineage_completeness"
    GLOSSARY_USAGE = "glossary_usage"
    USER_ACTIVITY = "user_activity"

class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Monitoring metric"""
    name: str
    value: Any
    timestamp: datetime
    metric_type: MetricType
    tags: Dict[str, str] = field(default_factory=dict)
    
@dataclass
class Alert:
    """Monitoring alert"""
    id: str
    title: str
    description: str
    severity: AlertSeverity
    timestamp: datetime
    metric_name: str
    threshold_value: Any
    actual_value: Any
    is_resolved: bool = False
    
@dataclass
class Threshold:
    """Monitoring threshold"""
    metric_name: str
    operator: str  # >, <, >=, <=, ==, !=
    value: Any
    severity: AlertSeverity
    description: str

class MonitoringDashboard:
    """Real-time monitoring dashboard for Purview"""
    
    def __init__(self, client: EnhancedPurviewClient):
        self.client = client
        self.console = Console()
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.thresholds: List[Threshold] = []
        self.is_monitoring = False
        self.monitoring_thread = None
        self.refresh_interval = 30  # seconds
        
        # Default thresholds
        self._setup_default_thresholds()
    
    def _setup_default_thresholds(self):
        """Setup default monitoring thresholds"""
        self.thresholds = [
            Threshold("failed_scans", ">=", 5, AlertSeverity.WARNING, "Multiple scan failures detected"),
            Threshold("api_response_time", ">=", 5000, AlertSeverity.WARNING, "API response time high"),
            Threshold("entity_count_change", "<=", -100, AlertSeverity.ERROR, "Significant entity count decrease"),
            Threshold("classification_coverage", "<=", 50, AlertSeverity.WARNING, "Low classification coverage"),
            Threshold("data_quality_score", "<=", 70, AlertSeverity.ERROR, "Data quality score below threshold"),
        ]
    
    async def collect_metrics(self) -> List[Metric]:
        """Collect current metrics from Purview"""
        metrics = []
        current_time = datetime.now()
        
        try:
            # Scan status metrics
            scan_metrics = await self._collect_scan_metrics()
            metrics.extend(scan_metrics)
            
            # Entity count metrics
            entity_metrics = await self._collect_entity_metrics()
            metrics.extend(entity_metrics)
            
            # API performance metrics
            api_metrics = await self._collect_api_metrics()
            metrics.extend(api_metrics)
            
            # Classification coverage metrics
            classification_metrics = await self._collect_classification_metrics()
            metrics.extend(classification_metrics)
            
            # Lineage completeness metrics
            lineage_metrics = await self._collect_lineage_metrics()
            metrics.extend(lineage_metrics)
            
        except Exception as e:
            self.console.print(f"[red]Error collecting metrics: {e}[/red]")
        
        # Store metrics
        self.metrics.extend(metrics)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
        
        return metrics
    
    async def _collect_scan_metrics(self) -> List[Metric]:
        """Collect scan-related metrics"""
        metrics = []
        current_time = datetime.now()
        
        try:
            # Get data sources
            data_sources = await self.client._make_request('GET', '/scan/datasources')
            
            running_scans = 0
            failed_scans = 0
            completed_scans = 0
            
            for ds in data_sources.get('value', []):
                ds_name = ds.get('name', '')
                
                # Get scans for this data source
                try:
                    scans_response = await self.client._make_request('GET', f'/scan/datasources/{ds_name}/scans')
                    scans = scans_response.get('value', [])
                    
                    for scan in scans:
                        scan_name = scan.get('name', '')
                        
                        # Get recent runs
                        try:
                            runs_response = await self.client._make_request('GET', f'/scan/datasources/{ds_name}/scans/{scan_name}/runs')
                            runs = runs_response.get('value', [])
                            
                            for run in runs[-5:]:  # Check last 5 runs
                                status = run.get('status', '').lower()
                                if status == 'running':
                                    running_scans += 1
                                elif status == 'failed':
                                    failed_scans += 1
                                elif status == 'succeeded':
                                    completed_scans += 1
                        except:
                            continue
                except:
                    continue
            
            metrics.extend([
                Metric("running_scans", running_scans, current_time, MetricType.SCAN_STATUS),
                Metric("failed_scans", failed_scans, current_time, MetricType.SCAN_STATUS),
                Metric("completed_scans", completed_scans, current_time, MetricType.SCAN_STATUS),
            ])
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not collect scan metrics: {e}[/yellow]")
        
        return metrics
    
    async def _collect_entity_metrics(self) -> List[Metric]:
        """Collect entity-related metrics"""
        metrics = []
        current_time = datetime.now()
        
        try:
            # Get entity counts by type
            search_payload = {
                "keywords": "*",
                "limit": 0,  # We only want the count
                "facets": [
                    {"facet": "entityType", "sort": {"count": "desc"}}
                ]
            }
            
            search_response = await self.client._make_request('POST', '/search/query', json=search_payload)
            
            total_entities = search_response.get('@search.count', 0)
            metrics.append(Metric("total_entities", total_entities, current_time, MetricType.ENTITY_COUNT))
            
            # Entity counts by type
            facets = search_response.get('@search.facets', {})
            entity_type_facet = facets.get('entityType', [])
            
            for facet in entity_type_facet:
                entity_type = facet.get('value', 'unknown')
                count = facet.get('count', 0)
                metrics.append(
                    Metric(f"entities_{entity_type}", count, current_time, MetricType.ENTITY_COUNT, {"type": entity_type})
                )
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not collect entity metrics: {e}[/yellow]")
        
        return metrics
    
    async def _collect_api_metrics(self) -> List[Metric]:
        """Collect API performance metrics"""
        metrics = []
        current_time = datetime.now()
        
        # Measure API response time with a simple request
        start_time = time.time()
        try:
            await self.client._make_request('GET', '/types/typedefs')
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            metrics.append(Metric("api_response_time", response_time, current_time, MetricType.API_PERFORMANCE))
        except Exception as e:
            response_time = -1  # Indicate failure
            metrics.append(Metric("api_response_time", response_time, current_time, MetricType.API_PERFORMANCE))
        
        return metrics
    
    async def _collect_classification_metrics(self) -> List[Metric]:
        """Collect classification coverage metrics"""
        metrics = []
        current_time = datetime.now()
        
        try:
            # Search for classified entities
            classified_search = {
                "keywords": "*",
                "limit": 0,
                "filter": {
                    "and": [
                        {"not": {"attributeName": "classifications", "operator": "eq", "attributeValue": None}}
                    ]
                }
            }
            
            classified_response = await self.client._make_request('POST', '/search/query', json=classified_search)
            classified_count = classified_response.get('@search.count', 0)
            
            # Get total entity count
            total_search = {"keywords": "*", "limit": 0}
            total_response = await self.client._make_request('POST', '/search/query', json=total_search)
            total_count = total_response.get('@search.count', 0)
            
            if total_count > 0:
                coverage_percentage = (classified_count / total_count) * 100
            else:
                coverage_percentage = 0
            
            metrics.extend([
                Metric("classified_entities", classified_count, current_time, MetricType.CLASSIFICATION_COVERAGE),
                Metric("classification_coverage", coverage_percentage, current_time, MetricType.CLASSIFICATION_COVERAGE),
            ])
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not collect classification metrics: {e}[/yellow]")
        
        return metrics
    
    async def _collect_lineage_metrics(self) -> List[Metric]:
        """Collect lineage completeness metrics"""
        metrics = []
        current_time = datetime.now()
        
        try:
            # This is a simplified approach - in practice, you'd want more sophisticated lineage analysis
            search_payload = {
                "keywords": "*",
                "limit": 100,
                "filter": {
                    "entityType": "DataSet"
                }
            }
            
            search_response = await self.client._make_request('POST', '/search/query', json=search_payload)
            entities = search_response.get('value', [])
            
            entities_with_lineage = 0
            for entity in entities:
                guid = entity.get('id', '')
                if guid:
                    try:
                        lineage = await self.client._make_request('GET', f'/lineage/{guid}')
                        if lineage.get('relations'):
                            entities_with_lineage += 1
                    except:
                        continue
            
            total_datasets = len(entities)
            if total_datasets > 0:
                lineage_percentage = (entities_with_lineage / total_datasets) * 100
            else:
                lineage_percentage = 0
            
            metrics.extend([
                Metric("entities_with_lineage", entities_with_lineage, current_time, MetricType.LINEAGE_COMPLETENESS),
                Metric("lineage_completeness", lineage_percentage, current_time, MetricType.LINEAGE_COMPLETENESS),
            ])
            
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not collect lineage metrics: {e}[/yellow]")
        
        return metrics
    
    def check_thresholds(self, metrics: List[Metric]) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        new_alerts = []
        
        for metric in metrics:
            for threshold in self.thresholds:
                if metric.name == threshold.metric_name:
                    violation = self._check_threshold_violation(metric.value, threshold)
                    
                    if violation:
                        alert = Alert(
                            id=f"{metric.name}_{int(metric.timestamp.timestamp())}",
                            title=f"Threshold Violation: {metric.name}",
                            description=threshold.description,
                            severity=threshold.severity,
                            timestamp=metric.timestamp,
                            metric_name=metric.name,
                            threshold_value=threshold.value,
                            actual_value=metric.value
                        )
                        new_alerts.append(alert)
        
        self.alerts.extend(new_alerts)
        return new_alerts
    
    def _check_threshold_violation(self, value: Any, threshold: Threshold) -> bool:
        """Check if a value violates a threshold"""
        try:
            if threshold.operator == ">":
                return value > threshold.value
            elif threshold.operator == ">=":
                return value >= threshold.value
            elif threshold.operator == "<":
                return value < threshold.value
            elif threshold.operator == "<=":
                return value <= threshold.value
            elif threshold.operator == "==":
                return value == threshold.value
            elif threshold.operator == "!=":
                return value != threshold.value
        except:
            return False
        
        return False
    
    def create_dashboard_layout(self) -> Layout:
        """Create the dashboard layout"""
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=5)
        )
        
        layout["body"].split_row(
            Layout(name="metrics", ratio=2),
            Layout(name="alerts", ratio=1)
        )
        
        return layout
    
    def update_dashboard_content(self, layout: Layout):
        """Update dashboard content with current data"""
        # Header
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_text = Text(f"Purview Monitoring Dashboard - {current_time}", style="bold blue")
        layout["header"].update(Panel(Align.center(header_text), border_style="blue"))
        
        # Metrics
        metrics_table = self._create_metrics_table()
        layout["metrics"].update(Panel(metrics_table, title="Current Metrics", border_style="green"))
        
        # Alerts
        alerts_table = self._create_alerts_table()
        layout["alerts"].update(Panel(alerts_table, title="Active Alerts", border_style="red"))
        
        # Footer with summary
        summary_text = self._create_summary_text()
        layout["footer"].update(Panel(summary_text, title="Summary", border_style="yellow"))
    
    def _create_metrics_table(self) -> Table:
        """Create metrics display table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")
        table.add_column("Timestamp", style="yellow")
        
        # Get latest metrics by name
        latest_metrics = {}
        for metric in self.metrics:
            if metric.name not in latest_metrics or metric.timestamp > latest_metrics[metric.name].timestamp:
                latest_metrics[metric.name] = metric
        
        for metric in sorted(latest_metrics.values(), key=lambda m: m.name):
            value_str = str(metric.value)
            if isinstance(metric.value, float):
                value_str = f"{metric.value:.2f}"
            
            timestamp_str = metric.timestamp.strftime("%H:%M:%S")
            table.add_row(metric.name, value_str, timestamp_str)
        
        return table
    
    def _create_alerts_table(self) -> Table:
        """Create alerts display table"""
        table = Table(show_header=True, header_style="bold red")
        table.add_column("Severity", style="red", no_wrap=True)
        table.add_column("Title", style="yellow")
        table.add_column("Time", style="cyan")
        
        # Show only unresolved alerts from last hour
        recent_alerts = [
            alert for alert in self.alerts 
            if not alert.is_resolved and alert.timestamp > datetime.now() - timedelta(hours=1)
        ]
        
        for alert in sorted(recent_alerts, key=lambda a: a.timestamp, reverse=True)[:10]:
            severity_style = {
                AlertSeverity.CRITICAL: "bold red",
                AlertSeverity.ERROR: "red",
                AlertSeverity.WARNING: "yellow",
                AlertSeverity.INFO: "blue"
            }.get(alert.severity, "white")
            
            table.add_row(
                Text(alert.severity.value.upper(), style=severity_style),
                alert.title,
                alert.timestamp.strftime("%H:%M:%S")
            )
        
        return table
    
    def _create_summary_text(self) -> Text:
        """Create summary text"""
        total_alerts = len([a for a in self.alerts if not a.is_resolved])
        critical_alerts = len([a for a in self.alerts if not a.is_resolved and a.severity == AlertSeverity.CRITICAL])
        
        # Get key metrics
        latest_metrics = {}
        for metric in self.metrics:
            if metric.name not in latest_metrics or metric.timestamp > latest_metrics[metric.name].timestamp:
                latest_metrics[metric.name] = metric
        
        total_entities = latest_metrics.get('total_entities', Metric('total_entities', 0, datetime.now(), MetricType.ENTITY_COUNT)).value
        running_scans = latest_metrics.get('running_scans', Metric('running_scans', 0, datetime.now(), MetricType.SCAN_STATUS)).value
        
        summary = Text()
        summary.append(f"Active Alerts: {total_alerts} ({critical_alerts} critical) | ", style="bold")
        summary.append(f"Total Entities: {total_entities} | ", style="cyan")
        summary.append(f"Running Scans: {running_scans} | ", style="green")
        summary.append(f"Refresh: {self.refresh_interval}s", style="yellow")
        
        return summary
    
    async def start_monitoring(self, refresh_interval: int = 30):
        """Start real-time monitoring"""
        self.refresh_interval = refresh_interval
        self.is_monitoring = True
        
        layout = self.create_dashboard_layout()
        
        with Live(layout, refresh_per_second=1, screen=True):
            while self.is_monitoring:
                try:
                    # Collect metrics
                    metrics = await self.collect_metrics()
                    
                    # Check thresholds
                    new_alerts = self.check_thresholds(metrics)
                    
                    # Update dashboard
                    self.update_dashboard_content(layout)
                    
                    # Wait for next refresh
                    await asyncio.sleep(refresh_interval)
                    
                except KeyboardInterrupt:
                    self.stop_monitoring()
                    break
                except Exception as e:
                    console.print(f"[red]Monitoring error: {e}[/red]")
                    await asyncio.sleep(5)  # Wait before retrying
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        console.print("[green]Monitoring stopped[/green]")
    
    def export_metrics(self, output_path: str, format: str = 'json'):
        """Export collected metrics"""
        if format.lower() == 'json':
            metrics_data = [
                {
                    'name': m.name,
                    'value': m.value,
                    'timestamp': m.timestamp.isoformat(),
                    'metric_type': m.metric_type.value,
                    'tags': m.tags
                }
                for m in self.metrics
            ]
            
            with open(output_path, 'w') as f:
                json.dump(metrics_data, f, indent=2)
        
        elif format.lower() == 'csv':
            df = pd.DataFrame([
                {
                    'name': m.name,
                    'value': m.value,
                    'timestamp': m.timestamp,
                    'metric_type': m.metric_type.value,
                }
                for m in self.metrics
            ])
            df.to_csv(output_path, index=False)
        
        console.print(f"[green]Metrics exported to {output_path}[/green]")
    
    def export_alerts(self, output_path: str, format: str = 'json'):
        """Export alerts"""
        if format.lower() == 'json':
            alerts_data = [
                {
                    'id': a.id,
                    'title': a.title,
                    'description': a.description,
                    'severity': a.severity.value,
                    'timestamp': a.timestamp.isoformat(),
                    'metric_name': a.metric_name,
                    'threshold_value': a.threshold_value,
                    'actual_value': a.actual_value,
                    'is_resolved': a.is_resolved
                }
                for a in self.alerts
            ]
            
            with open(output_path, 'w') as f:
                json.dump(alerts_data, f, indent=2)
        
        console.print(f"[green]Alerts exported to {output_path}[/green]")

class MonitoringReports:
    """Generate monitoring reports and analytics"""
    
    def __init__(self, dashboard: MonitoringDashboard):
        self.dashboard = dashboard
        self.console = Console()
    
    def generate_daily_report(self, output_path: str):
        """Generate daily monitoring report"""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        # Filter metrics from last 24 hours
        daily_metrics = [
            m for m in self.dashboard.metrics 
            if m.timestamp >= yesterday
        ]
        
        # Filter alerts from last 24 hours
        daily_alerts = [
            a for a in self.dashboard.alerts 
            if a.timestamp >= yesterday
        ]
        
        report = {
            'report_date': now.isoformat(),
            'period': '24 hours',
            'summary': {
                'total_metrics_collected': len(daily_metrics),
                'total_alerts_generated': len(daily_alerts),
                'critical_alerts': len([a for a in daily_alerts if a.severity == AlertSeverity.CRITICAL]),
                'error_alerts': len([a for a in daily_alerts if a.severity == AlertSeverity.ERROR]),
                'warning_alerts': len([a for a in daily_alerts if a.severity == AlertSeverity.WARNING])
            },
            'metrics_analysis': self._analyze_metrics(daily_metrics),
            'alerts_analysis': self._analyze_alerts(daily_alerts),
            'recommendations': self._generate_recommendations(daily_metrics, daily_alerts)
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.console.print(f"[green]Daily report generated: {output_path}[/green]")
        return report
    
    def _analyze_metrics(self, metrics: List[Metric]) -> Dict:
        """Analyze metrics for patterns and trends"""
        analysis = {}
        
        # Group metrics by name
        metrics_by_name = {}
        for metric in metrics:
            if metric.name not in metrics_by_name:
                metrics_by_name[metric.name] = []
            metrics_by_name[metric.name].append(metric)
        
        for name, metric_list in metrics_by_name.items():
            values = [m.value for m in metric_list if isinstance(m.value, (int, float))]
            if values:
                analysis[name] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'trend': 'stable'  # Simplified trend analysis
                }
        
        return analysis
    
    def _analyze_alerts(self, alerts: List[Alert]) -> Dict:
        """Analyze alerts for patterns"""
        if not alerts:
            return {'total': 0}
        
        analysis = {
            'total': len(alerts),
            'by_severity': {},
            'by_metric': {},
            'most_common_issues': []
        }
        
        # Group by severity
        for alert in alerts:
            severity = alert.severity.value
            if severity not in analysis['by_severity']:
                analysis['by_severity'][severity] = 0
            analysis['by_severity'][severity] += 1
        
        # Group by metric
        for alert in alerts:
            metric = alert.metric_name
            if metric not in analysis['by_metric']:
                analysis['by_metric'][metric] = 0
            analysis['by_metric'][metric] += 1
        
        # Find most common issues
        metric_counts = sorted(analysis['by_metric'].items(), key=lambda x: x[1], reverse=True)
        analysis['most_common_issues'] = metric_counts[:5]
        
        return analysis
    
    def _generate_recommendations(self, metrics: List[Metric], alerts: List[Alert]) -> List[str]:
        """Generate recommendations based on metrics and alerts"""
        recommendations = []
        
        # Analyze alert patterns
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        if critical_alerts:
            recommendations.append("Address critical alerts immediately to prevent system issues")
        
        # Check scan failure patterns
        failed_scan_alerts = [a for a in alerts if 'failed_scans' in a.metric_name]
        if failed_scan_alerts:
            recommendations.append("Review scan configurations and data source connectivity")
        
        # Check API performance
        api_alerts = [a for a in alerts if 'api_response_time' in a.metric_name]
        if api_alerts:
            recommendations.append("Monitor API performance and consider scaling if needed")
        
        # Check classification coverage
        classification_alerts = [a for a in alerts if 'classification_coverage' in a.metric_name]
        if classification_alerts:
            recommendations.append("Improve data classification coverage through automated scanning")
        
        if not recommendations:
            recommendations.append("System is performing well - continue monitoring")
        
        return recommendations
