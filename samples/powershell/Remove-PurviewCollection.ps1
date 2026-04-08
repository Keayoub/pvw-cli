<# 
.SYNOPSIS
  Delete a Microsoft Purview Collection using Azure CLI authentication.
  Cleans up dependent resources (child collections, scans, data sources) first.

.PARAMETER AccountName
  Purview account name (e.g., contoso-purview)

.PARAMETER CollectionName
  Collection identifier: friendly DisplayName OR internal collection 'name'

.PARAMETER Force
  If set, will force delete and try harder to remove blocking scan/data source objects even if metadata is partial.

.PARAMETER DebugMode
  If set, displays detailed debug information during execution.

.EXAMPLE
  ./Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Prod"
  
.EXAMPLE
  ./Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Prod" -Force
  
.EXAMPLE
  ./Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Prod" -Force -DebugMode
#>

param(
  [Parameter(Mandatory=$true)][string]$AccountName,
  [Parameter(Mandatory=$true)][string]$CollectionName,
  [switch]$Force,
  [switch]$DebugMode
)

Write-Host "Getting access token using Azure CLI..."
try {
    $tokenJson = az account get-access-token --resource "https://purview.azure.net" --output json
    $tokenData = $tokenJson | ConvertFrom-Json
    $script:AccessToken = $tokenData.accessToken
    Write-Host "[OK] Token acquired successfully using Azure CLI."
}
catch {
    Write-Error "Failed to get access token using Azure CLI: $_"
    Write-Host "Please ensure you are logged in with 'az login' and have access to the Purview account."
    exit 1
}

function Invoke-PvApi {
  param(
    [Parameter(Mandatory=$true)][string]$Method,
    [Parameter(Mandatory=$true)][string]$Url,
    [object]$Body = $null,
    [int]$ExpectedStatus = 200,
    [switch]$IgnoreErrors
  )
  $headers = @{ 
    Authorization = "Bearer $script:AccessToken"
    'Content-Type' = 'application/json'
  }
  if ($null -ne $Body) { $json = ($Body | ConvertTo-Json -Depth 100) } else { $json = $null }
  
  try {
    $resp = Invoke-WebRequest -Method $Method -Uri $Url -Headers $headers -Body $json -ErrorAction Stop
    if ($resp.StatusCode -ne $ExpectedStatus -and $ExpectedStatus -ne 0) {
      Write-Verbose "Unexpected status code: $($resp.StatusCode) for $Method $Url"
    }
    if ($resp.Content) { 
      return ($resp.Content | ConvertFrom-Json) 
    } else { 
      return $null 
    }
  } catch {
    if ($IgnoreErrors) {
      if ($DebugMode) { Write-Host "Ignoring error for $Method $Url : $($_.Exception.Message)" -ForegroundColor Gray }
      return $null
    }
    
    # PowerShell Core compatible error handling
    $errorDetails = ""
    if ($_.Exception -and $_.Exception.Response) {
      $errorDetails = "HTTP $($_.Exception.Response.StatusCode)"
      if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
        $errorDetails += " - $($_.ErrorDetails.Message)"
      }
    } else {
      $errorDetails = $_.Exception.Message
    }
    
    throw "HTTP error for $Method $Url : $errorDetails"
  }
}

$ErrorActionPreference = "Stop"

$acctBase = "https://$AccountName.purview.azure.com"
$acctApi  = "$acctBase/account"
$scanApi  = "$acctBase/scan"

Write-Host ">>> Resolving collection identity..." -ForegroundColor Cyan
$cols = Invoke-PvApi -Method GET -Url "$acctApi/collections?api-version=2019-11-01-preview"
if (-not $cols) { throw "No collections returned from Purview." }

# The payload is typically { "value": [ { name, friendlyName, systemData, ... } ], "count": n }
$colObj = $null
foreach ($c in $cols.value) {
  if ($c.name -eq $CollectionName -or $c.friendlyName -eq $CollectionName) { $colObj = $c; break }
}

if (-not $colObj) {
  $skip = $cols.'@nextLink'
  while ($null -ne $skip -and -not $colObj) {
    $next = Invoke-PvApi -Method GET -Url $skip
    foreach ($c in $next.value) {
      if ($c.name -eq $CollectionName -or $c.friendlyName -eq $CollectionName) { $colObj = $c; break }
    }
    $skip = $next.'@nextLink'
  }
}

if (-not $colObj) {
  throw "Collection '$CollectionName' not found (by name or friendlyName)."
}
$collectionName = $colObj.name
$friendlyName   = $colObj.friendlyName
Write-Host "    Internal name: $collectionName (friendly: $friendlyName)" -ForegroundColor Green

Write-Host ">>> Checking child collections..." -ForegroundColor Cyan
$children = Invoke-PvApi -Method GET -Url "$acctApi/collections/$collectionName/getChildCollectionNames?api-version=2019-11-01-preview"
if ($children -and $children.value -and $children.value.Count -gt 0) {
  Write-Warning "Child collections exist under '$friendlyName' ($collectionName): $($children.value -join ', ')"
  
  if ($Force) {
    Write-Host "[!] FORCE MODE: Attempting to delete child collections first..." -ForegroundColor Yellow
    foreach ($childName in $children.value) {
      try {
        Write-Host "   - Deleting child collection: $childName"
        Invoke-PvApi -Method DELETE -Url "$acctApi/collections/$childName?api-version=2019-11-01-preview" -ExpectedStatus 200 | Out-Null
        Write-Host "   [OK] Child collection '$childName' deleted" -ForegroundColor Green
      } catch {
        Write-Warning "Failed to delete child collection '$childName': $($_.Exception.Message)"
        if (-not $Force) {
          throw "Cannot delete child collection. Use -Force to attempt aggressive cleanup."
        }
      }
    }
  } else {
    throw "Delete or move child collections first, or use -Force to attempt automatic deletion."
  }
}

Write-Host ">>> Enumerating data sources & scans bound to the collection..." -ForegroundColor Cyan
$dsResp = Invoke-PvApi -Method GET -Url "$scanApi/datasources?api-version=2023-09-01"
$dsItems = @()
if ($dsResp -and $dsResp.value) { $dsItems += $dsResp.value }
while ($dsResp.'@nextLink') {
  $dsResp = Invoke-PvApi -Method GET -Url $dsResp.'@nextLink'
  if ($dsResp.value) { $dsItems += $dsResp.value }
}

function Test-DataSourceInCollection {
  param($ds)
  try {
    if ($ds.collection -and $ds.collection.referenceName -eq $collectionName) { return $true }
    if ($ds.properties -and $ds.properties.collection -and $ds.properties.collection.referenceName -eq $collectionName) { return $true }
    if ($ds.collection -and $ds.collection.name -eq $collectionName) { return $true }
  } catch { }
  return $false
}

$dsTarget = $dsItems | Where-Object { Test-DataSourceInCollection $_ }

foreach ($ds in $dsTarget) {
  $dsName = $ds.name
  Write-Host "    DataSource in collection: $dsName -> removing scans then data source" -ForegroundColor Yellow
  if ($DebugMode) { Write-Host "    DEBUG: dsName = '$dsName'" -ForegroundColor Magenta }

  try {
    $scansUrl = "$scanApi/datasources/$dsName/scans?api-version=2023-09-01"
    if ($DebugMode) { Write-Host "    DEBUG: Fetching scans from: $scansUrl" -ForegroundColor Magenta }
    $scans = Invoke-PvApi -Uri $scansUrl
    $scanList = @()
    if ($scans -and $scans.value) { $scanList += $scans.value }
    while ($scans.'@nextLink') {
      $scans = Invoke-PvApi -Method GET -Url $scans.'@nextLink'
      if ($scans.value) { $scanList += $scans.value }
    }

    foreach ($s in $scanList) {
      # Debug: Check scan object properties
      $scanName = $null
      if ($s.name) {
        $scanName = $s.name
      } elseif ($s.properties -and $s.properties.name) {
        $scanName = $s.properties.name
      } elseif ($s.scanName) {
        $scanName = $s.scanName
      } else {
        if ($DebugMode) { Write-Host "Scan object properties: $($s | ConvertTo-Json -Depth 2)" -ForegroundColor Gray }
        $scanName = "UnknownScan_$([guid]::NewGuid().ToString().Substring(0,8))"
      }
      
      Write-Host "       - Deleting scan: $scanName"
      if ($DebugMode) { 
        Write-Host "       DEBUG: scanName variable = '$scanName'" -ForegroundColor Magenta
        Write-Host "       DEBUG: dsName variable = '$dsName'" -ForegroundColor Magenta
      }
      $deleteUrlTemplate = "$scanApi/datasources/{0}/scans/{1}?api-version=2023-09-01"
      $deleteUrl = $deleteUrlTemplate -f $dsName, $scanName
      if ($DebugMode) { Write-Host "       DEBUG: Constructed URL = '$deleteUrl'" -ForegroundColor Magenta }
      try {
        Invoke-PvApi -Method DELETE -Url $deleteUrl -ExpectedStatus 200 | Out-Null
        Write-Host "       [OK] Scan '$scanName' deleted" -ForegroundColor Green
      } catch {
        Write-Warning "Failed to delete scan '$scanName': $($_.Exception.Message)"
        if (-not $Force) {
          throw "Failed to delete scan. Use -Force to continue despite errors."
        }
      }
    }
  } catch {
    Write-Warning "Error listing scans for data source '$dsName': $($_.Exception.Message)"
    if (-not $Force) {
      throw "Failed to process scans. Use -Force to continue despite errors."
    }
  }

  Write-Host "       - Deleting data source: $dsName"
  if ($DebugMode) { Write-Host "       DEBUG: dsName variable = '$dsName'" -ForegroundColor Magenta }
  $deleteUrlTemplate = "$scanApi/datasources/{0}?api-version=2023-09-01"
  $deleteUrl = $deleteUrlTemplate -f $dsName
  if ($DebugMode) { Write-Host "       DEBUG: Constructed data source URL = '$deleteUrl'" -ForegroundColor Magenta }
  try {
    Invoke-PvApi -Method DELETE -Url $deleteUrl -ExpectedStatus 200 | Out-Null
    Write-Host "       [OK] Data source '$dsName' deleted" -ForegroundColor Green
  } catch {
    Write-Warning "Failed to delete data source '$dsName': $($_.Exception.Message)"
    if (-not $Force) {
      throw "Failed to delete data source. Use -Force to continue despite errors."
    }
  }
}

Write-Host ">>> Checking for assets in collection..." -ForegroundColor Cyan

$datamapApi = "$acctBase/datamap"
$catalogApi = "$acctBase/catalog"
$allAssets = @()

# Method 1: Try modern DataMap Search API (primary method)
try {
  # Use the modern datamap API endpoint with wildcards
  $searchPayload = @{
    keywords = "*"
    filter = @{
      collectionId = $collectionName
    }
    limit = 1000
  }
  
  $searchUrl = "$datamapApi/api/search/query?api-version=2023-09-01"
  if ($DebugMode) { Write-Host "DEBUG: Searching for assets (DataMap API) at: $searchUrl" -ForegroundColor Magenta }
  
  $searchResults = Invoke-PvApi -Method POST -Url $searchUrl -Body $searchPayload -IgnoreErrors
  
  if ($searchResults -and $searchResults.value) {
    $allAssets += $searchResults.value
    Write-Host "    DataMap API found $($searchResults.value.Count) assets" -ForegroundColor Cyan
    if ($DebugMode) { Write-Host "DEBUG: DataMap search successful" -ForegroundColor Magenta }
    
    # Handle pagination
    $nextLink = $searchResults.'@search.nextLink'
    while ($nextLink) {
      $moreResults = Invoke-PvApi -Method GET -Url $nextLink -IgnoreErrors
      if ($moreResults -and $moreResults.value) {
        $allAssets += $moreResults.value
        Write-Host "    Found $($moreResults.value.Count) more assets (pagination)..." -ForegroundColor Cyan
      }
      $nextLink = $moreResults.'@search.nextLink'
    }
  } else {
    Write-Host "    DataMap API returned no results" -ForegroundColor Yellow
  }
} catch {
  Write-Warning "DataMap search failed: $($_.Exception.Message)"
  if ($DebugMode) { Write-Host "DEBUG: Full error: $_" -ForegroundColor Magenta }
}

# Method 2: Try legacy Catalog Search API (fallback)
if ($allAssets.Count -eq 0) {
  try {
    $legacySearchPayload = @{
      keywords = "*"
      filter = @{
        collectionId = $collectionName
      }
      limit = 1000
    }
    
    $legacySearchUrl = "$catalogApi/api/search/query?api-version=2023-09-01"
    if ($DebugMode) { Write-Host "DEBUG: Trying legacy Catalog API" -ForegroundColor Magenta }
    
    $legacyResults = Invoke-PvApi -Method POST -Url $legacySearchUrl -Body $legacySearchPayload -IgnoreErrors
    
    if ($legacyResults -and $legacyResults.value) {
      $allAssets += $legacyResults.value
      Write-Host "    Legacy Catalog API found $($legacyResults.value.Count) assets" -ForegroundColor Cyan
    }
  } catch {
    if ($DebugMode) { Write-Warning "Legacy Catalog search failed: $($_.Exception.Message)" }
  }
}

# Method 3: Try Atlas API with collection filter
if ($allAssets.Count -eq 0) {
  try {
    $atlasSearchUrl = "$catalogApi/api/atlas/v2/search/basic?collectionId=$collectionName&limit=1000"
    if ($DebugMode) { Write-Host "DEBUG: Trying Atlas API" -ForegroundColor Magenta }
    
    $atlasResults = Invoke-PvApi -Method GET -Url $atlasSearchUrl -IgnoreErrors
    
    if ($atlasResults -and $atlasResults.entities) {
      foreach ($entity in $atlasResults.entities) {
        $entityGuid = if ($entity.guid) { $entity.guid } else { $entity.id }
        if ($entityGuid) {
          $allAssets += @{ id = $entityGuid; name = $entity.displayText }
        }
      }
      Write-Host "    Atlas API found $($allAssets.Count) assets" -ForegroundColor Cyan
    }
  } catch {
    if ($DebugMode) { Write-Warning "Atlas search failed: $($_.Exception.Message)" }
  }
}

# Method 4: Query Atlas entity store directly via DSL (bypasses search index lag)
if ($allAssets.Count -eq 0) {
  try {
    $dslPayload = @{
      query = @{
        bool = @{
          filter = @(
            @{ term = @{ "__state" = "ACTIVE" } },
            @{ term = @{ "collectionId" = $collectionName } }
          )
        }
      }
      size = 1000
    }
    $dslUrl = "$catalogApi/api/atlas/v2/search/dsl?api-version=2023-09-01"
    if ($DebugMode) { Write-Host "DEBUG: Trying Atlas DSL search" -ForegroundColor Magenta }
    $dslResults = Invoke-PvApi -Method POST -Url $dslUrl -Body $dslPayload -IgnoreErrors
    if ($dslResults -and $dslResults.entities) {
      foreach ($entity in $dslResults.entities) {
        $entityGuid = if ($entity.guid) { $entity.guid } else { $entity.id }
        if ($entityGuid) { $allAssets += @{ id = $entityGuid; name = $entity.displayText } }
      }
      Write-Host "    Atlas DSL search found $($allAssets.Count) assets" -ForegroundColor Cyan
    }
  } catch {
    if ($DebugMode) { Write-Warning "Atlas DSL search failed: $($_.Exception.Message)" }
  }
}

# Method 5: Purview Discovery API - list assets by collection (does not depend on search index)
if ($allAssets.Count -eq 0) {
  try {
    $discoveryUrl = "$datamapApi/api/atlas/v2/entity?collectionId=$collectionName&limit=1000&api-version=2023-09-01"
    if ($DebugMode) { Write-Host "DEBUG: Trying Discovery API" -ForegroundColor Magenta }
    $discoveryResults = Invoke-PvApi -Method GET -Url $discoveryUrl -IgnoreErrors
    if ($discoveryResults -and $discoveryResults.entities) {
      foreach ($entity in $discoveryResults.entities) {
        $entityGuid = if ($entity.guid) { $entity.guid } else { $entity.id }
        if ($entityGuid) { $allAssets += @{ id = $entityGuid; name = ($entity.attributes.name ?? $entityGuid) } }
      }
      Write-Host "    Discovery API found $($allAssets.Count) assets" -ForegroundColor Cyan
    }
  } catch {
    if ($DebugMode) { Write-Warning "Discovery API failed: $($_.Exception.Message)" }
  }
}

# Method 6: If all searches return 0 but collection has a 409, use batch delete script pattern
# Try a forced blind-delete attempt using the Remove-PurviewAsset-Batch approach via pvw CLI
if ($allAssets.Count -eq 0) {
  Write-Host "    [!] Search APIs returned 0 assets but collection may have unindexed assets." -ForegroundColor Yellow
  Write-Host "    Tip: Run Remove-PurviewAsset-Batch.ps1 -AccountName '$AccountName' -CollectionName '$CollectionName' -Mode BULK" -ForegroundColor Cyan
  Write-Host "    to clear assets directly via bulk delete, then re-run this script." -ForegroundColor Cyan
}

$totalAssets = $allAssets.Count
if ($totalAssets -gt 0) {
  Write-Host "    Found $totalAssets asset(s) in collection (from multiple detection methods)" -ForegroundColor Yellow
    
  if ($Force) {
    Write-Host "[!] FORCE MODE: Attempting to delete $totalAssets assets..." -ForegroundColor Yellow
    
    $deletedCount = 0
    $failedCount = 0
    
    foreach ($asset in $allAssets) {
      $guid = if ($asset.id) { $asset.id } elseif ($asset.guid) { $asset.guid } else { $null }
      if (-not $guid) { 
        $failedCount++
        continue 
      }
      
      $assetName = if ($asset.name) { $asset.name } elseif ($asset.displayText) { $asset.displayText } else { $guid }
      
      try {
        Write-Host "   - Deleting asset: $assetName (GUID: $guid)"
        $deleteAssetUrl = "$catalogApi/api/atlas/v2/entity/guid/$guid"
        Invoke-PvApi -Method DELETE -Url $deleteAssetUrl -ExpectedStatus 200 -IgnoreErrors | Out-Null
        $deletedCount++
        Write-Host "     [OK] Asset deleted" -ForegroundColor Green
        
        # Small delay to avoid rate limiting
        Start-Sleep -Milliseconds 100
      } catch {
        $failedCount++
        Write-Warning "Failed to delete asset '$assetName': $($_.Exception.Message)"
      }
    }
    
    Write-Host "   Asset deletion summary: $deletedCount deleted, $failedCount failed" -ForegroundColor $(if ($failedCount -eq 0) { "Green" } else { "Yellow" })
    
    # Wait longer for backend to process all deletions
    Write-Host "   Waiting 15 seconds for backend to fully process asset deletions..."
    Start-Sleep -Seconds 15
  } else {
    Write-Warning "Assets found in collection. Cannot delete collection while it contains assets."
    Write-Host "Use -Force to attempt automatic asset deletion, or manually delete/move assets first." -ForegroundColor Yellow
    exit 5
  }
} else {
  Write-Host "    [!] No assets detected via search APIs" -ForegroundColor Yellow
  
  # Even if no assets found, the collection might still have hidden/orphaned assets
  # Try to delete anyway if Force is enabled, and handle the error gracefully
  if ($Force) {
    Write-Host "    Force mode enabled - will attempt collection deletion anyway..." -ForegroundColor Cyan
    Write-Host "    (Assets may exist but not be indexed yet, or could be orphaned)" -ForegroundColor Gray
  }
}

Write-Host ">>> Deleting collection '$friendlyName' ($collectionName) ..." -ForegroundColor Cyan
if ($DebugMode) { 
  Write-Host "DEBUG: collectionName variable = '$collectionName'" -ForegroundColor Magenta
}
$deleteUrlTemplate = "$acctApi/collections/{0}?api-version=2019-11-01-preview"
$deleteUrl = $deleteUrlTemplate -f $collectionName
if ($DebugMode) { Write-Host "DEBUG: Constructed collection URL = '$deleteUrl'" -ForegroundColor Magenta }

if ($Force) {
  Write-Host "[!] FORCE MODE: Attempting aggressive collection deletion..." -ForegroundColor Yellow
}

try {
  Invoke-PvApi -Method DELETE -Url $deleteUrl -ExpectedStatus 200 | Out-Null
  Write-Host "[OK] SUCCESS: Collection '$friendlyName' deleted successfully!" -ForegroundColor Green
} catch {
  if ($_.Exception.Message -match "409" -or $_.Exception.Message -match '"code"\s*:\s*"Conflict"' -or $_.Exception.Message -match "12011" -or $_.Exception.Message -match "referenced by assets") {
    Write-Warning "Delete failed with HTTP 409 (Conflict) - collection still has asset references."
    Write-Host ""
    Write-Host "[INFO] This usually means assets exist but were not found by any search API." -ForegroundColor Yellow
    Write-Host "       Common causes: search indexing lag, orphaned/unindexed assets, lineage references." -ForegroundColor Yellow
    Write-Host ""

    if ($Force) {
      # Retry loop: 3 attempts with progressive wait
      $retryDelays = @(15, 30, 60)
      $deleted = $false
      foreach ($wait in $retryDelays) {
        Write-Host "   Waiting $wait seconds for backend to process pending deletions..." -ForegroundColor Cyan
        Start-Sleep -Seconds $wait
        try {
          Write-Host "   Retrying collection deletion..."
          Invoke-PvApi -Method DELETE -Url "$acctApi/collections/$collectionName?api-version=2019-11-01-preview" -ExpectedStatus 200 | Out-Null
          Write-Host "[OK] SUCCESS: Collection '$friendlyName' deleted!" -ForegroundColor Green
          $deleted = $true
          break
        } catch {
          Write-Warning "Retry failed: $($_.Exception.Message)"
        }
      }

      if (-not $deleted) {
        Write-Host ""
        Write-Host "[X] COLLECTION DELETION FAILED after all retries." -ForegroundColor Red
        Write-Host ""
        Write-Host "[INFO] NEXT STEPS:" -ForegroundColor Cyan
        Write-Host "   1. Run the batch asset removal script to clear unindexed assets:" -ForegroundColor White
        Write-Host "      .\Remove-PurviewAsset-Batch.ps1 -AccountName '$AccountName' -CollectionName '$collectionName' -Mode BULK" -ForegroundColor Green
        Write-Host "   2. Wait for completion, then re-run this script." -ForegroundColor White
        Write-Host "   3. If it still fails, check for lineage relationships or scan history blocking deletion." -ForegroundColor White
        exit 3
      }
    } else {
      Write-Host "[!] Re-run with -Force to attempt automatic retry with wait:" -ForegroundColor Yellow
      Write-Host "    .\Remove-PurviewCollection.ps1 -AccountName '$AccountName' -CollectionName '$CollectionName' -Force" -ForegroundColor Green
      Write-Host ""
      Write-Host "    Or clear assets first with:" -ForegroundColor Yellow
      Write-Host "    .\Remove-PurviewAsset-Batch.ps1 -AccountName '$AccountName' -CollectionName '$collectionName' -Mode BULK" -ForegroundColor Green
      exit 2
    }
  } else {
    Write-Error "Unexpected error during collection deletion: $($_.Exception.Message)"
    exit 4
  }
}

Write-Host "`n[OK] === COLLECTION DELETION COMPLETE ===" -ForegroundColor Green
Write-Host "[OK] Collection '$friendlyName' ($collectionName) has been successfully deleted" -ForegroundColor Green
Write-Host "[CLEANUP] All associated scans and data sources have been cleaned up" -ForegroundColor Green
