# pvw-cli — Microsoft Purview Command-Line Interface

[![Version](https://img.shields.io/badge/version-1.10.14-blue.svg)](https://github.com/Keayoub/pvw-cli/releases/tag/v1.10.14)
[![Status](https://img.shields.io/badge/status-stable-success.svg)](https://github.com/Keayoub/pvw-cli)

A Python CLI and library for automating Microsoft Purview. Covers the Data Map, Unified Catalog, Collections, Search, Lineage, Scan, and Management APIs.

---

## Install

```bash
pip install pvw-cli
```

For the latest development version:

```bash
git clone https://github.com/Keayoub/pvw-cli.git
cd pvw-cli
pip install -r requirements.txt
pip install -e .
```

---

## Configuration

Set these three environment variables before running any command:

| Variable | Description |
|---|---|
| `PURVIEW_ACCOUNT_NAME` | Your Purview account name (e.g. `mycompany-purview`) |
| `PURVIEW_ACCOUNT_ID` | Your Azure Tenant ID (used as the Purview account ID for UC APIs) |
| `PURVIEW_RESOURCE_GROUP` | The resource group containing your Purview account |

**PowerShell:**

```powershell
$env:PURVIEW_ACCOUNT_NAME = "your-purview-account"
$env:PURVIEW_ACCOUNT_ID   = "your-tenant-id-guid"
$env:PURVIEW_RESOURCE_GROUP = "your-resource-group"
```

**Bash / Linux / macOS:**

```bash
export PURVIEW_ACCOUNT_NAME=your-purview-account
export PURVIEW_ACCOUNT_ID=your-tenant-id-guid
export PURVIEW_RESOURCE_GROUP=your-resource-group
```

To find your Tenant ID:

```bash
az account show --query tenantId -o tsv
```

---

## Authentication

The CLI uses `DefaultAzureCredential` and tries methods in this order:

1. **Azure CLI** — run `az login` (easiest for local use)
2. **Service Principal** — set `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`
3. **Managed Identity** — works automatically on Azure VMs, App Service, etc.

**Legacy tenant note:** If you get `AADSTS500011: resource principal https://purview.azure.com not found`, your tenant uses the older service principal. Set:

```bash
export PURVIEW_AUTH_SCOPE=https://purview.azure.net/.default
```

Check which your tenant uses:

```bash
az ad sp show --id "73c2949e-da2d-457a-9607-fcc665198967" --query servicePrincipalNames -o json
```

---

## Command Groups

```
pvw account          Account management
pvw collections      Collections CRUD and permissions
pvw entity           Entity read, create, update, bulk operations
pvw glossary         Classic glossary terms
pvw lineage          Lineage creation and CSV import
pvw scan             Data source scanning
pvw search           Search and discovery
pvw types            Type definitions
pvw uc               Unified Catalog (domains, terms, data products, OKRs, CDEs)
pvw workflow         Approval workflows
pvw diagnostics      Cache stats and profile info
```

Run `pvw <command> --help` for full options on any command.

---

## Examples

### Search

```bash
# Search by keyword
pvw search query --keywords "customer" --limit 10

# Table output (default), JSON, or colored JSON
pvw search query --keywords "sales" --limit 5
pvw search query --keywords "sales" --limit 5 --output json
pvw search query --keywords "sales" --limit 5 --output jsonc

# Show GUIDs in output (useful for follow-up operations)
pvw search query --keywords "customer" --show-ids

# Autocomplete and suggestions
pvw search autocomplete --keywords "ord" --limit 5
pvw search suggest --keywords "prod" --limit 5
```

### Entity

```bash
# List all entities
pvw entity list --limit 25

# Filter by type
pvw entity list --type-name azure_sql_table --limit 10

# Read entity by GUID
pvw entity read --guid "4fae348b-e960-42f7-834c-38f6f6f60000"

# Update a single attribute
pvw entity update-attribute \
  --guid "4fae348b-e960-42f7-834c-38f6f6f60000" \
  --attribute description \
  --value "Customer address data - SalesLT schema"

# Add a classification
pvw entity add-classification \
  --guid "ea3412c3-7387-4bc1-9923-11f6f6f60000" \
  --classification "MICROSOFT.PERSONAL.EMAIL"

# Business metadata
pvw entity add-business-metadata \
  --guid "entity-guid" \
  --bm-name "Compliance" \
  --attr-name "DataOwner" \
  --attr-value "finance-team"
```

### Collections

```bash
# List collections and hierarchy
pvw collections list
pvw collections read-hierarchy --collection-name "Data Engineering"

# Create a collection
pvw collections create \
  --name "analytics" \
  --friendly-name "Analytics Team" \
  --description "Assets for the analytics team"

# View permissions
pvw collections read-permissions --collection-name "analytics"
```

### Unified Catalog (UC)

```bash
# Domains
pvw uc domain list
pvw uc domain create --name "Finance" --description "Financial data governance"
pvw uc domain get --domain-id "abc-123"

# Glossary terms
pvw uc term list --domain-id "abc-123"
pvw uc term list --domain-id "abc-123" --output json
pvw uc term create --name "Customer" --domain-id "abc-123" --description "A person who purchases products"
pvw uc term show --term-id "term-456"
pvw uc term update --term-id "term-456" --description "Updated definition"
pvw uc term delete --term-id "term-456" --confirm

# Bulk term import from CSV
pvw uc term import-csv --csv-file samples/csv/uc_terms_bulk_example.csv --domain-id "abc-123" --dry-run
pvw uc term import-csv --csv-file samples/csv/uc_terms_bulk_example.csv --domain-id "abc-123"

# Bulk term import from JSON
pvw uc term import-json --json-file samples/json/term/uc_terms_bulk_example.json --domain-id "abc-123"

# Sync UC terms to a classic glossary
pvw uc term sync-classic --domain-id "abc-123" --glossary-guid "gloss-guid"
pvw uc term sync-classic --domain-id "abc-123" --glossary-guid "gloss-guid" --update-existing
pvw uc term sync-classic --domain-id "abc-123" --glossary-guid "gloss-guid" --update-existing --delete-removed
pvw uc term sync-classic --domain-id "abc-123" --glossary-guid "gloss-guid" --update-existing --dry-run

# Data products
pvw uc dataproduct list --domain-id "abc-123"
pvw uc dataproduct create --name "Customer Analytics" --domain-id "abc-123" --type Analytical --status Draft
pvw uc dataproduct update --product-id "prod-789" --status Published --endorsed

# Link a data product to an entity
pvw uc dataproduct link-entity \
  --id "prod-789" \
  --entity-id "4fae348b-e960-42f7-834c-38f6f6f60000" \
  --type-name azure_sql_table

# Objectives (OKRs)
pvw uc objective list --domain-id "abc-123"
pvw uc objective create --definition "Improve data quality score to 95%" --domain-id "abc-123"

# Critical Data Elements (CDEs)
pvw uc cde list --domain-id "abc-123"
pvw uc cde create --name "Social Security Number" --data-type String --domain-id "abc-123"
pvw uc cde link-entity --id "cde-789" --entity-id "ea3412c3-7387-4bc1-9923-11f6f6f60000"

# Facets and analytics
pvw uc term facets --output table
pvw uc dataproduct facets --domain-id "abc-123" --output json
pvw uc cde facets --output table

# Governance health
pvw uc health query
pvw uc health query --severity High
pvw uc health summary
pvw uc health update --action-id "action-guid" --status InProgress
```

### Lineage

```bash
# Create column-level lineage
pvw lineage create-column \
  --process-name "ETL_Sales_Transform" \
  --source-table-guid "9ebbd583-4987-4d1b-b4f5-d8f6f6f60000" \
  --target-table-guids "c88126ba-5fb5-4d33-bbe2-5ff6f6f60000" \
  --column-mapping "ProductID:ProductID,Name:Name"

# Import from CSV
pvw lineage validate lineage_data.csv
pvw lineage import lineage_data.csv
pvw lineage sample output.csv --num-samples 10 --template detailed
```

Lineage CSV columns: `source_entity_guid`, `target_entity_guid`, `relationship_type`, `process_name`, `description`, `confidence_score`, `owner`, `metadata`

### Classic Glossary

```bash
pvw glossary list-terms --glossary-guid "your-glossary-guid"
pvw glossary create-term --payload-file term.json
```

### Workflows

```bash
pvw workflow list
pvw workflow get --workflow-id "workflow-123"
pvw workflow create --workflow-id "approval-1" --payload-file workflow-definition.json
pvw workflow execute --workflow-id "workflow-123"
pvw workflow executions --workflow-id "workflow-123"
```

### Diagnostics

```bash
pvw diagnostics cache-stats
pvw diagnostics profile-info
pvw diagnostics clear-cache
```

---

## Output Formats

Most list commands support `--output`:

| Format | Use case |
|---|---|
| `table` | Default — human-readable Rich table |
| `json` | Plain JSON for piping to PowerShell, bash, jq |
| `jsonc` | Colored JSON for viewing in terminal |

**PowerShell example:**

```powershell
$terms = pvw uc term list --domain-id $domainId --output json | ConvertFrom-Json
$terms | Where-Object { $_.status -eq "Draft" } | Export-Csv draft_terms.csv -NoTypeInformation
```

**Bash / jq example:**

```bash
pvw uc term list --domain-id $DOMAIN_ID --output json | jq '.[] | .name'
```

---

## Bulk Import CSV Format (Terms)

```csv
name,description,status,acronym,owner_id,resource_name,resource_url
Customer Acquisition Cost,Cost to acquire a new customer,Draft,CAC,<entra-object-id-guid>,Metrics Guide,https://docs.example.com
```

Notes:
- `owner_id` must be an Entra ID Object ID (GUID), not an email address
- Terms in unpublished domains must use `Draft` status
- Sample files: `samples/csv/uc_terms_bulk_example.csv`, `samples/json/term/uc_terms_bulk_example.json`

---

## Sample Files

| Path | Contents |
|---|---|
| `samples/csv/uc_terms_bulk_example.csv` | 8 sample UC terms for import |
| `samples/json/term/uc_terms_bulk_example.json` | 8 data management terms (JSON format) |
| `samples/csv/lineage_example.csv` | Sample lineage relationships |
| `samples/notebooks (basic)/` | Basic Purview CLI notebook examples |
| `samples/notebooks (plus)/` | Advanced examples including bulk import |

---

## Documentation

- [Full docs](doc/README.md)
- [Unified Catalog commands](doc/commands/unified-catalog.md)
- [Term bulk import guide](doc/commands/unified-catalog/term-bulk-import.md)
- [Performance optimization guide](doc/PERFORMANCE_OPTIMIZATION_GUIDE.md)
- [Release archive](releases/)

---

## Requirements

- Python 3.8+
- Microsoft Purview account
- Azure CLI (`az login`) or Service Principal credentials

---

## Support

- Issues: [GitHub Issues](https://github.com/Keayoub/pvw-cli/issues)
- Email: [keayoub@msn.com](mailto:keayoub@msn.com)

---

## License

See [LICENSE](LICENSE) for details.
