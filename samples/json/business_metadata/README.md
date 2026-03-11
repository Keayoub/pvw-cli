# Business Metadata Templates

Ce dossier contient des templates JSON prêts à l'emploi pour créer des groupes de Business Metadata dans Microsoft Purview.

## 📦 Templates Disponibles

### Business Concept Metadata (Pour Glossary Terms)

| Template | Description | Attributs |
|----------|-------------|-----------|
| `business_metadata_governance.json` | Gouvernance et conformité | DataOwner, ComplianceStatus, ReviewDate |
| `business_metadata_privacy.json` | Classification de confidentialité | PrivacyLevel, PIIContained, DataClassification |
| `business_metadata_advanced_with_enums.json` | Gouvernance avancée avec dropdowns | Status (enum), Confidentiality (enum), ApprovedBy, ApprovalDate |
| `business_metadata_advanced_no_enums.json` | Version sans définition d'enums (réutilise enums existants) | Mêmes attributs que advanced_with_enums |
| `business_metadata_dataproduct.json` | **NOUVEAU** : Métadonnées pour Data Products | ProductOwner, BusinessDomain, DataClassification, ComplianceStatus |

### Data Asset Metadata (Pour Tables, Files, Databases)

| Template | Description | Attributs |
|----------|-------------|-----------|
| `business_metadata_quality.json` | Métriques de qualité des données | QualityScore, LastValidated, ValidationNotes |

### Universal Metadata (Pour tous les types)

| Template | Description | Attributs |
|----------|-------------|-----------|
| `business_metadata_universal.json` | Documentation universelle | DocumentationLink, LastUpdated, UpdatedBy |

### Legacy Templates

| Template | Description | Usage |
|----------|-------------|-------|
| `dataset_template.json` | Template pour données tabulaires | Exemple de structure |
| `table_template.json` | Template pour tables SQL | Exemple de structure |

---

## 🚀 Utilisation

### Créer un groupe Business Metadata

```bash
# Business Concept (Glossary Terms)
pvw types create-business-metadata-def --payload-file samples/json/business_metadata/business_metadata_governance.json

# Data Asset (Tables, Files)
pvw types create-business-metadata-def --payload-file samples/json/business_metadata/business_metadata_quality.json
```

### Lister les groupes existants

```bash
pvw types list-business-metadata-groups
```

### Lire un groupe spécifique

```bash
pvw types read-business-metadata-def --name Governance
```

---

## ⚙️ Configuration Technique

### Pour Business Concepts (Glossary Terms)

**Configuration requise** :
```json
{
  "attributeDefs": [{
    "name": "AttributeName",
    "options": {
      "applicableEntityTypes": "[\"AtlasGlossaryTerm\"]"  // REQUIS
    }
  }],
  "options": {
    "applicableEntityTypes": "[\"AtlasGlossaryTerm\"]",  // REQUIS
    "dataGovernanceOptions": "{\"applicableConstructs\":[\"businessConcept:AtlasGlossaryTerm\"]}"
  }
}
```

**Points clés** :
- ✅ `applicableEntityTypes` DOIT être spécifié sur **chaque attribut**
- ✅ `applicableEntityTypes` DOIT être spécifié au **niveau du groupe**
- ✅ `dataGovernanceOptions` doit correspondre au type d'entité

### Pour Data Assets

**Configuration requise** :
```json
{
  "options": {
    "dataGovernanceOptions": "{\"applicableConstructs\":[\"dataset:*\"]}"
    // Pas de applicableEntityTypes nécessaire
  }
}
```

### Pour Data Products ⭐ NOUVEAU

**Configuration requise** :
```json
{
  "attributeDefs": [{
    "name": "AttributeName",
    "options": {
      "isPurviewDataGovernanceDefinition": "true",
      "dataGovernanceOptions": "{\"inheritApplicableConstructsFromGroup\":true,\"applicableConstructs\":[]}"
    }
  }],
  "options": {
    "isPurviewDataGovernanceDefinition": "true",
    "dataGovernanceOptions": "{\"applicableConstructs\":[\"domainScope:all\",\"businessConcept:dataProduct\",\"dataProductType:all\"]}"
  }
}
```

**Points clés** :
- ✅ `isPurviewDataGovernanceDefinition: "true"` au niveau groupe ET attributs
- ✅ `inheritApplicableConstructsFromGroup: true` pour hériter du scope du groupe
- ✅ Cible les Data Products (nouveau concept Purview)
- ✅ Pas besoin de `applicableEntityTypes`

---

## 🐛 Bug UI Connu

⚠️ **Interface Purview** : L'onglet "Custom metadata (preview)" a un bug d'affichage. Même avec la configuration correcte, tous les groupes peuvent apparaître sous "Data asset attributes".

**Validation** :
- Utilisez CLI : `pvw types list-business-metadata-groups`
- Testez l'ajout aux entités (HTTP 204 = succès)
- Le fonctionnement est correct malgré l'affichage UI incorrect

---

## 📖 Documentation Complète

- **Guide de création** : `doc/guides/create-business-metadata.md`
- **Solution scope** : `doc/guides/business-metadata-scope-SOLUTION.md`
- **Package complet** : `BUSINESS_METADATA_READY.md`

---

## 🔧 Modification des Templates

Pour modifier un template :
1. Éditez le fichier JSON
2. Testez avec `--dry-run` : ajoutez `--dry-run` à la commande create
3. Créez le groupe : `pvw types create-business-metadata-def --payload-file <file>`

**Types de données supportés** :
- `string` - Texte (avec `maxStrLength`)
- `int` - Nombre entier (avec `minValue`, `maxValue`)
- `float` - Nombre décimal
- `boolean` - Vrai/Faux
- `date` - Date (format timestamp)
- Custom enum - Valeurs prédéfinies (nécessite définition `enumDefs`)

---

**Date de dernière mise à jour** : 28 octobre 2025
