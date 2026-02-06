# Référence Complète - Colonnes CSV pour UC Terms Import

**Date:** Février 2026  
**Version:** v2.0 (Séparateur point-virgule uniquement)

---

## 📋 Colonnes Supportées

### ✅ CHAMPS DE BASE (Obligatoire/Optionnel)

| Nom Colonne CSV | Variantes Acceptées | Obligatoire | Type | Exemple |
|-----------------|---------------------|-------------|------|---------|
| **name** | `name`, `Name` | ✅ **OUI** | Texte | `Client Premium` |
| **description** | `description`, `Description`, `Definition` | ❌ Non | Texte | `Entité représentant un client` |
| **status** | `status`, `Status` | ❌ Non | Enum | `Draft`, `Published`, `Archived` |

---

### 🆔 IDENTIFIANTS (Pour Updates Idempotents)

| Nom Colonne CSV | Variantes Acceptées | Type | Exemple |
|-----------------|---------------------|------|---------|
| **term_id** | `term_id`, `id`, `ID`, `Term ID`, `TermId` | GUID | `f85d19ec-8c3c-4c35-a731-d997d0b929cd` |

ℹ️ **Utilité:** Permet de mettre à jour le même terme lors de réimports successifs

---

### 📝 MÉTADONNÉES SIMPLES

| Nom Colonne CSV | Variantes | Séparateur | Exemple |
|-----------------|-----------|------------|---------|
| **acronyms** | `acronyms`, `acronym`, `Acronym` | **`;`** | `CLT;CUST;CLI` |

---

### 👥 CONTACTS & GOUVERNANCE

| Nom Colonne CSV | Variantes | Séparateur | Format Valeurs | Exemple |
|-----------------|-----------|------------|----------------|---------|
| **owner_ids** | `owner_ids`, `owner_id` | **`;`** | GUIDs Entra Object ID | `guid1;guid2;guid3` |
| **experts** | `experts`, `Experts` | **`;`** | GUIDs Entra Object ID | `expert-guid1;expert-guid2` |

⚠️ **IMPORTANT:** Utilisez des **GUIDs Entra Object ID**, **PAS des emails** !

---

### 🔗 RELATIONS SÉMANTIQUES

| Nom Colonne CSV | Variantes | Séparateur | Exemple |
|-----------------|-----------|------------|---------|
| **synonyms** | `synonyms`, `Synonyms`, `synonym` | **`;`** | `Customer;Consumer;Client;Buyer` |
| **parent_term_name** | `parent_term_name`, `Parent Term Name` | - | `Business Terms` |
| **parent_term_id** | `parent_term_id`, `parentId` | - | `a1b2c3d4-e5f6-7890-abcd-ef1234567890` |
| **related_terms** | `related_terms`, `Related Terms`, `related_term_names` | **`;`** | `Client;Produit;Commande` |
| **related_term_ids** | `related_term_ids` | **`;`** | `guid1;guid2;guid3` |

---

### 📚 RESOURCES (Documentation)

| Nom Colonne CSV | Format | Séparateur | Exemple |
|-----------------|--------|------------|---------|
| **resource_name** | Liste de noms | **`;`** | `Guide API;Documentation;Tutorial` |
| **resource_url** | Liste d'URLs | **`;`** | `https://api.com;https://docs.com;https://tutorial.com` |
| **Resources** | Format UI `nom:url` | **`;`** | `Guide:https://...;API:https://...` |

ℹ️ **Note:** `resource_name` et `resource_url` doivent avoir le **même nombre d'éléments**

---

### 🎨 CUSTOM ATTRIBUTES (Notation par Points)

| Format Colonne | Description | Exemple Colonne | Exemple Valeur |
|----------------|-------------|-----------------|----------------|
| **Simple** | Attribut plat | `customAttributes.Reference` | `REF-001` |
| **Nested** | Groupe.Champ | `customAttributes.DataGovernance.Classification` | `PII` |
| **Deep Nested** | Plusieurs niveaux | `customAttributes.Business.Context.Domain` | `Finance` |
| **Multi-value** | Array JSON échappé | `customAttributes.DataGovernance.Tags` | `"[""Sensitive"",""Protected""]"` |

---

## 🎯 TABLEAU RÉCAPITULATIF DES SÉPARATEURS

| Champ | Séparateur | Format | Exemple |
|-------|------------|--------|---------|
| **acronyms** | **`;`** uniquement | `ACR1;ACR2;ACR3` | `CLT;CUST;CLI` |
| **owner_ids** | **`;`** uniquement | `guid1;guid2` | `owner-guid-1;owner-guid-2` |
| **experts** | **`;`** uniquement | `guid1;guid2;guid3` | `expert1;expert2;expert3` |
| **synonyms** | **`;`** uniquement | `syn1;syn2;syn3` | `Customer;Consumer;Client` |
| **parent_term_name** | Aucun (valeur unique) | `One Value` | `Business Terms` |
| **parent_term_id** | Aucun (valeur unique) | `GUID` | `a1b2c3d4-e5f6-...` |
| **related_terms** | **`;`** uniquement | `term1;term2;term3` | `Client;Produit;Commande` |
| **related_term_ids** | **`;`** uniquement | `guid1;guid2;guid3` | `guid1;guid2;guid3` |
| **resource_name** | **`;`** uniquement | `name1;name2` | `Guide;API Ref` |
| **resource_url** | **`;`** uniquement | `url1;url2` | `https://a;https://b` |
| **Custom Attributes (array)** | JSON échappé | `"[""v1"",""v2""]"` | `"[""PII"",""Sensitive""]"` |

---

## 📄 EXEMPLES DE FICHIERS CSV

### Exemple 1: Minimal (Termes Simples)
```csv
name,description,status
Client,Entité client,Draft
Produit,Catalogue produit,Published
Commande,Transaction d'achat,Draft
```

### Exemple 2: Standard (Avec Hiérarchie)
```csv
name,description,status,parent_term_name,acronyms
Business Terms,Termes métier racine,Published,,BIZTERMS
Client,Entité client,Published,Business Terms,CLT;CUST
Produit,Catalogue produit,Draft,Business Terms,PRD;PROD
```

### Exemple 3: Avec Relations
```csv
name,description,synonyms,related_terms
Client,Entité client,Customer;Consumer,Produit;Commande
Produit,Catalogue produit,Item;SKU;Article,Client;Commande
Commande,Transaction d'achat,Order;Purchase,Client;Produit
```

### Exemple 4: Avec Contacts
```csv
name,description,owner_ids,experts
Client Premium,Client VIP,owner-guid-1;owner-guid-2,expert-guid-1;expert-guid-2;expert-guid-3
```

### Exemple 5: Avec Resources
```csv
name,description,resource_name,resource_url
Client,Entité client,Guide Client;API Documentation,https://docs.com/client;https://api.com/client
```

### Exemple 6: Avec Custom Attributes
```csv
name,description,customAttributes.DataGovernance.Classification,customAttributes.DataGovernance.Tags
Client,Entité client,PII,"[""Sensitive"",""Customer Data""]"
Produit,Catalogue produit,NON_PII,"[""Public"",""Product Info""]"
```

### Exemple 7: COMPLET (Tous les Champs)
```csv
term_id,name,description,status,acronyms,owner_ids,experts,synonyms,parent_term_name,related_terms,resource_name,resource_url,customAttributes.DataGovernance.Classification,customAttributes.DataGovernance.Tags
,Client Premium,Client avec statut premium,Published,CLIP;VIP,owner-guid-1;owner-guid-2,expert-guid-1;expert-guid-2,Premium Customer;VIP Client;Elite Customer,Business Terms,Produit;Commande,CRM Guide;API Doc,https://crm.com;https://api.com,PII,"[""Sensitive"",""Customer Data"",""Protected""]"
```

---

## ⚠️ POINTS IMPORTANTS

### 1. Séparateur de Valeurs Multiples

✅ **UTILISER:**
```csv
acronyms,owner_ids,experts,synonyms,related_terms
CLT;CUST;CLI,owner1;owner2,expert1;expert2,Customer;Consumer,Client;Produit
```

❌ **NE PAS UTILISER:**
```csv
acronyms,owner_ids
CLT,CUST,CLI,owner1,owner2    ❌ Virgules = conflit avec délimiteur CSV
```

### 2. GUIDs vs Emails

❌ **INCORRECT:**
```csv
owner_ids,experts
john.doe@company.com,jane.smith@company.com
```

✅ **CORRECT:**
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

### 3. Multi-value dans Custom Attributes

✅ **CORRECT:**
```csv
customAttributes.Tags
"[""Sensitive"",""Protected"",""Confidential""]"
```

❌ **INCORRECT:**
```csv
customAttributes.Tags
["Sensitive","Protected"]    ❌ Guillemets non échappés
Sensitive;Protected;Confidential    ❌ Pas de format JSON
```

### 4. Casse des Noms de Colonnes

Le parsing est **insensible à la casse** pour certains champs :
- `name` = `Name` ✅
- `status` = `Status` ✅
- `description` = `Description` = `Definition` ✅

### 5. Ordre de Création

Pour les hiérarchies, respectez cet ordre :
1. **Termes racine** (sans `parent_term_name`)
2. **Termes niveau 2** (avec `parent_term_name`)
3. **Termes niveau 3+**

Ou utilisez `--update-existing` pour import dans n'importe quel ordre.

---

## 🔗 FICHIERS DE RÉFÉRENCE

| Fichier | Description |
|---------|-------------|
| `uc_terms_all_fields_example.csv` | Template avec tous les champs |
| `uc_terms_multivalue_example.csv` | Exemples multi-value avec arrays JSON |
| `UC_TERMS_ALL_FIELDS_README.md` | Guide détaillé de tous les champs |
| `UC_TERMS_MULTIVALUE_README.md` | Guide des valeurs multiples |

---

## 📝 TEMPLATE VIDE

```csv
term_id,name,description,status,acronyms,owner_ids,experts,synonyms,parent_term_name,parent_term_id,related_terms,related_term_ids,resource_name,resource_url,customAttributes.Group.Field
,,,Draft,,,,,,,,,,,
```

**Utilisation:**
1. Copiez cette ligne d'en-tête
2. Remplissez vos données
3. Importez avec `pvw uc term import-csv --csv-file yourfile.csv --domain-id <DOMAIN_ID>`

---

## 🚀 COMMANDES D'IMPORT

### Import Standard
```powershell
pvw uc term import-csv --csv-file terms.csv --domain-id "bc785cdb-11c3-4227-ab44-f6ad44048623"
```

### Dry-Run (Aperçu)
```powershell
pvw uc term import-csv --csv-file terms.csv --domain-id "bc785cdb-..." --dry-run
```

### Avec Update sur Doublons
```powershell
pvw uc term import-csv --csv-file terms.csv --domain-id "bc785cdb-..." --update-existing
```

### Avec Debug
```powershell
pvw uc term import-csv --csv-file terms.csv --domain-id "bc785cdb-..." --debug
```

---

**Dernière mise à jour:** Février 2026  
**Séparateur multi-valeurs:** Point-virgule `;` uniquement  
**Encodage CSV:** UTF-8
