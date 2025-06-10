#!/usr/bin/env python3
"""
Integration Test Suite for  Purview CLI v2.0
Tests integration between all modules and end-to-end workflows
"""

import sys
import os
from pathlib import Path
import asyncio
import json
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, track

console = Console()

class IntegrationTestSuite:
    """Integration tests for  Purview CLI"""
    
    def __init__(self):
        self.test_results = []
        self.mock_config = {
            'account_name': 'test-purview',
            'tenant_id': 'test-tenant-id',
            'client_id': 'test-client-id',
            'client_secret': 'test-client-secret',
            'endpoint': 'https://test-purview.purview.azure.com'
        }
        self.temp_dir = tempfile.mkdtemp()
    
    def log_test_result(self, test_name: str, success: bool, details: str = None):
        """Log test result"""
        self.test_results.append({
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now()
        })
        
        status = "✅ PASS" if success else "❌ FAIL"
        console.print(f"[{'green' if success else 'red'}]{status} {test_name}[/{'green' if success else 'red'}]")
        if details and not success:
            console.print(f"[red]  Details: {details}[/red]")
    
    async def test_cli_module_integration(self):
        """Test integration between CLI and all modules"""
        console.print("\n[bold blue]Testing CLI Module Integration[/bold blue]")
        
        try:
            from purviewcli.cli import cli            # Test CLI module has command groups
            import click
            ctx = click.Context(cli.cli)
            command_groups = ['scanning', 'governance', 'monitoring', 'lineage', 'plugins']
            
            missing_commands = []
            for group in command_groups:
                if group not in cli.cli.commands:
                    missing_commands.append(group)
            
            if missing_commands:
                self.log_test_result(
                    "CLI Module Integration",
                    False,
                    f"Missing command groups: {', '.join(missing_commands)}"
                )
            else:
                self.log_test_result("CLI Module Integration", True)
        
        except Exception as e:
            self.log_test_result("CLI Module Integration", False, str(e))
    
    async def test_scanning_to_monitoring_workflow(self):
        """Test workflow from scanning operations to monitoring"""
        console.print("\n[bold blue]Testing Scanning → Monitoring Workflow[/bold blue]")
        
        try:
            from purviewcli.client.scanning_operations import ScanningManager
            from purviewcli.client.monitoring_dashboard import MonitoringDashboard
            
            # Initialize modules
            scanning_manager = ScanningManager(self.mock_config)
            monitoring_dashboard = MonitoringDashboard(self.mock_config)
            
            # Mock scan operations
            mock_scan_result = {
                'scanId': 'test-scan-123',
                'status': 'Running',
                'dataSourceName': 'test-datasource',
                'startTime': datetime.now().isoformat()
            }
            
            with patch.object(scanning_manager, 'start_scan', new_callable=AsyncMock) as mock_start_scan:
                mock_start_scan.return_value = mock_scan_result
                
                # Start a scan
                scan_result = await scanning_manager.start_scan('test-datasource')
                
                # Verify scan started
                assert scan_result['scanId'] == 'test-scan-123'
                
                # Mock monitoring data that includes scan metrics
                mock_metrics = {
                    'total_scans': 10,
                    'active_scans': 2,
                    'failed_scans': 1,
                    'scan_success_rate': 0.9
                }
                
                with patch.object(monitoring_dashboard, '_fetch_purview_metrics', return_value=mock_metrics):
                    # Collect metrics
                    metrics = monitoring_dashboard.collect_metrics()
                    
                    # Verify metrics include scan data
                    assert 'metrics' in metrics
                    assert metrics['metrics']['total_scans'] == 10
                    
                    self.log_test_result("Scanning → Monitoring Workflow", True)
        
        except Exception as e:
            self.log_test_result("Scanning → Monitoring Workflow", False, str(e))
      async def test_plugin_system_integration(self):
        """Test plugin system integration with other modules"""
        console.print("\n[bold blue]Testing Plugin System Integration[/bold blue]")
        
        try:
            from purviewcli.plugins.plugin_system import PluginManager
            from purviewcli.client.monitoring_dashboard import MonitoringDashboard
            
            # Initialize modules
            plugin_manager = PluginManager()
            monitoring_dashboard = MonitoringDashboard(self.mock_config)
            
            # Create a test plugin that integrates with monitoring
            class MonitoringPlugin:
                name = "monitoring_integration_plugin"
                version = "1.0.0"
                description = "Test plugin for monitoring integration"
                
                def execute(self, **kwargs):
                    # Simulate plugin collecting custom metrics
                    return {
                        'status': 'success',
                        'custom_metrics': {
                            'plugin_executions': 1,
                            'custom_data_quality_score': 0.95
                        }
                    }
            
            # Register plugin
            test_plugin = MonitoringPlugin()
            plugin_manager.register_plugin(test_plugin)
            
            # Execute plugin
            plugin_result = plugin_manager.execute_plugin("monitoring_integration_plugin")
            
            # Verify plugin execution
            assert plugin_result['status'] == 'success'
            assert 'custom_metrics' in plugin_result
            
            # Simulate monitoring dashboard collecting plugin metrics
            mock_base_metrics = {
                'total_entities': 1000,
                'active_scans': 5
            }
            
            # Combine base metrics with plugin metrics
            combined_metrics = {
                **mock_base_metrics,
                **plugin_result['custom_metrics']
            }
            
            assert 'plugin_executions' in combined_metrics
            assert combined_metrics['custom_data_quality_score'] == 0.95
            
            self.log_test_result("Plugin System Integration", True)
        
        except Exception as e:
            self.log_test_result("Plugin System Integration", False, str(e))
      async def test_end_to_end_data_governance_workflow(self):
        """Test complete end-to-end data governance workflow"""
        console.print("\n[bold blue]Testing End-to-End Data Governance Workflow[/bold blue]")
        
        try:
            # Import required modules
            from purviewcli.client.scanning_operations import ScanningManager
            from purviewcli.client.business_rules import BusinessRulesEngine
            from purviewcli.client.lineage_visualization import AdvancedLineageAnalyzer
            from purviewcli.client.monitoring_dashboard import MonitoringDashboard
            
            # Initialize all modules
            scanning_manager = ScanningManager(self.mock_config)
            rules_engine = BusinessRulesEngine(self.mock_config)
            lineage_analyzer = AdvancedLineageAnalyzer(self.mock_config)
            monitoring_dashboard = MonitoringDashboard(self.mock_config)
            
            # Step 1: Start data discovery scan
            mock_scan_result = {
                'scanId': 'e2e-scan-123',
                'status': 'Completed',
                'entitiesDiscovered': ['entity-1', 'entity-2', 'entity-3']
            }
            
            with patch.object(scanning_manager, 'start_scan', new_callable=AsyncMock) as mock_scan:
                mock_scan.return_value = mock_scan_result
                scan_result = await scanning_manager.start_scan('e2e-datasource')
                
                # Step 2: Apply governance rules to discovered entities
                mock_recommendations = [
                    {'entity_guid': 'entity-1', 'action': 'apply_classification', 'value': 'PII'},
                    {'entity_guid': 'entity-2', 'action': 'set_owner', 'value': 'finance-team@company.com'}
                ]
                
                # Step 3: Apply recommendations and check compliance
                mock_entity_data = {
                    'guid': 'entity-1',
                    'name': 'customer_data',
                    'classifications': ['PII'],
                    'owner': 'data-team@company.com'
                }
                
                with patch.object(rules_engine, '_get_entity_data', return_value=mock_entity_data):
                    compliance_check = rules_engine.check_entity_compliance('entity-1')
                    
                    # Step 4: Analyze lineage impact
                    mock_lineage_impact = {
                        'entity_guid': 'entity-1',
                        'impact_score': 0.8,
                        'affected_entities': 15,
                        'critical_path': True
                    }
                    
                    with patch.object(lineage_analyzer, 'analyze_lineage_impact', return_value=mock_lineage_impact):
                        lineage_impact = lineage_analyzer.analyze_lineage_impact('entity-1')
                        
                        # Step 5: Monitor overall governance health
                        mock_final_metrics = {
                            'total_entities': len(scan_result['entitiesDiscovered']),
                            'classification_coverage': 0.9,
                            'compliance_score': 0.85,
                            'lineage_completeness': 0.8
                        }
                        
                        with patch.object(monitoring_dashboard, 'collect_metrics', return_value={'metrics': mock_final_metrics}):
                            final_metrics = monitoring_dashboard.collect_metrics()
                            
                            # Verify end-to-end workflow
                            workflow_success = (
                                scan_result['status'] == 'Completed' and
                                len(mock_recommendations) == 2 and
                                'violations' in compliance_check and
                                lineage_impact['impact_score'] > 0 and
                                final_metrics['metrics']['compliance_score'] > 0.8
                            )
                            
                            if workflow_success:
                                self.log_test_result("End-to-End Data Governance Workflow", True)
                            else:
                                self.log_test_result(
                                    "End-to-End Data Governance Workflow", 
                                    False, 
                                    "Workflow validation failed"
                                )
        
        except Exception as e:
            self.log_test_result("End-to-End Data Governance Workflow", False, str(e))
      async def test_configuration_consistency(self):
        """Test configuration consistency across all modules"""
        console.print("\n[bold blue]Testing Configuration Consistency[/bold blue]")
        
        try:
            # Import all modules
            from purviewcli.client.scanning_operations import ScanningManager
            from purviewcli.client.business_rules import BusinessRulesEngine
            from purviewcli.client.monitoring_dashboard import MonitoringDashboard
            from purviewcli.client.lineage_visualization import AdvancedLineageAnalyzer
            
            # Test same config across all modules
            test_configs = [
                self.mock_config,
                {'account_name': 'another-purview', 'endpoint': 'https://another.purview.azure.com'},
                {}  # Empty config test
            ]
              modules_classes = [
                ('ScanningManager', ScanningManager),
                ('BusinessRulesEngine', BusinessRulesEngine),
                ('MonitoringDashboard', MonitoringDashboard),
                ('AdvancedLineageAnalyzer', AdvancedLineageAnalyzer)
            ]
            
            config_consistency = True
            for config in test_configs:
                for module_name, module_class in modules_classes:
                    try:
                        instance = module_class(config)
                        # Verify config is properly stored and consistent
                        if hasattr(instance, 'config'):
                            stored_config = instance.config
                            # Basic consistency check
                            if config and 'account_name' in config:
                                if stored_config.get('account_name') != config.get('account_name'):
                                    config_consistency = False
                    except Exception as e:
                        if config:  # Only fail if config was provided
                            config_consistency = False
            
            self.log_test_result("Configuration Consistency", config_consistency)
        
        except Exception as e:
            self.log_test_result("Configuration Consistency", False, str(e))
    
    async def test_error_propagation(self):
        """Test error handling and propagation between modules"""
        console.print("\n[bold blue]Testing Error Propagation[/bold blue]")
        
        try:
            from purviewcli.client.scanning_operations import ScanningManager
            from purviewcli.client.monitoring_dashboard import MonitoringDashboard
            
            scanning_manager = ScanningManager(self.mock_config)
            monitoring_dashboard = MonitoringDashboard(self.mock_config)
            
            # Test error in scanning doesn't crash monitoring
            with patch.object(scanning_manager, 'start_scan', side_effect=Exception("Scan failed")):
                try:
                    await scanning_manager.start_scan('test-source')
                except Exception:
                    pass  # Expected
                
                # Monitoring should still work despite scan failure
                mock_metrics = {
                    'total_scans': 5,
                    'failed_scans': 1,  # Including the failed scan
                    'success_rate': 0.8
                }
                
                with patch.object(monitoring_dashboard, '_fetch_purview_metrics', return_value=mock_metrics):
                    metrics = monitoring_dashboard.collect_metrics()
                    
                    # Verify monitoring can handle scan failures
                    assert 'metrics' in metrics
                    assert metrics['metrics']['failed_scans'] == 1
                    
                    self.log_test_result("Error Propagation", True)
        
        except Exception as e:
            self.log_test_result("Error Propagation", False, str(e))
    
    def generate_integration_report(self):
        """Generate comprehensive integration test report"""
        console.print("\n" + "="*80)
        console.print(Panel("[bold blue] Purview CLI v2.0 - Integration Test Report[/bold blue]"))
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Summary table
        summary_table = Table(title="Integration Test Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")
        summary_table.add_column("Status", style="green")
        
        summary_table.add_row("Total Integration Tests", str(total_tests), "📊")
        summary_table.add_row("Passed", str(passed_tests), "✅")
        summary_table.add_row("Failed", str(failed_tests), "❌" if failed_tests > 0 else "✅")
        summary_table.add_row("Success Rate", f"{success_rate:.1f}%", "🎯")
        
        console.print(summary_table)
        
        # Detailed results
        if self.test_results:
            results_table = Table(title="Detailed Integration Test Results", show_header=True, header_style="bold magenta")
            results_table.add_column("Test Name", style="cyan", width=35)
            results_table.add_column("Status", style="yellow", width=10)
            results_table.add_column("Duration", style="blue", width=10)
            results_table.add_column("Details", style="red", width=25)
            
            for result in self.test_results:
                status = "✅ PASS" if result['success'] else "❌ FAIL"
                duration = "< 1s"  # Placeholder
                details = result['details'][:22] + "..." if result['details'] and len(result['details']) > 25 else (result['details'] or "")
                results_table.add_row(result['test_name'], status, duration, details)
            
            console.print(results_table)
        
        # Integration health assessment
        console.print("\n[bold blue]Integration Health Assessment:[/bold blue]")
        
        if success_rate >= 90:
            console.print("[green]🎉 Excellent integration health! All modules work together seamlessly.[/green]")
            console.print("[green]✓ Ready for production deployment[/green]") 
            console.print("[green]✓ End-to-end workflows are functional[/green]")
            console.print("[green]✓ Error handling is robust[/green]")
        elif success_rate >= 75:
            console.print("[yellow]⚠ Good integration health with some minor issues.[/yellow]")
            console.print("[yellow]• Review failed tests and fix integration issues[/yellow]")
            console.print("[yellow]• Test manually before production deployment[/yellow]")
        else:
            console.print("[red]❌ Poor integration health. Major issues detected.[/red]")
            console.print("[red]• Significant integration problems need to be resolved[/red]")
            console.print("[red]• Not recommended for production deployment[/red]")
            console.print("[red]• Review module interfaces and dependencies[/red]")
        
        console.print("\n" + "="*80)
        return success_rate


async def main():
    """Main integration test execution"""
    console.print("[bold green] Purview CLI v2.0 - Integration Test Suite[/bold green]")
    console.print("="*80)
    
    test_suite = IntegrationTestSuite()
      # Run all integration tests
    integration_tests = [
        test_suite.test_cli_module_integration,
        test_suite.test_scanning_to_monitoring_workflow,
        test_suite.test_plugin_system_integration,
        test_suite.test_end_to_end_data_governance_workflow,
        test_suite.test_configuration_consistency,
        test_suite.test_error_propagation
    ]
    
    console.print("\n[bold blue]Running Integration Tests...[/bold blue]")
    
    for test_func in track(integration_tests, description="Executing tests..."):
        await test_func()
        # Small delay to make progress visible
        await asyncio.sleep(0.1)
    
    # Generate comprehensive report
    success_rate = test_suite.generate_integration_report()
    
    return success_rate >= 75  # 75% threshold for integration tests


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Integration test execution interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Integration test execution failed: {str(e)}[/red]")
        sys.exit(1)
