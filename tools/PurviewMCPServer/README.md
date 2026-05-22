# Purview MCP Server (tools)

This folder contains the FastMCP server implementation for the Purview CLI and a set of resources to help LLMs interact with the server.

## Prompt Instructions

- `prompt_instructions.md` — Curated prompt templates and best practices for prompting the MCP server.
- The server exposes an MCP tool, `get_prompt_instructions()`, which returns the file contents so agents can fetch guidance programmatically.

## Fetching Prompts (Example)

- Call the tool `get_prompt_instructions()` via the MCP server API to retrieve the latest prompt guidance.

## Notes

- Ensure environment variables (e.g., `PURVIEW_ACCOUNT_NAME`) are set before running the server.
- See `server.py` for available MCP tools and their usage.

## Purview MCP Server - Enhanced Version 2.0

## Overview

The Purview MCP Server now provides comprehensive access to Microsoft Purview operations through the Model Context Protocol, enabling LLM-powered data governance workflows with **built-in prompt instructions** for AI assistants.

**Version:** 2.0 (Enhanced)  
**Documentation Coverage:** 90.5% (565/624 methods)  
**Total Tools:** 37 curated operations across 8 categories, plus the live operation registry  
**🆕 Feature:** Comprehensive prompt instructions embedded in MCP server

## 🎯 New: Built-in Prompt Instructions

The MCP server now includes **comprehensive prompt instructions** automatically provided to AI assistants through the FastMCP `instructions` parameter. This ensures optimal usage of the Purview CLI client.

The server also exposes `list_available_operations()` and `invoke_operation()` so new Purview client methods are reachable without waiting for a manual MCP refresh.

**What's Included:**

- ✅ Core capabilities overview for all 6 operation categories
- ✅ Best practices for entity operations, glossary, lineage, search
- ✅ Common workflows with step-by-step guidance
- ✅ CSV bulk operation patterns and templates
- ✅ QualifiedName format patterns for different entity types
- ✅ Error handling strategies and recovery patterns
- ✅ API coverage summary (86% Unified Catalog)
- ✅ Tips for LLM usage and chaining operations

**Benefits:**

- 🚀 AI assistants automatically understand Purview client capabilities
- 📚 No need to manually explain CLI features to AI
- 🎯 Best practices enforced from first interaction
- ⚡ Faster workflow creation with built-in patterns
- 🔧 Error handling guidance reduces troubleshooting time

**Documentation:**

- Embedded instructions: In FastMCP server initialization
- Standalone reference: `PROMPT_INSTRUCTIONS.md` (comprehensive guide)
- Quick reference: This README

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

1. **get_glossary_terms** - List all terms or from specific glossary
2. **create_glossary_term** - Define new business term
3. **assign_term_to_entities** - Tag assets with business terms

**Use Cases:**

- Business glossary management
- Data asset semantic enrichment
- Business-technical alignment

### Unified Catalog Operations (11 tools)

Microsoft Purview Business Metadata (new in this version):

1. `uc_list_domains` - List all governance domains
2. `uc_get_domain` - Get domain details
3. `uc_create_domain` - Create new governance domain
4. `uc_list_terms` - List business metadata terms in domain
5. `uc_get_term` - Get term details
6. `uc_create_term` - Create new business metadata term
7. `uc_search_terms` - Search terms across domains
8. `uc_list_custom_metadata_defs` - List business metadata definitions and attributes
9. `uc_cleanup_metadata_definition` - Resolve/check/delete metadata definition safely
10. `uc_delete_metadata_definition` - Delete business metadata definition by name
11. `uc_delete_metadata_from_asset` - Remove metadata group assignment from an asset

**Use Cases:**

- Hierarchical business term organization
- Domain-driven data governance
- Business metadata standardization
- Cross-domain term discovery
- Expired metadata cleanup and definition lifecycle management

### Collection Operations (5 tools)

Hierarchical asset organization:

1. **list_collections** - List all collections
2. **get_collection** - Get collection details
3. **create_collection** - Create new collection
4. **delete_collection** - Remove collection
5. **get_collection_path** - Get hierarchical path

**Use Cases:**

- Multi-tenant data organization
- Department/project isolation
- Role-based access control
- Collection hierarchy management

### Lineage Operations (2 tools)

Data flow tracking:

1. **get_lineage** - Get upstream/downstream lineage
2. **create_lineage** - Create lineage relationship

**Use Cases:**

- Impact analysis
- Data flow visualization
- Compliance tracking
- Root cause analysis

### Advanced Search Operations (2 tools - new)

Enhanced discovery capabilities:

1. **search_suggest** - Autocomplete/suggestions
2. **search_browse** - Browse by entity type with aggregations

**Use Cases:**

- Search UI building
- Type-based exploration
- Classification discovery
- Quick navigation

### Type Definition Operations (2 tools - new)

Schema and metadata model management:

1. **get_typedef** - Get type definition schema
2. **list_typedefs** - List all type definitions

**Use Cases:**

- Understanding data models
- Custom type creation
- Schema validation
- API integration

### Relationship Operations (3 tools - new)

Entity connections and associations:

1. **create_relationship** - Create entity relationships
2. **get_relationship** - Get relationship details
3. **delete_relationship** - Remove relationship

**Use Cases:**

- Parent-child relationships
- Custom associations
- Relationship management
- Data modeling

### Account Operations (1 tool)

Purview account management:

1. **get_account_properties** - Get account configuration

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

For detailed Claude Code setup instructions, including local-checkout and direct
`uvx` launch examples, see `docs/purview-mcp-server.md`.

When configuring any client, make sure these values are set in the MCP server
environment:

- `PURVIEW_ACCOUNT_NAME`
- `PURVIEW_ACCOUNT_ID`
- `AZURE_TENANT_ID`

Transport configuration is environment-driven:

- `PURVIEW_MCP_TRANSPORT` (default: `stdio`; supported: `stdio`, `streamable-http`, `sse`, `http`)
- `PURVIEW_MCP_HOST` (default: `127.0.0.1`)
- `PURVIEW_MCP_PORT` (default: `8000`)

For Streamable HTTP clients, use `http://127.0.0.1:8000/mcp`.
For SSE clients, use `http://127.0.0.1:8000/sse`.

Prefer a read-only smoke test first, such as `list_available_operations()`.

### Environment Variables Required

```bash
PURVIEW_ACCOUNT_NAME=<your-purview-account>    # Required
AZURE_TENANT_ID=<tenant-id>                    # Optional
AZURE_REGION=<region>                          # Optional (default: auto-detect)
PURVIEW_MAX_RETRIES=3                          # Optional
PURVIEW_TIMEOUT=30                             # Optional
PURVIEW_BATCH_SIZE=100                         # Optional
```

### Authentication

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

### For Entity Discovery

1. Start with `search_suggest` for autocomplete
2. Use `search_entities` with filters
3. Drill down with `get_entity` for details
4. Explore relationships with `get_lineage`

### For Governance Setup

1. Create domains with `uc_create_domain`
2. Define terms with `uc_create_term`
3. Organize in collections with `create_collection`
4. Tag assets with `assign_term_to_entities`

### For Bulk Operations

1. Use `batch_create_entities` for efficiency
2. Monitor progress with status updates
3. Handle failures gracefully
4. Use CSV operations for large datasets

### For Exploration

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

### Batch Operations

- Default batch size: 100 entities
- Automatic retry on failures
- Progress tracking available

### Rate Limiting

- Respects Purview API limits
- Automatic backoff on 429 errors
- Configurable retry count

### Caching

- Type definitions cached
- Collection paths cached
- Reduces API calls

## Testing

### Local Testing

```bash
# Install from source with pip
pip install -e .
pip install -e tools/PurviewMCPServer

# Run server
pvw-mcp
```

### Install with `uv` (recommended)

```bash
# Install as a persistent CLI tool
uv tool install --from "git+https://github.com/Keayoub/pvw-cli.git#subdirectory=tools/PurviewMCPServer" pvw-mcp

# Or run without installing
uvx --from "git+https://github.com/Keayoub/pvw-cli.git#subdirectory=tools/PurviewMCPServer" pvw-mcp
```

### Run with `npx`

```bash
# npx launcher (uses pvw-mcp if already installed, otherwise uvx)
npx -y chat.mcp.purview
```

Optional: override the `uv` source used by the `npx` launcher.

```bash
PVW_MCP_UV_FROM="pvw-mcp-server" npx -y chat.mcp.purview
```

PowerShell equivalent:

```powershell
$env:PVW_MCP_UV_FROM = "pvw-mcp-server"
npx -y chat.mcp.purview
```

### MCP Client Testing

Use any MCP client (Claude Desktop, VS Code extension, custom client):

```json
{
  "mcpServers": {
    "purview": {
      "command": "npx",
      "args": ["-y", "chat.mcp.purview"],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "your-account"
      }
    }
  }
}
```

Alternative configuration using `uvx` directly:

```json
{
  "mcpServers": {
    "purview": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Keayoub/pvw-cli.git#subdirectory=tools/PurviewMCPServer",
        "pvw-mcp"
      ],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "your-account"
      }
    }
  }
}
```

### Python SDK with `uvx`

Install the Python MCP SDK first:

```bash
uv pip install mcp
```

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server = StdioServerParameters(
    command="uvx",
    args=[
        "--from",
        "git+https://github.com/Keayoub/pvw-cli.git#subdirectory=tools/PurviewMCPServer",
        "pvw-mcp",
    ],
    env={"PURVIEW_ACCOUNT_NAME": "your-account"},
)

async with stdio_client(server) as (read_stream, write_stream):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()
        tools = await session.list_tools()
        print(tools)
```

## Prompt Instructions Quick Reference

The MCP server automatically provides these instructions to AI assistants:

### Core Capabilities Covered

1. **Entity Operations** - CRUD, bulk operations, CSV import/export
2. **Glossary Management** - Terms, categories, assignments
3. **Unified Catalog** - Domains, business metadata, policies, relationships
4. **Data Lineage** - Trace data flow, create lineage relationships
5. **Search & Discovery** - Keyword, faceted, browse operations
6. **Collections & Account** - Hierarchy, permissions, configuration

### Common Workflows Included

- Catalog New Data Source (5 steps)
- Build Business Glossary (5 steps)
- Implement Data Governance (6 steps)
- Data Discovery (5 steps)
- Bulk Data Onboarding (5 steps)

### Best Practices Embedded

- ✅ Always use qualifiedName for updates
- ✅ Preview CSV imports with dry-run
- ✅ Appropriate batch sizes based on volume
- ✅ Error handling with error CSV files
- ✅ Validate entities before operations
- ✅ Start with domains for UC operations
- ✅ Use Process entities for lineage

### QualifiedName Patterns

- **Azure SQL**: `mssql://server/database/schema/table`
- **ADLS Gen2**: `https://account.dfs.core.windows.net/container/path`
- **Generic**: `//source/path/asset@account`

### For More Details

- **Full Instructions**: See `PROMPT_INSTRUCTIONS.md` (comprehensive 650+ lines)
- **Embedded**: Automatically provided to AI assistants via FastMCP
- **Examples**: Real-world workflow patterns with tool calls

## Documentation References

- **Prompt Instructions:** `PROMPT_INSTRUCTIONS.md` (NEW - comprehensive guide)
- **API Documentation Status:** `doc/api-documentation-status.md`
- **Completion Summary:** `doc/documentation-completion-summary.md`
- **Client Modules:** `purviewcli/client/`
- **Test Suite:** `tests/test_mcp_server.py`
- **Purview CLI Docs:** `doc/` (full CLI documentation)

## Roadmap

### Planned Additions (remaining 9.5%)

- Data sharing operations (31 methods from _share.py)
- Scanning operations (14 methods from scanning_operations.py)
- Data quality validation (6 methods from data_quality.py)
- Additional utility methods

### Future Enhancements

- Streaming responses for large datasets
- Webhook support for events
- Advanced filtering and faceting
- Enhanced prompt engineering with usage examples
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
