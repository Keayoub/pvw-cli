# Bulk Update Terms Documentation

## Overview

The `update-csv` and `update-json` commands allow you to update multiple terms at once from CSV or JSON files. This is useful for:

- Updating term statuses in bulk (e.g., Draft → Published)
- Adding acronyms or owners to multiple terms
- Standardizing descriptions across terms
- Batch corrections and enhancements

## Commands

### update-csv

Update multiple terms from a CSV file.

```bash
pvw uc term update-csv --csv-file <path> [--dry-run]
```

**Options:**
- `--csv-file` (required): Path to CSV file with term updates
- `--dry-run`: Preview updates without applying them

### update-json

Update multiple terms from a JSON file.

```bash
pvw uc term update-json --json-file <path> [--dry-run]
```

**Options:**
- `--json-file` (required): Path to JSON file with term updates
- `--dry-run`: Preview updates without applying them

## CSV Format

### Required Column
- `term_id`: The GUID of the term to update (required)

### Optional Columns (Replace Operations)
- `name`: New term name (replaces existing)
- `description`: New description (replaces existing)
- `status`: New status (Draft, Published, Archived)
- `acronyms`: New acronyms separated by semicolons (replaces all existing)
- `owner_ids`: New owner IDs separated by semicolons (replaces all existing)

### Optional Columns (Add Operations)
- `add_acronyms`: Acronyms to add separated by semicolons (preserves existing)
- `add_owner_ids`: Owner IDs to add separated by semicolons (preserves existing)

### CSV Example

```csv
term_id,name,description,status,acronyms,owner_ids,add_acronyms,add_owner_ids
abc-123,Updated Name,New description,Published,,,API;REST,
def-456,,Only updating description,,,,,user@company.com
ghi-789,,,Draft,,,,
```

**Row 1:** Updates name, description, status, and adds acronyms API and REST
**Row 2:** Updates description only and adds an owner
**Row 3:** Changes status to Draft

## JSON Format

### Structure

```json
{
  "updates": [
    {
      "term_id": "term-guid",
      "name": "New Name",                    // Optional: Replace name
      "description": "New description",      // Optional: Replace description
      "status": "Published",                 // Optional: Change status
      "acronyms": ["API", "REST"],          // Optional: Replace all acronyms
      "owner_ids": ["user@company.com"],    // Optional: Replace all owners
      "add_acronyms": ["SQL"],              // Optional: Add acronyms (preserves existing)
      "add_owner_ids": ["user2@company.com"] // Optional: Add owners (preserves existing)
    }
  ]
}
```

### JSON Example

```json
{
  "updates": [
    {
      "term_id": "abc-123",
      "name": "Customer Acquisition Cost",
      "status": "Published",
      "add_acronyms": ["CAC"]
    },
    {
      "term_id": "def-456",
      "description": "Updated description with more details",
      "add_owner_ids": ["manager@company.com"]
    }
  ]
}
```

## Usage Examples

### Example 1: Dry Run (Preview Changes)

Always preview your updates before applying them:

```bash
# CSV dry run
pvw uc term update-csv --csv-file terms_updates.csv --dry-run

# JSON dry run
pvw uc term update-json --json-file terms_updates.json --dry-run
```

### Example 2: Publish All Draft Terms

Create a CSV with term IDs and status changes:

```csv
term_id,status
abc-123,Published
def-456,Published
ghi-789,Published
```

```bash
pvw uc term update-csv --csv-file publish_drafts.csv
```

### Example 3: Add Acronyms to Multiple Terms

```csv
term_id,add_acronyms
abc-123,API;REST
def-456,SQL;DB
ghi-789,KPI;OKR
```

```bash
pvw uc term update-csv --csv-file add_acronyms.csv
```

### Example 4: Update Descriptions Only

```json
{
  "updates": [
    {
      "term_id": "abc-123",
      "description": "Enhanced description with more context"
    },
    {
      "term_id": "def-456",
      "description": "Clarified definition based on team feedback"
    }
  ]
}
```

```bash
pvw uc term update-json --json-file update_descriptions.json
```

### Example 5: Add Owners to Terms

```csv
term_id,add_owner_ids
abc-123,datagovernance@company.com;compliance@company.com
def-456,finance@company.com
```

```bash
pvw uc term update-csv --csv-file add_owners.csv
```

### Example 6: Replace All Acronyms

To replace (not add) acronyms, use the `acronyms` column:

```csv
term_id,acronyms
abc-123,NEW;ACRONYM;ONLY
def-456,SINGLE
```

```bash
pvw uc term update-csv --csv-file replace_acronyms.csv
```

## PowerShell Integration

### Get Term IDs for Updates

```powershell
# Get all draft terms
$domainId = "your-domain-id"
$terms = py -m purviewcli uc term list --domain-id $domainId --output json | ConvertFrom-Json
$draftTerms = $terms | Where-Object { $_.status -eq "Draft" }

# Export term IDs to CSV for bulk update
$draftTerms | Select-Object @{Name='term_id';Expression={$_.id}}, @{Name='status';Expression={'Published'}} | 
    Export-Csv -Path "publish_drafts.csv" -NoTypeInformation
```

### Generate Update JSON from PowerShell

```powershell
$updates = @{
    updates = @(
        $draftTerms | ForEach-Object {
            @{
                term_id = $_.id
                status = "Published"
            }
        }
    )
}

$updates | ConvertTo-Json -Depth 10 | Set-Content "publish_drafts.json"
```

## Important Notes

### Replace vs Add Operations

**Replace Operations** (overwrites existing values):
- `name`, `description`, `status` - Always replace
- `acronyms` - Replaces all existing acronyms
- `owner_ids` - Replaces all existing owners

**Add Operations** (preserves existing values):
- `add_acronyms` - Adds to existing acronyms
- `add_owner_ids` - Adds to existing owners

### Best Practices

1. **Always use --dry-run first** to preview changes
2. **Back up term data** before bulk updates
3. **Start with small batches** (5-10 terms) to test
4. **Use add operations** when you want to preserve existing data
5. **Verify term IDs** are correct before updating
6. **Check status values** are valid: Draft, Published, Archived
7. **Rate limiting**: Updates are automatically rate-limited (200ms between requests)

### Error Handling

- Failed updates are reported with error messages
- Update continues even if individual terms fail
- Summary shows success/failure counts
- Failed terms are listed with error details

### Performance

- Sequential updates (no native bulk endpoint)
- ~1-2 seconds per term
- 50 terms ≈ 1-2 minutes
- 100 terms ≈ 2-4 minutes

## Common Workflows

### Workflow 1: Publish Review Cycle

```bash
# 1. List all draft terms
pvw uc term list --domain-id <domain-id> --output json > drafts.json

# 2. Review and create update file
# (manually or with script)

# 3. Dry run
pvw uc term update-json --json-file publish_terms.json --dry-run

# 4. Execute
pvw uc term update-json --json-file publish_terms.json
```

### Workflow 2: Add Missing Acronyms

```bash
# 1. Export terms without acronyms (PowerShell)
$terms = py -m purviewcli uc term list --domain-id $domainId --output json | ConvertFrom-Json
$noAcronyms = $terms | Where-Object { -not $_.acronyms -or $_.acronyms.Count -eq 0 }
$noAcronyms | Select-Object @{Name='term_id';Expression={$_.id}}, name | Export-Csv -Path "terms_need_acronyms.csv" -NoTypeInformation

# 2. Manually add acronyms column

# 3. Update
pvw uc term update-csv --csv-file terms_with_acronyms.csv
```

### Workflow 3: Data Quality Improvements

```bash
# 1. Export all terms
pvw uc term list --domain-id <domain-id> --output json > all_terms.json

# 2. Analyze and create improvement file
# (add missing descriptions, standardize acronyms, add owners)

# 3. Apply improvements
pvw uc term update-json --json-file improvements.json --dry-run
pvw uc term update-json --json-file improvements.json
```

## Sample Files

Sample files are available in the repository:

- `samples/csv/uc_terms_bulk_update_example.csv`
- `samples/json/term/uc_terms_bulk_update_example.json`

## Troubleshooting

### Issue: "Missing term_id"
**Solution:** Ensure every row has a valid term_id in the CSV/JSON

### Issue: "Term not found"
**Solution:** Verify the term_id exists using `pvw uc term show --term-id <id>`

### Issue: "Invalid status"
**Solution:** Use only: Draft, Published, or Archived

### Issue: "Owner not found"
**Solution:** Use Entra Object IDs (GUIDs), not email addresses

### Issue: Updates are slow
**Solution:** This is normal - updates are rate-limited to avoid API throttling

## See Also

- [Bulk Import Documentation](./term-bulk-import.md)
- [Term Create/Update Commands](./term.md)
- [PowerShell Examples Notebook](../../samples/notebooks (plus)/unified_catalog_powershell_examples.ipynb)
