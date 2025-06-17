"""
Sample CLI integration tests for lineage and data-product commands.
These tests use subprocess to invoke the CLI as a user would.
"""
import subprocess
import os
import sys
import tempfile
import json
import pytest

CLI = [sys.executable, '-m', 'purviewcli']

def run_cli(args):
    result = subprocess.run(CLI + args, capture_output=True, text=True)
    return result

def test_lineage_sample_and_validate():
    with tempfile.TemporaryDirectory() as tmpdir:
        sample_csv = os.path.join(tmpdir, 'sample-lineage.csv')
        # Generate sample
        result = run_cli(['lineage', 'sample', '--template', 'basic', sample_csv])
        assert result.returncode == 0
        assert 'Sample lineage CSV generated' in result.stdout
        # Validate sample
        result = run_cli(['lineage', 'validate', sample_csv])
        assert result.returncode == 0
        assert 'Lineage validation passed' in result.stdout

def test_data_product_help():
    result = run_cli(['data-product', '--help'])
    assert result.returncode == 0
    assert 'Usage:' in result.stdout or 'data-product' in result.stdout

# Add more tests for data-product commands as needed, e.g. list, get, create, etc.
# def test_data_product_list():
#     result = run_cli(['data-product', 'list'])
#     assert result.returncode == 0
#     assert 'data-products' in result.stdout

if __name__ == '__main__':
    pytest.main([__file__])
