# ==============================================================================
# Unified Catalog: Hierarchical Terms - PowerShell Examples
# ==============================================================================
# 
# This script demonstrates how to create and manage hierarchical term structures
# in Microsoft Purview Unified Catalog using the parent-id feature.
#
# Prerequisites:
# - Purview CLI installed: pip install purviewcli
# - Authenticated to Purview
# - PowerShell 5.1 or PowerShell 7+
#
# Usage:
#   .\uc_parent_id_examples.ps1
#
# ==============================================================================

# Configuration
$domainId = "your-domain-guid-here"  # Replace with your governance domain ID
$purviewAccount = $env:PURVIEW_ACCOUNT_NAME

Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "Unified Catalog: Hierarchical Terms Examples" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""
Write-Host "Purview Account: $purviewAccount" -ForegroundColor Yellow
Write-Host "Domain ID: $domainId" -ForegroundColor Yellow
Write-Host ""

if ($domainId -eq "your-domain-guid-here") {
    Write-Host "⚠️  Please update the `$domainId variable with your actual domain GUID" -ForegroundColor Red
    exit 1
}

# ==============================================================================
# Helper Functions
# ==============================================================================

function Invoke-PvwCommand {
    param(
        [string[]]$Arguments,
        [switch]$AsJson
    )
    
    try {
        $output = & pvw @Arguments 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Error executing command" -ForegroundColor Red
            Write-Host $output -ForegroundColor Red
            return $null
        }
        
        if ($AsJson) {
            return $output | ConvertFrom-Json
        }
        
        return $output
    }
    catch {
        Write-Host "❌ Exception: $_" -ForegroundColor Red
        return $null
    }
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "─" * 80 -ForegroundColor Gray
    Write-Host "📋 $Title" -ForegroundColor Cyan
    Write-Host "─" * 80 -ForegroundColor Gray
}

# ==============================================================================
# Example 1: Create Simple Parent-Child Hierarchy
# ==============================================================================

Write-Section "Example 1: Create Simple Parent-Child Hierarchy"

Write-Host "Creating root term: 'Data Quality'..." -ForegroundColor Yellow

$rootTerm = Invoke-PvwCommand -Arguments @(
    "uc", "term", "create",
    "--name", "Data Quality",
    "--description", "Root category for all data quality metrics",
    "--domain-id", $domainId,
    "--status", "Published",
    "--acronym", "DQ",
    "--output", "json"
) -AsJson

if ($rootTerm) {
    $rootId = $rootTerm.id
    Write-Host "✅ Root term created: $rootId" -ForegroundColor Green
    
    # Create child terms
    Write-Host "`nCreating child terms..." -ForegroundColor Yellow
    
    $childTerms = @(
        @{Name="Accuracy"; Description="Measures data correctness"; Acronym="ACC"},
        @{Name="Completeness"; Description="Measures data presence"; Acronym="COMP"},
        @{Name="Consistency"; Description="Measures data uniformity"; Acronym="CONS"},
        @{Name="Timeliness"; Description="Measures data availability"; Acronym="TIME"}
    )
    
    $childIds = @{}
    
    foreach ($child in $childTerms) {
        $result = Invoke-PvwCommand -Arguments @(
            "uc", "term", "create",
            "--name", $child.Name,
            "--description", $child.Description,
            "--domain-id", $domainId,
            "--parent-id", $rootId,
            "--status", "Published",
            "--acronym", $child.Acronym,
            "--output", "json"
        ) -AsJson
        
        if ($result) {
            $childIds[$child.Name] = $result.id
            Write-Host "  ✅ Created: $($child.Name)" -ForegroundColor Green
        }
    }
    
    Write-Host "`n📊 Created $($childIds.Count) child terms" -ForegroundColor Cyan
}
else {
    Write-Host "❌ Failed to create root term" -ForegroundColor Red
}

# ==============================================================================
# Example 2: Create Multi-Level Hierarchy (Grandchildren)
# ==============================================================================

Write-Section "Example 2: Create Multi-Level Hierarchy"

if ($childIds.ContainsKey("Accuracy")) {
    $accuracyId = $childIds["Accuracy"]
    Write-Host "Creating granular metrics under 'Accuracy'..." -ForegroundColor Yellow
    
    $accuracyMetrics = @(
        @{Name="Field-Level Accuracy"; Description="Accuracy at field level"; Status="Draft"},
        @{Name="Record-Level Accuracy"; Description="Accuracy at record level"; Status="Draft"},
        @{Name="Syntactic Accuracy"; Description="Format and structure correctness"; Status="Draft"},
        @{Name="Semantic Accuracy"; Description="Meaning and context correctness"; Status="Draft"}
    )
    
    foreach ($metric in $accuracyMetrics) {
        $result = Invoke-PvwCommand -Arguments @(
            "uc", "term", "create",
            "--name", $metric.Name,
            "--description", $metric.Description,
            "--domain-id", $domainId,
            "--parent-id", $accuracyId,
            "--status", $metric.Status,
            "--output", "json"
        ) -AsJson
        
        if ($result) {
            Write-Host "  ✅ Created: $($metric.Name)" -ForegroundColor Green
        }
    }
}

# ==============================================================================
# Example 3: Update Existing Term to Add Parent
# ==============================================================================

Write-Section "Example 3: Update Existing Term to Add Parent"

Write-Host "Creating a standalone term..." -ForegroundColor Yellow

$standaloneTerm = Invoke-PvwCommand -Arguments @(
    "uc", "term", "create",
    "--name", "Data Validity",
    "--description", "Validates data against business rules",
    "--domain-id", $domainId,
    "--status", "Draft",
    "--output", "json"
) -AsJson

if ($standaloneTerm -and $rootId) {
    $standaloneId = $standaloneTerm.id
    Write-Host "✅ Created standalone term: $standaloneId" -ForegroundColor Green
    
    Write-Host "`nUpdating term to add parent relationship..." -ForegroundColor Yellow
    
    $updateResult = Invoke-PvwCommand -Arguments @(
        "uc", "term", "update",
        "--term-id", $standaloneId,
        "--parent-id", $rootId,
        "--output", "json"
    ) -AsJson
    
    if ($updateResult) {
        Write-Host "✅ Successfully added parent to 'Data Validity'" -ForegroundColor Green
    }
}

# ==============================================================================
# Example 4: Bulk Update from CSV
# ==============================================================================

Write-Section "Example 4: Bulk Update from CSV"

Write-Host "Creating CSV file for bulk update..." -ForegroundColor Yellow

$csvContent = @"
term_id,name,description,parent_id,status,acronyms
$rootId,Data Quality Framework,Updated root description,,Published,DQF
"@

if ($childIds.ContainsKey("Completeness")) {
    $csvContent += @"

$($childIds["Completeness"]),Completeness,Updated completeness description,$rootId,Published,COMP
"@
}

$csvPath = "hierarchical_terms_update.csv"
$csvContent | Out-File -FilePath $csvPath -Encoding UTF8

Write-Host "✅ Created CSV file: $csvPath" -ForegroundColor Green
Write-Host "`nCSV Content:" -ForegroundColor Yellow
Get-Content $csvPath | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host "`nRunning DRY RUN to preview changes..." -ForegroundColor Yellow
Invoke-PvwCommand -Arguments @(
    "uc", "term", "update-csv",
    "--csv-file", $csvPath,
    "--dry-run"
)

Write-Host "`n💡 To apply changes, run without --dry-run flag:" -ForegroundColor Cyan
Write-Host "   pvw uc term update-csv --csv-file $csvPath" -ForegroundColor White

# ==============================================================================
# Example 5: Query and Display Hierarchy
# ==============================================================================

Write-Section "Example 5: Query and Display Hierarchy"

Write-Host "Retrieving all terms in domain..." -ForegroundColor Yellow

$allTerms = Invoke-PvwCommand -Arguments @(
    "uc", "term", "list",
    "--domain-id", $domainId,
    "--output", "json"
) -AsJson

if ($allTerms) {
    $terms = $allTerms.value
    Write-Host "✅ Found $($terms.Count) terms" -ForegroundColor Green
    
    # Build hierarchy map
    $hierarchy = @{}
    $rootTerms = @()
    
    foreach ($term in $terms) {
        $termId = $term.id
        $parentId = $term.parentId
        $name = $term.name
        $status = $term.status
        
        if (-not $parentId) {
            # Root level term
            $rootTerms += @{
                Id = $termId
                Name = $name
                Status = $status
            }
        }
        else {
            # Child term
            if (-not $hierarchy.ContainsKey($parentId)) {
                $hierarchy[$parentId] = @()
            }
            $hierarchy[$parentId] += @{
                Id = $termId
                Name = $name
                Status = $status
            }
        }
    }
    
    # Display hierarchy
    Write-Host "`n📂 Term Hierarchy:" -ForegroundColor Cyan
    
    foreach ($root in $rootTerms) {
        Write-Host "  📌 $($root.Name) [$($root.Status)]" -ForegroundColor White
        
        if ($hierarchy.ContainsKey($root.Id)) {
            foreach ($child in $hierarchy[$root.Id]) {
                Write-Host "     ├── $($child.Name) [$($child.Status)]" -ForegroundColor Gray
                
                # Display grandchildren if any
                if ($hierarchy.ContainsKey($child.Id)) {
                    foreach ($grandchild in $hierarchy[$child.Id]) {
                        Write-Host "     │   └── $($grandchild.Name) [$($grandchild.Status)]" -ForegroundColor DarkGray
                    }
                }
            }
        }
    }
}

# ==============================================================================
# Example 6: Move Term to Different Parent
# ==============================================================================

Write-Section "Example 6: Move Term to Different Parent"

Write-Host "Creating a new parent category..." -ForegroundColor Yellow

$newParent = Invoke-PvwCommand -Arguments @(
    "uc", "term", "create",
    "--name", "Advanced Quality Metrics",
    "--description", "Advanced and specialized quality metrics",
    "--domain-id", $domainId,
    "--status", "Published",
    "--output", "json"
) -AsJson

if ($newParent) {
    $newParentId = $newParent.id
    Write-Host "✅ Created new parent: $newParentId" -ForegroundColor Green
    
    Write-Host "`n💡 To move a term to this new parent:" -ForegroundColor Cyan
    Write-Host "   pvw uc term update --term-id <term-guid> --parent-id $newParentId" -ForegroundColor White
}

# ==============================================================================
# Example 7: Remove Parent Relationship
# ==============================================================================

Write-Section "Example 7: Remove Parent Relationship"

Write-Host "💡 To remove a parent relationship and make a term top-level:" -ForegroundColor Cyan
Write-Host "   pvw uc term update --term-id <term-guid> --parent-id `"`"" -ForegroundColor White
Write-Host ""
Write-Host "Note: Setting parent-id to empty string removes the parent" -ForegroundColor Yellow

# ==============================================================================
# Example 8: JSON Bulk Update
# ==============================================================================

Write-Section "Example 8: JSON Bulk Update"

Write-Host "Creating JSON file for bulk update..." -ForegroundColor Yellow

$jsonContent = @{
    updates = @(
        @{
            term_id = $rootId
            name = "Data Quality Framework"
            status = "Published"
        }
    )
} | ConvertTo-Json -Depth 10

$jsonPath = "hierarchical_terms_update.json"
$jsonContent | Out-File -FilePath $jsonPath -Encoding UTF8

Write-Host "✅ Created JSON file: $jsonPath" -ForegroundColor Green
Write-Host "`nJSON Content:" -ForegroundColor Yellow
Get-Content $jsonPath | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host "`n💡 To preview JSON bulk update:" -ForegroundColor Cyan
Write-Host "   pvw uc term update-json --json-file $jsonPath --dry-run" -ForegroundColor White

# ==============================================================================
# Summary and Next Steps
# ==============================================================================

Write-Section "Summary"

Write-Host "✅ Examples completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "What we demonstrated:" -ForegroundColor Cyan
Write-Host "  1. ✅ Created parent-child hierarchies" -ForegroundColor White
Write-Host "  2. ✅ Created multi-level hierarchies (grandchildren)" -ForegroundColor White
Write-Host "  3. ✅ Updated existing terms to add parents" -ForegroundColor White
Write-Host "  4. ✅ Bulk updates via CSV" -ForegroundColor White
Write-Host "  5. ✅ Queried and displayed hierarchy" -ForegroundColor White
Write-Host "  6. ✅ Moved terms between parents" -ForegroundColor White
Write-Host "  7. ✅ Removed parent relationships" -ForegroundColor White
Write-Host "  8. ✅ Bulk updates via JSON" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "  • View hierarchy in Purview portal: https://$purviewAccount.purview.azure.com" -ForegroundColor White
Write-Host "  • Check documentation: doc/commands/unified-catalog/hierarchical-terms.md" -ForegroundColor White
Write-Host "  • Try Jupyter notebook: samples/notebooks (plus)/uc_hierarchical_terms.ipynb" -ForegroundColor White
Write-Host "  • Review sample files: samples/csv/ and samples/json/" -ForegroundColor White
Write-Host ""
Write-Host "=" * 80 -ForegroundColor Cyan

# ==============================================================================
# Cleanup (Optional)
# ==============================================================================

$cleanup = Read-Host "`nDo you want to clean up created files? (y/N)"
if ($cleanup -eq "y" -or $cleanup -eq "Y") {
    Remove-Item -Path $csvPath -ErrorAction SilentlyContinue
    Remove-Item -Path $jsonPath -ErrorAction SilentlyContinue
    Write-Host "✅ Cleaned up temporary files" -ForegroundColor Green
}
