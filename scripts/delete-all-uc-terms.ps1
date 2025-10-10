<#
.SYNOPSIS
    Delete all Unified Catalog terms in a domain
    
.DESCRIPTION
    Fetches all terms from a specified domain and deletes them one by one.
    Provides detailed progress and summary information.
    
.PARAMETER DomainId
    The governance domain ID to delete terms from
    
.PARAMETER Force
    Skip confirmation prompt and delete immediately
    
.EXAMPLE
    .\delete-all-uc-terms.ps1 -DomainId "59ae27b5-40bc-4c90-abfe-fe1a0638fe3a"
    
.EXAMPLE
    .\delete-all-uc-terms.ps1 -DomainId "59ae27b5-40bc-4c90-abfe-fe1a0638fe3a" -Force
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$DomainId,
    
    [Parameter(Mandatory=$false)]
    [switch]$Force
)

Write-Host  "`n╔════════════════════════════════════════════════════════════════╗"   -ForegroundColor Cyan
Write-Host  "║          Unified Catalog - Bulk Term Deletion                  ║"     -ForegroundColor Cyan
Write-Host  "╚════════════════════════════════════════════════════════════════╝`n"   -ForegroundColor Cyan

Write-Host "[*] Fetching terms from domain: " -NoNewline -ForegroundColor Yellow
Write-Host $DomainId -ForegroundColor White

# Fetch all terms using the new --output json flag
try {
    $terms = py -m purviewcli uc term list --domain-id $DomainId --output json | ConvertFrom-Json
    
    if (-not $terms) {
        Write-Host "`n[!] No terms found in this domain." -ForegroundColor Yellow
        exit 0
    }
    
    $termCount = $terms.Count
    Write-Host "[OK] Found " -NoNewline -ForegroundColor Green
    Write-Host $termCount -NoNewline -ForegroundColor White
    Write-Host " term(s)`n" -ForegroundColor Green
    
} catch {
    Write-Host "`n❌ Error fetching terms: $_" -ForegroundColor Red
    exit 1
}

# Display terms in a table
Write-Host "Terms to be deleted:" -ForegroundColor Yellow
$terms | Select-Object -Property `
    @{Label="Name"; Expression={$_.name}},
    @{Label="Status"; Expression={$_.status}},
    @{Label="ID"; Expression={$_.id.Substring(0,20) + "..."}} | 
    Format-Table -AutoSize

# Confirmation
if (-not $Force) {
    Write-Host "[!] WARNING: This will permanently delete all $termCount terms!" -ForegroundColor Red
    $confirmation = Read-Host "`nType 'DELETE' to confirm (or anything else to cancel)"
    
    if ($confirmation -ne "DELETE") {
        Write-Host "`n[X] Operation cancelled by user." -ForegroundColor Yellow
        exit 0
    }
}

# Delete terms
Write-Host "`n[*] Starting deletion...`n" -ForegroundColor Cyan

$successCount = 0
$failedCount = 0
$failedTerms = @()

$counter = 0
foreach ($term in $terms) {
    $counter++
    $termId = $term.id
    $termName = $term.name
    
    # Progress indicator
    $progress = [math]::Round(($counter / $termCount) * 100, 0)
    Write-Host "[$counter/$termCount] " -NoNewline -ForegroundColor Cyan
    Write-Host "$termName " -NoNewline -ForegroundColor White
    Write-Host "($progress%) " -NoNewline -ForegroundColor DarkGray
    
    try {
        # Delete the term (suppress output to avoid encoding issues)
        $output = py -m purviewcli uc term delete --term-id $termId --force 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK]" -ForegroundColor Green
            $successCount++
        } else {
            Write-Host "[FAILED]" -ForegroundColor Red
            $failedCount++
            $failedTerms += [PSCustomObject]@{
                Name = $termName
                ID = $termId
                Error = $output.Trim()
            }
        }
    } catch {
        Write-Host "[ERROR]" -ForegroundColor Red
        $failedCount++
        $failedTerms += [PSCustomObject]@{
            Name = $termName
            ID = $termId
            Error = $_.Exception.Message
        }
    }
    
    # Small delay to avoid rate limiting
    Start-Sleep -Milliseconds 200
}

# Summary
Write-Host "`n" + ("="*70) -ForegroundColor Cyan
Write-Host "DELETION SUMMARY" -ForegroundColor Cyan
Write-Host ("="*70) -ForegroundColor Cyan

Write-Host "`n  Total terms:           " -NoNewline -ForegroundColor White
Write-Host $termCount -ForegroundColor Cyan

Write-Host "  [OK] Successfully deleted: " -NoNewline -ForegroundColor Green
Write-Host $successCount -ForegroundColor White

Write-Host "  [X]  Failed:               " -NoNewline -ForegroundColor Red
Write-Host $failedCount -ForegroundColor White

# Show failed terms if any
if ($failedCount -gt 0) {
    Write-Host "`n[!] Failed Terms:" -ForegroundColor Red
    $failedTerms | Format-Table -Property Name, ID, Error -AutoSize
}

# Final status
Write-Host ""
if ($failedCount -eq 0) {
    Write-Host "[SUCCESS] All terms deleted successfully!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Deletion completed with $failedCount error(s)" -ForegroundColor Yellow
}

Write-Host ""
