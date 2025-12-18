# ✅ Résumé: Fichier CSV d'exemple créé

## 📂 Fichier principal

**`samples/csv/bulk_update_example_complete.csv`**

Fichier CSV contenant 10 entités réalistes avec tous les types d'attributs personnalisés.

---

## 📝 Contenu

### En-têtes du CSV
```
guid | displayName | description | sourceSystem | refreshFrequency | lastRefreshDate | 
dataOwner | businessMetadata.department | businessMetadata.costCenter | 
businessMetadata.project | customAttributes.dataClassification | 
customAttributes.sensitivityLevel | customAttributes.retentionDays
```

### Données (10 lignes)
```
1. Customer Master Data (Salesforce, PII, HIGH, 2555 jours)
2. Product Catalog (SAP-ERP, INTERNAL, MEDIUM, 1825 jours)
3. Sales Orders History (SAP-ERP, CONFIDENTIAL, HIGH, 3650 jours)
4. Marketing Campaign Metrics (Salesforce, INTERNAL, LOW, 365 jours)
5. Employee Directory (Workday, RESTRICTED, CRITICAL, 7300 jours)
6. Financial Reports (Oracle, HIGHLY_CONFIDENTIAL, CRITICAL, 10950 jours)
7. Inventory Levels (SAP-ERP, INTERNAL, MEDIUM, 730 jours)
8. Website Analytics (Google-Analytics, PUBLIC, LOW, 395 jours)
9. Social Media Metrics (Hootsuite, INTERNAL, LOW, 180 jours)
10. Supply Chain Events (Kinaxis, INTERNAL, MEDIUM, 1095 jours)
```

---

## 🎯 Trois types d'attributs démarchandisés

### 1️⃣ Attributs simples
```csv
guid,displayName,description,sourceSystem,refreshFrequency,lastRefreshDate,dataOwner
```
→ Ajoutés directement dans `attributes`

### 2️⃣ Business Metadata
```csv
businessMetadata.department,businessMetadata.costCenter,businessMetadata.project
```
→ Regroupés dans `attributes.businessMetadata`

### 3️⃣ Custom Attributes
```csv
customAttributes.dataClassification,customAttributes.sensitivityLevel,customAttributes.retentionDays
```
→ Regroupés dans `attributes.customAttributes`

---

## 🚀 Utilisation

### 1. Test (preview mode)
```bash
pvw entity bulk-update-csv \
  --csv-file samples\csv\bulk_update_example_complete.csv \
  --dry-run --debug
```

**Résultat**: Affiche le JSON qui serait envoyé à Purview

### 2. Exécution réelle
```bash
pvw entity bulk-update-csv \
  --csv-file samples\csv\bulk_update_example_complete.csv \
  --debug
```

**Résultat**: Met à jour les 10 entités dans Purview

### 3. Adapter pour votre usage
```bash
# Copier le fichier
cp samples\csv\bulk_update_example_complete.csv samples\csv\mon_fichier.csv

# Éditer avec Excel ou VS Code
code samples\csv\mon_fichier.csv

# Remplacer les GUIDs par les vôtres
# Adapter les valeurs à votre contexte
# Utiliser le fichier
```

---

## 📊 Exemple de sortie (mode dry-run)

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

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [bulk-update-example-guide.md](bulk-update-example-guide.md) | Guide complet avec explications détaillées |
| [csv-example-visualization.md](csv-example-visualization.md) | Visualisation en tableaux de toutes les lignes |
| [example-csv-quickstart.md](example-csv-quickstart.md) | Démarrage rapide |
| [example-csv-reference.md](example-csv-reference.md) | Référence rapide |
| [CUSTOM_METADATA_HOWTO.md](CUSTOM_METADATA_HOWTO.md) | Guide complet custom metadata |
| [custom-metadata-quickref.md](custom-metadata-quickref.md) | Quick reference |

---

## ✨ Caractéristiques du fichier d'exemple

✅ **10 entités réalistes** - Représentant différents domaines métier  
✅ **Tous les types de métadonnées** - Simples, Business, Custom Attributes  
✅ **Valeurs cohérentes** - Exemples d'utilisation réelle  
✅ **GUIDs au format UUID v4** - Format standard Purview  
✅ **Prêt à adapter** - Peut servir de template  
✅ **Bien documenté** - Avec guides d'utilisation  

---

## ⚙️ Modifications possibles

### Ajouter des colonnes
```csv
# Avant
guid,displayName,sourceSystem

# Après
guid,displayName,sourceSystem,monNouvелAttribute
```

### Modifier les valeurs
Ouvrez le fichier CSV avec Excel ou VS Code et éditez directement.

### Supprimer des lignes
Gardez seulement celles dont vous avez besoin.

### Remplacer les GUIDs
Récupérez les GUIDs réels de vos entités Purview:
```bash
pvw search query-search --search "mon-asset"
```

---

## ✅ Avant d'exécuter

- [ ] Fichier CSV créé/adapté
- [ ] GUIDs vérifiés (réels ou exemples)
- [ ] Test avec `--dry-run --debug` effectué
- [ ] JSON généré vérifié
- [ ] Noms d'attributs vérifiés
- [ ] Business metadata templates existent (si utilisés)

---

## 📋 Fichiers CSV disponibles

Dans `samples/csv/`:
- `bulk_update_example_complete.csv` ← **Celui-ci** (10 entités complètes)
- `simple_custom_attrs.csv` (attributs simples)
- `example_custom_metadata.csv` (business metadata)
- `test_bulk_update_custom_attrs.csv` (mix d'attributs)

---

## 🎉 Prêt à utiliser!

Le fichier `bulk_update_example_complete.csv` est:
- ✅ Complet (tous les types d'attributs)
- ✅ Réaliste (données métier cohérentes)
- ✅ Documenté (guides détaillés)
- ✅ Adaptable (template prêt)
- ✅ Testé (validé par la suite de tests)

**Vous pouvez maintenant:**
1. Tester avec le fichier d'exemple
2. L'adapter à votre contexte
3. Automatiser vos mises à jour en masse
4. Enrichir vos métadonnées dans Purview
