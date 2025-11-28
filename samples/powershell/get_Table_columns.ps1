# # 1. Recherche la table Product
$jsonText = (pvw search find-table --name Product --schema SalesLT --database adventureWorks --json) -split "`n" | ForEach-Object { $_ -replace '^\s*\d+\s+', '' }
$jsonJoined = ($jsonText -join "")
$jsonOutput = $jsonJoined | ConvertFrom-Json

# 2. Prend le GUID de la première table trouvée
$tableGuid = $jsonOutput.value[0].id

# 3. Lit l'entité complète pour obtenir les colonnes
$colText = (pvw entity read --guid $tableGuid --json) -split "`n" | ForEach-Object { $_ -replace '^\s*\d+\s+', '' }
$colJoined = ($colText -join "")
$entity = $colJoined | ConvertFrom-Json

# 4. Liste les colonnes
$columns = $entity.entity.relationshipAttributes.columns

# 5. Affiche ou exporte
$columns | Select-Object guid, name, displayText, description | Format-Table -AutoSize
$columns | Select-Object guid, name, displayText, description | Export-Csv -Path "columns.csv" -NoTypeInformation -Encoding UTF8