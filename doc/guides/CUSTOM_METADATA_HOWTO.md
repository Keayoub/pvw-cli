# 🎯 Guide Pratique: Gérer les Custom Metadata avec bulk-update-csv

## Vue d'ensemble

Le bulk-update-csv supporte maintenant **trois types de métadonnées personnalisées** :

1. **Attributs simples** - Colonnes ajoutées directement dans `attributes`
2. **Business Metadata** - Métadonnées structurées avec notation pointée
3. **Custom Attributes** - Section dédiée pour attributs personnalisés

---

## 📝 Formats supportés

### Format 1: Attributs personnalisés simples

**Fichier CSV:**
```csv
guid,displayName,description,myCustomField,anotherCustomField
abc-123,Asset 1,Description,Value 1,Value A
def-456,Asset 2,Description,Value 2,Value B
```

**Commande:**
```bash
pvw entity bulk-update-csv --csv-file simple.csv --dry-run --debug
```

**Résultat dans Purview:**
```json
{
  "guid": "abc-123",
  "attributes": {
    "displayName": "Asset 1",
    "description": "Description",
    "myCustomField": "Value 1",
    "anotherCustomField": "Value A"
  }
}
```

---

### Format 2: Business Metadata avec notation pointée

**Fichier CSV:**
```csv
guid,displayName,businessMetadata.department,businessMetadata.owner,businessMetadata.costCenter
abc-123,Sales Data,Sales Department,john.doe@company.com,CC-1234
def-456,Marketing Data,Marketing Department,jane.smith@company.com,CC-5678
```

**Commande:**
```bash
pvw entity bulk-update-csv --csv-file business_metadata.csv --dry-run --debug
```

**Résultat dans Purview:**
```json
{
  "guid": "abc-123",
  "attributes": {
    "displayName": "Sales Data",
    "businessMetadata": {
      "department": "Sales Department",
      "owner": "john.doe@company.com",
      "costCenter": "CC-1234"
    }
  }
}
```

---

### Format 3: Custom Attributes avec section dédiée

**Fichier CSV:**
```csv
guid,displayName,customAttributes.classification,customAttributes.sensitivity,customAttributes.dataOwner
abc-123,Sensitive Data,CONFIDENTIAL,HIGH,Data Team
def-456,Public Data,PUBLIC,LOW,Analytics Team
```

**Commande:**
```bash
pvw entity bulk-update-csv --csv-file custom_attributes.csv --dry-run --debug
```

**Résultat dans Purview:**
```json
{
  "guid": "abc-123",
  "attributes": {
    "displayName": "Sensitive Data",
    "customAttributes": {
      "classification": "CONFIDENTIAL",
      "sensitivity": "HIGH",
      "dataOwner": "Data Team"
    }
  }
}
```

---

### Format 4: Mix complet (RECOMMANDÉ pour cas complexes)

**Fichier CSV:**
```csv
guid,displayName,description,sourceSystem,businessMetadata.department,businessMetadata.owner,customAttributes.classification
abc-123,Complete Example,Full metadata example,SAP-ERP,Sales,john@company.com,CONFIDENTIAL
def-456,Another Example,More metadata,Salesforce,Marketing,jane@company.com,INTERNAL
```

**Commande:**
```bash
pvw entity bulk-update-csv --csv-file complete.csv --dry-run --debug
```

**Résultat dans Purview:**
```json
{
  "guid": "abc-123",
  "attributes": {
    "displayName": "Complete Example",
    "description": "Full metadata example",
    "sourceSystem": "SAP-ERP",
    "businessMetadata": {
      "department": "Sales",
      "owner": "john@company.com"
    },
    "customAttributes": {
      "classification": "CONFIDENTIAL"
    }
  }
}
```

---

## 🚀 Workflow recommandé

### Étape 1: Préparer votre CSV

Créez un fichier CSV avec les colonnes appropriées. Exemples disponibles dans `samples/csv/` :
- `simple_custom_attrs.csv` - Attributs simples
- `example_custom_metadata.csv` - Business metadata complet
- `test_bulk_update_custom_attrs.csv` - Mix d'attributs

### Étape 2: Test en mode dry-run avec debug

```bash
pvw entity bulk-update-csv --csv-file votre_fichier.csv --dry-run --debug
```

**Ce que vous verrez:**
```
[DEBUG] CSV columns: ['guid', 'displayName', 'businessMetadata.department', ...]
[DEBUG] Total rows: 5
[DEBUG] First row:
{'guid': 'abc-123', 'displayName': 'Asset 1', ...}
[DEBUG] has_guid: True
[DEBUG] Batch 1 entities:
[
  {
    "guid": "abc-123",
    "attributes": {
      "displayName": "Asset 1",
      "businessMetadata": {
        "department": "Sales"
      }
    }
  }
]
[DRY RUN] Would update GUID abc-123 set displayName=Asset 1
[DRY RUN] Would update GUID abc-123 set businessMetadata.department=Sales
```

### Étape 3: Vérifier le payload JSON

Le mode `--debug` affiche le JSON exact qui sera envoyé à Purview. Vérifiez:
- ✅ Les noms d'attributs sont corrects
- ✅ Les valeurs sont bien formatées
- ✅ Les sections (businessMetadata, customAttributes) sont correctes
- ✅ Les GUIDs sont valides

### Étape 4: Exécution réelle

```bash
pvw entity bulk-update-csv --csv-file votre_fichier.csv --error-csv errors.csv --debug
```

### Étape 5: Vérifier les résultats

```bash
# Lire une entité mise à jour
pvw entity read --guid abc-123

# Vérifier les business metadata
pvw entity read --guid abc-123 | Select-String "businessMetadata" -Context 5
```

---

## 💡 Exemples de cas d'usage

### Cas 1: Ajouter un département à plusieurs assets

**1. Créer le CSV:**
```csv
guid,businessMetadata.department,businessMetadata.owner
aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee,Sales,sales-team@company.com
bbbbbbbb-cccc-dddd-eeee-aaaaaaaaaaaa,Marketing,marketing-team@company.com
cccccccc-dddd-eeee-aaaa-bbbbbbbbbbbb,Engineering,eng-team@company.com
```

**2. Tester:**
```powershell
pvw entity bulk-update-csv --csv-file add_department.csv --dry-run --debug
```

**3. Exécuter:**
```powershell
pvw entity bulk-update-csv --csv-file add_department.csv --debug
```

---

### Cas 2: Classifier des données sensibles

**1. Créer le CSV:**
```csv
guid,customAttributes.dataClassification,customAttributes.sensitivityLevel,customAttributes.retentionDays
aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee,PII,HIGH,2555
bbbbbbbb-cccc-dddd-eeee-aaaaaaaaaaaa,CONFIDENTIAL,MEDIUM,1825
cccccccc-dddd-eeee-aaaa-bbbbbbbbbbbb,PUBLIC,LOW,365
```

**2. Tester:**
```powershell
pvw entity bulk-update-csv --csv-file classify_data.csv --dry-run --debug
```

**3. Exécuter:**
```powershell
pvw entity bulk-update-csv --csv-file classify_data.csv --debug
```

---

### Cas 3: Enrichir avec des métadonnées système source

**1. Créer le CSV:**
```csv
guid,displayName,sourceSystem,sourceTable,sourceSchema,lastRefreshDate
aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee,Customer Data,SAP-ERP,CUSTOMERS,SALES,2025-12-18
bbbbbbbb-cccc-dddd-eeee-aaaaaaaaaaaa,Order Data,SAP-ERP,ORDERS,SALES,2025-12-18
cccccccc-dddd-eeee-aaaa-bbbbbbbbbbbb,Product Data,SAP-ERP,PRODUCTS,INVENTORY,2025-12-17
```

**2. Tester et exécuter:**
```powershell
pvw entity bulk-update-csv --csv-file enrich_source_metadata.csv --dry-run --debug
pvw entity bulk-update-csv --csv-file enrich_source_metadata.csv --debug
```

---

### Cas 4: Métadonnées de gouvernance complètes

**1. Créer le CSV:**
```csv
guid,displayName,businessMetadata.department,businessMetadata.dataOwner,businessMetadata.costCenter,customAttributes.dataClassification,customAttributes.retentionPolicy,customAttributes.encryptionRequired
abc-123,Customer Database,Sales,john.doe@company.com,CC-1234,PII,7-YEARS,YES
def-456,Marketing Analytics,Marketing,jane.smith@company.com,CC-5678,INTERNAL,3-YEARS,NO
ghi-789,Financial Reports,Finance,bob.johnson@company.com,CC-9012,HIGHLY_CONFIDENTIAL,10-YEARS,YES
```

**2. Tester et exécuter:**
```powershell
pvw entity bulk-update-csv --csv-file governance_metadata.csv --dry-run --debug
pvw entity bulk-update-csv --csv-file governance_metadata.csv --debug
```

---

## 🔧 Options avancées

### Contrôler la taille des lots

Pour de gros fichiers, utilisez des lots plus petits:
```bash
pvw entity bulk-update-csv --csv-file large_file.csv --batch-size 25 --debug
```

### Capturer les erreurs

Sauvegarder les lignes échouées pour correction:
```bash
pvw entity bulk-update-csv --csv-file data.csv --error-csv failed_rows.csv --debug
```

### Mode silencieux (sans debug)

Pour exécution en production:
```bash
pvw entity bulk-update-csv --csv-file data.csv --batch-size 50
```

---

## ⚠️ Points importants

### 1. Notation pointée obligatoire pour imbrication
❌ **FAUX** - Ne fonctionne pas:
```csv
guid,businessMetadata
abc-123,{"department": "Sales"}
```

✅ **CORRECT** - Utilisez la notation pointée:
```csv
guid,businessMetadata.department
abc-123,Sales
```

### 2. Noms d'attributs sensibles à la casse
```csv
# Attention aux majuscules/minuscules
displayName   ✅ Correct
DisplayName   ❌ Différent attribute
displayname   ❌ Différent attribute
```

### 3. Valeurs vides ignorées
```csv
guid,displayName,description
abc-123,Asset Name,        # description vide = ignorée
```

### 4. GUIDs requis pour mise à jour
- ✅ **Mise à jour**: CSV doit contenir colonne `guid`
- ✅ **Création**: CSV doit contenir `typeName` et `qualifiedName`

---

## 🆘 Dépannage

### Problème: "No such option: --debug"
**Solution:**
```bash
cd c:\Dvlp\Purview\Purview_cli
pip install -e .
```

### Problème: Attributs non appliqués
**Diagnostic:**
```bash
pvw entity bulk-update-csv --csv-file data.csv --dry-run --debug
```
Vérifiez le JSON généré pour voir comment les attributs sont mappés.

### Problème: Business Metadata non créé
**Causes possibles:**
1. Le template business metadata n'existe pas dans Purview
2. Noms d'attributs incorrects
3. Permissions insuffisantes

**Solution:**
1. Vérifiez que le template existe dans Purview UI
2. Utilisez `--debug` pour voir les noms exacts envoyés
3. Vérifiez les permissions business metadata

### Problème: Certaines lignes échouent
**Solution:**
```bash
# Capturer les erreurs
pvw entity bulk-update-csv --csv-file data.csv --error-csv errors.csv --debug

# Examiner errors.csv
Get-Content errors.csv

# Corriger et réessayer
pvw entity bulk-update-csv --csv-file errors.csv --debug
```

---

## 📚 Ressources

### Documentation
- **Guide complet**: `doc/guides/custom-metadata-management.md`
- **Quick reference**: `doc/guides/custom-metadata-quickref.md`
- **Bulk update guide**: `doc/guides/bulk-update-custom-attributes.md`

### Exemples
- **CSV simples**: `samples/csv/simple_custom_attrs.csv`
- **CSV complets**: `samples/csv/example_custom_metadata.csv`
- **CSV tests**: `samples/csv/test_bulk_update_custom_attrs.csv`

### Scripts
- **Demo interactive**: `samples/demo_custom_metadata.ps1`
- **Tests unitaires**: `tests/test_bulk_update_custom_attributes.py`

### Commandes utiles
```bash
# Aide
pvw entity bulk-update-csv --help

# Tests
python tests\test_bulk_update_custom_attributes.py

# Demo
.\samples\demo_custom_metadata.ps1
```

---

## ✅ Checklist avant exécution

- [ ] CSV créé avec colonnes appropriées
- [ ] GUIDs valides et existants dans Purview
- [ ] Noms d'attributs vérifiés (sensibles à la casse)
- [ ] Test avec `--dry-run --debug` effectué
- [ ] JSON généré vérifié
- [ ] Business metadata templates existent (si utilisés)
- [ ] Permissions vérifiées
- [ ] `--error-csv` configuré pour capturer les erreurs
- [ ] Backup des données si nécessaire

---

## 🎯 Résumé rapide

```bash
# 1. Test
pvw entity bulk-update-csv --csv-file data.csv --dry-run --debug

# 2. Exécution
pvw entity bulk-update-csv --csv-file data.csv --error-csv errors.csv --debug

# 3. Vérification
pvw entity read --guid <guid>
```

**Format CSV recommandé:**
```csv
guid,displayName,customAttr,businessMetadata.dept,customAttributes.class
abc,Name,Value,Sales,CONFIDENTIAL
```

**Trois types d'attributs supportés:**
1. Simples: `customAttr` → `attributes.customAttr`
2. Business: `businessMetadata.dept` → `attributes.businessMetadata.dept`
3. Custom: `customAttributes.class` → `attributes.customAttributes.class`
