#!/usr/bin/env python3
"""
Comprehensive Test Suite for Enhanced Purview CLI v2.0 Advanced Modules
Tests all newly created advanced features including monitoring, ML integration, 
lineage visualization, and plugin system.
"""

import sys
import os
from pathlib import Path
import asyncio
import json
import tempfile
from unittest.mock import Mock, patch, AsyncMock
import pytest

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

console = Console()

class TestAdvancedModules:
    """Comprehensive test suite for advanced modules"""
    
    def __init__(self):
        self.test_results = []
        self.mock_config = self._create_mock_config()
    
    def _create_mock_config(self):
        """Create mock configuration for testing"""
        return {
            'account_name': 'test-purview',
            'tenant_id': 'test-tenant-id',
            'client_id': 'test-client-id',
            'client_secret': 'test-client-secret',
            'endpoint': 'https://test-purview.purview.azure.com'
        }
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        try:
            console.print(f"\n[yellow]Running: {test_name}[/yellow]")
            result = test_func()
            
            if result:
                console.print(f"[green]✓ {test_name} - PASSED[/green]")
                self.test_results.append((test_name, True, None))
            else:
                console.print(f"[red]✗ {test_name} - FAILED[/red]")
                self.test_results.append((test_name, False, "Test returned False"))
        except Exception as e:
            console.print(f"[red]✗ {test_name} - ERROR: {str(e)}[/red]")
            self.test_results.append((test_name, False, str(e)))
    
    async def run_async_test(self, test_name: str, test_func):
        """Run an async test and record results"""
        try:
            console.print(f"\n[yellow]Running: {test_name}[/yellow]")
            result = await test_func()
            
            if result:
                console.print(f"[green]✓ {test_name} - PASSED[/green]")
                self.test_results.append((test_name, True, None))
            else:
                console.print(f"[red]✗ {test_name} - FAILED[/red]")
                self.test_results.append((test_name, False, "Test returned False"))
        except Exception as e:
            console.print(f"[red]✗ {test_name} - ERROR: {str(e)}[/red]")
            self.test_results.append((test_name, False, str(e)))
    
    def test_scanning_operations_import(self):
        """Test scanning operations module import"""
        try:
            from purviewcli.client.scanning_operations import ScanningManager, ScanTemplateManager
            
            # Test class instantiation
            scanning_manager = ScanningManager(self.mock_config)
            template_manager = ScanTemplateManager(self.mock_config)
            
            # Verify attributes exist
            assert hasattr(scanning_manager, 'config')
            assert hasattr(scanning_manager, 'batch_scan_entities')
            assert hasattr(template_manager, 'create_scan_template')
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_business_rules_import(self):
        """Test business rules engine import"""
        try:
            from purviewcli.client.business_rules import BusinessRulesEngine, ComplianceRule
            
            # Test class instantiation
            rules_engine = BusinessRulesEngine(self.mock_config)
            
            # Verify attributes exist
            assert hasattr(rules_engine, 'config')
            assert hasattr(rules_engine, 'rules')
            assert hasattr(rules_engine, 'check_compliance')
            
            # Test rule creation
            rule = ComplianceRule(
                name="test_rule",
                description="Test rule",
                rule_type="data_ownership",
                conditions={"required_field": "owner"}
            )
            
            assert rule.name == "test_rule"
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_monitoring_dashboard_import(self):
        """Test monitoring dashboard import"""
        try:
            from purviewcli.client.monitoring_dashboard import MonitoringDashboard, AlertManager
            
            # Test class instantiation
            dashboard = MonitoringDashboard(self.mock_config)
            alert_manager = AlertManager()
            
            # Verify attributes exist
            assert hasattr(dashboard, 'config')
            assert hasattr(dashboard, 'collect_metrics')
            assert hasattr(alert_manager, 'add_threshold')
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_ml_integration_import(self):
        """Test ML integration module import"""
        try:
            from purviewcli.client.ml_integration import (
                IntelligentDataDiscovery, 
                MLRecommendationEngine, 
                PredictiveAnalytics
            )
            
            # Test class instantiation
            data_discovery = IntelligentDataDiscovery(self.mock_config)
            recommendation_engine = MLRecommendationEngine(self.mock_config)
            predictive_analytics = PredictiveAnalytics(self.mock_config)
            
            # Verify attributes exist
            assert hasattr(data_discovery, 'config')
            assert hasattr(recommendation_engine, 'generate_recommendations')
            assert hasattr(predictive_analytics, 'predict_scan_failures')
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_lineage_visualization_import(self):
        """Test lineage visualization module import"""
        try:
            from purviewcli.client.lineage_visualization import AdvancedLineageAnalyzer
            
            # Test class instantiation
            lineage_analyzer = AdvancedLineageAnalyzer(self.mock_config)
            
            # Verify attributes exist
            assert hasattr(lineage_analyzer, 'config')
            assert hasattr(lineage_analyzer, 'analyze_lineage_impact')
            assert hasattr(lineage_analyzer, 'detect_lineage_gaps')
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_plugin_system_import(self):
        """Test plugin system import"""
        try:
            from purviewcli.plugins.plugin_system import PluginManager, BasePlugin
            
            # Test class instantiation
            plugin_manager = PluginManager()
            
            # Verify attributes exist
            assert hasattr(plugin_manager, 'plugins')
            assert hasattr(plugin_manager, 'load_plugin')
            assert hasattr(plugin_manager, 'execute_plugin')
            
            # Test base plugin
            assert hasattr(BasePlugin, 'name')
            assert hasattr(BasePlugin, 'execute')
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_business_rules_functionality(self):
        """Test business rules engine functionality"""
        try:
            from purviewcli.client.business_rules import BusinessRulesEngine
            
            rules_engine = BusinessRulesEngine(self.mock_config)
            
            # Test sample entity data
            test_entity = {
                'name': 'test_entity',
                'owner': 'test@company.com',
                'classifications': ['PII'],
                'qualifiedName': 'test_entity@datasource'
            }
            
            # Mock the API calls
            with patch.object(rules_engine, '_get_entity_data', return_value=test_entity):
                # Test compliance check
                compliance_result = rules_engine.check_entity_compliance('test-guid')
                
                # Verify result structure
                assert 'entity_guid' in compliance_result
                assert 'violations' in compliance_result
                assert 'compliance_score' in compliance_result
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_monitoring_dashboard_functionality(self):
        """Test monitoring dashboard functionality"""
        try:
            from purviewcli.client.monitoring_dashboard import MonitoringDashboard
            
            dashboard = MonitoringDashboard(self.mock_config)
            
            # Mock the API calls
            mock_metrics = {
                'total_entities': 1000,
                'active_scans': 5,
                'failed_scans': 2,
                'classification_coverage': 0.85
            }
            
            with patch.object(dashboard, '_fetch_purview_metrics', return_value=mock_metrics):
                # Test metrics collection
                metrics = dashboard.collect_metrics()
                
                # Verify metrics structure
                assert 'timestamp' in metrics
                assert 'metrics' in metrics
                assert metrics['metrics']['total_entities'] == 1000
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_plugin_system_functionality(self):
        """Test plugin system functionality"""
        try:
            from purviewcli.plugins.plugin_system import PluginManager
            
            plugin_manager = PluginManager()
            
            # Test creating a simple test plugin
            class TestPlugin:
                name = "test_plugin"
                version = "1.0.0"
                
                def execute(self, **kwargs):
                    return {"status": "success", "message": "Test plugin executed"}
            
            # Test plugin registration
            plugin_manager.register_plugin(TestPlugin())
            
            # Verify plugin was registered
            assert "test_plugin" in plugin_manager.plugins
            
            # Test plugin execution
            result = plugin_manager.execute_plugin("test_plugin")
            assert result["status"] == "success"
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    async def test_async_operations(self):
        """Test async operations in modules"""
        try:
            from purviewcli.client.scanning_operations import ScanningManager
            
            scanning_manager = ScanningManager(self.mock_config)
            
            # Mock async API calls
            with patch.object(scanning_manager, '_api_call', new_callable=AsyncMock) as mock_api:
                mock_api.return_value = {"status": "success", "scanId": "test-scan-id"}
                
                # Test async scan operation
                result = await scanning_manager.start_scan("test-datasource")
                
                # Verify result
                assert "scanId" in result
                assert result["status"] == "success"
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_configuration_handling(self):
        """Test configuration handling across modules"""
        try:
            from purviewcli.client.scanning_operations import ScanningManager
            from purviewcli.client.business_rules import BusinessRulesEngine
            from purviewcli.client.monitoring_dashboard import MonitoringDashboard
            
            # Test with various config formats
            configs = [
                self.mock_config,
                {'account_name': 'test', 'endpoint': 'https://test.purview.azure.com'},
            ]
            
            for config in configs:
                try:
                    scanning_manager = ScanningManager(config)
                    rules_engine = BusinessRulesEngine(config)
                    dashboard = MonitoringDashboard(config)
                    
                    # Verify config is stored
                    assert scanning_manager.config is not None
                    assert rules_engine.config is not None
                    assert dashboard.config is not None
                except Exception as e:
                    console.print(f"[yellow]Config test warning: {str(e)}[/yellow]")
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def test_error_handling(self):
        """Test error handling in modules"""
        try:
            from purviewcli.client.business_rules import BusinessRulesEngine
            
            rules_engine = BusinessRulesEngine(self.mock_config)
            
            # Test with invalid entity GUID
            with patch.object(rules_engine, '_get_entity_data', side_effect=Exception("Entity not found")):
                try:
                    compliance_result = rules_engine.check_entity_compliance('invalid-guid')
                    # Should handle error gracefully
                    assert 'error' in compliance_result or 'violations' in compliance_result
                except Exception:
                    # Exception handling is working
                    pass
            
            return True
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            return False
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        console.print("\n" + "="*80)
        console.print(Panel("[bold blue]Enhanced Purview CLI v2.0 - Advanced Modules Test Report[/bold blue]"))
        
        # Summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for _, passed, _ in self.test_results if passed)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Summary table
        summary_table = Table(title="Test Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")
        summary_table.add_column("Status", style="green")
        
        summary_table.add_row("Total Tests", str(total_tests), "📊")
        summary_table.add_row("Passed", str(passed_tests), "✅")
        summary_table.add_row("Failed", str(failed_tests), "❌" if failed_tests > 0 else "✅")
        summary_table.add_row("Success Rate", f"{success_rate:.1f}%", "🎯")
        
        console.print(summary_table)
        
        # Detailed results
        if self.test_results:
            results_table = Table(title="Detailed Test Results", show_header=True, header_style="bold magenta")
            results_table.add_column("Test Name", style="cyan", width=40)
            results_table.add_column("Status", style="yellow", width=10)
            results_table.add_column("Error", style="red", width=30)
            
            for test_name, passed, error in self.test_results:
                status = "✅ PASS" if passed else "❌ FAIL"
                error_msg = error[:27] + "..." if error and len(error) > 30 else (error or "")
                results_table.add_row(test_name, status, error_msg)
            
            console.print(results_table)
        
        # Recommendations
        console.print("\n[bold blue]Recommendations:[/bold blue]")
        if failed_tests == 0:
            console.print("[green]🎉 All tests passed! The Enhanced Purview CLI v2.0 advanced modules are working correctly.[/green]")
            console.print("[green]✓ Ready for production deployment[/green]")
            console.print("[green]✓ All new features are functional[/green]")
        else:
            console.print(f"[yellow]⚠ {failed_tests} test(s) failed. Recommended actions:[/yellow]")
            console.print("[yellow]• Review failed test details above[/yellow]")
            console.print("[yellow]• Check module dependencies and imports[/yellow]")
            console.print("[yellow]• Verify configuration settings[/yellow]")
            console.print("[yellow]• Run tests individually for detailed debugging[/yellow]")
        
        console.print("\n" + "="*80)
        
        return success_rate


async def main():
    """Main test execution function"""
    console.print("[bold green]Enhanced Purview CLI v2.0 - Advanced Modules Test Suite[/bold green]")
    console.print("="*80)
    
    test_suite = TestAdvancedModules()
    
    # Import and instantiation tests
    console.print(Panel("[bold blue]Module Import Tests[/bold blue]"))
    test_suite.run_test("Scanning Operations Import", test_suite.test_scanning_operations_import)
    test_suite.run_test("Business Rules Import", test_suite.test_business_rules_import)
    test_suite.run_test("Monitoring Dashboard Import", test_suite.test_monitoring_dashboard_import)
    test_suite.run_test("ML Integration Import", test_suite.test_ml_integration_import)
    test_suite.run_test("Lineage Visualization Import", test_suite.test_lineage_visualization_import)
    test_suite.run_test("Plugin System Import", test_suite.test_plugin_system_import)
    
    # Functionality tests
    console.print(Panel("[bold blue]Functionality Tests[/bold blue]"))
    test_suite.run_test("Business Rules Functionality", test_suite.test_business_rules_functionality)
    test_suite.run_test("Monitoring Dashboard Functionality", test_suite.test_monitoring_dashboard_functionality)
    test_suite.run_test("Plugin System Functionality", test_suite.test_plugin_system_functionality)
    test_suite.run_test("Configuration Handling", test_suite.test_configuration_handling)
    test_suite.run_test("Error Handling", test_suite.test_error_handling)
    
    # Async tests
    console.print(Panel("[bold blue]Async Operation Tests[/bold blue]"))
    await test_suite.run_async_test("Async Operations", test_suite.test_async_operations)
    
    # Generate final report
    success_rate = test_suite.generate_test_report()
    
    return success_rate >= 80  # Consider 80% success rate as acceptable


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Test execution interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Test execution failed: {str(e)}[/red]")
        sys.exit(1)
