# Synchronisation des Termes : Unified Catalog → Glossaire Classique

## Vue d'ensemble

La commande `pvw uc term sync-classic` permet de synchroniser les termes du **Unified Catalog** (métadonnées métier) vers les **glossaires classiques** de Microsoft Purview. Cette fonctionnalité crée un pont entre les deux systèmes de gestion de vocabulaire métier.

### Cas d'usage

- **Migration progressive** : Transition du Unified Catalog vers les glossaires classiques
- **Interopérabilité** : Maintenir les termes dans les deux systèmes simultanément
- **Intégration** : Permettre aux systèmes legacy d'accéder aux termes UC via les glossaires classiques
- **Conformité** : Assurer la cohérence entre les deux référentiels de données

## Architecture

```
┌─────────────────────────────────┐
│  Unified Catalog (UC)           │
│  ├─ Governance Domains          │
│  └─ Business Metadata Terms     │
└────────────┬────────────────────┘
             │ Synchronisation
             │ (pvw uc term sync-classic)
             ↓
┌─────────────────────────────────┐
│  Glossaires Classiques          │
│  ├─ Glossaries                  │
│  ├─ Terms                       │
│  └─ Categories                  │
└─────────────────────────────────┘
```

## Syntaxe

```bash
pvw uc term sync-classic [OPTIONS]
```

### Options principales

| Option | Description | Requis |
|--------|-------------|---------|
| `--domain-id TEXT` | GUID du domaine UC à synchroniser | Non* |
| `--glossary-guid TEXT` | GUID du glossaire cible | Non** |
| `--create-glossary` | Créer le glossaire s'il n'existe pas | Non |
| `--dry-run` | Mode prévisualisation (aucune modification) | Non |
| `--update-existing` | Mettre à jour les termes existants | Non |

\* Si non fourni, synchronise tous les domaines  
\** Si non fourni, utilise/crée un glossaire avec le nom du domaine

## Exemples d'utilisation

### 1. Synchronisation simple d'un domaine

Synchroniser tous les termes d'un domaine vers son glossaire correspondant :

```bash
pvw uc term sync-classic --domain-id "abc-123-def-456"
```

**Résultat** :
- Recherche un glossaire portant le même nom que le domaine
- Crée les termes UC dans le glossaire classique
- Ignore les termes déjà existants

### 2. Prévisualisation (dry-run)

Voir ce qui sera synchronisé sans appliquer les modifications :

```bash
pvw uc term sync-classic --domain-id "abc-123-def-456" --dry-run
```

**Affichage** :
```
🔍 DRY RUN MODE - No changes will be made

Step 1: Fetching Unified Catalog terms...
✓ Found 15 UC term(s)

Step 2: Determining target glossary...
✓ Found existing glossary: Sales Domain (guid-123)

Step 3: Checking existing classic glossary terms...
✓ Found 3 existing term(s) in classic glossary

Step 4: Synchronizing terms...
   Would create: Customer
   Would create: Product
   ⊖ Skipping: Revenue (already exists)
   ...
```

### 3. Créer le glossaire automatiquement

Si le glossaire n'existe pas, le créer automatiquement :

```bash
pvw uc term sync-classic --domain-id "abc-123-def-456" --create-glossary
```

**Comportement** :
- Vérifie si un glossaire existe avec le nom du domaine
- Si absent, crée un nouveau glossaire automatiquement
- Synchronise ensuite les termes

### 4. Mettre à jour les termes existants

Synchroniser et mettre à jour les termes déjà présents dans le glossaire :

```bash
pvw uc term sync-classic --domain-id "abc-123-def-456" --update-existing
```

**Mise à jour** :
- Description
- Statut (Draft, Published, etc.)
- Acronymes/Abréviations

### 5. Synchronisation vers un glossaire spécifique

Synchroniser vers un glossaire particulier plutôt qu'utiliser le nom du domaine :

```bash
pvw uc term sync-classic \
  --domain-id "abc-123-def-456" \
  --glossary-guid "glossary-xyz-789"
```

### 6. Combinaison complète

Exemple avancé avec toutes les options :

```bash
pvw uc term sync-classic \
  --domain-id "abc-123-def-456" \
  --glossary-guid "glossary-xyz-789" \
  --update-existing \
  --dry-run
```

## Correspondance des champs

### UC Term → Classic Glossary Term

| Champ UC | Champ Glossaire Classique | Notes |
|----------|---------------------------|-------|
| `name` | `name` | Identique |
| `description` | `longDescription` | Description complète |
| `status` | `status` | Draft, Published, Archived |
| `acronyms[]` | `abbreviation` | Concaténés avec virgule |
| `contacts.owner[]` | `experts[]` | Conversion des propriétaires |
| `domain` | `anchor.glossaryGuid` | Référence au glossaire |

### Champs non synchronisés

Les champs suivants du UC ne sont **pas** synchronisés car ils n'ont pas d'équivalent direct :

- `resources[]` (liens additionnels)
- `parentId` (hiérarchie de termes UC)
- Attributs personnalisés UC

## Gestion des conflits

### Termes existants

**Par défaut** (sans `--update-existing`) :
- Les termes existants sont **ignorés**
- Message : `⊖ Skipping: TermName (already exists)`

**Avec `--update-existing`** :
- Les termes existants sont **mis à jour**
- Seules les propriétés modifiées sont appliquées

### Détection des doublons

La détection se fait par **nom de terme** (case-insensitive) :

```python
existing_terms[term_name.lower()] = term_guid
```

## Workflow recommandé

### Synchronisation initiale

```bash
# 1. Prévisualisation
pvw uc term sync-classic --domain-id <domain-id> --dry-run

# 2. Vérification du résultat attendu
# (Analyser la sortie)

# 3. Exécution réelle
pvw uc term sync-classic --domain-id <domain-id> --create-glossary
```

### Synchronisation régulière

```bash
# Mettre à jour les termes existants et créer les nouveaux
pvw uc term sync-classic \
  --domain-id <domain-id> \
  --update-existing
```

### Script d'automatisation (PowerShell)

```powershell
# sync-all-domains.ps1
$domains = @(
    "domain-sales-guid",
    "domain-marketing-guid",
    "domain-finance-guid"
)

foreach ($domainId in $domains) {
    Write-Host "Syncing domain: $domainId" -ForegroundColor Cyan
    
    pvw uc term sync-classic `
        --domain-id $domainId `
        --create-glossary `
        --update-existing
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR syncing domain $domainId" -ForegroundColor Red
    }
}

Write-Host "All domains synchronized!" -ForegroundColor Green
```

## Résolution des problèmes

### Erreur : "No target glossary found"

**Cause** : Aucun glossaire correspondant au domaine n'a été trouvé

**Solution** :
```bash
# Option 1 : Créer automatiquement
pvw uc term sync-classic --domain-id <id> --create-glossary

# Option 2 : Spécifier un glossaire existant
pvw uc term sync-classic --domain-id <id> --glossary-guid <guid>
```

### Erreur : "No Unified Catalog terms found"

**Cause** : Le domaine ne contient aucun terme

**Solution** :
1. Vérifier que le domain-id est correct
2. Vérifier que des termes existent dans le domaine UC :
   ```bash
   pvw uc term list --domain-id <domain-id>
   ```

### Échecs de création/mise à jour

**Cause** : Problèmes de permissions ou de format

**Solution** :
1. Activer le mode debug :
   ```bash
   $env:PURVIEWCLI_DEBUG = "1"
   pvw uc term sync-classic --domain-id <id>
   ```

2. Vérifier les permissions :
   - Data Curator (pour UC)
   - Data Curator (pour Glossaires classiques)

## Limitations

1. **Hiérarchie des termes** : La hiérarchie UC (parentId) n'est pas préservée dans les glossaires classiques
2. **Attributs personnalisés** : Les attributs UC spécifiques ne sont pas synchronisés
3. **Relations** : Les relations entre termes UC ne sont pas migrées
4. **Synchronisation unidirectionnelle** : UC → Classique uniquement (pas de sync inverse)

## Bonnes pratiques

### 1. Toujours tester avec --dry-run

```bash
pvw uc term sync-classic --domain-id <id> --dry-run
```

### 2. Utiliser des noms de domaine cohérents

Assurez-vous que le nom du domaine UC corresponde au glossaire classique souhaité.

### 3. Documenter les mappings

Conservez un fichier de mapping pour tracer quelle domaine UC correspond à quel glossaire :

```csv
Domain ID,Domain Name,Glossary GUID,Glossary Name
abc-123,Sales,xyz-456,Sales Glossary
def-789,Marketing,uvw-012,Marketing Terms
```

### 4. Planifier des synchronisations régulières

Utilisez Azure Automation ou un scheduler pour synchroniser périodiquement :

```bash
# Crontab Linux
0 2 * * * /path/to/sync-script.sh

# Windows Task Scheduler
# Exécuter tous les jours à 2h00
```

## Voir aussi

- [Guide d'authentification](authentication.md)
- [Documentation Unified Catalog](../commands/unified-catalog.md)
- [Documentation Glossary](../commands/glossary.md)
- [Diagramme : UC Intended Design](../diagrams/UC-Intended%20Design.mmd)

## Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation : `pvw uc term sync-classic --help`
- Mode debug : `$env:PURVIEWCLI_DEBUG = "1"`
