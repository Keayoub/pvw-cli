# Purview CLI - Unified Catalog Quick Reference Guide
**Version**: 1.10.25  
**Date**: April 27, 2026

This guide provides quick access to all Unified Catalog commands available in pvw-cli.

---

## 🚀 Getting Started

```bash
# Install or upgrade to latest version
pip install --upgrade pvw-cli

# Verify installation
pvw --version

# Get help
pvw uc --help
```

---

## 📚 Glossary Terms Commands

### Basic Operations

```bash
# List all terms
pvw uc term list

# Get specific term by ID
pvw uc term get --term-id <guid>

# Create a new term
pvw uc term create --name "Customer" --description "Person who purchases products"

# Update a term
pvw uc term update --term-id <guid> --description "Updated description"

# Delete a term
pvw uc term delete --term-id <guid>
```

### Advanced Term Operations

```bash
# Query terms with filters
pvw uc term query --filter "name eq 'Customer'"

# Display glossary hierarchy as tree
pvw uc term hierarchy

# Get hierarchy with max depth
pvw uc term hierarchy --max-depth 3

# Include draft terms in hierarchy
pvw uc term hierarchy --include-draft

# Get term facets (statistics)
pvw uc term facets

# List relationships for a term
pvw uc term relationships --term-id <guid>

# Filter relationships by type
pvw uc term relationships --term-id <guid> --relationship-type Synonym
```

### Bulk Import Terms

```bash
# Import terms from CSV
pvw uc term import-csv --file terms.csv

# Export terms to CSV template
pvw uc term export-csv --output terms_export.csv
```

---

## 🏢 Business Domains Commands

### Basic Operations

```bash
# List all domains
pvw uc domain list

# Get specific domain
pvw uc domain get --domain-id <guid>

# Create a domain
pvw uc domain create --name "Sales" --description "Sales department domain"

# Update a domain
pvw uc domain update --domain-id <guid> --description "Updated description"

# Delete a domain
pvw uc domain delete --domain-id <guid>
```

---

## 📦 Data Products Commands

### Basic Operations

```bash
# List all data products
pvw uc dataproduct list

# Get specific data product
pvw uc dataproduct get --product-id <guid>

# Create a data product
pvw uc dataproduct create --name "Customer 360" --description "Complete customer view"

# Update a data product
pvw uc dataproduct update --product-id <guid> --status Active

# Delete a data product
pvw uc dataproduct delete --product-id <guid>
```

### Advanced Product Operations

```bash
# Query data products
pvw uc dataproduct query --filter "status eq 'Active'"

# Get data product facets
pvw uc dataproduct facets

# List product relationships
pvw uc dataproduct list-relationships --product-id <guid>

# Create product relationship
pvw uc dataproduct create-relationship --product-id <guid> --target-id <target-guid>
```

---

## 🔒 Critical Data Elements (CDE) Commands

### Basic Operations

```bash
# List all CDEs
pvw uc cde list

# Get specific CDE
pvw uc cde get --cde-id <guid>

# Create a CDE
pvw uc cde create --name "SSN" --description "Social Security Number"

# Update a CDE
pvw uc cde update --cde-id <guid> --criticality-level High

# Delete a CDE
pvw uc cde delete --cde-id <guid>
```

### Advanced CDE Operations

```bash
# Query CDEs with filters
pvw uc cde query --filter "criticalityLevel eq 'High'"

# Get CDE facets (compliance/criticality statistics)
pvw uc cde facets

# List CDE relationships
pvw uc cde list-relationships --cde-id <guid>

# Create CDE relationship
pvw uc cde create-relationship --cde-id <guid> --target-id <target-guid>
```

---

## 🎯 Objectives & Key Results (OKRs) Commands

### Objectives

```bash
# List all objectives
pvw uc objective list

# Get specific objective
pvw uc objective get --objective-id <guid>

# Create an objective
pvw uc objective create --name "Q2 Data Quality" --description "Improve data quality"

# Update an objective
pvw uc objective update --objective-id <guid> --status "In Progress"

# Delete an objective
pvw uc objective delete --objective-id <guid>

# Query objectives
pvw uc objective query --filter "status eq 'Active'"

# Get objective facets
pvw uc objective facets
```

### Key Results

```bash
# List key results for an objective
pvw uc keyresult list --objective-id <guid>

# Get specific key result
pvw uc keyresult get --objective-id <guid> --keyresult-id <guid>

# Create a key result
pvw uc keyresult create --objective-id <guid> --name "80% data completeness"

# Update a key result
pvw uc keyresult update --objective-id <guid> --keyresult-id <guid> --progress 75

# Delete a key result
pvw uc keyresult delete --objective-id <guid> --keyresult-id <guid>
```

---

## ✅ Data Quality Commands

### Domain Quality Reporting

```bash
# List business domains (for quality)
pvw uc quality domains --account <account-id>

# Get domain quality report
pvw uc quality domain-report --account <account-id> --domainId <domain-id>

# List domain data sources
pvw uc quality data-sources --account <account-id> --domainId <domain-id>

# List domain quality schedules
pvw uc quality schedules --account <account-id> --domainId <domain-id>

# List domain quality alerts
pvw uc quality alerts --account <account-id> --domainId <domain-id>

# List domain assets with quality scores
pvw uc quality assets --account <account-id> --domainId <domain-id>

# Get quality score for a domain
pvw uc quality score domain --account <account-id> --domainId <domain-id>
```

### Quality Connections

```bash
# List quality connections
pvw uc quality list-connections --account <account-id>

# Get specific connection
pvw uc quality get-connection --account <account-id> --connectionId <conn-id>

# Create quality connection
pvw uc quality create-connection --account <account-id> --payloadFile connection.json

# Update quality connection
pvw uc quality update-connection --account <account-id> --connectionId <conn-id>

# Delete quality connection
pvw uc quality delete-connection --account <account-id> --connectionId <conn-id>
```

---

## 🔧 Common Options

All commands support these common options:

```bash
# Output as JSON
--output json

# Specify Purview account
--account <account-name>

# Use a specific profile
--profile <profile-name>

# Verbose output for debugging
--debug
```

---

## 💡 Useful Patterns

### Export and Reimport Terms

```bash
# Export terms to CSV
pvw uc term list --output json > terms_backup.json

# Export with specific fields
pvw uc term export-csv --output terms_template.csv

# Modify CSV and import
pvw uc term import-csv --file terms_modified.csv
```

### Bulk Operations with JSON

```bash
# Create multiple terms from JSON file
pvw uc term create --payloadFile terms_bulk.json

# Update multiple entities
pvw uc dataproduct update --product-id <guid> --payloadFile update.json
```

### Filtering and Querying

```bash
# Query with OData filter
pvw uc term query --filter "status eq 'Active' and domain eq 'Sales'"

# Pagination
pvw uc term list --skip 0 --top 50

# Sort results
pvw uc term list --orderby "name asc"
```

### Cross-Entity Relationships

```bash
# Link term to data product
pvw uc term relationships --term-id <term-guid> --entity-type DATAPRODUCT

# View all relationships for a product
pvw uc dataproduct list-relationships --product-id <product-guid>
```

---

## 📊 Data Quality Workflow Example

```bash
# 1. Get your account ID
ACCOUNT_ID="your-purview-account-id"

# 2. List available domains
pvw uc quality domains --account $ACCOUNT_ID

# 3. Get quality report for a domain
DOMAIN_ID="domain-guid-from-step-2"
pvw uc quality domain-report --account $ACCOUNT_ID --domainId $DOMAIN_ID

# 4. Check data sources in domain
pvw uc quality data-sources --account $ACCOUNT_ID --domainId $DOMAIN_ID

# 5. Review quality alerts
pvw uc quality alerts --account $ACCOUNT_ID --domainId $DOMAIN_ID

# 6. Get asset quality scores
pvw uc quality assets --account $ACCOUNT_ID --domainId $DOMAIN_ID --limit 100

# 7. Export quality report as JSON
pvw uc quality domain-report --account $ACCOUNT_ID --domainId $DOMAIN_ID --output json > quality_report.json
```

---

## 🆘 Troubleshooting

### Authentication Issues

```bash
# Login with Azure CLI
az login

# Verify credentials
az account show

# Set default subscription
az account set --subscription <subscription-id>
```

### Account Discovery Issues

```bash
# Explicitly set account ID
export PURVIEW_ACCOUNT_ID="your-account-id"

# Set account name
export PURVIEW_NAME="your-purview-account-name"

# Set resource group
export PURVIEW_RESOURCE_GROUP="your-resource-group"
```

### Permission Issues

```bash
# Check your Purview roles:
# - Data Curator: Required for create/update/delete
# - Data Reader: Required for read operations
# - Data Source Administrator: Required for scanning operations

# Verify collection permissions
pvw collection get --collectionName <collection-name>
```

---

## � Advanced Operations (Phase 3)

### Entity Advanced Operations

```bash
# Get entity change history
pvw entity history --guid <entity-guid>
pvw entity history --guid <entity-guid> --output json

# Validate entity before creation/update
pvw entity validate --guid <entity-guid>
pvw entity validate --payload-file entity.json --type-name DataSet

# Show entity dependencies
pvw entity dependencies --guid <entity-guid>
pvw entity dependencies --guid <entity-guid> --output json

# Get entity usage statistics
pvw entity usage --guid <entity-guid>
pvw entity usage --guid <entity-guid> --output json

# Get entity audit events
pvw entity audit --guid <entity-guid>
```

### Lineage Advanced Operations

```bash
# Get upstream lineage (data sources)
pvw lineage upstream --guid <entity-guid>
pvw lineage upstream --guid <entity-guid> --depth 5
pvw lineage upstream --guid <entity-guid> --output json

# Get downstream lineage (data consumers)
pvw lineage downstream --guid <entity-guid>
pvw lineage downstream --guid <entity-guid> --depth 5
pvw lineage downstream --guid <entity-guid> --output json

# Get temporal lineage (historical changes)
pvw lineage temporal --guid <entity-guid>
pvw lineage temporal --guid <entity-guid> --start-time 2026-01-01T00:00:00Z --end-time 2026-04-01T00:00:00Z
pvw lineage temporal --guid <entity-guid> --output json

# Get impact analysis
pvw lineage impact --guid <entity-guid>
pvw lineage impact-report --guid <entity-guid> --output-file impact_report.json
```

---

## 📊 Analytics & Reporting Commands

### Account Analytics

```bash
# Get comprehensive account analytics
pvw account analytics

# View account analytics as JSON
pvw account analytics --output json

# Get resource usage statistics
pvw account usage

# Get resource usage as JSON
pvw account usage --output json

# View resource limits and quotas
pvw account limits

# Get limits as JSON
pvw account limits --output json
```

**Analytics Metrics**:
- Entity counts by type
- Collection statistics
- Storage usage metrics
- Activity trends
- API call counts and limits
- Active connections

### Collection Analytics

```bash
# Get analytics for all collections
pvw collections analytics

# Get analytics for specific collection
pvw collections analytics --collection-name my-collection

# View as JSON
pvw collections analytics --output json

# Specific collection JSON output
pvw collections analytics --collection-name my-collection --output json
```

**Collection Metrics**:
- Asset counts by type
- Hierarchy depth and breadth
- Data source distribution
- Access patterns
- Usage trends
- Total collections and depth

### Search Analytics

```bash
# Get search analytics
pvw search analytics

# View as JSON
pvw search analytics --output json
```

**Search Metrics**:
- Most searched terms
- Popular asset types
- Search success rates
- Query performance metrics
- Daily search volumes
- Search trends over time
- Peak usage hours
- Cache hit rates

---

## 📚 Additional Resources

- **Full Documentation**: See `doc/` folder in repository
- **API Reference**: [doc/API_GAPS_ANALYSIS.md](./API_GAPS_ANALYSIS.md)
- **Performance Guide**: [doc/PERFORMANCE_OPTIMIZATION_GUIDE.md](./PERFORMANCE_OPTIMIZATION_GUIDE.md)
- **Authentication Guide**: [doc/AUTHENTICATION_TROUBLESHOOTING.md](./AUTHENTICATION_TROUBLESHOOTING.md)
- **Sample Notebooks**: `samples/notebooks (basic)/` and `samples/notebooks (plus)/`

---

## 🔄 Recent Updates (v1.10.25+)

- ✅ **Data Quality APIs**: Full implementation of quality namespace (v1.10.25) 
- ✅ **Facets APIs**: All entity type facets (terms, products, CDEs, objectives)
- ✅ **Hierarchy API**: Glossary term hierarchy visualization
- ✅ **Relationships API**: Generic relationship listing
- ✅ **Sample Notebooks**: Basic and advanced quality command notebooks
- ✅ **Phase 3 Advanced Operations**: Entity history, validation, dependencies, usage (April 27, 2026)
- ✅ **Advanced Lineage**: Upstream, downstream, temporal lineage operations (April 27, 2026)
- ✅ **Phase 4 Analytics & Reporting**: Account, collection, and search analytics (April 27, 2026)

---

**Version**: 1.10.25+  
**Last Updated**: April 27, 2026  
**CLI Repository**: https://github.com/Keayoub/pvw-cli

