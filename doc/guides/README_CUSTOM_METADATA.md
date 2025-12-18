# 📖 README - Custom Metadata Management

## ✅ Fonctionnalités implémentées

### 1. Option `--debug` ajoutée
La commande `bulk-update-csv` supporte maintenant l'option `--debug` pour un diagnostic détaillé.

### 2. Support complet des métadonnées personnalisées
- ✅ Attributs simples
- ✅ Business Metadata avec notation pointée
- ✅ Custom Attributes avec section dédiée
- ✅ Mix de tous les types

## 🚀 Démarrage rapide

### Test simple
```bash
pvw entity bulk-update-csv --csv-file samples\csv\simple_custom_attrs.csv --dry-run --debug
```

### Exemple avec business metadata
```bash
pvw entity bulk-update-csv --csv-file samples\csv\example_custom_metadata.csv --dry-run --debug
```

## 📁 Fichiers importants

### Documentation
| Fichier | Description |
|---------|-------------|
| `doc/guides/CUSTOM_METADATA_HOWTO.md` | Guide pratique complet avec exemples |
| `doc/guides/custom-metadata-management.md` | Documentation détaillée |
| `doc/guides/custom-metadata-quickref.md` | Référence rapide (cheat sheet) |
| `doc/guides/bulk-update-custom-attributes.md` | Guide bulk update |

### Exemples CSV
| Fichier | Contenu |
|---------|---------|
| `samples/csv/simple_custom_attrs.csv` | Attributs simples |
| `samples/csv/example_custom_metadata.csv` | Business metadata complet |
| `samples/csv/test_bulk_update_custom_attrs.csv` | Mix d'attributs |

### Scripts et tests
| Fichier | Description |
|---------|-------------|
| `samples/demo_custom_metadata.ps1` | Démo interactive |
| `tests/test_bulk_update_custom_attributes.py` | Tests unitaires (7 scénarios) |

## 📋 Formats CSV supportés

### Format basique
```csv
guid,displayName,myCustomField
abc-123,Asset Name,Custom Value
```

### Business Metadata
```csv
guid,businessMetadata.department,businessMetadata.owner
abc-123,Sales,owner@company.com
```

### Custom Attributes
```csv
guid,customAttributes.classification
abc-123,CONFIDENTIAL
```

### Mix complet
```csv
guid,displayName,customField,businessMetadata.dept,customAttributes.class
abc-123,Name,Value,Sales,CONFIDENTIAL
```

## 🎯 Commandes essentielles

```bash
# Preview (recommandé)
pvw entity bulk-update-csv --csv-file data.csv --dry-run --debug

# Exécution réelle
pvw entity bulk-update-csv --csv-file data.csv --debug

# Avec gestion erreurs
pvw entity bulk-update-csv --csv-file data.csv --error-csv errors.csv --debug
```

## 📊 Exemples par cas d'usage

### Ajouter un département
```csv
guid,businessMetadata.department
abc-123,Sales
def-456,Marketing
```

### Classifier les données
```csv
guid,customAttributes.classification,customAttributes.sensitivity
abc-123,PII,HIGH
def-456,PUBLIC,LOW
```

### Enrichir avec métadonnées source
```csv
guid,sourceSystem,refreshFrequency,lastRefreshDate
abc-123,SAP,DAILY,2025-12-18
def-456,Salesforce,HOURLY,2025-12-18
```

## 🔍 Notation pointée

| CSV | Résultat JSON |
|-----|---------------|
| `myAttr` | `attributes: { myAttr }` |
| `businessMetadata.dept` | `attributes: { businessMetadata: { dept } }` |
| `customAttributes.class` | `attributes: { customAttributes: { class } }` |

## ✅ Tests

Exécuter la suite de tests :
```bash
python tests\test_bulk_update_custom_attributes.py
```

Résultat attendu :
```
✓ Test 1: Simple Attributes
✓ Test 2: Custom Attributes
✓ Test 3: Business Metadata (Nested)
✓ Test 4: Custom Attributes Section
✓ Test 5: Mixed Attributes
✓ Test 6: Mapping with GUID (Partial Update)
✓ Test 7: CSV Processing
```

## 🆘 Support

### Documentation complète
Pour plus de détails, consultez le guide complet :
```
doc/guides/CUSTOM_METADATA_HOWTO.md
```

### Quick reference
Pour une référence rapide :
```
doc/guides/custom-metadata-quickref.md
```

### Aide en ligne
```bash
pvw entity bulk-update-csv --help
```

## 🎉 Résumé

✅ L'option `--debug` fonctionne maintenant  
✅ Support complet des métadonnées personnalisées  
✅ Documentation complète et exemples  
✅ Tests validés  

**Prêt à utiliser !**
