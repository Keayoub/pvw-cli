# Bulk Update CSV - Guide d'Utilisation

## Problèmes Résolus

### 1. ✅ Option `--debug` maintenant disponible
L'option `--debug` a été ajoutée à la commande `bulk-update-csv` pour permettre un diagnostic détaillé.

### 2. ✅ Support des attributs personnalisés
La fonction `map_flat_entity_to_purview_entity` a été améliorée pour supporter:
- Les attributs simples
- Les attributs personnalisés (custom attributes)
- Les attributs imbriqués avec notation pointée

## Utilisation

### Syntaxe de base
```bash
pvw entity bulk-update-csv --csv-file <fichier.csv> --batch-size 100 --dry-run --debug
```

### Options disponibles
- `--csv-file PATH` (requis): Chemin du fichier CSV
- `--batch-size INTEGER` (défaut: 100): Taille des lots de traitement
- `--dry-run`: Prévisualiser sans faire les changements
- `--error-csv PATH` (optionnel): Fichier CSV pour écrire les lignes échouées
- `--debug`: Mode debug avec logs détaillés

## Format du CSV

### Exemple 1: Mise à jour par GUID (recommandé pour les attributs partiels)
```csv
guid,displayName,description,customAttr1
aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee,My Asset,Description,Custom Value
bbbbbbbb-cccc-dddd-eeee-aaaaaaaaaaaa,Asset 2,Another description,Value 2
```

### Exemple 2: Attributs imbriqués avec notation pointée
```csv
guid,displayName,description,businessMetadata.department,businessMetadata.cost
aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee,Asset 1,Description,Sales,10000
bbbbbbbb-cccc-dddd-eeee-aaaaaaaaaaaa,Asset 2,Description,Marketing,5000
```

### Exemple 3: Création avec typeName et qualifiedName
```csv
typeName,qualifiedName,displayName,description,customAttr
DataSet,mydb.schema.table1@cluster,My Table,Table Description,Value1
DataSet,mydb.schema.table2@cluster,My Table 2,Table Description 2,Value2
```

## Format des attributs personnalisés supportés

### Attributs simples
```csv
guid,displayName,description
```
→ Créé: `attributes: { displayName, description }`

### Attributs personnalisés simples
```csv
guid,customAttr1,customAttr2
```
→ Créé: `attributes: { customAttr1, customAttr2 }`

### Attributs imbriqués (notation pointée)
```csv
guid,businessMetadata.department,businessMetadata.cost
```
→ Créé: `attributes: { businessMetadata: { department, cost } }`

### Attributs de section spéciale
```csv
guid,customAttributes.attrName
```
→ Créé: `attributes: { customAttributes: { attrName } }`

## Exemples de commandes

### Test avec affichage des détails
```bash
pvw entity bulk-update-csv --csv-file test.csv --dry-run --debug
```

### Mise à jour réelle avec logs détaillés
```bash
pvw entity bulk-update-csv --csv-file test.csv --debug
```

### Avec gestion des erreurs
```bash
pvw entity bulk-update-csv --csv-file test.csv --error-csv errors.csv --debug
```

### Avec contrôle de la taille des lots
```bash
pvw entity bulk-update-csv --csv-file test.csv --batch-size 50 --debug
```

## Logs Debug

Avec l'option `--debug`, vous verrez:
- Colonnes détectées du CSV
- Nombre total de lignes
- Première ligne du CSV
- Mode détecté (guid-based ou typeName-based)
- Chaque attribut ajouté
- Structure JSON complète envoyée à l'API
- Réponse API pour chaque batch

Exemple de sortie debug:
```
[DEBUG] CSV columns: ['guid', 'displayName', 'description', 'customAttr1']
[DEBUG] Total rows: 3
[DEBUG] First row:
{...}
[DEBUG] has_type_qn: False
[DEBUG] has_guid: True
[DEBUG] Batch 1 entities:
{...}
[DEBUG] Payload:
{...}
[DEBUG] API Result: {...}
```

## Dépannage

### Erreur: "No such option: --debug"
✅ Résolue! Assurez-vous que vous avez la dernière version du CLI.

### Attributs personnalisés non pris en compte
- Vérifiez que les noms de colonnes correspondent à vos attributs Purview
- Utilisez `--debug` pour voir comment les attributs sont mappés
- Vérifiez que les valeurs ne sont pas vides (NaN)

### Attributs imbriqués non fonctionnant
- Utilisez la notation pointée: `businessMetadata.department`
- Assurez-vous que les sections parentes existent dans Purview
- Testez d'abord avec `--dry-run` pour prévisualiser

## Notes importantes

1. **GUIDs requis pour les mises à jour partielles**: Si vous utilisez GUID, les updates sont partielles (seuls les attributs fournis sont modifiés)

2. **typeName + qualifiedName pour les créations**: Pour créer de nouvelles entités, fournissez ces deux champs

3. **NaN/None sont ignorés**: Les cellules vides ne sont pas envoyées à l'API

4. **Taille limite**: Purview limite les items à 2 MB chacun

5. **Batch processing**: Les grandes modifications sont traitées par lot pour éviter les timeouts
