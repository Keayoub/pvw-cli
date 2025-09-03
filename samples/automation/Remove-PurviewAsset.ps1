# Remove-PurviewAsset.ps1
# Simple script to remove assets from a collection in Azure Purview
# Usage: .\Remove-PurviewAsset.ps1 -AccountName <PurviewAccountName> -CollectionName <CollectionName> [-AssetName <AssetName>] [-ListOnly]

param(
    [Parameter(Mandatory=$true)]
    [string]$AccountName,
    [Parameter(Mandatory=$true)]
    [string]$CollectionName,
    [Parameter(Mandatory=$false)]
    [string]$AssetName,
    [Parameter(Mandatory=$false)]
    [switch]$ListOnly,
    [Parameter(Mandatory=$false)]
    [switch]$ShowAll
)

# Get access token
Write-Host "Getting access token..."
try {
    $tokenJson = az account get-access-token --resource "https://purview.azure.net" --output json
    $tokenData = $tokenJson | ConvertFrom-Json
    $accessToken = $tokenData.accessToken
    Write-Host "Token acquired successfully."
} catch {
    Write-Error "Failed to get access token: $_"
    exit 1
}

$headers = @{
    'Authorization' = "Bearer $accessToken"
    'Content-Type' = 'application/json'
}

Write-Host "Account: $AccountName"
Write-Host "Collection: $CollectionName"

# Verify collection exists
Write-Host "`nVerifying collection..."
$collectionsUri = "https://$AccountName.purview.azure.com/account/collections?api-version=2019-11-01-preview"
try {
    $collectionsResponse = Invoke-RestMethod -Method GET -Uri $collectionsUri -Headers $headers
    $targetCollection = $collectionsResponse.value | Where-Object { $_.name -eq $CollectionName }
    
    if (-not $targetCollection) {
        Write-Error "Collection '$CollectionName' not found."
        Write-Host "Available collections:"
        $collectionsResponse.value | ForEach-Object { Write-Host "  - $($_.name)" }
        exit 1
    }
    
    Write-Host "Collection found: $($targetCollection.name)"
    $collectionId = $targetCollection.name
} catch {
    Write-Error "Failed to retrieve collections: $($_.Exception.Message)"
    exit 1
}

# Search for assets in the collection with pagination
Write-Host "`nSearching for assets in collection..."
$searchUri = "https://$AccountName.purview.azure.com/datamap/api/search/query?api-version=2023-09-01"
$allAssets = @()
$limit = 1000  # Maximum per request
$offset = 0

do {
    $searchBody = @{ 
        "keywords" = "*"
        "limit" = $limit
        "offset" = $offset
        "filter" = @{ "collectionId" = $collectionId }
    } | ConvertTo-Json

    try {
        $assetsResponse = Invoke-RestMethod -Method POST -Uri $searchUri -Headers $headers -Body $searchBody
        if ($assetsResponse.value) {
            $allAssets += $assetsResponse.value
            $offset += $limit
            Write-Host "Found $($allAssets.Count) assets so far..."
        }
    } catch {
        Write-Error "Failed to search for assets: $($_.Exception.Message)"
        exit 1
    }
} while ($assetsResponse.value -and $assetsResponse.value.Count -eq $limit)

$assets = $allAssets

if (-not $assets -or $assets.Count -eq 0) {
    Write-Host "No assets found in collection '$CollectionName'."
    exit 0
}

Write-Host "Found $($assets.Count) total asset(s) in collection:"

if ($assets.Count -gt 10000) {
    # For very large collections (>10K), just show the count
    Write-Host "Collection contains $($assets.Count) assets - too many to display individually."
    Write-Host "Asset types summary:"
    $assetTypes = $assets | Group-Object assetType | Sort-Object Count -Descending
    $assetTypes | ForEach-Object { Write-Host "  $($_.Name): $($_.Count) assets" }
} elseif ($ShowAll -or $assets.Count -le 20) {
    # Show all assets if ShowAll flag is used or 20 or fewer
    for ($i = 0; $i -lt $assets.Count; $i++) {
        $asset = $assets[$i]
        Write-Host "[$($i + 1)] Name: $($asset.name)"
        Write-Host "    Type: $($asset.assetType)"
        Write-Host "    ID: $($asset.id)"
        Write-Host ""
    }
} else {
    # Show first 10 and last 10 for medium collections (21-10K)
    Write-Host "Showing first 10 and last 10 assets (use -ShowAll to see all $($assets.Count) assets):"
    for ($i = 0; $i -lt 10; $i++) {
        $asset = $assets[$i]
        Write-Host "[$($i + 1)] Name: $($asset.name) | Type: $($asset.assetType)"
    }
    Write-Host "... ($($assets.Count - 20) more assets) ..."
    for ($i = ($assets.Count - 10); $i -lt $assets.Count; $i++) {
        $asset = $assets[$i]
        Write-Host "[$($i + 1)] Name: $($asset.name) | Type: $($asset.assetType)"
    }
}

# If ListOnly, show options and exit
if ($ListOnly) {
    Write-Host "To remove assets, use one of these commands:"
    Write-Host "  Remove specific asset:"
    Write-Host "    .\Remove-PurviewAsset.ps1 -AccountName $AccountName -CollectionName $CollectionName -AssetName 'AssetNameHere'"
    Write-Host ""
    Write-Host "  List assets only:"
    Write-Host "    .\Remove-PurviewAsset.ps1 -AccountName $AccountName -CollectionName $CollectionName -ListOnly"
    exit 0
}

# Find the asset to remove
if (-not $AssetName) {
    Write-Host "No -AssetName specified."
    Write-Host "This script will PERMANENTLY DELETE ALL $($assets.Count) assets from the collection."
    Write-Host "⚠️  WARNING: This action cannot be undone!"
    $confirmation = Read-Host "Type 'DELETE' to confirm permanent deletion of ALL $($assets.Count) assets from Purview"
    if ($confirmation -ne 'DELETE') {
        Write-Host "Operation cancelled."
        exit 0
    }
    $assetsToRemove = $assets
} else {
    $assetToRemove = $assets | Where-Object { $_.name -eq $AssetName }
    if (-not $assetToRemove) {
        Write-Error "Asset '$AssetName' not found in collection."
        Write-Host "Available assets:"
        $assets | ForEach-Object { Write-Host "  - $($_.name)" }
        exit 1
    }
    $assetsToRemove = @($assetToRemove)
}

# Delete assets permanently from Purview in batches
$total = $assetsToRemove.Count
$successCount = 0
$failureCount = 0
$batchSize = 100  # Process in batches for better performance

Write-Host "`nDeleting $total asset(s) permanently from Purview in batches of $batchSize..."

for ($i = 0; $i -lt $total; $i += $batchSize) {
    $endIndex = [Math]::Min($i + $batchSize - 1, $total - 1)
    $batch = $assetsToRemove[$i..$endIndex]
    $batchNumber = [Math]::Floor($i / $batchSize) + 1
    $totalBatches = [Math]::Ceiling($total / $batchSize)
    
    Write-Host "`nProcessing batch $batchNumber/$totalBatches ($($batch.Count) assets)..."
    
    # Try bulk delete first
    $guids = $batch | ForEach-Object { $_.id }
    $bulkDeleteUri = "https://$AccountName.purview.azure.com/catalog/api/atlas/v2/entity/bulk"
    
    # Create query string with GUIDs
    $guidParams = ($guids | ForEach-Object { "guid=$_" }) -join "&"
    $bulkDeleteUriWithParams = "$bulkDeleteUri?$guidParams"
    
    try {
        Invoke-RestMethod -Method DELETE -Uri $bulkDeleteUriWithParams -Headers $headers
        Write-Host "  ✓ Bulk deleted $($batch.Count) assets successfully"
        $successCount += $batch.Count
    } catch {
        Write-Host "  ✗ Bulk delete failed: $($_.Exception.Message)"
        Write-Host "  Falling back to individual deletion for this batch..."
        
        # Fall back to individual deletion for this batch
        foreach ($asset in $batch) {
            Write-Host "    Deleting: $($asset.name)"
            $deleteUri = "https://$AccountName.purview.azure.com/catalog/api/atlas/v2/entity/guid/$($asset.id)"
            
            try {
                Invoke-RestMethod -Method DELETE -Uri $deleteUri -Headers $headers
                Write-Host "      ✓ Deleted"
                $successCount++
            } catch {
                Write-Host "      ✗ Failed: $($_.Exception.Message)"
                $failureCount++
            }
        }
    }
    
    # Progress update
    $percentComplete = [Math]::Round(($successCount + $failureCount) / $total * 100, 1)
    Write-Host "  Progress: $($successCount + $failureCount)/$total ($percentComplete%) completed"
}

Write-Host "`n=== SUMMARY ==="
Write-Host "Successfully deleted: $successCount asset(s)"
Write-Host "Failed to delete: $failureCount asset(s)"
Write-Host "Total processed: $total asset(s)"

Write-Host "`nScript completed."
