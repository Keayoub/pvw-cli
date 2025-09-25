# Get-PurviewCollectionDetails.ps1
# Comprehensive script to get all details about a Purview collection
# Usage: .\Get-PurviewCollectionDetails.ps1 -AccountName <PurviewAccountName> -CollectionName <CollectionName>

param(
    [Parameter(Mandatory=$true)]
    [string]$AccountName,
    [Parameter(Mandatory=$true)]
    [string]$CollectionName
)

$ErrorActionPreference = "Stop"

Write-Host "=== Purview Collection Details Script ===" -ForegroundColor Cyan
Write-Host "Account: $AccountName" -ForegroundColor Yellow
Write-Host "Collection: $CollectionName" -ForegroundColor Yellow
Write-Host ""

# Get access token
Write-Host "Getting access token..." -ForegroundColor Cyan
try {
    $tokenJson = az account get-access-token --resource "https://purview.azure.net" --output json
    $tokenData = $tokenJson | ConvertFrom-Json
    $accessToken = $tokenData.accessToken
    Write-Host "✓ Token acquired successfully" -ForegroundColor Green
} catch {
    Write-Error "Failed to get access token: $_"
    exit 1
}

$headers = @{
    'Authorization' = "Bearer $accessToken"
    'Content-Type' = 'application/json'
}

# Helper function for API calls
function Invoke-PvApi {
    param(
        [string]$Method = "GET",
        [string]$Uri,
        [object]$Body = $null,
        [switch]$IgnoreErrors
    )
    
    try {
        $params = @{
            Method = $Method
            Uri = $Uri
            Headers = $headers
        }
        
        if ($Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        $response = Invoke-RestMethod @params
        return $response
    }
    catch {
        if ($IgnoreErrors) {
            Write-Verbose "API call failed (ignored): $($_.Exception.Message)"
            return $null
        } else {
            throw $_
        }
    }
}

# 1. Get Collection Information
Write-Host "`n1. COLLECTION INFORMATION" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor DarkGray

$collectionsUri = "https://$AccountName.purview.azure.com/account/collections?api-version=2019-11-01-preview"
try {
    $collectionsResponse = Invoke-PvApi -Uri $collectionsUri
    $targetCollection = $collectionsResponse.value | Where-Object { $_.name -eq $CollectionName }
    
    if ($targetCollection) {
        Write-Host "✓ Collection found!" -ForegroundColor Green
        Write-Host "  Name: $($targetCollection.name)" -ForegroundColor White
        Write-Host "  Friendly Name: $($targetCollection.friendlyName)" -ForegroundColor White
        Write-Host "  Parent: $($targetCollection.parentCollection.referenceName)" -ForegroundColor White
        Write-Host "  Status: $($targetCollection.collectionProvisioningState)" -ForegroundColor White
        $collectionId = $targetCollection.name
    } else {
        Write-Host "✗ Collection '$CollectionName' not found" -ForegroundColor Red
        Write-Host "Available collections:" -ForegroundColor Yellow
        $collectionsResponse.value | ForEach-Object { Write-Host "  - $($_.name)" -ForegroundColor Gray }
        exit 1
    }
} catch {
    Write-Host "✗ Failed to retrieve collections: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Get Assets in Collection
Write-Host "`n2. ASSETS IN COLLECTION" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor DarkGray

$searchUri = "https://$AccountName.purview.azure.com/datamap/api/search/query?api-version=2023-09-01"
$searchBody = @{ 
    "keywords" = "*"
    "limit" = 100
    "filter" = @{ "collectionId" = $collectionId }
}

try {
    $assetsResponse = Invoke-PvApi -Method POST -Uri $searchUri -Body $searchBody
    if ($assetsResponse -and $assetsResponse.value -and $assetsResponse.value.Count -gt 0) {
        Write-Host "✓ Found $($assetsResponse.value.Count) asset(s)" -ForegroundColor Green
        $assetsResponse.value | Select-Object name, assetType, qualifiedName | Format-Table -AutoSize
    } else {
        Write-Host "✗ No assets found in collection" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Failed to search assets: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Check Data Sources
Write-Host "`n3. DATA SOURCES" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor DarkGray

$dsApiVersions = @("2023-09-01", "2022-07-01-preview")
$foundDataSources = $false
$collectionDataSources = @()

foreach ($apiVersion in $dsApiVersions) {
    Write-Host "Trying data sources API version: $apiVersion" -ForegroundColor Gray
    $dsUri = "https://$AccountName.purview.azure.com/scan/datasources?api-version=$apiVersion"
    
    try {
        $dsResponse = Invoke-PvApi -Uri $dsUri -IgnoreErrors
        
        if ($dsResponse -and $dsResponse.value -and $dsResponse.value.Count -gt 0) {
            Write-Host "✓ Found $($dsResponse.value.Count) total data source(s)" -ForegroundColor Green
            
            # Check which data sources belong to this collection
            foreach ($ds in $dsResponse.value) {
                $dsCollectionRef = $null
                if ($ds.properties -and $ds.properties.collection -and $ds.properties.collection.referenceName) {
                    $dsCollectionRef = $ds.properties.collection.referenceName
                } elseif ($ds.collection -and $ds.collection.referenceName) {
                    $dsCollectionRef = $ds.collection.referenceName
                }
                
                Write-Verbose "Data Source: $($ds.name) -> Collection: $($dsCollectionRef)"
                
                if ($dsCollectionRef -eq $collectionId -or $dsCollectionRef -eq $CollectionName) {
                    $collectionDataSources += $ds
                    Write-Host "  ✓ Data Source: $($ds.name) (Type: $($ds.kind))" -ForegroundColor White
                }
            }
            
            if ($collectionDataSources.Count -gt 0) {
                Write-Host "✓ Found $($collectionDataSources.Count) data source(s) in collection '$CollectionName'" -ForegroundColor Green
            } else {
                Write-Host "✗ No data sources found in collection '$CollectionName'" -ForegroundColor Yellow
            }
            
            $foundDataSources = $true
            break
        } else {
            Write-Host "  No data sources returned for API version $apiVersion" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  Data sources API v$apiVersion failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

if (-not $foundDataSources) {
    Write-Host "✗ Data sources API not available or no data sources exist" -ForegroundColor Yellow
}

# 4. Check Scans for Collection Data Sources
if ($collectionDataSources.Count -gt 0) {
    Write-Host "`n4. SCANS FOR COLLECTION DATA SOURCES" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor DarkGray
    
    foreach ($ds in $collectionDataSources) {
        Write-Host "Checking scans for data source: $($ds.name)" -ForegroundColor Yellow
        $scanApiVersions = @("2023-09-01", "2022-07-01-preview")
        $foundScans = $false
        
        foreach ($scanApiVersion in $scanApiVersions) {
            $scansUri = "https://$AccountName.purview.azure.com/scan/datasources/$($ds.name)/scans?api-version=$scanApiVersion"
            
            try {
                $scansResponse = Invoke-PvApi -Uri $scansUri -IgnoreErrors
                
                if ($scansResponse -and $scansResponse.value -and $scansResponse.value.Count -gt 0) {
                    Write-Host "✓ Found $($scansResponse.value.Count) scan(s) for $($ds.name):" -ForegroundColor Green
                    $scansResponse.value | Select-Object name, @{Name="Status";Expression={$_.properties.lastRun.result}} | Format-Table -AutoSize
                    $foundScans = $true
                    break
                }
            } catch {
                Write-Verbose "Scans API v$scanApiVersion failed for $($ds.name): $($_.Exception.Message)"
            }
        }
        
        if (-not $foundScans) {
            Write-Host "  No scans found for $($ds.name)" -ForegroundColor Gray
        }
    }
}

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Collection: $CollectionName (ID: $collectionId)" -ForegroundColor White
Write-Host "Assets: $(if ($assetsResponse -and $assetsResponse.value) { $assetsResponse.value.Count } else { 0 })" -ForegroundColor White
Write-Host "Data Sources in Collection: $($collectionDataSources.Count)" -ForegroundColor White
Write-Host ""
Write-Host "Script completed successfully!" -ForegroundColor Green
