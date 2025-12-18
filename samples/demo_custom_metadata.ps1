# Script de démonstration - Gestion des métadonnées personnalisées
# Ce script montre comment utiliser bulk-update-csv avec différents types de métadonnées

Write-Host "=== Démonstration: Gestion des Métadonnées Personnalisées ===" -ForegroundColor Cyan
Write-Host ""

# Répertoire des exemples
$samplesDir = "samples\csv"

# ============================================
# Exemple 1: Attributs personnalisés simples
# ============================================
Write-Host "Exemple 1: Attributs personnalisés simples" -ForegroundColor Yellow
Write-Host "Fichier: $samplesDir\simple_custom_attrs.csv" -ForegroundColor Gray
Write-Host ""
Write-Host "Contenu du CSV:" -ForegroundColor Gray
Get-Content "$samplesDir\simple_custom_attrs.csv" | Select-Object -First 3
Write-Host ""
Write-Host "Commande:" -ForegroundColor Green
Write-Host "  pvw entity bulk-update-csv --csv-file $samplesDir\simple_custom_attrs.csv --dry-run --debug" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur une touche pour exécuter (mode dry-run)..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

python -m purviewcli entity bulk-update-csv --csv-file "$samplesDir\simple_custom_attrs.csv" --dry-run --debug

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Gray
Write-Host ""

# ============================================
# Exemple 2: Business Metadata complet
# ============================================
Write-Host "Exemple 2: Business Metadata avec attributs imbriqués" -ForegroundColor Yellow
Write-Host "Fichier: $samplesDir\example_custom_metadata.csv" -ForegroundColor Gray
Write-Host ""
Write-Host "Contenu du CSV:" -ForegroundColor Gray
Get-Content "$samplesDir\example_custom_metadata.csv" | Select-Object -First 3
Write-Host ""
Write-Host "Ce CSV contient:" -ForegroundColor Gray
Write-Host "  - Business Metadata: department, costCenter, owner, dataClassification" -ForegroundColor White
Write-Host "  - Custom Attributes: sourceSystem, refreshFrequency, lastRefreshDate" -ForegroundColor White
Write-Host ""
Write-Host "Commande:" -ForegroundColor Green
Write-Host "  pvw entity bulk-update-csv --csv-file $samplesDir\example_custom_metadata.csv --dry-run --debug" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur une touche pour exécuter (mode dry-run)..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

python -m purviewcli entity bulk-update-csv --csv-file "$samplesDir\example_custom_metadata.csv" --dry-run --debug

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Gray
Write-Host ""

# ============================================
# Exemple 3: Test custom attributes du projet
# ============================================
Write-Host "Exemple 3: Mix d'attributs personnalisés et business metadata" -ForegroundColor Yellow
Write-Host "Fichier: $samplesDir\test_bulk_update_custom_attrs.csv" -ForegroundColor Gray
Write-Host ""
Write-Host "Contenu du CSV:" -ForegroundColor Gray
Get-Content "$samplesDir\test_bulk_update_custom_attrs.csv"
Write-Host ""
Write-Host "Commande:" -ForegroundColor Green
Write-Host "  pvw entity bulk-update-csv --csv-file $samplesDir\test_bulk_update_custom_attrs.csv --dry-run --debug" -ForegroundColor White
Write-Host ""
Write-Host "Appuyez sur une touche pour exécuter (mode dry-run)..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
Write-Host ""

python -m purviewcli entity bulk-update-csv --csv-file "$samplesDir\test_bulk_update_custom_attrs.csv" --dry-run --debug

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Gray
Write-Host ""

# ============================================
# Résumé
# ============================================
Write-Host "=== Résumé des capacités ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Attributs simples:" -ForegroundColor Yellow
Write-Host "   guid,displayName,myCustomField" -ForegroundColor White
Write-Host "   → attributes: { displayName, myCustomField }" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Business Metadata (notation pointée):" -ForegroundColor Yellow
Write-Host "   guid,businessMetadata.department,businessMetadata.owner" -ForegroundColor White
Write-Host "   → attributes: { businessMetadata: { department, owner } }" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Custom Attributes (section dédiée):" -ForegroundColor Yellow
Write-Host "   guid,customAttributes.classification" -ForegroundColor White
Write-Host "   → attributes: { customAttributes: { classification } }" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Mix de tous les types:" -ForegroundColor Yellow
Write-Host "   guid,displayName,customField,businessMetadata.dept,customAttributes.class" -ForegroundColor White
Write-Host "   → Tous mappés correctement dans leurs sections respectives" -ForegroundColor Gray
Write-Host ""
Write-Host "=== Options utiles ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "--dry-run      " -NoNewline -ForegroundColor Yellow
Write-Host "Prévisualiser sans modifier" -ForegroundColor White
Write-Host "--debug        " -NoNewline -ForegroundColor Yellow
Write-Host "Afficher les détails de traitement et payloads JSON" -ForegroundColor White
Write-Host "--batch-size N " -NoNewline -ForegroundColor Yellow
Write-Host "Contrôler la taille des lots (défaut: 100)" -ForegroundColor White
Write-Host "--error-csv    " -NoNewline -ForegroundColor Yellow
Write-Host "Sauvegarder les lignes échouées pour correction" -ForegroundColor White
Write-Host ""
Write-Host "=== Documentation ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Guide complet:    " -NoNewline -ForegroundColor Yellow
Write-Host "doc\guides\custom-metadata-management.md" -ForegroundColor White
Write-Host "Tests unitaires:  " -NoNewline -ForegroundColor Yellow
Write-Host "tests\test_bulk_update_custom_attributes.py" -ForegroundColor White
Write-Host "Exemples CSV:     " -NoNewline -ForegroundColor Yellow
Write-Host "samples\csv\" -ForegroundColor White
Write-Host ""
Write-Host "=== Prêt à utiliser! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Pour exécuter réellement (sans --dry-run), utilisez:" -ForegroundColor Cyan
Write-Host "  pvw entity bulk-update-csv --csv-file <votre_fichier.csv> --debug" -ForegroundColor White
Write-Host ""
