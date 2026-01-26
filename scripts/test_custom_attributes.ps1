# Test script to create custom attributes with different data types

Write-Host "=== Testing Custom Attributes Creation ===" -ForegroundColor Cyan

$types = @(
    @{ name = "TestAttributeString"; dataType = "string"; desc = "Test string attribute" },
    @{ name = "TestAttributeNumber"; dataType = "number"; desc = "Test numeric attribute (integer/decimal)" },
    @{ name = "TestAttributeBoolean"; dataType = "boolean"; desc = "Test boolean attribute (true/false)" },
    @{ name = "TestAttributeDate"; dataType = "date"; desc = "Test date attribute (ISO 8601 format)" }
)

$results = @()

foreach ($type in $types) {
    Write-Host "`nCreating: $($type.name) [Type: $($type.dataType)]" -ForegroundColor Yellow
    
    try {
        $output = & pvw uc attribute create `
            --name $type.name `
            --data-type $type.dataType `
            --description $type.desc 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK] Created successfully" -ForegroundColor Green
            $results += @{
                name = $type.name
                type = $type.dataType
                status = "SUCCESS"
                output = $output
            }
        } else {
            Write-Host "  [ERROR] Failed with exit code $LASTEXITCODE" -ForegroundColor Red
            Write-Host "  Output: $output"
            $results += @{
                name = $type.name
                type = $type.dataType
                status = "FAILED"
                output = $output
            }
        }
    } catch {
        Write-Host "  [ERROR] Exception: $_" -ForegroundColor Red
        $results += @{
            name = $type.name
            type = $type.dataType
            status = "FAILED"
            output = $_
        }
    }
}

# List all created attributes
Write-Host "`n=== Listing All Custom Attributes ===" -ForegroundColor Cyan
& pvw uc attribute list

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
$successful = @($results | Where-Object { $_.status -eq "SUCCESS" }).Count
$failed = @($results | Where-Object { $_.status -eq "FAILED" }).Count

Write-Host "Total: $($results.Count)"
Write-Host "Successful: $successful" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red

if ($failed -gt 0) {
    Write-Host "`nFailed Attributes:" -ForegroundColor Yellow
    $results | Where-Object { $_.status -eq "FAILED" } | ForEach-Object {
        Write-Host "  - $($_.name) [$($_.type)]"
        Write-Host "    Output: $($_.output)"
    }
}
