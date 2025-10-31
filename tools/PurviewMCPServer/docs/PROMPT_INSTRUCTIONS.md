# Microsoft Purview MCP Server - Prompt Instructions

This document provides comprehensive guidelines for AI assistants and users working with the Microsoft Purview MCP Server to maximize the effectiveness of the Purview CLI client.

## Overview

The Purview MCP Server provides **86% API coverage** of Microsoft Purview's Unified Catalog, offering comprehensive access to data governance, catalog management, and metadata operations through 50+ tools.

## Core Capabilities

### 1. Data Catalog Management (Entity Operations)

Manage Atlas entities representing data assets in your organization:

**Key Operations:**
- `get_entity` - Retrieve entity by GUID with full metadata
- `create_entity` - Register new data assets
- `update_entity` - Modify entity attributes
- `delete_entity` - Remove entities from catalog
- `batch_create_entities` - Bulk entity creation
- `batch_update_entities` - Bulk entity updates
- `search_entities` - Search catalog with filters
- `import_entities_from_csv` - Bulk import from CSV
- `export_entities_to_csv` - Bulk export to CSV

**Entity Types:**
- `DataSet` - Generic dataset/file
- `azure_sql_table` - Azure SQL table
- `azure_sql_column` - Azure SQL column
- `azure_datalake_gen2_path` - ADLS Gen2 folder/file
- `Process` - ETL job, transformation, pipeline
- `Column` - Generic column

**Best Practices:**
1. Always use `qualifiedName` as the unique identifier for updates
2. Specify `typeName` when creating entities
3. Use batch operations for bulk work (more efficient)
4. Test CSV imports with dry-run before applying
5. Use appropriate batch sizes:
   - Small (< 100 entities): 50-100
   - Medium (100-1000): 100-200
   - Large (> 1000): 200-500

**Example Workflow:**
```
1. search_entities("customer data") - Check if exists
2. create_entity({typeName: "DataSet", attributes: {...}}) - Register asset
3. assign_term_to_entities - Link business terms
4. create_lineage - Define data flow
```

### 2. Business Glossary (Glossary Operations)

Manage business terminology and vocabulary:

**Key Operations:**
- `get_glossary_terms` - List all terms or by glossary
- `create_glossary_term` - Create new term with metadata
- `assign_term_to_entities` - Link terms to entities

**Best Practices:**
1. Create hierarchies using parent-child relationships
2. Add rich metadata (acronyms, resources, contacts)
3. Link terms to entities for discoverability
4. Use status workflow: Draft → Approved → Alert → Expired

**Example:**
```
1. create_glossary_term({name: "Customer ID", definition: "..."})
2. Create related terms (synonyms, hierarchies)
3. assign_term_to_entities - Link to data assets
```

### 3. Unified Catalog (Modern Governance Features)

Microsoft Purview's modern data governance framework:

**Governance Domains:**
- `uc_list_domains` - List all governance domains
- `uc_get_domain` - Get domain details
- `uc_create_domain` - Create new domain
- Organize governance by business domain (Finance, Sales, HR)

**Business Metadata Terms:**
- `uc_list_terms` - List terms in a domain
- `uc_get_term` - Get term details
- `uc_create_term` - Create standardized vocabulary
- `uc_search_terms` - Search across all domains

**Best Practices:**
1. **Start with domains** - Create organizational structure first
2. **Use business metadata terms** - Build standardized vocabulary
3. **Link relationships** - Connect UC resources to physical entities
4. **Query with filters** - Use advanced OData queries
5. **Manage policies** - Define governance and RBAC policies

**Example Governance Workflow:**
```
1. uc_create_domain({name: "Finance", description: "..."})
2. uc_create_term({name: "Revenue", definition: "...", domain_id: "..."})
3. Search for related entities
4. Link term to entities via relationships
5. uc_policy_create - Define access policies
```

### 4. Data Lineage

Trace data flow and dependencies:

**Key Operations:**
- `get_lineage` - Get upstream/downstream lineage
- `create_lineage` - Define process with inputs/outputs
- `import_lineage_from_csv` - Bulk lineage creation

**Best Practices:**
1. Use **Process entities** to represent transformations
2. Define clear inputs and outputs
3. Use meaningful process names (describe the transformation)
4. CSV import for bulk lineage relationships
5. Validate entities exist before creating lineage

**Lineage Directions:**
- `INPUT` - Upstream dependencies (data sources)
- `OUTPUT` - Downstream consumers (derived datasets)
- `BOTH` - Complete data flow (default)

### 5. Search & Discovery

Find and discover data assets:

**Key Operations:**
- `search_entities` - Keyword search with filters
- `search_browse` - Browse by entity type hierarchy
- `search_suggest` - Get search suggestions

**Best Practices:**
1. Start broad, then filter (keyword + filters)
2. Use entity types for scoping (DataSet, Table, Column)
3. Leverage classifications (PII, Confidential)
4. Browse for hierarchical exploration

**Search Patterns:**
```
1. search_entities({query: "customer", limit: 50})
2. Filter by type, classification, collection
3. get_entity - Get detailed information
4. get_lineage - Understand data flow
5. get_glossary_terms - View business context
```

### 6. Collections & Account

Organize and manage Purview account:

**Key Operations:**
- `list_collections` - List collection hierarchy
- `get_collection` - Get collection details
- `create_collection` - Create new collection
- `delete_collection` - Remove collection
- `get_collection_path` - Get hierarchical path
- `get_account_properties` - Account configuration

## Common Workflows

### Workflow 1: Catalog New Data Source
```
Goal: Register new data assets in the catalog

Steps:
1. search_entities({query: "customer_db"}) 
   → Check if assets already exist
   
2. create_entity({
     typeName: "azure_sql_table",
     attributes: {
       qualifiedName: "mssql://server/db/schema/table",
       name: "Customers"
     }
   })
   → Register the data asset
   
3. create_glossary_term({name: "Customer", definition: "..."})
   → Define business terms if needed
   
4. assign_term_to_entities({term_guid: "...", entity_guids: ["..."]})
   → Link terms to entities
   
5. create_lineage({...}) (if applicable)
   → Define data flow relationships
```

### Workflow 2: Build Business Glossary
```
Goal: Create standardized business vocabulary

Steps:
1. uc_list_domains()
   → Review existing governance domains
   
2. uc_create_domain({
     name: "Finance",
     description: "Financial data domain",
     owner_id: "user@company.com"
   })
   → Create domain structure
   
3. uc_create_term({
     domain_id: "...",
     name: "Revenue",
     definition: "Total income from sales",
     owner_id: "user@company.com"
   })
   → Add business metadata terms
   
4. search_entities({query: "sales revenue"})
   → Find related data assets
   
5. Link terms to entities via relationships
   → Connect vocabulary to physical assets
```

### Workflow 3: Implement Data Governance
```
Goal: Establish governance framework

Steps:
1. uc_list_domains()
   → Review domain structure
   
2. uc_create_domain({...}) (if needed)
   → Create governance domains
   
3. uc_create_term({...})
   → Define governance terminology
   
4. Create data products (curated collections)
   → Organize governed data assets
   
5. Define policies for access control
   → Implement RBAC and governance rules
   
6. Link relationships to physical entities
   → Connect governance to catalog
```

### Workflow 4: Data Discovery
```
Goal: Find and understand data assets

Steps:
1. search_entities({query: "customer sales", limit: 50})
   → Keyword search
   
2. search_browse({entity_type: "azure_sql_table"})
   → Browse by type hierarchy
   
3. get_entity({guid: "..."})
   → Get detailed entity information
   
4. get_lineage({guid: "...", direction: "BOTH", depth: 3})
   → Understand data flow
   
5. get_glossary_terms()
   → View business context and assigned terms
```

### Workflow 5: Bulk Data Onboarding
```
Goal: Import large numbers of entities

Steps:
1. Prepare CSV file with entity data
   → Follow CSV template format
   
2. import_entities_from_csv({
     csv_file_path: "entities.csv",
     mapping_config: {...}
   }) with validation
   → Preview changes (dry-run)
   
3. import_entities_from_csv({...})
   → Execute import
   
4. import_lineage_from_csv({...}) (if applicable)
   → Add lineage relationships
   
5. export_entities_to_csv({...})
   → Export results for validation
```

## CSV Bulk Operations

The CLI provides extensive CSV support for automation:

### CSV Templates

**Entity Import Templates:**
- `basic` - Basic entity attributes (typeName, qualifiedName, name, description)
- `etl` - ETL process entities with inputs/outputs
- `column-mapping` - Column-level mapping

### CSV Format for Entities

**Mode 1: Create-or-Update (by typeName + qualifiedName)**
```csv
typeName,qualifiedName,displayName,description,owner,source,collection
DataSet,//storage/sales.csv@account,Sales Data,Monthly sales,data-team,ERP,sales
azure_sql_table,mssql://server/db/schema/table,Orders,Order data,dba-team,SQL,finance
```

**Mode 2: Update by GUID (Partial Updates)**
```csv
guid,displayName,description,owner
abc-123-def-456,Updated Sales Data,New description,new-owner
def-456-ghi-789,Updated Customer Data,New description,customer-owner
```

### CSV Best Practices

1. **Always use dry-run first** - Preview changes before applying
2. **Use appropriate batch sizes** - Adjust based on data volume
3. **Handle errors with error CSV** - Save failed rows for retry
4. **Validate qualifiedNames** - Export existing entities first
5. **Use collections properly** - Organize assets logically

## QualifiedName Patterns

QualifiedName is the unique identifier for entities. Format varies by type:

### Azure SQL
```
mssql://server.database.windows.net/database/schema/table
mssql://server.database.windows.net/database/schema/table#column
```

### Azure Data Lake Storage Gen2
```
https://account.dfs.core.windows.net/container/path/to/file
https://account.dfs.core.windows.net/container/folder/
```

### Generic/Custom
```
//source/path/to/asset@account
//source/database/schema/table@instance
```

## Error Handling

### Common Issues and Solutions

**404 Not Found**
- Entity/term doesn't exist
- Check GUID/ID is correct
- Verify entity was created successfully

**400 Bad Request**
- Invalid payload structure
- Check required fields are provided
- Validate data types match schema

**403 Forbidden**
- Insufficient permissions
- Check RBAC assignments
- Verify collection access

**409 Conflict**
- Entity already exists
- Use update instead of create
- Check qualifiedName uniqueness

**429 Too Many Requests**
- Rate limited by API
- Reduce batch size
- Add delays between requests

### Recovery Strategies

1. **Use error CSV files** - Track and retry failed operations
2. **Reduce batch sizes** - Start with smaller batches
3. **Validate before operations** - Check entity existence
4. **Check permissions** - Verify RBAC access
5. **Review logs** - Enable debug mode for details

## Advanced Features

### Business Metadata
- Attach custom business context to entities
- Supported scopes: Entity, Column, Classification
- Use `add_or_update_business_metadata` tool
- Requires proper applicableEntityTypes configuration

### Relationships API
- Link data products to physical entities
- Connect CDEs to columns with qualified names
- Create associations between UC and Atlas resources
- Support for bulk relationship operations

### Query APIs
- Advanced OData filtering: `$filter`, `$top`, `$skip`
- Multi-criteria searches across resources
- Pagination support for large result sets
- Complex queries with multiple predicates

### Custom Attributes
- Create extensible attribute definitions
- Define custom properties for UC resources
- Organization-specific metadata extensions
- Type-safe attribute validation

## API Coverage Summary

The server provides **86% coverage** of Purview Unified Catalog APIs (45/52 operations):

| Resource Type | Coverage | Operations | Status |
|--------------|----------|------------|---------|
| Business Domains | 100% | 5/5 | ✅ Complete |
| Data Products | 90% | 9/10 | ⚠️ 1 missing |
| Glossary Terms | 73% | 8/11 | ⚠️ 3 missing |
| OKRs | 92% | 11/12 | ⚠️ 1 missing |
| CDEs | 90% | 9/10 | ⚠️ 1 missing |
| Policies | 100% | 5/5 | ✅ Complete |
| Relationships | 100% | 6/6 | ✅ Complete |
| Query | 100% | 4/4 | ✅ Complete |
| Custom Metadata | 100% | 5/5 | ✅ Complete |
| Custom Attributes | 100% | 5/5 | ✅ Complete |

## Output Formats

Available output formats for commands:

- **JSON** - Structured data for programmatic processing
- **JSONC** - JSON with comments for readability
- **Table** - Human-readable console output (default)
- **CSV** - Bulk data export for Excel/analysis

## Microsoft Learn Integration

The server includes Microsoft Learn documentation tools:

- `search_learn_microsoft_content` - Search official Microsoft docs
- `get_learn_microsoft_content` - Get specific documentation pages
- `get_learn_microsoft_modules` - Browse learning modules
- `get_learn_microsoft_paths` - Explore learning paths

Use these to supplement Purview operations with official Microsoft guidance and best practices.

## Authentication & Configuration

### Environment Variables

Set these environment variables for configuration:

**Required:**
- `PURVIEW_ACCOUNT_NAME` - Your Purview account name

**Optional:**
- `AZURE_TENANT_ID` - Azure tenant ID
- `AZURE_REGION` - Azure region (for special clouds: china, usgov)
- `PURVIEW_MAX_RETRIES` - Max retry attempts (default: 3)
- `PURVIEW_TIMEOUT` - Request timeout in seconds (default: 30)
- `PURVIEW_BATCH_SIZE` - Default batch size (default: 100)

### Authentication Methods

The client uses Azure DefaultAzureCredential, supporting:

1. **Azure CLI** - Run `az login` first
2. **Service Principal** - Set `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_SECRET`
3. **Managed Identity** - Automatic in Azure environments
4. **Interactive Browser** - Fallback for development

## Tips for AI Assistants

1. **Chain operations logically** - Combine search → get → update workflows
2. **Use bulk operations** - More efficient than individual API calls
3. **Validate assumptions** - Check entity existence before operations
4. **Leverage search first** - Discover before creating duplicates
5. **Use UC for modern governance** - Unified Catalog provides richer features
6. **Preview with dry-run** - Always test bulk operations before execution
7. **Export for analysis** - Use CSV exports for data validation
8. **Follow naming conventions** - Consistent qualifiedNames ensure reliability
9. **Handle errors gracefully** - Implement retry logic with exponential backoff
10. **Document decisions** - Explain reasoning when making data governance choices

## Examples

### Example 1: Register New Azure SQL Table
```
Tool: create_entity
Parameters:
{
  "entity_data": {
    "typeName": "azure_sql_table",
    "attributes": {
      "qualifiedName": "mssql://sqlserver.database.windows.net/salesdb/dbo/customers",
      "name": "customers",
      "description": "Customer master data table",
      "owner": "data-team@company.com"
    }
  }
}
```

### Example 2: Search and Assign Term
```
Step 1 - Search entities:
Tool: search_entities
Parameters: {query: "customer", limit: 20}

Step 2 - Create glossary term:
Tool: create_glossary_term
Parameters: {
  term_data: {
    name: "Customer",
    description: "Individual or organization that purchases products"
  }
}

Step 3 - Assign term:
Tool: assign_term_to_entities
Parameters: {
  term_guid: "term-guid-from-step-2",
  entity_guids: ["entity-guid-from-step-1"]
}
```

### Example 3: Create Governance Domain
```
Tool: uc_create_domain
Parameters:
{
  "name": "Finance",
  "description": "Financial data governance domain",
  "owner_id": "finance-lead@company.com"
}
```

### Example 4: Bulk Import Entities
```
Tool: import_entities_from_csv
Parameters:
{
  "csv_file_path": "/path/to/entities.csv",
  "mapping_config": {
    "typeName": "DataSet",
    "template": "basic"
  }
}
```

### Example 5: Get Lineage
```
Tool: get_lineage
Parameters:
{
  "guid": "entity-guid",
  "direction": "BOTH",
  "depth": 3
}
```

## Reference Documentation

For detailed documentation, refer to:

- **Main README**: `README.md` - Overview and quick start
- **Command Reference**: `doc/commands/` - Per-command documentation
- **User Guides**: `doc/guides/` - Step-by-step tutorials
- **Examples**: `samples/` - Sample code and scenarios
- **API Documentation**: Auto-generated API docs

## Support

- **GitHub Issues**: [https://github.com/Keayoub/Purview_cli/issues](https://github.com/Keayoub/Purview_cli/issues)
- **Email**: keayoub@msn.com

---

**Version**: 1.2.5  
**Last Updated**: October 31, 2025  
**API Coverage**: 86% (45/52 Unified Catalog operations)
