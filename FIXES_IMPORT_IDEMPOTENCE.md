# Fix: Idempotent Term Import & Custom Attributes

## Problem Description

**Issue 1: Duplicate Terms on Re-import**
- When running the same import twice with the same `term_id` column, a new duplicate term was created instead of updating the existing one
- Expected: 2nd import should UPDATE, not CREATE

**Issue 2: Custom Attributes Not Applied**
- Custom attributes were parsed from CSV but not reflected in the term
- Root cause: API limitation - custom attributes must be applied via UPDATE, not during CREATE (2-step process)

## Solution

### 1. Added `term_id` Column Support ✓

The CSV import now recognizes and uses the `term_id` column (or variations: `id`, `ID`, `Term ID`, `TermId`).

**CSV Example:**
```csv
term_id,name,description,status,owner_ids,customAttributes.Glossaire.Reference
#DEMO_01#NA#Client#,Client,Customer entity,Draft,uuid-owner,REF-001
#DEMO_02#NA#Product#,Product,Product catalog,Draft,uuid-owner,REF-002
```

### 2. Fixed Duplicate Prevention Logic ✓

New import logic with priority order:

1. **Primary**: If `term_id` is in CSV → fetch by ID → UPDATE if exists, else CREATE
2. **Secondary**: If `--update-existing` flag set → search by name → UPDATE if found, else CREATE
3. **Default**: CREATE new term

```python
# If term_id is provided in CSV, use it directly (most reliable)
if term.get("term_id"):
    term_id = term["term_id"]
    existing_term = client.get_term_by_id({"--term-id": [term_id]})
    if existing_term and not existing_term.get("error"):
        # UPDATE existing term
        result = client.update_term(args)
        operation = "Updated"
    else:
        # CREATE new term
        result = client.create_term(args)
        operation = "Created"
```

### 3. Custom Attributes Now Applied ✓

When `term_id` is provided (enabling idempotence), custom attributes are automatically applied via the UPDATE step:

```
Step 1: CREATE term with basic fields (name, description, status, owners, etc.)
Step 2: UPDATE term to add custom attributes (managedAttributes API)
Result: Term with all custom attributes populated
```

**Behavior per scenario:**

| Scenario | Behavior |
|----------|----------|
| CSV has `term_id` + custom attributes | CREATE + UPDATE (custom attributes applied) ✓ |
| CSV has no `term_id`, use `--update-existing` | CREATE + UPDATE (custom attributes applied) ✓ |
| CSV has no `term_id`, no flags | CREATE only (custom attributes NOT applied - API limitation) ⚠ |
| Re-import same CSV with `term_id` | UPDATE only - no duplicates ✓ |

### 4. Updated Documentation ✓

The `pvw uc term import-csv` command help now documents:
- The new `term_id` column support
- How idempotent updates work
- Custom attributes 2-step process
- Examples with and without `term_id`

## Usage Examples

### Example 1: Idempotent Import with Custom Attributes
```bash
# File: glossaire_terms.csv
# term_id,name,description,status,customAttributes.Glossaire.Reference
# #DEMO_01#NA#Client#,Client,Entité client,Draft,REF-001

pvw uc term import-csv \
  --csv-file glossaire_terms.csv \
  --domain-id 'bc785cdb-11c3-4227-ab44-f6ad44048623'

# 1st run: Creates 1 term
# 2nd run (same file): Updates 1 term (no duplicates!)
```

### Example 2: Update by Name (Fallback)
```bash
# File: terms.csv (without term_id)
# name,description,customAttributes.Classification
# Client,Customer entity,PII
# Product,Product catalog,PUBLIC

pvw uc term import-csv \
  --csv-file terms.csv \
  --domain-id 'bc785cdb-11c3-4227-ab44-f6ad44048623' \
  --update-existing

# Searches by name in domain, updates if found, creates if not
```

### Example 3: Dry Run
```bash
pvw uc term import-csv \
  --csv-file glossaire_terms.csv \
  --domain-id 'bc785cdb-11c3-4227-ab44-f6ad44048623' \
  --dry-run
```

## Technical Details

### Files Modified
- `purviewcli/cli/unified_catalog.py` - CSV import logic

### Key Changes
1. **Line ~1693**: Added `term_id` column parsing (supports 5 column name variations)
2. **Line ~1695**: Added `term_id` field to term dict
3. **Line ~1912-1935**: New idempotence logic with priority order
4. **Line ~1619-1660**: Updated command docstring with examples

### API Behind the Scenes
- **GET** `/datagovernance/catalog/terms/{termId}` - Lookup existing term
- **POST** `/datagovernance/catalog/terms` - Create new term
- **PUT** `/datagovernance/catalog/terms/{termId}` - Update term (including custom attributes via `managedAttributes`)

## Regression Notes

✓ Backward compatible - existing CSV files without `term_id` still work
✓ `--update-existing` flag still works for name-based dedup
✓ All other import features unchanged (synonyms, experts, parent terms, relationships, etc.)
⚠ Custom attributes require either `term_id` or `--update-existing` flag

## Testing Recommendations

```bash
# Test 1: Idempotent import
pvw uc term import-csv --csv-file test.csv --domain-id <id>  # Should create 3 terms
pvw uc term import-csv --csv-file test.csv --domain-id <id>  # Should update 3 terms, 0 new

# Test 2: Custom attributes applied
pvw uc term import-csv --csv-file test.csv --domain-id <id> --debug
# Check logs show: "Existing managed attributes: ...", "Merged managed attributes: ..."

# Test 3: Name-based fallback
pvw uc term import-csv --csv-file test.csv --domain-id <id> --update-existing --dry-run
```
