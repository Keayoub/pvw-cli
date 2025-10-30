# Purview MCP Server

A Model Context Protocol (MCP) server that integrates Microsoft Purview with Large Language Models (LLMs) and AI assistants. This enables natural language interactions with Microsoft Purview for data governance and catalog management.

## Overview

The Purview MCP Server wraps the `purviewcli` Python library to provide a standardized interface for AI assistants like Claude Desktop, Cline, and other MCP-compatible tools. It exposes 20+ Purview operations as tools that LLMs can discover and use to automate data governance workflows.

### Key Features

- **18+ Purview Tools** - Entity, lineage, collection, glossary, CSV, and account operations
- **Natural Language Interface** - Ask questions like "Search for SQL entities" or "Create a new collection"
- **Azure Authentication** - Seamless authentication using Azure DefaultAzureCredential
- **Async/Await** - Efficient async operations for better performance
- **Error Handling** - Graceful error handling with detailed logging
- **Stdio Communication** - Standard MCP protocol via stdio for wide compatibility

## Installation

### Prerequisites

1. Python 3.8 or later
2. Azure CLI (for authentication): `az login`
3. Access to a Microsoft Purview account

### Install Dependencies

```bash
cd mcp
pip install -r requirements.txt
```

**Note:** The MCP server requires the parent `pvw-cli` package. Install it with:

```bash
# From the repository root
pip install -e .

# Or from PyPI
pip install pvw-cli
```

## Configuration

### Required Environment Variables

- `PURVIEW_ACCOUNT_NAME` - Your Purview account name (required)

### Optional Environment Variables

- `AZURE_TENANT_ID` - Azure tenant ID (optional, auto-detected from Azure CLI)
- `AZURE_REGION` - Azure region: `commercial` (default), `china`, or `usgov`
- `PURVIEW_MAX_RETRIES` - Maximum retry attempts for API calls (default: 3)
- `PURVIEW_TIMEOUT` - Request timeout in seconds (default: 30)
- `PURVIEW_BATCH_SIZE` - Batch size for bulk operations (default: 100)

### Setting Environment Variables

**Windows CMD:**
```cmd
set PURVIEW_ACCOUNT_NAME=your-purview-account
set AZURE_TENANT_ID=your-tenant-id
```

**PowerShell:**
```powershell
$env:PURVIEW_ACCOUNT_NAME = "your-purview-account"
$env:AZURE_TENANT_ID = "your-tenant-id"
```

**Linux/macOS:**
```bash
export PURVIEW_ACCOUNT_NAME=your-purview-account
export AZURE_TENANT_ID=your-tenant-id
```

## Running the Server

### Standalone Mode

Test the server in standalone mode:

```bash
cd mcp
python server.py
```

The server will start and listen for MCP protocol messages via stdio.

### With Claude Desktop

Add to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "purview": {
      "command": "python",
      "args": ["/path/to/pvw-cli/mcp/server.py"],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "your-purview-account",
        "AZURE_TENANT_ID": "your-tenant-id"
      }
    }
  }
}
```

Restart Claude Desktop and you'll see Purview tools available in the tools menu.

### With Cline (VS Code Extension)

Add to Cline's MCP settings (`.cline/mcp_settings.json` in your workspace):

```json
{
  "mcpServers": {
    "purview": {
      "command": "python",
      "args": ["/path/to/pvw-cli/mcp/server.py"],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "your-purview-account"
      }
    }
  }
}
```

Restart VS Code and Cline will discover the Purview tools.

## Available Tools

### Entity Operations

1. **get_entity** - Get entity details by GUID
2. **create_entity** - Create a new entity
3. **update_entity** - Update an existing entity
4. **delete_entity** - Delete an entity by GUID
5. **search_entities** - Search entities with filters and facets
6. **batch_create_entities** - Create multiple entities in batches
7. **batch_update_entities** - Update multiple entities in batches

### Lineage Operations

8. **get_lineage** - Get entity lineage (upstream/downstream)
9. **create_lineage** - Create a lineage relationship

### Collection Operations

10. **list_collections** - List all collections
11. **get_collection** - Get collection details by name
12. **create_collection** - Create a new collection
13. **delete_collection** - Delete a collection
14. **get_collection_path** - Get hierarchical path of a collection

### Glossary Operations

15. **get_glossary_terms** - Get all glossary terms
16. **create_glossary_term** - Create a new glossary term
17. **assign_term_to_entities** - Assign a term to multiple entities

### CSV Operations

18. **import_entities_from_csv** - Import entities from CSV file
19. **export_entities_to_csv** - Export entities to CSV file

### Account Operations

20. **get_account_properties** - Get Purview account properties

## Usage Examples

### Example 1: Search for Entities

**Natural Language:** "Search for all SQL Server tables"

**LLM will call:**
```json
{
  "tool": "search_entities",
  "arguments": {
    "query": "SQL Server",
    "limit": 50
  }
}
```

### Example 2: Get Entity Lineage

**Natural Language:** "Show me the lineage for entity with GUID abc-123"

**LLM will call:**
```json
{
  "tool": "get_lineage",
  "arguments": {
    "guid": "abc-123",
    "direction": "BOTH",
    "depth": 3
  }
}
```

### Example 3: Create a Collection

**Natural Language:** "Create a collection named 'Data Science' under the root collection"

**LLM will call:**
```json
{
  "tool": "create_collection",
  "arguments": {
    "collection_name": "data-science",
    "collection_data": {
      "friendlyName": "Data Science",
      "description": "Data science datasets and models",
      "parentCollection": {
        "referenceName": "root"
      }
    }
  }
}
```

### Example 4: Export Entities to CSV

**Natural Language:** "Export all Azure SQL entities to a CSV file"

**LLM will call:**
```json
{
  "tool": "export_entities_to_csv",
  "arguments": {
    "query": "Azure SQL",
    "csv_file_path": "/tmp/azure_sql_entities.csv",
    "columns": ["guid", "typeName", "attr_name", "attr_qualifiedName"]
  }
}
```

### Example 5: Batch Create Entities

**Natural Language:** "Create 5 dataset entities for my new project"

**LLM will call:**
```json
{
  "tool": "batch_create_entities",
  "arguments": {
    "entities": [
      {
        "typeName": "DataSet",
        "attributes": {
          "name": "dataset1",
          "qualifiedName": "dataset1@account"
        }
      },
      // ... more entities
    ]
  }
}
```

## Authentication

The MCP server uses Azure DefaultAzureCredential for authentication, which supports multiple authentication methods in order:

1. **Environment Variables** - AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET
2. **Managed Identity** - For Azure VMs, App Services, etc.
3. **Azure CLI** - Run `az login` first (recommended for development)
4. **Visual Studio Code** - Authenticated Azure account in VS Code
5. **Interactive Browser** - Falls back to browser-based login

### Setup Authentication

**Recommended for Development (Azure CLI):**
```bash
az login
```

**Service Principal (for automation):**
```bash
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
```

## Troubleshooting

### Error: "PURVIEW_ACCOUNT_NAME environment variable is required"

**Solution:** Set the `PURVIEW_ACCOUNT_NAME` environment variable before running the server.

### Error: "Authentication failed"

**Solution:** 
1. Ensure you're logged in with Azure CLI: `az login`
2. Check your Azure credentials have access to the Purview account
3. Verify the tenant ID if specified

### Error: "mcp package not installed"

**Solution:** Install the MCP package:
```bash
pip install mcp>=1.0.0
```

### Error: "No module named 'purviewcli'"

**Solution:** Install the parent package:
```bash
pip install -e /path/to/pvw-cli
# Or from PyPI
pip install pvw-cli
```

### Server Not Responding

**Solutions:**
1. Check server logs (stderr output)
2. Verify environment variables are set correctly
3. Test Purview connectivity manually using pvw-cli commands
4. Ensure Python version is 3.8 or later

### Tool Execution Failures

**Solutions:**
1. Check the error message in the tool response
2. Verify the input parameters match the tool schema
3. Test the equivalent pvw-cli command manually
4. Check Azure permissions for the operation

## Development

### Project Structure

```
mcp/
├── server.py          # Main MCP server implementation
├── package.json       # MCP server metadata
├── requirements.txt   # Python dependencies
├── __init__.py       # Package initialization
└── README.md         # This file
```

### Adding New Tools

To add a new Purview operation as an MCP tool:

1. Add the tool definition to `list_tools()` in `server.py`
2. Add the tool execution logic to `_execute_tool()` in `server.py`
3. Ensure the corresponding method exists in `PurviewClient`
4. Update this README with the new tool documentation

### Testing

Test individual tools by running the server and sending MCP protocol messages:

```bash
# Start the server
python server.py

# In another terminal, send test messages (requires MCP client)
# Or use Claude Desktop/Cline for interactive testing
```

### Logging

The server logs to stderr by default. Adjust logging level in `server.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

## Architecture

```
┌─────────────────┐
│   LLM/AI Tool   │ (Claude, Cline, etc.)
└────────┬────────┘
         │ MCP Protocol (stdio)
         ▼
┌─────────────────┐
│ Purview MCP     │
│    Server       │
└────────┬────────┘
         │ Python API
         ▼
┌─────────────────┐
│ PurviewClient   │ (purviewcli.client.api_client)
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│ Microsoft       │
│   Purview       │
└─────────────────┘
```

## Security Considerations

- **Credentials:** Never commit credentials to version control
- **Permissions:** Ensure the authenticated account has appropriate Purview permissions
- **Logging:** Be cautious about logging sensitive data
- **Network:** Use secure networks when connecting to Purview
- **Rate Limiting:** The server respects Purview API rate limits with retry logic

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see the parent repository for full license text.

## Support

- **Issues:** https://github.com/Keayoub/pvw-cli/issues
- **Documentation:** https://github.com/Keayoub/pvw-cli/wiki
- **Main CLI:** https://github.com/Keayoub/pvw-cli

## Changelog

### Version 1.0.0 (October 2025)

- Initial release
- 20+ Purview operations exposed as MCP tools
- Support for entity, lineage, collection, glossary, CSV, and account operations
- Azure authentication via DefaultAzureCredential
- Async/await pattern for efficient operations
- Comprehensive error handling and logging
- Compatible with Claude Desktop, Cline, and other MCP clients

## Acknowledgments

- Built on top of the excellent [pvw-cli](https://github.com/Keayoub/pvw-cli) project
- Uses the [Model Context Protocol](https://modelcontextprotocol.io/) standard
- Powered by [Microsoft Purview](https://azure.microsoft.com/en-us/services/purview/)
