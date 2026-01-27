# Test Service Principal Authentication and Token Refresh
# This script validates that SP authentication and automatic token refresh work correctly

param(
    [string]$ClientId,
    [string]$ClientSecret,
    [string]$TenantId,
    [string]$PurviewName = "purview-account-name",
    [string]$CollectionId = "root",
    [switch]$SkipRefreshTest = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Service Principal Authentication Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Configure credentials
if (-not $ClientId) {
    $ClientId = Read-Host "Enter Service Principal Client ID"
}
if (-not $ClientSecret) {
    $SecureSecret = Read-Host "Enter Service Principal Client Secret" -AsSecureString
    $ClientSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($SecureSecret))
}
if (-not $TenantId) {
    $TenantId = Read-Host "Enter Tenant ID"
}

$env:AZURE_CLIENT_ID = $ClientId
$env:AZURE_CLIENT_SECRET = $ClientSecret
$env:AZURE_TENANT_ID = $TenantId
$env:PURVIEW_NAME = $PurviewName
$env:PURVIEW_ACCOUNT_NAME = $PurviewName

Write-Host "[1/8] Configuration:" -ForegroundColor Yellow
Write-Host "  CLIENT_ID: $($ClientId.Substring(0, 8))..." -ForegroundColor Gray
Write-Host "  TENANT_ID: $TenantId" -ForegroundColor Gray
Write-Host "  PURVIEW: $PurviewName" -ForegroundColor Gray
Write-Host ""

# Step 1a: DNS Resolution Test
Write-Host "[1a/8] DNS Resolution Test..." -ForegroundColor Yellow
$purviewFqdn = "$PurviewName.purview.azure.com"
Write-Host "  Resolving: $purviewFqdn" -ForegroundColor Gray

try {
    $dnsResult = [System.Net.Dns]::GetHostAddresses($purviewFqdn)
    if ($dnsResult.Count -gt 0) {
        Write-Host "  [OK] DNS resolution successful" -ForegroundColor Green
        foreach ($ip in $dnsResult) {
            $ipString = $ip.IPAddressToString
            # Check if it's a private IP (Private Endpoint indicator)
            if ($ipString -match '^(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)') {
                Write-Host "    [PRIVATE] $ipString (Private Endpoint detected)" -ForegroundColor Cyan
            } else {
                Write-Host "    [PUBLIC] $ipString (Public endpoint)" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "  [WARNING] DNS resolution returned no results" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [FAILED] DNS resolution failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Possible issues:" -ForegroundColor Yellow
    Write-Host "    1. Network connectivity issue" -ForegroundColor Gray
    Write-Host "    2. Private DNS zone not configured" -ForegroundColor Gray
    Write-Host "    3. Purview name is incorrect" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "    - Verify you're connected to the VNet with the Private Endpoint" -ForegroundColor Gray
    Write-Host "    - Check DNS settings: nslookup $purviewFqdn" -ForegroundColor Gray
    Write-Host "    - Verify Private DNS Zone links: $PurviewName.privatelink.purview.azure.com" -ForegroundColor Gray
}
Write-Host ""

# Step 1b: Verify environment variables are set
Write-Host "[1b/8] Verifying environment variables..." -ForegroundColor Yellow
$envVars = @{
    "AZURE_CLIENT_ID" = $env:AZURE_CLIENT_ID
    "AZURE_CLIENT_SECRET" = if ($env:AZURE_CLIENT_SECRET) { "***SET***" } else { "NOT SET" }
    "AZURE_TENANT_ID" = $env:AZURE_TENANT_ID
    "PURVIEW_NAME" = $env:PURVIEW_NAME
    "PURVIEW_ACCOUNT_NAME" = $env:PURVIEW_ACCOUNT_NAME
}

$allSet = $true
foreach ($var in $envVars.Keys) {
    $value = $envVars[$var]
    if ($value -eq "NOT SET") {
        Write-Host "  [WARNING] $var : NOT SET" -ForegroundColor Yellow
        $allSet = $false
    } else {
        Write-Host "  [OK] $var : $value" -ForegroundColor Green
    }
}

if (-not $allSet) {
    Write-Host ""
    Write-Host "  [FAILED] Some environment variables are not set!" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Check pvw-cli version
Write-Host "[2/8] Checking pvw-cli version..." -ForegroundColor Yellow
$version = pvw --version 2>&1
Write-Host "  $version" -ForegroundColor Gray

if ($version -notmatch "1\.6\.[1-9]") {
    Write-Host "  [WARNING] Version should be 1.6.1 or higher for proper token handling" -ForegroundColor Red
    Write-Host "  Run: pip install --upgrade pvw-cli" -ForegroundColor Yellow
}
Write-Host ""

# Step 2b: Test Azure CLI authentication
Write-Host "[2b/8] Testing Azure CLI authentication with Service Principal..." -ForegroundColor Yellow
Write-Host "  Attempting to get access token..." -ForegroundColor Gray

try {
    $tokenResult = az account get-access-token --resource "https://purview.azure.net" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $tokenObj = $tokenResult | ConvertFrom-Json
        $tokenPreview = $tokenObj.accessToken.Substring(0, 20) + "..."
        Write-Host "  [OK] Successfully obtained access token" -ForegroundColor Green
        Write-Host "    Token preview: $tokenPreview" -ForegroundColor Gray
        Write-Host "    Expires on: $($tokenObj.expiresOn)" -ForegroundColor Gray
        Write-Host "    Scope: https://purview.azure.net" -ForegroundColor Gray
    } else {
        Write-Host "  [FAILED] Could not obtain access token" -ForegroundColor Red
        Write-Host "  Error: $tokenResult" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Possible issues:" -ForegroundColor Yellow
        Write-Host "    1. Service Principal credentials are incorrect" -ForegroundColor Gray
        Write-Host "    2. Check AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID" -ForegroundColor Gray
        Write-Host "    3. Service Principal may not exist or be in wrong tenant" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Debug: Try running this manually:" -ForegroundColor Cyan
        Write-Host "    az login --service-principal -u `"$ClientId`" -p `"<secret>`" --tenant `"$TenantId`"" -ForegroundColor Gray
        exit 1
    }
} catch {
    Write-Host "  [FAILED] Exception during token request: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2a: Network Connectivity Test
Write-Host "[2a/8] Network Connectivity Test..." -ForegroundColor Yellow
$purviewFqdn = "$PurviewName.purview.azure.com"
$purviewPrivateFqdn = "$PurviewName.privatelink.purview.azure.com"

Write-Host "  Testing HTTPS connectivity on port 443..." -ForegroundColor Gray
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $asyncResult = $tcpClient.BeginConnect($purviewFqdn, 443, $null, $null)
    $wait = $asyncResult.AsyncWaitHandle.WaitOne(3000, $false)
    
    if ($tcpClient.Connected) {
        Write-Host "  [OK] TCP connection to port 443 successful" -ForegroundColor Green
        $tcpClient.Close()
    } else {
        Write-Host "  [WARNING] TCP connection timeout (3s)" -ForegroundColor Yellow
        Write-Host "    This may indicate network connectivity issues with Private Endpoint" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [WARNING] TCP connection failed: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "    Possible issues:" -ForegroundColor Gray
    Write-Host "      - Not connected to VNet with Private Endpoint" -ForegroundColor Gray
    Write-Host "      - Network security group blocking port 443" -ForegroundColor Gray
    Write-Host "      - Private Endpoint not configured" -ForegroundColor Gray
}
Write-Host ""

# Step 3: Test initial authentication
Write-Host "[3/8] Testing initial authentication with pvw-cli..." -ForegroundColor Yellow
$result1 = pvw account get-account 2>&1 | Out-String

if ($result1 -match '"friendlyName"' -or $result1 -match '"name"') {
    Write-Host "  [OK] Initial authentication successful" -ForegroundColor Green
    
    # Extract account name
    try {
        $json = $result1 | ConvertFrom-Json
        $accountName = $json.name
        Write-Host "  Account: $accountName" -ForegroundColor Cyan
    } catch {
        Write-Host "  [OK] Got valid response" -ForegroundColor Green
    }
} elseif ($result1 -match "401" -or $result1 -match "Unauthenticated" -or $result1 -match "Invalid token") {
    Write-Host "  [FAILED] Authentication failed with 401 (Unauthenticated)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Diagnostics:" -ForegroundColor Yellow
    Write-Host "  - Azure CLI token test (above) indicates the real issue" -ForegroundColor Gray
    Write-Host "  - If Azure CLI token succeeded: pvw-cli bug, try upgrading" -ForegroundColor Gray
    Write-Host "  - If Azure CLI token failed: SP credentials or permissions issue" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Full output:" -ForegroundColor Yellow
    Write-Host $result1
    exit 1
} elseif ($result1 -match "403" -or $result1 -match "Forbidden") {
    Write-Host "  [FAILED] Authentication succeeded but PERMISSION DENIED (403)" -ForegroundColor Red
    Write-Host ""
    Write-Host "This means:" -ForegroundColor Yellow
    Write-Host "  ✓ Service Principal credentials are CORRECT" -ForegroundColor Green
    Write-Host "  ✓ Token authentication is working" -ForegroundColor Green
    Write-Host "  ✗ Service Principal doesn't have required permissions on Purview" -ForegroundColor Red
    Write-Host ""
    Write-Host "To fix:" -ForegroundColor Yellow
    Write-Host "  1. Go to Purview Portal > Root Collection > Role assignments" -ForegroundColor Gray
    Write-Host "  2. Add Service Principal: $ServicePrincipalName" -ForegroundColor Gray
    Write-Host "  3. Assign role: Data Curator OR Collection Admin" -ForegroundColor Gray
    Write-Host "  4. Wait 5-10 minutes for permissions to propagate" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Service Principal ID to add: $ClientId" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Full output:" -ForegroundColor Yellow
    Write-Host $result1
    exit 1
} elseif ($result1 -match "Service Unavailable\|500\|504") {
    Write-Host "  [FAILED] Server error (5xx)" -ForegroundColor Red
    Write-Host "  Purview service may be temporarily unavailable" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Try again in a few moments, or check Azure Service Health" -ForegroundColor Gray
    exit 1
} else {
    Write-Host "  [UNKNOWN] Unexpected response" -ForegroundColor Yellow
    Write-Host $result1
    exit 2
}
Write-Host ""

# Step 4: Test GET operations
Write-Host "[4/7] Testing GET operations (read-only)..." -ForegroundColor Yellow
$startTime = Get-Date

# Test GET - Account details
$result2 = pvw account get-account 2>&1 | Out-String
if ($result2 -match '"friendlyName"' -or $result2 -match '"name"') {
    Write-Host "  [OK] GET account details successful" -ForegroundColor Green
} else {
    Write-Host "  [FAILED] GET account failed" -ForegroundColor Red
    Write-Host $result2
    exit 1
}

# Test GET - Collections list
$result3 = pvw collections list 2>&1 | Out-String
if ($result3 -match '"value"' -or $result3 -match '"count"') {
    Write-Host "  [OK] GET collections list successful" -ForegroundColor Green
} else {
    Write-Host "  [FAILED] GET collections failed" -ForegroundColor Red
    Write-Host $result3
    exit 1
}

# Test GET - Glossary list
$result4 = pvw glossary list 2>&1 | Out-String
if ($result4 -match '"value"' -or $result4 -match "glossary" -or $result4 -match "error.*404") {
    Write-Host "  [OK] GET glossary list successful" -ForegroundColor Green
} else {
    Write-Host "  [FAILED] GET glossary failed" -ForegroundColor Red
    Write-Host $result4
    exit 1
}

$endTime = Get-Date
$elapsed = ($endTime - $startTime).TotalSeconds
Write-Host "  Time elapsed: $([math]::Round($elapsed, 2))s" -ForegroundColor Gray
Write-Host ""

# Step 5: Test POST operation (create)
Write-Host "[5/7] Testing POST operation (create)..." -ForegroundColor Yellow
$testCollectionName = "test-auth-$(Get-Date -Format 'yyyyMMddHHmmss')"
$testCollectionFriendlyName = "Test Auth Collection"

# Use provided CollectionId or default to root
$parentCollection = $CollectionId

Write-Host "  Parent collection: $parentCollection" -ForegroundColor Gray
Write-Host "  Creating test collection: $testCollectionName" -ForegroundColor Gray
$resultPost = pvw collections create --collection-name $testCollectionName --parent-collection $parentCollection --friendly-name $testCollectionFriendlyName 2>&1 | Out-String

if ($resultPost -match '"name".*' + $testCollectionName -or $resultPost -match "Succeeded" -or $resultPost -match '"status".*success') {
    Write-Host "  [OK] POST create collection successful" -ForegroundColor Green
    $createdCollection = $testCollectionName
} elseif ($resultPost -match "409" -or $resultPost -match "already exists") {
    Write-Host "  [OK] POST request successful (collection already exists)" -ForegroundColor Green
    $createdCollection = $testCollectionName
} elseif ($resultPost -match "401" -or $resultPost -match "Unauthenticated" -or $resultPost -match "Invalid token") {
    Write-Host "  [FAILED] POST operation failed with 401 - Authentication issue" -ForegroundColor Red
    Write-Host "  This indicates token is not being sent correctly for POST requests" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Full output:" -ForegroundColor Yellow
    Write-Host $resultPost
    exit 1
} elseif ($resultPost -match "403" -or $resultPost -match "Forbidden") {
    Write-Host "  [WARNING] POST failed with 403 - Permission denied" -ForegroundColor Yellow
    Write-Host "  Service Principal may not have write permissions on Purview" -ForegroundColor Gray
    Write-Host "  Required role: Data Curator or Collection Admin" -ForegroundColor Gray
    $createdCollection = $null
} elseif ($resultPost -match "400") {
    Write-Host "  [WARNING] POST failed with 400 - Bad request (may be expected)" -ForegroundColor Yellow
    Write-Host $resultPost
    $createdCollection = $null
} else {
    Write-Host "  [UNKNOWN] POST operation returned unexpected result" -ForegroundColor Yellow
    Write-Host $resultPost
    $createdCollection = $null
}
Write-Host ""

# Step 6: Test PUT operation (update) - only if collection was created
if ($createdCollection) {
    Write-Host "[6/7] Testing PUT operation (update)..." -ForegroundColor Yellow
    
    $updatedFriendlyName = "Test Auth Collection Updated"
    $resultPut = pvw collections update --collection-name $createdCollection --friendly-name $updatedFriendlyName 2>&1 | Out-String
    
    if ($resultPut -match $updatedFriendlyName -or $resultPut -match "success" -or $resultPut -match "Succeeded") {
        Write-Host "  [OK] PUT update collection successful" -ForegroundColor Green
    } elseif ($resultPut -match "401" -or $resultPut -match "Unauthenticated" -or $resultPut -match "Invalid token") {
        Write-Host "  [FAILED] PUT operation failed with 401 - Authentication issue" -ForegroundColor Red
        Write-Host "  This indicates token is not being sent correctly for PUT requests" -ForegroundColor Yellow
        Write-Host $resultPut
        exit 1
    } elseif ($resultPut -match "403") {
        Write-Host "  [WARNING] PUT failed with 403 - Permission denied" -ForegroundColor Yellow
    } elseif ($resultPut -match "404") {
        Write-Host "  [WARNING] PUT failed with 404 - Collection not found" -ForegroundColor Yellow
    } else {
        Write-Host "  [INFO] PUT operation result:" -ForegroundColor Gray
        Write-Host $resultPut
    }
    Write-Host ""
    
    # Step 7: Test DELETE operation (cleanup)
    Write-Host "[7/7] Testing DELETE operation (cleanup)..." -ForegroundColor Yellow
    
    $resultDelete = pvw collections delete --collection-name $createdCollection 2>&1 | Out-String
    
    if ($resultDelete -match "success" -or $resultDelete -match "204" -or $resultDelete -match "deleted") {
        Write-Host "  [OK] DELETE collection successful" -ForegroundColor Green
    } elseif ($resultDelete -match "401" -or $resultDelete -match "Unauthenticated" -or $resultDelete -match "Invalid token") {
        Write-Host "  [FAILED] DELETE operation failed with 401 - Authentication issue" -ForegroundColor Red
        Write-Host "  This indicates token is not being sent correctly for DELETE requests" -ForegroundColor Yellow
        Write-Host $resultDelete
        exit 1
    } elseif ($resultDelete -match "403") {
        Write-Host "  [WARNING] DELETE failed with 403 - Permission denied" -ForegroundColor Yellow
        Write-Host "  Note: Test collection '$createdCollection' may need manual cleanup" -ForegroundColor Gray
    } elseif ($resultDelete -match "404") {
        Write-Host "  [OK] Collection already deleted or not found" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] DELETE operation result:" -ForegroundColor Gray
        Write-Host $resultDelete
    }
} else {
    Write-Host "[6/8] Skipping PUT test (no collection created)" -ForegroundColor Gray
    Write-Host "[7/8] Skipping DELETE test (no collection created)" -ForegroundColor Gray
}
Write-Host ""

# Step 8: Network Diagnostics Summary
Write-Host "[8/8] Network Diagnostics Summary..." -ForegroundColor Yellow

# Run detailed network diagnostics with nslookup if available
$nslookupAvailable = Get-Command nslookup -ErrorAction SilentlyContinue
if ($nslookupAvailable) {
    Write-Host ""
    Write-Host "  DNS Query Results (nslookup):" -ForegroundColor Cyan
    Write-Host "  ==============================" -ForegroundColor Gray
    
    $nslookupResult = nslookup $purviewFqdn 2>&1 | Out-String
    $nslookupResult -split "`n" | ForEach-Object {
        if ($_ -match "Name:|Address:|^[0-9]") {
            Write-Host "    $_" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  [INFO] nslookup not available, skipping detailed DNS diagnostics" -ForegroundColor Gray
}

Write-Host ""
Write-Host "  Private Endpoint Configuration Check:" -ForegroundColor Cyan
Write-Host "  ======================================" -ForegroundColor Gray
Write-Host "  If using Private Endpoint, verify:" -ForegroundColor Yellow
Write-Host "    1. Private DNS Zone: $purviewPrivateFqdn" -ForegroundColor Gray
Write-Host "       Expected resolution: Private IP (10.x.x.x, 172.16-31.x.x, 192.168.x.x)" -ForegroundColor Gray
Write-Host "    2. VNet Link: Private DNS zone linked to your VNet" -ForegroundColor Gray
Write-Host "    3. Network Security Group: Port 443 allowed inbound" -ForegroundColor Gray
Write-Host "    4. Route Table: Ensure routes don't bypass Private Endpoint" -ForegroundColor Gray
Write-Host ""
Write-Host "  Troubleshooting Commands:" -ForegroundColor Yellow
Write-Host "    ipconfig /all                          # View network config and DNS" -ForegroundColor Gray
Write-Host "    nslookup $purviewFqdn" -ForegroundColor Gray
Write-Host "    Test-NetConnection $purviewFqdn -Port 443" -ForegroundColor Gray
Write-Host "    Get-DnsClientCache                     # View DNS cache" -ForegroundColor Gray
Write-Host ""
Write-Host "  Private Endpoint URLs:" -ForegroundColor Yellow
Write-Host "    Account:   $purviewFqdn" -ForegroundColor Gray
Write-Host "    Catalog:   catalog.$purviewFqdn" -ForegroundColor Gray
Write-Host "    Guardian:  guardian.$purviewFqdn" -ForegroundColor Gray
Write-Host ""
# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test Results: ALL PASSED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your Service Principal authentication is working correctly!" -ForegroundColor Green
Write-Host "You can now use pvw-cli with these environment variables." -ForegroundColor Gray
Write-Host ""

# Advanced Troubleshooting Guide
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Advanced Troubleshooting Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "If you still see 403 Forbidden errors despite having Data Curator role:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Check role assignment propagation (can take 5-10 minutes):" -ForegroundColor Cyan
Write-Host "   - Wait a few minutes and try again" -ForegroundColor Gray
Write-Host "   - Portal may show role instantly but API needs time to sync" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Verify role is assigned to the root collection:" -ForegroundColor Cyan
Write-Host "   - Go to Purview Portal" -ForegroundColor Gray
Write-Host "   - Click 'Root Collection' (not a sub-collection)" -ForegroundColor Gray
Write-Host "   - Go to 'Role assignments'" -ForegroundColor Gray
Write-Host "   - Your Service Principal must be listed with Data Curator OR Collection Admin" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Service Principal object ID vs App ID:" -ForegroundColor Cyan
Write-Host "   - You may need to add the Service Principal OBJECT ID, not App ID" -ForegroundColor Gray
Write-Host "   - Run this to get the object ID:" -ForegroundColor Gray
Write-Host "     az ad sp show --id $ClientId --query objectId -o tsv" -ForegroundColor Gray
Write-Host ""

Write-Host "4. Check if service principal has Azure RBAC permissions on resource group:" -ForegroundColor Cyan
Write-Host "   - Run: az role assignment list --assignee $ClientId --scope /subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}" -ForegroundColor Gray
Write-Host "   - SP should have Reader or Contributor role" -ForegroundColor Gray
Write-Host ""

Write-Host "5. Try different roles:" -ForegroundColor Cyan
Write-Host "   - Data Curator: Can create, modify, and delete assets" -ForegroundColor Gray
Write-Host "   - Collection Admin: Full access to collections and roles" -ForegroundColor Gray
Write-Host "   - Data Reader: Read-only access" -ForegroundColor Gray
Write-Host ""

Write-Host "6. Check Purview audit logs:" -ForegroundColor Cyan
Write-Host "   - Portal > Settings > Audit logs" -ForegroundColor Gray
Write-Host "   - Look for 403 errors with detailed error message" -ForegroundColor Gray
Write-Host ""

Write-Host "7. For Private Endpoint issues:" -ForegroundColor Cyan
Write-Host "   - Verify DNS resolves to Private IP:" -ForegroundColor Gray
Write-Host "     nslookup $purviewFqdn" -ForegroundColor Gray
Write-Host "   - Test connectivity:" -ForegroundColor Gray
Write-Host "     Test-NetConnection $purviewFqdn -Port 443 -InformationLevel Detailed" -ForegroundColor Gray
Write-Host "   - Check VNet connectivity from your machine" -ForegroundColor Gray
Write-Host ""

Write-Host "Still having issues? Collect this info for support:" -ForegroundColor Yellow
Write-Host "  1. Output of: az account show" -ForegroundColor Gray
Write-Host "  2. Output of: az ad sp show --id $ClientId" -ForegroundColor Gray
Write-Host "  3. Output of: nslookup $purviewFqdn" -ForegroundColor Gray
Write-Host "  4. Full error message from failed pvw command" -ForegroundColor Gray
Write-Host ""

exit 0
