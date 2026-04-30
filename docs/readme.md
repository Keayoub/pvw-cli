# pvw-cli Documentation

`pvw-cli` is a Python CLI and library for automating Microsoft Purview. It covers Data Map, Unified Catalog, Collections, Search, Lineage, Scan, and Management APIs.

## Install

Install from PyPI:

```bash
pip install pvw-cli
```

Install from source:

```bash
git clone https://github.com/Keayoub/pvw-cli.git
cd pvw-cli
pip install -r requirements.txt
pip install -e .
```

## Configure

Set these required environment variables before running commands:

| Variable | Description |
|---|---|
| `PURVIEW_ACCOUNT_NAME` | Your Purview account name |
| `PURVIEW_ACCOUNT_ID` | Your Azure Tenant ID |
| `PURVIEW_RESOURCE_GROUP` | Resource group containing the Purview account |

PowerShell:

```powershell
$env:PURVIEW_ACCOUNT_NAME = "your-purview-account"
$env:PURVIEW_ACCOUNT_ID = "your-tenant-id-guid"
$env:PURVIEW_RESOURCE_GROUP = "your-resource-group"
```

Bash:

```bash
export PURVIEW_ACCOUNT_NAME=your-purview-account
export PURVIEW_ACCOUNT_ID=your-tenant-id-guid
export PURVIEW_RESOURCE_GROUP=your-resource-group
```

To find your tenant ID:

```bash
az account show --query tenantId -o tsv
```

## Authenticate

`pvw-cli` uses `DefaultAzureCredential` and tries these authentication methods:

1. Azure CLI via `az login`
2. Service principal via `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_CLIENT_SECRET`
3. Managed identity when running on Azure

If your tenant uses the older Purview resource principal, set:

```bash
export PURVIEW_AUTH_SCOPE=https://purview.azure.net/.default
```

## Start Using pvw-cli

See the installed command groups:

```bash
pvw --help
```

Common command groups:

```text
pvw account
pvw collections
pvw entity
pvw glossary
pvw lineage
pvw scan
pvw search
pvw types
pvw uc
pvw workflow
pvw diagnostics
```

Examples:

```bash
pvw account getAccount
pvw search query --keywords "customer"
pvw glossary readTerms
```

## Where to Go Next

- [Getting Started](getting-started.md) for installation, configuration, and first commands
- [Full Documentation Catalog](documentation-catalog.md) to browse all documentation pages
- [Full Samples Catalog](samples-catalog.md) to browse notebooks, PowerShell, JSON, and CSV samples
- [Command Documentation](commands/) for per-command help
- [Integrated Portal](integrated/readme.md) for organized guides and reference material

## Support

- [GitHub Repository](https://github.com/Keayoub/pvw-cli)
- [Issue Tracker](https://github.com/Keayoub/pvw-cli/issues)
