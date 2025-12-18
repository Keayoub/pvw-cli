# 📌 Fichier CSV d'exemple - Référence

## 📂 Location

```
samples/csv/bulk_update_example_complete.csv
```

## 📊 Format CSV

```
guid,displayName,description,sourceSystem,refreshFrequency,lastRefreshDate,dataOwner,businessMetadata.department,businessMetadata.costCenter,businessMetadata.project,customAttributes.dataClassification,customAttributes.sensitivityLevel,customAttributes.retentionDays
```

## 📝 Lignes de données (résumé)

```
1. guid=a1b2c3d4... | Customer Master Data | Salesforce | PII | HIGH | 2555 days
2. guid=b2c3d4e5... | Product Catalog | SAP-ERP | INTERNAL | MEDIUM | 1825 days
3. guid=c3d4e5f6... | Sales Orders History | SAP-ERP | CONFIDENTIAL | HIGH | 3650 days
4. guid=d4e5f6a7... | Marketing Campaign Metrics | Salesforce | INTERNAL | LOW | 365 days
5. guid=e5f6a7b8... | Employee Directory | Workday | RESTRICTED | CRITICAL | 7300 days
6. guid=f6a7b8c9... | Financial Reports | Oracle | HIGHLY_CONFIDENTIAL | CRITICAL | 10950 days
7. guid=a7b8c9da... | Inventory Levels | SAP-ERP | INTERNAL | MEDIUM | 730 days
8. guid=b8c9daeb... | Website Analytics | Google-Analytics | PUBLIC | LOW | 395 days
9. guid=c9daebfc... | Social Media Metrics | Hootsuite | INTERNAL | LOW | 180 days
10. guid=daebfcfd... | Supply Chain Events | Kinaxis | INTERNAL | MEDIUM | 1095 days
```

## 🎯 Utilisations

### Voir le contenu brut
```bash
cat samples\csv\bulk_update_example_complete.csv
```

### Test en preview
```bash
pvw entity bulk-update-csv \
  --csv-file samples\csv\bulk_update_example_complete.csv \
  --dry-run --debug
```

### Exécution réelle
```bash
pvw entity bulk-update-csv \
  --csv-file samples\csv\bulk_update_example_complete.csv \
  --debug
```

### Copier pour adapter
```bash
cp samples\csv\bulk_update_example_complete.csv samples\csv\mon_fichier.csv
```

## 🔑 Types d'attributs dans le fichier

### ✅ Attributs simples
- displayName
- description
- sourceSystem
- refreshFrequency
- lastRefreshDate
- dataOwner

### ✅ Business Metadata
- businessMetadata.department
- businessMetadata.costCenter
- businessMetadata.project

### ✅ Custom Attributes
- customAttributes.dataClassification
- customAttributes.sensitivityLevel
- customAttributes.retentionDays

## 📚 Documentation liée

- [Guide complet](bulk-update-example-guide.md)
- [Visualisation tableau](csv-example-visualization.md)
- [Quick start](example-csv-quickstart.md)
- [Comment-faire](CUSTOM_METADATA_HOWTO.md)
- [Quick ref](custom-metadata-quickref.md)

## ⚠️ Important

**Les GUIDs dans ce fichier sont des exemples.**

Pour utiliser, vous devez:
1. ✅ Remplacer les GUIDs par les vrais GUIDs de vos entités
2. ✅ Adapter les valeurs à votre contexte
3. ✅ Tester avec `--dry-run --debug` d'abord

## 🎉 Prêt à utiliser comme template!
