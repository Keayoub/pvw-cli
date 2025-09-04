# Remove-PurviewAsset-Batch.ps1
# Continuous script to remove ALL assets from a collection using search-delete loops
# Usage: .\Remove-PurviewAsset-Batch.ps1 -AccountName <PurviewAccountName> -CollectionName <CollectionName> [-ListOnly] [-Mode <SINGLE|BULK>]

param(
    [Parameter(Mandatory = $true)]
    [string]$AccountName,
    [Parameter(Mandatory = $true)]
    [string]$CollectionName,
    [Parameter(Mandatory = $false)]
    [switch]$ListOnly,
    [Parameter(Mandatory = $false)]
    [ValidateSet("SINGLE", "BULK")]
    [string]$Mode = "BULK"
)

# Get access token
Write-Host "Getting access token..."
try {
    $tokenJson = az account get-access-token --resource "https://purview.azure.net" --output json
    $tokenData = $tokenJson | ConvertFrom-Json
    $accessToken = $tokenData.accessToken
    Write-Host "✅ Token acquired successfully."
}
catch {
    Write-Error "Failed to get access token: $_"
    exit 1
}

$headers = @{
    'Authorization' = "Bearer $accessToken"
    'Content-Type'  = 'application/json'
}

Write-Host "Account: $AccountName"
Write-Host "Collection: $CollectionName"

# Debug: Validate parameters
if ([string]::IsNullOrWhiteSpace($AccountName)) {
    Write-Error "AccountName parameter is empty or not provided!"
    Write-Host "Usage: .\Remove-PurviewAsset-Batch.ps1 -AccountName <PurviewAccountName> -CollectionName <CollectionName> [-ListOnly] [-Mode <SINGLE|BULK>]"
    exit 1
}

if ([string]::IsNullOrWhiteSpace($CollectionName)) {
    Write-Error "CollectionName parameter is empty or not provided!"
    Write-Host "Usage: .\Remove-PurviewAsset-Batch.ps1 -AccountName <PurviewAccountName> -CollectionName <CollectionName> [-ListOnly] [-Mode <SINGLE|BULK>]"
    exit 1
}

Write-Host "Debug: AccountName='$AccountName', CollectionName='$CollectionName'"

# Function to search for assets
function Search-PurviewAssets {
    param($searchUri, $headers, $collectionName, $limit = 5000)
    
    $searchBody = @{
        "keywords" = "*"
        "limit"    = $limit
        "filter"   = @{
            "collectionId" = $collectionName
        }
    } | ConvertTo-Json -Depth 3

    try {
        $assetsResponse = Invoke-RestMethod -Method POST -Uri $searchUri -Headers $headers -Body $searchBody
        Write-Host "  ✅ Search successful, found $($assetsResponse.value.Count) assets" -ForegroundColor Green
        
        # Ensure we always return an array (even if empty) and never null for successful searches
        if ($assetsResponse.value) {
            return $assetsResponse.value
        } else {
            return @()  # Return empty array instead of null
        }
    } catch {
        Write-Host "  ❌ Search failed with detailed error:" -ForegroundColor Red
        Write-Host "    Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        Write-Host "    Error Message: $($_.Exception.Message)" -ForegroundColor Yellow
        
        # Try to get response content for more details
        try {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorContent = $reader.ReadToEnd()
            Write-Host "    Response Content: $errorContent" -ForegroundColor Yellow
        } catch {
            Write-Host "    Could not read error response content" -ForegroundColor Yellow
        }
        
        return $null
    }
}

# Initial search to check collection
Write-Host "`nChecking collection for assets..."
$searchUri = "https://$AccountName.purview.azure.com/datamap/api/search/query?api-version=2023-09-01"

# First, test basic connectivity to Purview account
Write-Host "Testing basic Purview connectivity..."
$testUri = "https://$AccountName.purview.azure.com/account/collections?api-version=2019-11-01-preview"
try {
    $collectionsResponse = Invoke-RestMethod -Method GET -Uri $testUri -Headers $headers -TimeoutSec 30
    Write-Host "✅ Purview account accessible"
    
    # Check if our target collection exists
    $targetCollection = $collectionsResponse.value | Where-Object { $_.name -eq $CollectionName }
    if (-not $targetCollection) {
        Write-Host "❌ Collection '$CollectionName' not found!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Cannot access Purview account:" -ForegroundColor Red
    Write-Host "  Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
    exit 1
}

$initialAssets = Search-PurviewAssets -searchUri $searchUri -headers $headers -collectionName $CollectionName -limit 10

# Check if search failed completely (null result indicates API error)
if ($null -eq $initialAssets) {
    Write-Host "❌ Cannot access collection or search failed." -ForegroundColor Red
    exit 1
}

# Check if collection is empty (empty array or no assets)
if ($initialAssets.Count -eq 0) {
    Write-Host "✅ Collection '$CollectionName' is accessible and empty - no assets to delete!" -ForegroundColor Green
    Write-Host "The collection cleanup is complete." -ForegroundColor Cyan
    exit 0
}

Write-Host "✅ Collection contains assets. Starting comprehensive search..."

# Get a larger sample to estimate total (use smaller limit to avoid API restrictions)
$sampleAssets = Search-PurviewAssets -searchUri $searchUri -headers $headers -collectionName $CollectionName -limit 1000

if ($sampleAssets -and $sampleAssets.Count -gt 0) {
    Write-Host "📊 Found $($sampleAssets.Count) assets in collection"
    if ($sampleAssets.Count -eq 1000) {
        Write-Host "⚠️  Collection has 1000+ assets - continuous loop will process all"
    }
} else {
    Write-Host "❌ No assets found in collection."
    exit 0
}

# If ListOnly, exit
if ($ListOnly) {
    Write-Host "`nTo delete ALL assets in this collection, run:"
    Write-Host "  .\Remove-PurviewAsset-Batch.ps1 -AccountName $AccountName -CollectionName $CollectionName -Mode BULK"
    Write-Host "  .\Remove-PurviewAsset-Batch.ps1 -AccountName $AccountName -CollectionName $CollectionName -Mode SINGLE"
    Write-Host "`n⚠️  This will use a continuous loop to delete ALL assets until the collection is empty!"
    exit 0
}

# Set deletion mode based on parameter
Write-Host "`n⚠️  This will PERMANENTLY DELETE ALL ASSETS from collection '$CollectionName'."
Write-Host "⚠️  WARNING: This action cannot be undone!"
Write-Host "⚠️  The script will run continuously until the collection is completely empty."
Write-Host ""

if ($Mode -eq 'SINGLE') {
    $bulkMode = $false
    Write-Host "📊 SINGLE MODE: Individual asset deletion with detailed progress..." -ForegroundColor Cyan
} else {
    $bulkMode = $true
    Write-Host "⚡ BULK MODE: Batch processing for maximum speed (250 assets per batch)..." -ForegroundColor Cyan
}

Write-Host "Press Ctrl+C to cancel if needed. Starting in 3 seconds..."
Start-Sleep -Seconds 3

# Start continuous deletion loop
Write-Host "`n🚀 Starting continuous deletion process..."
$totalDeleted = 0
$totalFailed = 0
$loopCount = 0
$overallStartTime = Get-Date
$batchSize = 250

do {
    $loopCount++
    $loopStartTime = Get-Date
    
    Write-Host "`n=== LOOP $loopCount ==="
    Write-Host "🔍 Searching for next batch of assets..."
    
    # Search for assets (use safer batch size to avoid API limits)
    $assets = Search-PurviewAssets -searchUri $searchUri -headers $headers -collectionName $CollectionName -limit 1000
    
    if (-not $assets -or $assets.Count -eq 0) {
        Write-Host "✅ No more assets found - collection is empty!"
        break
    }
    
    Write-Host "📦 Found $($assets.Count) assets in this loop"
    
    # Delete assets in this loop
    $loopSuccessCount = 0
    $loopFailureCount = 0

    if ($bulkMode) {
        # BULK MODE: Process in 250-asset batches for speed
        for ($i = 0; $i -lt $assets.Count; $i += $batchSize) {
            $endIndex = [Math]::Min($i + $batchSize - 1, $assets.Count - 1)
            $batch = $assets[$i..$endIndex]
            $batchNumber = [Math]::Floor($i / $batchSize) + 1
            $totalBatches = [Math]::Ceiling($assets.Count / $batchSize)
            
            Write-Host "  Processing batch $batchNumber/$totalBatches ($($batch.Count) assets)..." -NoNewline
            
            $batchSuccess = 0
            foreach ($asset in $batch) {
                $deleteUri = "https://$AccountName.purview.azure.com/catalog/api/atlas/v2/entity/guid/$($asset.id)"
                try {
                    $null = Invoke-RestMethod -Method DELETE -Uri $deleteUri -Headers $headers -TimeoutSec 30
                    $batchSuccess++
                    $loopSuccessCount++
                } catch {
                    $loopFailureCount++
                }
            }
            Write-Host " ✅ $batchSuccess/$($batch.Count) deleted"
        }
    } else {
        # SINGLE MODE: Individual asset deletion with detailed progress
        $processed = 0
        foreach ($asset in $assets) {
            $processed++
            if (($processed % 100) -eq 0) {
                Write-Host "  Progress: $processed/$($assets.Count) assets processed..."
            }
            
            $deleteUri = "https://$AccountName.purview.azure.com/catalog/api/atlas/v2/entity/guid/$($asset.id)"
            try {
                $null = Invoke-RestMethod -Method DELETE -Uri $deleteUri -Headers $headers -TimeoutSec 30
                $loopSuccessCount++
            } catch {
                $loopFailureCount++
            }
        }
    }
    
    # Loop summary
    $loopTime = (Get-Date) - $loopStartTime
    $loopRate = if ($loopTime.TotalMinutes -gt 0) { [Math]::Round($loopSuccessCount / $loopTime.TotalMinutes, 0) } else { 0 }
    $totalDeleted += $loopSuccessCount
    $totalFailed += $loopFailureCount
    
    Write-Host "📊 Loop $loopCount results: $loopSuccessCount deleted, $loopFailureCount failed | Rate: $loopRate/min"
    
    # Overall progress
    $overallTime = (Get-Date) - $overallStartTime
    $overallRate = if ($overallTime.TotalMinutes -gt 0) { [Math]::Round($totalDeleted / $overallTime.TotalMinutes, 0) } else { 0 }
    Write-Host "🎯 Overall progress: $totalDeleted total deleted | Overall rate: $overallRate/min"
    
    # Short delay before next search
    Start-Sleep -Milliseconds 500
    
} while ($assets -and $assets.Count -gt 0)

# Final comprehensive summary
$totalTime = (Get-Date) - $overallStartTime
$finalRate = if ($totalTime.TotalMinutes -gt 0) { [Math]::Round($totalDeleted / $totalTime.TotalMinutes, 0) } else { 0 }

Write-Host "`n🎉 === CONTINUOUS DELETION COMPLETE ==="
Write-Host "✅ Total assets deleted: $totalDeleted"
Write-Host "❌ Total failures: $totalFailed"
Write-Host "🔄 Total loops executed: $loopCount"
Write-Host "⏱️  Total time: $([Math]::Round($totalTime.TotalMinutes, 1)) minutes ($([Math]::Round($totalTime.TotalHours, 1)) hours)"
Write-Host "🚀 Average rate: $finalRate deletions/minute"

if ($totalFailed -eq 0) {
    Write-Host "`n🎉 SUCCESS: All assets successfully deleted from collection '$CollectionName'!" -ForegroundColor Green
    Write-Host "🧹 Collection is now completely empty." -ForegroundColor Green
} elseif ($totalDeleted -gt 0) {
    Write-Host "`n✅ PARTIAL SUCCESS: $totalDeleted assets deleted, $totalFailed failed." -ForegroundColor Yellow
    Write-Host "🔄 You may run the script again to retry failed deletions." -ForegroundColor Yellow
} else {
    Write-Host "`n❌ NO DELETIONS: No assets were deleted. Check permissions." -ForegroundColor Red
}
