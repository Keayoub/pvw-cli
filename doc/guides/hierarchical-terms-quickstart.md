# Quick Start: Hierarchical Terms in Unified Catalog

## Overview

This guide shows you how to quickly create hierarchical term structures in Microsoft Purview Unified Catalog using the new `parent-id` feature.

## Prerequisites

```bash
# Install Purview CLI
pip install -upgrade pvw-cli

# Set your Purview account name
export PURVIEW_ACCOUNT_NAME="your-purview-account"

# Authentication is handled via Azure CLI or Service Principal
# Option 1: Azure CLI (interactive)
az login

# Option 2: Service Principal (for automation)
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

## 5-Minute Quick Start

### 1. Get Your Domain ID

```bash
# List all governance domains
pvw uc domain list

# Copy your domain GUID
export DOMAIN_ID="your-domain-guid-here"
```

### 2. Create a Root Term

```bash
# Create the parent term
pvw uc term create \
  --name "Data Quality" \
  --description "Root category for data quality metrics" \
  --domain-id "$DOMAIN_ID" \
  --status "Published"

# Save the returned ID
export ROOT_TERM_ID="returned-term-guid"
```

### 3. Create Child Terms

```bash
# Create first child
pvw uc term create \
  --name "Accuracy" \
  --description "Data accuracy metrics" \
  --domain-id "$DOMAIN_ID" \
  --parent-id "$ROOT_TERM_ID" \
  --status "Published"

# Create second child
pvw uc term create \
  --name "Completeness" \
  --description "Data completeness metrics" \
  --domain-id "$DOMAIN_ID" \
  --parent-id "$ROOT_TERM_ID" \
  --status "Published"
```

### 4. Verify Hierarchy

```bash
# List all terms in your domain
pvw uc term list --domain-id "$DOMAIN_ID"

# Check a specific term
pvw uc term show --term-id "$ROOT_TERM_ID"
```

## Real-World Example: Data Quality Taxonomy

```bash
#!/bin/bash
# create_dq_taxonomy.sh

DOMAIN_ID="your-domain-id"

# Step 1: Create root
echo "Creating root term..."
ROOT_RESPONSE=$(pvw uc term create \
  --name "Data Quality Framework" \
  --description "Comprehensive data quality taxonomy" \
  --domain-id "$DOMAIN_ID" \
  --status "Published" \
  --output json)

ROOT_ID=$(echo $ROOT_RESPONSE | jq -r '.id')
echo "✅ Root ID: $ROOT_ID"

# Step 2: Create dimensions
echo "Creating dimensions..."

ACCURACY_ID=$(pvw uc term create \
  --name "Accuracy" \
  --description "Correctness of data" \
  --domain-id "$DOMAIN_ID" \
  --parent-id "$ROOT_ID" \
  --status "Published" \
  --acronym "ACC" \
  --output json | jq -r '.id')
echo "✅ Accuracy ID: $ACCURACY_ID"

COMPLETENESS_ID=$(pvw uc term create \
  --name "Completeness" \
  --description "Presence of required data" \
  --domain-id "$DOMAIN_ID" \
  --parent-id "$ROOT_ID" \
  --status "Published" \
  --acronym "COMP" \
  --output json | jq -r '.id')
echo "✅ Completeness ID: $COMPLETENESS_ID"

# Step 3: Create metrics
echo "Creating specific metrics..."

pvw uc term create \
  --name "Field-Level Accuracy" \
  --description "Accuracy at field level" \
  --domain-id "$DOMAIN_ID" \
  --parent-id "$ACCURACY_ID" \
  --status "Draft"

pvw uc term create \
  --name "Record-Level Completeness" \
  --description "Completeness at record level" \
  --domain-id "$DOMAIN_ID" \
  --parent-id "$COMPLETENESS_ID" \
  --status "Draft"

echo "✅ Taxonomy created successfully!"
```

## Bulk Operations

### CSV Approach

Create `taxonomy.csv`:

```csv
term_id,name,description,parent_id,status
root-001,Data Quality,Root category,,Published
dim-001,Accuracy,Accuracy metrics,root-001,Published
dim-002,Completeness,Completeness metrics,root-001,Published
met-001,Field Accuracy,Field-level accuracy,dim-001,Draft
met-002,Record Completeness,Record-level completeness,dim-002,Draft
```

Execute:

```bash
# Preview changes
pvw uc term update-csv --csv-file taxonomy.csv --dry-run

# Apply changes
pvw uc term update-csv --csv-file taxonomy.csv
```

### JSON Approach

Create `taxonomy.json`:

```json
{
  "updates": [
    {
      "term_id": "root-guid",
      "name": "Data Quality",
      "status": "Published"
    },
    {
      "term_id": "child-1-guid",
      "name": "Accuracy",
      "parent_id": "root-guid",
      "status": "Published"
    },
    {
      "term_id": "child-2-guid",
      "name": "Completeness",
      "parent_id": "root-guid",
      "status": "Published"
    }
  ]
}
```

Execute:

```bash
# Preview
pvw uc term update-json --json-file taxonomy.json --dry-run

# Apply
pvw uc term update-json --json-file taxonomy.json
```

## Common Tasks

### Add Parent to Existing Term

```bash
pvw uc term update \
  --term-id "<existing-term-guid>" \
  --parent-id "<parent-term-guid>"
```

### Change Parent

```bash
pvw uc term update \
  --term-id "<child-term-guid>" \
  --parent-id "<new-parent-guid>"
```

### Remove Parent (Make Top-Level)

```bash
pvw uc term update \
  --term-id "<child-term-guid>" \
  --parent-id ""
```

### Update Multiple Terms

```bash
# Update term and set parent in one command
pvw uc term update \
  --term-id "<term-guid>" \
  --name "Updated Name" \
  --description "New description" \
  --parent-id "<parent-guid>" \
  --status "Published"
```

## PowerShell Version

```powershell
# Set variables
$domainId = "your-domain-id"

# Create root
$root = pvw uc term create `
  --name "Data Quality" `
  --description "Root category" `
  --domain-id $domainId `
  --status "Published" `
  --output json | ConvertFrom-Json

$rootId = $root.id

# Create child
pvw uc term create `
  --name "Accuracy" `
  --description "Accuracy metrics" `
  --domain-id $domainId `
  --parent-id $rootId `
  --status "Published"
```

## Python Version

```python
import subprocess
import json

domain_id = "your-domain-id"

# Create root
result = subprocess.run([
    "pvw", "uc", "term", "create",
    "--name", "Data Quality",
    "--description", "Root category",
    "--domain-id", domain_id,
    "--status", "Published",
    "--output", "json"
], capture_output=True, text=True)

root = json.loads(result.stdout)
root_id = root["id"]

# Create child
subprocess.run([
    "pvw", "uc", "term", "create",
    "--name", "Accuracy",
    "--description", "Accuracy metrics",
    "--domain-id", domain_id,
    "--parent-id", root_id,
    "--status", "Published"
])
```

## Troubleshooting

### "Parent term not found"
- Verify the parent GUID is correct
- Check that the parent term exists: `pvw uc term show --term-id <parent-guid>`

### "Domain mismatch"
- Ensure parent and child are in the same domain
- Use the same `--domain-id` for all terms

### CSV bulk update failing
- Run with `--dry-run` first to preview changes
- Check CSV format (no extra spaces, proper GUIDs)
- Verify all parent GUIDs exist

## Next Steps

- 📖 Read the [full documentation](../../doc/commands/unified-catalog/hierarchical-terms.md)
- 📓 Try the [Jupyter notebook](../notebooks%20(plus)/uc_hierarchical_terms.ipynb)
- 💻 Check [PowerShell examples](../powershell/uc_parent_id_examples.ps1)
- 📋 Review [sample CSV](../csv/uc_term_update_sample.csv) and [JSON](../json/uc_term_update_sample.json) files

## Support

For issues or questions:
- GitHub Issues: [pvw-cli repository](https://github.com/Keayoub/pvw-cli)
- Documentation: `doc/commands/unified-catalog/`
