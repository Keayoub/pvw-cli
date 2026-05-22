# Azure Functions Hosting for Purview MCP Server

Two ways to expose the Purview MCP Server as a remote endpoint.

---

## Option 1 — Standalone FastMCP (no Azure Functions)

Run FastMCP directly as a network server. No Azure Functions required. Best for local development and containers.

```powershell
$env:PURVIEW_ACCOUNT_NAME  = "your-account"
$env:PURVIEW_MCP_TRANSPORT = "streamable-http"
$env:PURVIEW_MCP_PORT      = "8000"
python -m pvw_mcp_server.server
```

| Property | Value |
|---|---|
| MCP endpoint | `http://127.0.0.1:8000/mcp` |
| VS Code `mcp.json` type | `"http"` |
| Tools exposed | All 37 tools |
| Azure Functions required | No |
| Azurite required | No |
| Best for | Local dev, Docker, containers |

---

## Option 2 — Self-hosted FastMCP on Azure Functions (`app/`)

FastMCP runs inside Azure Functions via the ASGI middleware. Functions acts as the HTTP host; FastMCP handles all MCP protocol logic automatically for all registered tools.

```powershell
cd tools/hosting/app
func start
```

| Property | Value |
|---|---|
| MCP endpoint | `http://localhost:7071/api/mcp` (local) |
| VS Code `mcp.json` type | `"http"` |
| Tools exposed | All 37 tools |
| Azure Functions required | Yes (v2 Python model) |
| Azurite required | No (`AzureWebJobsStorage: ""`) |
| Auth | `FUNCTION` key (set `Anonymous` for local dev) |
| Best for | Serverless cloud hosting |

**How it works:**

```
MCP Client  ──POST /api/mcp──▶  Azure Functions host
                                       │
                               func.AsgiMiddleware
                                       │
                          mcp.streamable_http_app()
                                       │
                              server.py @mcp.tool()s
```

### Key files

| File | Purpose |
|---|---|
| `app/function_app.py` | ASGI entry point — wraps `mcp.streamable_http_app()` |
| `app/host.json` | Extension bundle v4 config |
| `app/local.settings.json` | Local env vars (`AzureWebJobsStorage: ""`) |
| `app/requirements.txt` | `azure-functions`, `fastmcp>=2.0.0`, `purview-mcp-server` |

### VS Code mcp.json (remote)

```json
{
  "servers": {
    "purview-mcp-server": {
      "type": "http",
      "url": "https://\/api/mcp",
      "headers": {
        "x-functions-key": "\"
      }
    }
  }
}
```

---

## Environment Variables (`local.settings.json`)

Configure these in `app/local.settings.json` for local development, or as Azure Function App Settings for cloud deployment.

| Variable | Required | Default | Description |
|---|---|---|---|
| `PURVIEW_ACCOUNT_NAME` | **Yes** | — | Purview account name (no `.purview.azure.com` suffix) |
| `AZURE_TENANT_ID` | **Yes** | — | Azure AD tenant GUID for authentication |
| `AZURE_SUBSCRIPTION_ID` | **Yes** | — | Azure subscription ID containing the Purview account |
| `AZURE_REGION` | No | public | Sovereign cloud override: `usgov`, `china` |
| `AZURE_CLIENT_ID` | No | — | Service principal client ID (omit to use Azure CLI / Managed Identity) |
| `AZURE_CLIENT_SECRET` | No | — | Service principal secret (required when `AZURE_CLIENT_ID` is set) |
| `PURVIEW_MAX_RETRIES` | No | `3` | API retry count on transient failures |
| `PURVIEW_TIMEOUT` | No | `30` | Request timeout in seconds |
| `PURVIEW_BATCH_SIZE` | No | `100` | Bulk operation batch size |

**Example `local.settings.json`:**

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FUNCTIONS_EXTENSION_VERSION": "~4",
    "PURVIEW_ACCOUNT_NAME": "your-purview-account",
    "AZURE_TENANT_ID": "<tenant-guid>",
    "AZURE_SUBSCRIPTION_ID": "<subscription-guid>",
    "AZURE_REGION": "",
    "PURVIEW_MAX_RETRIES": "3",
    "PURVIEW_TIMEOUT": "30",
    "PURVIEW_BATCH_SIZE": "100"
  },
  "Host": {
    "LocalHttpPort": 7079,
    "CORS": "*",
    "CORSCredentials": false
  }
}
```

> `AzureWebJobsStorage` can be left empty for local development (no storage trigger needed).  
> Authentication order: Service Principal → Azure CLI (`az login`) → Managed Identity.

---

## Deployment to Azure

```powershell
# From VS Code command palette
Azure Functions: Deploy to Function App
```

Or with Azure Developer CLI:

```powershell
cd tools/hosting
azd up
```

See [docs/purview-mcp-server.md](../../docs/purview-mcp-server.md) for the full reference.
