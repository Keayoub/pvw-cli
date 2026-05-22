# Purview MCP Server

> **Complete reference** — what it is, transport protocols, all client setups, Azure Functions hosting, every tool, prompt examples, and troubleshooting.

---

## Table of Contents

1. [What It Is](#what-it-is)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Environment Variables](#environment-variables)
5. [Transport Protocols](#transport-protocols)
6. [Quick Start](#quick-start)
7. [Client Setup](#client-setup)
   - [VS Code + GitHub Copilot](#vs-code--github-copilot)
   - [Claude Code](#claude-code)
   - [Cursor](#cursor)
   - [Any Other MCP Client](#any-other-mcp-client)
8. [Azure Functions Hosting](#azure-functions-hosting)
9. [Available Tools](#available-tools)
10. [Prompt Examples](#prompt-examples)
11. [Common Workflows](#common-workflows)
12. [Troubleshooting](#troubleshooting)
13. [Related Docs](#related-docs)

---

## What It Is

The **Purview MCP Server** exposes Microsoft Purview data governance operations through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/). It wraps the `pvw-cli` client library so that AI assistants (GitHub Copilot, Claude, Cursor, Codex) can:

- Discover, read, create, update, and delete Purview entities and relationships
- Manage business glossary terms and unified catalog domains
- Run bulk CSV imports and lineage creation
- Perform search, browse, and autocomplete queries
- Invoke any `pvw-cli` operation dynamically through the operation registry

**Implementation:** `tools/PurviewMCPServer/server.py`
**Config module:** `tools/PurviewMCPServer/config.py`
**Azure Functions host:** `tools/hosting/app/function_app.py`
**Tools:** 37 curated operations across 8 categories + live operation registry
**Protocol spec:** MCP v2025-03-26 (streamable-HTTP) / v2024-11-05 (SSE legacy)

---

## Architecture Overview

```
+------------------------------------------------------------------+
|  AI Client (VS Code Copilot / Claude / Cursor / Codex)          |
|                                                                  |
|  +---------------+  +------------------+  +------------------+  |
|  |  stdio        |  | streamable-HTTP  |  |  SSE (legacy)    |  |
|  |  (process)    |  | POST /mcp        |  |  GET /sse +      |  |
|  |               |  |                  |  |  POST /messages  |  |
|  +-------+-------+  +--------+---------+  +--------+---------+  |
+----------|-----------------------|-----------------------|-------+
           |                       |                       |
           v                       v                       v
+------------------------------------------------------------------+
|  server.py  (FastMCP >= 2.0)                                    |
|  PurviewMCPConfig.from_env()  transport / host / port           |
|  37 @mcp.tool() decorated functions                             |
+------------------------+-----------------------------------------+
                         |
         +---------------+---------------+
         v               v               v
  PurviewClient   UnifiedCatalogClient   pvw-cli CLI
  (async HTTPX)   (REST / UC API)        (operation registry)
         |               |               |
         +---------------+---------------+
                         |
                         v
           Microsoft Purview REST API
           (Atlas + Unified Catalog + Scan)
```

When deployed on **Azure Functions**, the ASGI layer sits between the Functions host and FastMCP:

```
VS Code --[POST /api/mcp]--> Azure Functions host (port 7073)
                                      |
                                AsgiMiddleware
                                      |
                           FastMCP http_app(path="/api/mcp")
                                      |
                                server.py tools
```

---

## Prerequisites

| Requirement | Details |
|---|---|
| Python 3.11+ | `python --version` |
| `pvw-cli` dependencies | `pip install -e .` from repo root |
| `pvw-mcp-server` package | `pip install -e tools/PurviewMCPServer` |
| Azure authentication | `az login` or service principal env vars |
| Purview account | `PURVIEW_ACCOUNT_NAME` env var |
| Azure Functions Core Tools v4 | Only for Azure Functions hosting mode |

---

## Environment Variables

Copy `tools/PurviewMCPServer/.env.example` to `.env` and fill in:

```bash
# -- Required ------------------------------------------------------------------
PURVIEW_ACCOUNT_NAME=<account-name>        # Without .purview.azure.com suffix

# -- Authentication ------------------------------------------------------------
# Option A: Azure CLI (az login) -- no extra vars needed
# Option B: Service Principal
AZURE_TENANT_ID=<tenant-guid>
AZURE_CLIENT_ID=<app-registration-client-id>
AZURE_CLIENT_SECRET=<secret>

# -- Optional client overrides -------------------------------------------------
AZURE_REGION=              # Sovereign cloud: "usgov", "china" (empty = public Azure)
PURVIEW_MAX_RETRIES=3      # Retry count for Purview API calls
PURVIEW_TIMEOUT=30         # Request timeout in seconds
PURVIEW_BATCH_SIZE=100     # Default batch size for bulk operations

# -- MCP transport (only needed for HTTP modes) --------------------------------
PURVIEW_MCP_TRANSPORT=stdio        # stdio | streamable-http | http | sse
PURVIEW_MCP_HOST=127.0.0.1         # Bind host for HTTP/SSE modes
PURVIEW_MCP_PORT=8000              # Bind port for HTTP/SSE modes
```

The server validates all values at startup and raises a clear `ValueError` for missing or invalid config.

---

## Transport Protocols

The server supports three MCP transport protocols, selected via `PURVIEW_MCP_TRANSPORT`:

### 1. stdio (default)

The AI client **spawns the server process** and communicates over stdin/stdout. No network port needed. This is the simplest and most portable mode — used by all local AI editors.

```
PURVIEW_MCP_TRANSPORT=stdio   <- default, no need to set explicitly
```

**MCP client config type:** `"command"` (process launch)

### 2. Streamable-HTTP (recommended for network use)

The modern MCP transport (spec v2025-03-26). The server listens on `POST /mcp`. Clients send JSON-RPC and receive streamed responses. Used by the Azure Functions hosting mode.

```bash
PURVIEW_MCP_TRANSPORT=streamable-http    # or alias: http
PURVIEW_MCP_HOST=127.0.0.1
PURVIEW_MCP_PORT=8000
```

Endpoint: `http://127.0.0.1:8000/mcp`
**MCP client config type:** `"http"`

### 3. SSE (legacy)

Server-Sent Events transport (spec v2024-11-05). Two endpoints:
- `GET /sse` — persistent event stream (client connects and listens)
- `POST /messages` — client sends tool calls

```bash
PURVIEW_MCP_TRANSPORT=sse
PURVIEW_MCP_HOST=127.0.0.1
PURVIEW_MCP_PORT=8000
```

Endpoint: `http://127.0.0.1:8000/sse`
**MCP client config type:** `"sse"`

> **Note:** SSE is **not compatible** with Azure Functions — persistent connections are required and Functions is stateless. Use stdio or streamable-HTTP instead.

### Protocol comparison

| Feature | stdio | Streamable-HTTP | SSE |
|---|---|---|---|
| Network required | No | Yes | Yes |
| Works in Azure Functions | N/A | Yes | No |
| MCP spec version | Any | v2025-03-26 | v2024-11-05 |
| VS Code `mcp.json` type | `"command"` | `"http"` | `"sse"` |
| Persistent connection | No | No | Yes (GET /sse) |
| Best for | Local dev | Remote/cloud | Legacy clients |

---

## Quick Start

### Option A — stdio (simplest)

```powershell
# From repo root, with venv active
$env:PURVIEW_ACCOUNT_NAME = "your-account"
python tools/PurviewMCPServer/server.py
```

### Option B — Streamable-HTTP (standalone)

```powershell
$env:PURVIEW_ACCOUNT_NAME  = "your-account"
$env:PURVIEW_MCP_TRANSPORT = "streamable-http"
$env:PURVIEW_MCP_PORT      = "8000"
python tools/PurviewMCPServer/server.py
# MCP endpoint: http://127.0.0.1:8000/mcp
```

### Option C — Azure Functions (func host)

```powershell
cd tools/hosting/app
func start --port 7073
# MCP endpoint: http://localhost:7073/api/mcp
# Health check:  http://localhost:7073/api/health
```

---

## Client Setup

### VS Code + GitHub Copilot

The repository ships a ready-to-use `.vscode/mcp.json`:

```json
{
  "servers": {
    "purview-mcp-server-stdio": {
      "command": "./.venv/Scripts/python",
      "args": ["tools/PurviewMCPServer/server.py"],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "your-account"
      }
    },
    "purview-mcp-server-http": {
      "type": "http",
      "url": "http://localhost:7073/api/mcp"
    }
  }
}
```

- Use `purview-mcp-server-stdio` for local dev (no `func start` needed).
- Use `purview-mcp-server-http` when `func start --port 7073` is running.

**Steps:**
1. Open the MCP panel (Copilot toolbar → MCP servers icon).
2. Click **Start** next to the server entry.
3. When connected, the tool count appears above the server name.
4. Open Copilot Chat in Agent mode and interact with Purview.

### Claude Code

#### Local checkout (stdio)

```json
{
  "mcpServers": {
    "purview": {
      "command": "python",
      "args": ["tools/PurviewMCPServer/server.py"],
      "cwd": "C:/Dvlp/Projects/Purview/Purview_cli",
      "env": {
        "PURVIEW_ACCOUNT_NAME": "your-account",
        "AZURE_TENANT_ID": "your-tenant-guid"
      }
    }
  }
}
```

#### Direct from GitHub (uvx — no local checkout)

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
        "PURVIEW_ACCOUNT_NAME": "your-account",
        "AZURE_TENANT_ID": "your-tenant-guid"
      }
    }
  }
}
```

After editing: restart Claude Code → call `list_available_operations()` to verify → then use write operations.

### Cursor

Open **Cursor → Settings → MCP** and add:

```json
{
  "command": "python",
  "args": ["tools/PurviewMCPServer/server.py"],
  "env": {
    "PURVIEW_ACCOUNT_NAME": "your-account"
  }
}
```

Click **Reconnect MCP**, then test with `list_available_operations`.

### Any Other MCP Client

Stdio baseline (works everywhere):

```json
{
  "mcpServers": {
    "purview": {
      "command": "python",
      "args": ["tools/PurviewMCPServer/server.py"],
      "env": {
        "PURVIEW_ACCOUNT_NAME": "<account>",
        "AZURE_TENANT_ID": "<tenant>"
      }
    }
  }
}
```

HTTP baseline (when server is already running):

```json
{
  "mcpServers": {
    "purview": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

---

## Azure Functions Hosting

The `tools/hosting/app/` folder is an Azure Functions v2 Python app that wraps FastMCP as an ASGI app. This is the recommended path for remote / cloud deployment.

### Local development

```powershell
cd tools/hosting/app
func start --port 7073
```

Registered endpoints:

| Endpoint | Purpose |
|---|---|
| `GET  http://localhost:7073/api/health` | Liveness probe — returns `{"status":"healthy"}` |
| `POST http://localhost:7073/api/mcp` | MCP streamable-HTTP — tool calls |
| `GET  http://localhost:7073/api/mcp` | MCP session initialisation |
| `DELETE http://localhost:7073/api/mcp` | MCP session teardown |

**Why `/api/mcp` and not `/mcp`?**
Azure Functions v2 Python model automatically prefixes all `@app.route` entries with `/api/`. The `AsgiMiddleware` forwards the full request path (including `/api/`) to the FastMCP ASGI app, so the app must be mounted at `path="/api/mcp"` inside `function_app.py`. This differs from the self-hosted custom handler pattern described in the [Microsoft tutorial](https://learn.microsoft.com/en-us/azure/azure-functions/functions-mcp-tutorial), where the endpoint is at `/mcp` (no prefix).

### local.settings.json (minimal)

```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "",
    "PURVIEW_ACCOUNT_NAME": "your-account",
    "AZURE_TENANT_ID": "your-tenant-guid"
  },
  "Host": {
    "LocalHttpPort": 7071,
    "CORS": "*"
  }
}
```

Set `AzureWebJobsStorage: ""` for local dev without Azurite.

### Deploying to Azure

Required app settings in Azure:

```bash
PURVIEW_ACCOUNT_NAME=your-account
AZURE_TENANT_ID=your-tenant-guid
# Plus managed identity or service principal vars
```

Production MCP endpoint: `https://<function-app>.azurewebsites.net/api/mcp`

---

## Available Tools

### Entity Operations (8 tools)

| Tool | Description |
|---|---|
| `get_entity` | Retrieve entity by GUID with full attributes |
| `create_entity` | Register a new data asset |
| `update_entity` | Update attributes on an existing entity |
| `delete_entity` | Remove an entity from the catalog |
| `search_entities` | Keyword search with type/classification filters |
| `batch_create_entities` | Bulk register multiple entities in one call |
| `batch_update_entities` | Bulk attribute updates |
| `import_entities_from_csv` | Import entities from a CSV file with column mapping |

### Glossary Operations (3 tools)

| Tool | Description |
|---|---|
| `get_glossary_terms` | List all terms, optionally scoped to a glossary |
| `create_glossary_term` | Define a new business term |
| `assign_term_to_entities` | Tag one or more entities with a glossary term |

### Unified Catalog Operations (11 tools)

| Tool | Description |
|---|---|
| `uc_list_domains` | List all governance domains |
| `uc_get_domain` | Get full domain details by ID |
| `uc_create_domain` | Create a new governance domain |
| `uc_list_terms` | List business metadata terms in a domain |
| `uc_get_term` | Get term details |
| `uc_create_term` | Create a new business metadata term |
| `uc_search_terms` | Search terms across all domains |
| `uc_list_custom_metadata_defs` | List all business metadata definitions and attributes |
| `uc_cleanup_metadata_definition` | Check or safely clean up a metadata definition (`check_only=true` for preview) |
| `uc_delete_metadata_definition` | Delete a business metadata definition by name |
| `uc_delete_metadata_from_asset` | Remove a metadata group assignment from a specific asset |

### Collection Operations (5 tools)

| Tool | Description |
|---|---|
| `list_collections` | List all collections |
| `get_collection` | Get collection details |
| `create_collection` | Create a new collection |
| `delete_collection` | Remove a collection |
| `get_collection_path` | Get the full hierarchical path to a collection |

### Lineage Operations (2 tools)

| Tool | Description |
|---|---|
| `get_lineage` | Get upstream and downstream lineage for an entity |
| `create_lineage` | Create a lineage relationship between entities |

### Search Operations (2 tools)

| Tool | Description |
|---|---|
| `search_suggest` | Autocomplete suggestions for entity names |
| `search_browse` | Browse entities by type with faceted aggregations |

### Type Definition Operations (2 tools)

| Tool | Description |
|---|---|
| `get_typedef` | Get the schema for a specific type definition |
| `list_typedefs` | List all available type definitions |

### Relationship Operations (3 tools)

| Tool | Description |
|---|---|
| `create_relationship` | Create a relationship between two entities |
| `get_relationship` | Retrieve relationship details by GUID |
| `delete_relationship` | Delete a relationship |

### Account & Operation Registry (3 tools)

| Tool | Description |
|---|---|
| `get_account_properties` | Get Purview account configuration |
| `list_available_operations` | List all pvw-cli operations grouped by category |
| `invoke_operation` | Invoke any pvw-cli operation dynamically by name |

---

## Prompt Examples

Use these directly in GitHub Copilot, Claude, or Cursor after connecting the server.

### 1. Discover the server

```
Use the Purview MCP server and list available operations. Group them by area
(entity, glossary, unified catalog, lineage) and highlight the safest
read-only operations to start with.
```

### 2. Find assets by keyword

```
Use Purview MCP to search for assets with keyword "customer" (limit 10).
Return a table with entity GUID, name, typeName, and collection. Summarize
the top 3 most relevant results.
```

### 3. Safe metadata cleanup check (no delete)

```
Run uc_cleanup_metadata_definition for "MyBusinessMetadata" with
check_only=true. Show whether this metadata is still assigned to assets.
If assigned, list the impacted asset IDs before any delete action.
```

### 4. Governance domain setup

```
Use Purview MCP to:
1) List existing unified catalog domains.
2) Create domain "Finance" with a short description.
3) Create term "Customer Health Score" in that domain.
4) Return the domain ID and term ID for future use.
```

### 5. Bulk import from CSV

```
Use import_entities_from_csv to import the file at "samples/csv/entities.csv"
as azure_sql_table entities. Map column "table_name" to "name" and
"schema_name" to "schema". Show the import result summary.
```

### 6. Impact analysis via lineage

```
Get lineage for entity <guid>, depth 3, both upstream and downstream.
List all upstream sources and highlight any entities with no classification.
```

### 7. Full metadata cleanup workflow

```
Safely clean up business metadata definition "LegacyMetadata":
1) Run uc_cleanup_metadata_definition in check_only=true mode.
2) If no active assignments remain, execute the full cleanup.
3) Delete the definition with uc_delete_metadata_definition.
4) Confirm by listing custom metadata definitions again.
```

### 8. Troubleshooting a 403

```
I am getting a 403 from a Purview MCP write operation. Please:
1) Re-run a related read-only operation to validate connectivity.
2) Show the exact failing operation name and input.
3) Suggest the minimum Purview permissions and identity checks needed.
4) Propose the next safe command to continue without modifying data.
```

---

## Common Workflows

### Workflow 1: Catalog a new data source

```
1. search_entities            <- check if it already exists
2. create_entity              <- register if new
3. create_glossary_term       <- define business term (if needed)
4. assign_term_to_entities    <- tag the new entity
5. create_lineage             <- link to upstream source (if known)
```

### Workflow 2: Governance domain setup

```
1. uc_list_domains            <- audit existing domains
2. uc_create_domain           <- create if needed
3. uc_create_term             <- add vocabulary
4. assign_term_to_entities    <- enrich assets
```

### Workflow 3: Metadata lifecycle cleanup

```
1. uc_list_custom_metadata_defs             <- inventory all definitions
2. uc_cleanup_metadata_definition (check)  <- safe preview
3. uc_cleanup_metadata_definition (run)    <- execute if safe
4. uc_delete_metadata_definition           <- remove the definition
```

### Workflow 4: Entity exploration

```
1. search_suggest             <- autocomplete for discovery
2. search_entities            <- filtered keyword search
3. get_entity                 <- full details on a specific asset
4. get_lineage                <- understand data flow
5. get_glossary_terms         <- see assigned terms
```

### Recommended first commands for any new setup

```
1) list_available_operations()
2) get_account_properties()
3) search_entities(query="customer", limit=5)
4) uc_list_domains()
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `PURVIEW_ACCOUNT_NAME is required` | Missing env var | Set `PURVIEW_ACCOUNT_NAME` in shell or `.env` |
| `401 Unauthorized` | Not authenticated | Run `az login` or set service principal env vars |
| `403 Forbidden` | Insufficient Purview role | Assign **Purview Data Curator** or **Data Reader** role |
| `404 Not Found` | Wrong GUID or entity does not exist | Verify GUID with `search_entities` first |
| `429 Too Many Requests` | Rate limited | Reduce `PURVIEW_BATCH_SIZE` or add delay between calls |
| `No module named 'config'` | Editable install out of sync | Re-run `pip install -e tools/PurviewMCPServer` |
| `404 on /api/mcp` | Path mismatch in func host | Confirm `function_app.py` mounts at `path="/api/mcp"` |
| Tools missing after restart | Stale MCP cache in client | Fully restart MCP server and reconnect the client |
| SSE not working in func host | Persistent connection incompatible with Functions | Switch to `streamable-http` or `stdio` |

---

## Related Docs

- [Unified Catalog guide](unified-catalog.md)
- [Unified Catalog commands](commands/unified-catalog.md)
- [Authentication troubleshooting](authentication-troubleshooting.md)
- [Performance optimization guide](performance-optimization-guide.md)
- [Bulk CSV guide](entity-bulk-csv-guide.md)
- [Common workflows](common-workflows.md)
