# Guide Complet - Tous les Champs Supportés pour l'Import UC Terms

## 📋 Fichier Exemple
`samples/csv/uc_terms_all_fields_example.csv`

## 🎯 Tous les Champs Supportés

### ✅ Champs Obligatoires

| Champ | Description | Exemple |
|-------|-------------|---------|
| `name` | Nom du terme (unique par domaine) | `Client` |
| `domain_id` | Via `--domain-id` en ligne de commande | `bc785cdb-11c3-4227-ab44-...` |

### ✅ Champs Identité & Métadonnées

| Champ | Type | Description | Exemple |
|-------|------|-------------|---------|
| `term_id` | GUID | ID unique pour updates idempotents (optionnel mais recommandé) | `f85d19ec-8c3c-4c35-...` |
| `description` | Texte | Description du terme | `Entité représentant un client` |
| `status` | Enum | `Draft`, `Published`, ou `Archived` | `Published` |
| `acronyms` | Liste | Acronymes, séparés par virgule | `CLT,CUST` |

### ✅ Champs Contacts & Gouvernance

| Champ | Type | Description | Format | Exemple |
|-------|------|-------------|--------|---------|
| `owner_ids` | GUIDs | Propriétaires du terme | Virgule ou point-virgule | `guid1,guid2` |
| `experts` | GUIDs | Experts du terme | Virgule ou point-virgule | `guid1;guid2;guid3` |

⚠️ **Important**: Utilisez des **GUIDs Entra Object ID**, pas des emails !

### ✅ Champs Relations Sémantiques

| Champ | Type | Description | Format |
|-------|------|-------------|--------|
| `synonyms` | Texte | Synonymes du terme | Virgule ou point-virgule |
| `parent_term_name` | Texte | Nom du terme parent | Texte simple |
| `parent_term_id` | GUID | ID direct du terme parent | GUID |
| `related_terms` | Texte | Noms de termes liés | Virgule ou point-virgule |
| `related_term_ids` | GUIDs | IDs de termes liés | Virgule |

**Exemples:**
```csv
synonyms: "Customer,Consumer,Buyer"
parent_term_name: "Business Terms"
related_terms: "Client;Produit;Commande"
```

### ✅ Champs Resources (Documentation)

| Champ | Type | Description | Format |
|-------|------|-------------|--------|
| `resource_name` | Texte | Noms des ressources | Point-virgule pour multiples |
| `resource_url` | URLs | URLs des ressources | Point-virgule pour multiples |

**Exemple:**
```csv
resource_name: "Documentation Client;API Guide"
resource_url: "https://docs.example.com/client;https://api.example.com/client"
```

### ✅ Champs Custom Attributes (Attributs Personnalisés)

| Format | Description | Exemple CSV | JSON Résultant |
|--------|-------------|-------------|----------------|
| Simple | Attribut plat | `customAttributes.Reference` → `REF-001` | `{"Reference": "REF-001"}` |
| Nested | Attribut groupé | `customAttributes.Data.Classification` → `PII` | `{"Data": {"Classification": "PII"}}` |
| Multi-level | Hiérarchie profonde | `customAttributes.A.B.C` → `value` | `{"A": {"B": {"C": "value"}}}` |

**Exemples:**
```csv
customAttributes.DataGovernance.Classification,customAttributes.DataGovernance.Sensitivity
PII,HIGH
```

Résultat JSON:
```json
{
  "DataGovernance": {
    "Classification": "PII",
    "Sensitivity": "HIGH"
  }
}
```

## 🎨 Formats de Séparation Supportés

| Champ | Séparateur Supporté | Exemple |
|-------|---------------------|---------|
| `acronyms` | Virgule (`,`) | `CLT,CUST,CLI` |
| `owner_ids` | Virgule (`,`) | `guid1,guid2` |
| `experts` | Virgule `,` ou Point-virgule `;` | `guid1;guid2;guid3` |
| `synonyms` | Virgule `,` ou Point-virgule `;` | `Customer,Consumer` |
| `related_terms` | Virgule `,` ou Point-virgule `;` | `Client;Produit` |
| `resource_name` | Point-virgule (`;`) | `Guide;API Ref` |
| `resource_url` | Point-virgule (`;`) | `http://a;http://b` |

## 📊 Structure Hiérarchique

### Hiérarchie de Termes (3 niveaux)

```
Business Terms (racine)
├── Client
│   ├── Adresse Client
│   └── Contact Client
├── Transaction
│   ├── Commande
│   ├── Facture
│   └── Paiement
│       └── Remboursement (niveau 3)
└── Produit
    ├── Catégorie Produit
    └── Prix Produit
```

**CSV Correspondant:**
```csv
name,parent_term_name
Business Terms,
Client,Business Terms
Adresse Client,Client
Contact Client,Client
Transaction,Business Terms
Paiement,Transaction
Remboursement,Paiement
```

## 🔄 Modes d'Import

### 1. Import Initial (CREATE)
```bash
pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN_ID>
```

### 2. Import avec Détection de Doublons (UPDATE)
```bash
pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN_ID> --update-existing
```

### 3. Aperçu Avant Import (DRY-RUN)
```bash
pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN_ID> --dry-run
```

### 4. Debug Mode
```bash
pvw uc term import-csv --csv-file terms.csv --domain-id <DOMAIN_ID> --debug
```

## 🔍 Résolution Automatique

Le système résout automatiquement :

| Ce Que Vous Donnez | Ce Que le Système Fait |
|-------------------|------------------------|
| `parent_term_name: "Client"` | Cherche le terme "Client" → Récupère son ID → Utilise l'ID |
| `related_terms: "A,B,C"` | Cherche chaque terme → Crée les relations |
| `synonyms: "X,Y,Z"` | Crée chaque synonyme s'il n'existe pas → Crée les relations |

## ⚡ Post-Processing Automatique

Après la création du terme de base, le système :

1. ✅ **Lie le terme parent** (si `parent_term_name` ou `parent_term_id`)
2. ✅ **Ajoute les experts** (si `experts`)
3. ✅ **Crée les synonymes** (si `synonyms`)
   - Crée les termes synonymes s'ils n'existent pas
   - Établit les relations de type "Synonym"
4. ✅ **Lie les termes associés** (si `related_terms`)
   - Crée les relations de type "Related"

## 📝 Exemples d'Utilisation

### Exemple 1: Terme Simple
```csv
name,description,status
Client,Customer entity,Draft
```

### Exemple 2: Terme avec Hiérarchie
```csv
name,description,parent_term_name
Business Terms,Root terms,
Client,Customer entity,Business Terms
```

### Exemple 3: Terme Complet
```csv
name,description,status,acronyms,owner_ids,experts,synonyms,parent_term_name,related_terms,resource_name,resource_url,customAttributes.Data.Class
Client,Customer entity,Published,CLT,owner-guid,expert1;expert2,"Customer,Consumer",Business Terms,Produit;Commande,Client Guide,https://docs.example.com/client,PII
```

## 🎯 Template CSV Vide

```csv
term_id,name,description,status,acronyms,owner_ids,experts,synonyms,parent_term_name,parent_term_id,related_terms,related_term_ids,resource_name,resource_url,customAttributes.Group.Field
,Mon Terme,Description du terme,Draft,,,,,,,,,,,
```

## ⚠️ Points Importants

### 1. GUIDs vs Emails
❌ **NE PAS UTILISER:**
```csv
owner_ids,experts
user@company.com,expert@company.com
```

✅ **UTILISER:**
```csv
owner_ids,experts
0360aff3-add5-4b7c-b172-52add69b0199,f85d19ec-8c3c-4c35-a731-d997d0b929cd
```

**Comment obtenir les GUIDs:**
```powershell
# Azure CLI
az ad user show --id user@company.com --query id -o tsv

# PowerShell
(Get-AzADUser -UserPrincipalName user@company.com).Id
```

### 2. Ordre de Création

Pour les hiérarchies, créez dans l'ordre :
1. Termes racine (sans parent)
2. Termes niveau 2
3. Termes niveau 3

Ou utilisez `--update-existing` pour importer dans n'importe quel ordre (le système réessaiera).

### 3. Status et Domaine

❌ **ERREUR COURANTE:**
```csv
status
Published  # Dans un domaine non publié → ERREUR 400
```

✅ **SOLUTION:**
```csv
status
Draft  # Utiliser Draft pour domaines non publiés
```

## 🔗 Fichiers Associés

- **Exemple complet**: `samples/csv/uc_terms_all_fields_example.csv`
- **Exemple simple**: `samples/csv/uc_terms_import_example_complete.csv`
- **Guide détaillé**: `doc/guides/UC_TERMS_IMPORT_GUIDE.md`
- **Documentation API**: `doc/commands/unified-catalog/term-bulk-import.md`

## 📚 Support

Pour des questions:
1. Consultez `doc/guides/UC_TERMS_IMPORT_GUIDE.md`
2. Exemple notebook: `samples/notebooks (plus)/unified_catalog_terms_examples.ipynb`
3. GitHub Issues: https://github.com/Keayoub/pvw-cli/issues
