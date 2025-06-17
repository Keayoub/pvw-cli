"""
Integration tests for data-product CLI commands using sample data.
"""
import subprocess
import sys
import os
import tempfile
import json
import pytest

CLI = [sys.executable, '-m', 'purviewcli']
SAMPLE_CSV = os.path.join(os.path.dirname(__file__), 'sample_data_product.csv')


def run_cli(args):
    result = subprocess.run(CLI + args, capture_output=True, text=True)
    return result

def test_data_product_import_dry_run():
    result = run_cli(['data-product', 'import', '--csv-file', SAMPLE_CSV, '--dry-run'])
    assert result.returncode == 0
    assert 'Dry run' in result.stdout or 'MOCK' in result.stdout

def test_data_product_create_show_delete():
    qualified_name = 'test-dp-cli'
    # Create
    result = run_cli(['data-product', 'create', '--qualified-name', qualified_name, '--name', 'Test DP', '--description', 'Test description'])
    assert result.returncode == 0
    assert 'SUCCESS' in result.stdout or 'Created' in result.stdout
    # Show
    result = run_cli(['data-product', 'show', '--qualified-name', qualified_name])
    assert result.returncode == 0
    # Delete
    result = run_cli(['data-product', 'delete', '--qualified-name', qualified_name])
    assert result.returncode == 0

if __name__ == '__main__':
    pytest.main([__file__])
