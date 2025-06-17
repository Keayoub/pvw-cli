#!/usr/bin/env python3
"""
Comprehensive Test Runner for  Purview CLI v1.0.0
Executes all test suites and provides unified reporting
"""

import sys
import os
from pathlib import Path
import asyncio
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.live import Live

console = Console()

class ComprehensiveTestRunner:
    """Unified test runner for all  Purview CLI test suites"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        self.test_suites = [
            {
                'name': 'Unit Tests (Existing)',
                'description': 'Core functionality and existing modules',
                'script': 'test_functionality.py',
                'category': 'core'
            },
            {
                'name': 'CSV Operations Tests (Existing)',
                'description': 'CSV import/export and data validation',
                'script': 'test_csv_functionality.py',
                'category': 'core'
            },
            {
                'name': 'Advanced Modules Tests',
                'description': 'New advanced modules (monitoring, etc.)',
                'script': 'tests/test_advanced_modules.py',
                'category': 'advanced'
            },
            {
                'name': 'Integration Tests',
                'description': 'Module integration and workflows',
                'script': 'tests/test_integration.py',
                'category': 'integration'
            },
            {
                'name': 'Performance Tests',
                'description': 'Performance and load testing',
                'script': 'tests/test_performance.py',
                'category': 'performance'
            }
        ]
    
    def run_test_suite(self, test_suite: Dict[str, str]) -> Dict[str, Any]:
        """Run a single test suite"""
        console.print(f"\n[bold blue]Running: {test_suite['name']}[/bold blue]")
        console.print(f"[yellow]{test_suite['description']}[/yellow]")
        
        script_path = project_root / test_suite['script']
        
        if not script_path.exists():
            return {
                'name': test_suite['name'],
                'status': 'skipped',
                'reason': f"Test script not found: {script_path}",
                'execution_time': 0,
                'output': '',
                'errors': ''
            }
        
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Determine status based on return code
            if result.returncode == 0:
                status = 'passed'
                console.print(f"[green]✅ {test_suite['name']} - PASSED[/green]")
            else:
                status = 'failed'
                console.print(f"[red]❌ {test_suite['name']} - FAILED[/red]")
            
            return {
                'name': test_suite['name'],
                'category': test_suite['category'],
                'status': status,
                'execution_time': execution_time,
                'output': result.stdout,
                'errors': result.stderr,
                'return_code': result.returncode
            }
        
        except subprocess.TimeoutExpired:
            return {
                'name': test_suite['name'],
                'category': test_suite['category'],
                'status': 'timeout',
                'execution_time': 300,
                'output': '',
                'errors': 'Test execution timed out after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            return {
                'name': test_suite['name'],
                'category': test_suite['category'],
                'status': 'error',
                'execution_time': time.time() - start_time,
                'output': '',
                'errors': str(e),
                'return_code': -1
            }
    
    async def run_async_test_suite(self, test_suite: Dict[str, str]) -> Dict[str, Any]:
        """Run an async test suite"""
        console.print(f"\n[bold blue]Running: {test_suite['name']} (Async)[/bold blue]")
        console.print(f"[yellow]{test_suite['description']}[/yellow]")
        
        script_path = project_root / test_suite['script']
        
        if not script_path.exists():
            return {
                'name': test_suite['name'],
                'status': 'skipped',
                'reason': f"Test script not found: {script_path}",
                'execution_time': 0,
                'output': '',
                'errors': ''
            }
        
        start_time = time.time()
        
        try:
            # Run the async test script
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path),
                cwd=str(project_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait for completion with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=300  # 5 minute timeout
            )
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Determine status based on return code
            if process.returncode == 0:
                status = 'passed'
                console.print(f"[green]✅ {test_suite['name']} - PASSED[/green]")
            else:
                status = 'failed'
                console.print(f"[red]❌ {test_suite['name']} - FAILED[/red]")
            
            return {
                'name': test_suite['name'],
                'category': test_suite['category'],
                'status': status,
                'execution_time': execution_time,
                'output': stdout.decode() if stdout else '',
                'errors': stderr.decode() if stderr else '',
                'return_code': process.returncode
            }
        
        except asyncio.TimeoutError:
            return {
                'name': test_suite['name'],
                'category': test_suite['category'],
                'status': 'timeout',
                'execution_time': 300,
                'output': '',
                'errors': 'Test execution timed out after 5 minutes',
                'return_code': -1
            }
        except Exception as e:
            return {
                'name': test_suite['name'],
                'category': test_suite['category'],
                'status': 'error',
                'execution_time': time.time() - start_time,
                'output': '',
                'errors': str(e),
                'return_code': -1
            }
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if all required dependencies are available"""
        console.print("[bold blue]Checking Dependencies...[/bold blue]")
        
        dependencies = {
            'python': True,  # Already running Python
            'rich': False,
            'pandas': False,
            'psutil': False,
            'scikit-learn': False,
            'click': False,
            'asyncio': False
        }
        
        # Check each dependency
        for dep in dependencies:
            if dep == 'python':
                continue
            
            try:
                if dep == 'asyncio':
                    import asyncio
                else:
                    __import__(dep.replace('-', '_'))
                dependencies[dep] = True
                console.print(f"[green]✅ {dep}[/green]")
            except ImportError:
                dependencies[dep] = False
                console.print(f"[red]❌ {dep} - Missing[/red]")
        
        return dependencies
    
    def check_project_structure(self) -> Dict[str, bool]:
        """Check if project structure is correct"""
        console.print("\n[bold blue]Checking Project Structure...[/bold blue]")
        
        required_paths = {
            'purviewcli/': project_root / 'purviewcli',
            'purviewcli/client/': project_root / 'purviewcli' / 'client',
            'purviewcli/cli/': project_root / 'purviewcli' / 'cli',
            'purviewcli/plugins/': project_root / 'purviewcli' / 'plugins',
            'tests/': project_root / 'tests',
            'samples/': project_root / 'samples'
        }
        
        structure_check = {}
        for path_name, path in required_paths.items():
            exists = path.exists()
            structure_check[path_name] = exists
            status = "✅" if exists else "❌"
            console.print(f"{status} {path_name}")
        
        return structure_check
    
    def generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        if not self.test_results:
            return {}
        
        # Calculate overall statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'passed')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'failed')
        skipped_tests = sum(1 for result in self.test_results.values() if result['status'] == 'skipped')
        error_tests = sum(1 for result in self.test_results.values() if result['status'] == 'error')
        timeout_tests = sum(1 for result in self.test_results.values() if result['status'] == 'timeout')
        
        total_execution_time = sum(result['execution_time'] for result in self.test_results.values())
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Categorize results
        categories = {}
        for result in self.test_results.values():
            category = result.get('category', 'unknown')
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0, 'total': 0}
            
            categories[category]['total'] += 1
            if result['status'] == 'passed':
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'skipped_tests': skipped_tests,
            'error_tests': error_tests,
            'timeout_tests': timeout_tests,
            'success_rate': success_rate,
            'total_execution_time': total_execution_time,
            'categories': categories,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
    
    def generate_detailed_report(self):
        """Generate detailed test execution report"""
        console.print("\n" + "="*80)
        console.print(Panel("[bold blue] Purview CLI v1.0.0 - Comprehensive Test Report[/bold blue]"))
        
        summary = self.generate_test_summary()
        
        if not summary:
            console.print("[red]No test results available[/red]")
            return
        
        # Executive Summary
        console.print(Panel("[bold green]Executive Summary[/bold green]"))
        
        exec_table = Table(show_header=True, header_style="bold magenta")
        exec_table.add_column("Metric", style="cyan")
        exec_table.add_column("Value", style="yellow")
        exec_table.add_column("Assessment", style="green")
        
        exec_table.add_row("Total Test Suites", str(summary['total_tests']), "📊")
        exec_table.add_row("Passed", str(summary['passed_tests']), "✅")
        exec_table.add_row("Failed", str(summary['failed_tests']), "❌" if summary['failed_tests'] > 0 else "✅")
        exec_table.add_row("Skipped", str(summary['skipped_tests']), "⏭️" if summary['skipped_tests'] > 0 else "✅")
        exec_table.add_row("Errors", str(summary['error_tests']), "🚨" if summary['error_tests'] > 0 else "✅")
        exec_table.add_row("Timeouts", str(summary['timeout_tests']), "⏱️" if summary['timeout_tests'] > 0 else "✅")
        exec_table.add_row("Success Rate", f"{summary['success_rate']:.1f}%", 
                          "🎯" if summary['success_rate'] >= 90 else "⚠️" if summary['success_rate'] >= 70 else "❌")
        exec_table.add_row("Total Execution Time", f"{summary['total_execution_time']:.1f}s", "⚡")
        
        console.print(exec_table)
        
        # Category Breakdown
        if summary['categories']:
            console.print("\n[bold blue]Test Category Breakdown:[/bold blue]")
            
            cat_table = Table(show_header=True, header_style="bold magenta")
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Total", style="yellow")
            cat_table.add_column("Passed", style="green")
            cat_table.add_column("Failed", style="red")
            cat_table.add_column("Success Rate", style="blue")
            
            for category, stats in summary['categories'].items():
                success_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                cat_table.add_row(
                    category.title(),
                    str(stats['total']),
                    str(stats['passed']),
                    str(stats['failed']),
                    f"{success_rate:.1f}%"
                )
            
            console.print(cat_table)
        
        # Detailed Results
        console.print("\n[bold blue]Detailed Test Results:[/bold blue]")
        
        detail_table = Table(show_header=True, header_style="bold magenta")
        detail_table.add_column("Test Suite", style="cyan", width=25)
        detail_table.add_column("Status", style="yellow", width=10)
        detail_table.add_column("Time (s)", style="blue", width=10)
        detail_table.add_column("Category", style="green", width=12)
        detail_table.add_column("Issues", style="red", width=23)
        
        for test_name, result in self.test_results.items():
            status_map = {
                'passed': '✅ PASS',
                'failed': '❌ FAIL',
                'skipped': '⏭️ SKIP',
                'error': '🚨 ERROR',
                'timeout': '⏱️ TIMEOUT'
            }
            
            status = status_map.get(result['status'], result['status'])
            time_str = f"{result['execution_time']:.1f}"
            category = result.get('category', 'unknown').title()
            
            # Extract issues summary
            issues = ""
            if result['status'] != 'passed':
                if result.get('errors'):
                    issues = result['errors'][:20] + "..." if len(result['errors']) > 20 else result['errors']
                elif result.get('reason'):
                    issues = result['reason'][:20] + "..." if len(result['reason']) > 20 else result['reason']
            
            detail_table.add_row(test_name, status, time_str, category, issues)
        
        console.print(detail_table)
        
        # Recommendations
        console.print("\n[bold blue]Recommendations:[/bold blue]")
        
        if summary['success_rate'] >= 90:
            console.print("[green]🎉 Excellent! The  Purview CLI is ready for production.[/green]")
            console.print("[green]✓ All major test suites are passing[/green]")
            console.print("[green]✓ Core functionality is stable[/green]")
            console.print("[green]✓ Advanced features are working correctly[/green]")
            console.print("[green]✓ Performance is acceptable[/green]")
        elif summary['success_rate'] >= 70:
            console.print("[yellow]⚠ Good progress with some issues to address.[/yellow]")
            console.print("[yellow]• Review failed test cases[/yellow]")
            console.print("[yellow]• Fix any integration issues[/yellow]")
            console.print("[yellow]• Consider additional testing before production[/yellow]")
        else:
            console.print("[red]❌ Significant issues detected. Not ready for production.[/red]")
            console.print("[red]• Critical test failures need immediate attention[/red]")
            console.print("[red]• Review error messages and fix underlying issues[/red]")
            console.print("[red]• Re-run tests after fixes[/red]")
        
        # Specific recommendations based on failures
        if summary['failed_tests'] > 0:
            console.print("\n[bold red]Failed Test Analysis:[/bold red]")
            failed_categories = set()
            for result in self.test_results.values():
                if result['status'] == 'failed':
                    failed_categories.add(result.get('category', 'unknown'))
            
            for category in failed_categories:
                console.print(f"[red]• {category.title()} tests failing - check module dependencies and implementation[/red]")
        
        if summary['skipped_tests'] > 0:
            console.print("\n[bold yellow]Skipped Test Analysis:[/bold yellow]")
            console.print("[yellow]• Review skipped tests - may indicate missing dependencies or files[/yellow]")
        
        # Performance insights
        if summary['total_execution_time'] > 60:
            console.print("\n[bold yellow]Performance Note:[/bold yellow]")
            console.print(f"[yellow]• Total test execution time: {summary['total_execution_time']:.1f}s[/yellow]")
            console.print("[yellow]• Consider optimizing slower test suites[/yellow]")
        
        console.print("\n" + "="*80)
        
        return summary['success_rate']
    
    def save_test_report(self, filename: str = None):
        """Save test results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"
        
        report_data = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'cli_version': '2.0',
                'python_version': sys.version,
                'start_time': self.start_time.isoformat() if self.start_time else None,
                'end_time': self.end_time.isoformat() if self.end_time else None
            },
            'summary': self.generate_test_summary(),
            'detailed_results': self.test_results
        }
        
        report_path = project_root / filename
        try:
            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)
            console.print(f"\n[green]Test report saved to: {report_path}[/green]")
        except Exception as e:
            console.print(f"\n[red]Failed to save test report: {str(e)}[/red]")
    
    async def run_all_tests(self):
        """Run all test suites"""
        console.print("[bold green] Purview CLI v1.0.0 - Comprehensive Test Execution[/bold green]")
        console.print("="*80)
        
        self.start_time = datetime.now()
        
        # Pre-flight checks
        console.print("[bold blue]Pre-flight Checks[/bold blue]")
        dependencies = self.check_dependencies()
        structure = self.check_project_structure()
        
        missing_deps = [dep for dep, available in dependencies.items() if not available]
        missing_structure = [path for path, exists in structure.items() if not exists]
        
        if missing_deps:
            console.print(f"\n[yellow]Warning: Missing dependencies: {', '.join(missing_deps)}[/yellow]")
            console.print("[yellow]Some tests may fail due to missing dependencies[/yellow]")
        
        if missing_structure:
            console.print(f"\n[yellow]Warning: Missing project structure: {', '.join(missing_structure)}[/yellow]")
            console.print("[yellow]Some tests may be skipped[/yellow]")
        
        # Run test suites
        console.print("\n[bold blue]Executing Test Suites[/bold blue]")
        
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Running tests...", total=len(self.test_suites))
            
            for test_suite in self.test_suites:
                # Determine if test should be run async
                if test_suite['category'] in ['integration', 'performance']:
                    result = await self.run_async_test_suite(test_suite)
                else:
                    result = self.run_test_suite(test_suite)
                
                self.test_results[test_suite['name']] = result
                progress.advance(task)
        
        self.end_time = datetime.now()
        
        # Generate comprehensive report
        success_rate = self.generate_detailed_report()
        
        # Save detailed report
        self.save_test_report()
        
        return success_rate >= 70


async def main():
    """Main test runner execution"""
    runner = ComprehensiveTestRunner()
    
    try:
        success = await runner.run_all_tests()
        
        if success:
            console.print("\n[bold green]🎉 Test execution completed successfully![/bold green]")
            return 0
        else:
            console.print("\n[bold red]❌ Test execution completed with failures[/bold red]")
            return 1
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Test execution interrupted by user[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Test execution failed: {str(e)}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
