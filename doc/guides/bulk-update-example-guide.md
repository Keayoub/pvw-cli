# 📊 Exemple de CSV pour Bulk Update avec Custom Attributes

## 📁 Fichier: `samples/csv/bulk_update_example_complete.csv`

Ce fichier CSV contient un exemple complet avec:
- **10 entités** réalistes
- **3 types de custom attributes**
- **Cas d'usage réels** d'une entreprise

---

## 🎯 Structure du CSV

### Colonnes principales

| Colonne | Type | Description |
|---------|------|-------------|
| `guid` | Identifiant | GUID unique de l'entité dans Purview |
| `displayName` | Attribut simple | Nom affiché dans Purview |
| `description` | Attribut simple | Description de l'asset |

### Custom Attributes simples

| Colonne | Description |
|---------|-------------|
| `sourceSystem` | Système source (SAP-ERP, Salesforce, etc.) |
| `refreshFrequency` | Fréquence de rafraîchissement (DAILY, HOURLY, REAL_TIME) |
| `lastRefreshDate` | Date du dernier rafraîchissement |
| `dataOwner` | Email du propriétaire des données |

### Business Metadata (notation pointée)

| Colonne | Description |
|---------|-------------|
| `businessMetadata.department` | Département propriétaire |
| `businessMetadata.costCenter` | Centre de coûts |
| `businessMetadata.project` | Projet associé |

### Custom Attributes (section dédiée)

| Colonne | Description |
|---------|-------------|
| `customAttributes.dataClassification` | Classification (PII, CONFIDENTIAL, INTERNAL, PUBLIC, RESTRICTED, HIGHLY_CONFIDENTIAL) |
| `customAttributes.sensitivityLevel` | Niveau de sensibilité (CRITICAL, HIGH, MEDIUM, LOW) |
| `customAttributes.retentionDays` | Jours de rétention des données |

---

## 📝 Contenu de l'exemple

### Ligne 1: Customer Master Data
```csv
a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6,Customer Master Data,Complete customer information from CRM system,Salesforce-CRM,DAILY,2025-12-18,crm-team@company.com,Sales,CC-1001,CRM-Migration-2025,PII,HIGH,2555
```

**Qu'est-ce qui sera mis à jour dans Purview:**
```json
{
  "guid": "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6",
  "attributes": {
    "displayName": "Customer Master Data",
    "description": "Complete customer information from CRM system",
    "sourceSystem": "Salesforce-CRM",
    "refreshFrequency": "DAILY",
    "lastRefreshDate": "2025-12-18",
    "dataOwner": "crm-team@company.com",
    "businessMetadata": {
      "department": "Sales",
      "costCenter": "CC-1001",
      "project": "CRM-Migration-2025"
    },
    "customAttributes": {
      "dataClassification": "PII",
      "sensitivityLevel": "HIGH",
      "retentionDays": "2555"
    }
  }
}
```

---

## 🚀 Comment utiliser ce fichier

### 1. Test avec preview
```bash
pvw entity bulk-update-csv --csv-file samples\csv\bulk_update_example_complete.csv --dry-run --debug
```

**Vous verrez:**
```
[DEBUG] CSV columns: ['guid', 'displayName', 'description', 'sourceSystem', ...]
[DEBUG] Total rows: 10
[DEBUG] has_guid: True
[DEBUG] Batch 1 entities:
[
  {
    "guid": "a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6",
    "attributes": {
      "displayName": "Customer Master Data",
      ...
      "businessMetadata": {...},
      "customAttributes": {...}
    }
  },
  ...
]
```

### 2. Exécution réelle (si les GUIDs existent dans votre Purview)
```bash
pvw entity bulk-update-csv --csv-file samples\csv\bulk_update_example_complete.csv --debug
```

### 3. Avec gestion des erreurs
```bash
pvw entity bulk-update-csv \
  --csv-file samples\csv\bulk_update_example_complete.csv \
  --error-csv failed_updates.csv \
  --debug
```

---

## 📊 Exemples de données

### Customer Master Data (Salesforce)
```
GUID: a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6
Attributs:
  - sourceSystem: Salesforce-CRM
  - refreshFrequency: DAILY
  - Department: Sales
  - Classification: PII (données personnelles)
  - Sensitivity: HIGH
  - Retention: 2555 jours (7 ans)
```

### Sales Orders History (SAP)
```
GUID: c3d4e5f6-a7b8-49ca-d1e2-f3a4b5c6d7e8
Attributs:
  - sourceSystem: SAP-ERP
  - refreshFrequency: HOURLY
  - Department: Sales
  - Classification: CONFIDENTIAL
  - Sensitivity: HIGH
  - Retention: 3650 jours (10 ans)
```

### Website Analytics (Google Analytics)
```
GUID: b8c9daeb-fcaf-541f-c6d7-e8f9a0b1c2d3
Attributs:
  - sourceSystem: Google-Analytics
  - refreshFrequency: DAILY
  - Department: Digital
  - Classification: PUBLIC (données publiques)
  - Sensitivity: LOW
  - Retention: 395 jours (13 mois)
```

---

## 🔧 Personnaliser le fichier

### Modifier les GUIDs
Remplacez les GUIDs par les vrais GUIDs de vos entités dans Purview:

```bash
# Lister les entités pour obtenir les GUIDs
pvw search query-search --search "your-asset-name"

# Puis remplacer dans le CSV
```

### Ajouter/supprimer des colonnes
Vous pouvez ajouter ou supprimer n'importe quelle colonne:

```csv
# Exemple: Ajouter une colonne supplémentaire
guid,displayName,description,sourceSystem,customAttributes.dataClassification,customAttributes.newField
a1b2c3d4-...,Asset Name,Description,SAP-ERP,PII,NewValue
```

### Modifier les Business Metadata
Changez les noms des attributs pour correspondre à vos templates:

```csv
# Au lieu de businessMetadata.department, utilisez votre attribut
businessMetadata.myCustomAttribute
```

---

## ✅ Validations avant exécution

### Checklist
- [ ] Les GUIDs existent dans votre Purview
- [ ] Les noms d'attributs correspondent à votre schéma
- [ ] Les business metadata templates existent
- [ ] Test avec `--dry-run --debug` effectué
- [ ] Le JSON généré vérifie les valeurs

### Vérification des GUIDs
```bash
# Vérifier qu'un GUID existe
pvw entity read --guid a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6
```

### Vérifier les templates de Business Metadata
```bash
# Dans Purview UI:
# - Allez dans "Governance" > "Business Metadata Templates"
# - Vérifiez que vos templates existent
```

---

## 📚 Cas d'usage par ligne

| Line | Asset | Use Case |
|------|-------|----------|
| 1 | Customer Data | Données personnelles sensibles |
| 2 | Product Catalog | Données métier courantes |
| 3 | Sales Orders | Données historiques importantes |
| 4 | Marketing Metrics | Données temps réel |
| 5 | Employee Directory | Données RH sensibles |
| 6 | Financial Reports | Données hautement confidentielles |
| 7 | Inventory Levels | Données temps réel critiques |
| 8 | Website Analytics | Données publiques |
| 9 | Social Media | Données non confidentielles |
| 10 | Supply Chain | Données logistiques temps réel |

---

## 🎯 Résultat attendu

Après exécution:
```
[OK] Bulk update completed. Success: 10, Failed: 0
```

Vérification:
```bash
# Lire une entité mise à jour
pvw entity read --guid a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6

# Vérifier les custom attributes
pvw entity read --guid a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6 | grep -A 20 "customAttributes"
```

---

## 💡 Conseils pratiques

### 1. Copier ce fichier comme template
```bash
cp samples\csv\bulk_update_example_complete.csv samples\csv\my_updates.csv
```

### 2. Éditer avec Excel ou PowerShell
```powershell
# Importer depuis CSV
$data = Import-Csv "samples\csv\my_updates.csv"

# Modifier les données
$data | Where-Object { $_.department -eq "Sales" } | Export-Csv "sales_updates.csv"

# Utiliser
pvw entity bulk-update-csv --csv-file sales_updates.csv --debug
```

### 3. Générer dynamiquement depuis Purview
```bash
# Exporter les entités actuelles
pvw search query-search --search "*" | Export-Csv current_assets.csv

# Ajouter vos custom attributes
# Puis utiliser pour bulk update
```

---

## 📖 Autres exemples

### Exemple simple (attributs seulement)
```bash
samples\csv\simple_custom_attrs.csv
```

### Exemple avec Business Metadata
```bash
samples\csv\example_custom_metadata.csv
```

### Exemple avec test initial
```bash
samples\csv\test_bulk_update_custom_attrs.csv
```

---

## 🆘 Dépannage

### Si certaines lignes échouent
```bash
pvw entity bulk-update-csv \
  --csv-file bulk_update_example_complete.csv \
  --error-csv errors.csv \
  --debug
```

Puis examiner `errors.csv` et corriger.

### Si les custom attributes ne s'appliquent pas
```bash
# Vérifier avec debug que les attributs sont envoyés
pvw entity bulk-update-csv \
  --csv-file bulk_update_example_complete.csv \
  --dry-run --debug
```

Vérifier dans les logs que vos attributs sont présents.

---

## ✨ Fonctionnalités démontrées

✅ Attributs simples (displayName, description, sourceSystem)  
✅ Custom attributes simples (refreshFrequency, lastRefreshDate, dataOwner)  
✅ Business Metadata structurée (department, costCenter, project)  
✅ Custom attributes section (dataClassification, sensitivityLevel, retentionDays)  
✅ GUIDs réalistes au format UUID v4  
✅ Données variées représentant différents domaines  

---

## 🎉 Prêt à utiliser!

Vous pouvez maintenant:
1. Copier ce fichier comme template
2. Remplacer les GUIDs par vos entités
3. Adapter les colonnes à votre schéma
4. Tester avec `--dry-run --debug`
5. Exécuter le bulk update
