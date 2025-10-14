# Purview CLI Authentication Guide

## Overview

The Purview CLI uses Azure authentication to access Microsoft Purview. There are several authentication methods available depending on your use case.

## Authentication Methods

### Method 1: Azure CLI (Interactive - Recommended for Development)

This is the easiest method for individual users and development environments.

**Prerequisites:**
- Azure CLI installed ([Install Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))

**Steps:**

```bash
# 1. Login with Azure CLI
az login

# 2. Set your Purview account
export PURVIEW_ACCOUNT_NAME="your-purview-account-name"

# 3. Test the connection
pvw scan keyVaultList
```

**Windows (PowerShell):**

```powershell
# 1. Login with Azure CLI
az login

# 2. Set your Purview account
$env:PURVIEW_ACCOUNT_NAME = "your-purview-account-name"

# 3. Test the connection
pvw scan scanname
```

### Method 2: Service Principal (Recommended for Automation)

Use this method for CI/CD pipelines, automation scripts, and production environments.

**Prerequisites:**
- Service Principal created with appropriate permissions
- Client ID, Tenant ID, and Client Secret

**Steps:**

```bash
# Set environment variables
export AZURE_CLIENT_ID="your-client-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export PURVIEW_ACCOUNT_NAME="your-purview-account-name"

# Test the connection
pvw scan keyVaultList
```

**Windows (PowerShell):**

```powershell
# Set environment variables
$env:AZURE_CLIENT_ID = "your-client-id"
$env:AZURE_TENANT_ID = "your-tenant-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
$env:PURVIEW_ACCOUNT_NAME = "your-purview-account-name"

# Test the connection
pvw scan keyVaultList
```

**Windows (CMD):**

```cmd
REM Set environment variables
SET AZURE_CLIENT_ID=your-client-id
SET AZURE_TENANT_ID=your-tenant-id
SET AZURE_CLIENT_SECRET=your-client-secret
SET PURVIEW_ACCOUNT_NAME=your-purview-account-name

REM Test the connection
pvw scan keyVaultList
```

### Method 3: Managed Identity (Azure VMs/Services)

Use this method when running the CLI on Azure VMs or Azure services that support managed identities.

**Prerequisites:**
- Code running on Azure VM, Azure App Service, Azure Functions, etc.
- Managed Identity enabled and assigned appropriate Purview permissions

**Steps:**

```bash
# Only set the Purview account name
export PURVIEW_ACCOUNT_NAME="your-purview-account-name"

# The CLI will automatically use the managed identity
pvw scan keyVaultList
```

## Creating a Service Principal

If you need to create a service principal for authentication:

### Using Azure Portal

1. Navigate to **Azure Active Directory** → **App registrations** → **New registration**
2. Name your application (e.g., "Purview CLI Automation")
3. Click **Register**
4. Note the **Application (client) ID** and **Directory (tenant) ID**
5. Go to **Certificates & secrets** → **New client secret**
6. Create a secret and note the **Value** (this is your client secret)

### Using Azure CLI

```bash
# Create service principal
az ad sp create-for-rbac --name "PurviewCLI" --role Contributor --scopes /subscriptions/{subscription-id}

# Output will contain:
# - appId (Client ID)
# - tenant (Tenant ID)
# - password (Client Secret)
```

## Assigning Permissions to Service Principal

Your service principal needs appropriate permissions on the Purview account:

### Using Azure Portal

1. Navigate to your **Purview account**
2. Go to **Access control (IAM)**
3. Click **Add role assignment**
4. Select appropriate role:
   - **Data Curator** - Full data management permissions
   - **Data Reader** - Read-only access
   - **Data Source Administrator** - Manage data sources and scans
5. Assign to your service principal

### Using Azure CLI

```bash
# Get your Purview resource ID
PURVIEW_RESOURCE_ID="/subscriptions/{subscription-id}/resourceGroups/{resource-group}/providers/Microsoft.Purview/accounts/{purview-account}"

# Assign Data Curator role
az role assignment create \
  --assignee {service-principal-id} \
  --role "Purview Data Curator" \
  --scope $PURVIEW_RESOURCE_ID
```

### Using Purview Portal

1. Open **Purview Portal** (https://{account-name}.purview.azure.com)
2. Go to **Data map** → **Collections**
3. Select your root collection
4. Go to **Role assignments**
5. Add your service principal with appropriate role

## Environment Variables Reference

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `PURVIEW_ACCOUNT_NAME` | Your Purview account name | ✅ Yes | `my-purview-account` |
| `AZURE_CLIENT_ID` | Service Principal Client ID | For SP auth | `abc-123-def-456` |
| `AZURE_TENANT_ID` | Azure Tenant ID | For SP auth | `def-456-ghi-789` |
| `AZURE_CLIENT_SECRET` | Service Principal Secret | For SP auth | `secret-value` |

## Configuration File (Alternative)

You can also store configuration in a file:

**File: `~/.purviewcli/config.json`**

```json
{
  "purview_account_name": "my-purview-account",
  "azure_client_id": "your-client-id",
  "azure_tenant_id": "your-tenant-id",
  "azure_client_secret": "your-client-secret"
}
```

**Note:** Environment variables take precedence over config file values.

## Testing Authentication

### Quick Test

```bash
# List key vaults (requires minimal permissions)
pvw scan keyVaultList
```

### Comprehensive Test

```bash
# Test various endpoints
pvw scan listAll
pvw search query --query "*" --limit 1
pvw types read
```

## Troubleshooting

### Issue: "Authentication failed"

**Solutions:**
1. Verify environment variables are set correctly
2. Check service principal credentials
3. Ensure service principal has permissions on Purview account
4. Try `az login` if using Azure CLI auth

### Issue: "No subscription found"

**Solution:**
```bash
# List available subscriptions
az account list

# Set the correct subscription
az account set --subscription "subscription-id"
```

### Issue: "Insufficient permissions"

**Solution:**
- Assign appropriate Purview roles (Data Curator, Data Reader, etc.)
- Check both Azure RBAC and Purview collection-level permissions

### Issue: "Cannot find Purview account"

**Solution:**
```bash
# Verify account name
echo $PURVIEW_ACCOUNT_NAME

# Check if account exists
az purview account show --name $PURVIEW_ACCOUNT_NAME --resource-group {resource-group}
```

## Best Practices

### For Development

1. ✅ Use **Azure CLI** (`az login`) for interactive development
2. ✅ Keep credentials out of source control
3. ✅ Use `.env` files (add to `.gitignore`)
4. ✅ Test with minimal permissions first

### For Production/Automation

1. ✅ Use **Service Principal** authentication
2. ✅ Store secrets in Azure Key Vault
3. ✅ Use **Managed Identity** when running on Azure
4. ✅ Follow least privilege principle
5. ✅ Rotate secrets regularly

### Security

1. ⚠️ **Never** commit credentials to source control
2. ⚠️ **Never** hardcode secrets in scripts
3. ✅ Use Azure Key Vault for secret storage
4. ✅ Use environment variables or config files
5. ✅ Regularly audit service principal permissions

## Example Scripts

### Bash Script with Service Principal

```bash
#!/bin/bash
# authenticate.sh

# Load from .env file
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Verify required variables
if [ -z "$PURVIEW_ACCOUNT_NAME" ]; then
    echo "Error: PURVIEW_ACCOUNT_NAME not set"
    exit 1
fi

if [ -z "$AZURE_CLIENT_ID" ]; then
    echo "Error: AZURE_CLIENT_ID not set"
    exit 1
fi

# Test connection
echo "Testing connection to Purview..."
pvw scan keyVaultList

if [ $? -eq 0 ]; then
    echo "✅ Authentication successful!"
else
    echo "❌ Authentication failed!"
    exit 1
fi
```

### PowerShell Script with Service Principal

```powershell
# authenticate.ps1

# Load from .env file or set directly
$env:PURVIEW_ACCOUNT_NAME = "my-purview-account"
$env:AZURE_CLIENT_ID = "client-id"
$env:AZURE_TENANT_ID = "tenant-id"
$env:AZURE_CLIENT_SECRET = "client-secret"

# Test connection
Write-Host "Testing connection to Purview..." -ForegroundColor Yellow
$result = pvw scan keyVaultList 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Authentication successful!" -ForegroundColor Green
} else {
    Write-Host "❌ Authentication failed!" -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
    exit 1
}
```

### Using Azure Key Vault

```bash
#!/bin/bash
# authenticate_from_keyvault.sh

VAULT_NAME="my-keyvault"

# Retrieve secrets from Azure Key Vault
export AZURE_CLIENT_ID=$(az keyvault secret show --vault-name $VAULT_NAME --name "purview-client-id" --query value -o tsv)
export AZURE_TENANT_ID=$(az keyvault secret show --vault-name $VAULT_NAME --name "purview-tenant-id" --query value -o tsv)
export AZURE_CLIENT_SECRET=$(az keyvault secret show --vault-name $VAULT_NAME --name "purview-client-secret" --query value -o tsv)
export PURVIEW_ACCOUNT_NAME=$(az keyvault secret show --vault-name $VAULT_NAME --name "purview-account-name" --query value -o tsv)

# Now run your CLI commands
pvw scan keyVaultList
```

## CI/CD Integration

### Azure DevOps Pipeline

```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: purview-secrets  # Variable group with secrets

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.9'
  
  - script: |
      pip install purviewcli
    displayName: 'Install Purview CLI'
  
  - script: |
      export PURVIEW_ACCOUNT_NAME=$(PURVIEW_ACCOUNT_NAME)
      export AZURE_CLIENT_ID=$(AZURE_CLIENT_ID)
      export AZURE_TENANT_ID=$(AZURE_TENANT_ID)
      export AZURE_CLIENT_SECRET=$(AZURE_CLIENT_SECRET)
      pvw scan keyVaultList
    displayName: 'Run Purview CLI'
```

### GitHub Actions

```yaml
# .github/workflows/purview.yml
name: Purview CLI

on:
  push:
    branches: [ main ]

jobs:
  run-purview-cli:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install Purview CLI
        run: pip install purviewcli
      
      - name: Run Purview Commands
        env:
          PURVIEW_ACCOUNT_NAME: ${{ secrets.PURVIEW_ACCOUNT_NAME }}
          AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
          AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
          AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
        run: |
          pvw scan keyVaultList
```

## Additional Resources

- [Azure CLI Installation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Service Principal Documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
- [Managed Identity Documentation](https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)
- [Purview Permissions](https://docs.microsoft.com/en-us/azure/purview/catalog-permissions)

---

**Need Help?**
- Check the [troubleshooting section](#troubleshooting)
- Review [GitHub Issues](https://github.com/Keayoub/pvw-cli/issues)
- Consult the [main README](../../README.md)
