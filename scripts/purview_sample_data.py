"""
Script to populate a new Microsoft Purview instance with sample data for demos and tests using only CSV files and CLI commands.
"""
import sys
import subprocess

def run_cli_command(command_args):
    """Run a CLI command and print output/errors."""
    try:
        result = subprocess.run(command_args, capture_output=True, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(command_args)}")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"Unexpected error running command: {' '.join(command_args)}")
        print(f"Error: {str(e)}")
        return False

def main():
    success_count = 0
    total_count = 5
    
    print("Importing sample collections from CSV via CLI...")
    csv_path = "samples/csv/sample_collections.csv"
    cmd = [sys.executable, '-m', 'purviewcli', 'collections', 'import-csv', '--csv-file', csv_path]
    if run_cli_command(cmd):
        success_count += 1

    print("\nImporting sample data products from CSV via CLI...")
    data_products_csv_path = "samples/csv/data-products.csv"
    cmd = [sys.executable, '-m', 'purviewcli', 'data-product', 'import', '--csv-file', data_products_csv_path]
    if run_cli_command(cmd):
        success_count += 1

    print("\nImporting sample entities from CSV via CLI...")
    entities_csv_path = "samples/csv/entities_sample.csv"
    cmd = [sys.executable, '-m', 'purviewcli', 'entity', 'bulk-create-csv', '--csv-file', entities_csv_path]
    if run_cli_command(cmd):
        success_count += 1

    print("\nImporting sample glossary terms from CSV via CLI...")
    glossary_csv_path = "samples/csv/glossary_terms_sample.csv"
    cmd = [sys.executable, '-m', 'purviewcli', 'glossary', 'import-terms-csv', '--csv-file', glossary_csv_path]
    if run_cli_command(cmd):
        success_count += 1

    print("\nImporting sample lineage from CSV via CLI...")
    lineage_csv_path = "samples/csv/sample_lineage.csv"
    cmd = [sys.executable, '-m', 'purviewcli', 'lineage', 'import', lineage_csv_path]
    if run_cli_command(cmd):
        success_count += 1

    print(f"\nSample data population complete.")
    print(f"Successfully imported {success_count}/{total_count} datasets.")

if __name__ == "__main__":
    main()
