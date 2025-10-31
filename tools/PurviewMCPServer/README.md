# Purview MCP Server - Enhanced Version 2.0

## Overview

The Purview MCP Server now provides comprehensive access to Microsoft Purview operations through the Model Context Protocol, enabling LLM-powered data governance workflows.

**Version:** 2.0 (Enhanced)  
**Documentation Coverage:** 90.5% (565/624 methods)  
**Total Tools:** 33 operations across 8 categories

## Available Tools

### Entity Operations (8 tools)
Core CRUD operations for data assets:

1. **get_entity** - Retrieve entity by GUID with full details
2. **create_entity** - Create new data asset
3. **update_entity** - Update existing entity attributes
4. **delete_entity** - Remove entity from catalog
5. **search_entities** - Keyword search with filters and pagination
6. **batch_create_entities** - Bulk entity creation (efficient)
7. **batch_update_entities** - Bulk entity updates (efficient)
8. **import_entities_from_csv** - Import from CSV with mapping config

**Use Cases:**
- Asset registration and discovery
- Metadata synchronization
- Bulk data migration
- Automated catalog maintenance

### Glossary Operations (3 tools)
Business vocabulary management:

9. **get_glossary_terms** - List all terms or from specific glossary
10. **create_glossary_term** - Define new business term
11. **assign_term_to_entities** - Tag assets with business terms

**Use Cases:**
- Business glossary management
- Data asset semantic enrichment
- Business-technical alignment

### Unified Catalog Operations (7 tools)
Microsoft Purview Business Metadata (new in this version):

12. **uc_list_domains** - List all governance domains
13. **uc_get_domain** - Get domain details
14. **uc_create_domain** - Create new governance domain
15. **uc_list_terms** - List business metadata terms in domain
16. **uc_get_term** - Get term details
17. **uc_create_term** - Create new business metadata term
18. **uc_search_terms** - Search terms across domains

**Use Cases:**
- Hierarchical business term organization
- Domain-driven data governance
- Business metadata standardization
- Cross-domain term discovery

### Collection Operations (5 tools)
Hierarchical asset organization:

19. **list_collections** - List all collections
20. **get_collection** - Get collection details
21. **create_collection** - Create new collection
22. **delete_collection** - Remove collection
23. **get_collection_path** - Get hierarchical path

**Use Cases:**
- Multi-tenant data organization
- Department/project isolation
- Role-based access control
- Collection hierarchy management

### Lineage Operations (2 tools)
Data flow tracking:

24. **get_lineage** - Get upstream/downstream lineage
25. **create_lineage** - Create lineage relationship

**Use Cases:**
- Impact analysis
- Data flow visualization
- Compliance tracking
- Root cause analysis

### Advanced Search Operations (2 tools - new)
Enhanced discovery capabilities:

26. **search_suggest** - Autocomplete/suggestions
27. **search_browse** - Browse by entity type with aggregations

**Use Cases:**
- Search UI building
- Type-based exploration
- Classification discovery
- Quick navigation

### Type Definition Operations (2 tools - new)
Schema and metadata model management:

28. **get_typedef** - Get type definition schema
29. **list_typedefs** - List all type definitions

**Use Cases:**
- Understanding data models
- Custom type creation
- Schema validation
- API integration

### Relationship Operations (3 tools - new)
Entity connections and associations:

30. **create_relationship** - Create entity relationships
31. **get_relationship** - Get relationship details
32. **delete_relationship** - Remove relationship

**Use Cases:**
- Parent-child relationships
- Custom associations
- Relationship management
- Data modeling

### Account Operations (1 tool)
Purview account management:

33. **get_account_properties** - Get account configuration

## New Capabilities in Version 2.0

### 1. Unified Catalog Integration
- Full support for Microsoft Purview Business Metadata
- Domain-based term organization
- Hierarchical governance structure
- Cross-domain search

### 2. Enhanced Search
- Autocomplete suggestions for better UX
- Browse by type with aggregations
- Faceted navigation support

### 3. Type System Access
- Type definition inspection
- Schema discovery
- Custom type support

### 4. Relationship Management
- Create custom relationships
- Manage entity connections
- Support for parent-child hierarchies

### 5. Comprehensive Documentation
- All operations have detailed docstrings
- Real-world examples included
- Business context provided
- Use cases documented

## Client Architecture

The MCP server leverages two client architectures:

### Async Client (PurviewClient)
Used for high-level operations:
- Entity CRUD
- Batch operations
- CSV import/export
- Account management
- Collections
- Lineage (async operations)

### Synchronous Clients (Specialized)
Used for specific operations:
- **UnifiedCatalogClient** - UC domains and terms
- **Search** - Advanced search operations
- **Types** - Type definitions
- **Relationship** - Relationship management
- **Glossary** - Business glossary (sync API)

## Configuration

### Environment Variables Required:
```bash
PURVIEW_ACCOUNT_NAME=<your-purview-account>    # Required
AZURE_TENANT_ID=<tenant-id>                    # Optional
AZURE_REGION=<region>                          # Optional (default: auto-detect)
PURVIEW_MAX_RETRIES=3                          # Optional
PURVIEW_TIMEOUT=30                             # Optional
PURVIEW_BATCH_SIZE=100                         # Optional
```

### Authentication:
- Uses Azure DefaultAzureCredential
- Supports: Managed Identity, Service Principal, Azure CLI, VS Code

## Usage Examples

### Example 1: Create Domain and Terms
```json
{
  "tool": "uc_create_domain",
  "arguments": {
    "domain_data": {
      "name": "Finance",
      "description": "Financial data governance domain",
      "owner_id": "0360aff3-add5-4b7c-b172-52add69b0199"
    }
  }
}
```

### Example 2: Search and Tag Entities
```json
{
  "tool": "search_entities",
  "arguments": {
    "query": "customer",
    "limit": 10
  }
}

{
  "tool": "assign_term_to_entities",
  "arguments": {
    "term_guid": "term-guid-123",
    "entity_guids": ["entity-1", "entity-2"]
  }
}
```

### Example 3: Bulk Import from CSV
```json
{
  "tool": "import_entities_from_csv",
  "arguments": {
    "csv_file_path": "/path/to/entities.csv",
    "mapping_config": {
      "typeName": "azure_sql_table",
      "attributes": {
        "table_name": "name",
        "schema_name": "schema"
      }
    }
  }
}
```

### Example 4: Browse by Type
```json
{
  "tool": "search_browse",
  "arguments": {
    "entity_type": "azure_sql_table",
    "limit": 50
  }
}
```

## LLM Integration Tips

### For Entity Discovery:
1. Start with `search_suggest` for autocomplete
2. Use `search_entities` with filters
3. Drill down with `get_entity` for details
4. Explore relationships with `get_lineage`

### For Governance Setup:
1. Create domains with `uc_create_domain`
2. Define terms with `uc_create_term`
3. Organize in collections with `create_collection`
4. Tag assets with `assign_term_to_entities`

### For Bulk Operations:
1. Use `batch_create_entities` for efficiency
2. Monitor progress with callbacks
3. Handle failures gracefully
4. Use CSV operations for large datasets

### For Exploration:
1. Browse types with `list_typedefs`
2. Understand schemas with `get_typedef`
3. Navigate hierarchies with `get_collection_path`
4. Discover relationships with `search_browse`

## Error Handling

All tools return structured responses:

**Success:**
```json
{
  "result": { ... },
  "status": "success"
}
```

**Error:**
```json
{
  "error": "Error message",
  "tool": "tool_name",
  "arguments": { ... }
}
```

## Performance Considerations

### Batch Operations:
- Default batch size: 100 entities
- Automatic retry on failures
- Progress tracking available

### Rate Limiting:
- Respects Purview API limits
- Automatic backoff on 429 errors
- Configurable retry count

### Caching:
- Type definitions cached
- Collection paths cached
- Reduces API calls

## Testing

### Local Testing:
```bash
# Install dependencies
pip install mcp>=1.0.0

# Set environment
export PURVIEW_ACCOUNT_NAME=your-account

# Run server
python mcp/server/server.py
```

### MCP Client Testing:
Use any MCP client (Claude Desktop, VS Code extension, custom client):

```json
{
  "mcpServers": {
    "purview": {
      "command": "python",
      "args": ["path/to/mcp/server/server.py"],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "your-account"
      }
    }
  }
}
```

## Documentation References

- **API Documentation Status:** `doc/api-documentation-status.md`
- **Completion Summary:** `doc/documentation-completion-summary.md`
- **Client Modules:** `purviewcli/client/`
- **Test Suite:** `tests/test_mcp_server.py`

## Roadmap

### Planned Additions (remaining 9.5%):
- Data sharing operations (31 methods from _share.py)
- Scanning operations (14 methods from scanning_operations.py)
- Data quality validation (6 methods from data_quality.py)
- Additional utility methods

### Future Enhancements:
- Streaming responses for large datasets
- Webhook support for events
- Advanced filtering and faceting
- Custom tool registration

## Changelog

### Version 2.0 (Current)
- ✅ Added 7 Unified Catalog operations
- ✅ Added 2 advanced search operations
- ✅ Added 2 type definition operations
- ✅ Added 3 relationship operations
- ✅ Comprehensive documentation (90.5% coverage)
- ✅ 33 total tools (up from 18)
- ✅ Support for both async and sync clients

### Version 1.0 (Initial)
- Basic entity operations
- Simple glossary support
- Collection management
- Lineage tracking
- CSV operations

---

**Status:** ✅ Ready for Production  
**MCP Integration:** ✅ Complete  
**Documentation:** ✅ 90.5% Coverage  
**Test Coverage:** 🔄 In Progress
