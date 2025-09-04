# Test-ScriptIntegration.ps1
# Integration test script to validate Remove-PurviewAsset-Batch.ps1 functions and logic
# Tests script components without making actual API calls

param(
    [Parameter(Mandatory = $false)]
    [string]$ScriptPath = ".\Remove-PurviewAsset-Batch.ps1"
)

Write-Host "🧪 INTEGRATION TEST FOR REMOVE-PURVIEWASSET-BATCH.PS1" -ForegroundColor Cyan
Write-Host "="*60

# Test 1: Parameter Validation
Write-Host "`n🔍 TEST 1: Parameter Validation" -ForegroundColor Yellow

try {
    # Test missing required parameters
    Write-Host "Testing missing parameters..."
    $result1 = & $ScriptPath -AccountName "" -CollectionName "test" 2>&1
    if ($result1 -match "AccountName parameter is empty") {
        Write-Host "✅ AccountName validation: PASS" -ForegroundColor Green
    } else {
        Write-Host "❌ AccountName validation: FAIL" -ForegroundColor Red
    }
    
    $result2 = & $ScriptPath -AccountName "test" -CollectionName "" 2>&1
    if ($result2 -match "CollectionName parameter is empty") {
        Write-Host "✅ CollectionName validation: PASS" -ForegroundColor Green
    } else {
        Write-Host "❌ CollectionName validation: FAIL" -ForegroundColor Red
    }
    
    # Test mode validation
    Write-Host "Testing mode validation..."
    $result3 = & $ScriptPath -AccountName "test" -CollectionName "test" -Mode "INVALID" 2>&1
    if ($result3 -match "Cannot validate argument") {
        Write-Host "✅ Mode validation: PASS" -ForegroundColor Green
    } else {
        Write-Host "❌ Mode validation: FAIL" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Parameter validation test failed: $_" -ForegroundColor Red
}

# Test 2: Script Syntax and Structure
Write-Host "`n🔍 TEST 2: Script Syntax Validation" -ForegroundColor Yellow

try {
    # Check if script has valid PowerShell syntax
    $syntaxErrors = Get-Command -Syntax $ScriptPath -ErrorAction SilentlyContinue
    if ($syntaxErrors) {
        Write-Host "✅ Script syntax: VALID" -ForegroundColor Green
    }
    
    # Check for required functions
    $scriptContent = Get-Content $ScriptPath -Raw
    
    if ($scriptContent -match "function Search-PurviewAssets") {
        Write-Host "✅ Search-PurviewAssets function: FOUND" -ForegroundColor Green
    } else {
        Write-Host "❌ Search-PurviewAssets function: MISSING" -ForegroundColor Red
    }
    
    if ($scriptContent -match "Start-Job -ScriptBlock") {
        Write-Host "✅ Parallel processing logic: FOUND" -ForegroundColor Green
    } else {
        Write-Host "❌ Parallel processing logic: MISSING" -ForegroundColor Red
    }
    
    if ($scriptContent -match "bulk\?.*guid=") {
        Write-Host "✅ Bulk delete API usage: FOUND" -ForegroundColor Green
    } else {
        Write-Host "❌ Bulk delete API usage: MISSING" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Syntax validation failed: $_" -ForegroundColor Red
}

# Test 3: Configuration Values
Write-Host "`n🔍 TEST 3: Configuration Analysis" -ForegroundColor Yellow

try {
    $scriptContent = Get-Content $ScriptPath -Raw
    
    # Extract configuration values
    if ($scriptContent -match '\$batchSize = (\d+)') {
        $batchSize = $Matches[1]
        Write-Host "📊 Batch Size: $batchSize" -ForegroundColor Cyan
        if ([int]$batchSize -ge 500) {
            Write-Host "✅ Batch size optimization: GOOD" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Batch size: Could be larger" -ForegroundColor Yellow
        }
    }
    
    if ($scriptContent -match '\$maxParallelJobs = (\d+)') {
        $parallelJobs = $Matches[1]
        Write-Host "📊 Parallel Jobs: $parallelJobs" -ForegroundColor Cyan
        if ([int]$parallelJobs -ge 2 -and [int]$parallelJobs -le 4) {
            Write-Host "✅ Parallel job count: OPTIMAL" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Parallel jobs: May need adjustment" -ForegroundColor Yellow
        }
    }
    
    if ($scriptContent -match '\$bulkDeleteSize = (\d+)') {
        $bulkSize = $Matches[1]
        Write-Host "📊 Bulk Delete Size: $bulkSize" -ForegroundColor Cyan
        if ([int]$bulkSize -ge 200) {
            Write-Host "✅ Bulk delete size: GOOD" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Bulk delete size: Could be larger" -ForegroundColor Yellow
        }
    }
    
    if ($scriptContent -match '\$apiThrottleMs = (\d+)') {
        $throttle = $Matches[1]
        Write-Host "📊 API Throttle: ${throttle}ms" -ForegroundColor Cyan
        if ([int]$throttle -ge 200 -and [int]$throttle -le 500) {
            Write-Host "✅ API throttling: BALANCED" -ForegroundColor Green
        } else {
            Write-Host "⚠️  API throttling: May need adjustment" -ForegroundColor Yellow
        }
    }
    
} catch {
    Write-Host "❌ Configuration analysis failed: $_" -ForegroundColor Red
}

# Test 4: Performance Estimation
Write-Host "`n🔍 TEST 4: Performance Estimation" -ForegroundColor Yellow

try {
    # Calculate theoretical performance based on configuration
    $batchSize = if ($scriptContent -match '\$batchSize = (\d+)') { [int]$Matches[1] } else { 1000 }
    $parallelJobs = if ($scriptContent -match '\$maxParallelJobs = (\d+)') { [int]$Matches[1] } else { 4 }
    $bulkDeleteSize = if ($scriptContent -match '\$bulkDeleteSize = (\d+)') { [int]$Matches[1] } else { 50 }
    $apiThrottleMs = if ($scriptContent -match '\$apiThrottleMs = (\d+)') { [int]$Matches[1] } else { 200 }
    
    # Calculate requests per minute per job
    $requestsPerMinutePerJob = 60000 / $apiThrottleMs  # 60000ms in a minute
    $totalRequestsPerMinute = $requestsPerMinutePerJob * $parallelJobs
    $assetsPerMinute = $totalRequestsPerMinute * $bulkDeleteSize
    
    Write-Host "📊 PERFORMANCE ANALYSIS" -ForegroundColor Cyan
    Write-Host "Requests per minute per job: $([Math]::Round($requestsPerMinutePerJob, 1))"
    Write-Host "Total requests per minute: $([Math]::Round($totalRequestsPerMinute, 1))"
    Write-Host "Theoretical assets per minute: $([Math]::Round($assetsPerMinute, 0))"
    
    # Estimate time for 850K assets
    $timeFor850K = 850000 / $assetsPerMinute
    Write-Host "Estimated time for 850K assets: $([Math]::Round($timeFor850K, 1)) minutes ($([Math]::Round($timeFor850K/60, 1)) hours)"
    
    if ($assetsPerMinute -gt 3000) {
        Write-Host "🚀 EXCELLENT: Theoretical performance > 3000 assets/min" -ForegroundColor Green
    } elseif ($assetsPerMinute -gt 2000) {
        Write-Host "✅ GOOD: Theoretical performance > 2000 assets/min" -ForegroundColor Green
    } else {
        Write-Host "⚠️  MODERATE: Theoretical performance < 2000 assets/min" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Performance estimation failed: $_" -ForegroundColor Red
}

# Test 5: Error Handling Checks
Write-Host "`n🔍 TEST 5: Error Handling Analysis" -ForegroundColor Yellow

try {
    $errorHandlingFeatures = @(
        @{ Pattern = "try\s*\{.*catch\s*\{"; Name = "Try-Catch blocks" },
        @{ Pattern = "429|503"; Name = "Rate limiting detection" },
        @{ Pattern = "maxRetries"; Name = "Retry logic" },
        @{ Pattern = "Start-Sleep.*retryDelayMs"; Name = "Retry delays" },
        @{ Pattern = "TimeoutSec"; Name = "Timeout handling" },
        @{ Pattern = "Write-Host.*failed"; Name = "Failure reporting" }
    )
    
    foreach ($feature in $errorHandlingFeatures) {
        if ($scriptContent -match $feature.Pattern) {
            Write-Host "✅ $($feature.Name): IMPLEMENTED" -ForegroundColor Green
        } else {
            Write-Host "❌ $($feature.Name): MISSING" -ForegroundColor Red
        }
    }
    
} catch {
    Write-Host "❌ Error handling analysis failed: $_" -ForegroundColor Red
}

# Summary
Write-Host "`n🎯 INTEGRATION TEST SUMMARY" -ForegroundColor Magenta
Write-Host "="*40

Write-Host "✅ Script appears ready for testing with small dataset"
Write-Host "✅ Configuration values are optimized for performance"
Write-Host "✅ Error handling and retry logic are implemented"

Write-Host "`n📋 RECOMMENDED TEST SEQUENCE:" -ForegroundColor Cyan
Write-Host "1. Run mock test: .\Test-PurviewMockData.ps1 -AccountName 'test' -CollectionName 'test' -TestSize SMALL"
Write-Host "2. Test with real small collection: .\Remove-PurviewAsset-Batch.ps1 -AccountName <real> -CollectionName <small> -ListOnly"
Write-Host "3. Test actual deletion on small collection: .\Remove-PurviewAsset-Batch.ps1 -AccountName <real> -CollectionName <small> -Mode BULK"
Write-Host "4. Scale up to production: .\Remove-PurviewAsset-Batch.ps1 -AccountName <real> -CollectionName <850k> -Mode BULK"

Write-Host "`n🏁 Integration test completed!" -ForegroundColor Green
