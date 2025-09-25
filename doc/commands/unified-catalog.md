# Microsoft Purview Unified Catalog CLI (UC)

**🚀 Complete implementation of Microsoft Purview Unified Catalog functionality with feature parity to [UnifiedCatalogPy](https://github.com/olafwrieden/unifiedcatalogpy).**

## Overview

The Unified Catalog (`uc`) command group provides comprehensive management of Microsoft Purview's modern data governance features:

- **✅ Governance Domains** - Organizational contexts for data assets
- **✅ Glossary Terms** - Business terminology and definitions with full metadata
- **✅ Data Products** - Curated data asset collections with lifecycle management
- **✅ Objectives & Key Results (OKRs)** - Data governance goal tracking and measurement
- **✅ Critical Data Elements (CDEs)** - Important data element definitions with data types
- **🚧 Health Management** - Data quality controls and actions (preview/coming soon)
- **🚧 Custom Attributes** - User-defined metadata attributes (coming soon)
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

Manage curated data asset collections with lifecycle tracking:

```bash
# List all data products
pvw uc dataproduct list

# List products in specific domain  
pvw uc dataproduct list --domain-id "abc-123"

# Create basic data product
pvw uc dataproduct create --name "Customer 360" 
                        --description "Complete customer analytics"
                        --domain-id "abc-123" --type "Analytical"

# Create with full metadata
pvw uc dataproduct create --name "Sales Dashboard" --domain-id "abc-123"
                        --type "Operational" --update-frequency "Daily"
                        --business-use "Track sales KPIs" 
                        --owner-id "sales@company.com" --endorsed

# Update product status
pvw uc dataproduct update --product-id "prod-789" --status "Published"

# Delete product  
pvw uc dataproduct delete --product-id "prod-789" --confirm
```

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
                 --domain-id "abc-123" --data-type "String"
                 --status "Published"

# Create with validation rules  
pvw uc cde create --name "Email Address" --domain-id "abc-123"
                 --data-type "String" --format "email"
                 --required --sensitive

# Update CDE properties
pvw uc cde update --cde-id "cde-456" --status "Deprecated"
                 --description "Legacy field - use NewEmail instead"

# Delete CDE
pvw uc cde delete --cde-id "cde-456" --confirm
```

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
