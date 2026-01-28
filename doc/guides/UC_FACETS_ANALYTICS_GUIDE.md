# 📊 Guide des APIs de Facets & Analytics - Unified Catalog

## Vue d'ensemble

Ce guide détaille les **4 APIs de Facets** disponibles dans Microsoft Purview Unified Catalog (2025-09-15-preview), qui permettent d'obtenir des statistiques agrégées et des vues analytiques sur les différents types de ressources.

## Table des matières

1. [Introduction aux Facets](#introduction)
2. [Get Term Facets](#term-facets)
3. [Get CDE Facets](#cde-facets)
4. [Get Data Product Facets](#data-product-facets)
5. [Get Objective Facets](#objective-facets)
6. [Comparaison des APIs](#comparaison)
7. [Cas d'usage avancés](#cas-dusage)

---

## 1. Introduction aux Facets {#introduction}

### Qu'est-ce qu'un Facet ?

Un **facet** est une statistique agrégée sur un champ spécifique d'une collection de ressources. Les facets permettent de :

- **Filtrer** rapidement les recherches par catégories
- **Analyser** la distribution des données
- **Créer des dashboards** de gouvernance
- **Identifier des tendances** et des anomalies

### Pattern commun des APIs

Toutes les APIs de facets partagent le même pattern :

```http
GET /datagovernance/catalog/{resourceType}/facets
```

**Paramètres communs** :
- `domainId` (optionnel) : Filtre par domaine de gouvernance
- `facetFields` (optionnel) : Liste des champs à agréger
- `api-version=2025-09-15-preview` (requis)

**Réponse commune** :
```json
{
  "facets": {
    "fieldName": {
      "value1": count1,
      "value2": count2
    }
  }
}
```

---

## 2. Get Term Facets {#term-facets}

### Description

Obtient des statistiques agrégées sur les **termes de glossaire**.

### Endpoint

```http
GET /datagovernance/catalog/terms/facets
```

### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `domainId` | string | Non | GUID du domaine de gouvernance |
| `facetFields` | array | Non | Champs à agréger (par défaut: tous) |
| `api-version` | string | Oui | `2025-09-15-preview` |

### Champs disponibles

- `status` : Statut du terme (Draft, Approved, Alert, Expired)
- `parentTerm` : Terme parent (pour hiérarchie)
- `owner` : Propriétaire du terme
- `steward` : Steward responsable

### Commande CLI

```bash
# Obtenir tous les facets
pvw uc term facets

# Filtrer par domaine
pvw uc term facets --domain-id "12345678-1234-1234-1234-123456789012"

# Sélectionner des champs spécifiques
pvw uc term facets --facet-fields status owner

# Export JSON
pvw uc term facets --output json > term_stats.json
```

### Client Python

```python
from purviewcli.client import PurviewClient

# Connexion
client = PurviewClient()
uc_client = client.unified_catalog()

# Tous les facets
result = uc_client.get_term_facets({})

# Filtré par domaine
result = uc_client.get_term_facets({
    "domainId": "12345678-1234-1234-1234-123456789012"
})

# Champs spécifiques
result = uc_client.get_term_facets({
    "facetFields": ["status", "owner"]
})

# Analyser les résultats
facets = result["facets"]
status_distribution = facets.get("status", {})
print(f"Draft: {status_distribution.get('Draft', 0)}")
print(f"Approved: {status_distribution.get('Approved', 0)}")
```

### Exemple de réponse

```json
{
  "facets": {
    "status": {
      "Draft": 45,
      "Approved": 230,
      "Alert": 12,
      "Expired": 3
    },
    "owner": {
      "john.doe@company.com": 120,
      "jane.smith@company.com": 95,
      "bob.johnson@company.com": 75
    }
  }
}
```

### Cas d'usage

1. **Dashboard de gouvernance** : Visualiser le statut global du glossaire
2. **KPI de qualité** : % de termes approuvés vs brouillons
3. **Workload analysis** : Distribution par propriétaire
4. **Alerts monitoring** : Termes en alerte ou expirés

---

## 3. Get CDE Facets {#cde-facets}

### Description

Obtient des statistiques agrégées sur les **Critical Data Elements (CDEs)**.

### Endpoint

```http
GET /datagovernance/catalog/criticalDataElements/facets
```

### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `domainId` | string | Non | GUID du domaine de gouvernance |
| `facetFields` | array | Non | Champs à agréger |
| `api-version` | string | Oui | `2025-09-15-preview` |

### Champs disponibles

- `status` : Statut du CDE (Active, Retired, Under Review)
- `complianceType` : Type de conformité (GDPR, HIPAA, SOC2, PCI-DSS)
- `dataClassification` : Classification (Public, Internal, Confidential, Secret)
- `owner` : Propriétaire du CDE
- `domain` : Domaine de gouvernance

### Commande CLI

```bash
# Dashboard de conformité
pvw uc cde facets

# Analyse par domaine
pvw uc cde facets --domain-id "12345678-1234-1234-1234-123456789012"

# Focus sur compliance
pvw uc cde facets --facet-fields complianceType dataClassification

# Export pour reporting
pvw uc cde facets --output json > cde_compliance.json
```

### Client Python

```python
# Analyse de conformité globale
result = uc_client.get_cde_facets({})

# Par domaine
result = uc_client.get_cde_facets({
    "domainId": "12345678-1234-1234-1234-123456789012"
})

# Compliance focus
result = uc_client.get_cde_facets({
    "facetFields": ["complianceType", "dataClassification"]
})

# Calcul de métriques
facets = result["facets"]
compliance = facets.get("complianceType", {})
total_cdes = sum(compliance.values())
gdpr_cdes = compliance.get("GDPR", 0)
gdpr_percentage = (gdpr_cdes / total_cdes * 100) if total_cdes > 0 else 0

print(f"GDPR Coverage: {gdpr_percentage:.1f}% ({gdpr_cdes}/{total_cdes})")
```

### Exemple de réponse

```json
{
  "facets": {
    "status": {
      "Active": 156,
      "Under Review": 23,
      "Retired": 8
    },
    "complianceType": {
      "GDPR": 89,
      "HIPAA": 45,
      "SOC2": 67,
      "PCI-DSS": 34
    },
    "dataClassification": {
      "Public": 12,
      "Internal": 45,
      "Confidential": 98,
      "Secret": 32
    }
  }
}
```

### Cas d'usage

1. **Compliance dashboard** : Vue d'ensemble GDPR/HIPAA/SOC2
2. **Risk assessment** : Distribution par classification
3. **Audit preparation** : Statistiques de conformité
4. **Retirement planning** : CDEs à retirer

---

## 4. Get Data Product Facets {#data-product-facets}

### Description

Obtient des statistiques agrégées sur les **Data Products**.

### Endpoint

```http
GET /datagovernance/catalog/dataProducts/facets
```

### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `domainId` | string | Non | GUID du domaine de gouvernance |
| `facetFields` | array | Non | Champs à agréger |
| `api-version` | string | Oui | `2025-09-15-preview` |

### Champs disponibles

- `status` : Statut du produit (Published, Draft, Archived)
- `domain` : Domaine de gouvernance
- `dataAssetCount` : Nombre d'assets (0, 1-5, 6-10, 11-20, 21+)
- `owner` : Propriétaire du produit

### Commande CLI

```bash
# Portfolio overview
pvw uc dataproduct facets

# Analyse par domaine
pvw uc dataproduct facets --domain-id "12345678-1234-1234-1234-123456789012"

# Focus sur status et assets
pvw uc dataproduct facets --facet-fields status dataAssetCount

# Export pour dashboard
pvw uc dataproduct facets --output json > product_portfolio.json
```

### Client Python

```python
# Portfolio complet
result = uc_client.get_data_product_facets({})

# Par domaine
result = uc_client.get_data_product_facets({
    "domainId": "12345678-1234-1234-1234-123456789012"
})

# Métriques ciblées
result = uc_client.get_data_product_facets({
    "facetFields": ["status", "dataAssetCount"]
})

# Analytics de maturité
facets = result["facets"]
status = facets.get("status", {})
total = sum(status.values())
published = status.get("Published", 0)
draft = status.get("Draft", 0)

maturity_score = (published / total * 100) if total > 0 else 0
print(f"Product Maturity: {maturity_score:.1f}%")
print(f"Ready for Production: {published}/{total}")
print(f"In Development: {draft}")
```

### Exemple de réponse

```json
{
  "facets": {
    "status": {
      "Published": 45,
      "Draft": 23,
      "Archived": 8
    },
    "domain": {
      "Finance": 28,
      "Marketing": 19,
      "Sales": 22,
      "Operations": 7
    },
    "dataAssetCount": {
      "0": 5,
      "1-5": 32,
      "6-10": 18,
      "11-20": 12,
      "21+": 9
    },
    "owner": {
      "data-team@company.com": 34,
      "analytics-team@company.com": 25,
      "bi-team@company.com": 17
    }
  }
}
```

### Cas d'usage

1. **Portfolio dashboard** : Vue d'ensemble des produits
2. **Readiness tracking** : % Published vs Draft
3. **Asset richness** : Distribution du nombre d'assets
4. **Domain distribution** : Équilibrage par domaine
5. **Ownership analysis** : Workload des équipes

---

## 5. Get Objective Facets {#objective-facets}

### Description

Obtient des statistiques agrégées sur les **Objectives (OKRs)**.

### Endpoint

```http
GET /datagovernance/catalog/objectives/facets
```

### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `domainId` | string | Non | GUID du domaine de gouvernance |
| `facetFields` | array | Non | Champs à agréger |
| `api-version` | string | Oui | `2025-09-15-preview` |

### Champs disponibles

- `status` : Statut de l'objectif (Not Started, In Progress, Completed, At Risk, Blocked)
- `period` : Période (Q1 2026, Q2 2026, H1 2026, 2026)
- `progressPercentage` : Plages de progression (0-25%, 26-50%, 51-75%, 76-100%)
- `owner` : Propriétaire de l'objectif

### Commande CLI

```bash
# OKR dashboard complet
pvw uc objective facets

# Analyse par domaine
pvw uc objective facets --domain-id "12345678-1234-1234-1234-123456789012"

# Focus sur santé OKR
pvw uc objective facets --facet-fields status progressPercentage

# Export pour reporting exécutif
pvw uc objective facets --output json > okr_health.json
```

### Client Python

```python
# Vue globale
result = uc_client.get_objective_facets({})

# Par domaine
result = uc_client.get_objective_facets({
    "domainId": "12345678-1234-1234-1234-123456789012"
})

# Health metrics
result = uc_client.get_objective_facets({
    "facetFields": ["status", "progressPercentage"]
})

# Calcul de santé OKR
facets = result["facets"]
status = facets.get("status", {})
total = sum(status.values())
completed = status.get("Completed", 0)
at_risk = status.get("At Risk", 0)
blocked = status.get("Blocked", 0)

completion_rate = (completed / total * 100) if total > 0 else 0
health_score = 100 - ((at_risk + blocked*2) / total * 100) if total > 0 else 0

print(f"OKR Completion Rate: {completion_rate:.1f}%")
print(f"OKR Health Score: {health_score:.1f}/100")
if at_risk > 0:
    print(f"⚠️ At Risk: {at_risk} objectives need attention!")
if blocked > 0:
    print(f"🚫 Blocked: {blocked} objectives are critical!")
```

### Exemple de réponse

```json
{
  "facets": {
    "status": {
      "Not Started": 8,
      "In Progress": 42,
      "Completed": 15,
      "At Risk": 12,
      "Blocked": 3
    },
    "period": {
      "Q1 2026": 25,
      "Q2 2026": 30,
      "H1 2026": 15,
      "2026": 10
    },
    "progressPercentage": {
      "0-25%": 18,
      "26-50%": 24,
      "51-75%": 21,
      "76-100%": 17
    },
    "owner": {
      "vp-engineering@company.com": 28,
      "vp-product@company.com": 25,
      "cto@company.com": 27
    }
  }
}
```

### Cas d'usage

1. **OKR health dashboard** : Vue d'ensemble de la santé OKR
2. **Completion tracking** : Taux de complétion par période
3. **Risk identification** : Objectifs à risque ou bloqués
4. **Progress distribution** : Courbe de progression
5. **Executive reporting** : Métriques pour leadership

---

## 6. Comparaison des APIs {#comparaison}

### Matrice des fonctionnalités

| Fonctionnalité | Term Facets | CDE Facets | Data Product Facets | Objective Facets |
|----------------|-------------|------------|---------------------|------------------|
| **Resource Type** | Glossary Terms | Critical Data Elements | Data Products | Objectives/OKRs |
| **Primary Use** | Glossary analytics | Compliance tracking | Portfolio management | OKR health monitoring |
| **Status Field** | ✅ Draft/Approved | ✅ Active/Retired | ✅ Published/Draft | ✅ In Progress/Completed |
| **Owner Field** | ✅ | ✅ | ✅ | ✅ |
| **Domain Filter** | ✅ | ✅ | ✅ | ✅ |
| **Compliance Field** | ❌ | ✅ complianceType | ❌ | ❌ |
| **Progress Field** | ❌ | ❌ | ❌ | ✅ progressPercentage |
| **Asset Count** | ❌ | ❌ | ✅ dataAssetCount | ❌ |
| **Period Field** | ❌ | ❌ | ❌ | ✅ period |

### Quand utiliser quelle API ?

| Scenario | API recommandée | Raison |
|----------|----------------|--------|
| Audit de conformité GDPR | CDE Facets | Champ `complianceType` dédié |
| Dashboard de maturité du glossaire | Term Facets | Statut Draft vs Approved |
| Portfolio de produits de données | Data Product Facets | Vue status + assets |
| Suivi OKR trimestriel | Objective Facets | Champs period + progress |
| Distribution des responsabilités | Toutes | Toutes ont le champ `owner` |
| Analyse par domaine | Toutes | Toutes supportent `domainId` |

---

## 7. Cas d'usage avancés {#cas-dusage}

### 7.1 Dashboard exécutif multi-facets

Combiner les 4 APIs pour créer un dashboard de gouvernance complet :

```python
def governance_executive_dashboard(domain_id=None):
    """Dashboard exécutif de gouvernance."""
    
    # Paramètres communs
    params = {"domainId": domain_id} if domain_id else {}
    
    # Récupérer tous les facets
    term_facets = uc_client.get_term_facets(params)
    cde_facets = uc_client.get_cde_facets(params)
    product_facets = uc_client.get_data_product_facets(params)
    objective_facets = uc_client.get_objective_facets(params)
    
    # Calculer KPIs
    kpis = {
        "glossary_maturity": calculate_maturity(term_facets, "status", "Approved"),
        "compliance_coverage": calculate_coverage(cde_facets, "complianceType", "GDPR"),
        "product_readiness": calculate_maturity(product_facets, "status", "Published"),
        "okr_health": calculate_health(objective_facets, "status")
    }
    
    # Afficher dashboard
    print("=== GOVERNANCE EXECUTIVE DASHBOARD ===\n")
    print(f"📚 Glossary Maturity: {kpis['glossary_maturity']:.1f}%")
    print(f"🔒 GDPR Coverage: {kpis['compliance_coverage']:.1f}%")
    print(f"📦 Product Readiness: {kpis['product_readiness']:.1f}%")
    print(f"🎯 OKR Health Score: {kpis['okr_health']:.1f}/100")
    
    return kpis

def calculate_maturity(facets_result, field, target_value):
    """Calcule le % de maturité."""
    facets = facets_result.get("facets", {}).get(field, {})
    total = sum(facets.values())
    target = facets.get(target_value, 0)
    return (target / total * 100) if total > 0 else 0

def calculate_coverage(facets_result, field, compliance_type):
    """Calcule le % de couverture d'un type de compliance."""
    facets = facets_result.get("facets", {}).get(field, {})
    total = sum(facets.values())
    covered = facets.get(compliance_type, 0)
    return (covered / total * 100) if total > 0 else 0

def calculate_health(facets_result, field):
    """Calcule le score de santé OKR."""
    facets = facets_result.get("facets", {}).get(field, {})
    total = sum(facets.values())
    if total == 0:
        return 0
    
    completed = facets.get("Completed", 0)
    at_risk = facets.get("At Risk", 0)
    blocked = facets.get("Blocked", 0)
    
    # Score: 100 - pénalités pour risques
    score = 100
    score -= (at_risk / total * 20)  # -20 points max pour at-risk
    score -= (blocked / total * 40)  # -40 points max pour blocked
    
    return max(0, score)
```

**Utilisation** :
```python
# Dashboard global
kpis = governance_executive_dashboard()

# Dashboard par domaine
finance_kpis = governance_executive_dashboard(
    domain_id="12345678-1234-1234-1234-123456789012"
)
```

### 7.2 Alerting automatique

Surveiller les seuils critiques et envoyer des alertes :

```python
def check_governance_alerts(thresholds):
    """Vérifie les seuils et génère des alertes."""
    
    alerts = []
    
    # 1. Vérifier la maturité du glossaire
    term_facets = uc_client.get_term_facets({})
    status = term_facets["facets"]["status"]
    total_terms = sum(status.values())
    draft_percentage = (status.get("Draft", 0) / total_terms * 100) if total_terms > 0 else 0
    
    if draft_percentage > thresholds["max_draft_percentage"]:
        alerts.append({
            "severity": "WARNING",
            "category": "Glossary",
            "message": f"Too many draft terms: {draft_percentage:.1f}% (threshold: {thresholds['max_draft_percentage']}%)"
        })
    
    # 2. Vérifier les CDEs expirés
    cde_facets = uc_client.get_cde_facets({})
    cde_status = cde_facets["facets"]["status"]
    retired_count = cde_status.get("Retired", 0)
    
    if retired_count > thresholds["max_retired_cdes"]:
        alerts.append({
            "severity": "INFO",
            "category": "CDE",
            "message": f"High number of retired CDEs: {retired_count} (consider cleanup)"
        })
    
    # 3. Vérifier la santé OKR
    objective_facets = uc_client.get_objective_facets({})
    obj_status = objective_facets["facets"]["status"]
    blocked_count = obj_status.get("Blocked", 0)
    at_risk_count = obj_status.get("At Risk", 0)
    
    if blocked_count > 0:
        alerts.append({
            "severity": "CRITICAL",
            "category": "OKR",
            "message": f"{blocked_count} objectives are BLOCKED - immediate action required!"
        })
    
    if at_risk_count > thresholds["max_at_risk_objectives"]:
        alerts.append({
            "severity": "WARNING",
            "category": "OKR",
            "message": f"{at_risk_count} objectives at risk (threshold: {thresholds['max_at_risk_objectives']})"
        })
    
    # 4. Vérifier les produits en brouillon
    product_facets = uc_client.get_data_product_facets({})
    prod_status = product_facets["facets"]["status"]
    total_products = sum(prod_status.values())
    draft_products = prod_status.get("Draft", 0)
    draft_percentage = (draft_products / total_products * 100) if total_products > 0 else 0
    
    if draft_percentage > thresholds["max_draft_products_percentage"]:
        alerts.append({
            "severity": "WARNING",
            "category": "Products",
            "message": f"Too many draft products: {draft_percentage:.1f}% (threshold: {thresholds['max_draft_products_percentage']}%)"
        })
    
    return alerts
```

**Utilisation** :
```python
# Définir les seuils
thresholds = {
    "max_draft_percentage": 30,  # Max 30% de termes en brouillon
    "max_retired_cdes": 20,      # Max 20 CDEs retirés
    "max_at_risk_objectives": 5, # Max 5 OKRs à risque
    "max_draft_products_percentage": 40  # Max 40% de produits en brouillon
}

# Vérifier
alerts = check_governance_alerts(thresholds)

# Traiter les alertes
for alert in alerts:
    print(f"[{alert['severity']}] {alert['category']}: {alert['message']}")
    
    # Envoyer email/Slack si CRITICAL
    if alert['severity'] == 'CRITICAL':
        send_notification(alert)
```

### 7.3 Rapport de tendances

Comparer les facets sur plusieurs périodes :

```python
import json
from datetime import datetime

def capture_facets_snapshot(domain_id=None):
    """Capture un snapshot de tous les facets."""
    
    params = {"domainId": domain_id} if domain_id else {}
    
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "domain_id": domain_id,
        "facets": {
            "terms": uc_client.get_term_facets(params),
            "cdes": uc_client.get_cde_facets(params),
            "products": uc_client.get_data_product_facets(params),
            "objectives": uc_client.get_objective_facets(params)
        }
    }
    
    # Sauvegarder
    filename = f"facets_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(snapshot, f, indent=2)
    
    return snapshot

def compare_snapshots(snapshot1, snapshot2):
    """Compare deux snapshots et calcule les tendances."""
    
    trends = {}
    
    # Comparer chaque catégorie
    for category in ["terms", "cdes", "products", "objectives"]:
        facets1 = snapshot1["facets"][category]["facets"]
        facets2 = snapshot2["facets"][category]["facets"]
        
        category_trends = {}
        
        # Comparer chaque facet
        for facet_name in facets1.keys():
            if facet_name in facets2:
                field1 = facets1[facet_name]
                field2 = facets2[facet_name]
                
                # Calculer les changements
                changes = {}
                for value in set(list(field1.keys()) + list(field2.keys())):
                    count1 = field1.get(value, 0)
                    count2 = field2.get(value, 0)
                    delta = count2 - count1
                    
                    if delta != 0:
                        changes[value] = {
                            "before": count1,
                            "after": count2,
                            "delta": delta,
                            "percentage_change": (delta / count1 * 100) if count1 > 0 else None
                        }
                
                if changes:
                    category_trends[facet_name] = changes
        
        if category_trends:
            trends[category] = category_trends
    
    return trends

def print_trends(trends):
    """Affiche les tendances de manière lisible."""
    
    print("=== GOVERNANCE TRENDS REPORT ===\n")
    
    for category, facets in trends.items():
        print(f"\n📊 {category.upper()}")
        print("-" * 60)
        
        for facet_name, changes in facets.items():
            print(f"\n  {facet_name}:")
            
            for value, change in changes.items():
                delta = change["delta"]
                symbol = "📈" if delta > 0 else "📉"
                
                pct_change = change.get("percentage_change")
                pct_str = f"({pct_change:+.1f}%)" if pct_change else ""
                
                print(f"    {symbol} {value}: {change['before']} → {change['after']} ({delta:+d}) {pct_str}")
```

**Utilisation** :
```python
# Semaine 1
snapshot_week1 = capture_facets_snapshot()

# ... attendre 1 semaine ...

# Semaine 2
snapshot_week2 = capture_facets_snapshot()

# Comparer
trends = compare_snapshots(snapshot_week1, snapshot_week2)
print_trends(trends)
```

**Exemple de sortie** :
```
=== GOVERNANCE TRENDS REPORT ===

📊 TERMS
------------------------------------------------------------

  status:
    📈 Approved: 220 → 230 (+10) (+4.5%)
    📉 Draft: 55 → 45 (-10) (-18.2%)

📊 OBJECTIVES
------------------------------------------------------------

  status:
    📈 Completed: 12 → 15 (+3) (+25.0%)
    📉 At Risk: 15 → 12 (-3) (-20.0%)
    ⚠️ Blocked: 2 → 3 (+1) (+50.0%)

  progressPercentage:
    📈 76-100%: 14 → 17 (+3) (+21.4%)
    📉 0-25%: 22 → 18 (-4) (-18.2%)
```

---

## Conclusion

Les 4 APIs de Facets fournissent une vue analytique puissante de votre environnement Purview :

1. **Term Facets** → Maturité du glossaire
2. **CDE Facets** → Conformité et classification
3. **Data Product Facets** → Portefeuille et richesse
4. **Objective Facets** → Santé OKR et progression

En combinant ces APIs, vous pouvez :
- Créer des **dashboards exécutifs** complets
- Mettre en place des **systèmes d'alerting** automatiques
- Suivre des **tendances** dans le temps
- Prendre des **décisions data-driven** sur la gouvernance

Pour plus d'informations :
- **[API Coverage Analysis](../UC_API_COVERAGE_ANALYSIS.md)** - Analyse complète
- **[New APIs Guide](UC_NEW_APIS_GUIDE.md)** - Guide des 4 premières APIs
- **[Release Notes v1.7.0](../../releases/v1.7.0.md)** - Notes de version
