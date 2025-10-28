# Business Metadata Templates

## ⚠️ Important: Command Structure

All commands require the `types` group:

```bash
# ✅ Correct
py -m purviewcli types create-business-metadata-def --payload-file file.json

# ❌ Incorrect (missing 'types')
py -m purviewcli create-business-metadata-def --payload-file file.json
```

---

## Available Templates

### 1. Governance (Business Concepts)
**File:** `business_metadata_governance.json`  
**Scope:** Business Concept (Terms, Domains, Business Rules)  
**Attributes:**
- `DataOwner` (string) - Owner of the business concept
- `ComplianceStatus` (string) - Compliance status
- `ReviewDate` (date) - Last review date

**Usage:**
```bash
py -m purviewcli types create-business-metadata-def --payload-file templates/business_metadata_governance.json
```

### 2. DataQuality (Data Assets)
**File:** `business_metadata_quality.json`  
**Scope:** Data Asset (Tables, Files, Databases)  
**Attributes:**
- `QualityScore` (int 0-100) - Data quality score
- `LastValidated` (date) - Last validation date
- `ValidationNotes` (string) - Validation notes

**Usage:**
```bash
py -m purviewcli types create-business-metadata-def --payload-file templates/business_metadata_quality.json
```

### 3. Privacy (Business Concepts)
**File:** `business_metadata_privacy.json`  
**Scope:** Business Concept (Terms only)  
**Attributes:**
- `PrivacyLevel` (string) - Privacy classification level
- `PIIContained` (boolean) - Contains PII data
- `DataClassification` (string) - Data classification

**Usage:**
```bash
py -m purviewcli types create-business-metadata-def --payload-file templates/business_metadata_privacy.json
```

### 4. Documentation (Universal)
**File:** `business_metadata_universal.json`  
**Scope:** Universal (All entities - Terms, Tables, Files, etc.)  
**Attributes:**
- `DocumentationLink` (string) - Link to documentation
- `LastUpdated` (date) - Last update date
- `UpdatedBy` (string) - Last updated by

**Usage:**
```bash
py -m purviewcli types create-business-metadata-def --payload-file templates/business_metadata_universal.json
```

### 5. Advanced Governance (with Enums)
**File:** `business_metadata_advanced_with_enums.json`  
**Scope:** Business Concept (Terms, Domains)  
**Attributes:**
- `Status` (enum) - Draft, InReview, Approved, Rejected, Archived
- `Confidentiality` (enum) - Public, Internal, Confidential, HighlyConfidential
- `ApprovedBy` (string) - Approver name
- `ApprovalDate` (date) - Approval date

**Usage:**
```bash
py -m purviewcli types create-business-metadata-def --payload-file templates/business_metadata_advanced_with_enums.json
```

---

## Quick Start

### Method 1: Interactive Wizard
```cmd
quick_start_business_metadata.bat
```

### Method 2: Test Single Template
```bash
# Validate first
py -m purviewcli types create-business-metadata-def --payload-file templates/business_metadata_governance.json --dry-run --validate

# Create
py -m purviewcli types create-business-metadata-def --payload-file templates/business_metadata_governance.json

# Verify
py -m purviewcli types list-business-metadata-groups
```

### Method 3: PowerShell Bulk Creation
```powershell
.\samples\powershell\create_business_metadata.ps1
```

---

## Command Reference

### List Commands
```bash
# List all groups
py -m purviewcli types list-business-metadata-groups
py -m purviewcli types list-business-metadata-groups --output json

# List all attributes
py -m purviewcli types list-business-attributes
py -m purviewcli types list-business-attributes --output json
```

### Create Command
```bash
# Validate first (dry-run)
py -m purviewcli types create-business-metadata-def --payload-file <file.json> --dry-run --validate

# Create
py -m purviewcli types create-business-metadata-def --payload-file <file.json>
```

### Read Command
```bash
py -m purviewcli types read-business-metadata-def --name GroupName
py -m purviewcli types read-business-metadata-def --guid <GUID>
```

### Update Command
```bash
py -m purviewcli types update-business-metadata-def --payload-file <file.json>
```

### Delete Command
```bash
py -m purviewcli types delete-business-metadata-def --name GroupName
```

---

## Common Errors

### Error: "No such command"
```
Error: No such command 'create-business-metadata-def'.
```

**Cause:** Missing `types` group.

**Solution:**
```bash
# ❌ Wrong
py -m purviewcli create-business-metadata-def --payload-file file.json

# ✅ Correct
py -m purviewcli types create-business-metadata-def --payload-file file.json
```

### Error: "Business metadata already exists"
**Solution:** Choose a different name or delete the existing group:
```bash
py -m purviewcli types delete-business-metadata-def --name ExistingGroupName
```

### Error: "Invalid JSON"
**Solution:** Validate your JSON at https://jsonlint.com/ or use the validate flag:
```bash
py -m purviewcli types create-business-metadata-def --payload-file file.json --dry-run --validate
```

---

## Scope Reference

### Business Concept Scope
```json
"options": {
  "dataGovernanceOptions": "{\"applicableConstructs\":[\"domain:*\",\"businessConcept:*\"]}"
}
```
**Applies to:** Terms, Domains, Business Rules

### Data Asset Scope
```json
"options": {
  "dataGovernanceOptions": "{\"applicableConstructs\":[\"dataset:*\"]}"
}
```
**Applies to:** Tables, Files, Databases, etc.

### Universal Scope
```json
"options": {
  "dataGovernanceOptions": "{\"applicableConstructs\":[\"domain:*\",\"businessConcept:*\",\"dataset:*\"]}"
}
```
**Applies to:** Everything

---

## Additional Resources

- **Complete Notebook:** `samples/notebooks (plus)/business_metadata_management.ipynb`
- **Quick Reference:** `doc/guides/business-metadata-quick-ref.md`
- **Package Summary:** `BUSINESS_METADATA_READY.md`
- **Scope Guide:** `doc/guides/business-metadata-scopes.md`

---

## Tips

1. **Always include `types` in your commands**
2. **Use `--dry-run --validate` before creating**
3. **Test in non-production environment first**
4. **Keep templates in version control**
5. **Document your metadata schema**
