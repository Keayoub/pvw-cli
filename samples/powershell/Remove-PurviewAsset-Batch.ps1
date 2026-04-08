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
    Write-Host "[OK] Token acquired successfully."
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

# Performance optimization settings with API protection - defined early for consistency
$batchSize = 1000          # Process assets in large batches for efficiency
$maxParallelJobs = 10      # 100 assets/job = exactly 2 API calls per job
$apiThrottleMs = 200       # Less throttling needed with smaller bulk requests
$batchThrottleMs = 800     # Shorter delays between batches
$retryDelayMs = 5000       # Delay after API errors (5 seconds)
$maxRetries = 3            # Maximum retries for failed requests
$bulkDeleteSize = 50       # RECOMMENDED: Microsoft best practice ~50 assets per bulk request

# Function to search for assets
function Search-PurviewAssets {
    param($searchUri, $headers, $collectionName, $limit = $batchSize)  # Use global batchSize variable
    
    $searchBody = @{
        "keywords" = "*"
        "limit"    = $limit
        "filter"   = @{
            "collectionId" = $collectionName
        }
    } | ConvertTo-Json -Depth 3

    try {
        $assetsResponse = Invoke-RestMethod -Method POST -Uri $searchUri -Headers $headers -Body $searchBody
        $found = if ($assetsResponse.value) { $assetsResponse.value.Count } else { 0 }
        Write-Host "  [OK] Search successful, found $found assets" -ForegroundColor Green
        
        if ($assetsResponse.value -and $assetsResponse.value.Count -gt 0) {
            return $assetsResponse.value
        }
        return @()  # Always return empty array on success with 0 results
    }
    catch {
        Write-Host "  [X] Search failed with detailed error:" -ForegroundColor Red
        Write-Host "    Status Code: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        Write-Host "    Error Message: $($_.Exception.Message)" -ForegroundColor Yellow
        
        # Try to get response content for more details
        try {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($errorStream)
            $errorContent = $reader.ReadToEnd()
            Write-Host "    Response Content: $errorContent" -ForegroundColor Yellow
        }
        catch {
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
    Write-Host "[OK] Purview account accessible"
    
    # Check if our target collection exists
    $targetCollection = $collectionsResponse.value | Where-Object { $_.name -eq $CollectionName }
    if (-not $targetCollection) {
        Write-Host "[X] Collection '$CollectionName' not found!" -ForegroundColor Red
        exit 1
    }
}
catch {
    Write-Host "[X] Cannot access Purview account:" -ForegroundColor Red
    Write-Host "  Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
    exit 1
}

$initialAssets = Search-PurviewAssets -searchUri $searchUri -headers $headers -collectionName $CollectionName -limit 10

# Check if search failed completely (null result indicates API error)
if ($null -eq $initialAssets) {
    Write-Host "[X] Search API error - cannot continue." -ForegroundColor Red
    exit 1
}

# If search returned 0, try Atlas direct query (bypasses search index lag)
if ($initialAssets.Count -eq 0) {
    Write-Host "[!] Search returned 0 assets - trying Atlas direct query (bypasses index lag)..." -ForegroundColor Yellow
    $atlasUri = "https://$AccountName.purview.azure.com/catalog/api/atlas/v2/search/basic?collectionId=$CollectionName&limit=100&api-version=2023-09-01"
    try {
        $atlasResp = Invoke-RestMethod -Method GET -Uri $atlasUri -Headers $headers
        if ($atlasResp -and $atlasResp.entities -and $atlasResp.entities.Count -gt 0) {
            Write-Host "  [OK] Atlas query found $($atlasResp.entities.Count) assets" -ForegroundColor Green
            # Normalize to same shape as search results
            $initialAssets = $atlasResp.entities | ForEach-Object {
                @{ id = if ($_.guid) { $_.guid } else { $_.id }; name = $_.displayText }
            }
        }
    } catch {
        Write-Host "  [!] Atlas query failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Second fallback: DSL search
if ($initialAssets.Count -eq 0) {
    Write-Host "[!] Trying Atlas DSL search..." -ForegroundColor Yellow
    $dslUri = "https://$AccountName.purview.azure.com/catalog/api/atlas/v2/search/dsl?api-version=2023-09-01"
    $dslBody = @{
        query = @{ bool = @{ filter = @(@{ term = @{ "collectionId" = $CollectionName } }) } }
        size = 1000
    } | ConvertTo-Json -Depth 6
    try {
        $dslResp = Invoke-RestMethod -Method POST -Uri $dslUri -Headers $headers -Body $dslBody -ContentType "application/json"
        if ($dslResp -and $dslResp.entities -and $dslResp.entities.Count -gt 0) {
            Write-Host "  [OK] DSL search found $($dslResp.entities.Count) assets" -ForegroundColor Green
            $initialAssets = $dslResp.entities | ForEach-Object {
                @{ id = if ($_.guid) { $_.guid } else { $_.id }; name = $_.displayText }
            }
        }
    } catch {
        Write-Host "  [!] DSL search failed: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# If still 0 after all fallbacks, collection is truly empty
if ($initialAssets.Count -eq 0) {
    Write-Host "[OK] Collection '$CollectionName' appears empty - no assets found via any search method." -ForegroundColor Green
    Write-Host "     If a 409 still occurs on collection delete, the blocking references may be scan history or lineage." -ForegroundColor Yellow
    Write-Host "     Try: pvw entity bulk-delete-from-collection --collection-name $CollectionName" -ForegroundColor Cyan
    exit 0
}

Write-Host "[OK] Collection contains assets. Starting comprehensive search..."

# Get a larger sample to estimate total (use smaller limit to avoid API restrictions)
$sampleAssets = Search-PurviewAssets -searchUri $searchUri -headers $headers -collectionName $CollectionName -limit $batchSize

if ($sampleAssets -and $sampleAssets.Count -gt 0) {
    Write-Host "[STATS] Found $($sampleAssets.Count) assets in collection"
    if ($sampleAssets.Count -eq $batchSize) {
        Write-Host "[!]  Collection has $batchSize+ assets - continuous loop will process all"
    }
}
else {
    Write-Host "[X] No assets found in collection."
    exit 0
}

# If ListOnly, exit
if ($ListOnly) {
    Write-Host "`nTo delete ALL assets in this collection, run:"
    Write-Host "  .\Remove-PurviewAsset-Batch.ps1 -AccountName $AccountName -CollectionName $CollectionName -Mode BULK"
    Write-Host "  .\Remove-PurviewAsset-Batch.ps1 -AccountName $AccountName -CollectionName $CollectionName -Mode SINGLE"
    Write-Host "`n[!]  This will use a continuous loop to delete ALL assets until the collection is empty!"
    exit 0
}

# Set deletion mode based on parameter
Write-Host "`n[!]  This will PERMANENTLY DELETE ALL ASSETS from collection '$CollectionName'."
Write-Host "[!]  WARNING: This action cannot be undone!"
Write-Host "[!]  The script will run continuously until the collection is completely empty."
Write-Host ""

if ($Mode -eq 'SINGLE') {
    $bulkMode = $false
    Write-Host "[STATS] SINGLE MODE: Individual asset deletion with detailed progress..." -ForegroundColor Cyan
}
else {
    $bulkMode = $true
    Write-Host "[BULK] BULK MODE: Large bulk operations with minimal parallel jobs (500 assets per bulk request, 2 parallel jobs)..." -ForegroundColor Cyan
}

Write-Host "Press Ctrl+C to cancel if needed. Starting in 3 seconds..."
Start-Sleep -Seconds 3

# Start continuous deletion loop
Write-Host "`n[START] Starting continuous deletion process..."
$totalDeleted = 0
$totalFailed = 0
$loopCount = 0
$overallStartTime = Get-Date

do {
    $loopCount++
    $loopStartTime = Get-Date
    
    Write-Host "`n=== LOOP $loopCount ==="
    Write-Host "[SEARCH] Searching for next batch of assets..."
    
    # Search for assets (use batchSize to avoid API limits)
    $assets = Search-PurviewAssets -searchUri $searchUri -headers $headers -collectionName $CollectionName -limit $batchSize
    
    # Fallback to Atlas direct query if search returns 0 (index lag)
    if (-not $assets -or $assets.Count -eq 0) {
        Write-Host "  [!] Search returned 0 - trying Atlas direct query..." -ForegroundColor Yellow
        try {
            $atlasUri = "https://$AccountName.purview.azure.com/catalog/api/atlas/v2/search/basic?collectionId=$CollectionName&limit=1000&api-version=2023-09-01"
            $atlasResp = Invoke-RestMethod -Method GET -Uri $atlasUri -Headers $headers
            if ($atlasResp -and $atlasResp.entities -and $atlasResp.entities.Count -gt 0) {
                Write-Host "  [OK] Atlas query found $($atlasResp.entities.Count) assets" -ForegroundColor Green
                $assets = $atlasResp.entities | ForEach-Object {
                    @{ id = if ($_.guid) { $_.guid } else { $_.id }; name = $_.displayText }
                }
            }
        } catch {
            Write-Host "  [!] Atlas fallback failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }

    if (-not $assets -or $assets.Count -eq 0) {
        Write-Host "[OK] No more assets found - collection is empty!"
        break
    }
    
    Write-Host "[PKG] Found $($assets.Count) assets in this loop"
    
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
                $chunks += , @($batch[$j..$chunkEnd])
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
                                $actualDeleted = 0
                                
                                if ($result -and $result.mutatedEntities -and $result.mutatedEntities.DELETE) {
                                    $actualDeleted = $result.mutatedEntities.DELETE.Count
                                }
                                elseif ($result -and (-not $result.errorCode) -and (-not $result.error)) {
                                    $actualDeleted = $bulkGroup.Count
                                }
                                else {
                                    # Any other case - count as 0 for safety
                                    $actualDeleted = 0
                                }
                                
                                # CRITICAL: Cap the count to never exceed what we actually sent
                                $actualDeleted = [Math]::Min($actualDeleted, $bulkGroup.Count)
                                
                                $success += $actualDeleted
                                $deleted = $true
                                
                            }
                            catch {
                                $retryCount++
                                
                                # Check for specific error types that might indicate bulk size issues
                                if ($_.Exception.Message -match "URI too long|Request-URI Too Large|414") {
                                    # URL too long - reduce bulk size permanently
                                    $currentBulkSize = [Math]::Max(50, [Math]::Floor($currentBulkSize * 0.5))
                                    Write-Warning "URI too long error, reducing bulk size to $currentBulkSize"
                                    break  # Break retry loop and try with smaller size
                                }
                                elseif ($_.Exception.Response.StatusCode -eq 429 -or $_.Exception.Response.StatusCode -eq 503) {
                                    # Rate limited or service unavailable - wait longer
                                    Start-Sleep -Milliseconds $retryDelayMs
                                }
                                elseif ($_.Exception.Message -match "timeout|timed out") {
                                    # Timeout - reduce bulk size
                                    $currentBulkSize = [Math]::Max(50, [Math]::Floor($currentBulkSize * 0.8))
                                    Write-Warning "Timeout error, reducing bulk size to $currentBulkSize"
                                    break
                                }
                                elseif ($retryCount -le $maxRetries) {
                                    # Other error - shorter retry delay
                                    Start-Sleep -Milliseconds ($retryDelayMs / 2)
                                }
                                else {
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
            
            # DEBUG: Track job results for accuracy with validation
            $jobCount = 0
            foreach ($result in $results) {
                $jobCount++                
                $maxPossibleSuccess = $chunks[$jobCount - 1].Count
                $actualSuccess = [Math]::Min($result.Success, $maxPossibleSuccess)
                
                if ($result.Success -gt $maxPossibleSuccess) {
                    Write-Host "    [!] Job $jobCount reported $($result.Success) successes but only had $maxPossibleSuccess assets - correcting" -ForegroundColor Yellow
                }
                              
                $batchSuccess += $actualSuccess
                $batchFailed += $result.Failed
                # Note: Don't add to loopSuccessCount here - it will be added after batch processing
                if ($result.OptimalBulkSize) {
                    $optimalSizes += $result.OptimalBulkSize
                }
            }
            
            # Adaptive bulk size adjustment based on feedback
            if ($optimalSizes.Count -gt 0) {
                $avgOptimalSize = [Math]::Floor(($optimalSizes | Measure-Object -Average).Average)
                if ($avgOptimalSize -lt $bulkDeleteSize) {
                    $bulkDeleteSize = $avgOptimalSize
                    Write-Host "    [STATS] Adaptive sizing: Reduced bulk size to $bulkDeleteSize for better performance" -ForegroundColor Cyan
                }
            }
            
            if ($batchSuccess -gt $batch.Count) {
                Write-Host "    [!] WARNING: Batch success ($batchSuccess) exceeds batch size ($($batch.Count)) - correcting to batch size" -ForegroundColor Red
                $batchSuccess = $batch.Count
            }
            
            Write-Host " [OK] $batchSuccess/$($batch.Count) deleted (bulk API)"
            if ($batchFailed -gt 0) {
                Write-Host "    [!] $batchFailed failed (will retry in next loop)" -ForegroundColor Yellow
            }
            
            # Add batch results to loop totals
            $loopSuccessCount += $batchSuccess
            $loopFailureCount += $batchFailed
            
            # Throttle between batches to respect API limits
            Start-Sleep -Milliseconds $batchThrottleMs
        }
    }
    else {
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
            }
            catch {
                $loopFailureCount++
            }
        }
    }
    
    # Loop summary
    $loopTime = (Get-Date) - $loopStartTime
    $loopRate = if ($loopTime.TotalMinutes -gt 0) { [Math]::Round($loopSuccessCount / $loopTime.TotalMinutes, 0) } else { 0 }
    $totalDeleted += $loopSuccessCount
    $totalFailed += $loopFailureCount
    
    Write-Host "[STATS] Loop $loopCount results: $loopSuccessCount deleted, $loopFailureCount failed | Rate: $loopRate/min"
    
    # Overall progress
    $overallTime = (Get-Date) - $overallStartTime
    $overallRate = if ($overallTime.TotalMinutes -gt 0) { [Math]::Round($totalDeleted / $overallTime.TotalMinutes, 0) } else { 0 }
    Write-Host "[TARGET] Overall progress: $totalDeleted total deleted | Overall rate: $overallRate/min"
    
    # Short delay before next search
    Start-Sleep -Milliseconds 500
    
} while ($assets -and $assets.Count -gt 0)

# Final comprehensive summary
$totalTime = (Get-Date) - $overallStartTime
$finalRate = if ($totalTime.TotalMinutes -gt 0) { [Math]::Round($totalDeleted / $totalTime.TotalMinutes, 0) } else { 0 }

Write-Host "`n[SUCCESS] === CONTINUOUS DELETION COMPLETE ==="
Write-Host "[OK] Total assets deleted: $totalDeleted"
Write-Host "[X] Total failures: $totalFailed"
Write-Host "[LOOP] Total loops executed: $loopCount"
Write-Host "[TIMER] Total time: $([Math]::Round($totalTime.TotalMinutes, 1)) minutes ($([Math]::Round($totalTime.TotalHours, 1)) hours)"
Write-Host "[START] Average rate: $finalRate deletions/minute"

if ($totalFailed -eq 0) {
    Write-Host "`n[SUCCESS] SUCCESS: All assets successfully deleted from collection '$CollectionName'!" -ForegroundColor Green
    Write-Host "[CLEANUP] Collection is now completely empty." -ForegroundColor Green
}
elseif ($totalDeleted -gt 0) {
    Write-Host "`n[OK] PARTIAL SUCCESS: $totalDeleted assets deleted, $totalFailed failed." -ForegroundColor Yellow
    Write-Host "[LOOP] You may run the script again to retry failed deletions." -ForegroundColor Yellow
}
else {
    Write-Host "`n[X] NO DELETIONS: No assets were deleted. Check permissions." -ForegroundColor Red
}
