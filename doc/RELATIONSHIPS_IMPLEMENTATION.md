# Data Product and CDE Relationships Implementation

## Overview

Implementation of Microsoft Purview Data Governance Relationship APIs for Data Products and Critical Data Elements (CDEs). These APIs enable linking data products and CDEs to other catalog entities like critical data columns, terms, data assets, and more.

**Status:** ✅ IMPLEMENTED (Oct 28, 2025)
**API Version:** 2025-09-15-preview
**Documentation:** https://learn.microsoft.com/en-us/rest/api/purview/purviewdatagovernance/

---

## Implementation Summary

### What Was Added

**6 New Operations** (3 for Data Products + 3 for CDEs):

1. **Data Product Relationships**
   - Create: `POST /datagovernance/catalog/dataproducts/{id}/relationships`
   - List: `GET /datagovernance/catalog/dataproducts/{id}/relationships`
   - Delete: `DELETE /datagovernance/catalog/dataproducts/{id}/relationships`

2. **CDE Relationships**
   - Create: `POST /datagovernance/catalog/criticalDataElements/{id}/relationships`
   - List: `GET /datagovernance/catalog/criticalDataElements/{id}/relationships`
   - Delete: `DELETE /datagovernance/catalog/criticalDataElements/{id}/relationships`

---

## API Specification

### Supported Entity Types

Both Data Product and CDE relationships support these entity types:

| Entity Type | Description | Use Case |
|------------|-------------|----------|
| `CRITICALDATACOLUMN` | Critical data column | Link to specific data columns |
| `TERM` | Business glossary term | Associate business definitions |
| `DATAASSET` | Data asset (table, file) | Link to source data |
| `CRITICALDATAELEMENT` | Critical data element | Cross-link CDEs |
| `DATAPRODUCT` | Data product | Link CDEs to data products |

### Request/Response Format

**Create Relationship Request:**
```json
POST {endpoint}/datagovernance/catalog/dataproducts/{productId}/relationships
?api-version=2025-09-15-preview
&entityType=CRITICALDATACOLUMN

{
  "relationship1": {
    "description": "Primary data source column",
    "relationshipType": "Related",
    "assetId": "asset-guid",
    "entityId": "entity-guid"
  }
}
```

**Response (200 OK):**
```json
{
  "systemData": {
    "createdAt": "2025-10-28T10:00:00.000Z",
    "createdBy": "user-guid",
    "lastModifiedAt": "2025-10-28T10:00:00.000Z",
    "lastModifiedBy": "user-guid"
  },
  "description": "Primary data source column",
  "relationshipType": "Related",
  "entityId": "entity-guid"
}
```

**List Relationships Response:**
```json
{
  "value": [
    {
      "systemData": {...},
      "description": "...",
      "relationshipType": "Related",
      "entityId": "entity-guid"
    }
  ],
  "nextLink": "continuation-token-url"
}
```

**Delete Relationship Response:**
```
HTTP 204 No Content
```

---

## CLI Commands

### Data Product Relationships

#### Add Relationship
```bash
# Basic usage - link data product to critical data column
pvw uc dataproduct add-relationship \
  --product-id <product-guid> \
  --entity-type CRITICALDATACOLUMN \
  --entity-id <column-guid>

# With description
pvw uc dataproduct add-relationship \
  --product-id <product-guid> \
  --entity-type TERM \
  --entity-id <term-guid> \
  --description "Primary business term" \
  --relationship-type "Related"

# Link to data asset
pvw uc dataproduct add-relationship \
  --product-id <product-guid> \
  --entity-type DATAASSET \
  --entity-id <asset-guid> \
  --asset-id <asset-guid>
```

#### List Relationships
```bash
# List all relationships
pvw uc dataproduct list-relationships --product-id <product-guid>

# Filter by entity type
pvw uc dataproduct list-relationships \
  --product-id <product-guid> \
  --entity-type CRITICALDATACOLUMN

# JSON output
pvw uc dataproduct list-relationships \
  --product-id <product-guid> \
  --output json
```

#### Remove Relationship
```bash
# Interactive confirmation (default)
pvw uc dataproduct remove-relationship \
  --product-id <product-guid> \
  --entity-type CRITICALDATACOLUMN \
  --entity-id <column-guid>

# Skip confirmation
pvw uc dataproduct remove-relationship \
  --product-id <product-guid> \
  --entity-type TERM \
  --entity-id <term-guid> \
  --no-confirm
```

### CDE Relationships

#### Add Relationship
```bash
# Basic usage - link CDE to critical data column
pvw uc cde add-relationship \
  --cde-id <cde-guid> \
  --entity-type CRITICALDATACOLUMN \
  --entity-id <column-guid>

# With description
pvw uc cde add-relationship \
  --cde-id <cde-guid> \
  --entity-type TERM \
  --entity-id <term-guid> \
  --description "Regulatory term definition"

# Link to data product
pvw uc cde add-relationship \
  --cde-id <cde-guid> \
  --entity-type DATAPRODUCT \
  --entity-id <product-guid>
```

#### List Relationships
```bash
# List all relationships
pvw uc cde list-relationships --cde-id <cde-guid>

# Filter by entity type
pvw uc cde list-relationships \
  --cde-id <cde-guid> \
  --entity-type TERM

# JSON output
pvw uc cde list-relationships \
  --cde-id <cde-guid> \
  --output json
```

#### Remove Relationship
```bash
# Interactive confirmation (default)
pvw uc cde remove-relationship \
  --cde-id <cde-guid> \
  --entity-type CRITICALDATACOLUMN \
  --entity-id <column-guid>

# Skip confirmation
pvw uc cde remove-relationship \
  --cde-id <cde-guid> \
  --entity-type DATAPRODUCT \
  --entity-id <product-guid> \
  --no-confirm
```

---

## Use Cases

### 1. Data Product Lineage
Link data products to their source data assets and critical data columns:

```bash
# Link data product to source table
pvw uc dataproduct add-relationship \
  --product-id <product-guid> \
  --entity-type DATAASSET \
  --entity-id <table-guid> \
  --description "Source data table"

# Link to specific critical columns
pvw uc dataproduct add-relationship \
  --product-id <product-guid> \
  --entity-type CRITICALDATACOLUMN \
  --entity-id <ssn-column-guid> \
  --description "Contains SSN - PII data"
```

### 2. Business Glossary Integration
Associate data products with business terms:

```bash
# Link data product to primary business term
pvw uc dataproduct add-relationship \
  --product-id <product-guid> \
  --entity-type TERM \
  --entity-id <customer-term-guid> \
  --description "Customer Master Data"

# Link to compliance term
pvw uc dataproduct add-relationship \
  --product-id <product-guid> \
  --entity-type TERM \
  --entity-id <gdpr-term-guid> \
  --description "GDPR-compliant data product"
```

### 3. CDE Compliance Tracking
Link CDEs to data columns and terms for regulatory compliance:

```bash
# Link CDE to regulated column
pvw uc cde add-relationship \
  --cde-id <cde-guid> \
  --entity-type CRITICALDATACOLUMN \
  --entity-id <pii-column-guid> \
  --description "PII field requiring special handling"

# Associate with compliance term
pvw uc cde add-relationship \
  --cde-id <cde-guid> \
  --entity-type TERM \
  --entity-id <hipaa-term-guid> \
  --description "HIPAA-regulated element"
```

### 4. Cross-Resource Linking
Link CDEs to data products for impact analysis:

```bash
# Show which data products contain a CDE
pvw uc cde add-relationship \
  --cde-id <ssn-cde-guid> \
  --entity-type DATAPRODUCT \
  --entity-id <customer-product-guid>

pvw uc cde add-relationship \
  --cde-id <ssn-cde-guid> \
  --entity-type DATAPRODUCT \
  --entity-id <billing-product-guid>

# List all data products containing the CDE
pvw uc cde list-relationships \
  --cde-id <ssn-cde-guid> \
  --entity-type DATAPRODUCT
```

---

## PowerShell Automation Examples

### Bulk Relationship Creation

```powershell
# Link multiple terms to a data product
$productId = "product-guid"
$terms = @("term-1-guid", "term-2-guid", "term-3-guid")

foreach ($termId in $terms) {
    py -m purviewcli uc dataproduct add-relationship `
        --product-id $productId `
        --entity-type TERM `
        --entity-id $termId `
        --no-confirm
    Start-Sleep -Milliseconds 200  # Rate limiting
}
```

### Relationship Audit

```powershell
# Get all data products and their relationships
$products = py -m purviewcli uc dataproduct list --output json | ConvertFrom-Json
$products.value | ForEach-Object {
    $productId = $_.id
    $relationships = py -m purviewcli uc dataproduct list-relationships `
        --product-id $productId --output json | ConvertFrom-Json
    
    [PSCustomObject]@{
        ProductName = $_.name
        ProductId = $productId
        RelationshipCount = $relationships.value.Count
        EntityTypes = ($relationships.value | Select-Object -ExpandProperty relationshipType -Unique)
    }
}
```

### CDE Impact Analysis

```powershell
# Find all data products linked to a CDE
$cdeId = "cde-guid"
$relationships = py -m purviewcli uc cde list-relationships `
    --cde-id $cdeId `
    --entity-type DATAPRODUCT `
    --output json | ConvertFrom-Json

Write-Host "CDE Impact Analysis:"
Write-Host "-------------------"
Write-Host "Linked Data Products: $($relationships.value.Count)"

foreach ($rel in $relationships.value) {
    Write-Host "  - Product ID: $($rel.entityId)"
    Write-Host "    Description: $($rel.description)"
    Write-Host "    Created: $($rel.systemData.createdAt)"
}
```

---

## Code Structure

### Files Modified

1. **`purviewcli/client/endpoints.py`**
   - Added 6 new endpoint definitions (3 data product + 3 CDE)
   - Lines: Data product relationships after line 395
   - Lines: CDE relationships after line 415

2. **`purviewcli/client/_unified_catalog.py`**
   - Added 6 new client methods with `@decorator`
   - `create_data_product_relationship()` - Line ~210
   - `get_data_product_relationships()` - Line ~245
   - `delete_data_product_relationship()` - Line ~265
   - `create_cde_relationship()` - Line ~955
   - `get_cde_relationships()` - Line ~990
   - `delete_cde_relationship()` - Line ~1010

3. **`purviewcli/cli/unified_catalog.py`**
   - Added 6 new CLI commands with Click decorators
   - Data product commands: Lines 500-665
   - CDE commands: Lines 2100-2265

### Implementation Pattern

Each operation follows the established pattern:

1. **Endpoint Definition** (endpoints.py):
   ```python
   "operation_name": "/datagovernance/catalog/resource/{id}/relationships"
   ```

2. **Client Method** (_unified_catalog.py):
   ```python
   @decorator
   def operation_name(self, args):
       """Docstring with API details."""
       # Parse arguments
       # Set method, endpoint, params, payload
   ```

3. **CLI Command** (unified_catalog.py):
   ```python
   @group.command(name="operation-name")
   @click.option(...)
   def operation_name(...):
       """Help text with examples."""
       # Create client
       # Call method
       # Format output (table/json)
   ```

---

## API Coverage Impact

**Before Implementation:**
- Data Products: 5/10 operations (50%)
- CDEs: 5/10 operations (50%)
- Overall: 35/50 operations (70%)

**After Implementation:**
- Data Products: 8/10 operations (80%) ⬆️ +30%
- CDEs: 8/10 operations (80%) ⬆️ +30%
- Overall: 41/50 operations (82%) ⬆️ +12%

**Remaining Gaps:**
- Query APIs (4 operations) - HIGH priority
- Facets (4 operations) - MEDIUM priority
- Related Term Entities (3 operations) - MEDIUM priority

---

## Testing Recommendations

### Functional Testing

1. **Create Relationships:**
   - Test all entity types (CRITICALDATACOLUMN, TERM, DATAASSET, etc.)
   - Verify required fields (product-id, entity-type, entity-id)
   - Test optional fields (description, relationship-type, asset-id)
   - Validate response includes systemData

2. **List Relationships:**
   - Test without filters (all relationships)
   - Test with entity-type filter
   - Verify pagination support
   - Test JSON vs table output

3. **Delete Relationships:**
   - Test interactive confirmation
   - Test --no-confirm flag
   - Verify 204 No Content response
   - Test error handling (not found, invalid ID)

### Error Scenarios

```bash
# Invalid product ID
pvw uc dataproduct add-relationship \
  --product-id "invalid-guid" \
  --entity-type TERM \
  --entity-id <term-guid>
# Expected: 404 Not Found

# Missing required entity-type
pvw uc dataproduct add-relationship \
  --product-id <product-guid> \
  --entity-id <term-guid>
# Expected: Click validation error

# Delete non-existent relationship
pvw uc dataproduct remove-relationship \
  --product-id <product-guid> \
  --entity-type TERM \
  --entity-id "non-existent-guid" \
  --no-confirm
# Expected: 404 Not Found or 204 No Content
```

### Integration Testing

Test relationship workflows end-to-end:

```bash
# 1. Create data product
PRODUCT_ID=$(pvw uc dataproduct create ... --output json | jq -r '.id')

# 2. Add relationships
pvw uc dataproduct add-relationship --product-id $PRODUCT_ID --entity-type TERM --entity-id <term-guid>
pvw uc dataproduct add-relationship --product-id $PRODUCT_ID --entity-type CRITICALDATACOLUMN --entity-id <col-guid>

# 3. List and verify
pvw uc dataproduct list-relationships --product-id $PRODUCT_ID

# 4. Clean up
pvw uc dataproduct remove-relationship --product-id $PRODUCT_ID --entity-type TERM --entity-id <term-guid> --no-confirm
pvw uc dataproduct remove-relationship --product-id $PRODUCT_ID --entity-type CRITICALDATACOLUMN --entity-id <col-guid> --no-confirm
pvw uc dataproduct delete --product-id $PRODUCT_ID --yes
```

---

## Known Limitations

1. **No Bulk Operations:**
   - CLI provides single-relationship operations only
   - Use PowerShell scripts for bulk operations (see examples above)

2. **No Relationship IDs:**
   - Relationships identified by (entityType, entityId) pair
   - No unique relationship ID in API
   - Delete requires both entity type and entity ID

3. **Limited Relationship Types:**
   - API supports "Related" type
   - No other relationship types documented yet

4. **No Bi-directional Queries:**
   - Can query "Data Product → Related Entities"
   - Cannot query "Entity → Related Data Products" via this API
   - Use Query APIs when implemented for reverse lookups

---

## Next Steps

### Immediate (HIGH Priority)

1. **Query APIs Implementation:**
   - POST `/datagovernance/catalog/dataproducts/query`
   - POST `/datagovernance/catalog/criticalDataElements/query`
   - POST `/datagovernance/catalog/terms/query`
   - POST `/datagovernance/catalog/objectives/query`
   - **Impact:** Enable advanced search, filtering, reverse lookups

### Near-term (MEDIUM Priority)

2. **Facets Implementation:**
   - GET `/datagovernance/catalog/dataproducts/{id}/facets`
   - GET `/datagovernance/catalog/criticalDataElements/{id}/facets`
   - GET `/datagovernance/catalog/terms/{id}/facets`
   - GET `/datagovernance/catalog/objectives/{id}/facets`
   - **Impact:** Analytics, aggregations, reporting

3. **Related Term Entities:**
   - POST `/datagovernance/catalog/terms/{id}/related`
   - GET `/datagovernance/catalog/terms/{id}/related`
   - DELETE `/datagovernance/catalog/terms/{id}/related/{relatedId}`
   - **Impact:** Glossary management, term hierarchies

---

## References

- **Microsoft Purview Data Governance API:** https://learn.microsoft.com/en-us/rest/api/purview/purviewdatagovernance/
- **Create Data Product Relationship:** https://learn.microsoft.com/en-us/rest/api/purview/purviewdatagovernance/create-data-product-relationship
- **List Data Product Relationships:** https://learn.microsoft.com/en-us/rest/api/purview/purviewdatagovernance/list-data-product-relationships
- **Delete Data Product Relationship:** https://learn.microsoft.com/en-us/rest/api/purview/purviewdatagovernance/delete-data-product-relationship
- **Gap Analysis Document:** `doc/API_COVERAGE_GAP_ANALYSIS.md`
- **API Discovery Document:** `doc/API_DISCOVERY_FINAL.md`

---

**Implementation Date:** October 28, 2025  
**API Version:** 2025-09-15-preview  
**Status:** ✅ Production Ready  
**Coverage:** 82% (41/50 operations)
