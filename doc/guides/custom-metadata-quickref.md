# 📋 Guide Rapide - Custom Metadata

## Formats CSV

### ✅ Attributs simples
```csv
guid,displayName,myCustomAttr
abc-123,Asset Name,Custom Value
```

### ✅ Business Metadata
```csv
guid,businessMetadata.department,businessMetadata.owner
abc-123,Sales,owner@company.com
```

### ✅ Custom Attributes Section
```csv
guid,customAttributes.classification
abc-123,CONFIDENTIAL
```

### ✅ Mix complet
```csv
guid,displayName,customField,businessMetadata.dept,customAttributes.class
abc-123,Name,Value,Sales,CONFIDENTIAL
```

## Commandes essentielles

### Preview (recommandé)
```bash
pvw entity bulk-update-csv --csv-file data.csv --dry-run --debug
```

### Exécution réelle
```bash
pvw entity bulk-update-csv --csv-file data.csv --debug
```

### Avec gestion erreurs
```bash
pvw entity bulk-update-csv --csv-file data.csv --error-csv errors.csv --debug
```

### Lots personnalisés
```bash
pvw entity bulk-update-csv --csv-file data.csv --batch-size 50 --debug
```

## Notation pointée

| CSV Column | Résultat JSON |
|------------|---------------|
| `myAttr` | `attributes: { myAttr }` |
| `businessMetadata.dept` | `attributes: { businessMetadata: { dept } }` |
| `customAttributes.class` | `attributes: { customAttributes: { class } }` |

## Options CLI

| Option | Description |
|--------|-------------|
| `--csv-file` | Chemin du CSV (requis) |
| `--dry-run` | Preview sans modification |
| `--debug` | Logs détaillés |
| `--batch-size` | Taille des lots (défaut: 100) |
| `--error-csv` | Fichier pour lignes échouées |

## Exemples pratiques

### Ajouter département
```csv
guid,businessMetadata.department
abc-123,Sales
def-456,Marketing
```

### Classifier données
```csv
guid,customAttributes.classification,customAttributes.sensitivity
abc-123,PII,HIGH
def-456,PUBLIC,LOW
```

### Enrichir métadonnées
```csv
guid,displayName,description,sourceSystem,refreshFrequency
abc-123,My Dataset,Description,SAP,DAILY
```

## Dépannage rapide

### ❌ "No such option: --debug"
→ Réinstaller: `pip install -e .`

### ❌ Attributs non appliqués
→ Vérifier avec `--debug` les noms exacts

### ❌ Business Metadata non créé
→ Vérifier que le template existe dans Purview

### ❌ Timeout sur gros fichiers
→ Réduire `--batch-size` (ex: 25)

## Vérification

### Lire après update
```bash
pvw entity read --guid abc-123
```

### Voir business metadata
```bash
pvw entity read --guid abc-123 | grep -A 10 "businessMetadata"
```

## Ressources

- **Guide complet**: `doc/guides/custom-metadata-management.md`
- **Tests**: `tests/test_bulk_update_custom_attributes.py`
- **Exemples**: `samples/csv/`
- **Demo**: `samples/demo_custom_metadata.ps1`
