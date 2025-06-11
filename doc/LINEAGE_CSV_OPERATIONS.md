# Lineage CSV Operations Guide

This guide explains how to use CSV files to perform bulk lineage operations in Azure Purview using the PurviewCLI.

## Overview

The lineage CSV operations allow you to:
- Create lineage relationships in bulk from CSV files
- Update existing lineage relationships
- Perform bulk lineage creation for better performance
- Support various lineage scenarios (ETL, data pipelines, column mappings)

## Supported Operations

### 1. `create_lineage_relationships`
Creates individual lineage relationships from CSV data.

**Use case**: When you need detailed control over each relationship and want to handle errors individually.

**Example**:
```python
results = await processor.process_csv_file(
    csv_path='basic_lineage.csv',
    operation='create_lineage_relationships',
    template=LINEAGE_TEMPLATES['basic_lineage']
)
```

### 2. `update_lineage_relationships`
Updates existing lineage relationships from CSV data.

**Use case**: When you need to modify attributes of existing lineage relationships.

**Required columns**: Must include `relationship_guid` column.

**Example**:
```python
results = await processor.process_csv_file(
    csv_path='lineage_updates.csv',
    operation='update_lineage_relationships',
    template=LINEAGE_TEMPLATES['basic_lineage']
)
```

### 3. `bulk_create_lineage`
Creates lineage relationships in bulk with optimized performance.

**Use case**: When you have large datasets and want maximum performance.

**Features**:
- Groups relationships by process
- Creates process entities automatically
- Optimized for large-scale operations

**Example**:
```python
results = await processor.process_csv_file(
    csv_path='bulk_lineage.csv',
    operation='bulk_create_lineage',
    template=LINEAGE_TEMPLATES['etl_lineage']
)
```

## Available Templates

### 1. `basic_lineage`
Simple source-to-target lineage relationships.

**Required columns**:
- `source_entity_guid`
- `target_entity_guid`
- `relationship_type`

**Optional columns**:
- `process_name`
- `description`
- `confidence_score`
- `owner`
- `metadata`

**Sample CSV**:
```csv
source_entity_guid,target_entity_guid,relationship_type,process_name,description,confidence_score
source-guid-001,target-guid-001,DataFlow,ETL_Process_1,Data transformation,0.9
```

### 2. `etl_lineage`
ETL process lineage with transformation details.

**Required columns**:
- `source_entity_guid`
- `target_entity_guid`
- `process_name`

**Optional columns**:
- `transformation_type`
- `owner`
- `schedule`
- `metadata`

**Sample CSV**:
```csv
source_entity_guid,target_entity_guid,process_name,transformation_type,owner,schedule
source-table-001,target-table-001,Daily_ETL_Job_1,aggregation,data-team,daily
```

### 3. `column_lineage`
Column-level lineage mapping.

**Required columns**:
- `source_entity_guid`
- `target_entity_guid`
- `source_column`
- `target_column`

**Optional columns**:
- `transformation_logic`
- `confidence_score`

**Sample CSV**:
```csv
source_entity_guid,target_entity_guid,source_column,target_column,transformation_logic
source-table-001,target-table-001,customer_id,cust_id,DIRECT
```

### 4. `data_pipeline`
Data pipeline lineage with scheduling information.

**Required columns**:
- `source_entity_guid`
- `target_entity_guid`
- `pipeline_name`

**Optional columns**:
- `pipeline_type`
- `schedule`
- `owner`
- `status`
- `metadata`

### 5. `copy_activity`
Copy activity lineage with performance metrics.

**Required columns**:
- `source_entity_guid`
- `target_entity_guid`
- `copy_activity_name`

**Optional columns**:
- `copy_type`
- `rows_copied`
- `bytes_copied`
- `duration_seconds`

## Usage Examples

### Example 1: Basic Lineage Creation

```python
import asyncio
from purviewcli.client.csv_operations import CSVBatchProcessor, LINEAGE_TEMPLATES

async def create_basic_lineage():
    processor = CSVBatchProcessor(purview_client)
    
    results = await processor.process_csv_file(
        csv_path='samples/csv/basic_lineage_sample.csv',
        operation='create_lineage_relationships',
        template=LINEAGE_TEMPLATES['basic_lineage'],
        progress_callback=lambda msg: print(f"Progress: {msg}")
    )
    
    print(f"Created: {results['summary']['created']} relationships")
    print(f"Failed: {results['summary']['failed']} relationships")
    if results['errors']:
        for error in results['errors']:
            print(f"Error: {error}")

asyncio.run(create_basic_lineage())
```

### Example 2: Bulk ETL Lineage Creation

```python
async def create_etl_lineage():
    processor = CSVBatchProcessor(purview_client)
    
    results = await processor.process_csv_file(
        csv_path='samples/csv/etl_lineage_sample.csv',
        operation='bulk_create_lineage',
        template=LINEAGE_TEMPLATES['etl_lineage']
    )
    
    print(f"Bulk created: {results['summary']['created']} relationships")

asyncio.run(create_etl_lineage())
```

### Example 3: Column-Level Lineage

```python
async def create_column_lineage():
    processor = CSVBatchProcessor(purview_client)
    
    results = await processor.process_csv_file(
        csv_path='samples/csv/column_lineage_sample.csv',
        operation='create_lineage_relationships',
        template=LINEAGE_TEMPLATES['column_lineage']
    )
    
    print(f"Created column mappings: {results['summary']['created']}")

asyncio.run(create_column_lineage())
```

## CSV Validation

Before processing, you can validate your CSV files:

```python
from purviewcli.client.csv_operations import validate_lineage_csv

# Validate the CSV format
validation_result = validate_lineage_csv('lineage.csv', 'basic_lineage')

if validation_result['valid']:
    print("✓ CSV is valid")
else:
    print("✗ CSV has errors:")
    for error in validation_result['errors']:
        print(f"  - {error}")

if validation_result['warnings']:
    print("Warnings:")
    for warning in validation_result['warnings']:
        print(f"  - {warning}")
```

## Error Handling

The lineage operations provide comprehensive error handling:

```python
results = await processor.process_csv_file(...)

# Check results
print(f"Total rows: {results['summary']['total']}")
print(f"Successful: {results['summary']['created']}")
print(f"Failed: {results['summary']['failed']}")

# Handle errors
if results['errors']:
    print("Errors encountered:")
    for error in results['errors']:
        print(f"  - {error}")

# Process successful results
for success in results['success']:
    print(f"Created relationship: {success}")
```

## Best Practices

1. **Validate GUIDs**: Ensure all entity GUIDs exist in Purview before creating lineage.

2. **Use Bulk Operations**: For large datasets (>100 relationships), use `bulk_create_lineage`.

3. **Confidence Scores**: Use confidence scores (0.0-1.0) to indicate the reliability of lineage relationships.

4. **Metadata**: Include relevant metadata as JSON for better tracking and debugging.

5. **Progress Callbacks**: Use progress callbacks for long-running operations to monitor progress.

6. **Error Handling**: Always check the results for errors and handle them appropriately.

## Performance Considerations

- **Batch Size**: The default batch size is optimized for most scenarios
- **Bulk Operations**: Use `bulk_create_lineage` for >100 relationships
- **Parallel Processing**: Consider splitting large CSV files and processing them in parallel
- **Memory Usage**: Large CSV files are processed row-by-row to minimize memory usage

## Troubleshooting

### Common Issues

1. **Invalid GUIDs**: Ensure all entity GUIDs exist in your Purview account
2. **Missing Columns**: Check that all required columns are present in your CSV
3. **JSON Metadata**: Ensure metadata columns contain valid JSON
4. **Confidence Scores**: Values must be between 0.0 and 1.0
5. **Duplicate Relationships**: Some operations may fail if relationships already exist

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Existing Lineage

The CSV operations integrate seamlessly with existing Purview lineage:
- Relationships created via CSV appear in the Purview portal
- Can be combined with API-based lineage operations
- Supports all standard Purview lineage features

## Sample Files

Sample CSV files are provided in the `samples/csv/` directory:
- `basic_lineage_sample.csv` - Basic lineage relationships
- `etl_lineage_sample.csv` - ETL process lineage
- `column_lineage_sample.csv` - Column-level mappings
