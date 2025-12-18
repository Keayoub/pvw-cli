# 📊 Visualisation du fichier CSV d'exemple

## Vue d'ensemble

Le fichier `bulk_update_example_complete.csv` contient 10 entités avec les colonnes suivantes:

```
guid | displayName | description | sourceSystem | refreshFrequency | 
lastRefreshDate | dataOwner | businessMetadata.department | businessMetadata.costCenter | 
businessMetadata.project | customAttributes.dataClassification | customAttributes.sensitivityLevel | 
customAttributes.retentionDays
```

---

## Données de chaque ligne

### 1️⃣ Customer Master Data
| Colonne | Valeur |
|---------|--------|
| **GUID** | `a1b2c3d4-e5f6-47a8-b9c0-d1e2f3a4b5c6` |
| **displayName** | Customer Master Data |
| **description** | Complete customer information from CRM system |
| **sourceSystem** | Salesforce-CRM |
| **refreshFrequency** | DAILY |
| **lastRefreshDate** | 2025-12-18 |
| **dataOwner** | crm-team@company.com |
| **Department** | Sales |
| **CostCenter** | CC-1001 |
| **Project** | CRM-Migration-2025 |
| **Classification** | PII |
| **Sensitivity** | HIGH |
| **Retention** | 2555 jours |

---

### 2️⃣ Product Catalog
| Colonne | Valeur |
|---------|--------|
| **GUID** | `b2c3d4e5-f6a7-48b9-c0d1-e2f3a4b5c6d7` |
| **displayName** | Product Catalog |
| **description** | Master product list and attributes |
| **sourceSystem** | SAP-ERP |
| **refreshFrequency** | WEEKLY |
| **lastRefreshDate** | 2025-12-15 |
| **dataOwner** | product-team@company.com |
| **Department** | Product Management |
| **CostCenter** | CC-1002 |
| **Project** | Catalog-Update-2025 |
| **Classification** | INTERNAL |
| **Sensitivity** | MEDIUM |
| **Retention** | 1825 jours |

---

### 3️⃣ Sales Orders History
| Colonne | Valeur |
|---------|--------|
| **GUID** | `c3d4e5f6-a7b8-49ca-d1e2-f3a4b5c6d7e8` |
| **displayName** | Sales Orders History |
| **description** | Historical sales transactions and details |
| **sourceSystem** | SAP-ERP |
| **refreshFrequency** | HOURLY |
| **lastRefreshDate** | 2025-12-18 |
| **dataOwner** | sales-analytics@company.com |
| **Department** | Sales |
| **CostCenter** | CC-1001 |
| **Project** | Analytics-2025 |
| **Classification** | CONFIDENTIAL |
| **Sensitivity** | HIGH |
| **Retention** | 3650 jours |

---

### 4️⃣ Marketing Campaign Metrics
| Colonne | Valeur |
|---------|--------|
| **GUID** | `d4e5f6a7-b8c9-50db-e2f3-a4b5c6d7e8f9` |
| **displayName** | Marketing Campaign Metrics |
| **description** | Campaign performance KPIs and results |
| **sourceSystem** | Salesforce-CRM |
| **refreshFrequency** | REAL_TIME |
| **lastRefreshDate** | 2025-12-18 |
| **dataOwner** | marketing-ops@company.com |
| **Department** | Marketing |
| **CostCenter** | CC-1003 |
| **Project** | Campaign-Analytics-2025 |
| **Classification** | INTERNAL |
| **Sensitivity** | LOW |
| **Retention** | 365 jours |

---

### 5️⃣ Employee Directory
| Colonne | Valeur |
|---------|--------|
| **GUID** | `e5f6a7b8-c9da-51ec-f3a4-b5c6d7e8f9a0` |
| **displayName** | Employee Directory |
| **description** | HR employee records and contact information |
| **sourceSystem** | Workday-HR |
| **refreshFrequency** | DAILY |
| **lastRefreshDate** | 2025-12-18 |
| **dataOwner** | hr-team@company.com |
| **Department** | Human Resources |
| **CostCenter** | CC-1004 |
| **Project** | HR-System-2025 |
| **Classification** | RESTRICTED |
| **Sensitivity** | CRITICAL |
| **Retention** | 7300 jours |

---

### 6️⃣ Financial Reports
| Colonne | Valeur |
|---------|--------|
| **GUID** | `f6a7b8c9-daeb-52fd-a4b5-c6d7e8f9a0b1` |
| **displayName** | Financial Reports |
| **description** | Monthly and quarterly financial statements |
| **sourceSystem** | Oracle-ERP |
| **refreshFrequency** | MONTHLY |
| **lastRefreshDate** | 2025-12-01 |
| **dataOwner** | finance-team@company.com |
| **Department** | Finance |
| **CostCenter** | CC-1005 |
| **Project** | Financial-Reporting-2025 |
| **Classification** | HIGHLY_CONFIDENTIAL |
| **Sensitivity** | CRITICAL |
| **Retention** | 10950 jours |

---

### 7️⃣ Inventory Levels
| Colonne | Valeur |
|---------|--------|
| **GUID** | `a7b8c9da-ebfc-530e-b5c6-d7e8f9a0b1c2` |
| **displayName** | Inventory Levels |
| **description** | Current stock and inventory information |
| **sourceSystem** | SAP-ERP |
| **refreshFrequency** | REAL_TIME |
| **lastRefreshDate** | 2025-12-18 |
| **dataOwner** | supply-chain@company.com |
| **Department** | Supply Chain |
| **CostCenter** | CC-1006 |
| **Project** | Inventory-2025 |
| **Classification** | INTERNAL |
| **Sensitivity** | MEDIUM |
| **Retention** | 730 jours |

---

### 8️⃣ Website Analytics
| Colonne | Valeur |
|---------|--------|
| **GUID** | `b8c9daeb-fcaf-541f-c6d7-e8f9a0b1c2d3` |
| **displayName** | Website Analytics |
| **description** | Web traffic and user behavior data |
| **sourceSystem** | Google-Analytics |
| **refreshFrequency** | DAILY |
| **lastRefreshDate** | 2025-12-18 |
| **dataOwner** | web-team@company.com |
| **Department** | Digital |
| **CostCenter** | CC-1007 |
| **Project** | Web-Analytics-2025 |
| **Classification** | PUBLIC |
| **Sensitivity** | LOW |
| **Retention** | 395 jours |

---

### 9️⃣ Social Media Metrics
| Colonne | Valeur |
|---------|--------|
| **GUID** | `c9daebfc-fbb0-5520-d7e8-f9a0b1c2d3e4` |
| **displayName** | Social Media Metrics |
| **description** | Social platform engagement and reach data |
| **sourceSystem** | Hootsuite |
| **refreshFrequency** | HOURLY |
| **lastRefreshDate** | 2025-12-18 |
| **dataOwner** | social-team@company.com |
| **Department** | Marketing |
| **CostCenter** | CC-1003 |
| **Project** | Social-Analytics-2025 |
| **Classification** | INTERNAL |
| **Sensitivity** | LOW |
| **Retention** | 180 jours |

---

### 🔟 Supply Chain Events
| Colonne | Valeur |
|---------|--------|
| **GUID** | `daebfcfd-fcb1-5631-e8f9-a0b1c2d3e4f5` |
| **displayName** | Supply Chain Events |
| **description** | Logistics and supply chain event tracking |
| **sourceSystem** | Kinaxis |
| **refreshFrequency** | REAL_TIME |
| **lastRefreshDate** | 2025-12-18 |
| **dataOwner** | logistics-team@company.com |
| **Department** | Supply Chain |
| **CostCenter** | CC-1006 |
| **Project** | Supply-Chain-2025 |
| **Classification** | INTERNAL |
| **Sensitivity** | MEDIUM |
| **Retention** | 1095 jours |

---

## 📈 Résumé statistique

| Métrique | Valeur |
|----------|--------|
| **Total entities** | 10 |
| **Source systems** | 7 (SAP-ERP, Salesforce-CRM, Workday-HR, Oracle-ERP, Google-Analytics, Hootsuite, Kinaxis) |
| **Departments** | 6 (Sales, Product Management, Human Resources, Finance, Supply Chain, Digital) |
| **Classifications** | 6 types (PII, INTERNAL, CONFIDENTIAL, RESTRICTED, HIGHLY_CONFIDENTIAL, PUBLIC) |
| **Refresh frequencies** | 4 types (DAILY, WEEKLY, HOURLY, REAL_TIME, MONTHLY) |
| **Sensitivity levels** | 3 types (CRITICAL, HIGH, MEDIUM, LOW) |

---

## 🎯 Patterns utilisés

### Classifications
```
PII                    → Données personnelles identifiables
CONFIDENTIAL           → Données confidentielles métier
INTERNAL               → Données internes (non confidentielles)
RESTRICTED             → Données avec accès restreint
HIGHLY_CONFIDENTIAL    → Données hautement confidentielles
PUBLIC                 → Données publiques
```

### Fréquences de rafraîchissement
```
REAL_TIME   → Mise à jour en continu
HOURLY      → Mise à jour toutes les heures
DAILY       → Mise à jour chaque jour
WEEKLY      → Mise à jour chaque semaine
MONTHLY     → Mise à jour chaque mois
```

### Niveaux de sensibilité
```
CRITICAL    → Critique pour l'organisation
HIGH        → Hautement sensible
MEDIUM      → Modérément sensible
LOW         → Peu sensible
```

### Jours de rétention
```
180  jours  ≈ 6 mois
365  jours  ≈ 1 an
395  jours  ≈ 13 mois
730  jours  ≈ 2 ans
1095 jours  ≈ 3 ans
1825 jours  ≈ 5 ans
2555 jours  ≈ 7 ans
3650 jours  ≈ 10 ans
7300 jours  ≈ 20 ans
10950 jours ≈ 30 ans
```

---

## ✅ Comment utiliser ce fichier

### Option 1: Test en preview
```bash
pvw entity bulk-update-csv --csv-file samples\csv\bulk_update_example_complete.csv --dry-run --debug
```

### Option 2: Exécution réelle
```bash
pvw entity bulk-update-csv --csv-file samples\csv\bulk_update_example_complete.csv --debug
```

### Option 3: Avec gestion erreurs
```bash
pvw entity bulk-update-csv \
  --csv-file samples\csv\bulk_update_example_complete.csv \
  --error-csv errors.csv \
  --debug
```

---

## 🔄 Comment adapter ce fichier

### 1. Remplacer les GUIDs
```powershell
# Exporter les GUIDs de vos entités
$gvuids = pvw search query-search --search "*" 

# Copier les GUIDs dans le CSV
```

### 2. Modifier les valeurs
Ouvrez le fichier CSV avec:
- **Excel** - Interface facile
- **VS Code** - Édition texte
- **PowerShell** - Traitement par lot

### 3. Ajouter ou supprimer colonnes
```csv
# Avant
guid,displayName,sourceSystem

# Après
guid,displayName,sourceSystem,newColumn
```

---

## 📝 Copier comme template

```bash
# Copier le fichier
cp samples\csv\bulk_update_example_complete.csv samples\csv\my_bulk_update.csv

# Éditer
code samples\csv\my_bulk_update.csv

# Utiliser
pvw entity bulk-update-csv --csv-file samples\csv\my_bulk_update.csv --debug
```

---

## 🎉 C'est prêt!

Vous avez maintenant un exemple complet avec:
- ✅ 10 entités réalistes
- ✅ Tous les types de custom attributes
- ✅ Business metadata structurée
- ✅ Valeurs réalistes et cohérentes
- ✅ Prêt à adapter à votre contexte
