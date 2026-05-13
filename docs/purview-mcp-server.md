# Purview MCP Server

Use this guide to run and use the Purview MCP Server shipped in this repository.

## What It Is

The Purview MCP Server exposes Microsoft Purview operations through Model Context Protocol (MCP), so AI assistants can call curated tools for:

- Entity operations (create, read, update, delete, batch)
- Glossary operations
- Unified Catalog operations (domains and terms)
- Search, lineage, relationship, and collection operations
- Dynamic operation discovery via operation registry helpers

Server implementation location:

- `tools/PurviewMCPServer/server.py`

## Prerequisites

1. Python environment with project dependencies installed.
2. Azure authentication configured (for example, `az login`).
3. Required environment variables configured for your Purview account.

Minimum variables:

```bash
PURVIEW_ACCOUNT_NAME=<your-purview-account>
PURVIEW_ACCOUNT_ID=<your-tenant-id-guid>
```

## Start The Server

From repository root:

```bash
python tools/PurviewMCPServer/server.py
```

The server starts with FastMCP and exposes tools declared in `server.py`.

## MCP Server Config Template

Most MCP clients use the same logical schema: server name, command, args, and env.

Use this local Python config as the baseline:

```json
{
  "mcpServers": {
    "purview": {
      "command": "python",
      "args": ["tools/PurviewMCPServer/server.py"],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "<your-purview-account>",
        "PURVIEW_ACCOUNT_ID": "<your-tenant-id-guid>",
        "AZURE_TENANT_ID": "<your-tenant-id-guid>"
      }
    }
  }
}
```

If your client supports npm-based MCP launchers, this package form is also available:

```json
{
  "mcpServers": {
    "purview": {
      "command": "npx",
      "args": ["-y", "chat.mcp.purview"],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "<your-purview-account>",
        "PURVIEW_ACCOUNT_ID": "<your-tenant-id-guid>",
        "AZURE_TENANT_ID": "<your-tenant-id-guid>"
      }
    }
  }
}
```

## Client Setup

### VS Code + GitHub Copilot

1. Open MCP server settings from the VS Code MCP/Copilot UI.
2. Add a server named `purview` using the config template above.
3. Save, then restart the MCP connection.
4. In Copilot Chat, verify the tools are available by asking for available MCP tools.

### Cursor

1. Open Cursor MCP settings.
2. Add a new MCP server (`purview`) with the same command/args/env.
3. Reconnect MCP in Cursor.
4. Test with a read-only call such as listing available operations.

### Codex

1. Open Codex MCP configuration (UI or config file, depending on your Codex build).
2. Register the `purview` server with the same MCP schema shown above.
3. Restart the Codex agent session.
4. Verify by calling `list_available_operations` first.

### Claude Code

1. Open Claude Code MCP configuration.
2. Add `purview` with the same server configuration.
3. Restart or reload MCP servers in Claude Code.
4. Validate with read-only tools before write operations.

## How To Use It

Use an MCP-capable client/agent and connect it to this server process. Then call tools directly, for example:

- `get_entity`
- `search_entities`
- `uc_list_domains`
- `uc_create_term`
- `list_available_operations`
- `invoke_operation`

Recommended usage pattern:

1. Discover available tools and required inputs.
2. Start with read/search operations.
3. Validate IDs and names from read output.
4. Apply write operations.
5. Use bulk operations for large ingestion or migration.

## Recommended First Commands

Run these in order when testing a new MCP client setup:

```text
1) list_available_operations()
2) invoke_operation("search", "searchQuery", {"--keywords": "customer", "--limit": 5})
3) uc_list_custom_metadata_defs()
4) uc_cleanup_metadata_definition("<definition-or-attribute-name>", check_only=true)
```

For business metadata lifecycle operations now exposed in MCP:

- `uc_list_custom_metadata_defs`
- `uc_cleanup_metadata_definition`
- `uc_delete_metadata_definition`
- `uc_delete_metadata_from_asset`

## Example Workflow

```text
1) search_entities("customer")
2) get_entity(<guid>)
3) uc_list_domains()
4) uc_create_term(...)
5) create_lineage(...)
```

## Troubleshooting

- 401/403: Check Azure auth and permissions.
- 404: Validate GUID, term ID, domain ID, or type name.
- 429: Reduce request rate or batch size.
- If tools seem missing, restart the server and re-check operation registry tools.

## Related Docs

- [Unified Catalog guide](unified-catalog.md)
- [Unified Catalog commands](commands/unified-catalog.md)
- [Authentication troubleshooting](authentication-troubleshooting.md)
- [Performance guide](performance-optimization-guide.md)
