# Create and Configure Service Principal for Purview CLI
# This script creates a new Service Principal, generates credentials, and assigns necessary roles
# Usage: .\create-service-principal.ps1 -PurviewName "your-purview" -ResourceGroup "rg-purview"

param(
    [Parameter(Mandatory=$true)]
    [string]$PurviewName,
    
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup,
    
    [string]$ServicePrincipalName = "sp-purview-cli-$PurviewName",
    
    [ValidateSet("DataCurator", "DataReader", "DataSourceAdmin", "CollectionAdmin")]
    [string[]]$Roles = @("DataCurator"),
    
    [int]$SecretExpirationDays = 365,
    
    [switch]$SkipRoleAssignment = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Principal Creation for Purview" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Azure CLI is installed
Write-Host "[1/7] Checking prerequisites..." -ForegroundColor Yellow
$azCheck = Get-Command az -ErrorAction SilentlyContinue
if (-not $azCheck) {
    Write-Host "[FAILED] Azure CLI is not installed" -ForegroundColor Red
    Write-Host "Install from: https://aka.ms/installazurecliwindows" -ForegroundColor Yellow
    exit 1
}
Write-Host "  [OK] Azure CLI found" -ForegroundColor Green

# Check if logged in
$azAccount = az account show 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAILED] Not logged in to Azure CLI" -ForegroundColor Red
    Write-Host "Please run: az login" -ForegroundColor Yellow
    exit 1
}
$accountInfo = $azAccount | ConvertFrom-Json
Write-Host "  [OK] Logged in as: $($accountInfo.user.name)" -ForegroundColor Green
Write-Host "  Subscription: $($accountInfo.name)" -ForegroundColor Gray
Write-Host ""

# Get Purview account details
Write-Host "[2/7] Getting Purview account details..." -ForegroundColor Yellow
$purviewAccount = az purview account show --name $PurviewName --resource-group $ResourceGroup 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAILED] Could not find Purview account '$PurviewName' in resource group '$ResourceGroup'" -ForegroundColor Red
    Write-Host $purviewAccount
    exit 1
}
$purviewInfo = $purviewAccount | ConvertFrom-Json
$purviewResourceId = $purviewInfo.id
Write-Host "  [OK] Found Purview: $PurviewName" -ForegroundColor Green
Write-Host "  Resource ID: $purviewResourceId" -ForegroundColor Gray
Write-Host ""

# Create Service Principal
Write-Host "[3/7] Creating Service Principal..." -ForegroundColor Yellow
Write-Host "  Name: $ServicePrincipalName" -ForegroundColor Gray

# Check if SP already exists
$existingSP = az ad sp list --display-name $ServicePrincipalName 2>&1 | ConvertFrom-Json
if ($existingSP -and $existingSP.Count -gt 0) {
    Write-Host "  [WARNING] Service Principal already exists" -ForegroundColor Yellow
    $spInfo = $existingSP[0]
    $appId = $spInfo.appId
    Write-Host "  App ID: $appId" -ForegroundColor Gray
    
    $useExisting = Read-Host "Use existing Service Principal? (Y/N)"
    if ($useExisting -ne "Y" -and $useExisting -ne "y") {
        Write-Host "  [ABORTED] Please use a different name" -ForegroundColor Yellow
        exit 1
    }
} else {
    # Create new SP
    $spCreate = az ad sp create-for-rbac --name $ServicePrincipalName --skip-assignment 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAILED] Could not create Service Principal" -ForegroundColor Red
        Write-Host $spCreate
        exit 1
    }
    $spInfo = $spCreate | ConvertFrom-Json
    $appId = $spInfo.appId
    $clientSecret = $spInfo.password
    $tenantId = $spInfo.tenant
    
    Write-Host "  [OK] Service Principal created" -ForegroundColor Green
    Write-Host "  App ID (Client ID): $appId" -ForegroundColor Cyan
    Write-Host "  Tenant ID: $tenantId" -ForegroundColor Gray
    Write-Host "  Client Secret: $clientSecret" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [IMPORTANT] Save these credentials securely!" -ForegroundColor Red
    Write-Host ""
}
Write-Host ""

# Register Purview Service Principal in tenant (if not already)
Write-Host "[4/7] Registering Purview Service Principal in tenant..." -ForegroundColor Yellow
$purviewSPAppId = "73c2949e-da2d-457a-9607-fcc665198967"
$purviewSP = az ad sp show --id $purviewSPAppId 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Creating Purview Service Principal registration..." -ForegroundColor Gray
    az ad sp create --id $purviewSPAppId 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Purview Service Principal registered" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Could not register Purview SP (may require admin consent)" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [OK] Purview Service Principal already registered" -ForegroundColor Green
}
Write-Host ""

# Assign roles to Service Principal on Purview
if (-not $SkipRoleAssignment) {
    Write-Host "[5/7] Assigning roles to Service Principal..." -ForegroundColor Yellow
    
    $roleMapping = @{
        "DataCurator" = "Data Curator"
        "DataReader" = "Data Reader"
        "DataSourceAdmin" = "Data Source Administrator"
        "CollectionAdmin" = "Collection Admin"
    }
    
    foreach ($role in $Roles) {
        $purviewRole = $roleMapping[$role]
        Write-Host "  Assigning role: $purviewRole" -ForegroundColor Gray
        
        # Note: Purview roles are assigned via Purview UI or REST API, not Azure RBAC
        Write-Host "  [INFO] Purview roles must be assigned via Purview Portal" -ForegroundColor Yellow
        Write-Host "    1. Go to: https://portal.azure.com/#view/Microsoft_Azure_Purview/PurviewResourceOverviewBlade/resourceId/$([uri]::EscapeDataString($purviewResourceId))/view~/root-collections" -ForegroundColor Gray
        Write-Host "    2. Click 'Root Collection' > 'Role assignments'" -ForegroundColor Gray
        Write-Host "    3. Add Service Principal: $ServicePrincipalName" -ForegroundColor Gray
        Write-Host "    4. Assign role: $purviewRole" -ForegroundColor Gray
    }
    
    # Assign Azure RBAC Reader role on the resource group (for metadata read)
    Write-Host ""
    Write-Host "  Assigning Azure RBAC Reader role on resource group..." -ForegroundColor Gray
    az role assignment create --assignee $appId --role "Reader" --scope "/subscriptions/$($accountInfo.id)/resourceGroups/$ResourceGroup" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] Azure Reader role assigned" -ForegroundColor Green
    } else {
        Write-Host "  [WARNING] Could not assign Azure Reader role" -ForegroundColor Yellow
    }
} else {
    Write-Host "[5/7] Skipping role assignment (use -SkipRoleAssignment:$false to enable)" -ForegroundColor Gray
}
Write-Host ""

# Generate client secret (if not already created)
if (-not $clientSecret) {
    Write-Host "[6/7] Generating new client secret..." -ForegroundColor Yellow
    $secretName = "purview-cli-secret-$(Get-Date -Format 'yyyyMMdd')"
    $endDate = (Get-Date).AddDays($SecretExpirationDays).ToString("yyyy-MM-dd")
    
    $secretCreate = az ad app credential reset --id $appId --append --display-name $secretName --end-date $endDate 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAILED] Could not create client secret" -ForegroundColor Red
        Write-Host $secretCreate
        exit 1
    }
    $secretInfo = $secretCreate | ConvertFrom-Json
    $clientSecret = $secretInfo.password
    $tenantId = $secretInfo.tenant
    
    Write-Host "  [OK] Client secret generated" -ForegroundColor Green
    Write-Host "  Secret: $clientSecret" -ForegroundColor Cyan
    Write-Host "  Expires: $endDate" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [IMPORTANT] Save this secret - you won't be able to retrieve it again!" -ForegroundColor Red
}
Write-Host ""

# Configure environment variables
Write-Host "[7/7] Configuring environment variables..." -ForegroundColor Yellow
if (-not $tenantId) {
    $tenantId = $accountInfo.tenantId
}

$env:AZURE_CLIENT_ID = $appId
$env:AZURE_CLIENT_SECRET = $clientSecret
$env:AZURE_TENANT_ID = $tenantId
$env:PURVIEW_NAME = $PurviewName
$env:PURVIEW_ACCOUNT_NAME = $PurviewName
$env:PURVIEW_RESOURCE_GROUP = $ResourceGroup

Write-Host "  [OK] Environment variables configured" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Principal Configuration Complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Credentials (save these securely):" -ForegroundColor Yellow
Write-Host "  AZURE_CLIENT_ID: $appId" -ForegroundColor Cyan
Write-Host "  AZURE_CLIENT_SECRET: $clientSecret" -ForegroundColor Cyan
Write-Host "  AZURE_TENANT_ID: $tenantId" -ForegroundColor Cyan
Write-Host ""
Write-Host "Purview Configuration:" -ForegroundColor Yellow
Write-Host "  PURVIEW_NAME: $PurviewName" -ForegroundColor Gray
Write-Host "  PURVIEW_RESOURCE_GROUP: $ResourceGroup" -ForegroundColor Gray
Write-Host ""

# Save credentials to file (optional)
$saveToFile = Read-Host "Save credentials to file? (Y/N)"
if ($saveToFile -eq "Y" -or $saveToFile -eq "y") {
    $credFile = "purview-sp-credentials-$(Get-Date -Format 'yyyyMMddHHmmss').txt"
    @"
Service Principal Credentials for Purview CLI
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

AZURE_CLIENT_ID=$appId
AZURE_CLIENT_SECRET=$clientSecret
AZURE_TENANT_ID=$tenantId
PURVIEW_NAME=$PurviewName
PURVIEW_RESOURCE_GROUP=$ResourceGroup
PURVIEW_AUTH_SCOPE=https://purview.azure.net/.default

PowerShell Configuration:
`$env:AZURE_CLIENT_ID = "$appId"
`$env:AZURE_CLIENT_SECRET = "$clientSecret"
`$env:AZURE_TENANT_ID = "$tenantId"
`$env:PURVIEW_NAME = "$PurviewName"
`$env:PURVIEW_RESOURCE_GROUP = "$ResourceGroup"
`$env:PURVIEW_AUTH_SCOPE = "https://purview.azure.net/.default"

Next Steps:
1. Assign Purview roles in the Purview Portal (see instructions above)
2. Test with: pvw account get-account
"@ | Out-File -FilePath $credFile -Encoding UTF8
    
    Write-Host "[OK] Credentials saved to: $credFile" -ForegroundColor Green
    Write-Host "[WARNING] Keep this file secure and delete after use!" -ForegroundColor Red
}
Write-Host ""

# Test connection
$testNow = Read-Host "Test connection now? (Y/N)"
if ($testNow -eq "Y" -or $testNow -eq "y") {
    Write-Host ""
    Write-Host "Testing connection to Purview..." -ForegroundColor Yellow
    
    # Check if pvw-cli is installed
    $pvwCheck = Get-Command pvw -ErrorAction SilentlyContinue
    if (-not $pvwCheck) {
        Write-Host "[WARNING] pvw-cli is not installed" -ForegroundColor Yellow
        Write-Host "Install with: pip install pvw-cli" -ForegroundColor Gray
    } else {
        $testResult = pvw account get-account 2>&1 | Out-String
        if ($testResult -match "friendlyName") {
            Write-Host "[OK] Successfully connected to Purview!" -ForegroundColor Green
        } else {
            Write-Host "[FAILED] Connection test failed" -ForegroundColor Red
            Write-Host "This is expected if you haven't assigned Purview roles yet" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Output:" -ForegroundColor Gray
            Write-Host $testResult
        }
    }
}
Write-Host ""
Write-Host "Done!" -ForegroundColor Green
