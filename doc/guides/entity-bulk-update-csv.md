# Bulk Entity Updates from CSV - Complete Guide

## Overview

The Purview CLI provides powerful bulk update capabilities for entities using CSV files. You can update hundreds or thousands of entities efficiently using the `pvw entity bulk-update-csv` command.

## Command

```bash
pvw entity bulk-update-csv --csv-file <path-to-csv> [options]
```

### Options

| Option | Description | Default | Required |
|--------|-------------|---------|----------|
| `--csv-file` | Path to CSV file with entity updates | - | ✅ Yes |
| `--batch-size` | Number of entities to process per API call | 100 | ❌ No |
| `--dry-run` | Preview changes without applying them | False | ❌ No |
| `--error-csv` | Path to save failed rows | - | ❌ No |

## CSV Format

The CSV format supports two modes:

### Mode 1: Update by TypeName + QualifiedName (Create-or-Update)

This mode creates entities if they don't exist, or updates them if they do.

**Required Columns:**
- `typeName` - Entity type (e.g., `DataSet`, `azure_sql_table`, `azure_datalake_gen2_path`)
- `qualifiedName` - Unique identifier for the entity

**Optional Columns:**
- `displayName` - Display name
- `description` - Description
- `owner` - Owner name
- `source` - Data source
- `collection` - Collection name/path
- Any custom attributes supported by the entity type

**Example:**

```csv
typeName,qualifiedName,displayName,description,owner,source,collection
DataSet,//storage/sales.csv@account,Sales Data,Monthly sales data,data-team,ERP,sales-collection
DataSet,//storage/customers.csv@account,Customer Data,Customer master data,data-team,CRM,customer-collection
azure_sql_table,mssql://server/db/schema/table,Orders Table,Order transactions,dba-team,SQL,finance-collection
```

### Mode 2: Update by GUID (Partial Updates)

This mode updates existing entities by their GUID. More efficient for updating specific attributes.

**Required Column:**
- `guid` - Entity GUID

**Optional Columns:**
- Any attribute you want to update (only provided columns will be updated)

**Example:**

```csv
guid,displayName,description,owner
abc-123-def-456,Updated Sales Data,New description for sales,new-owner
def-456-ghi-789,Updated Customer Data,New description for customers,customer-owner
```

## Complete Examples

### Example 1: Create or Update Multiple DataSets

**File: `datasets_update.csv`**

```csv
typeName,qualifiedName,displayName,description,owner,source,collection
DataSet,//storage/data/sales_2024.csv@myaccount,Sales 2024,2024 sales data,sales-team,ERP,sales
DataSet,//storage/data/sales_2023.csv@myaccount,Sales 2023,2023 sales data,sales-team,ERP,sales
DataSet,//storage/data/customers.csv@myaccount,Customers,Customer master,data-team,CRM,customer
DataSet,//storage/data/products.csv@myaccount,Products,Product catalog,product-team,PIM,products
```

**Command:**

```bash
# Preview changes (dry run)
pvw entity bulk-update-csv --csv-file datasets_update.csv --dry-run

# Apply changes
pvw entity bulk-update-csv --csv-file datasets_update.csv

# Apply with error logging
pvw entity bulk-update-csv --csv-file datasets_update.csv --error-csv failed.csv
```

### Example 2: Update Azure SQL Tables

**File: `sql_tables_update.csv`**

```csv
typeName,qualifiedName,displayName,description,owner,createTime
azure_sql_table,mssql://server.database.windows.net/DB/dbo/Sales,Sales Table,Transaction sales data,dba-team,2024-01-01
azure_sql_table,mssql://server.database.windows.net/DB/dbo/Customers,Customer Table,Customer master data,dba-team,2024-01-01
azure_sql_table,mssql://server.database.windows.net/DB/dbo/Orders,Orders Table,Order details,dba-team,2024-01-01
```

**Command:**

```bash
pvw entity bulk-update-csv --csv-file sql_tables_update.csv --batch-size 50
```

### Example 3: Update Entities by GUID (Partial Updates)

**File: `guid_updates.csv`**

```csv
guid,displayName,description,owner
abc-123-def-456-ghi-789,Updated Sales Dataset,Corrected description,new-sales-owner
def-456-ghi-789-jkl-012,Updated Marketing Dataset,Updated marketing data description,marketing-lead
ghi-789-jkl-012-mno-345,Updated Finance Dataset,Q4 financial data,finance-manager
```

**Command:**

```bash
pvw entity bulk-update-csv --csv-file guid_updates.csv
```

### Example 4: Update Azure Data Lake Paths

**File: `adls_paths_update.csv`**

```csv
typeName,qualifiedName,displayName,description,owner,path
azure_datalake_gen2_path,https://account.dfs.core.windows.net/container/folder/sales/,Sales Folder,Contains sales data,data-eng,/folder/sales/
azure_datalake_gen2_path,https://account.dfs.core.windows.net/container/folder/customers/,Customer Folder,Contains customer data,data-eng,/folder/customers/
azure_datalake_gen2_path,https://account.dfs.core.windows.net/container/folder/products/,Product Folder,Contains product catalog,data-eng,/folder/products/
```

**Command:**

```bash
pvw entity bulk-update-csv --csv-file adls_paths_update.csv --batch-size 25
```

### Example 5: Bulk Update with Large Batches

For processing thousands of entities:

```bash
# Process 1000 entities with batch size of 200
pvw entity bulk-update-csv \
  --csv-file large_entity_update.csv \
  --batch-size 200 \
  --error-csv failed_entities.csv
```

## Best Practices

### 1. Always Use Dry Run First

```bash
# Preview changes
pvw entity bulk-update-csv --csv-file updates.csv --dry-run

# Review output, then apply
pvw entity bulk-update-csv --csv-file updates.csv
```

### 2. Use Appropriate Batch Sizes

| Scenario | Recommended Batch Size |
|----------|----------------------|
| Small updates (< 100 entities) | 50-100 |
| Medium updates (100-1000 entities) | 100-200 |
| Large updates (> 1000 entities) | 200-500 |
| Updates with large payloads | 25-50 |

### 3. Handle Errors with Error CSV

```bash
pvw entity bulk-update-csv \
  --csv-file updates.csv \
  --error-csv failed.csv

# Review failed.csv and retry
pvw entity bulk-update-csv --csv-file failed.csv
```

### 4. Validate QualifiedNames

```bash
# Export existing entities first to get proper qualifiedNames
pvw entity read-bulk --file existing_entities.json

# Extract and validate qualifiedNames before updating
```

### 5. Use Collections Properly

Ensure collections exist before assigning:

```bash
# List collections
pvw collections list

# Verify collection paths match your CSV
```

## Common Entity Types and Their QualifiedName Formats

| Entity Type | QualifiedName Format | Example |
|-------------|---------------------|---------|
| `DataSet` | `//storage/path@account` | `//storage/data/sales.csv@myaccount` |
| `azure_sql_table` | `mssql://server/db/schema/table` | `mssql://server.database.windows.net/DB/dbo/Sales` |
| `azure_sql_db` | `mssql://server/database` | `mssql://server.database.windows.net/SalesDB` |
| `azure_datalake_gen2_path` | `https://account.dfs.core.windows.net/container/path` | `https://storage.dfs.core.windows.net/data/sales/` |
| `azure_datalake_gen2_filesystem` | `https://account.dfs.core.windows.net/container` | `https://storage.dfs.core.windows.net/raw` |
| `azure_storage_account` | `https://account.blob.core.windows.net` | `https://mystorageaccount.blob.core.windows.net` |
| `Process` | Custom format | `spark://cluster/job/etl_sales` |

## Working with Custom Attributes

You can include custom attributes in your CSV:

```csv
typeName,qualifiedName,displayName,customAttribute1,customAttribute2
DataSet,//data/sales.csv@acct,Sales,value1,value2
```

The CLI will map these to the entity's attributes automatically.

## Advanced Scenarios

### Scenario 1: Update Thousands of Entities from Export

```bash
# Step 1: Export existing entities
pvw search query --query "*" --limit 5000 > entities_export.json

# Step 2: Convert to CSV (use script or tool)
python convert_json_to_csv.py entities_export.json entities.csv

# Step 3: Modify CSV as needed
# Edit entities.csv with your changes

# Step 4: Bulk update
pvw entity bulk-update-csv \
  --csv-file entities.csv \
  --batch-size 200 \
  --error-csv failed.csv
```

### Scenario 2: Incremental Updates

```bash
# Update only specific attributes for all entities
# CSV with guid + attributes to update
pvw entity bulk-update-csv --csv-file partial_updates.csv
```

### Scenario 3: Migration Scenario

```bash
# Migrate entity metadata from one account to another

# Source account
export PURVIEW_ACCOUNT_NAME=source-account
pvw entity read-bulk --file source_entities.json

# Convert and modify for target
# ... processing ...

# Target account
export PURVIEW_ACCOUNT_NAME=target-account
pvw entity bulk-update-csv --csv-file target_entities.csv
```

## Troubleshooting

### Issue: "CSV must contain at least 'typeName' and 'qualifiedName' columns"

**Solution:** Ensure your CSV has the required columns:
```csv
typeName,qualifiedName
DataSet,//storage/data.csv@account
```

### Issue: Entities not found during GUID updates

**Solution:** Use create-or-update mode with typeName + qualifiedName instead:
```csv
typeName,qualifiedName,displayName
DataSet,//storage/data.csv@account,My Dataset
```

### Issue: Batch failures

**Solution:** Reduce batch size and use error CSV:
```bash
pvw entity bulk-update-csv \
  --csv-file updates.csv \
  --batch-size 25 \
  --error-csv failed.csv
```

### Issue: Invalid qualifiedName format

**Solution:** Check the entity type documentation for proper format. Each type has specific requirements.

### Issue: Collection not found

**Solution:** Create the collection first or use existing collection paths:
```bash
pvw collections read --collection <collection-name>
```

## Performance Tips

1. **Optimize Batch Size**: Test different batch sizes to find optimal performance
2. **Use GUID Mode**: When possible, use GUID mode for faster partial updates
3. **Parallel Processing**: Split large CSV files and run multiple processes
4. **Off-Peak Hours**: Run large bulk operations during off-peak hours
5. **Monitor Progress**: Use `--error-csv` to track failures and retry

## PowerShell Example

```powershell
# Bulk update with retry logic
$csvFile = "entity_updates.csv"
$errorCsv = "failed.csv"
$maxRetries = 3

for ($i = 1; $i -le $maxRetries; $i++) {
    Write-Host "Attempt $i of $maxRetries"
    
    pvw entity bulk-update-csv `
        --csv-file $csvFile `
        --batch-size 100 `
        --error-csv $errorCsv
    
    if (Test-Path $errorCsv) {
        $failedCount = (Import-Csv $errorCsv).Count
        Write-Host "Failed: $failedCount entities"
        
        if ($failedCount -gt 0 -and $i -lt $maxRetries) {
            Write-Host "Retrying failed entities..."
            $csvFile = $errorCsv
        } else {
            break
        }
    } else {
        Write-Host "Success! All entities updated."
        break
    }
}
```

## Python Example

```python
import subprocess
import pandas as pd

# Prepare entity updates
df = pd.DataFrame({
    'typeName': ['DataSet', 'DataSet'],
    'qualifiedName': ['//data/sales.csv@acct', '//data/customers.csv@acct'],
    'displayName': ['Sales Data', 'Customer Data'],
    'description': ['Updated sales', 'Updated customers'],
    'owner': ['data-team', 'data-team']
})

# Save to CSV
csv_file = 'entity_updates.csv'
df.to_csv(csv_file, index=False)

# Execute bulk update
result = subprocess.run([
    'pvw', 'entity', 'bulk-update-csv',
    '--csv-file', csv_file,
    '--batch-size', '50',
    '--error-csv', 'failed.csv'
], capture_output=True, text=True)

print(result.stdout)

# Check for failures
if Path('failed.csv').exists():
    failed_df = pd.read_csv('failed.csv')
    print(f"Failed entities: {len(failed_df)}")
```

## Related Commands

| Command | Description |
|---------|-------------|
| `pvw entity bulk-create-csv` | Bulk create entities from CSV |
| `pvw entity bulk-create` | Bulk create from JSON |
| `pvw entity bulk-update` | Bulk update from JSON |
| `pvw entity read-bulk` | Export entities to JSON |
| `pvw search query` | Search and export entities |

## Sample CSV Files

Sample files are available in the `samples/csv/` directory:

- `entities_sample.csv` - Basic entity updates
- `table_import_sample.csv` - Table entities
- `dataset_import_sample.csv` - Dataset entities

## Additional Resources

- [Entity CLI Documentation](../commands/entity.md)
- [Entity Types Reference](../reference/entity-types.md)
- [Collection Management](../commands/collections.md)
- [Search and Export Guide](../guides/search-export.md)

## FAQ

**Q: Can I update entity classifications via CSV?**  
A: Yes, but use the `bulk-classify-csv` command instead.

**Q: What's the difference between bulk-create-csv and bulk-update-csv?**  
A: `bulk-create-csv` is optimized for new entities. `bulk-update-csv` handles both create and update operations.

**Q: Can I delete entities via CSV?**  
A: No, use the `delete` command or API for deletions.

**Q: How do I get entity GUIDs for GUID-mode updates?**  
A: Export entities first: `pvw search query --query "*" > entities.json`

**Q: Can I update relationships via CSV?**  
A: Not directly. Use the relationship API or lineage commands.

**Q: Is there a limit on CSV file size?**  
A: No hard limit, but split very large files (> 10,000 rows) for better performance.

---

**Last Updated**: October 14, 2025
