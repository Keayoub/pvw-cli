# Correctifs apportés au bulk-update-csv

## Date: 18 décembre 2025

## Problèmes résolus

### ✅ 1. Option `--debug` manquante
**Problème**: La commande `pvw entity bulk-update-csv --debug` retournait l'erreur:
```
Error: No such option: --debug
```

**Solution**: 
- Ajouté l'option `--debug` comme paramètre Click dans la commande `bulk_update_csv`
- Ajouté du logging détaillé à plusieurs points clés:
  - Informations du CSV (colonnes, nombre de lignes, première ligne)
  - Mode de traitement détecté (guid vs typeName)
  - Structure des payloads envoyés à l'API
  - Réponses de l'API Purview
  - Exceptions détaillées

**Fichiers modifiés**:
- [purviewcli/cli/entity.py](purviewcli/cli/entity.py#L1691)

### ✅ 2. Support des attributs personnalisés dans le bulk update
**Problème**: Les attributs personnalisés dans le CSV n'étaient pas correctement supportés lors du bulk update de termes/entités.

**Solution**: 
- Amélioré la fonction `map_flat_entity_to_purview_entity` pour supporter:
  - **Attributs simples**: `displayName`, `description`, etc.
  - **Attributs personnalisés**: n'importe quel nom de colonne
  - **Attributs imbriqués avec notation pointée**:
    - `businessMetadata.department` → `{"businessMetadata": {"department": "value"}}`
    - `customAttributes.attrName` → `{"customAttributes": {"attrName": "value"}}`
  - **Gestion améliorée des GUIDs**: Le GUID est maintenant extrait et ajouté au niveau racine de l'entité
  - **Mode debug optionnel**: Affichage détaillé de chaque attribut mappé

**Fichiers modifiés**:
- [purviewcli/client/_entity.py](purviewcli/client/_entity.py#L22)

## Améliorations techniques

### Fonction `map_flat_entity_to_purview_entity`

**Avant**:
```python
def map_flat_entity_to_purview_entity(row):
    # Version simple: tous les attributs mis à plat
    attrs = {}
    for k, v in data.items():
        attrs[k] = v
    return {"typeName": type_name, "attributes": attrs}
```

**Après**:
```python
def map_flat_entity_to_purview_entity(row, debug=False):
    # Support:
    # - Attributs simples
    # - Notation pointée pour attributs imbriqués
    # - Sections spéciales (businessMetadata, customAttributes)
    # - GUID au niveau racine
    # - Mode debug pour diagnostic
```

### Nouvelles capacités CSV

#### Format 1: GUID + Attributs simples
```csv
guid,displayName,description,customAttr1
abc-123,Asset Name,Description,Custom Value
```

#### Format 2: GUID + Attributs imbriqués
```csv
guid,displayName,businessMetadata.department,businessMetadata.cost
abc-123,Asset Name,Sales,10000
```

#### Format 3: GUID + Sections spéciales
```csv
guid,displayName,customAttributes.classification
abc-123,Asset Name,CONFIDENTIAL
```

## Tests créés

### Test unitaire complet
- **Fichier**: [tests/test_bulk_update_custom_attributes.py](tests/test_bulk_update_custom_attributes.py)
- **7 scénarios de test**:
  1. Attributs simples
  2. Attributs personnalisés
  3. Business metadata (imbriqué)
  4. Section customAttributes
  5. Mix de tous les types
  6. Mapping avec GUID
  7. Traitement CSV complet

### CSV d'exemple
- **Fichier**: [samples/csv/test_bulk_update_custom_attrs.csv](samples/csv/test_bulk_update_custom_attrs.csv)
- Exemple pratique avec GUID, displayName, description, et attributs imbriqués

### Documentation
- **Fichier**: [doc/guides/bulk-update-custom-attributes.md](doc/guides/bulk-update-custom-attributes.md)
- Guide complet avec:
  - Syntaxe des commandes
  - Formats CSV supportés
  - Exemples d'utilisation
  - Dépannage

## Utilisation

### Commande de base
```bash
pvw entity bulk-update-csv --csv-file mon_fichier.csv --debug
```

### Test en mode dry-run
```bash
pvw entity bulk-update-csv --csv-file mon_fichier.csv --dry-run --debug
```

### Avec gestion des erreurs
```bash
pvw entity bulk-update-csv --csv-file mon_fichier.csv --error-csv erreurs.csv --debug
```

## Exemples de logs debug

```
[DEBUG] CSV columns: ['guid', 'displayName', 'description', 'customAttr1']
[DEBUG] Total rows: 3
[DEBUG] First row:
{'guid': 'aaaaa...', 'displayName': 'Asset 1', ...}
[DEBUG] has_type_qn: False
[DEBUG] has_guid: True
[DEBUG] Batch 1 entities:
[
  {
    "typeName": null,
    "attributes": {
      "displayName": "Asset 1",
      "description": "Description",
      "customAttr1": "Value"
    },
    "guid": "aaaaa..."
  }
]
[DEBUG] Payload:
{
  "entities": [...]
}
[DEBUG] API Result: {...}
```

## Tests de validation

Tous les tests passent ✅:
```
✓ Test 1: Simple Attributes
✓ Test 2: Custom Attributes
✓ Test 3: Business Metadata (Nested)
✓ Test 4: Custom Attributes Section
✓ Test 5: Mixed Attributes
✓ Test 6: Mapping with GUID (Partial Update)
✓ Test 7: CSV Processing
```

## Bénéfices

1. **Diagnostic facilité**: L'option `--debug` permet de voir exactement ce qui est envoyé à l'API
2. **Plus de flexibilité**: Support complet des attributs personnalisés et imbriqués
3. **Meilleure compatibilité**: Fonctionne avec n'importe quel type d'attribut Purview
4. **Documentation**: Guide complet et exemples pratiques
5. **Testable**: Suite de tests unitaires pour garantir la qualité

## Prochaines étapes possibles

- [ ] Ajouter support pour les classifications dans le CSV
- [ ] Ajouter support pour les relations dans le CSV
- [ ] Améliorer la gestion d'erreurs avec retry automatique
- [ ] Ajouter un mode de validation du CSV avant exécution
