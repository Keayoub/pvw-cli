# Purview MCP Server Extension for Visual Studio Code

**Version 2.0 - Now powered by FastMCP! 🚀**

Provides [Model Context Protocol (MCP)](https://modelcontextprotocol.io) integration and tooling for **Microsoft Purview** in Visual Studio Code.

All Purview MCP tools in a single server. The Purview MCP Server implements the [MCP specification](https://modelcontextprotocol.io/introduction) to create a seamless connection between AI agents and Purview services. **Version 2.0** uses **FastMCP** for cleaner code, automatic validation, and improved performance. Purview MCP Server can be used alone or with the [GitHub Copilot for Azure extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azure-github-copilot) in VS Code.

## Table of Contents

* [Overview](#overview)
* [Installation](#installation)
* [Usage](#usage)
  * [Getting Started](#getting-started)
  * [What can you do with the Purview MCP Server?](#what-can-you-do-with-the-purview-mcp-server)
  * [Configure Azure Authentication](#configure-azure-authentication)
* [Support and Reference](#support-and-reference)

## Overview

Purview MCP Server supercharges your agents with Purview context across **40+ different Azure Purview services**.

## Installation

### Requirements

* **VS Code** 1.103 or above
* **Python** 3.8 or later
* **Azure CLI** for authentication (`az login`)

### Install Extension

* Install the [Purview MCP Server Visual Studio Code extension](https://marketplace.visualstudio.com/items?itemName=keayoub.purview-mcp) from the Marketplace
* Or install from VSIX: `code --install-extension purview-mcp-1.0.0.vsix`

The extension bundles the MCP server and all required Python files - **no need to clone the repository!**

> **Note:** Python dependencies (mcp, fastmcp, azure-identity, aiohttp, etc.) will be automatically installed when you first start the server.
>
> **What's New in v2.0:**
> - 🚀 Migrated to **FastMCP** for better performance and cleaner code
> - ✅ Automatic parameter validation with Pydantic
> - 📖 Auto-generated tool documentation
> - 🔧 Simplified server architecture (30% less code)
> - 🔄 Backward compatible with legacy MCP server (available as fallback)

### Enable Autostart

1. Open **Settings** in VS Code.
2. Search for `chat.mcp.autostart`.
3. Select **newAndOutdated** so automatically start MCP servers without manual refresh.

You can also set this from the refresh icon in the Chat view, which also shows which MCP servers will auto-start next time you send a chat message.

## Usage

### Getting Started

1. Run `MCP: List Servers`.
2. Select `Purview MCP Server`, ext, then click **Start Server**.
3. Go to the **Output** tab in VS Code.
4. Look for log messages confirming the server can run the MCP settings.

### What can you do with the Purview MCP Server?

The Purview MCP Server exposes over **40 tools** for interacting with Microsoft Purview:

* **Account & Collections**: List and manage Purview accounts and collections
* **Entities**: Create, read, update, and delete data catalog entities
* **Glossary**: Manage business glossary terms and relationships
* **Lineage**: Query and visualize data lineage
* **Search & Discovery**: Search the data catalog
* **Types**: Work with entity type definitions
* **Relationships**: Manage entity relationships
* **Scan Management**: Configure and run data scans
* **Insights**: Access data estate insights
* **Policy Store**: Manage access policies
* **Unified Catalog**: Work with unified catalog features

### Configure Azure Authentication

#### Manual Configuration (Optional)

In VS Code Settings, pre-configure (Settings → Search "purview-mcp"):

* `purview-mcp.accountName`: Your Purview account name (required)
* `purview-mcp.accountId`: Purview account ID for Unified Catalog (optional)
* `purview-mcp.tenantId`: Azure tenant ID (optional)

If not configured, the extension will prompt you when you start the server.

The Purview MCP Server uses Azure Default Credential for authentication. Make sure you're logged in with Azure CLI:

```bash
az login
```

#### First Run: Automatic Dependency Installation

When you start the server for the first time, the extension will:

1. Check if Python dependencies are installed
2. Prompt you to install them automatically if missing
3. Install `mcp`, `fastmcp`, `azure-identity`, `aiohttp`, `pandas`, and `purviewcli` from the bundled requirements.txt

### FastMCP vs Legacy Server

Version 2.0 uses **FastMCP** by default for better performance and developer experience. You can switch to the legacy MCP server if needed:

1. Open **Settings** in VS Code
2. Search for `purview-mcp.useFastMCP`
3. Uncheck to use the legacy server (`server_legacy.py`)

Both servers provide the same 33 tools and full functionality.

## Support and Reference

* [Documentation](https://github.com/Keayoub/pvw-cli/tree/main/doc)
* [Report an Issue](https://github.com/Keayoub/pvw-cli/issues)
* [MCP Specification](https://modelcontextprotocol.io)
