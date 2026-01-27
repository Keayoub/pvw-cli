# Collections API - Permissions & Roles Requirements

## Overview

Creating collections in Microsoft Purview requires specific Azure RBAC roles and Purview-level permissions. The `pvw collections create` command needs both **Azure subscription-level permissions** AND **Purview account-level permissions**.

---

## 1. Azure Subscription Level Permissions

Your Service Principal must have these Azure roles on the **Purview Account** resource:

### Option A: Full Admin Access (Recommended for Development/Testing)
```
Role: Owner
Scope: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{purviewAccountName}
```

### Option B: Contributor Access (Recommended for Production)
```
Role: Contributor
Scope: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{purviewAccountName}
```

### Option C: Minimal Required Permissions (Least Privilege)
```
Role: Custom Role with these actions:
- Microsoft.Purview/accounts/read
- Microsoft.Purview/accounts/write
- Microsoft.Purview/accounts/collectionWrite  (if available)
- Microsoft.Authorization/roleAssignments/read
Scope: Purview Account resource
```

---

## 2. Purview Account Level Permissions

Even with Azure RBAC roles, you need **Purview-level permissions** within the Purview account:

### Required Purview Role(s)

You need ONE of these Purview Data Plane roles:

| Role | Create Collections | Manage Permissions | Modify Assets |
|------|-------------------|-------------------|---------------|
| **Purview Data Source Administrator** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Purview Collection Administrator** | ✅ Yes | ✅ Yes | ⚠️ Limited |
| **Purview Data Curator** | ❌ No | ❌ No | ✅ Yes |
| **Purview Data Reader** | ❌ No | ❌ No | ❌ No |

### How to Assign Purview Roles

**Via Azure Portal:**
1. Navigate to your **Purview account**
2. Click **Access Control (IAM)** in the left menu
3. Click **+ Add** → **Add role assignment**
4. Select **Purview Data Source Administrator** (or Collection Administrator)
5. Select your **Service Principal**
6. Click **Review + Assign**

**Via PowerShell:**
```powershell
# Get Purview account
$purviewAccount = Get-AzPurviewAccount -ResourceGroupName $resourceGroupName -Name $purviewAccountName

# Add service principal to Purview role
$servicePrincipalObjectId = "your-sp-object-id"
$purviewAccount | New-AzRoleAssignment `
  -ObjectId $servicePrincipalObjectId `
  -RoleDefinitionName "Purview Data Source Administrator"
```

**Via Azure CLI:**
```bash
# Get your service principal's object ID
SP_OBJECT_ID=$(az ad sp show --id $AZURE_CLIENT_ID --query id -o tsv)

# Assign Purview role
az role assignment create \
  --role "Purview Data Source Administrator" \
  --assignee $SP_OBJECT_ID \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG_NAME/providers/Microsoft.Purview/accounts/$PURVIEW_ACCOUNT"
```

---

## 3. Complete Permission Checklist

### ✅ Prerequisites
- [ ] Service Principal is created in Azure AD
- [ ] Service Principal has a valid client secret
- [ ] Service Principal's **Object ID** is noted (not Application ID)
- [ ] Service Principal's **Client ID** and **Tenant ID** are noted

### ✅ Azure Subscription Level (Required)
- [ ] Service Principal has **Owner** OR **Contributor** role on Purview account
- [ ] Role assignment is active (may take 5-10 minutes to propagate)
- [ ] Test with: `az role assignment list --assignee <SP_OBJECT_ID> --scope <PURVIEW_RESOURCE_ID>`

### ✅ Purview Account Level (Required)
- [ ] Service Principal has **Purview Data Source Administrator** role
- [ ] OR Service Principal has **Collection Administrator** role
- [ ] Role is assigned at the **root collection** or higher
- [ ] Wait 5-10 minutes for permission propagation

### ✅ Authentication Setup
- [ ] `AZURE_CLIENT_ID` environment variable is set
- [ ] `AZURE_TENANT_ID` environment variable is set
- [ ] `AZURE_CLIENT_SECRET` environment variable is set
- [ ] `PURVIEW_ACCOUNT_NAME` environment variable is set (format: `account-name`, NOT full URL)

### ✅ Network & Connectivity
- [ ] Network can reach Purview API endpoints
- [ ] Firewall/NSG allows outbound HTTPS (port 443)
- [ ] No MFA restrictions on Service Principal
- [ ] Managed Identity is enabled (if using MI instead of SP)

---

## 4. Troubleshooting "HTTP 403" Errors

### Symptom
```
HTTP 403: Forbidden
collections create failed
```

### Root Causes & Solutions

#### 4.1 Missing Purview Role Assignment
**Check if role is assigned:**
```powershell
# PowerShell - Check Purview roles
$purviewAccount = Get-AzPurviewAccount -ResourceGroupName $rg -Name $purviewName
Get-AzRoleAssignment -ObjectId $servicePrincipalObjectId -Scope $purviewAccount.Id
```

**Expected output:**
```
RoleDefinitionName      : Purview Data Source Administrator
Scope                   : /subscriptions/.../providers/Microsoft.Purview/accounts/...
```

**If missing:** Add the role (see section 2 above)

#### 4.2 Insufficient Azure RBAC Role
**Check current Azure role:**
```bash
az role assignment list \
  --assignee $AZURE_CLIENT_ID \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG/providers/Microsoft.Purview/accounts/$ACCOUNT"
```

**Expected output:**
```json
{
  "roleDefinitionName": "Contributor"
}
```

**If missing or insufficient:** Upgrade to **Contributor** or **Owner** role

#### 4.3 Permission Propagation Delay
Azure role assignments can take **5-10 minutes** to propagate:
- Wait and retry after 10 minutes
- Restart the CLI session
- Logout and login again with `az login`

#### 4.4 Wrong Purview Account Name
**Verify account name:**
```bash
az purview account list --resource-group $RG_NAME --query "[].name"
```

**Set environment variable correctly:**
```powershell
$env:PURVIEW_ACCOUNT_NAME = "my-purview-account"  # NOT "my-purview-account.purview.azure.com"
```

#### 4.5 Service Principal Not Registered in Tenant
**Error:**
```
AADSTS500011: The resource principal named ... was not found in the tenant
```

**Solution:**
```bash
# Register Purview service principal in your tenant
az ad sp create --id 73c2949e-da2d-457a-9607-fcc665198967
```

---

## 5. Full Permission Setup Script

### PowerShell Script - Complete Setup
```powershell
# Configuration
$subscriptionId = "your-subscription-id"
$resourceGroupName = "your-resource-group"
$purviewAccountName = "your-purview-account"
$servicePrincipalAppId = "your-app-id"
$servicePrincipalDisplayName = "your-sp-display-name"

# Step 1: Set Azure context
Set-AzContext -SubscriptionId $subscriptionId

# Step 2: Get Service Principal Object ID
$sp = Get-AzADServicePrincipal -ApplicationId $servicePrincipalAppId
$spObjectId = $sp.Id
Write-Host "Service Principal Object ID: $spObjectId"

# Step 3: Get Purview account resource ID
$purviewAccount = Get-AzPurviewAccount `
  -ResourceGroupName $resourceGroupName `
  -Name $purviewAccountName
$purviewResourceId = $purviewAccount.Id
Write-Host "Purview Account Resource ID: $purviewResourceId"

# Step 4: Assign Azure RBAC role (Contributor)
Write-Host "Assigning Contributor role..."
New-AzRoleAssignment `
  -ObjectId $spObjectId `
  -RoleDefinitionName "Contributor" `
  -Scope $purviewResourceId -ErrorAction SilentlyContinue

# Step 5: Assign Purview Data Source Administrator role
Write-Host "Assigning Purview Data Source Administrator role..."
# Note: This typically requires the Azure Portal as there's no direct PowerShell cmdlet
Write-Host "Please manually assign 'Purview Data Source Administrator' role via Azure Portal"
Write-Host "1. Go to Purview Account > Access Control (IAM)"
Write-Host "2. Add role assignment > Purview Data Source Administrator"
Write-Host "3. Select your service principal"

# Step 6: Verify assignments
Write-Host "`nVerifying role assignments..."
Get-AzRoleAssignment `
  -ObjectId $spObjectId `
  -Scope $purviewResourceId

Write-Host "`nSetup complete! Wait 5-10 minutes for permissions to propagate."
Write-Host "Then test with: pvw collections create --collection-name test-collection"
```

### Bash/Azure CLI Script - Complete Setup
```bash
#!/bin/bash

# Configuration
SUBSCRIPTION_ID="your-subscription-id"
RESOURCE_GROUP="your-resource-group"
PURVIEW_ACCOUNT="your-purview-account"
SP_APP_ID="your-app-id"
SP_DISPLAY_NAME="your-sp-display-name"

# Step 1: Set Azure context
az account set --subscription $SUBSCRIPTION_ID

# Step 2: Get Service Principal Object ID
SP_OBJECT_ID=$(az ad sp show --id $SP_APP_ID --query id -o tsv)
echo "Service Principal Object ID: $SP_OBJECT_ID"

# Step 3: Get Purview account resource ID
PURVIEW_RESOURCE_ID=$(az purview account show \
  --resource-group $RESOURCE_GROUP \
  --name $PURVIEW_ACCOUNT \
  --query id -o tsv)
echo "Purview Account Resource ID: $PURVIEW_RESOURCE_ID"

# Step 4: Assign Azure RBAC role (Contributor)
echo "Assigning Contributor role..."
az role assignment create \
  --assignee-object-id $SP_OBJECT_ID \
  --role "Contributor" \
  --scope $PURVIEW_RESOURCE_ID

# Step 5: Assign Purview role via Portal
echo "Please manually assign 'Purview Data Source Administrator' role via Azure Portal:"
echo "1. Go to Purview Account > Access Control (IAM)"
echo "2. Add role assignment > Purview Data Source Administrator"
echo "3. Select service principal: $SP_DISPLAY_NAME"

# Step 6: Verify assignments
echo -e "\nVerifying role assignments..."
az role assignment list \
  --assignee-object-id $SP_OBJECT_ID \
  --scope $PURVIEW_RESOURCE_ID

echo -e "\nSetup complete! Wait 5-10 minutes for permissions to propagate."
echo "Then test with: pvw collections create --collection-name test-collection"
```

---

## 6. Verification Commands

### Verify Azure RBAC Roles
```powershell
# PowerShell
$sp = Get-AzADServicePrincipal -ApplicationId $AZURE_CLIENT_ID
$assignments = Get-AzRoleAssignment -ObjectId $sp.Id
$assignments | Select RoleDefinitionName, Scope
```

```bash
# Bash
SP_OBJECT_ID=$(az ad sp show --id $AZURE_CLIENT_ID --query id -o tsv)
az role assignment list --assignee-object-id $SP_OBJECT_ID --output table
```

### Verify Purview Permissions
```powershell
# Check if you can list collections (basic permission test)
pvw collections list
```

```bash
# If successful, you have at least read permissions
pvw collections list

# Try creating a test collection (requires full permissions)
pvw collections create --collection-name "test-perms-$(Get-Random)" --friendly-name "Test"
```

### Debug 403 Errors
```powershell
# PowerShell with detailed error output
$env:LOGLEVEL = "DEBUG"
pvw collections create --collection-name test-collection --friendly-name "Test Collection"
```

```bash
# Bash with error details
LOGLEVEL=DEBUG pvw collections create --collection-name test-collection --friendly-name "Test Collection"
```

---

## 7. Common Issues Summary

| Issue | Symptom | Solution |
|-------|---------|----------|
| Missing Purview Role | HTTP 403 Forbidden | Assign **Purview Data Source Administrator** role |
| Insufficient Azure RBAC | HTTP 403 Forbidden | Upgrade to **Contributor** or **Owner** role |
| Wrong Account Name | Collection not found | Use account name only, not full URL |
| Permissions Not Propagated | HTTP 403 even after assignment | Wait 5-10 minutes and retry |
| SP Not Registered | AADSTS500011 | Run `az ad sp create --id 73c2949e-da2d-457a-9607-fcc665198967` |
| Network/Firewall | Connection timeout | Verify outbound HTTPS access to Purview endpoints |

---

## 8. References

- **Microsoft Purview Collections API:** https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/collections
- **Azure RBAC Roles:** https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
- **Purview Data Plane Roles:** https://learn.microsoft.com/en-us/azure/purview/catalog-permissions
- **Service Principal Setup:** https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal

---

## 9. Getting Help

If you're still experiencing issues after checking all permissions:

1. **Enable debug logging:**
   ```bash
   export LOGLEVEL=DEBUG
   pvw collections create --collection-name test --friendly-name Test
   ```

2. **Check the error code:**
   - **403 Forbidden** → Permission issue (see section 4)
   - **401 Unauthorized** → Authentication issue
   - **400 Bad Request** → Invalid parameters
   - **409 Conflict** → Resource already exists

3. **Contact Support:**
   - Provide error logs and HTTP status codes
   - Include account configuration (sanitized)
   - Share the exact command that's failing
