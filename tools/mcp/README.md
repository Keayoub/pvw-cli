# Purview MCP Server

FastMCP-based server that exposes Microsoft Purview data governance operations through the [Model Context Protocol](https://modelcontextprotocol.io/).

> **Full documentation:** [`docs/purview-mcp-server.md`](../../docs/purview-mcp-server.md)

---

## Quick Start

```powershell
# stdio (default) — from repo root, venv active
$env:PURVIEW_ACCOUNT_NAME = "your-account"
python tools/PurviewMCPServer/server.py
```

```powershell
# Streamable-HTTP
$env:PURVIEW_MCP_TRANSPORT = "streamable-http"
$env:PURVIEW_MCP_PORT      = "8000"
python tools/PurviewMCPServer/server.py
# endpoint: http://127.0.0.1:8000/mcp
```

```powershell
# Azure Functions (func host)
cd tools/hosting/app && func start --port 7073
# endpoint: http://localhost:7073/api/mcp
```

---

## Transport Protocols

| Transport | Env value | VS Code mcp.json type | Endpoint |
|---|---|---|---|
| stdio (default) | `stdio` | `"command"` | process stdin/stdout |
| Streamable-HTTP | `streamable-http` or `http` | `"http"` | `/mcp` (standalone) or `/api/mcp` (Azure Functions) |
| SSE (legacy) | `sse` | `"sse"` | `/sse` (standalone only — not compatible with Azure Functions) |

---

## VS Code mcp.json

```json
{
  "servers": {
    "purview-mcp-server-stdio": {
      "command": "./.venv/Scripts/python",
      "args": ["tools/PurviewMCPServer/server.py"],
      "env": { "PURVIEW_ACCOUNT_NAME": "your-account" }
    },
    "purview-mcp-server-http": {
      "type": "http",
      "url": "http://localhost:7073/api/mcp"
    }
  }
}
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `PURVIEW_ACCOUNT_NAME` | Yes | — | Purview account name (no suffix) |
| `AZURE_TENANT_ID` | No | — | Azure tenant GUID |
| `AZURE_CLIENT_ID` | No | — | Service principal client ID |
| `AZURE_CLIENT_SECRET` | No | — | Service principal secret |
| `AZURE_REGION` | No | public | Sovereign cloud: `usgov`, `china` |
| `PURVIEW_MAX_RETRIES` | No | `3` | API retry count |
| `PURVIEW_TIMEOUT` | No | `30` | Request timeout (seconds) |
| `PURVIEW_BATCH_SIZE` | No | `100` | Bulk operation batch size |
| `PURVIEW_MCP_TRANSPORT` | No | `stdio` | Transport protocol |
| `PURVIEW_MCP_HOST` | No | `127.0.0.1` | Bind host (HTTP/SSE modes) |
| `PURVIEW_MCP_PORT` | No | `8000` | Bind port (HTTP/SSE modes) |

Copy `.env.example` to `.env` and fill in your values. Never commit `.env`.

---

## Available Tools (37 + registry)

| Category | Tools |
|---|---|
| Entity (8) | `get_entity`, `create_entity`, `update_entity`, `delete_entity`, `search_entities`, `batch_create_entities`, `batch_update_entities`, `import_entities_from_csv` |
| Glossary (3) | `get_glossary_terms`, `create_glossary_term`, `assign_term_to_entities` |
| Unified Catalog (11) | `uc_list_domains`, `uc_get_domain`, `uc_create_domain`, `uc_list_terms`, `uc_get_term`, `uc_create_term`, `uc_search_terms`, `uc_list_custom_metadata_defs`, `uc_cleanup_metadata_definition`, `uc_delete_metadata_definition`, `uc_delete_metadata_from_asset` |
| Collections (5) | `list_collections`, `get_collection`, `create_collection`, `delete_collection`, `get_collection_path` |
| Lineage (2) | `get_lineage`, `create_lineage` |
| Search (2) | `search_suggest`, `search_browse` |
| Type Defs (2) | `get_typedef`, `list_typedefs` |
| Relationships (3) | `create_relationship`, `get_relationship`, `delete_relationship` |
| Account + Registry (3) | `get_account_properties`, `list_available_operations`, `invoke_operation` |

---

## Recommended First Commands

```
1) list_available_operations()
2) get_account_properties()
3) search_entities(query="customer", limit=5)
4) uc_list_domains()
```

---

## Files

| File | Purpose |
|---|---|
| `server.py` | FastMCP server — all 37 tool definitions |
| `config.py` | `PurviewMCPConfig` frozen dataclass — env var parsing and validation |
| `__version__.py` | Package version |
| `.env.example` | Environment variable template |
| `PROMPT_INSTRUCTIONS.md` | Detailed prompt guidance for AI assistants |
| `pyproject.toml` | Package metadata (`pvw-mcp-server`) |
| `Dockerfile` | Container image for standalone deployment |
| `docker-compose.yml` | Local container stack |

For Azure Functions hosting files, see `tools/hosting/`.

---

See [`docs/purview-mcp-server.md`](../../docs/purview-mcp-server.md) for the full reference including client setup for Claude Code and Cursor, Azure Functions deployment, all prompt examples, workflows, and troubleshooting.
