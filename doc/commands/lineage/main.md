# Lineage CSV Operations

This document describes how to use the Purview CLI to perform lineage operations using CSV and JSON files, including batch processing, validation, and template/sample generation.

## Supported Commands

### CSV Batch Operations

- **Process lineage from CSV:**
  ```cmd
  pvw lineage csv process <csv_file> [--batch-size=<val>] [--validate-entities] [--create-missing-entities] [--progress]
  ```
  - Processes and creates lineage relationships in bulk from a CSV file.
  - Supports batch size, entity validation, and progress reporting.

- **Validate lineage CSV:**
  ```cmd
  pvw lineage csv validate <csv_file>
  ```
  - Validates the structure and content of a lineage CSV file against supported templates.

- **Generate sample lineage CSV:**
  ```cmd
  pvw lineage csv sample <output_file> [--num-samples=<val>] [--template=<val>]
  ```
  - Generates a sample CSV file for lineage operations.
  - Available templates: basic_lineage, etl_lineage, column_lineage

- **List available templates:**
  ```cmd
  pvw lineage csv templates
  ```
  - Lists available CSV templates for lineage operations.

### JSON Batch Operations

- **Process lineage from JSON:**
  - While the CLI is optimized for CSV, you can convert JSON to CSV or use the Python API for direct JSON ingestion.
  - See Python API example below.

## Python API Usage

You can use the Python API to process lineage from CSV or JSON files:

```python
from purviewcli.client.csv_operations import CSVBatchProcessor

processor = CSVBatchProcessor(purview_client)
# For CSV
await processor.process_csv_file('lineage.csv', 'create_lineage_relationships', template)
# For JSON
import pandas as pd
df = pd.read_json('lineage.json')
await processor._create_lineage_from_csv(df, template)
```

## Examples

- See [doc/integrated/examples/README.md](../../integrated/examples/README.md) for more usage examples.

## Best Practices

- Always validate your CSV file before processing: `pvw lineage csv validate <csv_file>`
- Use batch processing for large files.
- Refer to the [Complete CLI Reference](../../integrated/reference/complete-cli-reference.md#csv-operations) for all options and advanced usage.

---

_Last updated: 2025-06-11_
