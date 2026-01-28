# Guide des Nouvelles APIs Unified Catalog

## 📅 Date de publication
**28 janvier 2026**

## 🎯 Vue d'ensemble

Ce guide présente les 3 nouvelles APIs implémentées pour Microsoft Purview Unified Catalog (version API 2025-09-15-preview) :

1. **List Hierarchy Terms** - Visualisation arborescente du glossaire
2. **Get Term Facets** - Statistiques et filtres pour les termes
3. **Get CDE Facets** - Statistiques et filtres pour les Critical Data Elements
4. **List Related Entities** - Liste complète des relations d'un terme

---

## 1️⃣ List Hierarchy Terms

### Description
Récupère la structure hiérarchique complète des termes du glossaire, organisée en arborescence parent-enfant.

### Cas d'usage
- 🌲 **Navigation arborescente** : Afficher le glossaire sous forme d'arbre interactif
- 📊 **Export de taxonomie** : Extraire la structure complète pour documentation
- ✅ **Validation** : Vérifier les relations parent-enfant
- 📖 **Documentation** : Générer des rapports de glossaire hiérarchiques

### Commande CLI

```bash
# Afficher la hiérarchie complète en vue arbre
pvw uc term hierarchy

# Hiérarchie pour un domaine spécifique
pvw uc term hierarchy --domain-id <domain-guid>

# Limiter la profondeur à 3 niveaux
pvw uc term hierarchy --max-depth 3

# Inclure les termes en brouillon
pvw uc term hierarchy --include-draft

# Vue tableau
pvw uc term hierarchy --output table

# Export JSON
pvw uc term hierarchy --output json
```

### Exemple de sortie (Tree View)

```
📚 Glossary Hierarchy (45 terms, max depth: 3)
├── Customer (PUBLISHED) - ID: a1b2c3d4...
│   ├── Individual Customer (PUBLISHED) - ID: e5f6g7h8...
│   │   └── Premium Customer (PUBLISHED) - ID: i9j0k1l2...
│   └── Corporate Customer (PUBLISHED) - ID: m3n4o5p6...
├── Product (PUBLISHED) - ID: q7r8s9t0...
│   ├── Physical Product (DRAFT) - ID: u1v2w3x4...
│   └── Digital Product (PUBLISHED) - ID: y5z6a7b8...
└── Transaction (PUBLISHED) - ID: c9d0e1f2...
    └── Online Transaction (PUBLISHED) - ID: g3h4i5j6...
```

### Exemple de sortie (Table View)

| Level | Name | ID | Status | Children |
|-------|------|----|----|----------|
| 0 | Customer | a1b2c3d4e5f6... | PUBLISHED | 2 |
| 1 | └─ Individual Customer | e5f6g7h8i9j0... | PUBLISHED | 1 |
| 2 |   └─ Premium Customer | i9j0k1l2m3n4... | PUBLISHED | - |
| 1 | └─ Corporate Customer | m3n4o5p6q7r8... | PUBLISHED | - |
| 0 | Product | q7r8s9t0u1v2... | PUBLISHED | 2 |

### Utilisation en Python

```python
from purviewcli.client import UnifiedCatalogClient

client = UnifiedCatalogClient()
args = {
    "--domain-id": ["<domain-guid>"],
    "--max-depth": ["3"]
}

result = client.get_terms_hierarchy(args)

# Parcourir la hiérarchie
for term in result.get('hierarchyTerms', []):
    print(f"Root: {term['name']}")
    for child in term.get('children', []):
        print(f"  - {child['name']}")
        for grandchild in child.get('children', []):
            print(f"    - {grandchild['name']}")
```

---

## 2️⃣ Get Term Facets

### Description
Récupère des statistiques agrégées sur les termes du glossaire, groupées par attributs (statut, domaine, propriétaire, etc.).

### Cas d'usage
- 🔍 **Filtres de recherche** : Afficher les options de filtrage avec compteurs
- 📊 **Dashboards** : Créer des graphiques de distribution
- 📈 **Rapports de gouvernance** : Analyser la composition du glossaire
- 🎯 **Métriques** : Suivre l'adoption et la qualité du glossaire

### Commande CLI

```bash
# Obtenir tous les facets
pvw uc term facets

# Facets pour un domaine spécifique
pvw uc term facets --domain-id <domain-guid>

# Facets spécifiques uniquement
pvw uc term facets --facet-fields status --facet-fields domain

# Export JSON
pvw uc term facets --output json
```

### Exemple de sortie

```
📊 Glossary Terms Facets (Total: 180 terms)

┏━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Value      ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ Active     │   123 │      68.3% │
│ Draft      │    45 │      25.0% │
│ Deprecated │    12 │       6.7% │
└────────────┴───────┴────────────┘

┏━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Value      ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ Marketing  │    56 │      31.1% │
│ Finance    │    43 │      23.9% │
│ Sales      │    34 │      18.9% │
│ IT         │    47 │      26.1% │
└────────────┴───────┴────────────┘
```

### Utilisation en Python

```python
from purviewcli.client import UnifiedCatalogClient

client = UnifiedCatalogClient()
args = {
    "--domain-id": ["<domain-guid>"]
}

facets_result = client.get_term_facets(args)

# Analyser la distribution par statut
for status, count in facets_result['facets']['status'].items():
    print(f"{status}: {count} terms")

# Calculer le pourcentage de termes publiés
total = facets_result['totalCount']
published = facets_result['facets']['status'].get('PUBLISHED', 0)
percentage = (published / total * 100) if total > 0 else 0
print(f"Terms published: {percentage:.1f}%")
```

---

## 3️⃣ Get CDE Facets

### Description
Récupère des statistiques agrégées sur les Critical Data Elements, avec focus sur la criticité, la conformité et la gouvernance.

### Cas d'usage
- 🛡️ **Dashboards de conformité** : Suivre la couverture GDPR/HIPAA/SOC2
- ⚠️ **Évaluation des risques** : Analyser la distribution des données critiques
- 📋 **Rapports réglementaires** : Générer des rapports de conformité
- 🔒 **Gouvernance** : Surveiller les données sensibles

### Commande CLI

```bash
# Obtenir tous les facets CDE
pvw uc cde facets

# Facets pour un domaine spécifique
pvw uc cde facets --domain-id <domain-guid>

# Facets spécifiques
pvw uc cde facets --facet-fields criticalityLevel --facet-fields complianceFramework

# Export JSON
pvw uc cde facets --output json
```

### Exemple de sortie

```
🔒 Critical Data Elements Facets (Total: 135 CDEs)

⚠️ CriticalityLevel Distribution
┏━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Value  ┃ Count ┃ Percentage ┃
┡━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ High   │    45 │      33.3% │  ← Rouge (alerte)
│ Medium │    67 │      49.6% │  ← Jaune
│ Low    │    23 │      17.0% │  ← Vert
└────────┴───────┴────────────┘

📋 ComplianceFramework Distribution
┏━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Value  ┃ Count ┃ Percentage ┃
┡━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ GDPR   │    34 │      25.2% │
│ HIPAA  │    12 │       8.9% │
│ SOC2   │    23 │      17.0% │
└────────┴───────┴────────────┘

🛡️ Compliance Coverage Summary:
  • GDPR: 34 CDEs
  • HIPAA: 12 CDEs
  • SOC2: 23 CDEs
```

### Utilisation en Python

```python
from purviewcli.client import UnifiedCatalogClient

client = UnifiedCatalogClient()
args = {}

facets_result = client.get_cde_facets(args)

# Analyser les données critiques
high_critical = facets_result['facets']['criticalityLevel']['High']
print(f"High criticality CDEs: {high_critical}")

# Vérifier la couverture GDPR
gdpr_count = facets_result['facets']['complianceFramework'].get('GDPR', 0)
total = facets_result['totalCount']
gdpr_coverage = (gdpr_count / total * 100) if total > 0 else 0
print(f"GDPR coverage: {gdpr_coverage:.1f}% ({gdpr_count}/{total})")

# Identifier les risques
if high_critical > 50:
    print("⚠️ WARNING: High number of critical data elements!")
```

---

## 4️⃣ List Related Entities

### Description
Liste toutes les entités liées à un terme spécifique (synonymes, termes associés, parents, domaines, etc.).

### Cas d'usage
- 🔗 **Visualisation de graphe** : Construire des vues réseau des relations
- 🎯 **Impact Analysis** : Identifier les entités affectées avant suppression
- 🧭 **Navigation** : Explorer les connexions entre termes
- 📝 **Audit** : Tracer toutes les relations d'un terme

### Commande CLI

```bash
# Obtenir toutes les relations d'un terme
pvw uc term relationships --term-id <term-guid>

# Filtrer uniquement les synonymes
pvw uc term relationships --term-id <term-guid> --relationship-type Synonym

# Filtrer les termes associés
pvw uc term relationships --term-id <term-guid> --relationship-type Related

# Filtrer les parents
pvw uc term relationships --term-id <term-guid> --relationship-type Parent

# Export JSON
pvw uc term relationships --term-id <term-guid> --output json
```

### Exemple de sortie

```
🔗 Relationships for Term (Total: 5)

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Relationship Type ┃ Entity ID            ┃ Entity Type┃ Description        ┃ Created    ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ Synonym           │ a1b2c3d4e5f6g7h8...  │ TERM       │ Alternative name   │ 2026-01-15 │
│ Synonym           │ i9j0k1l2m3n4o5p6...  │ TERM       │ French translation │ 2026-01-15 │
│ Related           │ q7r8s9t0u1v2w3x4...  │ TERM       │ Related concept    │ 2026-01-20 │
│ Related           │ y5z6a7b8c9d0e1f2...  │ TERM       │ Similar term       │ 2026-01-22 │
│ Parent            │ g3h4i5j6k7l8m9n0...  │ TERM       │ Parent category    │ 2026-01-10 │
└───────────────────┴──────────────────────┴────────────┴────────────────────┴────────────┘

Summary by Type:
  • Parent: 1
  • Related: 2
  • Synonym: 2
```

### Utilisation en Python

```python
from purviewcli.client import UnifiedCatalogClient

client = UnifiedCatalogClient()
args = {
    "--term-id": ["<term-guid>"]
}

result = client.list_related_entities(args)

# Analyser les relations par type
relationships = result.get('relationships', [])
type_counts = {}
for rel in relationships:
    rel_type = rel.get('relationshipType', 'Unknown')
    type_counts[rel_type] = type_counts.get(rel_type, 0) + 1

print(f"Total relationships: {len(relationships)}")
for rel_type, count in sorted(type_counts.items()):
    print(f"  - {rel_type}: {count}")

# Obtenir uniquement les synonymes
synonym_args = {
    "--term-id": ["<term-guid>"],
    "--relationship-type": ["Synonym"]
}
synonyms = client.list_related_entities(synonym_args)
print(f"Found {len(synonyms.get('relationships', []))} synonyms")
```

---

## 📊 Comparaison des APIs

| Fonctionnalité | Hierarchy | Term Facets | CDE Facets | Relationships |
|----------------|-----------|-------------|------------|---------------|
| **Type de données** | Structure | Statistiques | Statistiques | Relations |
| **Format de sortie** | Arbre/Table | Table | Table | Table |
| **Cas principal** | Navigation | Analytics | Conformité | Exploration |
| **Filtrage domaine** | ✅ | ✅ | ✅ | ❌ |
| **Export JSON** | ✅ | ✅ | ✅ | ✅ |
| **Pagination** | ❌ | ❌ | ❌ | ❌ |

---

## 🎨 Intégration dans des workflows

### Workflow 1 : Audit de Glossaire Complet

```bash
# 1. Obtenir la hiérarchie complète
pvw uc term hierarchy --output json > hierarchy.json

# 2. Analyser la distribution
pvw uc term facets --output json > facets.json

# 3. Examiner les relations d'un terme clé
pvw uc term relationships --term-id <term-guid> --output json > relationships.json
```

### Workflow 2 : Rapport de Conformité

```bash
# 1. Analyser les CDEs par criticité
pvw uc cde facets

# 2. Filtrer les CDEs par domaine
pvw uc cde facets --domain-id <finance-domain-guid>

# 3. Requête pour les CDEs GDPR
pvw uc cde query --status PUBLISHED --name-keyword "GDPR"
```

### Workflow 3 : Nettoyage de Relations

```python
from purviewcli.client import UnifiedCatalogClient

client = UnifiedCatalogClient()

# 1. Lister toutes les relations
term_id = "<term-guid>"
result = client.list_related_entities({"--term-id": [term_id]})

# 2. Identifier les relations obsolètes
for rel in result.get('relationships', []):
    if rel.get('description', '').startswith('DEPRECATED'):
        # 3. Supprimer la relation
        delete_args = {
            "--term-id": [term_id],
            "--entity-id": [rel['entityId']]
        }
        client.delete_term_relationship(delete_args)
        print(f"Deleted: {rel['relationshipType']} to {rel['entityId']}")
```

---

## ⚙️ Configuration et Prérequis

### Permissions requises

| API | Permission minimale |
|-----|---------------------|
| List Hierarchy Terms | **Catalog Reader** |
| Get Term Facets | **Catalog Reader** |
| Get CDE Facets | **Catalog Reader** |
| List Related Entities | **Catalog Reader** |

### Version API

Toutes ces APIs utilisent la version **2025-09-15-preview** de l'API Purview Unified Catalog.

### Installation

```bash
# Installer la dernière version de pvw-cli
pip install --upgrade purview-cli

# Vérifier l'installation
pvw --version
```

---

## 🔧 Dépannage

### Erreur : "Command not found"

**Solution** : Assurez-vous d'avoir la dernière version du CLI :
```bash
pip install --upgrade purview-cli
```

### Erreur : "No facets data available"

**Cause** : Aucune donnée dans le domaine spécifié ou API non disponible.

**Solution** :
1. Vérifier que le domaine contient des termes/CDEs
2. Retirer le filtre `--domain-id` pour voir tous les facets
3. Vérifier que l'API 2025-09-15-preview est disponible dans votre région

### Erreur : "Term not found" (List Relationships)

**Cause** : Le term-id fourni n'existe pas.

**Solution** :
```bash
# Lister les termes pour trouver l'ID correct
pvw uc term list --domain-id <domain-guid>

# Ou rechercher par nom
pvw uc term query --name-keyword "customer"
```

### Performance lente sur Hierarchy

**Cause** : Hiérarchie très profonde ou nombreux termes.

**Solution** :
```bash
# Limiter la profondeur
pvw uc term hierarchy --max-depth 3

# Filtrer par domaine
pvw uc term hierarchy --domain-id <domain-guid>
```

---

## 📚 Ressources complémentaires

- [Documentation officielle API UC](https://learn.microsoft.com/en-us/rest/api/purview/purview-unified-catalog/)
- [Guide d'import de termes](UC_TERMS_IMPORT_GUIDE.md)
- [Analyse de couverture API](../UC_API_COVERAGE_ANALYSIS.md)
- [Microsoft Purview Documentation](https://learn.microsoft.com/en-us/purview/)

---

## 🎯 Prochaines étapes recommandées

Après avoir maîtrisé ces APIs, explorez :

1. **Data Products Facets** (priorité moyenne) - Analytics pour les produits de données
2. **Objectives Facets** (priorité moyenne) - Dashboards OKR
3. **Custom integrations** - Intégrer ces APIs dans vos outils BI/Dashboards

---

**Dernière mise à jour** : 28 janvier 2026  
**Version** : v1.7.0  
**Auteur** : GitHub Copilot
