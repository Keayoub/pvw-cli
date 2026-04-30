# Getting Started

This guide shows how to install, configure, authenticate, and run your first `pvw-cli` commands.

## 1. Install

Install from PyPI:

```bash
pip install pvw-cli
```

Or install from source:

```bash
git clone https://github.com/Keayoub/pvw-cli.git
cd pvw-cli
pip install -r requirements.txt
pip install -e .
```

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
