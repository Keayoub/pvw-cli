# Get-PurviewCollectionDetails.ps1
# Comprehensive script to get all details about a Purview collection
# Usage: .\Get-PurviewCollectionDetails.ps1 -AccountName <PurviewAccountName> -CollectionName <CollectionName>

param(
    [Parameter(Mandatory=$true)]
    [string]$AccountName,
    [Parameter(Mandatory=$true)]
    [string]$CollectionName
)

Write-Host "=== Purview Collection Details Script ==="
Write-Host "Account: $AccountName"
Write-Host "Collection: $CollectionName"
Write-Host ""

# Get access token
Write-Host "Getting access token..."
try {
    $tokenJson = az account get-access-token --resource "https://purview.azure.net" --output json
    $tokenData = $tokenJson | ConvertFrom-Json
    $accessToken = $tokenData.accessToken
    Write-Host "✓ Token acquired successfully"
} catch {
    Write-Error "Failed to get access token: $_"
    exit 1
}

$headers = @{
    'Authorization' = "Bearer $accessToken"
    'Content-Type' = 'application/json'
}

# 1. Get Collection Information
Write-Host "`n1. COLLECTION INFORMATION"
Write-Host "=" * 50

$collectionsUri = "https://$AccountName.purview.azure.com/account/collections?api-version=2019-11-01-preview"
try {
    $collectionsResponse = Invoke-RestMethod -Method GET -Uri $collectionsUri -Headers $headers
    $targetCollection = $collectionsResponse.value | Where-Object { $_.name -eq $CollectionName }
    
    if ($targetCollection) {
        Write-Host "✓ Collection found!"
        Write-Host "  Name: $($targetCollection.name)"
        Write-Host "  Friendly Name: $($targetCollection.friendlyName)"
        Write-Host "  Parent: $($targetCollection.parentCollection.referenceName)"
        Write-Host "  Status: $($targetCollection.collectionProvisioningState)"
        $collectionId = $targetCollection.name
    } else {
        Write-Host "✗ Collection '$CollectionName' not found"
        Write-Host "Available collections:"
        $collectionsResponse.value | ForEach-Object { Write-Host "  - $($_.name)" }
        exit 1
    }
} catch {
    Write-Host "✗ Failed to retrieve collections: $($_.Exception.Message)"
    exit 1
}

# 2. Get Assets in Collection
Write-Host "`n2. ASSETS IN COLLECTION"
Write-Host "=" * 50

$searchUri = "https://$AccountName.purview.azure.com/datamap/api/search/query?api-version=2023-09-01"
$searchBody = @{ 
    "keywords" = "*"
    "limit" = 100
    "filter" = @{ "collectionId" = $collectionId }
} | ConvertTo-Json

try {
    $assetsResponse = Invoke-RestMethod -Method POST -Uri $searchUri -Headers $headers -Body $searchBody
    if ($assetsResponse -and $assetsResponse.value) {
        Write-Host "✓ Found $($assetsResponse.value.Count) asset(s)"
        $assetsResponse.value | Format-Table name, assetType, qualifiedName -AutoSize
    } else {
        Write-Host "✗ No assets found in collection"
    }
} catch {
    Write-Host "✗ Failed to search assets: $($_.Exception.Message)"
}

# 3. Check Data Sources
Write-Host "`n3. DATA SOURCES"
Write-Host "=" * 50

$dsApiVersions = @("2023-09-01", "2022-07-01-preview")
$foundDataSources = $false
$collectionDataSources = @()

foreach ($apiVersion in $dsApiVersions) {
    Write-Host "Trying data sources API version: $apiVersion"
    $dsUri = "https://$AccountName.purview.azure.com/datasources?api-version=$apiVersion"
    
    try {
        $dsResponse = Invoke-RestMethod -Method GET -Uri $dsUri -Headers $headers
        
        if ($dsResponse -and $dsResponse.value) {
            Write-Host "✓ Found $($dsResponse.value.Count) total data source(s)"
            
            # Check which data sources belong to this collection
            foreach ($ds in $dsResponse.value) {
                $dsCollectionRef = $null
                if ($ds.properties -and $ds.properties.collection -and $ds.properties.collection.referenceName) {
                    $dsCollectionRef = $ds.properties.collection.referenceName
                }
                
                Write-Host "  Data Source: $($ds.name) -> Collection: $($dsCollectionRef)"
                
                if ($dsCollectionRef -eq $collectionId -or $dsCollectionRef -eq $CollectionName) {
                    $collectionDataSources += $ds
                }
            }
            
            if ($collectionDataSources.Count -gt 0) {
                Write-Host "✓ Found $($collectionDataSources.Count) data source(s) in collection '$CollectionName':"
                $collectionDataSources | Format-Table name, kind -AutoSize
            } else {
                Write-Host "✗ No data sources found in collection '$CollectionName'"
            }
            
            $foundDataSources = $true
            break
        }
    } catch {
        Write-Host "  Data sources API v$apiVersion failed: $($_.Exception.Message)"
    }
}

if (-not $foundDataSources) {
    Write-Host "✗ Data sources API not available"
}

# 4. Check Scans for Collection Data Sources
if ($collectionDataSources.Count -gt 0) {
    Write-Host "`n4. SCANS FOR COLLECTION DATA SOURCES"
    Write-Host "=" * 50
    
    foreach ($ds in $collectionDataSources) {
        Write-Host "Checking scans for data source: $($ds.name)"
        $scanApiVersions = @("2023-09-01", "2022-07-01-preview")
        
        foreach ($scanApiVersion in $scanApiVersions) {
            $scansUri = "https://$AccountName.purview.azure.com/datasources/$($ds.name)/scans?api-version=$scanApiVersion"
            
            try {
                $scansResponse = Invoke-RestMethod -Method GET -Uri $scansUri -Headers $headers
                
                if ($scansResponse -and $scansResponse.value) {
                    Write-Host "✓ Found $($scansResponse.value.Count) scan(s) for $($ds.name):"
                    $scansResponse.value | Format-Table name, @{Name="Status";Expression={$_.properties.lastRun.result}} -AutoSize
                    break
                } else {
                    Write-Host "  No scans found for $($ds.name)"
                }
            } catch {
                Write-Host "  Scans API v$scanApiVersion failed for $($ds.name): $($_.Exception.Message)"
            }
        }
    }
}

Write-Host "`n=== SUMMARY ==="
Write-Host "Collection: $CollectionName (ID: $collectionId)"
Write-Host "Assets: $(if ($assetsResponse.value) { $assetsResponse.value.Count } else { 0 })"
Write-Host "Data Sources in Collection: $($collectionDataSources.Count)"
Write-Host ""
Write-Host "Script completed."
