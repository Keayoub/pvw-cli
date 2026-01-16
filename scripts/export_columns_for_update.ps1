#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Export table columns to CSV for bulk updating in Purview

.DESCRIPTION
    This script extracts all columns from a table entity in Purview and creates a CSV file
    ready for bulk updates. You can then edit the CSV and use it with:
    pvw entity bulk-update-csv --csv-file <output-file>

.PARAMETER TableGuid
    The GUID of the table entity in Purview

.PARAMETER OutputCsv
    Path to the output CSV file (default: columns_to_update.csv)

.PARAMETER IncludeColumns
    Comma-separated list of attributes to include in CSV (default: guid,displayName,description,qualifiedName)

.EXAMPLE
    .\export_columns_for_update.ps1 -TableGuid "abc-123-def-456"
    
.EXAMPLE
    .\export_columns_for_update.ps1 -TableGuid "abc-123-def-456" -OutputCsv "my_columns.csv"

.EXAMPLE
    .\export_columns_for_update.ps1 -TableGuid "abc-123-def-456" -IncludeColumns "guid,displayName,description,owner"
#>

param(
    [Parameter(Mandatory=$true, HelpMessage="GUID of the table entity")]
    [string]$TableGuid,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputCsv = "columns_to_update.csv",
    
    [Parameter(Mandatory=$false)]
    [string]$IncludeColumns = "guid,displayText,displayName,description,qualifiedName"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Export Table Columns for Bulk Update" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Read the table entity
Write-Host "[1/4] Reading table entity: $TableGuid" -ForegroundColor Yellow
$tableJson = pvw entity read --guid $TableGuid --json 2>&1 | Out-String

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to read table entity. Make sure the GUID is correct and you have access." -ForegroundColor Red
    Write-Host $tableJson -ForegroundColor Red
    exit 1
}

# Parse the JSON response
try {
    $response = $tableJson | ConvertFrom-Json
    # Handle wrapped response (entity + referredEntities) vs direct entity
    if ($response.entity) {
        $table = $response.entity
    } else {
        $table = $response
    }
} catch {
    Write-Host "ERROR: Failed to parse table entity JSON response" -ForegroundColor Red
    Write-Host $tableJson
    exit 1
}

Write-Host "  Table: $($table.attributes.name)" -ForegroundColor Green
Write-Host "  Type: $($table.typeName)" -ForegroundColor Green

# Step 2: Extract column relationships
Write-Host ""
Write-Host "[2/4] Extracting column references..." -ForegroundColor Yellow

$columnGuids = @()

# Check for columns in relationshipAttributes
if ($table.relationshipAttributes -and $table.relationshipAttributes.columns) {
    $columnGuids += $table.relationshipAttributes.columns | ForEach-Object { $_.guid }
    Write-Host "  Found $($table.relationshipAttributes.columns.Count) columns in relationshipAttributes" -ForegroundColor Green
}

# Check for columns in attributes (some table types store columns here)
if ($table.attributes -and $table.attributes.columns) {
    $columnGuids += $table.attributes.columns | ForEach-Object { $_.guid }
    Write-Host "  Found $($table.attributes.columns.Count) columns in attributes" -ForegroundColor Green
}

if ($columnGuids.Count -eq 0) {
    Write-Host "  WARNING: No columns found in the table entity." -ForegroundColor Yellow
    Write-Host "  This might be because:" -ForegroundColor Yellow
    Write-Host "    1. The table has no columns" -ForegroundColor Yellow
    Write-Host "    2. The entity type stores columns differently" -ForegroundColor Yellow
    Write-Host "    3. The entity hasn't been fully scanned yet" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Attempting alternative method: searching for columns..." -ForegroundColor Yellow
    
    # Try to get qualifiedName and search for related columns
    if ($table.attributes.qualifiedName) {
        $tableQN = $table.attributes.qualifiedName
        Write-Host "  Searching for columns with qualifiedName pattern: $tableQN" -ForegroundColor Cyan
        
        # Search for columns that belong to this table
        $searchResults = pvw search query --keywords "$tableQN" --json 2>&1 | Out-String
        
        try {
            $results = $searchResults | ConvertFrom-Json
            if ($results.value) {
                $columns = $results.value | Where-Object { $_.entityType -match "column" }
                if ($columns) {
                    Write-Host "  Found $($columns.Count) columns via search" -ForegroundColor Green
                    $columnGuids = $columns | ForEach-Object { $_.id }
                }
            }
        } catch {
            Write-Host "  Search method also failed" -ForegroundColor Yellow
        }
    }
}

if ($columnGuids.Count -eq 0) {
    Write-Host ""
    Write-Host "ERROR: Could not find any columns for this table." -ForegroundColor Red
    Write-Host "Please verify the table GUID and ensure the table has been scanned in Purview." -ForegroundColor Red
    exit 1
}

# Remove duplicates
$columnGuids = $columnGuids | Select-Object -Unique

Write-Host "  Total unique columns: $($columnGuids.Count)" -ForegroundColor Green

# Step 3: Extract column details from referredEntities (already in the response!)
Write-Host ""
Write-Host "[3/4] Extracting column details from referredEntities..." -ForegroundColor Yellow

$columns = @()
$columnAttrs = $IncludeColumns -split ','

# Use referredEntities from the original response (MUCH faster - no additional API calls!)
if ($response.referredEntities) {
    Write-Host "  Using referredEntities from table response (fast path)" -ForegroundColor Green
    
    foreach ($columnGuid in $columnGuids) {
        $column = $response.referredEntities.$columnGuid
        
        if ($column) {
            # Build column object with requested attributes
            $columnObj = [ordered]@{}
            
            foreach ($attr in $columnAttrs) {
                $attr = $attr.Trim()
                if ($attr -eq "guid") {
                    $columnObj[$attr] = $column.guid
                } elseif ($attr -eq "displayText" -and $column.displayText) {
                    $columnObj[$attr] = $column.displayText
                } elseif ($column.attributes.PSObject.Properties.Name -contains $attr) {
                    $columnObj[$attr] = $column.attributes.$attr
                } else {
                    $columnObj[$attr] = ""
                }
            }
            
            $columns += New-Object PSObject -Property $columnObj
        } else {
            Write-Host "    WARNING: Column $columnGuid not found in referredEntities" -ForegroundColor Yellow
        }
    }
} else {
    # Fallback: fetch columns individually (slower but more compatible)
    Write-Host "  No referredEntities found, fetching columns individually..." -ForegroundColor Yellow
    
    foreach ($columnGuid in $columnGuids) {
        Write-Host "  Processing column: $columnGuid" -ForegroundColor Gray
        
        $columnJson = pvw entity read --guid $columnGuid --json 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            try {
                $columnResponse = $columnJson | ConvertFrom-Json
                # Handle wrapped response
                if ($columnResponse.entity) {
                    $column = $columnResponse.entity
                } else {
                    $column = $columnResponse
                }
                
                # Build column object with requested attributes
                $columnObj = [ordered]@{}
                
                foreach ($attr in $columnAttrs) {
                    $attr = $attr.Trim()
                    if ($attr -eq "guid") {
                        $columnObj[$attr] = $column.guid
                    } elseif ($attr -eq "displayText" -and $column.displayText) {
                        $columnObj[$attr] = $column.displayText
                    } elseif ($column.attributes.PSObject.Properties.Name -contains $attr) {
                        $columnObj[$attr] = $column.attributes.$attr
                    } else {
                        $columnObj[$attr] = ""
                    }
                }
                
                $columns += New-Object PSObject -Property $columnObj
            } catch {
                Write-Host "    WARNING: Failed to parse column $columnGuid" -ForegroundColor Yellow
            }
        } else {
            Write-Host "    WARNING: Failed to read column $columnGuid" -ForegroundColor Yellow
        }
    }
}

Write-Host "  Successfully extracted $($columns.Count) column details" -ForegroundColor Green

# Step 4: Export to CSV
Write-Host ""
Write-Host "[4/4] Exporting to CSV..." -ForegroundColor Yellow

if ($columns.Count -eq 0) {
    Write-Host "ERROR: No columns to export" -ForegroundColor Red
    exit 1
}

$columns | Export-Csv -Path $OutputCsv -NoTypeInformation -Encoding UTF8

Write-Host "  CSV file created: $OutputCsv" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUCCESS! Columns exported successfully" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Open and edit: $OutputCsv" -ForegroundColor White
Write-Host "  2. Update the displayName, description, or other attributes" -ForegroundColor White
Write-Host "  3. Run: pvw entity bulk-update-csv --csv-file $OutputCsv --dry-run" -ForegroundColor White
Write-Host "  4. If dry-run looks good, run without --dry-run to apply changes" -ForegroundColor White
Write-Host ""
Write-Host "Example preview of CSV:" -ForegroundColor Cyan
Get-Content $OutputCsv -TotalCount 5 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
Write-Host ""
