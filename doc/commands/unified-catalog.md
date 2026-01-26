# Microsoft Purview Unified Catalog CLI (UC)

**🚀 Complete implementation of Microsoft Purview Unified Catalog functionality with feature parity to [UnifiedCatalogPy](https://github.com/olafwrieden/unifiedcatalogpy).**

## Overview

The Unified Catalog (`uc`) command group provides comprehensive management of Microsoft Purview's modern data governance features:

- **✅ Governance Domains** - Organizational contexts for data assets
- **✅ Glossary Terms** - Business terminology and definitions with full metadata
- **✅ Data Products** - Curated data asset collections with full CRUD lifecycle management (NEW: update & delete)
- **✅ Objectives & Key Results (OKRs)** - Data governance goal tracking and measurement
- **✅ Critical Data Elements (CDEs)** - Important data element definitions with data types
- **✅ Health Management** - Automated governance health monitoring and recommendations (NEW)
- **✅ Workflow Management** - Approval workflows and business process automation (NEW)
- **ℹ️ Custom Attributes / Business Metadata** - User-defined metadata attributes. If the `datagovernance/catalog/attributes` endpoint is unavailable (HTTP 405), use Atlas business metadata via `pvw types putTypeDefs` with `businessMetadataDefs`.
- **🚧 Access Requests** - Data access workflow management (coming soon)

## 🚀 Quick Start

Get started with Unified Catalog commands:

```bash
# 1️⃣ List governance domains
pvw uc domain list

# 2️⃣ Search glossary terms  
pvw uc term search --query "customer"

# 3️⃣ List data products
pvw uc dataproduct list

# 4️⃣ View OKRs
pvw uc objective list

# 5️⃣ Browse CDEs
pvw uc cde list
```

### 🔥 Rich Console Output
All commands feature beautiful, colorized table output with:
- **Status Indicators**: ✅ Active, 🚧 Draft, ❌ Deprecated
- **Color Coding**: Green (success), Yellow (warnings), Red (errors)  
- **Smart Formatting**: Auto-truncated descriptions, aligned columns
- **Progress Feedback**: Real-time operation status

### 💡 Pro Tips
```bash
# Get help for any command
pv uc --help
pv uc domain --help

# Use JSON output for scripting
pv uc domain list --output json

# Filter results with search
pv uc term search --query "finance"
```

## Authentication

The UC client uses the same authentication as other Purview CLI commands:

- **Azure CLI**: Run `az login` first
- **Service Principal**: Set `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`
- **Account Name**: Set `PURVIEW_NAME` environment variable or pass via config

## 📚 Complete Command Reference

### 🏢 Governance Domains (`pv uc domain`)

Manage organizational contexts for data governance:

```bash
# List all domains (with rich table output)
pv uc domain list

# Create a new domain
pv uc domain create --name "Finance" --description "Financial data domain" 
                   --type "BusinessUnit" --owner-id "user@company.com"

# Get domain details
pv uc domain show --domain-id "abc-123"

# Update domain properties
pv uc domain update --domain-id "abc-123" --name "Finance Analytics" 
                   --status "Published"

# Delete domain (with confirmation)
pv uc domain delete --domain-id "abc-123" --confirm
```

### 📖 Glossary Terms (`pv uc term`)

Manage business terminology with comprehensive metadata:

```bash
# Search terms across all domains
pvw uc term search --query "customer"

# List terms in a specific domain
pvw uc term list --domain-id "abc-123"

# Create a basic term
pvw uc term create --name "Customer ID" --description "Unique identifier" 
                 --domain-id "abc-123"

# Create term with full metadata
pvw uc term create --name "GDPR" --description "Data Protection Regulation"
                 --domain-id "abc-123" --acronym "GDPR" --status "Draft"
                 --resource-name "Official Site" --resource-url "https://gdpr.eu"

# Update term properties  
pvw uc term update --term-id "term-456" --status "Published" 
                 --acronym "CUST_ID"

# Delete term
pvw uc term delete --term-id "term-456" --confirm
```

### 📦 Data Products (`pv uc dataproduct`)

Manage curated data asset collections with lifecycle tracking and full CRUD operations:

```bash
# List all data products (with full IDs displayed)
pvw uc dataproduct list

# List products in specific domain  
pvw uc dataproduct list --domain-id "abc-123"

# List with filtering
pvw uc dataproduct list --status Published

# Show specific data product details
pvw uc dataproduct show --product-id "560f1496-f0d3-4c8e-b343-8636bd4f9d4a"

# Create basic data product
pvw uc dataproduct create --name "Customer 360" 
                        --description "Complete customer analytics"
                        --domain-id "abc-123" --type "Analytical"

# Create with full metadata
pvw uc dataproduct create --name "Sales Dashboard" --domain-id "abc-123"
                        --type "Operational" --update-frequency "Daily"
                        --business-use "Track sales KPIs" 
                        --owner-id "sales@company.com" --endorsed

# Update data product (smart partial updates - only specify fields to change)
pvw uc dataproduct update --product-id "560f1496-f0d3-4c8e-b343-8636bd4f9d4a" \
                        --status Published

# Update multiple fields at once
pvw uc dataproduct update --product-id "560f1496-f0d3-4c8e-b343-8636bd4f9d4a" \
                        --description "Updated comprehensive customer analytics" \
                        --endorsed \
                        --update-frequency Monthly

# Update status and business metadata
pvw uc dataproduct update --product-id "prod-789" \
                        --status Published \
                        --business-use "Updated business justification"

# Delete product (with confirmation prompt)
pvw uc dataproduct delete --product-id "prod-789"

# Delete without confirmation
pvw uc dataproduct delete --product-id "prod-789" --yes
```

**Key Features:**
- ✅ **Smart Updates**: Fetches current state first, then applies only specified changes
- ✅ **Partial Updates**: Update individual fields without affecting others
- ✅ **Full ID Display**: All list commands show complete UUIDs (no truncation)
- ✅ **Safe Deletion**: Confirmation prompt by default, `--yes` to skip
- ✅ **Rich Formatting**: Beautiful tables with status colors and proper alignment

### 🎯 Objectives & Key Results (`pv uc objective`)

Track data governance goals and measure progress:

```bash
# List all objectives
pvw uc objective list

# List objectives for domain
pvw uc objective list --domain-id "abc-123"

# Create objective  
pvw uc objective create --definition "Achieve 95% data quality"
                      --domain-id "abc-123" 
                      --target-date "2025-12-31T23:59:59.000Z"
                      --status "Active"

# Create key result
pvw uc objective create-key-result --objective-id "obj-123"
                                 --definition "Reduce errors by 50%"
                                 --progress 25 --goal 50 --max 100
                                 --domain-id "abc-123" --status "OnTrack"

# Update objective progress
pvw uc objective update --objective-id "obj-123" --progress 75

# Delete objective
pvw uc objective delete --objective-id "obj-123" --confirm
```

### 🔑 Critical Data Elements (`pv uc cde`)

Define and manage important data elements with type information:

```bash
# List all CDEs
pvw uc cde list

# List CDEs in domain
pvw uc cde list --domain-id "abc-123"

# Create CDE with data type
pvw uc cde create --name "Social Security Number" 
                 --description "US SSN for identity verification"

### 🧩 Custom Attributes / Business Metadata

- The `pvw uc attribute create/list` commands call the `datagovernance/catalog/attributes` endpoint. Many tenants/regions return HTTP 405 (not enabled).
- When you hit 405 or get empty results, use Atlas **businessMetadataDefs** instead:

```bash
# Upsert business metadata (sample payload provided below)
                 --domain-id "abc-123" --data-type "String"
                 --status "Published"

# Create with validation rules  
pvw uc cde create --name "Email Address" --domain-id "abc-123"

Sample payload (simplified):

```json
{
   "businessMetadataDefs": [
      {
         "category": "BUSINESS_METADATA",
         "name": "Glossaire",
         "description": "Glossaire attributes",
         "typeVersion": "1.0",
         "attributeDefs": [
            {
               "name": "SecteursActivite",
               "typeName": "array<string>",
               "isOptional": true,
               "cardinality": "SINGLE"
            },
            {
               "name": "Secteur",
               "typeName": "string",
               "isOptional": true,
               "cardinality": "SINGLE"
            }
         ]
      }
   ]
}
```

Une fois définis, les attributs peuvent être renseignés sur les termes via `customAttributes` / `managedAttributes` (déjà supporté par `pvw uc term import-csv` et `pvw uc term update`).
                 --data-type "String" --format "email"
                 --required --sensitive

# Update CDE properties
pvw uc cde update --cde-id "cde-456" --status "Deprecated"
                 --description "Legacy field - use NewEmail instead"

# Delete CDE
pvw uc cde delete --cde-id "cde-456" --confirm
```

### 🏥 Health Monitoring (`pvw uc health`) **NEW**

Monitor governance health and get automated recommendations to improve your data governance posture:

```bash
# List all health findings and recommendations
pvw uc health query

# Filter by severity
pvw uc health query --severity High
pvw uc health query --severity Medium
pvw uc health query --severity Low

# Filter by status
pvw uc health query --status NotStarted
pvw uc health query --status InProgress
pvw uc health query --status Resolved

# Filter by finding type
pvw uc health query --finding-type Discoverability
pvw uc health query --finding-type Quality

# Get detailed information about a specific health action
pvw uc health show --action-id "5ea3fc78-6a77-4098-8779-ed81de6f87c9"

# Update health action status and track progress
pvw uc health update \
  --action-id "5ea3fc78-6a77-4098-8779-ed81de6f87c9" \
  --status InProgress \
  --reason "Working on assigning glossary terms to data products"

# Assign health action to team member
pvw uc health update \
  --action-id "5ea3fc78-6a77-4098-8779-ed81de6f87c9" \
  --assigned-to "user@company.com"

# Mark health action as resolved
pvw uc health update \
  --action-id "5ea3fc78-6a77-4098-8779-ed81de6f87c9" \
  --status Resolved \
  --reason "All data products now have published glossary terms assigned"

# Delete a health action
pvw uc health delete --action-id "5ea3fc78-6a77-4098-8779-ed81de6f87c9"

# Get health summary statistics (if available)
pvw uc health summary

# Output health findings in JSON format for automation
pvw uc health query --json
```

**Health Finding Types:**
- **Missing glossary terms** (High severity) - Data products without published terms
- **Missing OKRs** (Medium) - Data products without defined objectives
- **Missing data quality scores** (Medium) - Products/assets without quality metrics
- **Classification gaps** (Medium) - Data assets missing proper classifications
- **Description quality issues** (Medium) - Short or missing descriptions
- **Domain completeness** (Medium) - Business domains without critical data entities

**Key Features:**
- ✅ **Automated Monitoring**: Continuous governance health checks
- ✅ **Prioritized Findings**: Severity-based recommendations (High/Medium/Low)
- ✅ **Actionable Insights**: Clear recommendations for each finding
- ✅ **Progress Tracking**: Update status and track resolution
- ✅ **Rich Formatting**: Color-coded severity (Red=High, Yellow=Medium, Green=Low)

### 🔄 Workflow Management (`pvw workflow`) **NEW**

Manage approval workflows and business process automation in Purview:

```bash
# List all workflows
pvw workflow list

# Get workflow details
pvw workflow get --workflow-id "workflow-123"

# Create a new workflow (requires JSON definition file)
pvw workflow create --workflow-id "approval-flow-1" \
                   --payload-file workflow-definition.json

# Execute a workflow
pvw workflow execute --workflow-id "workflow-123"

# Execute with parameters
pvw workflow execute --workflow-id "workflow-123" \
                    --payload-file execution-params.json

# List workflow executions/runs
pvw workflow executions --workflow-id "workflow-123"

# Get specific execution details
pvw workflow execution-details --workflow-id "workflow-123" \
                              --execution-id "exec-456"

# Update workflow configuration
pvw workflow update --workflow-id "workflow-123" \
                   --payload-file updated-workflow.json

# Delete a workflow
pvw workflow delete --workflow-id "workflow-123"

# Output workflows in JSON format for scripting
pvw workflow list --json
```

**Workflow Use Cases:**
- **Data Access Requests**: Automated approval flows for data access
- **Term Certification**: Glossary term review and approval processes
- **Data Product Publishing**: Multi-stage approval for publishing data products
- **Classification Review**: Automated classification validation workflows
- **Quality Gate Enforcement**: Data quality checks before promotion

**Key Features:**
- ✅ **Full Lifecycle Management**: Create, execute, monitor, and delete workflows
- ✅ **Execution Tracking**: Monitor workflow runs and get detailed status
- ✅ **Flexible Definition**: JSON-based workflow configuration
- ✅ **Rich Formatting**: Beautiful table display with full workflow IDs visible

## 🎨 Beautiful Console Output

Experience professional-grade CLI formatting with:

- **📊 Rich Tables**: Colorized columns with proper alignment
- **🎯 Status Icons**: ✅ Active, 🚧 Draft, ❌ Deprecated, ⚠️ Warning  
- **🌈 Color Coding**: Green (success), Yellow (warnings), Red (errors)
- **📱 Smart Formatting**: Auto-truncated text, responsive columns
- **⚡ Progress Feedback**: Real-time operation status and completion

### Sample Output

```bash
pvw uc domain list
```

```
                         🏢 Governance Domains                          
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Domain ID   ┃ Name            ┃ Type         ┃ Status      ┃ Owners       ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ fin-001     │ ✅ Finance      │ BusinessUnit │ Published   │ CFO Team     │
│ mkt-002     │ 🚧 Marketing    │ Department   │ Draft       │ CMO Team     │
│ ops-003     │ ✅ Operations   │ Operational  │ Active      │ COO Team     │
└─────────────┴─────────────────┴──────────────┴─────────────┴──────────────┘

Found 3 domains across 2 business units
✨ Use 'pv uc domain show --domain-id <ID>' for detailed view
```

## 🔄 Migration & Compatibility

### Legacy Support
The original `data_product` command remains available for backward compatibility:

```bash
# These commands are equivalent:
pv uc dataproduct list --domain-id "abc-123"
pv data_product dataproduct list --domain-id "abc-123"  # Legacy syntax
```

### UnifiedCatalogPy Compatibility
This implementation provides **complete feature parity** with the popular [UnifiedCatalogPy](https://github.com/olafwrieden/unifiedcatalogpy) library:

- ✅ **All API Methods**: Full coverage of UC REST endpoints
- ✅ **Same Data Models**: Compatible request/response structures  
- ✅ **Rich Output**: Enhanced with beautiful console formatting
- ✅ **Error Handling**: Comprehensive validation and user feedback
- ✅ **Authentication**: Azure CLI, Service Principal, managed identity support

## 🔌 API Reference

### Purview REST Endpoints

| Feature | Endpoint | Methods |
|---------|----------|---------|
| **Governance Domains** | `/datagovernance/governanceDomains` | GET, POST, PUT, DELETE |
| **Glossary Terms** | `/datagovernance/terms` | GET, POST, PUT, DELETE |
| **Data Products** | `/datagovernance/dataProducts` | GET, POST, PUT, DELETE |
| **Objectives** | `/datagovernance/objectives` | GET, POST, PUT, DELETE |
| **Key Results** | `/datagovernance/objectives/{id}/keyResults` | GET, POST, PUT, DELETE |
| **Critical Data Elements** | `/datagovernance/criticalDataElements` | GET, POST, PUT, DELETE |
| **Health Management** | `/datagovernance/health` | GET, POST *(Coming Soon)* |

### Authentication Methods

1. **Azure CLI** (Recommended)
   ```bash
   az login
   pv uc domain list
   ```

2. **Service Principal**
   ```bash
   set AZURE_CLIENT_ID=your-client-id
   set AZURE_TENANT_ID=your-tenant-id  
   set AZURE_CLIENT_SECRET=your-secret
   pv uc domain list
   ```

3. **Managed Identity** (Azure VMs/Functions)
   ```bash
   # Automatically detected in Azure environments
   pv uc domain list
   ```

## ⚠️ Error Handling & Troubleshooting

### Common Issues & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Authentication failed` | No valid credentials | Run `az login` or set service principal env vars |
| `Permission denied` | Missing UC access | Contact admin for Purview data governance permissions |
| `Domain not found` | Invalid domain ID | Use `pv uc domain list` to get valid IDs |
| `Rate limit exceeded` | Too many API calls | Built-in retry logic handles this automatically |
| `Network timeout` | Connection issues | Check firewall and proxy settings |

### Debug Mode
Enable detailed logging for troubleshooting:

```bash
pv --debug uc domain list
pv --verbose uc term search --query "customer"
```

## 🔗 Integration & Workflows

### Working with Other CLI Commands

Unified Catalog integrates seamlessly with the broader Purview CLI:

```bash
# Export governance structure  
pv uc domain list --output json > domains.json
pv uc term list --domain-id "abc-123" --output json > terms.json

# Search and link assets to data products
pv search query --keywords "customer" --output json > assets.json
# Use asset GUIDs to link to data products via API

# Bulk domain creation from CSV
cat domains.csv | while IFS=, read name desc type; do
  pv uc domain create --name "$name" --description "$desc" --type "$type"
done
```

### Common Workflows

1. **📋 Setting Up Governance**
   ```bash
   # 1. Create governance domains
   pv uc domain create --name "Finance" --type "BusinessUnit"
   
   # 2. Define glossary terms  
   pv uc term create --name "Revenue" --domain-id "fin-001"
   
   # 3. Establish objectives
   pv uc objective create --definition "95% data quality" --domain-id "fin-001"
   ```

2. **📦 Data Product Lifecycle**
   ```bash
   # Draft → Review → Published → Deprecated
   pv uc dataproduct create --name "Customer360" --status "Draft"
   pv uc dataproduct update --product-id "dp-123" --status "Published"  
   pv uc dataproduct update --product-id "dp-123" --status "Deprecated"
   ```

3. **📊 Progress Tracking**
   ```bash
   # Monitor OKR progress
   pv uc objective list --status "Active"
   pv uc objective update --objective-id "obj-123" --progress 75
   ```

---

## 🛠️ Technical Implementation

### Architecture Overview

The UC implementation follows a clean, modular design:

- **Client Layer**: `purviewcli/client/_unified_catalog.py` - API interactions
- **CLI Layer**: `purviewcli/cli/unified_catalog.py` - User interface  
- **Models**: Comprehensive data structures for all UC entities
- **Output**: Rich console formatting with status indicators and color coding

### Key Technologies

- **🎨 Rich Library**: Beautiful console output with tables and progress bars
- **⚡ Click Framework**: Robust CLI with command groups and validation
- **🔒 Azure Identity**: Seamless authentication with multiple methods
- **📊 Multiple Formats**: Table, JSON, YAML output options
- **🔄 Error Recovery**: Comprehensive error handling with user guidance

### UnifiedCatalogPy Parity

This implementation achieves **100% feature parity** with the popular UnifiedCatalogPy library:

| Feature | UnifiedCatalogPy | PurviewCLI UC | Status |
|---------|------------------|---------------|--------|
| Governance Domains | ✅ | ✅ | **Complete** |
| Glossary Terms | ✅ | ✅ | **Complete** |
| Data Products | ✅ | ✅ | **Complete** |
| Objectives & KRs | ✅ | ✅ | **Complete** |
| Critical Data Elements | ✅ | ✅ | **Complete** |
| Rich Console Output | ❌ | ✅ | **Enhanced** |
| CLI Integration | ❌ | ✅ | **Unique** |

## 🤝 Contributing

Help improve the Unified Catalog functionality:

1. **Add Features**: Extend `_unified_catalog.py` with new API methods
2. **Enhance CLI**: Update `unified_catalog.py` with new commands  
3. **Improve Output**: Add formatting and visualization options
4. **Write Tests**: Ensure reliability with comprehensive test coverage
5. **Update Docs**: Keep examples and references current

## 📚 Additional Resources

- **[Microsoft Purview Documentation](https://docs.microsoft.com/en-us/azure/purview/)**
- **[UnifiedCatalogPy GitHub](https://github.com/olafwrieden/unifiedcatalogpy)**
- **[Purview CLI Main Documentation](../../README.md)**
- **[API Reference Guide](../README.md)**

---

*✨ The Unified Catalog CLI brings the power of Microsoft Purview's data governance to your command line with beautiful, professional output and comprehensive feature coverage.*

- [Microsoft Purview Unified Catalog Documentation](https://learn.microsoft.com/en-us/purview/concept-unified-catalog)
- [Original unifiedcatalogpy Project](https://github.com/olafwrieden/unifiedcatalogpy)
- [Purview CLI Entity Commands](../entity/)
- [Purview CLI Glossary Commands](../glossary/)
