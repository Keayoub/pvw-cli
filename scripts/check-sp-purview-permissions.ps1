# Check Service Principal Purview Permissions
# Diagnoses if SP has correct roles and at which collection level

param(
    [string]$ClientId,
    [string]$TenantId,
    [string]$PurviewName = "ccq-pview-prod-01",
    [string]$ResourceGroup = "rg-purview-prod01",
    [string]$SubscriptionId
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Purview SP Permissions Diagnostic" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Get SP Object ID
Write-Host "[1/5] Getting Service Principal Object ID..." -ForegroundColor Yellow
if (-not $ClientId) {
    $ClientId = Read-Host "Enter Service Principal Client ID"
}
if (-not $TenantId) {
    $TenantId = Read-Host "Enter Tenant ID"
}

try {
    $spInfo = az ad sp show --id $ClientId --query "{objectId: objectId, appId: appId, displayName: displayName}" 2>&1 | ConvertFrom-Json
    $objectId = $spInfo.objectId
    $appId = $spInfo.appId
    $displayName = $spInfo.displayName
    
    Write-Host "  [OK] Service Principal found" -ForegroundColor Green
    Write-Host "    Display Name: $displayName" -ForegroundColor Cyan
    Write-Host "    App ID: $appId" -ForegroundColor Gray
    Write-Host "    Object ID: $objectId" -ForegroundColor Cyan
} catch {
    Write-Host "  [FAILED] Could not find Service Principal" -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Step 2: Check Azure RBAC permissions on resource group
Write-Host "[2/5] Checking Azure RBAC permissions on Purview resource group..." -ForegroundColor Yellow
if (-not $ResourceGroup) {
    $ResourceGroup = Read-Host "Enter Resource Group name"
}
if (-not $SubscriptionId) {
    $current = az account show --query "{subscriptionId: id}" 2>&1 | ConvertFrom-Json
    $SubscriptionId = $current.subscriptionId
}

$roleAssignments = az role assignment list --assignee $objectId --scope "/subscriptions/$SubscriptionId/resourceGroups/$ResourceGroup" 2>&1 | ConvertFrom-Json

if ($roleAssignments -and $roleAssignments.Count -gt 0) {
    Write-Host "  [OK] Service Principal has Azure RBAC roles:" -ForegroundColor Green
    foreach ($assignment in $roleAssignments) {
        Write-Host "    - $($assignment.roleDefinitionName)" -ForegroundColor Cyan
    }
} else {
    Write-Host "  [WARNING] No Azure RBAC roles assigned!" -ForegroundColor Yellow
    Write-Host "  SP should have Reader or Contributor on resource group" -ForegroundColor Gray
}
Write-Host ""

# Step 3: Get Purview account info
Write-Host "[3/5] Getting Purview account information..." -ForegroundColor Yellow
$purviewAccount = az purview account show --name $PurviewName --resource-group $ResourceGroup 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAILED] Could not find Purview account" -ForegroundColor Red
    exit 1
}
$purviewInfo = $purviewAccount | ConvertFrom-Json
$purviewId = $purviewInfo.id

Write-Host "  [OK] Purview account found" -ForegroundColor Green
Write-Host "    Name: $($purviewInfo.name)" -ForegroundColor Cyan
Write-Host "    ID: $purviewId" -ForegroundColor Gray
Write-Host ""

# Step 4: Check Purview-specific RBAC
Write-Host "[4/5] Checking Purview resource-level RBAC..." -ForegroundColor Yellow
$purviewRoleAssignments = az role assignment list --assignee $objectId --scope $purviewId 2>&1 | ConvertFrom-Json

if ($purviewRoleAssignments -and $purviewRoleAssignments.Count -gt 0) {
    Write-Host "  [OK] Service Principal has roles on Purview resource:" -ForegroundColor Green
    foreach ($assignment in $purviewRoleAssignments) {
        Write-Host "    - $($assignment.roleDefinitionName)" -ForegroundColor Cyan
    }
} else {
    Write-Host "  [INFO] No Azure RBAC roles on Purview resource (roles managed in Purview Portal)" -ForegroundColor Gray
}
Write-Host ""

# Step 5: Check Purview Domain-level permissions via REST API
Write-Host "[5/5] Checking Purview Domain-level permissions..." -ForegroundColor Yellow
Write-Host ""

Write-Host "  Getting access token..." -ForegroundColor Gray
$tokenResult = az account get-access-token --resource "https://purview.azure.net" 2>&1 | ConvertFrom-Json
$headers = @{
    "Authorization" = "Bearer $($tokenResult.accessToken)"
    "Content-Type" = "application/json"
}

# Get Purview metadata - this requires Data Curator or Collection Admin at Domain level
$purviewApiUrl = "https://$PurviewName.purview.azure.com/account"

try {
    $accountInfo = Invoke-RestMethod -Uri "$purviewApiUrl" -Headers $headers -Method GET -ErrorAction Stop
    
    Write-Host "  [OK] Successfully connected to Purview API" -ForegroundColor Green
    Write-Host "    Account: $($accountInfo.properties.friendlyName)" -ForegroundColor Cyan
    Write-Host "    Account ID: $($accountInfo.properties.objectId)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  [INFERENCE] Service Principal appears to have Domain-level access" -ForegroundColor Green
    
} catch {
    $errorMsg = $_.Exception.Message
    
    if ($errorMsg -match "403") {
        Write-Host "  [FAILED] Got 403 Forbidden from API" -ForegroundColor Red
        Write-Host "  This suggests permissions may be missing at Domain level" -ForegroundColor Yellow
    } else {
        Write-Host "  [WARNING] API call failed: $errorMsg" -ForegroundColor Yellow
    }
}

# Check collections list endpoint
Write-Host ""
Write-Host "  Checking Collection list access..." -ForegroundColor Gray
$collectionsUrl = "https://$PurviewName.purview.azure.com/collections?api-version=2021-07-01"

try {
    $collections = Invoke-RestMethod -Uri $collectionsUrl -Headers $headers -Method GET -ErrorAction Stop
    
    if ($collections.value) {
        Write-Host "  [OK] Can list collections - has Data Curator or Collection Admin at Domain level" -ForegroundColor Green
        Write-Host "    Collections accessible: $($collections.value.Count)" -ForegroundColor Gray
        
        # Show first 3 collections
        $collections.value | Select-Object -First 3 | ForEach-Object {
            Write-Host "      - $($_.name)" -ForegroundColor Gray
        }
    }
} catch {
    $errorMsg = $_.Exception.Message
    if ($errorMsg -match "403") {
        Write-Host "  [FAILED] Cannot list collections (403 Forbidden)" -ForegroundColor Red
        Write-Host "  SP does NOT have Data Curator or Collection Admin at Domain level" -ForegroundColor Yellow
    } else {
        Write-Host "  [WARNING] Error: $errorMsg" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Permission Check Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Service Principal Details:" -ForegroundColor Yellow
Write-Host "  Display Name: $displayName" -ForegroundColor Cyan
Write-Host "  Object ID: $objectId" -ForegroundColor Cyan
Write-Host "  App ID: $appId" -ForegroundColor Gray
Write-Host ""

Write-Host "Domain-Level Role Assignment:" -ForegroundColor Yellow
Write-Host "  To assign or verify Domain-level roles:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to Purview Portal:" -ForegroundColor Gray
Write-Host "   https://web.purview.azure.com" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Click 'Data map' > 'Collections' in left sidebar" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Click on 'Root' collection" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Go to 'Role assignments' tab" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Check if your SP is listed with:" -ForegroundColor Gray
Write-Host "   - Object ID: $objectId" -ForegroundColor Cyan
Write-Host "   - Role: Data Curator OR Collection Admin" -ForegroundColor Green
Write-Host ""

Write-Host "If 403 error on POST/PUT/DELETE:" -ForegroundColor Yellow
Write-Host "  1. Verify role is on ROOT collection (not sub-collection)" -ForegroundColor Gray
Write-Host "  2. Wait 5-10 minutes for role propagation" -ForegroundColor Gray
Write-Host "  3. Try Collection Admin if Data Curator doesn't work" -ForegroundColor Gray
Write-Host "  4. Check Purview audit logs for detailed error" -ForegroundColor Gray
Write-Host ""

exit 0
