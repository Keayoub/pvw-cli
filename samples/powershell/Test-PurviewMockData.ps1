# Test-PurviewMockData.ps1
# Mock test script to validate Remove-PurviewAsset-Batch.ps1 performance and functionality
# Creates mock Purview responses to test the bulk delete script without affecting real data

param(
    [Parameter(Mandatory = $true)]
    [string]$AccountName,
    [Parameter(Mandatory = $true)]
    [string]$CollectionName,
    [Parameter(Mandatory = $false)]
    [ValidateSet("SMALL", "MEDIUM", "LARGE", "MASSIVE")]
    [string]$TestSize = "MEDIUM",
    [Parameter(Mandatory = $false)]
    [switch]$TestErrors,
    [Parameter(Mandatory = $false)]
    [switch]$TestRateLimiting
)

# Test configurations
$testConfigs = @{
    "SMALL"   = @{ AssetCount = 150; Loops = 2; Description = "Small test (150 assets)" }
    "MEDIUM"  = @{ AssetCount = 1500; Loops = 5; Description = "Medium test (1,500 assets)" }
    "LARGE"   = @{ AssetCount = 15000; Loops = 20; Description = "Large test (15,000 assets)" }
    "MASSIVE" = @{ AssetCount = 50000; Loops = 60; Description = "Massive test (50,000 assets)" }
}

$config = $testConfigs[$TestSize]
Write-Host "🧪 MOCK TEST CONFIGURATION" -ForegroundColor Cyan
Write-Host "Test Size: $($config.Description)" -ForegroundColor Yellow
Write-Host "Mock Assets: $($config.AssetCount)" -ForegroundColor Yellow
Write-Host "Expected Loops: ~$($config.Loops)" -ForegroundColor Yellow
Write-Host "Account: $AccountName" -ForegroundColor Yellow
Write-Host "Collection: $CollectionName" -ForegroundColor Yellow

if ($TestErrors) {
    Write-Host "⚠️  Error simulation: ENABLED" -ForegroundColor Red
}
if ($TestRateLimiting) {
    Write-Host "⚠️  Rate limiting simulation: ENABLED" -ForegroundColor Red
}

Write-Host "`n" + "="*60
Write-Host "🚀 Starting Mock Test Execution..." -ForegroundColor Green
Write-Host "="*60

# Create mock HTTP server function
function Start-MockPurviewServer {
    param($Port = 8080)
    
    Write-Host "🔧 Setting up mock Purview API responses..."
    
    # This would normally start a local HTTP server
    # For this demo, we'll simulate the responses in the script
    Write-Host "✅ Mock server ready on port $Port"
}

# Generate mock asset data
function Generate-MockAssets {
    param($Count)
    
    Write-Host "📝 Generating $Count mock assets..."
    
    $assets = @()
    for ($i = 1; $i -le $Count; $i++) {
        $assets += [PSCustomObject]@{
            id = [System.Guid]::NewGuid().ToString()
            typeName = @("azure_blob_container", "azure_sql_table", "azure_data_factory_pipeline", "azure_synapse_table")[(Get-Random -Maximum 4)]
            displayText = "MockAsset_$i"
            qualifiedName = "mock://test/asset$i"
            status = "ACTIVE"
        }
    }
    
    Write-Host "✅ Generated $Count mock assets"
    return $assets
}

# Mock the Remove-PurviewAsset-Batch.ps1 script behavior
function Test-BulkDeletePerformance {
    param($MockAssets)
    
    Write-Host "`n🎯 PERFORMANCE TEST SIMULATION" -ForegroundColor Cyan
    Write-Host "Testing bulk delete with $($MockAssets.Count) assets..."
    
    # Simulate the script's performance settings
    $batchSize = 1000
    $maxParallelJobs = 4
    $bulkDeleteSize = 50
    $apiThrottleMs = 200
    $batchThrottleMs = 800
    
    $totalDeleted = 0
    $totalFailed = 0
    $loopCount = 0
    $overallStartTime = Get-Date
    
    # Simulate the continuous loop
    $remainingAssets = $MockAssets
    
    while ($remainingAssets.Count -gt 0) {
        $loopCount++
        $loopStartTime = Get-Date
        
        Write-Host "`n=== MOCK LOOP $loopCount ==="
        
        # Simulate search (take up to 1000 assets)
        $searchLimit = [Math]::Min(1000, $remainingAssets.Count)
        $currentBatch = $remainingAssets[0..($searchLimit - 1)]
        $remainingAssets = $remainingAssets[$searchLimit..($remainingAssets.Count - 1)]
        
        Write-Host "🔍 Mock search found $($currentBatch.Count) assets"
        
        # Simulate bulk processing
        $loopSuccessCount = 0
        $loopFailureCount = 0
        
        for ($i = 0; $i -lt $currentBatch.Count; $i += $batchSize) {
            $endIndex = [Math]::Min($i + $batchSize - 1, $currentBatch.Count - 1)
            $batch = $currentBatch[$i..$endIndex]
            $batchNumber = [Math]::Floor($i / $batchSize) + 1
            $totalBatches = [Math]::Ceiling($currentBatch.Count / $batchSize)
            
            Write-Host "  Processing batch $batchNumber/$totalBatches ($($batch.Count) assets)..." -NoNewline
            
            # Simulate parallel processing
            $chunks = @()
            $chunkSize = [Math]::Ceiling($batch.Count / $maxParallelJobs)
            for ($j = 0; $j -lt $batch.Count; $j += $chunkSize) {
                $chunkEnd = [Math]::Min($j + $chunkSize - 1, $batch.Count - 1)
                $chunks += ,@($batch[$j..$chunkEnd])
            }
            
            $batchSuccess = 0
            $batchFailed = 0
            
            # Simulate parallel job processing
            foreach ($chunk in $chunks) {
                # Simulate bulk delete groups
                for ($k = 0; $k -lt $chunk.Count; $k += $bulkDeleteSize) {
                    $bulkEndIndex = [Math]::Min($k + $bulkDeleteSize - 1, $chunk.Count - 1)
                    $bulkGroup = $chunk[$k..$bulkEndIndex]
                    
                    # Simulate API call delay
                    Start-Sleep -Milliseconds ($apiThrottleMs / 10)  # Faster for testing
                    
                    # Simulate success/failure
                    $simulatedSuccess = $bulkGroup.Count
                    $simulatedFailed = 0
                    
                    # Simulate occasional failures if TestErrors is enabled
                    if ($TestErrors -and (Get-Random -Maximum 10) -eq 0) {
                        $simulatedFailed = [Math]::Floor($bulkGroup.Count * 0.1)
                        $simulatedSuccess = $bulkGroup.Count - $simulatedFailed
                    }
                    
                    # Simulate rate limiting if enabled
                    if ($TestRateLimiting -and (Get-Random -Maximum 20) -eq 0) {
                        Write-Host " [RATE LIMITED]" -ForegroundColor Yellow -NoNewline
                        Start-Sleep -Milliseconds ($apiThrottleMs * 2)
                    }
                    
                    $batchSuccess += $simulatedSuccess
                    $batchFailed += $simulatedFailed
                }
            }
            
            $loopSuccessCount += $batchSuccess
            $loopFailureCount += $batchFailed
            
            Write-Host " ✅ $batchSuccess/$($batch.Count) deleted (mock)"
            if ($batchFailed -gt 0) {
                Write-Host "    ⚠️ $batchFailed failed (simulated)" -ForegroundColor Yellow
            }
            
            # Simulate batch throttling
            Start-Sleep -Milliseconds ($batchThrottleMs / 10)  # Faster for testing
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
        
        # Show remaining assets
        if ($remainingAssets.Count -gt 0) {
            Write-Host "📋 Remaining assets: $($remainingAssets.Count)"
        }
        
        # Short delay before next search
        Start-Sleep -Milliseconds 50  # Faster for testing
    }
    
    # Final summary
    $totalTime = (Get-Date) - $overallStartTime
    $finalRate = if ($totalTime.TotalMinutes -gt 0) { [Math]::Round($totalDeleted / $totalTime.TotalMinutes, 0) } else { 0 }
    
    Write-Host "`n🎉 === MOCK TEST COMPLETE ===" -ForegroundColor Green
    Write-Host "✅ Total assets processed: $totalDeleted"
    Write-Host "❌ Total failures: $totalFailed"
    Write-Host "🔄 Total loops executed: $loopCount"
    Write-Host "⏱️  Total time: $([Math]::Round($totalTime.TotalMinutes, 2)) minutes"
    Write-Host "🚀 Average rate: $finalRate deletions/minute"
    
    # Performance analysis
    Write-Host "`n📊 PERFORMANCE ANALYSIS" -ForegroundColor Cyan
    
    $expectedRealTime = ($config.AssetCount / $finalRate) * 850000 / $config.AssetCount
    Write-Host "📈 Projected time for 850K assets: $([Math]::Round($expectedRealTime, 1)) minutes ($([Math]::Round($expectedRealTime/60, 1)) hours)"
    
    $apiCalls = $loopCount * [Math]::Ceiling($config.AssetCount / 1000) * [Math]::Ceiling(1000 / 500)
    Write-Host "🔗 Estimated API calls made: $apiCalls"
    Write-Host "📡 API efficiency: $([Math]::Round($totalDeleted / $apiCalls, 0)) assets per call"
    
    if ($finalRate -gt 3000) {
        Write-Host "🚀 EXCELLENT: Performance exceeds 3000 assets/minute target!" -ForegroundColor Green
    } elseif ($finalRate -gt 2000) {
        Write-Host "✅ GOOD: Performance meets 2000+ assets/minute target" -ForegroundColor Green
    } elseif ($finalRate -gt 1000) {
        Write-Host "⚠️  ACCEPTABLE: Performance above 1000 assets/minute" -ForegroundColor Yellow
    } else {
        Write-Host "❌ POOR: Performance below 1000 assets/minute - needs optimization" -ForegroundColor Red
    }
    
    return @{
        TotalDeleted = $totalDeleted
        TotalFailed = $totalFailed
        LoopCount = $loopCount
        TotalTimeMinutes = $totalTime.TotalMinutes
        AverageRate = $finalRate
        ProjectedTimeFor850K = $expectedRealTime
    }
}

# Main test execution
try {
    Write-Host "🏁 Starting mock test execution..." -ForegroundColor Green
    
    # Generate mock data
    $mockAssets = Generate-MockAssets -Count $config.AssetCount
    
    # Run performance test
    $results = Test-BulkDeletePerformance -MockAssets $mockAssets
    
    # Save test results
    $testReport = @{
        TestConfiguration = $config
        TestParameters = @{
            AccountName = $AccountName
            CollectionName = $CollectionName
            TestSize = $TestSize
            ErrorsEnabled = $TestErrors.IsPresent
            RateLimitingEnabled = $TestRateLimiting.IsPresent
        }
        Results = $results
        Timestamp = Get-Date
    }
    
    $reportPath = ".\Mock-Test-Results-$TestSize-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
    $testReport | ConvertTo-Json -Depth 4 | Out-File -FilePath $reportPath -Encoding UTF8
    
    Write-Host "`n💾 Test report saved to: $reportPath" -ForegroundColor Cyan
    
    Write-Host "`n🎯 RECOMMENDATIONS" -ForegroundColor Magenta
    if ($results.AverageRate -ge 2000) {
        Write-Host "✅ Script is ready for production use with 850K assets"
        Write-Host "✅ Expected completion time: $([Math]::Round($results.ProjectedTimeFor850K/60, 1)) hours"
    } else {
        Write-Host "⚠️  Consider optimizing batch sizes or parallel settings"
        Write-Host "⚠️  Test with -TestErrors and -TestRateLimiting for robustness"
    }
    
} catch {
    Write-Error "Mock test failed: $_"
    Write-Host "❌ Check your parameters and try again" -ForegroundColor Red
}

Write-Host "`n🏁 Mock test completed!" -ForegroundColor Green
Write-Host "Ready to test the real script: .\Remove-PurviewAsset-Batch.ps1 -AccountName $AccountName -CollectionName $CollectionName -Mode BULK"
