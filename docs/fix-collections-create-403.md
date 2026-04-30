# ✅ SOLUTION RAPIDE: Erreur "HTTP 403" avec `pvw collections create`

## Vous avez: Service Principal (SP) avec "Collection Admin"
## Problème: `pvw collections create` retourne "HTTP 403 Forbidden"

---

## LA RAISON

Les droits "Collection Admin" **SEUL** ne suffisent pas. L'API Collections de Microsoft Purview requiert:

✓ **Droits Azure RBAC** (niveau souscription Azure)  
✓ **Rôles Purview Data Plane** (niveau Purview)

Vous avez probablement que **l'un** des deux.

---

## ✅ SOLUTION EN 5 ÉTAPES

### Étape 1: Vérifier le rôle Azure RBAC

```bash
# Obtenir l'Object ID du SP
$spObjectId = (az ad sp show --id $env:AZURE_CLIENT_ID --query id -o tsv)
echo "Object ID: $spObjectId"

# Vérifier les rôles Azure RBAC
az role assignment list --assignee-object-id $spObjectId --scope "<PURVIEW_RESOURCE_ID>" --output table
```

**Résultat attendu:** `Contributor` ou `Owner`

**Si manquant:** Assigner le rôle

```bash
az role assignment create \
  --role "Contributor" \
  --assignee-object-id "<SP_OBJECT_ID>" \
  --scope "<PURVIEW_RESOURCE_ID>"
```

### Étape 2: Vérifier les rôles Purview Data Plane

Via **Azure Portal:**
1. Allez à **Purview Account**
2. Cliquez **Access Control (IAM)**
3. Cherchez votre Service Principal dans la liste
4. Vérifiez qu'il a **"Purview Data Source Administrator"** ou **"Collection Administrator"**

### Étape 3: Assigner le rôle Purview (SI MANQUANT)

Via **Azure Portal:**
1. **Access Control (IAM)** > **+ Add** > **Add role assignment**
2. Sélectionnez **"Purview Data Source Administrator"** (recommandé pour create)
3. Sélectionnez votre **Service Principal**
4. Cliquez **Review + Assign**

### Étape 4: Attendre la propagation

⏳ **Azure met 5-10 minutes** pour propager les rôles  
→ Attendez et réessayez

### Étape 5: Tester

```bash
# Vérifier les permissions Purview
pvw collections list

# Tester la création
pvw collections create \
  --collection-name "test-collection" \
  --friendly-name "Ma Collection Test" \
  --description "Test des permissions"
```

---

## 📋 CHECKLIST COMPLÈTE

```
Permissions Azure RBAC (niveau souscription):
  ☐ Service Principal = Owner OU Contributor
  ☐ Scope = Purview Account resource
  ☐ Vérifier avec: az role assignment list --assignee-object-id <SP_OBJECT_ID>

Permissions Purview Data Plane (niveau Purview):
  ☐ Service Principal = Purview Data Source Administrator OU Collection Administrator
  ☐ Vérifier via Portal: Purview > Access Control (IAM)

Configuration:
  ☐ AZURE_CLIENT_ID = défini
  ☐ AZURE_TENANT_ID = défini
  ☐ AZURE_CLIENT_SECRET = défini
  ☐ PURVIEW_ACCOUNT_NAME = défini (format: "my-account" PAS "my-account.purview.azure.com")

Timing:
  ☐ Attendre 5-10 minutes après assigner les rôles
  ☐ Vérifier une deuxième fois avec: pvw collections list
```

---

## 🔍 DIAGNOSTIC AUTOMATIQUE

Nous avons créé des scripts pour diagnostiquer automatiquement:

**PowerShell (Windows):**
```powershell
./scripts/diagnose_collections_permissions.ps1
```

**Python (tous OS):**
```bash
python scripts/diagnose_collections_permissions.py
```

→ Ces scripts testent **tous** les aspects et vous donnent des recommandations exactes

---

## 🆘 PROBLÈMES COURANTS

| Erreur | Cause | Solution |
|--------|-------|----------|
| `HTTP 403 Forbidden` | Rôle Purview manquant | Assigner "Purview Data Source Administrator" |
| `HTTP 403` peu après assigner le rôle | Propagation pas terminée | Attendre 10 minutes, puis relancer |
| `HTTP 403` même après assigner | Rôle Azure RBAC manquant | Vérifier que SP a "Contributor" sur le account Purview |
| Rôles corrects mais toujours 403 | Cache d'authentification | `az logout && az login`, puis relancer |

---

## 📚 DOCUMENTATION COMPLÈTE

Pour plus de détails:
- **Français:** `docs/collections-permissions-fr.md`
- **Complet (Anglais):** `docs/collections-permissions.md`

---

## ✨ COMMANDE FINALE À TESTER

Une fois tout en place:

```powershell
# PowerShell
$env:LOGLEVEL = "DEBUG"
pvw collections create `
  --collection-name "test-$(Get-Date -Format 'yyyyMMdd-HHmmss')" `
  --friendly-name "Test Collection" `
  --description "Test que tout fonctionne"
```

```bash
# Bash
export LOGLEVEL=DEBUG
pvw collections create \
  --collection-name "test-$(date +%s)" \
  --friendly-name "Test Collection" \
  --description "Test que tout fonctionne"
```

**Résultat attendu:** La collection est créée avec succès ✓

---

## 💬 Questions?

Si toujours pas de succès après tous ces étapes:
1. Exécutez le script de diagnostic
2. Partez les logs (LOGLEVEL=DEBUG)
3. Vérifiez `docs/collections-permissions.md` pour plus de détails
