# Script final pour récupérer TOUS les assets Fabric
# Utilise le filtre API entityType pour chaque type
# Récupère de toutes les collections en une seule requête par type

Write-Host "`n[INFO] Collecting ALL Fabric assets from ALL collections" -ForegroundColor Cyan
Write-Host "Using optimized API filters (entityType in API request)`n" -ForegroundColor Yellow

# Liste complète des types d'assets Fabric connus
$fabricTypes = @(
    "powerbi_dataset",
    "powerbi_dashboard",
    "powerbi_report",
    "powerbi_tile",
    "powerbi_dataflow",
    "powerbi_workspace",
    "powerbi_capacity",
    "fabric_lakehouse",
    "fabric_lakehouse_table",
    "fabric_warehouse",
    "fabric_warehouse_table",
    "fabric_kql_database",
    "fabric_kql_table",
    "fabric_eventhouse",
    "fabric_notebook",
    "fabric_pipeline",
    "fabric_dataflow_gen2",
    "fabric_ml_model",
    "fabric_ml_experiment",
    "fabric_semantic_model",
    "fabric_environment"
)

$allAssets = @()
$typeStats = @{}
$progressCounter = 0

foreach ($type in $fabricTypes) {
    $progressCounter++
    $percentComplete = [math]::Round(($progressCounter / $fabricTypes.Count) * 100)
    
    Write-Progress -Activity "Collecting Fabric Assets" `
        -Status "Processing $type ($progressCounter/$($fabricTypes.Count))" `
        -PercentComplete $percentComplete
    
    Write-Host "[FETCH] [$progressCounter/$($fabricTypes.Count)] Fetching $type..." -ForegroundColor Blue -NoNewline
    
    try {
        $result = pvw collections resources `
            --asset-type $type `
            --data-source Fabric `
            --json 2>$null
        
        if ($LASTEXITCODE -eq 0 -and $result) {
            $data = $result | ConvertFrom-Json
            $count = $data.total_resources
            
            if ($count -gt 0) {
                Write-Host " [OK] $count assets" -ForegroundColor Green
                $typeStats[$type] = $count
                
                # Ajouter les assets à la collection totale
                foreach ($coll in $data.collections) {
                    foreach ($asset in $coll.assets) {
                        # Ajouter la collection d'origine
                        $asset | Add-Member -NotePropertyName "collection" -NotePropertyValue $coll.name -Force
                        $allAssets += $asset
                    }
                }
                
                # Avertissement si limite atteinte
                if ($count -ge 1000) {
                    Write-Host "    [WARN] API limit reached (1000). More assets may exist." -ForegroundColor Yellow
                }
            } else {
                Write-Host " [SKIP] 0" -ForegroundColor Gray
            }
        } else {
            Write-Host " [ERROR] Error" -ForegroundColor Red
        }
    }
    catch {
        Write-Host " [ERROR] Exception: $_" -ForegroundColor Red
    }
}

Write-Progress -Activity "Collecting Fabric Assets" -Completed

Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "[SUMMARY] SUMMARY BY ASSET TYPE" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

$sortedStats = $typeStats.GetEnumerator() | Sort-Object Value -Descending
foreach ($entry in $sortedStats) {
    $percentage = [math]::Round(($entry.Value / $allAssets.Count) * 100, 1)
    Write-Host ("  {0,-30} : {1,5} ({2,5:N1}%)" -f $entry.Key, $entry.Value, $percentage) -ForegroundColor White
}

Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "[RESULTS] FINAL STATISTICS" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "  Total asset types found  : $($typeStats.Count)" -ForegroundColor White
Write-Host "  Total unique assets      : $($allAssets.Count)" -ForegroundColor White
Write-Host "  Target from portal       : 44,384" -ForegroundColor Yellow
$coverage = [math]::Round($allAssets.Count / 44384 * 100, 2)
$coverageColor = if ($coverage -lt 10) { "Red" } elseif ($coverage -lt 50) { "Yellow" } else { "Green" }
Write-Host "  Coverage                 : $coverage%" -ForegroundColor $coverageColor

# Export des résultats
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outputFile = "fabric_assets_all_$timestamp.json"
$allAssets | ConvertTo-Json -Depth 10 | Out-File $outputFile -Encoding UTF8
Write-Host "`n[SAVED] Results saved to: $outputFile" -ForegroundColor Green

# Export CSV pour analyse Excel
$csvFile = "fabric_assets_all_$timestamp.csv"
$allAssets | Select-Object name, guid, type, data_source, collection | Export-Csv $csvFile -NoTypeInformation -Encoding UTF8
Write-Host "[SAVED] CSV export saved to: $csvFile" -ForegroundColor Green

# Collection breakdown
Write-Host "`n[BREAKDOWN] BREAKDOWN BY COLLECTION:" -ForegroundColor Cyan
$collectionStats = $allAssets | Group-Object collection | Sort-Object Count -Descending
foreach ($collStat in $collectionStats) {
    Write-Host ("  {0,-25} : {1,5} assets" -f $collStat.Name, $collStat.Count) -ForegroundColor White
}

Write-Host "`n[SUCCESS] Collection completed successfully!`n" -ForegroundColor Green
