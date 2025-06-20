Write-Host "To list all entities in the Purview account, use the following command:"
py -m purviewcli entity list | ConvertFrom-Json | Select-Object -ExpandProperty data | Select-Object -ExpandProperty value | Format-Table id, displayText, description, qualifiedName, entityType

Write-Host "To list entities in a specific collection, use the following command:"
py -m purviewcli collections list | ConvertFrom-Json `
| Select-Object -ExpandProperty data `
| Select-Object -ExpandProperty value `
| Select-Object name, friendlyName, description, @{Name = 'parent Collection'; Expression = { $_.parentCollection.referenceName } } `
| Format-Table -AutoSize



# Coller ton JSON brut ici
$raw = py -m purviewcli search query --keywords "HR Data Product"

# Remplacer les éléments Python par JSON standard
$json = $raw -replace "'", '"' `
    -replace '\bTrue\b', 'true' `
    -replace '\bFalse\b', 'false' `
    -replace '\bNone\b', 'null'

# Convertir et afficher sous forme de tableau
($json | ConvertFrom-Json).data.value | Format-Table id, displayText, description, qualifiedName, entityType
