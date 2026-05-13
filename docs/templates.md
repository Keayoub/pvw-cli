# Templates & Downloads

Use these ready-made templates to speed up bulk operations in Microsoft Purview with `pvw-cli`.
Each file matches the exact column format expected by the corresponding CLI import command, so you can start from a
known-good structure, fill in your data, and avoid format errors on first import.

!!! tip "Quick workflow"
    Download a template → fill in your data → run the matching `pvw` import command → validate with `--dry-run` before committing.

---

## CSV Templates

### Unified Catalog Terms

| Template | Purpose | Download | Key Columns |
|---|---|---|---|
| `uc_terms_bulk_example.csv` | Import UC terms in bulk (8 sample rows) | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/uc_terms_bulk_example.csv) | `name`, `description`, `status`, `acronym`, `owner_id`, `resource_name`, `resource_url` |
| `uc_terms_all_fields_example.csv` | UC term import with all optional fields populated | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/uc_terms_all_fields_example.csv) | `name`, `description`, `status`, `acronym`, `owner_id`, `resource_name`, `resource_url` |
| `uc_terms_bulk_update_example.csv` | Bulk update attributes of existing UC terms | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/uc_terms_bulk_update_example.csv) | `term_id`, `name`, `description`, `status` |
| `uc_terms_multivalue_example.csv` | Terms with multi-value fields (synonyms, contacts) | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/uc_terms_multivalue_example.csv) | `name`, `status`, `synonyms`, `contacts` |

**Import command:**
```bash
# Dry run first — validates format without making changes
pvw uc term import-csv --csv-file samples/csv/uc_terms_bulk_example.csv --domain-id "your-domain-guid" --dry-run

# Live import
pvw uc term import-csv --csv-file samples/csv/uc_terms_bulk_example.csv --domain-id "your-domain-guid"
```

!!! note "owner_id field"
    The `owner_id` column requires an **Entra ID Object ID (GUID)**, not an email address.
    Retrieve it with: `az ad user show --id user@company.com --query id -o tsv`

---

### Lineage

| Template | Purpose | Download | Key Columns |
|---|---|---|---|
| `lineage_example.csv` | Table-level lineage import | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/lineage_example.csv) | `source_entity_guid`, `target_entity_guid`, `relationship_type`, `process_name`, `description`, `confidence_score`, `owner`, `metadata` |
| `lineage_example_with_columns.csv` | Column-level lineage import | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/lineage_example_with_columns.csv) | `source_entity_guid`, `target_entity_guid`, `source_column`, `target_column`, `process_name` |
| `basic_lineage_sample.csv` | Minimal lineage starter — two entities and a process | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/basic_lineage_sample.csv) | `source_entity_guid`, `target_entity_guid`, `process_name` |
| `column_lineage_sample.csv` | Sample for column-level tracking | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/column_lineage_sample.csv) | `source_entity_guid`, `target_entity_guid`, `source_column`, `target_column` |

**Import command:**
```bash
pvw lineage validate lineage_example.csv
pvw lineage import lineage_example.csv
```

---

### Entities

| Template | Purpose | Download | Key Columns |
|---|---|---|---|
| `entity_bulk_update_example.csv` | Bulk update entity attributes | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/entity_bulk_update_example.csv) | `typeName`, `qualifiedName`, `displayName`, `description`, `owner`, `source`, `collection` |
| `dataset_import_sample.csv` | Dataset entity onboarding | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/dataset_import_sample.csv) | `name`, `description`, `owner_email`, `source_system`, `tags`, `location`, `format` |
| `bulk_create_with_classifications.csv` | Create entities with classifications | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/bulk_create_with_classifications.csv) | `name`, `typeName`, `qualifiedName`, `classifications` |
| `table_import_sample.csv` | Table-type entity import | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/table_import_sample.csv) | `name`, `typeName`, `qualifiedName`, `description` |

**Import command:**
```bash
pvw entity bulk-import --csv-file entity_bulk_update_example.csv
```

---

### Classic Glossary

| Template | Purpose | Download | Key Columns |
|---|---|---|---|
| `glossary_terms_sample.csv` | Classic glossary term import | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/glossary_terms_sample.csv) | `name`, `glossary_guid`, `description`, `short_description`, `status`, `definition`, `examples` |
| `term_assignments_sample.csv` | Assign glossary terms to entities | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/term_assignments_sample.csv) | `term_guid`, `entity_guid` |

---

## JSON Templates

### Terms & Glossary

| Template | Purpose | Download |
|---|---|---|
| `term/uc_terms_bulk_example.json` | UC term bulk import (JSON format) | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/term/uc_terms_bulk_example.json) |
| `term/uc_terms_bulk_update_example.json` | Bulk update UC terms (JSON format) | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/term/uc_terms_bulk_update_example.json) |
| `glossary/term.json` | Single classic glossary term payload | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/glossary/term.json) |
| `glossary/terms.json` | Multiple classic glossary terms | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/glossary/terms.json) |

### Entities

| Template | Purpose | Download |
|---|---|---|
| `entity/entity.json` | Single entity create/update payload | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/entity/entity.json) |
| `entity/entities.json` | Bulk entity payload | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/entity/entities.json) |
| `entity/column_entities.json` | Column-type entities | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/entity/column_entities.json) |

### Scan Configuration

| Template | Purpose | Download |
|---|---|---|
| `scan/scan_source.json` | Register a data source for scanning | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/scan/scan_source.json) |
| `scan/scan.json` | Scan definition payload | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/scan/scan.json) |
| `scan/scan_trigger.json` | Scheduled scan trigger | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/scan/scan_trigger.json) |
| `scan/classification_rule.json` | Custom classification rule | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/scan/classification_rule.json) |

### Relationships

| Template | Purpose | Download |
|---|---|---|
| `relationship/create.json` | Create a relationship between two entities | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/relationship/create.json) |
| `relationship/update.json` | Update an existing relationship | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/relationship/update.json) |

### Business Metadata

These templates define business metadata attribute sets for different governance domains:

| Template | Purpose | Download |
|---|---|---|
| `business_metadata/business_metadata_universal.json` | Universal business metadata (applies to any asset type) | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/business_metadata/business_metadata_universal.json) |
| `business_metadata/business_metadata_governance.json` | Governance-focused metadata attributes | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/business_metadata/business_metadata_governance.json) |
| `business_metadata/business_metadata_privacy.json` | Privacy and classification metadata | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/business_metadata/business_metadata_privacy.json) |
| `business_metadata/business_metadata_quality.json` | Data quality attributes | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/business_metadata/business_metadata_quality.json) |
| `business_metadata/business_metadata_dataproduct.json` | Data product metadata | [Download](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/business_metadata/business_metadata_dataproduct.json) |

**Usage:**
```bash
# Create business metadata type definition from template
pvw types createTypeDefs --payload-file samples/json/business_metadata/business_metadata_governance.json

# Apply business metadata to an entity
pvw entity add-business-metadata \
  --guid "entity-guid" \
  --bm-name "Governance" \
  --attr-name "DataOwner" \
  --attr-value "data-team"
```

---

## PowerShell Scripts

These scripts combine multiple CLI calls into complete workflows. Download and customise for your environment.

| Script | Purpose | Download |
|---|---|---|
| `Complete-Sync-Example.ps1` | Full end-to-end UC → Classic Glossary sync with logging | [Download](https://github.com/Keayoub/pvw-cli/blob/main/samples/powershell/Complete-Sync-Example.ps1) |
| `Sync-UCToClassicGlossary.ps1` | Sync Unified Catalog terms to Classic Glossary | [Download](https://github.com/Keayoub/pvw-cli/blob/main/samples/powershell/Sync-UCToClassicGlossary.ps1) |
| `create_lineage_interactive.ps1` | Interactive lineage creation with guided prompts | [Download](https://github.com/Keayoub/pvw-cli/blob/main/samples/powershell/create_lineage_interactive.ps1) |
| `create_business_metadata.ps1` | Create and apply business metadata in batch | [Download](https://github.com/Keayoub/pvw-cli/blob/main/samples/powershell/create_business_metadata.ps1) |
| `delete-all-uc-terms.ps1` | Remove all UC terms from a domain (use carefully) | [Download](https://github.com/Keayoub/pvw-cli/blob/main/samples/powershell/delete-all-uc-terms.ps1) |
| `Remove-PurviewAsset-Batch.ps1` | Batch-delete Purview assets by filter | [Download](https://github.com/Keayoub/pvw-cli/blob/main/samples/powershell/Remove-PurviewAsset-Batch.ps1) |
| `List-AllPurviewCollections.ps1` | List the full collections hierarchy | [Download](https://github.com/Keayoub/pvw-cli/blob/main/samples/powershell/List-AllPurviewCollections.ps1) |

---

## Usage Examples

### Example 1 — Import UC terms from a CSV template

```bash
# 1. Download the template
curl -L "https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/uc_terms_bulk_example.csv" -o terms_template.csv

# 2. Edit the CSV with your data (name, description, status, owner_id...)
# 3. Dry-run to validate
pvw uc term import-csv --csv-file terms_template.csv --domain-id $DOMAIN_ID --dry-run

# 4. Run the live import
pvw uc term import-csv --csv-file terms_template.csv --domain-id $DOMAIN_ID
```

### Example 2 — Import lineage from a CSV template

```bash
# 1. Get GUIDs for your source and target entities
pvw search query --keywords "sales table" --output json | jq '.[].id'

# 2. Download template and fill in the GUIDs
curl -L "https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/lineage_example.csv" -o lineage.csv

# 3. Validate
pvw lineage validate lineage.csv

# 4. Import
pvw lineage import lineage.csv
```

### Example 3 — Bulk update entities from a CSV template

```bash
# 1. Download and populate the entity update template
curl -L "https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/entity_bulk_update_example.csv" -o entity_update.csv

# 2. Import
pvw entity bulk-import --csv-file entity_update.csv
```

### Example 4 — Register a data source using a JSON template

```bash
# 1. Download the scan source template
curl -L "https://github.com/Keayoub/pvw-cli/raw/main/samples/json/scan/scan_source.json" -o scan_source.json

# 2. Edit: set name, kind (e.g., AzureSqlDatabase), scanResults endpoint
# 3. Register
pvw scan putDataSource --data-source-name "my-sql-db" --payload-file scan_source.json
```

### Example 5 — Apply business metadata using a JSON template (PowerShell)

```powershell
# Download and customise the universal template
$bm = Invoke-RestMethod "https://github.com/Keayoub/pvw-cli/raw/main/samples/json/business_metadata/business_metadata_universal.json"

# Create the type definition
pvw types createTypeDefs --payload-file business_metadata_universal.json

# Apply to an entity
pvw entity add-business-metadata `
  --guid "4fae348b-e960-42f7-834c-38f6f6f60000" `
  --bm-name "Universal" `
  --attr-name "DataSteward" `
  --attr-value "governance-team"
```

---

## Related Pages

- [Getting Started](getting-started.md) — install and authenticate
- [Entity Bulk CSV Guide](entity-bulk-csv-guide.md) — detailed entity CSV format reference
- [Term Bulk Import Guide](commands/unified-catalog/term-bulk-import.md) — UC term import deep-dive
- [Lineage commands](commands/lineage/main.md) — full lineage command reference
- [Samples Catalog](samples-catalog.md) — complete index of all sample files
