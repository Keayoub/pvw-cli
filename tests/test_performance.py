#!/usr/bin/env python3
"""
Performance Test Suite for Enhanced Purview CLI v2.0
Tests performance characteristics of all modules under various load conditions
"""

import sys
import os
from pathlib import Path
import asyncio
import time
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import Mock, patch, AsyncMock
import json
import tempfile
from typing import Dict, List, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

console = Console()

class PerformanceTestSuite:
    """Performance testing suite for Enhanced Purview CLI"""
    
    def __init__(self):
        self.test_results = []
        self.mock_config = {
            'account_name': 'perf-test-purview',
            'tenant_id': 'test-tenant-id',
            'client_id': 'test-client-id',
            'client_secret': 'test-client-secret',
            'endpoint': 'https://perf-test.purview.azure.com'
        }
        self.baseline_metrics = {}
    
    def measure_performance(self, test_name: str, test_func, *args, **kwargs):
        """Measure performance of a test function"""
        # Record baseline system metrics
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = psutil.cpu_percent()
        
        # Execute test and measure time
        start_time = time.time()
        try:
            result = test_func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Record final system metrics
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = psutil.cpu_percent()
        
        # Calculate resource usage
        memory_usage = final_memory - initial_memory
        cpu_usage = final_cpu
        
        # Record results
        perf_result = {
            'test_name': test_name,
            'execution_time': execution_time,
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
            'success': success,
            'error': error,
            'result': result
        }
        
        self.test_results.append(perf_result)
        
        # Log result
        status = "✅ PASS" if success else "❌ FAIL"
        console.print(f"[{'green' if success else 'red'}]{status} {test_name}[/{'green' if success else 'red'}]")
        console.print(f"[blue]  Time: {execution_time:.3f}s | Memory: {memory_usage:.1f}MB | CPU: {cpu_usage:.1f}%[/blue]")
        
        if error:
            console.print(f"[red]  Error: {error}[/red]")
        
        return perf_result
    
    async def measure_async_performance(self, test_name: str, test_func, *args, **kwargs):
        """Measure performance of an async test function"""
        # Record baseline system metrics
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = psutil.cpu_percent()
        
        # Execute async test and measure time
        start_time = time.time()
        try:
            result = await test_func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Record final system metrics
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_cpu = psutil.cpu_percent()
        
        # Calculate resource usage
        memory_usage = final_memory - initial_memory
        cpu_usage = final_cpu
        
        # Record results
        perf_result = {
            'test_name': test_name,
            'execution_time': execution_time,
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
            'success': success,
            'error': error,
            'result': result
        }
        
        self.test_results.append(perf_result)
        
        # Log result
        status = "✅ PASS" if success else "❌ FAIL"
        console.print(f"[{'green' if success else 'red'}]{status} {test_name}[/{'green' if success else 'red'}]")
        console.print(f"[blue]  Time: {execution_time:.3f}s | Memory: {memory_usage:.1f}MB | CPU: {cpu_usage:.1f}%[/blue]")
        
        if error:
            console.print(f"[red]  Error: {error}[/red]")
        
        return perf_result
    
    def test_scanning_manager_performance(self):
        """Test scanning manager performance with multiple operations"""
        from purviewcli.client.scanning_operations import ScanningManager
        
        scanning_manager = ScanningManager(self.mock_config)
        
        # Mock multiple scan operations
        mock_scan_result = {
            'scanId': f'perf-scan-{i}',
            'status': 'Running',
            'dataSourceName': f'perf-datasource-{i}'
        }
        
        def bulk_scan_operations():
            results = []
            with patch.object(scanning_manager, 'start_scan', new_callable=AsyncMock) as mock_start:
                mock_start.return_value = mock_scan_result
                
                # Simulate 50 scan operations
                for i in range(50):
                    try:
                        # Simulate scan start
                        result = {'scanId': f'perf-scan-{i}', 'status': 'Running'}
                        results.append(result)
                    except Exception as e:
                        results.append({'error': str(e)})
            
            return len(results)
        
        return bulk_scan_operations()
    
    def test_business_rules_performance(self):
        """Test business rules engine performance with multiple entities"""
        from purviewcli.client.business_rules import BusinessRulesEngine
        
        rules_engine = BusinessRulesEngine(self.mock_config)
        
        # Mock entity data for bulk compliance checking
        mock_entities = []
        for i in range(100):
            mock_entities.append({
                'guid': f'perf-entity-{i}',
                'name': f'perf_entity_{i}',
                'owner': f'owner{i}@company.com',
                'classifications': ['PII'] if i % 3 == 0 else ['Public'],
                'qualifiedName': f'perf_entity_{i}@datasource'
            })
        
        def bulk_compliance_check():
            results = []
            with patch.object(rules_engine, '_get_entity_data') as mock_get_entity:
                for i, entity in enumerate(mock_entities):
                    mock_get_entity.return_value = entity
                    try:
                        compliance_result = rules_engine.check_entity_compliance(entity['guid'])
                        results.append(compliance_result)
                    except Exception as e:
                        results.append({'error': str(e)})
            
            return len(results)
        
        return bulk_compliance_check()
    
    def test_monitoring_dashboard_performance(self):
        """Test monitoring dashboard performance with metric collection"""
        from purviewcli.client.monitoring_dashboard import MonitoringDashboard
        
        dashboard = MonitoringDashboard(self.mock_config)
        
        # Mock extensive metrics data
        mock_metrics = {
            'total_entities': 10000,
            'total_scans': 500,
            'active_scans': 25,
            'failed_scans': 10,
            'classification_coverage': 0.85,
            'lineage_completeness': 0.75,
            'api_response_times': [0.1, 0.2, 0.15, 0.3, 0.25] * 100,  # 500 measurements
            'entity_types': {'Table': 5000, 'Column': 25000, 'Dataset': 1000},
            'daily_scans': list(range(1, 31)),  # 30 days of data
            'hourly_api_calls': list(range(1, 25))  # 24 hours of data
        }
        
        def bulk_metrics_collection():
            results = []
            with patch.object(dashboard, '_fetch_purview_metrics', return_value=mock_metrics):
                # Collect metrics 20 times (simulating frequent monitoring)
                for i in range(20):
                    try:
                        metrics = dashboard.collect_metrics()
                        results.append(metrics)
                    except Exception as e:
                        results.append({'error': str(e)})
            
            return len(results)
        
        return bulk_metrics_collection()
    
    def test_ml_integration_performance(self):
        """Test ML integration performance with large datasets"""
        from purviewcli.client.ml_integration import IntelligentDataDiscovery, MLRecommendationEngine
        
        ml_discovery = IntelligentDataDiscovery(self.mock_config)
        ml_recommendation = MLRecommendationEngine(self.mock_config)
        
        # Mock large dataset for ML analysis
        mock_entities = []
        for i in range(200):
            mock_entities.append({
                'guid': f'ml-entity-{i}',
                'name': f'ml_entity_{i}',
                'attributes': {
                    'schema': f'schema_{i % 10}',
                    'table_name': f'table_{i}',
                    'column_count': i % 50 + 1,
                    'row_count': (i + 1) * 1000,
                    'data_type': 'structured' if i % 2 == 0 else 'unstructured'
                }
            })
        
        def bulk_ml_analysis():
            results = []
            
            # Mock similarity analysis
            mock_similarity = {
                'similar_entities': [
                    {'entity_guid': f'similar-{j}', 'similarity_score': 0.8 + (j * 0.01)}
                    for j in range(10)
                ],
                'patterns': ['common_schema', 'similar_naming', 'data_type_match']
            }
            
            # Mock recommendations
            mock_recommendations = [
                {'entity_guid': f'ml-entity-{i}', 'recommendation_type': 'classification', 'value': 'PII'}
                for i in range(50)
            ]
            
            with patch.object(ml_discovery, 'find_similar_entities', return_value=mock_similarity):
                with patch.object(ml_recommendation, 'generate_recommendations', return_value=mock_recommendations):
                    # Perform ML analysis on 50 entities
                    for i in range(50):
                        try:
                            # Similarity analysis
                            similarity_result = ml_discovery.find_similar_entities(f'ml-entity-{i}')
                            results.append(similarity_result)
                            
                            # Recommendation generation
                            if i % 10 == 0:  # Every 10th entity
                                recommendations = ml_recommendation.generate_recommendations([f'ml-entity-{i}'])
                                results.append(recommendations)
                        except Exception as e:
                            results.append({'error': str(e)})
            
            return len(results)
        
        return bulk_ml_analysis()
    
    def test_lineage_analysis_performance(self):
        """Test lineage analysis performance with complex lineage graphs"""
        from purviewcli.client.lineage_visualization import AdvancedLineageAnalyzer
        
        lineage_analyzer = AdvancedLineageAnalyzer(self.mock_config)
        
        # Mock complex lineage data
        def create_mock_lineage(entity_guid, depth=3):
            return {
                'entity_guid': entity_guid,
                'upstream_entities': [f'{entity_guid}_upstream_{i}' for i in range(depth * 2)],
                'downstream_entities': [f'{entity_guid}_downstream_{i}' for i in range(depth * 3)],
                'lineage_depth': depth,
                'total_entities': depth * 5,
                'critical_path': True if depth > 2 else False
            }
        
        def bulk_lineage_analysis():
            results = []
            
            # Analyze lineage for 30 entities with varying complexity
            for i in range(30):
                entity_guid = f'lineage-entity-{i}'
                depth = (i % 5) + 1  # Depth from 1 to 5
                
                mock_lineage = create_mock_lineage(entity_guid, depth)
                
                with patch.object(lineage_analyzer, 'analyze_lineage_impact', return_value=mock_lineage):
                    try:
                        lineage_result = lineage_analyzer.analyze_lineage_impact(entity_guid)
                        results.append(lineage_result)
                        
                        # Also test gap detection every 5 entities
                        if i % 5 == 0:
                            mock_gaps = {
                                'missing_lineage': [f'gap-entity-{j}' for j in range(3)],
                                'incomplete_lineage': [f'incomplete-entity-{j}' for j in range(2)]
                            }
                            with patch.object(lineage_analyzer, 'detect_lineage_gaps', return_value=mock_gaps):
                                gap_result = lineage_analyzer.detect_lineage_gaps([entity_guid])
                                results.append(gap_result)
                    except Exception as e:
                        results.append({'error': str(e)})
            
            return len(results)
        
        return bulk_lineage_analysis()
    
    def test_plugin_system_performance(self):
        """Test plugin system performance with multiple plugins"""
        from purviewcli.plugins.plugin_system import PluginManager
        
        plugin_manager = PluginManager()
        
        # Create multiple test plugins
        class PerformanceTestPlugin:
            def __init__(self, plugin_id):
                self.name = f"perf_plugin_{plugin_id}"
                self.version = "1.0.0"
                self.plugin_id = plugin_id
            
            def execute(self, **kwargs):
                # Simulate some processing
                time.sleep(0.001)  # 1ms processing time
                return {
                    'plugin_id': self.plugin_id,
                    'status': 'success',
                    'processed_items': 100,
                    'execution_time': 0.001
                }
        
        def bulk_plugin_execution():
            results = []
            
            # Register 20 plugins
            for i in range(20):
                plugin = PerformanceTestPlugin(i)
                plugin_manager.register_plugin(plugin)
            
            # Execute all plugins multiple times
            for execution_round in range(3):
                for i in range(20):
                    plugin_name = f"perf_plugin_{i}"
                    try:
                        result = plugin_manager.execute_plugin(plugin_name)
                        results.append(result)
                    except Exception as e:
                        results.append({'error': str(e)})
            
            return len(results)
        
        return bulk_plugin_execution()
    
    def test_concurrent_operations_performance(self):
        """Test performance under concurrent operations"""
        from purviewcli.client.monitoring_dashboard import MonitoringDashboard
        from purviewcli.client.business_rules import BusinessRulesEngine
        
        dashboard = MonitoringDashboard(self.mock_config)
        rules_engine = BusinessRulesEngine(self.mock_config)
        
        def concurrent_operation(operation_id):
            """Single concurrent operation"""
            results = []
            
            # Mock data for the operation
            mock_metrics = {'total_entities': 1000 + operation_id}
            mock_entity = {
                'guid': f'concurrent-entity-{operation_id}',
                'name': f'concurrent_entity_{operation_id}',
                'owner': f'owner{operation_id}@company.com'
            }
            
            try:
                # Simulate concurrent metrics collection
                with patch.object(dashboard, '_fetch_purview_metrics', return_value=mock_metrics):
                    metrics = dashboard.collect_metrics()
                    results.append(metrics)
                
                # Simulate concurrent compliance checking
                with patch.object(rules_engine, '_get_entity_data', return_value=mock_entity):
                    compliance = rules_engine.check_entity_compliance(mock_entity['guid'])
                    results.append(compliance)
                
                return len(results)
            except Exception as e:
                return {'error': str(e)}
        
        def bulk_concurrent_operations():
            results = []
            
            # Execute 10 concurrent operations
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(concurrent_operation, i) for i in range(10)]
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        results.append({'error': str(e)})
            
            return len(results)
        
        return bulk_concurrent_operations()
    
    async def test_async_operations_performance(self):
        """Test async operations performance"""
        from purviewcli.client.scanning_operations import ScanningManager
        
        scanning_manager = ScanningManager(self.mock_config)
        
        async def async_scan_operation(scan_id):
            """Single async scan operation"""
            mock_result = {
                'scanId': f'async-scan-{scan_id}',
                'status': 'Running',
                'dataSourceName': f'async-datasource-{scan_id}'
            }
            
            with patch.object(scanning_manager, 'start_scan', new_callable=AsyncMock) as mock_start:
                mock_start.return_value = mock_result
                try:
                    result = await scanning_manager.start_scan(f'async-datasource-{scan_id}')
                    return result
                except Exception as e:
                    return {'error': str(e)}
        
        # Execute 20 async scan operations concurrently
        tasks = [async_scan_operation(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful operations
        successful_operations = sum(1 for result in results if isinstance(result, dict) and 'scanId' in result)
        return successful_operations
    
    def test_memory_usage_under_load(self):
        """Test memory usage under sustained load"""
        from purviewcli.client.ml_integration import IntelligentDataDiscovery
        
        ml_discovery = IntelligentDataDiscovery(self.mock_config)
        
        # Track memory usage over time
        memory_samples = []
        process = psutil.Process()
        
        def memory_intensive_operation():
            # Simulate memory-intensive ML operations
            large_dataset = []
            for i in range(1000):
                large_dataset.append({
                    'id': i,
                    'data': f'large_data_entry_{i}',
                    'features': list(range(100)),  # 100 features per entry
                    'metadata': {'category': f'category_{i % 10}', 'timestamp': time.time()}
                })
            
            # Record memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_samples.append(current_memory)
            
            # Mock ML analysis on large dataset
            mock_analysis = {
                'processed_entities': len(large_dataset),
                'memory_usage': current_memory,
                'patterns_found': i % 5 + 1
            }
            
            return mock_analysis
        
        # Run memory-intensive operations
        results = []
        for i in range(10):
            try:
                result = memory_intensive_operation()
                results.append(result)
            except Exception as e:
                results.append({'error': str(e)})
        
        # Calculate memory growth
        if memory_samples:
            memory_growth = max(memory_samples) - min(memory_samples)
            avg_memory = sum(memory_samples) / len(memory_samples)
            
            # Add memory stats to results
            results.append({
                'memory_stats': {
                    'samples': len(memory_samples),
                    'growth_mb': memory_growth,
                    'average_mb': avg_memory,
                    'peak_mb': max(memory_samples)
                }
            })
        
        return len(results)
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        console.print("\n" + "="*80)
        console.print(Panel("[bold blue]Enhanced Purview CLI v2.0 - Performance Test Report[/bold blue]"))
        
        if not self.test_results:
            console.print("[red]No performance test results available[/red]")
            return
        
        # Calculate overall statistics
        total_tests = len(self.test_results)
        successful_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        avg_execution_time = sum(r['execution_time'] for r in successful_tests) / len(successful_tests) if successful_tests else 0
        max_execution_time = max(r['execution_time'] for r in successful_tests) if successful_tests else 0
        total_memory_usage = sum(r['memory_usage'] for r in successful_tests) if successful_tests else 0
        avg_cpu_usage = sum(r['cpu_usage'] for r in successful_tests) / len(successful_tests) if successful_tests else 0
        
        # Summary statistics table
        summary_table = Table(title="Performance Summary", show_header=True, header_style="bold magenta")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")
        summary_table.add_column("Assessment", style="green")
        
        summary_table.add_row("Total Tests", str(total_tests), "📊")
        summary_table.add_row("Successful Tests", str(len(successful_tests)), "✅")
        summary_table.add_row("Failed Tests", str(len(failed_tests)), "❌" if failed_tests else "✅")
        summary_table.add_row("Avg Execution Time", f"{avg_execution_time:.3f}s", "⚡" if avg_execution_time < 1.0 else "⚠️")
        summary_table.add_row("Max Execution Time", f"{max_execution_time:.3f}s", "⚡" if max_execution_time < 5.0 else "⚠️")
        summary_table.add_row("Total Memory Usage", f"{total_memory_usage:.1f}MB", "💾")
        summary_table.add_row("Avg CPU Usage", f"{avg_cpu_usage:.1f}%", "🔥" if avg_cpu_usage < 50 else "⚠️")
        
        console.print(summary_table)
        
        # Detailed performance results
        perf_table = Table(title="Detailed Performance Results", show_header=True, header_style="bold magenta")
        perf_table.add_column("Test Name", style="cyan", width=30)
        perf_table.add_column("Time (s)", style="yellow", width=10)
        perf_table.add_column("Memory (MB)", style="blue", width=12)
        perf_table.add_column("CPU (%)", style="green", width=10)
        perf_table.add_column("Status", style="white", width=8)
        
        for result in self.test_results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            perf_table.add_row(
                result['test_name'],
                f"{result['execution_time']:.3f}",
                f"{result['memory_usage']:.1f}",
                f"{result['cpu_usage']:.1f}",
                status
            )
        
        console.print(perf_table)
        
        # Performance assessment
        console.print("\n[bold blue]Performance Assessment:[/bold blue]")
        
        # Determine overall performance rating
        performance_score = 0
        
        if avg_execution_time < 1.0:
            performance_score += 25
        elif avg_execution_time < 2.0:
            performance_score += 20
        elif avg_execution_time < 5.0:
            performance_score += 15
        else:
            performance_score += 10
        
        if max_execution_time < 5.0:
            performance_score += 25
        elif max_execution_time < 10.0:
            performance_score += 20
        else:
            performance_score += 10
        
        if total_memory_usage < 100:
            performance_score += 25
        elif total_memory_usage < 250:
            performance_score += 20
        elif total_memory_usage < 500:
            performance_score += 15
        else:
            performance_score += 10
        
        if len(failed_tests) == 0:
            performance_score += 25
        elif len(failed_tests) < 3:
            performance_score += 20
        else:
            performance_score += 10
        
        if performance_score >= 85:
            console.print("[green]🚀 Excellent performance! All modules are highly optimized.[/green]")
            console.print("[green]✓ Ready for high-load production environments[/green]")
            console.print("[green]✓ Efficient resource utilization[/green]")
            console.print("[green]✓ Fast response times[/green]")
        elif performance_score >= 70:
            console.print("[yellow]⚡ Good performance with room for optimization.[/yellow]")
            console.print("[yellow]• Consider optimizing slower operations[/yellow]")
            console.print("[yellow]• Monitor memory usage in production[/yellow]")
            console.print("[yellow]• Performance is acceptable for most use cases[/yellow]")
        elif performance_score >= 50:
            console.print("[orange]⚠️ Moderate performance. Optimization recommended.[/orange]")
            console.print("[orange]• Significant performance improvements needed[/orange]")
            console.print("[orange]• Consider code optimization and caching[/orange]")
            console.print("[orange]• May impact user experience under load[/orange]")
        else:
            console.print("[red]🐌 Poor performance. Immediate optimization required.[/red]")
            console.print("[red]• Critical performance issues detected[/red]")
            console.print("[red]• Not suitable for production without optimization[/red]")
            console.print("[red]• Review algorithms and resource usage patterns[/red]")
        
        # Specific recommendations
        console.print("\n[bold blue]Optimization Recommendations:[/bold blue]")
        
        if avg_execution_time > 2.0:
            console.print("[yellow]• Implement caching for frequently accessed data[/yellow]")
            console.print("[yellow]• Consider async processing for long-running operations[/yellow]")
        
        if total_memory_usage > 200:
            console.print("[yellow]• Optimize data structures and reduce memory footprint[/yellow]")
            console.print("[yellow]• Implement data streaming for large datasets[/yellow]")
        
        if failed_tests:
            console.print("[red]• Fix failing tests to ensure reliable performance[/red]")
            console.print("[red]• Review error handling and exception management[/red]")
        
        console.print("\n" + "="*80)
        return performance_score


async def main():
    """Main performance test execution"""
    console.print("[bold green]Enhanced Purview CLI v2.0 - Performance Test Suite[/bold green]")
    console.print("="*80)
    
    test_suite = PerformanceTestSuite()
    
    # Performance tests
    console.print("\n[bold blue]Running Performance Tests...[/bold blue]")
    
    # Synchronous performance tests
    sync_tests = [
        ("Scanning Manager Performance", test_suite.test_scanning_manager_performance),
        ("Business Rules Performance", test_suite.test_business_rules_performance),
        ("Monitoring Dashboard Performance", test_suite.test_monitoring_dashboard_performance),
        ("ML Integration Performance", test_suite.test_ml_integration_performance),
        ("Lineage Analysis Performance", test_suite.test_lineage_analysis_performance),
        ("Plugin System Performance", test_suite.test_plugin_system_performance),
        ("Concurrent Operations Performance", test_suite.test_concurrent_operations_performance),
        ("Memory Usage Under Load", test_suite.test_memory_usage_under_load)
    ]
    
    for test_name, test_func in sync_tests:
        console.print(f"\n[yellow]Running: {test_name}[/yellow]")
        test_suite.measure_performance(test_name, test_func)
    
    # Asynchronous performance tests
    console.print(f"\n[yellow]Running: Async Operations Performance[/yellow]")
    await test_suite.measure_async_performance(
        "Async Operations Performance", 
        test_suite.test_async_operations_performance
    )
    
    # Generate comprehensive performance report
    performance_score = test_suite.generate_performance_report()
    
    return performance_score >= 70  # 70% threshold for acceptable performance


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Performance test execution interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Performance test execution failed: {str(e)}[/red]")
        sys.exit(1)
