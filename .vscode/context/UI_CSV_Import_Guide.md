# Purview UI CSV Import - Implementation Guide

## Overview

Your CLI now supports importing glossary terms directly from Microsoft Purview UI export CSV files! The implementation leverages the same API that the UI uses, making integration seamless.

## Key Discovery

**The Purview UI uses the same REST API endpoints as your CLI!**

- **Classic Glossary**: `POST /datamap/api/atlas/v2/glossary/{glossaryGuid}/terms/import`
- **API accepts**: CSV file upload via `multipart/form-data`
- **API handles**: Email-to-GUID conversion, hierarchy, relationships automatically

You don't need to do complex transformations - the API does the heavy lifting!

---

## Usage Examples

### Classic Glossary Terms

```bash
# Import UI export CSV for classic glossary
pvw glossary import-terms \
  --csv-file "Sample-2025_11_18-09_39_56.csv" \
  --glossary-guid "your-glossary-guid" \
  --ui-format

# With term hierarchy support
pvw glossary import-terms \
  --csv-file "Sample-2025_11_18-09_39_56.csv" \
  --glossary-guid "your-glossary-guid" \
  --ui-format \
  --include-term-hierarchy
```

**Supported UI Fields:**
- ✅ Name, Nick Name, Definition
- ✅ Status (Draft/Published/Archived)
- ✅ Acronym (comma-separated)
- ✅ Experts, Stewards (email:info format)
- ✅ Resources (name:url format)
- ✅ Parent Term Name (hierarchy)
- ✅ Related Terms, Synonyms
- ✅ Term Template Names
- ✅ IsDefinitionRichText

The API handles everything - emails are automatically resolved to Entra IDs!

### UC Domain Glossary Terms

```bash
# Import UI export CSV for UC terms
pvw uc term import-csv \
  --csv-file "HR-2025_11_18-09_38_57.csv" \
  --domain-id "your-domain-id" \
  --ui-format \
  --dry-run  # Preview first

# Actual import (remove --dry-run)
pvw uc term import-csv \
  --csv-file "HR-2025_11_18-09_38_57.csv" \
  --domain-id "your-domain-id" \
  --ui-format
```

**Supported UI Fields:**
- ✅ Name, Definition
- ✅ Status (Draft/Published/Archived)
- ✅ Acronym (comma-separated)
- ✅ Resources (name:url format)
- ⚠️ Experts/Stewards (must be Entra Object ID GUIDs)

**Unsupported (UC API limitations):**
- ❌ Parent Term hierarchy
- ❌ Related Terms
- ❌ Synonyms
- ❌ Term Templates

The CLI warns you about unsupported fields and ignores them gracefully.

---

## CSV Format Examples

### UI Export Format (Classic Glossary)

```csv
Nick Name,Name,Definition,IsDefinitionRichText,Status,Related Terms,Synonyms,Acronym,Experts,Stewards,Resources,Parent Term Name,Term Template Names
Sample,Sample,<div>Sample update from import</div>,TRUE,Draft,,,,,,,,System Default;
Employee,Employee,A person engaged by the organization,FALSE,Published,,,Person; Staff; Worker,user1@company.com:Expert,admin@company.com:Steward,HR Portal:https://hr.example.com,,System Default;
```

### UI Export Format (UC Domain Glossary)

```csv
Nick Name,Name,Definition,IsDefinitionRichText,Status,Related Terms,Synonyms,Acronym,Experts,Stewards,Resources,Parent Term Name,Term Template Names
CRM,Customer Relationship Management,Software for managing customer interactions,,Draft,,,CRM,,,,,"System Default;"
PII,Personally Identifiable Information,Data that can identify an individual,,Draft,,,PII,,,,,"System Default;"
```

### Legacy CLI Format (Still Supported)

```csv
name,description,status,acronyms,owner_ids,resource_name,resource_url
Customer Acquisition Cost,The cost associated with acquiring a new customer,Draft,CAC,0360aff3-add5-4b7c-b172-52add69b0199,Marketing Metrics Guide,https://docs.example.com/marketing/cac
```

---

## Implementation Details

### What Changed

#### 1. **glossary.py** - Classic Glossary Import
- Added `--ui-format` flag
- When enabled: uploads CSV file directly via `multipart/form-data`
- No conversion needed - API handles everything!

#### 2. **unified_catalog.py** - UC Terms Import
- Added `--ui-format` flag
- Parses UI CSV and maps to UC API format
- Handles field name differences (Name → name, Definition → description)
- Warns about unsupported fields
- Validates owner IDs (GUIDs vs emails)

#### 3. **_glossary.py** - Client Updates
- Added CSV file upload support (`self.files`)
- Detects `--csvFile` parameter
- Sets up `multipart/form-data` request

#### 4. **endpoint.py** & **sync_client.py** - File Upload Support
- Added `files` parameter to `make_request()`
- Handles `multipart/form-data` content type
- Preserves file handles for upload

### Technical Flow

```
User runs command with --ui-format
        ↓
CLI checks if classic glossary or UC
        ↓
Classic Glossary Path:
  → Upload CSV file directly to API
  → API handles parsing, validation, import
        ↓
UC Terms Path:
  → Parse UI CSV format
  → Map fields to UC API format
  → Warn about unsupported fields
  → Create terms via UC API (one by one)
```

---

## Important Notes

### Classic Glossary
- ✅ **Full compatibility** - all UI fields supported
- ✅ API resolves email addresses automatically
- ✅ Supports hierarchy, relationships, templates
- ⚠️ Requires valid glossary GUID

### UC Domain Glossary
- ⚠️ **Partial compatibility** - UC API has limitations
- ❌ Emails in Experts/Stewards will fail - must use Entra Object IDs (GUIDs)
- ❌ Hierarchy, related terms, templates not supported
- ✅ Name, description, status, acronyms, resources work perfectly

### Owner IDs (GUIDs)

UC API requires **Entra Object IDs** (GUIDs like `0360aff3-add5-4b7c-b172-52add69b0199`), not email addresses.

**To get GUIDs:**
```bash
# Using Azure CLI
az ad user show --id user@company.com --query id -o tsv

# Using Microsoft Graph API
GET https://graph.microsoft.com/v1.0/users/user@company.com
```

**Workaround for bulk conversion:**
You could create a helper script to convert emails to GUIDs before import.

---

## Migration Workflow

### From UI Export to CLI Import

1. **Export from Purview UI**
   - Navigate to Glossary/Domain
   - Select terms to export
   - Download CSV file

2. **Review CSV file**
   - Check for instruction rows (remove if needed)
   - For UC: Verify owner IDs are GUIDs, not emails

3. **Test with dry-run**
   ```bash
   pvw uc term import-csv \
     --csv-file "export.csv" \
     --domain-id "your-domain" \
     --ui-format \
     --dry-run
   ```

4. **Review warnings**
   - Note any unsupported fields
   - Check for email addresses in owner fields

5. **Import**
   ```bash
   # Remove --dry-run flag
   pvw uc term import-csv \
     --csv-file "export.csv" \
     --domain-id "your-domain" \
     --ui-format
   ```

6. **Verify in UI**
   - Check created terms in Purview portal
   - Verify attributes, owners, resources

---

## Backward Compatibility

**Legacy CLI format still works!**

```bash
# Old format (no --ui-format flag)
pvw glossary import-terms \
  --csv-file "legacy_format.csv" \
  --glossary-guid "guid"

pvw uc term import-csv \
  --csv-file "legacy_format.csv" \
  --domain-id "domain-id"
```

The CLI auto-detects format based on column names.

---

## Error Handling

### Common Errors

**Error: "Email addresses not supported"** (UC only)
- Solution: Use Entra Object IDs (GUIDs) instead of emails

**Error: "Parent term not found"** (Classic)
- Solution: Ensure `--include-term-hierarchy` flag is set
- Or create parent terms first

**Error: "Invalid GUID format"**
- Solution: Verify glossary GUID or domain ID is correct

**Error: "No valid terms found"**
- Solution: Check CSV has data rows (not just headers)
- Remove instruction rows from UI export

---

## Performance

### Classic Glossary
- **Single API call** for entire CSV
- Fast bulk import
- API handles validation in batch

### UC Terms
- **One API call per term** (UC API limitation)
- Built-in rate limiting (200ms delay)
- Progress status with terminal output
- Error handling per term

---

## Testing

Test with your sample files:

```bash
# Classic glossary
pvw glossary import-terms \
  --csv-file "samples/csv/UI/Sample-2025_11_18-09_39_56.csv" \
  --glossary-guid "your-glossary-guid" \
  --ui-format

# UC terms (dry-run first!)
pvw uc term import-csv \
  --csv-file "samples/csv/UI/HR-2025_11_18-09_38_57.csv" \
  --domain-id "your-domain-id" \
  --ui-format \
  --dry-run
```

---

## Summary

✅ **Implemented:**
- Classic glossary UI CSV import (full support)
- UC domain glossary UI CSV import (with limitations noted)
- File upload support in HTTP client
- Field mapping and validation
- Backward compatibility with legacy format

✅ **Benefits:**
- Direct UI export → CLI import workflow
- No manual format conversion needed
- Clear warnings for unsupported fields
- Maintains existing CLI format support

✅ **Works Out of the Box:**
- Your attached files can be imported directly!
- `Sample-2025_11_18-09_39_56.csv` → Classic glossary
- `HR-2025_11_18-09_38_57.csv` → UC terms (with owner ID caveat)

---

**Ready to use!** Try importing your files now. 🚀
