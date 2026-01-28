# Guide d'Importation de Termes - Unified Catalog (UC)

Ce guide décrit comment utiliser la commande `pvw uc term import-csv` pour importer des termes de glossaire dans Microsoft Purview Unified Catalog avec toutes les fonctionnalités avancées.

## Nouvelles Fonctionnalités

### 1. Détection et Mise à Jour des Doublons

**Problème Résolu**: Auparavant, si vous importiez le même fichier CSV deux fois, les termes étaient créés en double même avec le même `term_id`.

**Solution**: Utiliser le flag `--update-existing`

```bash
pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN_ID> --update-existing
```

Avec ce flag:
- Avant de créer un terme, le système vérifie s'il existe déjà (par nom, dans le même domaine)
- Si le terme existe → **MISE À JOUR** au lieu de création
- Si le terme n'existe pas → **CRÉATION**

### 2. Hiérarchie des Termes (Parent Terms)

Vous pouvez maintenant créer une hiérarchie de termes en utilisant deux méthodes:

#### Méthode 1: Par Nom du Parent
```csv
name,description,parent_term_name
Produit,Catalogue produits,
Produit Alimentaire,Produits alimentaires,Produit
Produit Électronique,Produits électroniques,Produit
```

#### Méthode 2: Par ID du Parent
```csv
name,description,parent_term_id
Produit,Catalogue produits,
Sous-Produit,Sous-catégorie,a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Note**: Le système résout automatiquement les noms de parents en IDs lors de l'import.

### 3. Experts

Ajoutez des experts (en plus des propriétaires - owners) à vos termes:

```csv
name,description,owner_ids,experts
Client,Entité client,owner-guid-1,expert-guid-1;expert-guid-2;expert-guid-3
```

**Formats supportés**:
- GUIDs séparés par virgules: `guid1,guid2,guid3`
- GUIDs séparés par point-virgule: `guid1;guid2;guid3`
- Format UI Purview: `email:info;email:info`

### 4. Synonymes

Définissez des synonymes pour chaque terme:

```csv
name,synonyms
Client,"Customer,Consumer,Buyer"
Produit,"Item,SKU,Article,Product"
```

**Formats supportés**:
- Virgule: `syn1,syn2,syn3`
- Point-virgule: `syn1;syn2;syn3`

**Note**: Les synonymes sont maintenant pleinement supportés via l'API UC 2025-09-15-preview. Le système crée automatiquement les relations de type "Synonym" entre les termes.

### 5. Termes Associés (Related Terms)

Créez des liens entre termes liés:

#### Par Noms
```csv
name,related_terms
Client,"Commande,Facture,Adresse"
Commande,"Client,Produit,Paiement"
```

#### Par IDs
```csv
name,related_term_ids
Client,guid1,guid2,guid3
```

**Note**: Le système résout automatiquement les noms en IDs lors de l'import et crée les relations de type "Related" via l'API UC 2025-09-15-preview.

## Format CSV Complet

Voici un exemple de fichier CSV avec tous les champs disponibles:

```csv
name,description,status,acronyms,owner_ids,experts,synonyms,parent_term_name,related_terms,customAttributes.DataGovernance.Classification
Client,Entité client,Published,CLT,owner-guid,expert-guid-1;expert-guid-2,"Customer,Consumer",,Partie Prenante,PII
Produit,Catalogue produit,Draft,PRD,owner-guid,expert-guid,"Item,SKU",,Client,NON_PII
Commande,Transaction achat,Published,CMD,owner-guid,expert-guid,"Order,Purchase",Transaction,"Client;Produit",TRANSACTIONAL
```

### Champs Standards

| Champ | Obligatoire | Description | Exemple |
|-------|-------------|-------------|---------|
| `name` ou `Name` | ✅ Oui | Nom du terme | `Client` |
| `description` ou `Definition` | ❌ Non | Description du terme | `Entité représentant un client` |
| `status` ou `Status` | ❌ Non | Statut (Draft, Published, Archived) | `Published` |
| `acronyms` ou `Acronym` | ❌ Non | Acronymes (séparés par virgule) | `CLT,CUST` |
| `owner_ids` | ❌ Non | GUIDs des propriétaires (séparés par virgule) | `guid1,guid2` |

### Nouveaux Champs

| Champ | Description | Format | Exemple |
|-------|-------------|--------|---------|
| `experts` ou `Experts` | GUIDs des experts | Virgule ou point-virgule | `guid1;guid2` |
| `synonyms` ou `Synonyms` | Synonymes du terme | Virgule ou point-virgule | `Client,Customer,Consumer` |
| `parent_term_name` ou `Parent Term Name` | Nom du terme parent | Texte | `Business Terms` |
| `parent_term_id` | GUID du terme parent | GUID | `a1b2c3d4-...` |
| `related_terms` ou `Related Terms` | Noms des termes liés | Virgule ou point-virgule | `Order,Invoice` |
| `related_term_ids` | GUIDs des termes liés | Virgule | `guid1,guid2` |

### Attributs Personnalisés (Custom Attributes)

Utilisez la notation par points pour créer des attributs personnalisés:

```csv
name,customAttributes.Glossaire.Reference,customAttributes.DataQuality.Score
Client,REF-001,95
Produit,REF-002,88
```

Cela crée la structure JSON suivante:
```json
{
  "Glossaire": {
    "Reference": "REF-001"
  },
  "DataQuality": {
    "Score": "95"
  }
}
```

## Commandes

### Import Basique
```bash
pvw uc term import-csv \
  --csv-file terms.csv \
  --domain-id <DOMAIN_GUID>
```

### Import avec Mise à Jour des Doublons
```bash
pvw uc term import-csv \
  --csv-file terms.csv \
  --domain-id <DOMAIN_GUID> \
  --update-existing
```

### Aperçu Sans Import (Dry Run)
```bash
pvw uc term import-csv \
  --csv-file terms.csv \
  --domain-id <DOMAIN_GUID> \
  --dry-run
```

### Import avec Debugging
```bash
pvw uc term import-csv \
  --csv-file terms.csv \
  --domain-id <DOMAIN_GUID> \
  --debug
```

### Import avec Tout
```bash
pvw uc term import-csv \
  --csv-file terms.csv \
  --domain-id <DOMAIN_GUID> \
  --update-existing \
  --debug
```

## Exemples de Fichiers

### Exemple 1: Import Simple
`samples/csv/uc_terms_simple.csv`
```csv
name,description,status
Client,Entité client,Draft
Produit,Catalogue produit,Published
```

### Exemple 2: Import avec Hiérarchie
`samples/csv/uc_terms_hierarchy.csv`
```csv
name,description,parent_term_name
Business Terms,Termes métier racine,
Client,Entité client,Business Terms
Produit,Catalogue produit,Business Terms
```

### Exemple 3: Import Complet
`samples/csv/uc_terms_import_example_complete.csv`
- Inclut tous les champs disponibles
- Démontre la hiérarchie
- Montre les synonymes
- Inclut les termes liés
- Utilise les attributs personnalisés

## Résolution de Problèmes

### Les Termes Sont Créés en Double

**Solution**: Utilisez le flag `--update-existing` lors de l'import:
```bash
pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN> --update-existing
```

### Le Terme Parent N'est Pas Trouvé

**Cause**: Le terme parent doit exister avant de pouvoir être assigné.

**Solution**: Importez d'abord les termes parents, puis les termes enfants:
```bash
# Import 1: Termes parents
pvw uc term import-csv --csv-file parents.csv --domain-id <DOMAIN>

# Import 2: Termes enfants avec parent_term_name
pvw uc term import-csv --csv-file children.csv --domain-id <DOMAIN>
```

### Les Experts Ne Sont Pas Ajoutés

**Cause**: Les emails ne sont pas supportés, seuls les GUIDs Entra ID fonctionnent.

**Solution**: Récupérez les GUIDs Entra Object ID des utilisateurs:
```bash
# Via Azure CLI
az ad user show --id user@company.com --query id -o tsv

# Ou via PowerShell
Get-AzADUser -UserPrincipalName user@company.com | Select-Object Id
```

### Les Attributs Personnalisés Ne Sont Pas Visibles

**Cause**: Les attributs personnalisés doivent être définis dans le schéma UC avant utilisation.

**Solution**: Créez d'abord le schéma d'attributs personnalisés dans Purview UI, puis importez les termes.

## Limites Connues

1. **Experts**: La structure des contacts UC peut nécessiter des GUIDs Entra Object ID (emails non supportés)
2. **Ordre de création**: Les termes parents et les termes référencés (synonyms, related) doivent exister avant la liaison

## Flux de Travail Recommandé

1. **Préparation**
   - Créez votre domaine UC
   - Définissez les attributs personnalisés dans Purview UI
   - Récupérez les GUIDs des utilisateurs (owners, experts)

2. **Import Initial**
   ```bash
   pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN> --dry-run
   ```
   Vérifiez l'aperçu avant l'import réel.

3. **Import Réel**
   ```bash
   pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN>
   ```

4. **Mises à Jour Ultérieures**
   ```bash
   pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN> --update-existing
   ```

## Support

Pour des questions ou des problèmes, consultez:
- [README principal](../../README.md)
- [Documentation des commandes UC](../../doc/commands/unified-catalog.md)
- GitHub Issues: https://github.com/Keayoub/pvw-cli/issues
