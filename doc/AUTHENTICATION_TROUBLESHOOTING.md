# Purview CLI Authentication Troubleshooting Guide

## Overview

The Purview CLI now includes specific error handling for authentication issues. When you encounter authentication errors, the CLI will provide detailed messages explaining the problem and suggested solutions.

## Common Authentication Errors

### 1. **Service Principal Not Registered** (AADSTS500011)

**Error Message:**
```
The Purview service principal is not registered in your Azure AD tenant.
Your Azure AD administrator must register the service principal.
Ask them to run: New-AzureADServicePrincipal -AppId 73c2949e-da2d-457a-9607-fcc665198967
```

**Cause:** The Purview service principal application is not installed in your Azure AD tenant.

**Solution:**
- Ask your Azure AD **Global Administrator** or **Application Administrator** to register the service principal:
  ```powershell
  # PowerShell command (requires AzureAD module)
  New-AzureADServicePrincipal -AppId 73c2949e-da2d-457a-9607-fcc665198967
  ```

  Or via Azure CLI:
  ```bash
  az ad sp create --id 73c2949e-da2d-457a-9607-fcc665198967
  ```

---

### 2. **Azure CLI Not Found**

**Error Message:**
```
Azure CLI (az) not found
```

**Cause:** The Azure CLI is not installed or not available on your system PATH.

**Solution:**
- Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
- On Windows, use the MSI installer or Windows Package Manager:
  ```powershell
  winget install Microsoft.AzureCLI
  ```

---

### 3. **Not Logged In with Azure CLI**

**Error Message:**
```
Azure CLI authentication failed. 
Please ensure you are logged in with 'az login' and have the necessary permissions to access Purview.
```

**Cause:** You haven't authenticated with Azure CLI yet.

**Solution:**
- Run the login command:
  ```bash
  az login
  ```
- For specific tenant:
  ```bash
  az login --tenant "your-tenant-id"
  ```

---

### 4. **Service Principal Credentials Invalid**

**Error Message:**
```
Service principal authentication failed: ...
```

**Cause:** The service principal credentials are invalid or expired.

**Solution:**
- Verify your environment variables are correctly set:
  ```bash
  echo $AZURE_CLIENT_ID
  echo $AZURE_TENANT_ID
  # Don't echo AZURE_CLIENT_SECRET for security!
  ```

- Ensure the service principal exists and has valid credentials
- For interactive login, remove the env variables and use `az login` instead

---

### 5. **Insufficient Permissions**

**Error Message:**
```
HTTP 403: ...
```

**Cause:** Your account doesn't have the necessary permissions on the Purview resource.

**Solution:**
- Ensure your account has one of these roles on the Purview resource:
  - **Purview Data Reader** - minimum, for read access
  - **Purview Data Curator** - to create and modify
  - **Purview Data Source Administrator** - to manage data sources

- Check assignments in the Azure Portal:
  1. Go to your Purview account
  2. Access Control (IAM)
  3. Check your user/service principal has appropriate role

---

## Authentication Methods (In Priority Order)

The CLI tries authentication methods in this order:

### 1. **Service Principal (Environment Variables)**
```bash
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"
```

### 2. **Azure CLI** (`az login`)
```bash
az login
```

### 3. **DefaultAzureCredential** (Fallback)
- Managed Identity (Azure VMs, App Service)
- VS Code extension
- System credentials

---

## Debugging

### Enable Debug Logging

Set the `LOGLEVEL` environment variable:

```bash
# Bash/Linux
export LOGLEVEL=DEBUG
pvw account get-account

# PowerShell
$env:LOGLEVEL='DEBUG'
pvw account get-account
```

### Common Debug Outputs

**Successful Authentication:**
```
[DEBUG] Attempting authentication with Azure CLI
[DEBUG] Successfully obtained token from Azure CLI
[INFO] Successfully authenticated using Azure CLI for Purview API
```

**Failed Authentication:**
```
[DEBUG] Attempting authentication with Azure CLI
[DEBUG] Azure CLI returned code 1: AADSTS500011: The resource principal...
[ERROR] Service principal not registered: The Purview service principal is not registered...
```

---

## Network Troubleshooting

If you're getting connectivity errors on a VM with VNet:

### 1. Verify Firewall Rules
```bash
# Test connectivity to Purview endpoint
ping your-account.purview.azure.net
nslookup your-account.purview.azure.net
```

### 2. Check Private Endpoint Configuration
- If using Private Endpoint, ensure DNS resolves to private IP
- Verify NSG rules allow HTTPS (port 443)

### 3. Test with Azure CLI
```bash
# This will test basic connectivity
az account get-access-token --resource "https://purview.azure.net"
```

---

## Getting Help

If you continue to experience authentication issues:

1. Run with `--debug` flag to see detailed logs
2. Check the error message for the specific AADSTS code
3. Search Azure AD error codes: https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-aadsts-error-codes
4. Verify your tenant configuration with Azure AD administrator
5. Check Purview resource permissions in Azure Portal

---

## Related Resources

- [Azure Purview Authentication](https://learn.microsoft.com/en-us/purview/tutorial-using-rest-apis)
- [Azure CLI Authentication](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli)
- [Service Principal Setup](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal)
