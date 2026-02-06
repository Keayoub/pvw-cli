# Guide - Valeurs Multiples (Multi-Value) dans UC Terms Import

## 📋 Fichier Exemple
`samples/csv/uc_terms_multivalue_example.csv`

## 🎯 Qu'est-ce qu'une Valeur Multiple (Multi-Value) ?

Les **valeurs multiples** permettent de stocker des **listes/arrays** dans les custom attributes au lieu d'une simple valeur texte.

### Exemple Simple
```
❌ Valeur simple:   Classification = "PII"
✅ Valeur multiple:  Tags = ["Sensitive", "Customer Data", "Protected"]
```

## 📝 Formats Supportés pour Multi-Value

### 1️⃣ Custom Attributes (Arrays JSON)

**Format CSV:**
```csv
customAttributes.DataGovernance.Tags
"[""Sensitive"",""Customer Data"",""Protected""]"
```

**Résultat JSON:**
```json
{
  "DataGovernance": {
    "Tags": ["Sensitive", "Customer Data", "Protected"]
  }
}
```

⚠️ **Important**: Utilisez des **guillemets doubles échappés** (`""`) dans le CSV.

### 2️⃣ Champs Natifs (Séparateurs)

Certains champs supportent naturellement les valeurs multiples avec des séparateurs :

| Champ | Séparateur | Exemple CSV | Résultat |
|-------|------------|-------------|----------|
| `acronyms` | Virgule `,` | `CLT,CUST,CLI` | `["CLT", "CUST", "CLI"]` |
| `owner_ids` | Virgule `,` | `guid1,guid2,guid3` | Array de GUIDs |
| `experts` | `;` ou `,` | `guid1;guid2;guid3` | Array de GUIDs |
| `synonyms` | `;` ou `,` | `Customer,Client,Consumer` | Array de textes |
| `related_terms` | `;` ou `,` | `A;B;C` | Array de noms |
| `resource_name` | Point-virgule `;` | `Guide;API;Doc` | Array de noms |
| `resource_url` | Point-virgule `;` | `http://a;http://b` | Array d'URLs |

## 🎨 Exemples Pratiques

### Exemple 1: Tags de Classification Multiple

**CSV:**
```csv
name,customAttributes.DataGovernance.Tags
Client Premium,"[""Sensitive"",""Customer Data"",""Protected""]"
```

**JSON Résultant:**
```json
{
  "customAttributes": {
    "DataGovernance": {
      "Tags": ["Sensitive", "Customer Data", "Protected"]
    }
  }
}
```

### Exemple 2: Réglementations Multiples

**CSV:**
```csv
name,customAttributes.Compliance.Regulations
Données Financières,"[""GDPR"",""SOX"",""Basel III"",""IFRS""]"
```

**JSON Résultant:**
```json
{
  "customAttributes": {
    "Compliance": {
      "Regulations": ["GDPR", "SOX", "Basel III", "IFRS"]
    }
  }
}
```

### Exemple 3: Systèmes Techniques Multiples

**CSV:**
```csv
name,customAttributes.Technical.Systems
Client Premium,"[""CRM System"",""Billing Platform"",""Analytics Dashboard""]"
```

**JSON Résultant:**
```json
{
  "customAttributes": {
    "Technical": {
      "Systems": ["CRM System", "Billing Platform", "Analytics Dashboard"]
    }
  }
}
```

### Exemple 4: Keywords pour Recherche

**CSV:**
```csv
name,customAttributes.Metadata.Keywords
Client Premium,"[""customer"",""premium"",""vip"",""high-value""]"
```

**JSON Résultant:**
```json
{
  "customAttributes": {
    "Metadata": {
      "Keywords": ["customer", "premium", "vip", "high-value"]
    }
  }
}
```

## 🔧 Comment Échapper les Guillemets

### Dans CSV (Excel/LibreOffice)

**Méthode 1: Guillemets doublés**
```csv
"[""value1"",""value2"",""value3""]"
```

**Méthode 2: Édition manuelle**
1. Saisir la valeur dans Excel: `["value1","value2","value3"]`
2. Excel formatera automatiquement lors de la sauvegarde

### Dans PowerShell (Génération CSV)

```powershell
$terms = @(
    @{
        name = "Client Premium"
        tags = '["Sensitive","Customer Data","Protected"]'
    }
)

$terms | ForEach-Object {
    [PSCustomObject]@{
        name = $_.name
        'customAttributes.DataGovernance.Tags' = "`"$($_.tags)`""
    }
} | Export-Csv -Path "terms.csv" -NoTypeInformation
```

### En Python (Génération CSV)

```python
import csv
import json

terms = [
    {
        'name': 'Client Premium',
        'customAttributes.DataGovernance.Tags': json.dumps([
            "Sensitive",
            "Customer Data", 
            "Protected"
        ])
    }
]

with open('terms.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['name', 'customAttributes.DataGovernance.Tags']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(terms)
```

## 📊 Exemples de Cas d'Usage

### 1. Conformité Réglementaire Multiple

```csv
name,description,customAttributes.Compliance.Regulations,customAttributes.Compliance.CertificationRequired
Données Patient,Données médicales des patients,"[""HIPAA"",""HITECH"",""GDPR"",""FDA 21 CFR Part 11""]","[""ISO 27001"",""SOC 2 Type II""]"
```

### 2. Systèmes Sources Multiples

```csv
name,description,customAttributes.Technical.SourceSystems,customAttributes.Technical.DataFlow
Client 360,Vue complète du client,"[""CRM"",""ERP"",""Marketing Automation"",""Support Ticketing""]","[""Real-time"",""Batch"",""Event-driven""]"
```

### 3. Classifications Multiples

```csv
name,description,customAttributes.DataGovernance.Classifications,customAttributes.DataGovernance.SecurityLabels
Contrat Client,Contrats commerciaux,"[""Legal"",""Financial"",""Confidential""]","[""Internal"",""Restricted"",""Need-to-Know""]"
```

### 4. Parties Prenantes Multiples

```csv
name,description,customAttributes.BusinessContext.Stakeholders,customAttributes.BusinessContext.BusinessUnits
Initiative Stratégique,Projet stratégique majeur,"[""CEO"",""CFO"",""VP Sales"",""VP Marketing""]","[""Sales"",""Marketing"",""Finance"",""Operations""]"
```

### 5. Technologies Multiples

```csv
name,description,customAttributes.Technical.Technologies,customAttributes.Technical.Protocols
API Gateway,Passerelle API,"[""REST"",""GraphQL"",""gRPC"",""WebSocket""]","[""HTTP/2"",""TLS 1.3"",""OAuth 2.0"",""OpenID Connect""]"
```

## 🎯 Structures Complexes (Nested Multi-Value)

### Arrays Imbriqués

**CSV:**
```csv
name,customAttributes.DataQuality.Checks
Transaction,"[""Completeness"",""Accuracy"",""Consistency"",""Timeliness"",""Validity""]"
```

### Objets dans Arrays (Format JSON Avancé)

**CSV:**
```csv
name,customAttributes.Lineage.Sources
Client 360,"{""sources"":[{""name"":""CRM"",""type"":""Database""},{""name"":""Marketing"",""type"":""API""}]}"
```

**Résultat:**
```json
{
  "Lineage": {
    "Sources": {
      "sources": [
        {"name": "CRM", "type": "Database"},
        {"name": "Marketing", "type": "API"}
      ]
    }
  }
}
```

## ⚠️ Pièges à Éviter

### ❌ Oubli des guillemets échappés
```csv
customAttributes.Tags
["tag1","tag2"]  ❌ Parse error
```

### ✅ Correct
```csv
customAttributes.Tags
"[""tag1"",""tag2""]"  ✅ Fonctionne
```

---

### ❌ Mélanger séparateurs et JSON
```csv
customAttributes.Tags
Sensitive,Protected,Confidential  ❌ Sera traité comme texte simple
```

### ✅ Correct
```csv
customAttributes.Tags
"[""Sensitive"",""Protected"",""Confidential""]"  ✅ Array JSON
```

---

### ❌ Virgules dans les valeurs
```csv
customAttributes.Regulations
"[""GDPR, Article 5"",""CCPA, Section 1798""]"  ❌ Parsing ambigu
```

### ✅ Correct
```csv
customAttributes.Regulations
"[""GDPR Article 5"",""CCPA Section 1798""]"  ✅ Pas de virgules dans valeurs
```

## 🧪 Test du CSV

### Validation Manuelle

```powershell
# Tester le parsing JSON
$jsonArray = '["tag1","tag2","tag3"]'
$parsed = $jsonArray | ConvertFrom-Json
Write-Host "Résultat: $($parsed.Count) items"
```

### Dry-Run avec pvw-cli

```powershell
pvw uc term import-csv `
  --csv-file "samples/csv/uc_terms_multivalue_example.csv" `
  --domain-id "bc785cdb-11c3-4227-ab44-f6ad44048623" `
  --dry-run `
  --debug
```

Le flag `--debug` affichera le JSON parsé pour vérification.

## 📚 Récapitulatif

| Type de Multi-Value | Méthode | Exemple |
|---------------------|---------|---------|
| **Champs natifs** | Séparateurs (`,` ou `;`) | `acronyms: "A,B,C"` |
| **Custom attributes** | JSON Array échappé | `"[""A"",""B"",""C""]"` |
| **Resources** | Noms et URLs séparés par `;` | `name: "A;B"` + `url: "url1;url2"` |
| **Objets complexes** | JSON complet échappé | `"{""key"":[...]}"` |

## 🚀 Pour Aller Plus Loin

**Fichier de test complet**: `samples/csv/uc_terms_multivalue_example.csv`

Ce fichier contient **10 termes** avec:
- ✅ 4+ custom attributes multi-value par terme
- ✅ Tags, Regulations, Systems, Keywords
- ✅ Exemples réels (GDPR, HIPAA, SOX, etc.)
- ✅ Différents domaines (Finance, Healthcare, IoT, etc.)

**Import:**
```powershell
pvw uc term import-csv --csv-file "samples/csv/uc_terms_multivalue_example.csv" --domain-id "<YOUR_DOMAIN_ID>" --update-existing
```
