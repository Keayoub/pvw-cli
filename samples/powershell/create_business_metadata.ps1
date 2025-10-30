# Create Business Metadata Groups - Example Script
# This script demonstrates how to create multiple business metadata groups

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Business Metadata Creation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# List of templates to create
$templates = @(
    @{
        Name = "Governance (Business Concepts)"
        File = "templates/business_metadata_governance.json"
        Scope = "Business Concept"
        Description = "Governance metadata for terms and domains"
    },
    @{
        Name = "DataQuality (Data Assets)"
        File = "templates/business_metadata_quality.json"
        Scope = "Data Asset"
        Description = "Quality metrics for tables and files"
    },
    @{
        Name = "Privacy (Business Concepts)"
        File = "templates/business_metadata_privacy.json"
        Scope = "Business Concept"
        Description = "Privacy classification for terms"
    },
    @{
        Name = "Documentation (Universal)"
        File = "templates/business_metadata_universal.json"
        Scope = "Universal"
        Description = "Documentation links for all entities"
    }
)

# Display what will be created
Write-Host "The following Business Metadata groups will be created:" -ForegroundColor Yellow
Write-Host ""
foreach ($template in $templates) {
    Write-Host "  [*] $($template.Name)" -ForegroundColor White
    Write-Host "      File: $($template.File)" -ForegroundColor Gray
    Write-Host "      Scope: $($template.Scope)" -ForegroundColor Gray
    Write-Host "      Description: $($template.Description)" -ForegroundColor Gray
    Write-Host ""
}

# Ask for confirmation
$response = Read-Host "Do you want to proceed? (Y/N)"
if ($response -ne 'Y' -and $response -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Creating metadata groups..." -ForegroundColor Green
Write-Host ""

# Create each metadata group
$successCount = 0
$errorCount = 0

foreach ($template in $templates) {
    Write-Host "[INFO] Creating: $($template.Name)..." -ForegroundColor Cyan
    
    try {
        # First validate with dry-run
        Write-Host "       Validating JSON..." -ForegroundColor Gray
        py -m purviewcli types create-business-metadata-def --payload-file $template.File --dry-run --validate 2>&1 | Out-Null
        
        # Create the metadata
        $result = py -m purviewcli types create-business-metadata-def --payload-file $template.File 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] Created: $($template.Name)" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "[FAILED] Error creating: $($template.Name)" -ForegroundColor Red
            Write-Host "         $result" -ForegroundColor Red
            $errorCount++
        }
    }
    catch {
        Write-Host "[FAILED] Exception: $_" -ForegroundColor Red
        $errorCount++
    }
    
    # Small delay to avoid rate limiting
    Start-Sleep -Seconds 1
    Write-Host ""
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUCCESS: $successCount groups created" -ForegroundColor Green
Write-Host "FAILED: $errorCount groups failed" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Gray" })
Write-Host ""

# Verify creation
Write-Host "Verifying created groups..." -ForegroundColor Yellow
Write-Host ""
py -m purviewcli types list-business-metadata-groups

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "1. View all attributes:" -ForegroundColor White
Write-Host "   py -m purviewcli types list-business-attributes" -ForegroundColor Gray
Write-Host ""
Write-Host "2. View specific group details:" -ForegroundColor White
Write-Host "   py -m purviewcli types read-business-metadata-def --name Governance" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Apply metadata to entities:" -ForegroundColor White
Write-Host "   Use Purview UI or entity update commands" -ForegroundColor Gray
Write-Host ""
