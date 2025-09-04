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
    Write-Host "⚡ BULK MODE: Large bulk operations with minimal parallel jobs (500 assets per bulk request, 2 parallel jobs)..." -ForegroundColor Cyan
}

Write-Host "Press Ctrl+C to cancel if needed. Starting in 3 seconds..."
Start-Sleep -Seconds 3

# Start continuous deletion loop
Write-Host "`n🚀 Starting continuous deletion process..."
$totalDeleted = 0
$totalFailed = 0
$loopCount = 0
$overallStartTime = Get-Date

# Performance optimization settings with API protection
$batchSize = 1000          # Process assets in large batches for efficiency
$maxParallelJobs = 4       # INCREASED: More parallel jobs to compensate for smaller bulk sizes
$apiThrottleMs = 200       # REDUCED: Less throttling needed with smaller bulk requests
$batchThrottleMs = 800     # REDUCED: Shorter delays between batches
$retryDelayMs = 5000       # Delay after API errors (5 seconds)
$maxRetries = 3            # Maximum retries for failed requests
$bulkDeleteSize = 50       # RECOMMENDED: Microsoft best practice ~50 assets per bulk request

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
        # OPTIMIZED BULK MODE: Using Purview Bulk Delete API with parallel processing
        for ($i = 0; $i -lt $assets.Count; $i += $batchSize) {
            $endIndex = [Math]::Min($i + $batchSize - 1, $assets.Count - 1)
            $batch = $assets[$i..$endIndex]
            $batchNumber = [Math]::Floor($i / $batchSize) + 1
            $totalBatches = [Math]::Ceiling($assets.Count / $batchSize)
            
            Write-Host "  Processing batch $batchNumber/$totalBatches ($($batch.Count) assets)..." -NoNewline
            
            # Split batch into parallel chunks for bulk delete API
            $chunkSize = [Math]::Ceiling($batch.Count / $maxParallelJobs)
            $chunks = @()
            for ($j = 0; $j -lt $batch.Count; $j += $chunkSize) {
                $chunkEnd = [Math]::Min($j + $chunkSize - 1, $batch.Count - 1)
                $chunks += ,@($batch[$j..$chunkEnd])
            }
            
            # Process chunks in parallel using bulk delete API
            $jobs = @()
            foreach ($chunk in $chunks) {
                $job = Start-Job -ScriptBlock {
                    param($assetChunk, $accountName, $accessToken, $throttleMs, $maxRetries, $retryDelayMs, $bulkDeleteSize)
                    
                    $headers = @{
                        'Authorization' = "Bearer $accessToken"
                        'Content-Type'  = 'application/json'
                    }
                    
                    $success = 0
                    $failed = 0
                    $currentBulkSize = $bulkDeleteSize
                    
                    # Process chunk in bulk delete groups with adaptive sizing
                    for ($k = 0; $k -lt $assetChunk.Count; $k += $currentBulkSize) {
                        $bulkEndIndex = [Math]::Min($k + $currentBulkSize - 1, $assetChunk.Count - 1)
                        $bulkGroup = $assetChunk[$k..$bulkEndIndex]
                        
                        # Build bulk delete URI with multiple guid parameters
                        $guidParams = ($bulkGroup | ForEach-Object { "guid=$($_.id)" }) -join "&"
                        $bulkDeleteUri = "https://$accountName.purview.azure.com/datamap/api/atlas/v2/entity/bulk?$guidParams"
                        
                        # Check URL length - reduce bulk size if too long
                        if ($bulkDeleteUri.Length -gt 8000) {
                            $currentBulkSize = [Math]::Max(50, [Math]::Floor($currentBulkSize * 0.7))
                            Write-Warning "URL too long, reducing bulk size to $currentBulkSize"
                            continue  # Retry with smaller batch
                        }
                        
                        $retryCount = 0
                        $deleted = $false
                        
                        while (-not $deleted -and $retryCount -le $maxRetries) {
                            try {
                                $result = Invoke-RestMethod -Method DELETE -Uri $bulkDeleteUri -Headers $headers -TimeoutSec 120
                                
                                # Count successful deletions from bulk response
                                if ($result.mutatedEntities -and $result.mutatedEntities.DELETE) {
                                    $success += $result.mutatedEntities.DELETE.Count
                                } else {
                                    $success += $bulkGroup.Count  # Assume all succeeded if no detailed response
                                }
                                $deleted = $true
                                
                            } catch {
                                $retryCount++
                                
                                # Check for specific error types that might indicate bulk size issues
                                if ($_.Exception.Message -match "URI too long|Request-URI Too Large|414") {
                                    # URL too long - reduce bulk size permanently
                                    $currentBulkSize = [Math]::Max(50, [Math]::Floor($currentBulkSize * 0.5))
                                    Write-Warning "URI too long error, reducing bulk size to $currentBulkSize"
                                    break  # Break retry loop and try with smaller size
                                } elseif ($_.Exception.Response.StatusCode -eq 429 -or $_.Exception.Response.StatusCode -eq 503) {
                                    # Rate limited or service unavailable - wait longer
                                    Start-Sleep -Milliseconds $retryDelayMs
                                } elseif ($_.Exception.Message -match "timeout|timed out") {
                                    # Timeout - reduce bulk size
                                    $currentBulkSize = [Math]::Max(50, [Math]::Floor($currentBulkSize * 0.8))
                                    Write-Warning "Timeout error, reducing bulk size to $currentBulkSize"
                                    break
                                } elseif ($retryCount -le $maxRetries) {
                                    # Other error - shorter retry delay
                                    Start-Sleep -Milliseconds ($retryDelayMs / 2)
                                } else {
                                    $failed += $bulkGroup.Count
                                }
                            }
                            
                            # Throttle API calls to avoid DDoS protection
                            Start-Sleep -Milliseconds $throttleMs
                        }
                        
                        if (-not $deleted -and $retryCount -gt $maxRetries) {
                            $failed += $bulkGroup.Count
                        }
                    }
                    
                    return @{ Success = $success; Failed = $failed; OptimalBulkSize = $currentBulkSize }
                } -ArgumentList $chunk, $AccountName, $accessToken, $apiThrottleMs, $maxRetries, $retryDelayMs, $bulkDeleteSize
                
                $jobs += $job
                
                # Stagger job starts to avoid overwhelming the API
                Start-Sleep -Milliseconds 100
            }
            
            # Wait for all parallel jobs to complete and collect results
            $batchSuccess = 0
            $batchFailed = 0
            $optimalSizes = @()
            
            $results = $jobs | Wait-Job | Receive-Job
            $jobs | Remove-Job
            
            foreach ($result in $results) {
                $batchSuccess += $result.Success
                $batchFailed += $result.Failed
                $loopSuccessCount += $result.Success
                $loopFailureCount += $result.Failed
                if ($result.OptimalBulkSize) {
                    $optimalSizes += $result.OptimalBulkSize
                }
            }
            
            # Adaptive bulk size adjustment based on feedback
            if ($optimalSizes.Count -gt 0) {
                $avgOptimalSize = [Math]::Floor(($optimalSizes | Measure-Object -Average).Average)
                if ($avgOptimalSize -lt $bulkDeleteSize) {
                    $bulkDeleteSize = $avgOptimalSize
                    Write-Host "    📊 Adaptive sizing: Reduced bulk size to $bulkDeleteSize for better performance" -ForegroundColor Cyan
                }
            }
            
            Write-Host " ✅ $batchSuccess/$($batch.Count) deleted (bulk API)"
            if ($batchFailed -gt 0) {
                Write-Host "    ⚠️ $batchFailed failed (will retry in next loop)" -ForegroundColor Yellow
            }
            
            # Throttle between batches to respect API limits
            Start-Sleep -Milliseconds $batchThrottleMs
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
