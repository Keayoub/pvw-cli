# Entity Bulk Update CSV - Quick Reference

## 🚀 Quick Start

```bash
# Preview changes (recommended first step)
pvw entity bulk-update-csv --csv-file updates.csv --dry-run

# Apply updates
pvw entity bulk-update-csv --csv-file updates.csv

# With error handling
pvw entity bulk-update-csv --csv-file updates.csv --error-csv failed.csv
```

## 📋 CSV Format Options

### Option 1: TypeName + QualifiedName (Create or Update)

```csv
typeName,qualifiedName,displayName,description,owner
DataSet,//storage/data.csv@account,My Data,Description,owner-name
```

### Option 2: GUID (Update Existing)

```csv
guid,displayName,description,owner
abc-123-def,Updated Name,Updated Description,new-owner
```

## 🔧 Common Commands

```bash
# Standard update
pvw entity bulk-update-csv --csv-file entities.csv

# Large batch processing
pvw entity bulk-update-csv --csv-file entities.csv --batch-size 200

# With error logging
pvw entity bulk-update-csv --csv-file entities.csv --error-csv errors.csv

# Dry run (preview only)
pvw entity bulk-update-csv --csv-file entities.csv --dry-run
```

## 📊 Common Entity Types

| Type | QualifiedName Format |
|------|---------------------|
| `DataSet` | `//storage/path@account` |
| `azure_sql_table` | `mssql://server/db/schema/table` |
| `azure_datalake_gen2_path` | `https://account.dfs.core.windows.net/container/path` |

## ⚙️ Options Reference

| Option | Description | Default |
|--------|-------------|---------|
| `--csv-file` | Path to CSV file | Required |
| `--batch-size` | Entities per API call | 100 |
| `--dry-run` | Preview without applying | False |
| `--error-csv` | Save failed rows to file | - |

## ✅ Best Practices

1. **Always dry-run first**: `--dry-run`
2. **Use error logging**: `--error-csv failed.csv`
3. **Optimize batch size**: 100-200 for most cases
4. **Validate qualifiedNames**: Check format before updating
5. **Test with small sample**: Start with 10-20 rows

## 📝 Complete Example

**File: `my_entities.csv`**
```csv
typeName,qualifiedName,displayName,description,owner,collection
DataSet,//storage/sales.csv@acct,Sales Data,2024 sales,sales-team,sales
DataSet,//storage/customers.csv@acct,Customers,Customer data,data-team,customers
```

**Commands:**
```bash
# 1. Preview
pvw entity bulk-update-csv --csv-file my_entities.csv --dry-run

# 2. Apply
pvw entity bulk-update-csv --csv-file my_entities.csv

# 3. Check errors (if any)
cat failed.csv
```

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Missing required columns | Add `typeName` and `qualifiedName` |
| Entity not found | Use create-or-update mode |
| Batch failures | Reduce `--batch-size` to 25-50 |
| Invalid qualifiedName | Check format for your entity type |

## 📚 Related Commands

```bash
# Create entities
pvw entity bulk-create-csv --csv-file new_entities.csv

# Export entities
pvw search query --query "*" > entities.json

# List entity types
pvw entity types
```

## 🎯 Sample Files

- [`entity_bulk_update_example.csv`](../../samples/csv/entity_bulk_update_example.csv)
- [`entity_guid_update_example.csv`](../../samples/csv/entity_guid_update_example.csv)
- [`entities_sample.csv`](../../samples/csv/entities_sample.csv)

## 📖 Full Documentation

[Complete Guide](./entity-bulk-update-csv.md)

---

**Quick Tip**: Always start with `--dry-run` to preview changes before applying!
