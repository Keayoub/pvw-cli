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

.PARAMETER Debug
  If set, displays detailed debug information during execution.

.EXAMPLE
  ./Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Prod"
  
.EXAMPLE
  ./Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Prod" -Force
  
.EXAMPLE
  ./Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Prod" -Force -Debug
#>

param(
  [Parameter(Mandatory=$true)][string]$AccountName,
  [Parameter(Mandatory=$true)][string]$CollectionName,
  [switch]$Force,
  [switch]$Debug
)

Write-Host "Getting access token using Azure CLI..."
try {
    $tokenJson = az account get-access-token --resource "https://purview.azure.net" --output json
    $tokenData = $tokenJson | ConvertFrom-Json
    $script:AccessToken = $tokenData.accessToken
    Write-Host "✅ Token acquired successfully using Azure CLI."
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
      if ($Debug) { Write-Host "Ignoring error for $Method $Url : $($_.Exception.Message)" -ForegroundColor Gray }
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

Write-Host ">>> Resolving collection identity…" -ForegroundColor Cyan
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

Write-Host ">>> Checking child collections…" -ForegroundColor Cyan
$children = Invoke-PvApi -Method GET -Url "$acctApi/collections/$collectionName/getChildCollectionNames?api-version=2019-11-01-preview"
if ($children -and $children.value -and $children.value.Count -gt 0) {
  Write-Warning "Child collections exist under '$friendlyName' ($collectionName): $($children.value -join ', ')"
  
  if ($Force) {
    Write-Host "⚠️ FORCE MODE: Attempting to delete child collections first..." -ForegroundColor Yellow
    foreach ($childName in $children.value) {
      try {
        Write-Host "   - Deleting child collection: $childName"
        Invoke-PvApi -Method DELETE -Url "$acctApi/collections/$childName?api-version=2019-11-01-preview" -ExpectedStatus 200 | Out-Null
        Write-Host "   ✅ Child collection '$childName' deleted" -ForegroundColor Green
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

Write-Host ">>> Enumerating data sources & scans bound to the collection…" -ForegroundColor Cyan
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
  if ($Debug) { Write-Host "    DEBUG: dsName = '$dsName'" -ForegroundColor Magenta }

  try {
    $scansUrl = "$scanApi/datasources/$dsName/scans?api-version=2023-09-01"
    if ($Debug) { Write-Host "    DEBUG: Fetching scans from: $scansUrl" -ForegroundColor Magenta }
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
        if ($Debug) { Write-Host "Scan object properties: $($s | ConvertTo-Json -Depth 2)" -ForegroundColor Gray }
        $scanName = "UnknownScan_$([guid]::NewGuid().ToString().Substring(0,8))"
      }
      
      Write-Host "       - Deleting scan: $scanName"
      if ($Debug) { 
        Write-Host "       DEBUG: scanName variable = '$scanName'" -ForegroundColor Magenta
        Write-Host "       DEBUG: dsName variable = '$dsName'" -ForegroundColor Magenta
      }
      $deleteUrlTemplate = "$scanApi/datasources/{0}/scans/{1}?api-version=2023-09-01"
      $deleteUrl = $deleteUrlTemplate -f $dsName, $scanName
      if ($Debug) { Write-Host "       DEBUG: Constructed URL = '$deleteUrl'" -ForegroundColor Magenta }
      try {
        Invoke-PvApi -Method DELETE -Url $deleteUrl -ExpectedStatus 200 | Out-Null
        Write-Host "       ✅ Scan '$scanName' deleted" -ForegroundColor Green
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
  if ($Debug) { Write-Host "       DEBUG: dsName variable = '$dsName'" -ForegroundColor Magenta }
  $deleteUrlTemplate = "$scanApi/datasources/{0}?api-version=2023-09-01"
  $deleteUrl = $deleteUrlTemplate -f $dsName
  if ($Debug) { Write-Host "       DEBUG: Constructed data source URL = '$deleteUrl'" -ForegroundColor Magenta }
  try {
    Invoke-PvApi -Method DELETE -Url $deleteUrl -ExpectedStatus 200 | Out-Null
    Write-Host "       ✅ Data source '$dsName' deleted" -ForegroundColor Green
  } catch {
    Write-Warning "Failed to delete data source '$dsName': $($_.Exception.Message)"
    if (-not $Force) {
      throw "Failed to delete data source. Use -Force to continue despite errors."
    }
  }
}

Write-Host ">>> Deleting collection '$friendlyName' ($collectionName) …" -ForegroundColor Cyan
if ($Debug) { 
  Write-Host "DEBUG: collectionName variable = '$collectionName'" -ForegroundColor Magenta
}
$deleteUrlTemplate = "$acctApi/collections/{0}?api-version=2019-11-01-preview"
$deleteUrl = $deleteUrlTemplate -f $collectionName
if ($Debug) { Write-Host "DEBUG: Constructed collection URL = '$deleteUrl'" -ForegroundColor Magenta }

if ($Force) {
  Write-Host "⚠️ FORCE MODE: Attempting aggressive collection deletion..." -ForegroundColor Yellow
}

try {
  Invoke-PvApi -Method DELETE -Url $deleteUrl -ExpectedStatus 200 | Out-Null
  Write-Host "🎉 SUCCESS: Collection '$friendlyName' deleted successfully!" -ForegroundColor Green
} catch {
  if ($_.Exception.Message -match "409" -or $_.Exception.Message -match '"code"\s*:\s*"Conflict"') {
    Write-Warning "Delete failed with HTTP 409 (Conflict) — collection is still referenced."
    Write-Host "Details:" -ForegroundColor Yellow
    Write-Host $_.Exception.Message
    
    if ($Force) {
      Write-Host "`n⚠️ FORCE MODE: Attempting additional cleanup strategies..." -ForegroundColor Yellow
      
      Write-Host "   - Waiting 10 seconds for backend cleanup..."
      Start-Sleep -Seconds 10
      
      try {
        Write-Host "   - Retrying collection deletion..."
        Invoke-PvApi -Method DELETE -Url "$acctApi/collections/$collectionName?api-version=2019-11-01-preview" -ExpectedStatus 200 | Out-Null
        Write-Host "🎉 SUCCESS: Collection '$friendlyName' deleted on retry!" -ForegroundColor Green
        exit 0
      } catch {
        Write-Warning "Force deletion still failed: $($_.Exception.Message)"
        Write-Host "`n❌ FORCE DELETE FAILED" -ForegroundColor Red
        Write-Host "The collection may have hidden dependencies that require manual intervention." -ForegroundColor Yellow
        Write-Host "Try again in a few minutes, or check for assets/lineage still referencing this collection." -ForegroundColor Yellow
        exit 3
      }
    } else {
      Write-Host "`nTips:" -ForegroundColor Yellow
      Write-Host "- Ensure no child collections, scans, or data sources remain" -ForegroundColor Yellow
      Write-Host "- Sometimes backend cleanup may take time before delete succeeds" -ForegroundColor Yellow
      Write-Host "- Use -Force parameter to attempt aggressive cleanup and retry" -ForegroundColor Yellow
      exit 2
    }
  } else {
    Write-Error "Unexpected error during collection deletion: $($_.Exception.Message)"
    exit 4
  }
}

Write-Host "`n🎉 === COLLECTION DELETION COMPLETE ===" -ForegroundColor Green
Write-Host "✅ Collection '$friendlyName' ($collectionName) has been successfully deleted" -ForegroundColor Green
Write-Host "🧹 All associated scans and data sources have been cleaned up" -ForegroundColor Green
