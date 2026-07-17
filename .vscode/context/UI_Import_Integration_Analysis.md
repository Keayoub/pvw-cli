# Purview UI Import File Integration Analysis

## Overview
This document analyzes the compatibility between Purview UI export/import CSV files and the existing purviewcli import functionality.

## Date: November 18, 2025

---

## 1. File Format Comparison

### 1.1 Classic Glossary Terms

#### UI Export Format (Sample-2025_11_18-09_39_56.csv)
```csv
Nick Name,Name,Definition,IsDefinitionRichText,Status,Related Terms,Synonyms,Acronym,Experts,Stewards,Resources,Parent Term Name,Term Template Names
```

**Fields:**
- Nick Name
- Name (required)
- Definition
- IsDefinitionRichText (boolean flag)
- Status (Draft/Published/Archived)
- Related Terms (semicolon-separated)
- Synonyms (semicolon-separated)
- Acronym (comma-separated)
- Experts (email:info format, semicolon-separated)
- Stewards (email:info format, semicolon-separated)
- Resources (name:url format, semicolon-separated)
- Parent Term Name (hierarchical path with underscores)
- Term Template Names (semicolon-separated)

#### Existing CLI Format (import-terms-sample.csv)
```csv
Name,Nick Name,Status,Definition,Acronym,Resources,Related Terms,Synonyms,Stewards,Experts,Parent Term Name,IsDefinitionRichText,Term Template Names
```

**Fields:** Similar but different order and format

#### Current CLI Implementation
- **Command:** `pvw glossary import-terms`
- **Location:** `purviewcli/cli/glossary.py` (lines 465-530)
- **API:** Uses `glossaryImportTerms` method
- **Format:** Accepts CSV but converts to JSON internally
- **Supports:** Basic term attributes (name, definition, status, nickName, abbreviation)
- **Limitations:** 
  - Does not parse complex fields (experts, stewards, resources)
  - No parent term hierarchy support
  - No related terms/synonyms support

---

### 1.2 Unified Catalog (UC) Domain Glossary Terms

#### UI Export Format (HR-2025_11_18-09_38_57.csv)
```csv
Nick Name,Name,Definition,IsDefinitionRichText,Status,Related Terms,Synonyms,Acronym,Experts,Stewards,Resources,Parent Term Name,Term Template Names
```

**Same format as classic terms!** The UI uses the same export structure for both.

#### Existing CLI Format (uc_terms_bulk_example.csv)
```csv
name,description,status,acronym,owner_id,resource_name,resource_url
```

**Fields:**
- name (required)
- description (optional)
- status (Draft/Published/Archived, default: Draft)
- acronym (comma-separated)
- owner_id (Entra Object ID GUIDs, comma-separated)
- resource_name (semicolon-separated for multiple)
- resource_url (semicolon-separated for multiple)

#### Current CLI Implementation
- **Command:** `pvw uc term import-csv`
- **Location:** `purviewcli/cli/unified_catalog.py` (lines 1396-1555)
- **API:** Uses Unified Catalog REST API directly
- **Format:** Custom CSV parser with domain-id parameter
- **Supports:**
  - name, description, status
  - acronyms (comma-separated)
  - owner_ids (Entra Object IDs - GUIDs)
  - resources (name/url pairs)
- **Features:**
  - Dry-run mode
  - Progress tracking
  - Detailed error reporting
  - Rate limiting (200ms delay between requests)

---

## 2. Key Differences Between UI and CLI Formats

### 2.1 Classic Glossary Terms

| Feature | UI Format | CLI Format | Compatible? |
|---------|-----------|------------|-------------|
| **Field Names** | Title Case | Mixed Case | ❌ No - needs mapping |
| **Experts** | email:info format | Not supported | ❌ No |
| **Stewards** | email:info format | Not supported | ❌ No |
| **Resources** | name:url format | Not supported | ❌ No |
| **Parent Term** | Underscore path | Not supported | ❌ No |
| **Rich Text** | IsDefinitionRichText flag | Not supported | ⚠️ Partial |
| **Acronym** | Single "Acronym" field | "abbreviation" field | ⚠️ Different name |

### 2.2 UC Domain Glossary Terms

| Feature | UI Format | CLI Format | Compatible? |
|---------|-----------|------------|-------------|
| **Field Names** | Title Case with spaces | lowercase_snake_case | ❌ No - needs mapping |
| **Name** | "Name" | "name" | ✅ Yes (content) |
| **Definition** | "Definition" (rich text) | "description" (plain) | ⚠️ Different name |
| **Acronym** | "Acronym" (comma-separated) | "acronym" (comma-separated) | ✅ Yes (content) |
| **Experts/Stewards** | email:info format | owner_id (GUID only) | ❌ No - different concept |
| **Resources** | Single field | Separate name/url fields | ⚠️ Different structure |
| **Parent Term** | Hierarchical path | Not supported | ❌ No |
| **Domain** | Not in file | --domain-id parameter | ⚠️ External parameter |

---

## 3. Integration Possibilities

### 3.1 Option 1: Add UI Format Support to Existing Commands

**Pros:**
- Single command per term type
- Backward compatible
- Minimal user confusion

**Cons:**
- Complex field mapping logic
- Need to detect format automatically or via flag
- May duplicate code

**Implementation:**
```python
# Add --ui-format flag to existing commands
@term.command(name="import-csv")
@click.option("--csv-file", required=True)
@click.option("--domain-id", required=True)
@click.option("--ui-format", is_flag=True, help="Parse Purview UI export format")
def import_terms_from_csv(csv_file, domain_id, ui_format):
    if ui_format:
        # Use UI field mapping
        field_map = {
            "Name": "name",
            "Definition": "description",
            "Acronym": "acronyms",
            # ... etc
        }
    else:
        # Use CLI native format
        # ... existing code
```

### 3.2 Option 2: Create New UI-Specific Import Commands

**Pros:**
- Clean separation of concerns
- No risk of breaking existing functionality
- Can optimize for UI format specifics

**Cons:**
- More commands for users to learn
- Potential code duplication

**Implementation:**
```python
# New command group
@term.command(name="import-csv-ui")
@click.option("--csv-file", required=True)
@click.option("--domain-id", required=True)
def import_terms_from_ui_csv(csv_file, domain_id):
    """Import terms from Purview UI export format."""
    # Parse UI CSV format
    # Convert to API format
    # Import using existing client
```

### 3.3 Option 3: Create Universal CSV Converter

**Pros:**
- Flexible - can convert between any formats
- Reusable utility
- Users can preview conversion before import

**Cons:**
- Two-step process for users
- More complex workflow

**Implementation:**
```python
# New utility command
@term.command(name="convert-csv")
@click.option("--input-file", required=True)
@click.option("--output-file", required=True)
@click.option("--from-format", type=click.Choice(['ui', 'cli']))
@click.option("--to-format", type=click.Choice(['ui', 'cli']))
def convert_csv_format(input_file, output_file, from_format, to_format):
    """Convert between UI and CLI CSV formats."""
    # Parse input format
    # Transform data
    # Write output format
```

---

## 4. Field Mapping Specifications

### 4.1 Classic Glossary Terms (UI → CLI)

```python
UI_TO_CLI_GLOSSARY_MAP = {
    "Name": "name",
    "Nick Name": "nickName",
    "Definition": "definition",
    "IsDefinitionRichText": "isDefinitionRichText",
    "Status": "status",
    "Acronym": "abbreviation",  # Note: renamed
    "Related Terms": "relatedTerms",  # Needs parsing
    "Synonyms": "synonyms",  # Needs parsing
    "Experts": "experts",  # Needs email:info parsing
    "Stewards": "stewards",  # Needs email:info parsing
    "Resources": "resources",  # Needs name:url parsing
    "Parent Term Name": "parentTermName",  # Needs hierarchy parsing
    "Term Template Names": "termTemplateNames"  # Needs parsing
}
```

### 4.2 UC Domain Terms (UI → CLI)

```python
UI_TO_CLI_UC_MAP = {
    "Name": "name",
    "Nick Name": "nickName",  # Not in current CLI format
    "Definition": "description",
    "Status": "status",
    "Acronym": "acronyms",  # Already comma-separated
    # Experts/Stewards need special handling
    # UI has email:info → CLI needs Entra Object ID GUIDs
    "Resources": ("resource_name", "resource_url"),  # Split into two
    "Parent Term Name": None,  # Not supported in CLI
    "Term Template Names": None,  # Not supported in CLI
}
```

---

## 5. Complex Field Parsing Requirements

### 5.1 Experts/Stewards Format

**UI Format:**
```
email1@address.com:info1;email2@address.com:info2;
```

**Parsing Logic:**
```python
def parse_contacts(field_value):
    """Parse UI contact format to list of dicts."""
    contacts = []
    if field_value:
        for item in field_value.split(';'):
            item = item.strip()
            if ':' in item:
                email, info = item.split(':', 1)
                contacts.append({
                    'email': email.strip(),
                    'info': info.strip()
                })
            elif item:  # Just email
                contacts.append({'email': item})
    return contacts
```

**Challenge for UC Terms:**
- UI uses email addresses
- CLI requires Entra Object IDs (GUIDs)
- **Need Azure AD lookup** to convert email → GUID
- May require additional API calls

### 5.2 Resources Format

**UI Format:**
```
Microsoft Purview Project:https://web.purview.azure.com;Azure portal:https://portal.azure.com;
```

**Parsing Logic:**
```python
def parse_resources(field_value):
    """Parse UI resources format to list of dicts."""
    resources = []
    if field_value:
        for item in field_value.split(';'):
            item = item.strip()
            if ':' in item:
                name, url = item.split(':', 1)
                # Handle URLs with colons (https://)
                if not url.startswith('//') and '://' in item:
                    parts = item.split('://')
                    if len(parts) == 2:
                        name, url_part = parts[0].rsplit(':', 1)
                        url = url_part + '://' + parts[1]
                resources.append({
                    'name': name.strip(),
                    'url': url.strip()
                })
    return resources
```

### 5.3 Parent Term Hierarchy

**UI Format:**
```
Parent Name 1_Parent Name 2_Term Name
```

**Parsing Logic:**
```python
def parse_parent_path(field_value):
    """Parse hierarchical parent path."""
    if field_value:
        parts = field_value.split('_')
        return {
            'path': parts[:-1],  # All but last
            'term_name': parts[-1] if parts else None
        }
    return None
```

**Challenge:**
- Requires creating parent terms first (dependency resolution)
- Need to handle circular references
- May need multiple passes

### 5.4 Related Terms Format

**UI Format:**
```
Term Name 4;Parent Term 2_Term Name 5@otherGlossaryName;
```

**Parsing Logic:**
```python
def parse_related_terms(field_value):
    """Parse related terms with optional glossary references."""
    terms = []
    if field_value:
        for item in field_value.split(';'):
            item = item.strip()
            if '@' in item:
                term_path, glossary = item.split('@', 1)
                terms.append({
                    'termPath': term_path.strip(),
                    'glossary': glossary.strip()
                })
            elif item:
                terms.append({'termPath': item})
    return terms
```

---

## 6. API Compatibility Analysis

### 6.1 Classic Glossary API

**Current Implementation:**
- Endpoint: `/api/atlas/v2/glossary/{glossaryGuid}/terms/import`
- Method: POST
- Format: JSON array of term objects
- **Supports:** All UI fields including hierarchy, experts, stewards

**Conclusion:** ✅ **UI format is FULLY compatible** with classic glossary API

### 6.2 Unified Catalog API

**Current Implementation:**
- Endpoint: `/api/governance/glossaries/{glossaryId}/terms`
- Method: POST (individual term creation)
- Format: Single term JSON object
- **Does NOT support:**
  - Experts/Stewards in UI format
  - Parent term hierarchy
  - Related terms
  - Synonyms
  - Term templates

**Conclusion:** ⚠️ **UI format has MORE fields** than UC API supports

**Implications:**
- Need to map/ignore unsupported fields
- Experts/Stewards → owner_ids requires Azure AD lookup
- Parent hierarchy not supported (flat structure only)
- May need to use classic glossary API even for UC terms

---

## 7. Recommendations

### 7.1 Immediate Actions

1. **Add UI format support to classic glossary import**
   - Extend `pvw glossary import-terms` command
   - Add `--ui-format` flag
   - Implement field mapping
   - Support all UI fields (experts, stewards, resources, hierarchy)

2. **Add UI format adapter for UC terms**
   - Create converter function in `unified_catalog.py`
   - Map UI format to CLI format
   - Handle owner_id conversion (email → GUID)
   - Add warning for unsupported fields

### 7.2 Code Changes Required

#### File: `purviewcli/cli/glossary.py`

```python
# Add UI format parsing function
def parse_ui_glossary_csv(csv_file):
    """Parse Purview UI export format for classic glossary terms."""
    import csv
    terms = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Skip instruction row
            if row.get('Name', '').startswith('(Please remove'):
                continue
                
            term = {
                'name': row.get('Name', '').strip(),
                'nickName': row.get('Nick Name', '').strip(),
                'definition': row.get('Definition', '').strip(),
                'status': row.get('Status', 'Draft').strip(),
                'abbreviation': row.get('Acronym', '').strip(),
                # ... parse other fields
            }
            
            # Parse experts
            if row.get('Experts'):
                term['experts'] = parse_contacts(row['Experts'])
            
            # Parse stewards  
            if row.get('Stewards'):
                term['stewards'] = parse_contacts(row['Stewards'])
            
            # Parse resources
            if row.get('Resources'):
                term['resources'] = parse_resources(row['Resources'])
            
            # Parse parent hierarchy
            if row.get('Parent Term Name'):
                term['parentTerm'] = parse_parent_path(row['Parent Term Name'])
            
            terms.append(term)
    
    return terms

# Update import-terms command
@glossary.command(name="import-terms")
@click.option('--csv-file', required=False, type=click.Path(exists=True))
@click.option('--json-file', required=False, type=click.Path(exists=True))
@click.option('--glossary-guid', required=True)
@click.option('--include-term-hierarchy', is_flag=True)
@click.option('--ui-format', is_flag=True, help='Parse Purview UI export CSV format')
def import_terms_csv(csv_file, json_file, glossary_guid, include_term_hierarchy, ui_format):
    """Import glossary terms from CSV or JSON file."""
    # ... existing validation
    
    if csv_file:
        if ui_format:
            # Use UI format parser
            terms = parse_ui_glossary_csv(csv_file)
        else:
            # Use existing simple parser
            terms = parse_simple_csv(csv_file)
        
        # Convert to API format and import
        # ... rest of implementation
```

#### File: `purviewcli/cli/unified_catalog.py`

```python
# Add UI format parsing for UC terms
def parse_ui_uc_csv(csv_file, domain_id):
    """Parse Purview UI export format for UC domain glossary terms.
    
    Note: UI format includes fields not supported by UC API:
    - Experts/Stewards (needs conversion to owner_ids with Azure AD lookup)
    - Parent Term hierarchy (not supported in UC)
    - Related Terms (not supported in UC)
    - Term Templates (not supported in UC)
    """
    import csv
    terms = []
    unsupported_fields = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            term = {
                'name': row.get('Name', '').strip(),
                'description': row.get('Definition', '').strip(),
                'status': row.get('Status', 'Draft').strip(),
                'domain_id': domain_id,
                'acronyms': [],
                'owner_ids': [],
                'resources': []
            }
            
            # Parse acronyms
            if row.get('Acronym'):
                term['acronyms'] = [a.strip() for a in row['Acronym'].split(',')]
            
            # Parse resources
            if row.get('Resources'):
                resources = parse_resources(row['Resources'])
                term['resources'] = [
                    {'name': r['name'], 'url': r['url']} 
                    for r in resources
                ]
            
            # Handle experts/stewards (requires Azure AD lookup)
            if row.get('Experts') or row.get('Stewards'):
                # Extract emails
                emails = []
                if row.get('Experts'):
                    experts = parse_contacts(row['Experts'])
                    emails.extend([e['email'] for e in experts])
                if row.get('Stewards'):
                    stewards = parse_contacts(row['Stewards'])
                    emails.extend([s['email'] for s in stewards])
                
                # TODO: Convert emails to Entra Object IDs
                # term['owner_ids'] = convert_emails_to_guids(emails)
                unsupported_fields.append(f"Experts/Stewards for term '{term['name']}'")
            
            # Warn about unsupported fields
            if row.get('Parent Term Name'):
                unsupported_fields.append(f"Parent hierarchy for term '{term['name']}'")
            if row.get('Related Terms'):
                unsupported_fields.append(f"Related terms for term '{term['name']}'")
            
            terms.append(term)
    
    return terms, unsupported_fields

# Add option to existing command
@term.command(name="import-csv")
@click.option("--csv-file", required=True, type=click.Path(exists=True))
@click.option("--domain-id", required=True)
@click.option("--ui-format", is_flag=True, help='Parse Purview UI export CSV format')
@click.option("--dry-run", is_flag=True)
def import_terms_from_csv(csv_file, domain_id, ui_format, dry_run):
    """Bulk import glossary terms from CSV file."""
    try:
        if ui_format:
            terms, unsupported = parse_ui_uc_csv(csv_file, domain_id)
            
            if unsupported:
                console.print("\n[yellow]WARNING: Following fields not supported by UC API:[/yellow]")
                for field in set(unsupported):
                    console.print(f"  [dim]- {field}[/dim]")
                console.print()
        else:
            # Use existing parser
            terms = parse_cli_uc_csv(csv_file, domain_id)
        
        # ... rest of existing implementation
```

### 7.3 Additional Utilities Needed

#### Azure AD Email-to-GUID Converter

```python
# File: purviewcli/plugins/azure_ad.py

from azure.identity import DefaultAzureCredential
from msgraph import GraphServiceClient

class AzureADHelper:
    """Helper for Azure AD operations."""
    
    def __init__(self):
        self.credential = DefaultAzureCredential()
        self.client = GraphServiceClient(credentials=self.credential)
    
    async def email_to_object_id(self, email: str) -> str:
        """Convert email address to Entra Object ID (GUID).
        
        Args:
            email: User email address
            
        Returns:
            Entra Object ID (GUID) or None if not found
        """
        try:
            users = await self.client.users.get(
                filter=f"mail eq '{email}' or userPrincipalName eq '{email}'"
            )
            if users and users.value:
                return users.value[0].id
        except Exception as e:
            console.print(f"[yellow]WARNING: Could not resolve {email}: {e}[/yellow]")
        return None
    
    async def emails_to_object_ids(self, emails: list) -> list:
        """Convert multiple email addresses to Object IDs.
        
        Args:
            emails: List of email addresses
            
        Returns:
            List of Object IDs (GUIDs)
        """
        import asyncio
        tasks = [self.email_to_object_id(email) for email in emails]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r]  # Filter out None values
```

### 7.4 Testing Requirements

1. **Test classic glossary UI import**
   - Import sample UI CSV file
   - Verify all fields (experts, stewards, resources, hierarchy)
   - Validate term relationships
   - Check rich text handling

2. **Test UC term UI import**
   - Import sample UI CSV file
   - Verify mapped fields (name, description, status, acronyms)
   - Confirm warnings for unsupported fields
   - Test resource parsing

3. **Test email-to-GUID conversion**
   - Mock Azure AD responses
   - Handle invalid emails gracefully
   - Test batch conversion performance

4. **Test format detection**
   - Auto-detect UI vs CLI format (optional feature)
   - Handle edge cases (empty files, malformed CSVs)

---

## 8. Migration Guide for Users

### 8.1 Classic Glossary Terms

**Export from UI:**
1. Navigate to Data Catalog → Glossaries
2. Select glossary
3. Click Export → Download CSV

**Import with CLI:**
```bash
# Option 1: Use UI format directly
pvw glossary import-terms \
  --csv-file "Sample-2025_11_18-09_39_56.csv" \
  --glossary-guid "your-glossary-guid" \
  --ui-format

# Option 2: Convert then import (if converter implemented)
pvw glossary convert-csv \
  --input-file "Sample-2025_11_18-09_39_56.csv" \
  --output-file "converted.csv" \
  --from-format ui \
  --to-format cli

pvw glossary import-terms \
  --csv-file "converted.csv" \
  --glossary-guid "your-glossary-guid"
```

### 8.2 UC Domain Glossary Terms

**Export from UI:**
1. Navigate to Unified Catalog → Domains
2. Select domain
3. Click Export → Download CSV

**Import with CLI:**
```bash
# Use UI format with domain ID
pvw uc term import-csv \
  --csv-file "HR-2025_11_18-09_38_57.csv" \
  --domain-id "your-domain-id" \
  --ui-format \
  --dry-run  # Preview first

# Remove --dry-run to actually import
pvw uc term import-csv \
  --csv-file "HR-2025_11_18-09_38_57.csv" \
  --domain-id "your-domain-id" \
  --ui-format
```

---

## 9. Summary

### Compatibility Matrix

| Feature | Classic Glossary | UC Terms | Notes |
|---------|------------------|----------|-------|
| **UI CSV Import** | ✅ Fully Compatible | ⚠️ Partially Compatible | UC has API limitations |
| **Name/Definition** | ✅ Yes | ✅ Yes | Direct mapping |
| **Status** | ✅ Yes | ✅ Yes | Direct mapping |
| **Acronyms** | ✅ Yes | ✅ Yes | Direct mapping |
| **Experts/Stewards** | ✅ Yes | ⚠️ Needs conversion | Email → GUID required |
| **Resources** | ✅ Yes | ✅ Yes | Parse name:url format |
| **Parent Hierarchy** | ✅ Yes | ❌ No | Not in UC API |
| **Related Terms** | ✅ Yes | ❌ No | Not in UC API |
| **Term Templates** | ✅ Yes | ❌ No | Not in UC API |

### Recommended Implementation Priority

1. **High Priority:** Classic glossary UI format support (fully compatible)
2. **Medium Priority:** UC term UI format adapter (with limitations documented)
3. **Low Priority:** Universal CSV converter utility
4. **Future:** Azure AD integration for email-to-GUID conversion

### Estimated Development Effort

- **Classic Glossary UI Support:** 4-6 hours
  - CSV parser: 2 hours
  - Field mapping: 1 hour
  - Testing: 2-3 hours

- **UC Term UI Adapter:** 6-8 hours
  - CSV parser: 2 hours
  - Field mapping with warnings: 2 hours
  - Azure AD integration (optional): 3 hours
  - Testing: 3 hours

- **Documentation:** 2-3 hours
  - User guide updates
  - Sample files
  - Migration examples

**Total: 12-17 hours**

---

## 10. Next Steps

1. ✅ **Analysis Complete** (this document)
2. ⏳ **Get user feedback** on recommended approach
3. ⏳ **Implement classic glossary UI format support**
4. ⏳ **Implement UC term UI format adapter**
5. ⏳ **Add Azure AD email-to-GUID converter** (optional)
6. ⏳ **Write tests**
7. ⏳ **Update documentation**
8. ⏳ **Create sample migration scripts**

---

## Appendix A: Sample Conversion Examples

### A.1 Classic Glossary Term (UI → API)

**UI CSV Row:**
```csv
"Employee","Employee","<div>A person engaged...</div>","","Published","","","Person, Staff, Worker","user1@company.com:Expert","admin@company.com:Owner","HR Portal:https://hr.example.com","","System Default;"
```

**Converted API JSON:**
```json
{
  "name": "Employee",
  "nickName": "Employee",
  "definition": "<div>A person engaged...</div>",
  "isDefinitionRichText": false,
  "status": "Published",
  "abbreviation": "Person, Staff, Worker",
  "experts": [
    {"email": "user1@company.com", "info": "Expert"}
  ],
  "stewards": [
    {"email": "admin@company.com", "info": "Owner"}
  ],
  "resources": [
    {"name": "HR Portal", "url": "https://hr.example.com"}
  ],
  "termTemplateNames": ["System Default"]
}
```

### A.2 UC Domain Term (UI → API)

**UI CSV Row:**
```csv
"Employee","Employee","A person engaged...","","Published","","","Person, Staff, Worker","user1@company.com","admin@company.com","HR Portal:https://hr.example.com","","System Default;"
```

**Converted API JSON:**
```json
{
  "name": "Employee",
  "description": "A person engaged...",
  "status": "Published",
  "domain_id": "hr-domain-guid",
  "acronyms": ["Person", "Staff", "Worker"],
  "owner_ids": [
    "guid-for-user1",
    "guid-for-admin"
  ],
  "resources": [
    {"name": "HR Portal", "url": "https://hr.example.com"}
  ]
}
```

**Notes:**
- Parent Term Name not included (not supported)
- Term Template Names not included (not supported)
- Experts/Stewards merged into owner_ids (requires Azure AD lookup)

---

**End of Analysis**
