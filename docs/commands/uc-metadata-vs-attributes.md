# UC Metadata vs. Custom Attributes - Clear Reference Guide

## Quick Comparison

| Aspect | **Business Metadata** (`metadata`) | **Custom Attributes** (`attribute`) |
|--------|-----------------------------------|-------------------------------------|
| **What It Is** | Apply KEY/VALUE pairs to UC assets | Define reusable attribute schemas |
| **Analogy** | Like assigning **labels** to entities | Like defining **custom attribute types** |
| **Use Case** | Tag specific assets with properties | Create standardized metadata patterns |
| **Scope** | Per-asset (data products, terms, etc.) | Global/tenant-wide definitions |
| **Commands** | `add`, `update`, `delete`, `get` | `create`, `update`, `delete`, `get` |
| **Availability** | Always available | May return HTTP 405 on some tenants |

---

## **Business Metadata** (`pvw uc metadata`)

### What It Does
Applies **group-based key/value metadata** to UC assets (similar to entity labels but with a GROUP structure).

### Conceptual Model
```
Asset (Data Product, Term, Domain, etc.)
  └─ Business Metadata
     └─ Group: "Governance"
        ├─ Key: "DataOwner" → Value: "john.doe@company.com"
        ├─ Key: "Classification" → Value: "SENSITIVE"
        └─ Key: "ReportingPeriod" → Value: "Q1-2026"
```

### Commands

#### **List definitions**
```bash
pvw uc metadata list
pvw uc metadata list --output json
```
Shows all available **business metadata groups and their allowed keys** (pre-defined schema).

#### **Add metadata to an asset**
```bash
pvw uc metadata add --asset-id <guid> \
                    --group Governance \
                    --key DataOwner \
                    --value "john.doe@company.com"
```
Assigns a GROUP/KEY/VALUE triple to a specific asset.

#### **Get metadata from an asset**
```bash
pvw uc metadata get --asset-id <guid>
```
Retrieves all business metadata applied to an asset.

#### **Update metadata on an asset**
```bash
pvw uc metadata update --asset-id <guid> \
                       --group Governance \
                       --key DataOwner \
                       --value "jane.smith@company.com"
```
Changes the value of an existing metadata key on an asset.

#### **Delete metadata from an asset**
```bash
pvw uc metadata delete --asset-id <guid> \
                       --group Governance \
                       --key DataOwner
```
Removes a specific key/value pair from an asset.

### Example Use Case
```bash
# Tag a data product with business metadata
pvw uc metadata add --asset-id "560f1496-f0d3-4c8e-b343-8636bd4f9d4a" \
                    --group Governance \
                    --key "DataOwner" \
                    --value "analytics-team@company.com"

pvw uc metadata add --asset-id "560f1496-f0d3-4c8e-b343-8636bd4f9d4a" \
                    --group Governance \
                    --key "Classification" \
                    --value "INTERNAL"

# View all metadata on the asset
pvw uc metadata get --asset-id "560f1496-f0d3-4c8e-b343-8636bd4f9d4a"

# Update the owner
pvw uc metadata update --asset-id "560f1496-f0d3-4c8e-b343-8636bd4f9d4a" \
                       --group Governance \
                       --key "DataOwner" \
                       --value "new-team@company.com"
```

---

## **Custom Attributes** (`pvw uc attribute`)

### What It Does
**Defines reusable attribute schemas** that can be applied to assets. Think of it as creating a "template" or "blueprint" for custom metadata.

### Conceptual Model
```
Tenant-Level Definitions
  └─ Custom Attribute: "CustomerSensitivity"
     ├─ Type: String
     ├─ Required: true
     ├─ Validation: "HIGH", "MEDIUM", "LOW"
     └─ Scope: Data Assets

  └─ Custom Attribute: "DataClassification"
     ├─ Type: String
     ├─ Required: true
     └─ Scope: All Catalog Items
```

### Commands

#### **List all custom attribute definitions**
```bash
pvw uc attribute list
pvw uc attribute list --output json
```
Shows all custom attribute schemas defined in the tenant.

#### **Create a new custom attribute definition**
```bash
pvw uc attribute create --name "CustomerSensitivity" \
                        --data-type string \
                        --required
```
Defines a new attribute schema that can be used across assets.

#### **Get a specific custom attribute definition**
```bash
pvw uc attribute get --attribute-id <guid>
```
Shows details about a specific custom attribute schema.

#### **Update a custom attribute definition**
```bash
pvw uc attribute update --attribute-id <guid> \
                        --required \
                        --description "Updated description"
```
Modifies an existing attribute schema.

#### **Delete a custom attribute definition**
```bash
pvw uc attribute delete --attribute-id <guid> --yes
```
Removes a custom attribute schema from the tenant.

### Example Use Case
```bash
# Define a custom attribute for all data assets
pvw uc attribute create --name "DataQualityScore" \
                        --data-type number \
                        --description "Overall quality rating (0-100)"

# Define another for sensitive data
pvw uc attribute create --name "PII_Classifier" \
                        --data-type string \
                        --description "PII classification level"

# List all custom attributes
pvw uc attribute list
```

⚠️ **Note**: Custom attribute operations may return **HTTP 405 (Method Not Allowed)** on many tenants—this means the feature is disabled at the tenant level, not a permission issue.

---

## Entity vs. UC: Metadata Patterns

### Data Map Entities (CLI: `pvw entity`)
```bash
# Labels (multiple values per entity)
pvw entity add-labels --guid <guid> --labels ["Production", "Sensitive"]
pvw entity set-labels --guid <guid> --labels ["NewLabel"]
pvw entity remove-labels --guid <guid> --labels ["OldLabel"]

# Custom Attributes (KEY/VALUE structure)
pvw entity set-custom-attribute --guid <guid> \
                                --attr-group "MyGroup" \
                                --attr-key "MyKey" \
                                --attr-value "MyValue"
```

### Unified Catalog Assets (CLI: `pvw uc`)
```bash
# Business Metadata (GROUP/KEY/VALUE structure)
pvw uc metadata add --asset-id <guid> \
                    --group Governance \
                    --key DataOwner \
                    --value "team@company.com"

# Custom Attributes (Schema definitions)
pvw uc attribute create --name "ComplianceLevel" \
                        --type String \
                        --scope DataAsset
```

---

## Decision Tree: Which Command Should I Use?

```
Q: Do you want to assign a value/tag to a SPECIFIC UC asset?
├─ YES? → Use `pvw uc metadata add/update`
└─ NO?
   Q: Do you want to define a reusable attribute schema for your tenant?
   ├─ YES? → Use `pvw uc attribute create`
   └─ NO? → Check other UC commands (domain, term, dataproduct, etc.)
```

---

## Common Scenarios

### Scenario 1: Mark a Data Product as Sensitive
```bash
# Use metadata to tag a specific product
pvw uc metadata add --asset-id "product-guid-123" \
                    --group Governance \
                    --key Classification \
                    --value "SENSITIVE"
```

### Scenario 2: Define a Tenant-Wide Compliance Requirement
```bash
# First, define the custom attribute (schema)
pvw uc attribute create --name "ComplianceFramework" \
                        --data-type string \
                        --required

# Then, apply it via metadata to specific assets
pvw uc metadata add --asset-id "asset-guid-456" \
                    --group Compliance \
                    --key Framework \
                    --value "GDPR"
```

### Scenario 3: Update Governance Information
```bash
# Change the data owner
pvw uc metadata update --asset-id "product-guid-789" \
                       --group Governance \
                       --key DataOwner \
                       --value "new-owner@company.com"
```

---

## Troubleshooting

### HTTP 405 Error on Custom Attributes

**Error:**
```
FAILED: Custom attribute not created
This endpoint is not enabled for this tenant/region. Use Atlas business metadata via 'pvw types putTypeDefs' with businessMetadataDefs instead.
HTTP 405: 
```

**Cause:**
The datagovernance catalog attributes endpoint is **disabled at the tenant level**. This is a platform limitation, not a permission issue.

**Solutions:**

#### Option 1: Use Business Metadata Instead (Recommended)
Instead of custom attribute definitions, use **business metadata** to achieve similar functionality:

```bash
# Create a business metadata group via Atlas
pvw types putTypeDefs --payload-file business-metadata-def.json

# Then apply it to assets
pvw uc metadata add --asset-id <guid> \
                    --group YourGroupName \
                    --key YourKey \
                    --value YourValue
```

#### Option 2: Request Endpoint Enablement
Contact your **Azure/Purview administrator** to enable the datagovernance catalog attributes endpoint (region-specific feature).

#### Option 3: Use Business Metadata Definitions
Define business metadata schemas directly in Atlas:

```json
{
  "businessMetadataDefs": [
    {
      "name": "CustomAttributes",
      "description": "Custom attribute definitions",
      "attributeDefs": [
        {
          "name": "DataQualityScore",
          "typeName": "string",
          "isOptional": true,
          "description": "Quality rating 0-100"
        }
      ]
    }
  ]
}
```

Then use:
```bash
pvw types putTypeDefs --payload-file business-metadata-def.json
pvw uc metadata add --asset-id <guid> --group CustomAttributes --key DataQualityScore --value "95"
```

---

### Other Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Group not found` | Business metadata group doesn't exist | Use `pvw uc metadata list` to see available groups |
| `Key not allowed in group` | Key is not defined in the group schema | Add to group definition or use different key |
| `Asset not found` | Invalid asset GUID | Verify asset ID is correct GUID format |
| `Invalid asset type` | Asset type doesn't support metadata | Check asset is a valid UC entity (domain, term, product, etc.) |

---

## Reference: Available UC Metadata Groups

Use `pvw uc metadata list` to see all available groups in your tenant. Common groups include:

- **Governance** - Data ownership, classification, stewardship
- **Compliance** - Regulatory framework, retention, sensitivity
- **Quality** - Quality scores, issue counts, last validated date
- **Operations** - Update frequency, SLA, support contacts
- **Custom Groups** - Organization-specific metadata (if configured)

