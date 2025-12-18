# Gestion des Métadonnées Personnalisées (Custom Metadata)

## Types de métadonnées personnalisées dans Purview

### 1. **Custom Attributes** (Attributs personnalisés simples)
Attributs au niveau de l'entité, ajoutés directement dans `attributes`

### 2. **Business Metadata** (Métadonnées métier)
Métadonnées structurées, regroupées par template, stockées dans `businessMetadata`

### 3. **Custom Properties** (Propriétés personnalisées)
Propriétés spécifiques à un type d'entité

## 📋 Formats CSV supportés

### Format 1: Attributs personnalisés simples
```csv
guid,displayName,description,customAttr1,customAttr2,myProperty
abc-123,My Asset,Description,Value1,Value2,PropertyValue
def-456,Asset 2,Desc 2,Val1,Val2,PropValue
```

**Résultat dans Purview:**
```json
{
  "guid": "abc-123",
  "typeName": "...",
  "attributes": {
    "displayName": "My Asset",
    "description": "Description",
    "customAttr1": "Value1",
    "customAttr2": "Value2",
    "myProperty": "PropertyValue"
  }
}
```

### Format 2: Business Metadata avec notation pointée
```csv
guid,displayName,businessMetadata.department,businessMetadata.costCenter,businessMetadata.owner
abc-123,My Asset,Sales,CC-1234,john.doe@company.com
def-456,Asset 2,Marketing,CC-5678,jane.smith@company.com
```

**Résultat dans Purview:**
```json
{
  "guid": "abc-123",
  "attributes": {
    "displayName": "My Asset",
    "businessMetadata": {
      "department": "Sales",
      "costCenter": "CC-1234",
      "owner": "john.doe@company.com"
    }
  }
}
```

### Format 3: Custom Attributes avec section dédiée
```csv
guid,displayName,customAttributes.classification,customAttributes.sensitivity,customAttributes.dataOwner
abc-123,My Asset,CONFIDENTIAL,HIGH,Data Team
def-456,Asset 2,INTERNAL,MEDIUM,Analytics Team
```

**Résultat dans Purview:**
```json
{
  "guid": "abc-123",
  "attributes": {
    "displayName": "My Asset",
    "customAttributes": {
      "classification": "CONFIDENTIAL",
      "sensitivity": "HIGH",
      "dataOwner": "Data Team"
    }
  }
}
```

### Format 4: Mix de tous les types
```csv
guid,displayName,description,customField1,businessMetadata.department,businessMetadata.project,customAttributes.dataClass
abc-123,Complex Asset,Full description,SimpleValue,Engineering,ProjectX,PII
def-456,Asset 2,Desc 2,Value2,Sales,ProjectY,PUBLIC
```

## 🚀 Commandes d'utilisation

### 1. Preview avec debug (recommandé pour démarrer)
```bash
pvw entity bulk-update-csv \
  --csv-file my_custom_metadata.csv \
  --dry-run \
  --debug
```

**Ce que vous verrez:**
```
[DEBUG] CSV columns: ['guid', 'displayName', 'businessMetadata.department', ...]
[DEBUG] Total rows: 10
[DEBUG] has_guid: True
[DEBUG] Batch 1 entities:
{
  "guid": "abc-123",
  "attributes": {
    "displayName": "My Asset",
    "businessMetadata": {
      "department": "Sales"
    }
  }
}
[DEBUG] Payload:
{...}
```

### 2. Exécution réelle avec logging
```bash
pvw entity bulk-update-csv \
  --csv-file my_custom_metadata.csv \
  --debug
```

### 3. Avec gestion des erreurs
```bash
pvw entity bulk-update-csv \
  --csv-file my_custom_metadata.csv \
  --error-csv failed_rows.csv \
  --debug
```

### 4. Traitement par lots personnalisé
```bash
pvw entity bulk-update-csv \
  --csv-file large_file.csv \
  --batch-size 50 \
  --debug
```

## 📝 Exemples pratiques

### Exemple 1: Ajouter un département et un propriétaire
**Fichier: add_department.csv**
```csv
guid,businessMetadata.department,businessMetadata.owner
aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee,Sales,john.doe@company.com
bbbbbbbb-cccc-dddd-eeee-aaaaaaaaaaaa,Marketing,jane.smith@company.com
cccccccc-dddd-eeee-aaaa-bbbbbbbbbbbb,Engineering,bob.johnson@company.com
```

**Commande:**
```bash
pvw entity bulk-update-csv --csv-file add_department.csv --debug
```

### Exemple 2: Classifier les données sensibles
**Fichier: classify_data.csv**
```csv
guid,customAttributes.dataClassification,customAttributes.sensitivityLevel,customAttributes.retentionDays
aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee,PII,HIGH,2555
bbbbbbbb-cccc-dddd-eeee-aaaaaaaaaaaa,CONFIDENTIAL,MEDIUM,1825
cccccccc-dddd-eeee-aaaa-bbbbbbbbbbbb,PUBLIC,LOW,365
```

**Commande:**
```bash
pvw entity bulk-update-csv --csv-file classify_data.csv --debug
```

### Exemple 3: Métadonnées métier complètes
**Fichier: business_metadata.csv**
```csv
guid,displayName,description,businessMetadata.department,businessMetadata.costCenter,businessMetadata.project,businessMetadata.dataOwner,businessMetadata.lastReviewed
abc-123,Sales Dataset,Customer sales data,Sales,CC-1234,Q4-Analytics,sales-team@company.com,2025-12-01
def-456,Marketing Campaign,Campaign performance,Marketing,CC-5678,Campaign-2025,marketing@company.com,2025-11-15
```

**Commande:**
```bash
pvw entity bulk-update-csv --csv-file business_metadata.csv --debug
```

### Exemple 4: Attributs personnalisés simples
**Fichier: custom_attrs.csv**
```csv
guid,sourceSystem,refreshFrequency,contactEmail,criticalityLevel
abc-123,SAP,DAILY,data-team@company.com,HIGH
def-456,Salesforce,HOURLY,crm-team@company.com,CRITICAL
ghi-789,SharePoint,WEEKLY,docs-team@company.com,MEDIUM
```

**Commande:**
```bash
pvw entity bulk-update-csv --csv-file custom_attrs.csv --debug
```

## 🎯 Bonnes pratiques

### 1. Toujours tester avec --dry-run d'abord
```bash
pvw entity bulk-update-csv --csv-file my_data.csv --dry-run --debug
```

### 2. Utiliser --debug pour diagnostiquer
Le mode debug vous montre:
- ✅ Comment les colonnes sont mappées
- ✅ La structure JSON envoyée à Purview
- ✅ Les réponses de l'API
- ✅ Les erreurs détaillées

### 3. Gérer les erreurs avec --error-csv
```bash
pvw entity bulk-update-csv \
  --csv-file my_data.csv \
  --error-csv errors.csv \
  --debug
```
Les lignes échouées seront sauvegardées pour correction.

### 4. Traiter par lots raisonnables
```bash
# Pour de gros fichiers, utilisez des lots plus petits
pvw entity bulk-update-csv \
  --csv-file large_file.csv \
  --batch-size 25 \
  --debug
```

### 5. Valider les noms d'attributs
- Les noms d'attributs sont **sensibles à la casse**
- Vérifiez que les attributs existent dans votre schéma Purview
- Utilisez `--debug` pour voir les noms exacts envoyés

## 🔧 Notation pointée pour attributs imbriqués

### Syntaxe générale
```
section.attributeName
```

### Sections supportées
- `businessMetadata.xxx` → Business metadata
- `customAttributes.xxx` → Custom attributes section
- `anySection.xxx` → Toute section personnalisée

### Exemples
```csv
businessMetadata.department          → {"businessMetadata": {"department": "..."}}
businessMetadata.costCenter          → {"businessMetadata": {"costCenter": "..."}}
customAttributes.classification      → {"customAttributes": {"classification": "..."}}
customAttributes.sensitivity         → {"customAttributes": {"sensitivity": "..."}}
myCustomSection.field1               → {"myCustomSection": {"field1": "..."}}
```

## ⚠️ Limitations et notes

### 1. Types de valeurs
- Toutes les valeurs CSV sont traitées comme des **strings**
- Pour les nombres, booléens, etc., le serveur Purview fait la conversion
- Les valeurs vides (NaN, null) sont **ignorées**

### 2. Taille des payloads
- Purview limite chaque entité à **2 MB**
- Si vous avez beaucoup d'attributs, réduisez `--batch-size`

### 3. GUIDs requis
- Le mode GUID est utilisé pour les **mises à jour partielles**
- Seuls les attributs fournis sont modifiés
- Les autres attributs restent inchangés

### 4. Business Metadata Templates
- Les business metadata doivent correspondre à des **templates existants**
- Créez vos templates dans Purview avant d'importer
- Vérifiez les noms exacts des attributs

## 📊 Vérification des résultats

### 1. Lire une entité après mise à jour
```bash
pvw entity read --guid abc-123
```

### 2. Vérifier les business metadata
```bash
pvw entity read --guid abc-123 | grep -A 10 "businessMetadata"
```

### 3. Exporter pour comparaison
```bash
# Avant
pvw entity read --guid abc-123 > before.json

# Mise à jour
pvw entity bulk-update-csv --csv-file updates.csv

# Après
pvw entity read --guid abc-123 > after.json

# Comparer
diff before.json after.json
```

## 🆘 Dépannage

### Problème: Attributs non appliqués
**Solution:**
1. Vérifiez les noms d'attributs avec `--debug`
2. Assurez-vous que l'attribut existe dans le schéma
3. Vérifiez les permissions sur l'entité

### Problème: Business Metadata non créé
**Solution:**
1. Vérifiez que le template existe dans Purview
2. Utilisez les noms exacts des attributs du template
3. Vérifiez les permissions business metadata

### Problème: Certaines lignes échouent
**Solution:**
1. Utilisez `--error-csv` pour capturer les échecs
2. Examinez les logs avec `--debug`
3. Corrigez les GUIDs invalides ou attributs manquants

### Problème: Timeout sur gros fichiers
**Solution:**
1. Réduisez `--batch-size` (ex: 25 ou 50)
2. Divisez le fichier en plusieurs petits fichiers
3. Augmentez le timeout réseau si possible

## 📚 Ressources

- [Guide Bulk Update](./bulk-update-custom-attributes.md)
- [Documentation Purview Business Metadata](https://learn.microsoft.com/azure/purview/)
- [Tests d'exemple](../../tests/test_bulk_update_custom_attributes.py)
- [Exemples CSV](../../samples/csv/)

## 💡 Exemples de cas d'usage

### Cas 1: Migration de métadonnées depuis un autre système
```csv
guid,sourceSystem,sourcePath,migrationDate,businessMetadata.originalOwner
abc,Legacy-System,/data/sales/customers,2025-12-18,old-owner@company.com
```

### Cas 2: Enrichissement automatique
```csv
guid,businessMetadata.dataQualityScore,businessMetadata.lastProfiledDate,businessMetadata.recordCount
abc,95.5,2025-12-18,1000000
```

### Cas 3: Conformité et gouvernance
```csv
guid,customAttributes.gdprApplicable,customAttributes.retentionPolicy,customAttributes.encryptionStatus
abc,YES,7-YEARS,ENCRYPTED
```

### Cas 4: Gestion de projet
```csv
guid,businessMetadata.projectName,businessMetadata.sprint,businessMetadata.priority,businessMetadata.assignee
abc,DataWarehouse-2025,Sprint-23,HIGH,team-lead@company.com
```
