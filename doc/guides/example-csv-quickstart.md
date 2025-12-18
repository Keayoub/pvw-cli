# 🚀 Guide rapide du fichier CSV d'exemple

## 📂 Fichier: `samples/csv/bulk_update_example_complete.csv`

Fichier CSV prêt à l'emploi avec 10 entités réalistes.

---

## ⚡ Utilisation rapide

### 1. Voir le contenu
```bash
type samples\csv\bulk_update_example_complete.csv
```

### 2. Test (preview)
```bash
pvw entity bulk-update-csv \
  --csv-file samples\csv\bulk_update_example_complete.csv \
  --dry-run --debug
```

### 3. Exécution
```bash
pvw entity bulk-update-csv \
  --csv-file samples\csv\bulk_update_example_complete.csv \
  --debug
```

---

## 📋 Contenu résumé

| Ligne | Asset | Système | Classification | Fréquence |
|------|-------|---------|-----------------|-----------|
| 1 | Customer Master Data | Salesforce | PII | DAILY |
| 2 | Product Catalog | SAP-ERP | INTERNAL | WEEKLY |
| 3 | Sales Orders | SAP-ERP | CONFIDENTIAL | HOURLY |
| 4 | Marketing Metrics | Salesforce | INTERNAL | REAL_TIME |
| 5 | Employee Directory | Workday | RESTRICTED | DAILY |
| 6 | Financial Reports | Oracle | HIGHLY_CONFIDENTIAL | MONTHLY |
| 7 | Inventory Levels | SAP-ERP | INTERNAL | REAL_TIME |
| 8 | Website Analytics | Google | PUBLIC | DAILY |
| 9 | Social Media | Hootsuite | INTERNAL | HOURLY |
| 10 | Supply Chain Events | Kinaxis | INTERNAL | REAL_TIME |

---

## 🔑 Colonnes du CSV

### Identifiants
- `guid` - UUID unique pour chaque entité

### Attributs simples
- `displayName` - Nom de l'asset
- `description` - Description
- `sourceSystem` - Système source
- `refreshFrequency` - Fréquence de mise à jour
- `lastRefreshDate` - Dernière mise à jour
- `dataOwner` - Propriétaire (email)

### Business Metadata
- `businessMetadata.department` - Département
- `businessMetadata.costCenter` - Centre de coûts
- `businessMetadata.project` - Projet

### Custom Attributes
- `customAttributes.dataClassification` - Classification (PII, CONFIDENTIAL, INTERNAL, PUBLIC, RESTRICTED, HIGHLY_CONFIDENTIAL)
- `customAttributes.sensitivityLevel` - Sensibilité (CRITICAL, HIGH, MEDIUM, LOW)
- `customAttributes.retentionDays` - Jours de rétention

---

## 💡 Adapter le fichier

### Utiliser comme template
```bash
cp samples\csv\bulk_update_example_complete.csv mon_fichier.csv
```

### Modifier les GUIDs
```powershell
# PowerShell
$csv = Import-Csv "mon_fichier.csv"
$csv[0].guid = "votre-nouveau-guid"
$csv | Export-Csv "mon_fichier.csv" -NoTypeInformation
```

### Filtrer par colonne
```powershell
# Garder seulement Sales
$csv = Import-Csv "bulk_update_example_complete.csv"
$csv | Where-Object { $_.businessMetadata.department -eq "Sales" } | 
  Export-Csv "sales_only.csv" -NoTypeInformation
```

---

## ✅ Résultats attendus

Après exécution avec succès:
```
[OK] Bulk update completed. Success: 10, Failed: 0
```

Vérification:
```bash
# Lire l'asset mis à jour
pvw entity read --guid a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6
```

---

## 📖 Voir aussi

- **Guide complet**: `doc/guides/bulk-update-example-guide.md`
- **Visualisation**: `doc/guides/csv-example-visualization.md`
- **Quick ref**: `doc/guides/custom-metadata-quickref.md`
- **Comment-faire**: `doc/guides/CUSTOM_METADATA_HOWTO.md`

---

## 🎯 Cas d'usage

✅ Enrichir avec des métadonnées métier  
✅ Ajouter classification de données  
✅ Mettre à jour les propriétaires  
✅ Ajouter des informations système source  
✅ Définir les politiques de rétention  
✅ Mettre à jour les fréquences de rafraîchissement  

---

## 🎉 Prêt!

Le fichier contient des données réalistes et peut être utilisé:
1. Directement pour tester
2. Comme template à adapter
3. Pour comprendre le format
4. Pour documentation

**Adaptation requise**: Remplacer les GUIDs par vos entités réelles!
