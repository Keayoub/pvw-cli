# Diagnose 403 Forbidden on Collection Operations
# This script checks for restricted inheritance and permission propagation issues

param(
    [string]$ClientId,
    [string]$ClientSecret,
    [string]$TenantId,
    [string]$PurviewName = "ccq-pview-prod-01",
    [string]$CollectionName = "yfwy2c"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Collection 403 Forbidden Diagnostic" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Configure credentials
if (-not $ClientId) {
    $ClientId = $env:AZURE_CLIENT_ID
    if (-not $ClientId) {
        $ClientId = Read-Host "Enter Service Principal Client ID"
    }
}
if (-not $ClientSecret) {
    $ClientSecret = $env:AZURE_CLIENT_SECRET
    if (-not $ClientSecret) {
        $SecureSecret = Read-Host "Enter Service Principal Client Secret" -AsSecureString
        $ClientSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($SecureSecret))
    }
}
if (-not $TenantId) {
    $TenantId = $env:AZURE_TENANT_ID
    if (-not $TenantId) {
        $TenantId = Read-Host "Enter Tenant ID"
    }
}

Write-Host "[1/5] Getting Service Principal Object ID..." -ForegroundColor Yellow
try {
    $spInfo = az ad sp show --id $ClientId --query "{objectId: objectId, displayName: displayName}" 2>&1 | ConvertFrom-Json
    $objectId = $spInfo.objectId
    Write-Host "  [OK] SP: $($spInfo.displayName)" -ForegroundColor Green
    Write-Host "  Object ID: $objectId" -ForegroundColor Cyan
} catch {
    Write-Host "  [FAILED] Could not get SP info" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Get access token
Write-Host "[2/5] Getting Purview access token..." -ForegroundColor Yellow
$tokenResult = az account get-access-token --resource "https://purview.azure.net" 2>&1 | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    Write-Host "  [FAILED] Could not get access token" -ForegroundColor Red
    exit 1
}
Write-Host "  [OK] Token obtained" -ForegroundColor Green
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $($tokenResult.accessToken)"
    "Content-Type" = "application/json"
}

# Step 3: Get collection metadata policy
Write-Host "[3/5] Checking collection permissions policy..." -ForegroundColor Yellow
$policyUrl = "https://$PurviewName.purview.azure.com/policystore/metadataPolicies?api-version=2021-07-01"

try {
    $policies = Invoke-RestMethod -Uri $policyUrl -Headers $headers -Method GET -ErrorAction Stop
    
    # Find policy for this collection
    $collectionPolicy = $policies.values | Where-Object { 
        $_.properties.collection.referenceName -eq $CollectionName 
    } | Select-Object -First 1
    
    if ($collectionPolicy) {
        Write-Host "  [OK] Found policy for collection: $CollectionName" -ForegroundColor Green
        
        # Check if inheritance is restricted
        $parentCollectionName = $collectionPolicy.properties.parentCollectionName
        Write-Host "  Parent collection: $parentCollectionName" -ForegroundColor Gray
        
        # Check if SP is in Collection Admin role
        $collectionAdminRule = $collectionPolicy.properties.attributeRules | Where-Object {
            $_.id -like "*collection-administrator:$CollectionName"
        }
        
        if ($collectionAdminRule) {
            $spInAdmins = $collectionAdminRule.dnfCondition | ForEach-Object {
                $_ | Where-Object { 
                    $_.attributeName -eq "principal.microsoft.id" -and 
                    $_.attributeValueIncludedIn -contains $objectId 
                }
            }
            
            if ($spInAdmins) {
                Write-Host "  [OK] SP is Collection Admin on this collection" -ForegroundColor Green
            } else {
                Write-Host "  [WARNING] SP NOT in Collection Admin role directly" -ForegroundColor Yellow
                Write-Host "  May be inheriting from parent collection" -ForegroundColor Gray
            }
        }
        
        # Check for inherited permissions
        Write-Host ""
        Write-Host "  Checking inherited permissions..." -ForegroundColor Gray
        
        # Look for inheritance indicators
        $hasInheritedRules = $collectionPolicy.properties.attributeRules | Where-Object {
            $_.dnfCondition | ForEach-Object {
                $_ | Where-Object { $_.fromRule -like "*:$parentCollectionName" }
            }
        }
        
        if ($hasInheritedRules) {
            Write-Host "  [OK] Collection inherits permissions from parent" -ForegroundColor Green
        } else {
            Write-Host "  [WARNING] Inheritance may be RESTRICTED!" -ForegroundColor Red
            Write-Host "  This means parent permissions don't apply here" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  [WARNING] Could not find policy for collection: $CollectionName" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "  [FAILED] Error getting policies: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Step 4: Test actual write operation
Write-Host "[4/5] Testing write operation on collection..." -ForegroundColor Yellow
$testCollectionName = "test-diag-$(Get-Date -Format 'yyyyMMddHHmmss')"

$createResult = pvw collections create `
    --collection-name $testCollectionName `
    --parent-collection $CollectionName `
    --friendly-name "Test Diagnostic Collection" 2>&1 | Out-String

if ($createResult -match "403" -or $createResult -match "Forbidden") {
    Write-Host "  [FAILED] Got 403 Forbidden - Permission denied" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Root cause analysis:" -ForegroundColor Yellow
    Write-Host "  1. Permissions are RESTRICTED on collection '$CollectionName'" -ForegroundColor Red
    Write-Host "  2. Service Principal must be added DIRECTLY to this collection" -ForegroundColor Yellow
    Write-Host "  3. Inherited permissions from Domain/parent are being blocked" -ForegroundColor Gray
} elseif ($createResult -match "401") {
    Write-Host "  [FAILED] Got 401 Unauthorized - Token/auth issue" -ForegroundColor Red
} elseif ($createResult -match '"name"' -or $createResult -match "Succeeded") {
    Write-Host "  [OK] Collection created successfully!" -ForegroundColor Green
    Write-Host "  This means permissions are working correctly" -ForegroundColor Gray
    
    # Clean up
    Write-Host "  Cleaning up test collection..." -ForegroundColor Gray
    pvw collections delete --collection-name $testCollectionName 2>&1 | Out-Null
} else {
    Write-Host "  [UNKNOWN] Unexpected response:" -ForegroundColor Yellow
    Write-Host $createResult
}
Write-Host ""

# Step 5: Provide fix instructions
Write-Host "[5/5] Fix Instructions..." -ForegroundColor Yellow
Write-Host ""

Write-Host "SOLUTION for 403 Forbidden:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Gray
Write-Host ""

Write-Host "1. Go to Purview Portal:" -ForegroundColor Yellow
Write-Host "   https://web.purview.azure.com" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Navigate to Collection:" -ForegroundColor Yellow
Write-Host "   Data Map > Collections > $CollectionName" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Check 'Restrict inherited permissions':" -ForegroundColor Yellow
Write-Host "   - Go to 'Role assignments' tab" -ForegroundColor Gray
Write-Host "   - Look for toggle: 'Restrict inherited permissions'" -ForegroundColor Gray
Write-Host ""

Write-Host "   If ENABLED (restricted):" -ForegroundColor Red
Write-Host "     Option A: DISABLE restriction to inherit from parent" -ForegroundColor Green
Write-Host "     Option B: Add SP directly with Object ID: $objectId" -ForegroundColor Green
Write-Host ""

Write-Host "4. Add Service Principal directly:" -ForegroundColor Yellow
Write-Host "   - Click 'Add' in Role assignments" -ForegroundColor Gray
Write-Host "   - Search for SP by Object ID: $objectId" -ForegroundColor Cyan
Write-Host "   - OR Search by Display Name: $($spInfo.displayName)" -ForegroundColor Cyan
Write-Host "   - Assign role: Collection Admin" -ForegroundColor Green
Write-Host ""

Write-Host "5. Wait 5-10 minutes for propagation" -ForegroundColor Yellow
Write-Host ""

Write-Host "6. Re-run this diagnostic script to verify" -ForegroundColor Yellow
Write-Host ""

Write-Host "Common issues:" -ForegroundColor Yellow
Write-Host "  - Used App ID instead of Object ID" -ForegroundColor Gray
Write-Host "  - Assigned to wrong collection (parent vs child)" -ForegroundColor Gray
Write-Host "  - Permissions restricted on this specific collection" -ForegroundColor Gray
Write-Host "  - Role propagation not complete (wait 10 min)" -ForegroundColor Gray
Write-Host ""

exit 0
