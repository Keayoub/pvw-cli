# Getting Started

This guide shows how to install, configure, authenticate, and run your first `pvw-cli` commands.

## Prerequisites

Before installing the CLI, make sure you have:

- Python 3.8 or later
- `pip` available in your Python environment
- Access to a Microsoft Purview account
- Azure credentials that can access that Purview account
- Azure CLI installed if you want the simplest local sign-in flow

Recommended before first use:

- Run `az login` for local interactive authentication
- Confirm your Purview account name, tenant ID, and resource group
- Use a virtual environment so CLI dependencies stay isolated

The packages declared in `pyproject.toml` are runtime dependencies and are installed automatically when you run `pip install pvw-cli`. You normally do not need to install them one by one unless you are debugging or developing the CLI itself.

## 1. Install

Install from PyPI:

```bash
pip install pvw-cli
```

Create and activate a virtual environment if you want an isolated install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install pvw-cli
```

Or install from source:

```bash
git clone https://github.com/Keayoub/pvw-cli.git
cd pvw-cli
pip install -r requirements.txt
pip install -e .
```

### Runtime dependency summary

`pvw-cli` installs these automatically:

- `azure-identity`: authentication through `DefaultAzureCredential`
- `azure-core`: Azure SDK pipeline primitives and shared client behavior
- `click`: command-line parsing and command group registration
- `rich`: formatted terminal output, tables, colors, and diagnostics
- `requests`: synchronous HTTP calls to Purview REST APIs
- `pandas`: CSV and tabular bulk-processing workflows
- `aiohttp`: async HTTP support for high-throughput or concurrent operations
- `pydantic`: typed configuration and validation models
- `PyYAML`: YAML parsing for config and structured metadata inputs
- `cryptography`: secure auth and token/certificate support used by the auth stack

## 2. Sign in to Azure

For local development, the easiest option is Azure CLI authentication:

```bash
az login
```

## 3. Configure Environment Variables

Set these values before using the CLI.

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

To get your tenant ID:

```bash
az account show --query tenantId -o tsv
```

## 4. Verify the CLI

Check the available commands:

```bash
pvw --help
```

Check one command group:

```bash
pvw search --help
```

## 5. Run Your First Commands

Read account details:

```bash
pvw account getAccount
```

Search the catalog:

```bash
pvw search query --keywords "customer"
```

List glossary terms:

```bash
pvw glossary readTerms
```

If your primary goal is modern governance in Microsoft Purview, continue with the dedicated [Unified Catalog](unified-catalog.md) page.

## 6. Troubleshooting Authentication

If you see a legacy tenant resource principal issue, set:

```bash
export PURVIEW_AUTH_SCOPE=https://purview.azure.net/.default
```

If you need more help, see:

- [Authentication Troubleshooting](authentication-troubleshooting.md)
- [Unified Catalog](unified-catalog.md)
- [Quick Reference](quick-reference.md)
- [Full Documentation Catalog](documentation-catalog.md)
