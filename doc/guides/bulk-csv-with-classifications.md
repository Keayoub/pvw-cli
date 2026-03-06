# Bulk CSV Operations with Classifications

## Overview

Both `bulk-create-csv` and `bulk-update-csv` commands now support inline classification assignment via the CSV file. This allows you to create/update entities and apply classifications in a single operation.

## Supported Columns

The commands detect the following classification columns:
- `classification` (preferred)
- `classificationName` (alternative)

**Multi-value support**: Separate multiple classifications with `;` or `,`

Example values:
- Single: `PII`
- Multiple: `PII;CONFIDENTIAL`
- Multiple (comma): `PII,CONFIDENTIAL,GDPR`

---

## Usage: bulk-create-csv

Creates entities and applies classifications during creation.

### CSV Format

```csv
typeName,qualifiedName,displayName,description,classification
azure_datalake_gen2_path,//storage/container/customers.parquet,Customer Data,Customer info,PII;CONFIDENTIAL
azure_datalake_gen2_path,//storage/container/orders.parquet,Orders,Sales orders,CONFIDENTIAL
azure_datalake_gen2_path,//storage/container/analytics.csv,Analytics,Public data,PUBLIC
```

### Command

```powershell
# Preview (dry-run)
pvw entity bulk-create-csv --csv-file data.csv --dry-run --debug

# Execute
pvw entity bulk-create-csv --csv-file data.csv --debug

# With error handling
pvw entity bulk-create-csv --csv-file data.csv --error-csv errors.csv --debug
```

### How it works

1. Reads CSV file with entity attributes + classifications
2. Creates entities via `entityCreateBulk` API
3. Classifications are included in the creation payload
4. All classifications are applied during entity creation

---

## Usage: bulk-update-csv

Updates entity attributes and applies classifications.

### CSV Format (GUID-based)

```csv
guid,description,classification
a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6,Updated column description,PII;CONFIDENTIAL
b2c3d4e5-f6a7-48b9-c0d1-e2f3a4b5c6d7,Updated table description,INTERNAL
```

### Command

```powershell
# Preview (dry-run)
pvw entity bulk-update-csv --csv-file updates.csv --dry-run --debug

# Execute
pvw entity bulk-update-csv --csv-file updates.csv --debug

# With error handling
pvw entity bulk-update-csv --csv-file updates.csv --error-csv errors.csv --debug
```

### How it works

1. Reads CSV file with GUIDs, attributes, and classifications
2. For each row:
   - First applies classifications (via `entityCreateClassifications`)
   - If classification fails, the row is skipped and logged
   - Then updates attributes (via `entityPartialUpdateAttribute`)
3. Failed rows are written to `--error-csv` if specified

---

## Debug Mode

Use `--debug` to see detailed processing:

```powershell
pvw entity bulk-create-csv --csv-file data.csv --dry-run --debug
```

Debug output shows:
- CSV columns detected (including classification columns)
- Classification parsing (multi-value handling)
- Payload structure sent to API
- API responses

Example debug output:
```
[DEBUG] CSV Structure:
  Columns: ['typeName', 'qualifiedName', 'displayName', 'description', 'classification']
  Classification columns: ['classification']

[DEBUG] First row data:
{'typeName': 'azure_datalake_gen2_path', ..., 'classification': 'PII;CONFIDENTIAL'}

[DEBUG] Added classifications = ['PII', 'CONFIDENTIAL']

[DEBUG] Batch 1 Payload:
{
  "entities": [
    {
      "typeName": "azure_datalake_gen2_path",
      "attributes": { ... },
      "classifications": [
        {"typeName": "PII"},
        {"typeName": "CONFIDENTIAL"}
      ]
    }
  ]
}
```

---

## Error Handling

### Classification Errors (bulk-update-csv)

If a classification fails to apply:
- The row is skipped (attributes are NOT updated)
- Error is logged
- Row is written to `--error-csv`

Example error:
```
[X] Error: GUID a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6 classifications: Classification 'INVALID' does not exist
```

### Invalid CSV Format

The CSV must contain:
- **bulk-create-csv**: `typeName` and `qualifiedName` columns
- **bulk-update-csv**: `guid` column

Classification column is optional.

---

## Examples

### Example 1: Create columns with classifications

```csv
typeName,qualifiedName,displayName,classification
azure_sql_db_column,sql://server/db/schema/table/ColumnName,Customer Email,PII;CONFIDENTIAL
azure_sql_db_column,sql://server/db/schema/table/OrderID,Order ID,INTERNAL
azure_sql_db_column,sql://server/db/schema/table/CreatedDate,Created Date,
```

Note: Empty classification value is ignored (no classifications applied).

### Example 2: Update descriptions and apply classifications

```csv
guid,description,classification
00144766-2df7-4e46-b8c9-7ef6f6f60001,Customer email column - contains PII,PII;CONFIDENTIAL;GDPR
00144766-2df7-4e46-b8c9-7ef6f6f60002,Order ID - internal reference,INTERNAL
00144766-2df7-4e46-b8c9-7ef6f6f60003,Public analytics data,PUBLIC
```

### Example 3: Combined with custom attributes

```csv
typeName,qualifiedName,displayName,classification,businessMetadata.department,customAttributes.owner
DataSet,//data/sales.csv,Sales Data,CONFIDENTIAL,Sales,sales-team@company.com
DataSet,//data/marketing.csv,Marketing Data,INTERNAL,Marketing,marketing-team@company.com
```

---

## Sample Files

Sample CSV files are available in `samples/csv/`:
- `bulk_create_with_classifications.csv` - Example for bulk-create-csv
- `bulk_update_with_classifications.csv` - Example for bulk-update-csv

---

## Related Commands

| Command | Description |
|---------|-------------|
| `pvw entity bulk-classify-csv` | Apply only classifications (no attribute updates) |
| `pvw entity add-schema-classification` | Apply classifications to table columns |
| `pvw entity read-schema-classifications` | View classifications on columns |

---

## Tips

1. **Use typeName not GUID**: Classification names (e.g., `PII`, `CONFIDENTIAL`) are the classification typeNames in Purview, not GUIDs.

2. **Multi-value separator**: Use `;` or `,` to separate multiple classifications. Spaces are trimmed.

3. **Classification must exist**: Ensure classifications are already defined in Purview before applying them.

4. **Test with dry-run**: Always use `--dry-run --debug` first to preview changes.

5. **Error CSV**: Use `--error-csv errors.csv` to capture failed rows for retry/investigation.

6. **Windows compatibility**: Output uses ASCII-compatible status tags (OK, FAILED, WARNING) instead of Unicode symbols.

---

Last updated: March 6, 2026
