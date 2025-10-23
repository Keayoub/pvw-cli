# Lineage CSV Import Guide

## Vue d'ensemble

La fonctionnalité `lineage import` permet d'importer des relations de traçabilité (lineage) à partir d'un fichier CSV. Cette fonctionnalité est utile pour automatiser la création de flux de données dans Microsoft Purview.

## Format CSV Requis

Le fichier CSV doit contenir au minimum les colonnes suivantes :

### Colonnes obligatoires
- `source_entity_guid` : GUID de l'entité source
- `target_entity_guid` : GUID de l'entité cible

### Colonnes optionnelles
- `relationship_type` : Type de relation (par défaut: "Process")
- `process_name` : Nom du processus de transformation
- `description` : Description de la transformation
- `confidence_score` : Score de confiance (0-1)
- `owner` : Propriétaire du processus
- `metadata` : Métadonnées JSON additionnelles

## Format Alternatif (Qualified Names)

Vous pouvez aussi utiliser des qualified names au lieu de GUIDs :

- `source_qualified_name` : Qualified name de l'entité source
- `target_qualified_name` : Qualified name de l'entité cible
- `source_type` : Type de l'entité source (ex: "azure_sql_table")
- `target_type` : Type de l'entité cible

## Exemples

### Exemple 1 : CSV avec GUIDs

```csv
source_entity_guid,target_entity_guid,relationship_type,process_name,description,confidence_score,owner,metadata
dcfc99ed-c74d-49aa-bd0b-72f6f6f60000,1db9c650-acfb-4914-8bc5-1cf6f6f60000,Process,Transform_Product_Data,Transform product data for analytics,0.95,data-engineering,"{""tool"": ""Azure Data Factory""}"
```

### Exemple 2 : CSV avec Qualified Names

```csv
source_qualified_name,target_qualified_name,source_type,target_type,process_name,description
mssql://server/database/schema/source_table,mssql://server/database/schema/target_table,azure_sql_table,azure_sql_table,ETL_Transform,Extract Transform Load process
```

## Commandes Disponibles

### 1. Valider un fichier CSV

Valide le format et le contenu du fichier CSV sans faire d'appels API :

```bash
pvw lineage validate trace.csv
```

**Résultat attendu :**
```
SUCCESS: Lineage validation passed: trace.csv (1 rows, columns: source_entity_guid, target_entity_guid, relationship_type, process_name, description, confidence_score, owner, metadata)
```

### 2. Importer le lineage

Importe les relations de traçabilité dans Purview :

```bash
pvw lineage import trace.csv
```

**Résultat attendu :**
```
SUCCESS: Lineage import completed successfully
{
  "entities": [...],
  "relationships": [...]
}
```

### 3. Générer un fichier d'exemple

Génère un fichier CSV d'exemple :

```bash
pvw lineage sample lineage_sample.csv
```

### 4. Voir les templates disponibles

Affiche les différents templates de CSV disponibles :

```bash
pvw lineage templates
```

## Flux de Travail Recommandé

1. **Créer un fichier CSV** avec vos GUIDs d'entités
   ```bash
   # Utilisez search find-table pour obtenir les GUIDs
   pvw search find-table --name "Product" --schema "dbo" --id-only
   ```

2. **Valider le fichier**
   ```bash
   pvw lineage validate trace.csv
   ```

3. **Importer en production**
   ```bash
   pvw lineage import trace.csv
   ```

## Notes Importantes

⚠️ **Format des GUIDs**
- Les GUIDs doivent être au format standard : `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- Vous pouvez utiliser le préfixe `guid=` mais il sera automatiquement nettoyé
- Les guillemets seront automatiquement supprimés

⚠️ **Types d'entités**
- Par défaut, le type "DataSet" est utilisé pour les entités source/cible
- Vous pouvez spécifier un type personnalisé avec `source_type` et `target_type`

⚠️ **Métadonnées JSON**
- Les métadonnées doivent être au format JSON valide
- Utilisez des doubles guillemets échappés : `"{""key"": ""value""}"`

## Dépannage

### Erreur : "Missing required columns"
**Solution :** Vérifiez que votre CSV contient soit `(source_entity_guid, target_entity_guid)` soit `(source_qualified_name, target_qualified_name)`

### Erreur : "Invalid GUID format"
**Solution :** Vérifiez que vos GUIDs respectent le format standard. Utilisez la commande `validate` pour identifier les GUIDs invalides.

### Erreur : "Entity not found"
**Solution :** Vérifiez que les entités source et cible existent dans Purview avant de créer le lineage.

## Exemples Avancés

### Exemple avec plusieurs transformations

```csv
source_entity_guid,target_entity_guid,relationship_type,process_name,description,owner
guid-source-1,guid-intermediate-1,Process,Step1_Extract,Extract from source,data-eng
guid-intermediate-1,guid-intermediate-2,Process,Step2_Transform,Transform data,data-eng
guid-intermediate-2,guid-target-1,Process,Step3_Load,Load to target,data-eng
```

### Exemple avec métadonnées complexes

```csv
source_entity_guid,target_entity_guid,process_name,metadata
guid-1,guid-2,ETL_Process,"{""tool"": ""ADF"", ""schedule"": ""daily"", ""retries"": 3}"
```

## Ressources

- [Documentation officielle Microsoft Purview Lineage API](https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/lineage)
- [Fichiers d'exemple](../../samples/csv/lineage_sample.csv)
- [Guide de traçabilité](./lineage-guide.md)
