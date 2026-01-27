# Collections API - Résumé des Permissions Requises

## Résumé Rapide

Pour que `pvw collections create` fonctionne avec un Service Principal (SP), vous avez besoin de **DEUX niveaux de permissions**:

### 1. Azure RBAC (Niveau Souscription)
Le SP doit avoir le rôle **`Contributor`** ou **`Owner`** sur la ressource Purview Account

```bash
# Via Azure CLI
az role assignment create \
  --role "Contributor" \
  --assignee-object-id <SP_OBJECT_ID> \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RG>/providers/Microsoft.Purview/accounts/<ACCOUNT>
```

### 2. Rôles Purview (Niveau Purview)
Le SP doit avoir l'un de ces rôles Purview:
- ✅ **Purview Data Source Administrator** (recommandé)
- ✅ **Collection Administrator**
- ❌ Purview Data Curator (NON - lecture seule)
- ❌ Purview Data Reader (NON - lecture seule)

**Via Azure Portal:**
1. Allez à Purview Account > Access Control (IAM)
2. Cliquez "+ Add" > "Add role assignment"
3. Sélectionnez **"Purview Data Source Administrator"**
4. Sélectionnez votre Service Principal
5. Cliquez "Review + Assign"

## Checklist Complète

```
✓ Vérifier Azure RBAC role
  az role assignment list --assignee-object-id <SP_OBJECT_ID> --scope <RESOURCE_ID>
  
✓ Vérifier que le SP est Cloud Administrator dans Purview
  (Via Portal: Purview > Data Plane Access > Collections tab)
  
✓ Vérifier les env variables
  echo $AZURE_CLIENT_ID
  echo $AZURE_TENANT_ID
  echo $PURVIEW_ACCOUNT_NAME (format: account-name ONLY, pas d'URL)
  
✓ Attendre 5-10 minutes pour la propagation
  
✓ Tester avec: pvw collections list
  
✓ Si encore 403: az logout && az login (rafraîchir l'auth)
```

## Diagnostic Automatique

Utilisez les scripts fournis pour diagnostiquer automatiquement:

**PowerShell:**
```powershell
./scripts/diagnose_collections_permissions.ps1
```

**Python:**
```bash
python scripts/diagnose_collections_permissions.py
```

## Causes Courantes de "HTTP 403"

| Cause | Solution |
|-------|----------|
| **Rôle Purview manquant** | Ajouter "Purview Data Source Administrator" |
| **Azure RBAC insuffisant** | Upgrade vers "Contributor" ou "Owner" |
| **Permissions pas propagées** | Attendre 5-10 minutes et réessayer |
| **Format PURVIEW_ACCOUNT_NAME** | Utiliser "my-account" PAS "my-account.purview.azure.com" |
| **SP pas enregistré en tenant** | `az ad sp create --id 73c2949e-da2d-457a-9607-fcc665198967` |

## Permissions Minimales

**Azure Subscription Level (REQUIRED):**
```
Microsoft.Purview/accounts/read
Microsoft.Purview/accounts/write
Microsoft.Authorization/roleAssignments/read
```

**Purview Data Plane (REQUIRED):**
```
Collections: Create, Read, Update, Delete
Permissions: Read, Write
```

## Commande Test

```bash
# Vérifier que tout fonctionne
pvw collections create \
  --collection-name "test-$(date +%s)" \
  --friendly-name "Test Collection" \
  --description "Test de permissions"
```

## Documentation Complète

Voir le fichier [COLLECTIONS_PERMISSIONS.md](COLLECTIONS_PERMISSIONS.md) pour les détails complets avec:
- Scripts PowerShell et Bash complets
- Exemples détaillés pour chaque permission
- Procédures de dépannage avancées
- Références Microsoft officiales
