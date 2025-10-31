# Purview MCP Server - Bundled Files

This directory contains the files bundled with the Purview MCP VS Code extension.

## Files

- **server.py** - The FastMCP server implementation for Purview CLI
- **requirements.txt** - Python dependencies required by the server
- **diagnose.ps1** - Diagnostic script to verify installation and configuration
- **register-mcp-server.ps1** - Script to register the MCP server in VS Code
- **check-mcp-feature.ps1** - Script to check MCP feature configuration and compare with other MCP extensions

## Check MCP Feature

To verify your MCP server configuration and compare with other installed MCP extensions:

### Windows (PowerShell)

```powershell
pwsh -File check-mcp-feature.ps1
```

This will show:
- Installed Purview MCP extension versions
- Current MCP configuration (servers, environment variables)
- Comparison with Azure MCP Server (if installed)
- Recommendations for fixing issues

## Manual Registration

If the MCP server doesn't appear in the extension's "MCP Servers" feature section after installation, you can manually register it:

### Windows (PowerShell)
```powershell
pwsh -File register-mcp-server.ps1
```

### What it does
The registration script will:
1. Find your installed Purview MCP extension
2. Read the MCP configuration from `%APPDATA%\Code\User\mcp.json`
3. Add the Purview MCP server configuration
4. Create a backup of your existing configuration
5. Write the updated configuration

### After Registration
1. **Restart VS Code completely** (not just reload)
2. Configure your Purview settings:
   - Purview MCP: Account Name
   - Purview MCP: Account ID
   - Purview MCP: Tenant ID
3. Check the extension's Features tab - you should now see "MCP Servers"
4. Test with `@mcp` in GitHub Copilot Chat

## Automatic Registration

You can also use the build script with the `-RegisterServer` flag to automatically install and register:

```powershell
.\build-extension.ps1 -RegisterServer
```

Or for a complete clean build with registration:

```powershell
.\build-extension.ps1 -Clean -RegisterServer
```

## Troubleshooting

If the server doesn't appear after registration:
1. Check that the extension is installed and enabled
2. Verify the bundled files exist in the extension folder
3. Run the diagnostic script: `pwsh -File diagnose.ps1`
4. Check VS Code's output panel for errors
5. Make sure you **restarted VS Code** (not just reloaded)

## Environment Variables

The MCP server uses these environment variables (configured via VS Code settings):
- `PURVIEW_ACCOUNT_NAME` - Your Azure Purview account name
- `PURVIEW_ACCOUNT_ID` - Your Azure Purview account ID (for Unified Catalog)
- `AZURE_TENANT_ID` - Your Azure AD tenant ID (optional)
