# Guide de test : Synchronisation UC → Glossaire Classique

Ce document explique comment tester la nouvelle fonctionnalité de synchronisation.

## Prérequis

- ✅ Purview CLI installé et configuré
- ✅ Authentification Azure fonctionnelle
- ✅ Permissions Data Curator sur Purview
- ✅ Au moins un domaine UC avec des termes

## Vérification rapide

### 1. Vérifier que la commande existe

```bash
pvw uc term --help
```

Vous devriez voir `sync-classic` dans la liste des commandes.

### 2. Afficher l'aide de la commande

```bash
pvw uc term sync-classic --help
```

Vérifiez que toutes les options sont affichées :
- `--domain-id`
- `--glossary-guid`
- `--create-glossary`
- `--dry-run`
- `--update-existing`

## Tests unitaires

### Test 1 : Dry-run basique

**Objectif** : Vérifier que le mode prévisualisation fonctionne

```bash
# Remplacer <domain-guid> par un vrai GUID de domaine
pvw uc term sync-classic --domain-id "<domain-guid>" --dry-run
```

**Résultat attendu** :
```
═══════════════════════════════════════════════════════════
  Unified Catalog → Classic Glossary Sync  
═══════════════════════════════════════════════════════════

🔍 DRY RUN MODE - No changes will be made

Step 1: Fetching Unified Catalog terms...
✓ Found X UC term(s)

Step 2: Determining target glossary...
   Domain: <Domain Name>
✓ Found existing glossary: <Glossary Name> (<glossary-guid>)

Step 3: Checking existing classic glossary terms...
✓ Found Y existing term(s) in classic glossary

Step 4: Synchronizing terms...
   Would create: Term1
   Would create: Term2
   ⊖ Skipping: Term3 (already exists)

═══════════════════════════════════════════════════════════
  Synchronization Summary  
═══════════════════════════════════════════════════════════
Total UC Terms    X
Created          X
Updated          0
Skipped          Y
Failed           0

💡 This was a dry run. Use without --dry-run to apply changes.
```

### Test 2 : Création de glossaire

**Objectif** : Vérifier la création automatique de glossaire

```bash
# Utiliser un domaine sans glossaire correspondant
pvw uc term sync-classic \
  --domain-id "<domain-guid>" \
  --create-glossary \
  --dry-run
```

**Résultat attendu** :
```
Step 2: Determining target glossary...
   Domain: <Domain Name>
Would create glossary: <Domain Name>
```

### Test 3 : Synchronisation réelle

**Objectif** : Effectuer une vraie synchronisation

⚠️ **ATTENTION** : Ce test créera/modifiera des données dans Purview

```bash
pvw uc term sync-classic \
  --domain-id "<domain-guid>" \
  --create-glossary
```

**Résultat attendu** :
- Pas de message "DRY RUN"
- Messages "✓ Created: TermName"
- Résumé avec termes créés > 0

### Test 4 : Mise à jour de termes existants

**Objectif** : Tester la mise à jour de termes

```bash
# Première exécution : créer les termes
pvw uc term sync-classic --domain-id "<domain-guid>"

# Modifier un terme UC dans l'interface web
# Puis ré-exécuter avec --update-existing

pvw uc term sync-classic \
  --domain-id "<domain-guid>" \
  --update-existing
```

**Résultat attendu** :
```
Step 4: Synchronizing terms...
   ✓ Updated: TermName
   ⊖ Skipping: OtherTerm (already exists)
```

### Test 5 : Glossaire spécifique

**Objectif** : Synchroniser vers un glossaire particulier

```bash
pvw uc term sync-classic \
  --domain-id "<domain-guid>" \
  --glossary-guid "<target-glossary-guid>"
```

**Résultat attendu** :
```
Step 2: Determining target glossary...
✓ Using target glossary: <target-glossary-guid>
```

## Tests d'erreur

### Test E1 : Domaine inexistant

```bash
pvw uc term sync-classic --domain-id "invalid-guid-12345"
```

**Résultat attendu** :
```
ERROR: [Message d'erreur approprié]
```

### Test E2 : Sans domaine ni glossaire

```bash
pvw uc term sync-classic
```

**Résultat attendu** :
```
ERROR: Either --domain-id or --glossary-guid must be provided
```

### Test E3 : Glossaire inexistant sans --create-glossary

```bash
pvw uc term sync-classic \
  --domain-id "<domain-without-glossary>"
```

**Résultat attendu** :
```
ERROR: No target glossary found. Use --glossary-guid or --create-glossary
```

## Tests d'intégration

### Test I1 : Script PowerShell

```powershell
# Tester le script de synchronisation automatique
.\samples\powershell\Sync-UCToClassicGlossary.ps1 `
    -DomainIds "domain-guid-1" `
    -DryRun
```

**Résultat attendu** :
- Log créé dans le répertoire configuré
- Statistiques affichées pour chaque domaine
- Code de sortie 0

### Test I2 : Script complet

```powershell
# Configurer le script avec vos paramètres de test
# Puis exécuter
.\samples\powershell\Complete-Sync-Example.ps1
```

**Résultat attendu** :
- Rapport HTML généré
- Logs détaillés
- Notifications envoyées (si configuré)

## Tests de performance

### Test P1 : Grand nombre de termes

**Setup** :
- Créer un domaine avec 100+ termes

```bash
pvw uc term sync-classic \
  --domain-id "<large-domain-guid>" \
  --create-glossary
```

**Métriques à surveiller** :
- Temps d'exécution total
- Nombre de termes traités par minute
- Utilisation mémoire

### Test P2 : Plusieurs domaines

```powershell
$domains = @("domain-1", "domain-2", "domain-3")
foreach ($d in $domains) {
    Measure-Command {
        pvw uc term sync-classic --domain-id $d
    }
}
```

## Validation post-synchronisation

### Vérifier dans l'interface Purview

1. Ouvrir le portail Purview
2. Naviguer vers **Data Catalog** > **Glossaries**
3. Ouvrir le glossaire synchronisé
4. Vérifier que :
   - ✅ Les termes UC sont présents
   - ✅ Les descriptions sont correctes
   - ✅ Les acronymes/abréviations sont présents
   - ✅ Le statut est correct (Draft/Published)

### Vérifier via CLI

```bash
# Lister les termes du glossaire
pvw glossary read-terms --glossaryGuid "<glossary-guid>"

# Vérifier un terme spécifique
pvw glossary read-term --termGuid "<term-guid>"
```

## Checklist de validation

- [ ] Commande `sync-classic` listée dans `pvw uc term --help`
- [ ] Aide complète affichée avec `--help`
- [ ] Dry-run fonctionne sans modifier les données
- [ ] Création de glossaire avec `--create-glossary`
- [ ] Synchronisation réelle crée les termes
- [ ] Mise à jour avec `--update-existing`
- [ ] Gestion d'erreurs appropriée
- [ ] Messages formatés avec Rich (couleurs, tableaux)
- [ ] Statistiques affichées correctement
- [ ] Script PowerShell fonctionne
- [ ] Rapports HTML générés
- [ ] Logs créés et formatés

## Rapport de test

Date : _______________  
Testeur : _______________

| Test | Statut | Notes |
|------|--------|-------|
| Test 1 : Dry-run | ⬜ | |
| Test 2 : Création glossaire | ⬜ | |
| Test 3 : Sync réelle | ⬜ | |
| Test 4 : Mise à jour | ⬜ | |
| Test 5 : Glossaire spécifique | ⬜ | |
| Test E1 : Domaine invalide | ⬜ | |
| Test E2 : Paramètres manquants | ⬜ | |
| Test E3 : Glossaire manquant | ⬜ | |
| Test I1 : Script PS basique | ⬜ | |
| Test I2 : Script PS complet | ⬜ | |

**Notes globales** :
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

## Environnements de test

| Environnement | Purview | Statut | Notes |
|---------------|---------|--------|-------|
| Dev | dev-purview | ⬜ | |
| Test | test-purview | ⬜ | |
| Staging | staging-purview | ⬜ | |
| Production | prod-purview | ⬜ | À tester avec précaution |

## Rollback

En cas de problème, comment revenir en arrière :

### Option 1 : Supprimer les termes créés

```bash
# Lister les termes du glossaire
pvw glossary read-terms --glossaryGuid "<glossary-guid>"

# Supprimer chaque terme
pvw glossary delete-term --termGuid "<term-guid>"
```

### Option 2 : Supprimer le glossaire entier

⚠️ **ATTENTION** : Supprime tous les termes du glossaire

```bash
pvw glossary delete --glossaryGuid "<glossary-guid>"
```

### Option 3 : Restaurer depuis backup

Si vous avez exporté le glossaire avant :

```bash
pvw glossary import-terms --payloadFile backup.json
```

## Support

En cas de problème :

1. Activer le mode debug :
   ```bash
   export PURVIEWCLI_DEBUG=1
   pvw uc term sync-classic --domain-id "<guid>" --dry-run
   ```

2. Consulter les logs

3. Ouvrir une issue GitHub avec :
   - Version de Purview CLI
   - Commande exécutée
   - Message d'erreur complet
   - Logs debug (si applicable)

---

**Dernière mise à jour** : 2025-01-15  
**Version du guide** : 1.0.0
