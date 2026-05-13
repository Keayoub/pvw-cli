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
