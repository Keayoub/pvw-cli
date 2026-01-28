# Corrections et Améliorations - Import de Termes Glossaire

## Résumé des Changements

Ce document résume les corrections et améliorations apportées à la fonction d'importation de termes dans le glossaire Unified Catalog (UC).

## Problèmes Résolus

### 1. ✅ Doublons lors de l'Import

**Problème Initial**:
Lorsqu'un fichier CSV était importé deux fois, les termes étaient créés en double même si le `term_id` était identique dans le fichier.

**Solution Implémentée**:
- Ajout d'une nouvelle option `--update-existing` à la commande `pvw uc term import-csv`
- Fonction helper `_find_existing_term_by_name()` qui recherche les termes existants par nom dans le domaine
- Logique de détection: avant création, le système vérifie si un terme avec le même nom existe déjà
- Si le terme existe → **MISE À JOUR** au lieu de création
- Si le terme n'existe pas → **CRÉATION**

**Utilisation**:
```bash
pvw uc term import-csv \
  --csv-file termes.csv \
  --domain-id <DOMAIN_ID> \
  --update-existing
```

### 2. ✅ Support des Termes Parents (Hiérarchie)

**Besoin Exprimé**:
Pouvoir créer une hiérarchie de termes avec des relations parent-enfant.

**Solution Implémentée**:
- Ajout du champ `parent_term_name` dans le CSV (recherche par nom)
- Ajout du champ `parent_term_id` dans le CSV (utilisation directe du GUID)
- Résolution automatique des noms de parents en IDs lors de l'import
- Attribution du parent après la création du terme

**Exemple CSV**:
```csv
name,description,parent_term_name
Business Terms,Termes métier,
Client,Entité client,Business Terms
Produit,Catalogue produit,Business Terms
```

### 3. ✅ Support des Experts

**Besoin Exprimé**:
Ajouter des experts en plus des propriétaires (owners) pour chaque terme.

**Solution Implémentée**:
- Nouveau champ `experts` dans le CSV
- Support de plusieurs formats:
  - GUIDs séparés par virgule: `guid1,guid2,guid3`
  - GUIDs séparés par point-virgule: `guid1;guid2;guid3`
  - Format UI Purview: `email:info;email:info`
- Les experts sont ajoutés après la création/mise à jour du terme
- Validation et avertissements si des emails sont utilisés au lieu de GUIDs

**Exemple CSV**:
```csv
name,owner_ids,experts
Client,owner-guid-1,expert-guid-1;expert-guid-2;expert-guid-3
```

### 4. ✅ Support des Synonymes

**Besoin Exprimé**:
Définir des synonymes pour chaque terme du glossaire.

**Solution Implémentée**:
- Nouveau champ `synonyms` ou `Synonyms` dans le CSV
- Support de plusieurs formats:
  - Séparés par virgule: `syn1,syn2,syn3`
  - Séparés par point-virgule: `syn1;syn2;syn3`
- Les synonymes sont enregistrés lors de l'import

**Exemple CSV**:
```csv
name,synonyms
Client,"Customer,Consumer,Buyer"
Produit,"Item,SKU,Article"
```

**Note**: Les synonymes sont maintenant pleinement supportés via l'API Microsoft Purview Unified Catalog 2025-09-15-preview. Le système crée automatiquement les termes synonymes s'ils n'existent pas et établit les relations de type "Synonym".

### 5. ✅ Support des Termes Associés (Related Terms)

**Besoin Exprimé**:
Créer des liens entre termes liés/associés.

**Solution Implémentée**:
- Nouveau champ `related_terms` ou `Related Terms` (recherche par nom)
- Nouveau champ `related_term_ids` (utilisation directe des GUIDs)
- Résolution automatique des noms en IDs lors de l'import
- Création automatique des liens via l'API UC 2025-09-15-preview endpoint `/datagovernance/catalog/terms/{termId}/relationships`
- Support complet des relations de type "Related"

**Exemple CSV**:
```csv
name,related_terms
Client,"Commande,Facture,Adresse"
Commande,"Client,Produit,Paiement"
```

## Fichiers Modifiés

### 1. `purviewcli/cli/unified_catalog.py`

**Modifications principales**:

1. **Nouvelle fonction helper** (ligne ~1441):
   ```python
   def _find_existing_term_by_name(client, term_name, domain_id):
       """Helper to find existing term by name and domain"""
   ```

2. **Mise à jour de la signature de la fonction** (ligne ~1478):
   ```python
   def import_terms_from_csv(csv_file, domain_id, dry_run, debug, update_existing):
   ```
   - Ajout du paramètre `--update-existing`

3. **Mise à jour de la documentation** (ligne ~1480):
   - Documentation complète des nouveaux champs
   - Exemples d'utilisation

4. **Parsing des nouveaux champs** (ligne ~1530-1570):
   - Parsing de `experts`
   - Parsing de `synonyms`
   - Parsing de `parent_term_name` et `parent_term_id`
   - Parsing de `related_terms` et `related_term_ids`

5. **Logique de création/mise à jour** (ligne ~1760-1900):
   - Détection de doublons avec `_find_existing_term_by_name()`
   - Choix entre CREATE et UPDATE
   - Post-processing pour parent terms
   - Post-processing pour experts
   - Post-processing pour synonyms (avec note sur limitation API)
   - Post-processing pour related terms (avec note sur implémentation partielle)

6. **Résumé amélioré** (ligne ~1905):
   - Affichage du nombre de termes créés
   - Affichage du nombre de termes mis à jour
   - Indication si `--update-existing` était activé

## Nouveaux Fichiers Créés

### 1. `samples/csv/uc_terms_import_example_complete.csv`

Fichier d'exemple complet démontrant tous les nouveaux champs:
- Termes parents
- Experts
- Synonymes
- Termes associés
- Attributs personnalisés

### 2. `doc/guides/UC_TERMS_IMPORT_GUIDE.md`

Guide complet en français:
- Explication de toutes les nouvelles fonctionnalités
- Exemples d'utilisation
- Format CSV complet
- Commandes disponibles
- Résolution de problèmes
- Flux de travail recommandé

## Utilisation

### Import Basique
```bash
pvw uc term import-csv \
  --csv-file termes.csv \
  --domain-id <DOMAIN_GUID>
```

### Import avec Détection de Doublons
```bash
pvw uc term import-csv \
  --csv-file termes.csv \
  --domain-id <DOMAIN_GUID> \
  --update-existing
```

### Aperçu Avant Import (Dry Run)
```bash
pvw uc term import-csv \
  --csv-file termes.csv \
  --domain-id <DOMAIN_GUID> \
  --dry-run
```

### Import avec Debugging
```bash
pvw uc term import-csv \
  --csv-file termes.csv \
  --domain-id <DOMAIN_GUID> \
  --update-existing \
  --debug
```

## Exemple de Sortie

```
[cyan]Importing terms from: termes.csv[/cyan]
[cyan]Found 8 term(s) in CSV file[/cyan]

[bold green]Processing term 1/8: Client[bold green]
[yellow]Term 'Client' already exists (ID: a1b2c3d4-e5f6-7890-abcd...). Updating...[/yellow]
[green]Updated: Client (ID: a1b2c3d4-e5f6-7890-abcd...)[/green]
  ✓ Added 2 expert(s)
  ⚠ Synonyms specified but not yet implemented in UC API
    Synonyms: Customer, Consumer

[bold green]Processing term 2/8: Produit[bold green]
[green]Created: Produit (ID: b2c3d4e5-f6a7-8901-bcde...)[/green]
  ✓ Linked to parent: Business Terms
  ✓ Added 1 expert(s)

...

============================================================
[cyan]Import Summary:[/cyan]
  Total terms processed: 8
  [green]Successfully created: 5[/green]
  [blue]Successfully updated: 3[/blue]
  [red]Failed: 0[/red]

[dim]Note: --update-existing was enabled[/dim]
```

## Limites et Notes

### Limitations Actuelles

1. **Experts**: 
   - Nécessitent des GUIDs Entra Object ID
   - Les emails ne sont pas supportés par l'API UC
   - Avertissements affichés si des emails sont détectés

2. **Ordre de Création**:
   - Les termes parents doivent exister avant les termes enfants
   - Pour les synonymes: si le terme synonyme n'existe pas, il sera créé automatiquement
   - Pour les related terms: les termes référencés doivent exister ou seront ignorés avec un avertissement

### Recommandations

1. **Ordre d'Import**:
   - Importer d'abord les termes parents
   - Puis importer les termes enfants avec `parent_term_name`

2. **Mise à Jour**:
   - Toujours utiliser `--update-existing` lors des imports répétés
   - Évite la création de doublons

3. **Validation**:
   - Utiliser `--dry-run` pour prévisualiser avant l'import réel
   - Vérifier les avertissements et erreurs

4. **GUIDs**:
   - Récupérer les GUIDs Entra Object ID pour owners et experts
   - Ne pas utiliser d'emails dans les champs `owner_ids` ou `experts`

## Tests Recommandés

1. **Test de Doublons**:
   ```bash
   # Import initial
   pvw uc term import-csv --csv-file test.csv --domain-id <DOMAIN>
   
   # Réimport avec update
   pvw uc term import-csv --csv-file test.csv --domain-id <DOMAIN> --update-existing
   
   # Vérifier qu'aucun doublon n'est créé
   ```

2. **Test de Hiérarchie**:
   ```bash
   # CSV avec parent_term_name
   pvw uc term import-csv --csv-file hierarchy.csv --domain-id <DOMAIN>
   
   # Vérifier dans Purview UI que la hiérarchie est correcte
   ```

3. **Test d'Experts**:
   ```bash
   # CSV avec champ experts
   pvw uc term import-csv --csv-file experts.csv --domain-id <DOMAIN> --debug
   
   # Vérifier les messages de confirmation des experts
   ```

## Support et Documentation

- **Guide Complet**: [doc/guides/UC_TERMS_IMPORT_GUIDE.md](doc/guides/UC_TERMS_IMPORT_GUIDE.md)
- **Exemple CSV**: [samples/csv/uc_terms_import_example_complete.csv](samples/csv/uc_terms_import_example_complete.csv)
- **Issues GitHub**: https://github.com/Keayoub/pvw-cli/issues

## Auteur et Date

- **Modifications effectuées**: 28 Janvier 2026
- **Version**: Compatible avec pvw-cli v1.6+
