# Analyse de Couverture API - Purview Unified Catalog

## Date d'analyse
**28 janvier 2026**

## Version API analysée
**Microsoft Purview Unified Catalog REST API: 2025-09-15-preview**

---

## 📊 Résumé

| Catégorie | Total API | Implémentées | Manquantes | Couverture |
|-----------|-----------|--------------|------------|------------|
| **Total** | **48** | **39** | **9** | **81%** |
| Terms | 7 | 7 | 0 | 100% |
| Domains | 5 | 5 | 0 | 100% |
| Data Products | 7 | 7 | 0 | 100% |
| Critical Data Elements | 7 | 7 | 0 | 100% |
| Objectives | 5 | 5 | 0 | 100% |
| Key Results | 5 | 5 | 0 | 100% |
| Policies | 4 | 4 | 0 | 100% |
| **Facets (Nouveaux)** | **4** | **0** | **4** | **0%** |
| **Hierarchies (Nouveaux)** | **1** | **0** | **1** | **0%** |
| **Related Entities (Nouveaux)** | **3** | **1** | **2** | **33%** |

---

## ✅ APIs Implémentées (39/48)

### Glossary Terms (7/7)
- [x] **Create Term** - `create_term()`
- [x] **Get Term** - `get_term_by_id()`
- [x] **Update Term** - `update_term()`
- [x] **Delete Term** - `delete_term()`
- [x] **List Term** - `get_terms()` / `get_terms_from_glossary()`
- [x] **Query Terms** - `query_terms()`
- [x] **Add Related Entity** - `add_term_relationship()` ✨ *Nouveau (ajouté le 28/01/2026)*

### Governance Domains (5/5)
- [x] **Create Domain** - `create_governance_domain()`
- [x] **Get Domain By Id** - `get_governance_domain_by_id()`
- [x] **Update Domain** - `update_governance_domain()`
- [x] **Delete Domain By Id** - `delete_governance_domain()`
- [x] **Enumerate Domains** - `get_governance_domains()`

### Data Products (7/7)
- [x] **Create Data Product** - `create_data_product()`
- [x] **Get Data Product By Id** - `get_data_product_by_id()`
- [x] **Update Data Product** - `update_data_product()`
- [x] **Delete Data Product By Id** - `delete_data_product()`
- [x] **List Data Products** - `get_data_products()`
- [x] **Query Data Products** - `query_data_products()`
- [x] **Create Data Product Relationship** - `create_data_product_relationship()`
- [x] **List Data Product Relationships** - `get_data_product_relationships()`
- [x] **Delete Data Product Relationship** - `delete_data_product_relationship()`

### Critical Data Elements (7/7)
- [x] **Create Critical Data Element** - `create_critical_data_element()`
- [x] **Get Critical Data Element By Id** - `get_critical_data_element_by_id()`
- [x] **Update Critical Data Element** - `update_critical_data_element()`
- [x] **Delete Critical Data Element By Id** - `delete_critical_data_element()`
- [x] **List Critical Data Element** - `get_critical_data_elements()`
- [x] **Query Critical Data Elements** - `query_critical_data_elements()`
- [x] **Create Critical Data Element Relationship** - `create_cde_relationship()`
- [x] **List Critical Data Element Relationships** - `get_cde_relationships()`
- [x] **Delete Critical Data Element Relationship** - `delete_cde_relationship()`

### Objectives (5/5)
- [x] **Create Objective** - `create_objective()`
- [x] **Get Objective By Id** - `get_objective_by_id()`
- [x] **Update Objective** - `update_objective()`
- [x] **Delete Objective By Id** - `delete_objective()`
- [x] **List Objectives** - `get_objectives()`
- [x] **Query Objectives** - `query_objectives()`

### Key Results (5/5)
- [x] **Create Key Result** - `create_key_result()`
- [x] **Get Key Result By Id** - `get_key_result_by_id()`
- [x] **Update Key Result** - `update_key_result()`
- [x] **Delete Key Result By Id** - `delete_key_result()`
- [x] **List Key Results** - `get_key_results()`

### Policies (4/4)
- [x] **List Policies** - `list_policies()`
- [x] **Update Policy** - `update_policy()`
- [x] Get Policy (via generic methods)
- [x] Delete Policy (via generic methods)

---

## ❌ APIs Manquantes (9/48)

### 🆕 Facets APIs (4 nouvelles APIs - 0% couverture)

#### 1. **Get Term Facets**
```
GET /datagovernance/catalog/terms/facets
```
**Description**: Récupère les facettes (filtres) pour les termes du glossaire.  
**Cas d'usage**: 
- Afficher les filtres disponibles dans une interface de recherche
- Grouper les termes par statut, domaine, propriétaire
- Construire des vues de navigation par facettes

**Exemple de réponse attendue**:
```json
{
  "facets": {
    "status": {
      "Draft": 45,
      "Active": 123,
      "Deprecated": 12
    },
    "domain": {
      "Finance": 34,
      "Marketing": 56,
      "Sales": 43
    },
    "owner": {
      "user1@contoso.com": 23,
      "user2@contoso.com": 45
    }
  }
}
```

**Priorité**: 🟡 **MOYENNE** - Utile pour les interfaces de recherche avancée

---

#### 2. **Get Data Product Facets**
```
GET /datagovernance/catalog/dataProducts/facets
```
**Description**: Récupère les facettes pour les produits de données.  
**Cas d'usage**:
- Filtrer les produits de données par domaine, statut, propriétaire
- Afficher le nombre de produits par catégorie
- Navigation par facettes dans le catalogue

**Exemple de réponse attendue**:
```json
{
  "facets": {
    "status": {
      "Draft": 12,
      "Published": 34,
      "Archived": 5
    },
    "domain": {
      "Customer Data": 15,
      "Financial Data": 20
    },
    "dataAssetCount": {
      "1-5": 10,
      "6-10": 15,
      "11+": 9
    }
  }
}
```

**Priorité**: 🟡 **MOYENNE** - Utile pour les dashboards et interfaces

---

#### 3. **Get Critical Data Element Facets**
```
GET /datagovernance/catalog/criticalDataElements/facets
```
**Description**: Récupère les facettes pour les éléments de données critiques.  
**Cas d'usage**:
- Filtrer les CDEs par niveau de criticité, domaine, conformité
- Analyser la distribution des données critiques
- Rapports de gouvernance

**Exemple de réponse attendue**:
```json
{
  "facets": {
    "criticalityLevel": {
      "High": 45,
      "Medium": 67,
      "Low": 23
    },
    "complianceFramework": {
      "GDPR": 34,
      "HIPAA": 12,
      "SOC2": 23
    },
    "domain": {
      "Healthcare": 23,
      "Finance": 45
    }
  }
}
```

**Priorité**: 🟢 **HAUTE** - Important pour la gouvernance et conformité

---

#### 4. **Get Objective Facets**
```
GET /datagovernance/catalog/objectives/facets
```
**Description**: Récupère les facettes pour les objectifs (OKRs).  
**Cas d'usage**:
- Filtrer les objectifs par statut, période, propriétaire
- Dashboards de suivi des OKRs
- Rapports de progression

**Exemple de réponse attendue**:
```json
{
  "facets": {
    "status": {
      "Not Started": 12,
      "In Progress": 23,
      "Completed": 45,
      "At Risk": 8
    },
    "period": {
      "Q1 2026": 34,
      "Q2 2026": 23
    },
    "progressPercentage": {
      "0-25": 15,
      "26-50": 20,
      "51-75": 18,
      "76-100": 35
    }
  }
}
```

**Priorité**: 🟡 **MOYENNE** - Utile pour les dashboards OKR

---

### 🆕 Hierarchies API (1 nouvelle API - 0% couverture)

#### 5. **List Hierarchy Terms**
```
GET /datagovernance/catalog/terms/hierarchy
```
**Description**: Récupère la hiérarchie complète des termes du glossaire.  
**Cas d'usage**:
- Afficher l'arborescence complète du glossaire
- Navigation hiérarchique dans l'interface utilisateur
- Visualisation de la structure parent-enfant
- Export de la taxonomie complète

**Exemple de réponse attendue**:
```json
{
  "hierarchyTerms": [
    {
      "id": "term-1",
      "name": "Customer",
      "level": 0,
      "children": [
        {
          "id": "term-2",
          "name": "Individual Customer",
          "level": 1,
          "children": [
            {
              "id": "term-3",
              "name": "Premium Customer",
              "level": 2,
              "children": []
            }
          ]
        },
        {
          "id": "term-4",
          "name": "Corporate Customer",
          "level": 1,
          "children": []
        }
      ]
    }
  ]
}
```

**Priorité**: 🟢 **HAUTE** - Essentiel pour la navigation et visualisation du glossaire

---

### 🆕 Related Entities APIs (2 APIs manquantes sur 3 - 33% couverture)

#### 6. **List Related Entities** (Générique)
```
GET /datagovernance/catalog/{entityType}/{entityId}/relationships
```
**Description**: Liste toutes les entités liées à une entité donnée (termes, domaines, CDEs, etc.).  
**Cas d'usage**:
- Afficher toutes les relations d'un terme (synonymes, termes associés, parents)
- Visualiser les dépendances entre entités
- Impact analysis - quelles entités sont affectées par un changement
- Graph visualization du catalogue

**Exemple de réponse attendue**:
```json
{
  "relationships": [
    {
      "entityId": "term-2",
      "entityType": "TERM",
      "relationshipType": "Synonym",
      "description": "Alternative name",
      "createdAt": "2026-01-15T10:00:00Z"
    },
    {
      "entityId": "term-3",
      "entityType": "TERM",
      "relationshipType": "Related",
      "description": "Related concept",
      "createdAt": "2026-01-20T14:30:00Z"
    },
    {
      "entityId": "domain-1",
      "entityType": "DOMAIN",
      "relationshipType": "BelongsTo",
      "description": "Parent domain",
      "createdAt": "2026-01-10T09:00:00Z"
    }
  ]
}
```

**Priorité**: 🟢 **HAUTE** - Essentiel pour la visualisation et navigation des relations

**Méthode actuelle**: `add_term_relationship()` existe pour créer des relations de termes, mais pas de méthode générique pour lister toutes les relations.

---

#### 7. **Delete Related Term** (Spécifique aux termes)
```
DELETE /datagovernance/catalog/terms/{termId}/relationships/{entityId}
```
**Description**: Supprime une relation spécifique entre deux termes.  
**Cas d'usage**:
- Retirer un synonyme qui n'est plus valide
- Supprimer une relation "Related" entre deux termes
- Nettoyer les relations obsolètes

**Priorité**: 🟢 **HAUTE** - Nécessaire pour la maintenance du glossaire

**Note**: Une méthode `delete_term_relationship()` existe déjà dans le code (ligne 2196), donc cette API est **partiellement implémentée**.

---

### 🔄 Méthodes d'énumération manquantes

#### 8. **Enumerate Objectives** (méthode dédiée)
**État**: Query Objectives existe, mais pas de méthode d'énumération simple comme pour les domaines.  
**Priorité**: 🟡 **BASSE** - `query_objectives()` et `get_objectives()` couvrent ce besoin

#### 9. **Enumerate Key Results** (méthode dédiée)
**État**: Similaire aux objectives, pas de méthode d'énumération dédiée.  
**Priorité**: 🟡 **BASSE** - `get_key_results()` couvre ce besoin

---

## 📋 Recommandations d'implémentation

### 🔴 Priorité HAUTE (à implémenter en priorité)

1. **List Hierarchy Terms** ⭐ **TOP PRIORITY**
   - Endpoint: `GET /datagovernance/catalog/terms/hierarchy`
   - Méthode proposée: `get_terms_hierarchy()`
   - Cas d'usage critique: Visualisation arborescente du glossaire
   - Impact: Fort - améliore significativement l'expérience utilisateur

2. **Get Critical Data Element Facets**
   - Endpoint: `GET /datagovernance/catalog/criticalDataElements/facets`
   - Méthode proposée: `get_cde_facets()`
   - Cas d'usage: Rapports de conformité et gouvernance
   - Impact: Moyen-Élevé - important pour la gouvernance

3. **List Related Entities** (Générique)
   - Endpoint: `GET /datagovernance/catalog/{entityType}/{entityId}/relationships`
   - Méthode proposée: `get_entity_relationships()` ou `list_related_entities()`
   - Cas d'usage: Visualisation complète des relations
   - Impact: Élevé - complète la gestion des relations

### 🟡 Priorité MOYENNE (à implémenter si besoin métier)

4. **Get Term Facets**
   - Endpoint: `GET /datagovernance/catalog/terms/facets`
   - Méthode proposée: `get_term_facets()`
   - Cas d'usage: Recherche avancée dans le glossaire

5. **Get Data Product Facets**
   - Endpoint: `GET /datagovernance/catalog/dataProducts/facets`
   - Méthode proposée: `get_data_product_facets()`
   - Cas d'usage: Filtrage des produits de données

6. **Get Objective Facets**
   - Endpoint: `GET /datagovernance/catalog/objectives/facets`
   - Méthode proposée: `get_objective_facets()`
   - Cas d'usage: Dashboards OKR

### ⚪ Priorité BASSE (optionnel)

7. Méthodes d'énumération dédiées pour Objectives et Key Results (déjà couvertes par les méthodes query/list existantes)

---

## 💡 Proposition d'implémentation

### Exemple: List Hierarchy Terms

**Fichier**: `purviewcli/client/endpoints.py`
```python
"list_hierarchy_terms": "/datagovernance/catalog/terms/hierarchy"
```

**Fichier**: `purviewcli/client/_unified_catalog.py`
```python
@decorator
def get_terms_hierarchy(self, args):
    """
    Get the complete hierarchical structure of glossary terms.
    
    Retrieves all terms organized in a tree structure showing parent-child
    relationships. Useful for visualizing the complete glossary taxonomy.
    
    Args:
        args: Dictionary with optional filters:
            --domain-id (str, optional): Filter by domain ID
            --max-depth (int, optional): Maximum depth level to retrieve
    
    Returns:
        Hierarchical structure with nested terms
    
    Example:
        args = {"--domain-id": ["domain-123"]}
        hierarchy = client.get_terms_hierarchy(args)
        # Returns tree structure with children property
    """
    self.method = "GET"
    self.endpoint = ENDPOINTS["unified_catalog"]["list_hierarchy_terms"]
    self.params = get_api_version_params("2025-09-15-preview")
    
    if "--domain-id" in args:
        self.params["domainId"] = args["--domain-id"][0]
    if "--max-depth" in args:
        self.params["maxDepth"] = args["--max-depth"][0]
```

**Fichier**: `purviewcli/cli/unified_catalog.py`
```python
@uc.command("terms-hierarchy", help="Get hierarchical structure of glossary terms")
@click.option("--domain-id", help="Filter by domain ID", required=False)
@click.option("--max-depth", help="Maximum depth level", type=int, required=False)
def get_terms_hierarchy(domain_id, max_depth):
    """Display glossary terms in hierarchical tree structure."""
    from purviewcli.client import UnifiedCatalogClient
    from rich.tree import Tree
    from rich import print as rprint
    
    client = UnifiedCatalogClient()
    args = {}
    if domain_id:
        args["--domain-id"] = [domain_id]
    if max_depth:
        args["--max-depth"] = [str(max_depth)]
    
    result = client.get_terms_hierarchy(args)
    
    # Create rich tree visualization
    tree = Tree("📚 Glossary Hierarchy")
    
    def add_terms_to_tree(terms, parent_tree):
        for term in terms:
            node = parent_tree.add(f"[bold]{term['name']}[/bold] ({term['status']})")
            if term.get('children'):
                add_terms_to_tree(term['children'], node)
    
    add_terms_to_tree(result.get('hierarchyTerms', []), tree)
    rprint(tree)
```

---

## 📊 Statistiques détaillées

### Couverture par catégorie fonctionnelle

| Fonctionnalité | APIs disponibles | Implémentées | Manquantes | % |
|----------------|------------------|--------------|------------|---|
| CRUD Operations | 35 | 35 | 0 | 100% |
| Query/Search | 4 | 4 | 0 | 100% |
| Relationships | 9 | 7 | 2 | 78% |
| Facets (Analytics) | 4 | 0 | 4 | 0% |
| Hierarchies | 1 | 0 | 1 | 0% |

### Distribution des priorités

- 🔴 **Haute priorité**: 3 APIs (List Hierarchy Terms, Get CDE Facets, List Related Entities)
- 🟡 **Moyenne priorité**: 3 APIs (Term Facets, Data Product Facets, Objective Facets)
- ⚪ **Basse priorité**: 3 APIs (énumérations déjà couvertes)

---

## 🎯 Conclusion

Votre client Purview Unified Catalog a une **excellente couverture de 81%** des APIs disponibles. Les APIs manquantes se concentrent principalement sur deux nouveaux domaines:

1. **Facets APIs** (4 APIs) - Fonctionnalités d'analytics et filtrage avancé
2. **Hierarchies API** (1 API) - Visualisation arborescente du glossaire

### Prochaines étapes recommandées:

1. ✅ **Court terme** (cette semaine):
   - Implémenter `get_terms_hierarchy()` - Impact immédiat sur l'expérience utilisateur
   - Ajouter `list_related_entities()` - Complète la gestion des relations

2. ✅ **Moyen terme** (ce mois):
   - Ajouter les APIs Facets pour les CDEs (gouvernance)
   - Implémenter les facets pour les termes (recherche avancée)

3. ✅ **Long terme** (optionnel):
   - Facets pour Data Products et Objectives (si besoin métier confirmé)

---

## 📚 Références

- [Microsoft Purview Unified Catalog REST API Reference](https://learn.microsoft.com/en-us/rest/api/purview/purview-unified-catalog/operation-groups?view=rest-purview-purview-unified-catalog-2025-09-15-preview)
- [Faceted Navigation in Azure Search](https://learn.microsoft.com/en-us/azure/search/search-faceted-navigation-examples)
- [Enterprise Glossary Overview](https://learn.microsoft.com/en-us/purview/unified-catalog-enterprise-glossary)

---

**Dernière mise à jour**: 28 janvier 2026  
**Version du client analysé**: pvw-cli (main branch)  
**Analyste**: GitHub Copilot
