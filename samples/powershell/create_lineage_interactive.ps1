# Create Lineage Between Purview Entities
# This script helps you create lineage relationships between existing entities in Microsoft Purview

Write-Host "`n=== Microsoft Purview Lineage Creator ===" -ForegroundColor Cyan
Write-Host "This script will help you create a lineage relationship between two entities`n" -ForegroundColor Gray

# Step 1: List available SQL tables
Write-Host "[STEP 1] Fetching SQL tables..." -ForegroundColor Yellow
$sqlTables = py -m purviewcli entity list --type-name "azure_sql_table" --limit 50 | ConvertFrom-Json

if ($sqlTables.value.Count -eq 0) {
    Write-Host "ERROR: No SQL tables found in Purview" -ForegroundColor Red
    exit 1
}

Write-Host "`nAvailable SQL Tables ($($sqlTables.'@search.count') found):" -ForegroundColor Green
for ($i = 0; $i -lt $sqlTables.value.Count; $i++) {
    $table = $sqlTables.value[$i]
    Write-Host "  [$($i+1)] $($table.displayText) - $($table.qualifiedName)" -ForegroundColor White
    Write-Host "      GUID: $($table.id)" -ForegroundColor Gray
}

# Step 2: Select source table
Write-Host "`n[STEP 2] Select a SOURCE table (enter number):" -ForegroundColor Yellow
$sourceIndex = Read-Host "Choice"
if ([int]$sourceIndex -lt 1 -or [int]$sourceIndex -gt $sqlTables.value.Count) {
    Write-Host "ERROR: Invalid choice" -ForegroundColor Red
    exit 1
}
$sourceEntity = $sqlTables.value[[int]$sourceIndex - 1]
Write-Host "Selected: $($sourceEntity.displayText) [$($sourceEntity.id)]" -ForegroundColor Green

# Step 3: List available datasets
Write-Host "`n[STEP 3] Fetching datasets..." -ForegroundColor Yellow
$datasets = py -m purviewcli entity list --type-name "DataSet" --limit 50 | ConvertFrom-Json

if ($datasets.value.Count -eq 0) {
    Write-Host "WARNING: No DataSets found. You can also use another SQL table as target." -ForegroundColor Yellow
}

Write-Host "`nAvailable DataSets ($($datasets.'@search.count') found):" -ForegroundColor Green
for ($i = 0; $i -lt $datasets.value.Count; $i++) {
    $ds = $datasets.value[$i]
    Write-Host "  [$($i+1)] $($ds.displayText) - $($ds.qualifiedName)" -ForegroundColor White
    Write-Host "      GUID: $($ds.id)" -ForegroundColor Gray
}

# Option to use another SQL table
Write-Host "  [$($datasets.value.Count + 1)] Use another SQL table as target" -ForegroundColor Cyan

# Step 4: Select target
Write-Host "`n[STEP 4] Select a TARGET entity (enter number):" -ForegroundColor Yellow
$targetIndex = Read-Host "Choice"

if ([int]$targetIndex -eq $datasets.value.Count + 1) {
    # Use another SQL table
    Write-Host "`nSelect target SQL table:" -ForegroundColor Yellow
    for ($i = 0; $i -lt $sqlTables.value.Count; $i++) {
        $table = $sqlTables.value[$i]
        Write-Host "  [$($i+1)] $($table.displayText)" -ForegroundColor White
    }
    $targetTableIndex = Read-Host "Choice"
    $targetEntity = $sqlTables.value[[int]$targetTableIndex - 1]
} else {
    if ([int]$targetIndex -lt 1 -or [int]$targetIndex -gt $datasets.value.Count) {
        Write-Host "ERROR: Invalid choice" -ForegroundColor Red
        exit 1
    }
    $targetEntity = $datasets.value[[int]$targetIndex - 1]
}

Write-Host "Selected: $($targetEntity.displayText) [$($targetEntity.id)]" -ForegroundColor Green

# Step 5: Create lineage JSON
Write-Host "`n[STEP 5] Creating lineage definition..." -ForegroundColor Yellow

$processName = "ETL_$($sourceEntity.name)_to_$($targetEntity.name)"
$qualifiedName = "$($processName.ToLower().Replace(' ', '_'))@kaydemopurview"

$lineageJson = @{
    entity = @{
        typeName = "Process"
        attributes = @{
            qualifiedName = $qualifiedName
            name = "ETL: $($sourceEntity.displayText) to $($targetEntity.displayText)"
            description = "Data lineage from $($sourceEntity.displayText) to $($targetEntity.displayText)"
            inputs = @(
                @{
                    guid = $sourceEntity.id
                    typeName = $sourceEntity.entityType
                }
            )
            outputs = @(
                @{
                    guid = $targetEntity.id
                    typeName = $targetEntity.entityType
                }
            )
        }
    }
    referredEntities = @{}
} | ConvertTo-Json -Depth 10

# Save to temp file
$tempFile = "temp_lineage.json"
$lineageJson | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "Lineage definition created:" -ForegroundColor Green
Write-Host $lineageJson -ForegroundColor Gray

# Step 6: Confirmation
Write-Host "`n[STEP 6] Ready to create lineage:" -ForegroundColor Yellow
Write-Host "  Source: $($sourceEntity.displayText)" -ForegroundColor White
Write-Host "  Target: $($targetEntity.displayText)" -ForegroundColor White
Write-Host "  Process: $processName" -ForegroundColor White

$confirm = Read-Host "`nProceed with creation? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Operation cancelled" -ForegroundColor Yellow
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    exit 0
}

# Step 7: Create lineage
Write-Host "`n[STEP 7] Creating lineage in Purview..." -ForegroundColor Yellow
$result = py -m purviewcli entity create --payload-file $tempFile 2>&1

Write-Host "`nResult:" -ForegroundColor Cyan
Write-Host $result

# Cleanup
Remove-Item $tempFile -ErrorAction SilentlyContinue

Write-Host "`n=== Lineage Creation Complete ===" -ForegroundColor Green
Write-Host "Tip: View this lineage in the Purview UI by navigating to either entity" -ForegroundColor Gray
