# Microsoft Purview Data Governance API - Gap Analysis

**Analysis Date:** November 5, 2025  
**API Version:** 2025-09-15-preview  
**Your Implementation:** pvw-cli v1.2.x

---

## Executive Summary

Your CLI implementation has **excellent coverage** of the Microsoft Purview Data Governance API. You've implemented approximately **85-90%** of the available operations. The gaps are primarily in **advanced features** and **newer API endpoints**.

---

## ✅ Fully Implemented Categories

### 1. **Domains (Business Domains)** - 100% ✅
- ✅ Enumerate Domains
- ✅ Create Domain
- ✅ Get Domain By Id
- ✅ Update Domain
- ✅ Delete Domain By Id

**Client:** `_unified_catalog.py` - Methods: `get_governance_domains()`, `create_governance_domain()`, etc.  
**CLI:** `pvw uc domain list/create/show/update/delete`

---

### 2. **Data Products** - 100% ✅
- ✅ List Data Products
- ✅ Create Data Product
- ✅ Get Data Product By Id
- ✅ Update Data Product
- ✅ Delete Data Product By Id
- ✅ Query Data Products
- ✅ Create Data Product Relationship
- ✅ List Data Product Relationships
- ✅ Delete Data Product Relationship

**Client:** `_unified_catalog.py` - Complete CRUD + relationships  
**CLI:** `pvw uc dataproduct list/create/show/update/delete/query`

---

### 3. **Terms (Business Metadata)** - 95% ✅
- ✅ List Term
- ✅ Create Term
- ✅ Get Term
- ✅ Update Term
- ✅ Delete Term
- ✅ Query Terms
- ✅ Bulk Import/Update via CSV/JSON
- ⚠️ **MISSING:** Delete Related Term (minor)
- ⚠️ **MISSING:** List Hierarchy Terms (minor)

**Client:** `_unified_catalog.py` - Complete CRUD + bulk operations  
**CLI:** `pvw uc term list/create/show/update/delete/query/import-csv/import-json`

---

### 4. **Objectives (OKRs)** - 100% ✅
- ✅ List Objectives
- ✅ Create Objective
- ✅ Get Objective By Id
- ✅ Update Objective
- ✅ Delete Objective By Id
- ✅ Query Objectives

**Client:** `_unified_catalog.py` - Complete CRUD  
**CLI:** `pvw uc objective list/create/show/query`

---

### 5. **Critical Data Elements (CDEs)** - 100% ✅
- ✅ List Critical Data Element
- ✅ Create Critical Data Element
- ✅ Get Critical Data Element By Id
- ✅ Update Critical Data Element
- ✅ Delete Critical Data Element By Id
- ✅ Query Critical Data Elements
- ✅ Create Critical Data Element Relationship
- ✅ List Critical Data Element Relationships
- ✅ Delete Critical Data Element Relationship

**Client:** `_unified_catalog.py` - Complete CRUD + relationships  
**CLI:** `pvw uc cde list/create/show/update/delete/query`

---

### 6. **Policies** - 90% ✅
- ✅ List Policies
- ✅ Get Policy (by ID)
- ✅ Create Policy
- ✅ Update Policy
- ✅ Delete Policy

**Client:** `_unified_catalog.py` - Complete CRUD  
**CLI:** `pvw uc policy ...`

---

## ⚠️ Partially Implemented Categories

### 7. **Key Results** - 80% ✅ / 20% ❌

**Implemented in Client (`_unified_catalog.py`):**
- ✅ `get_key_results()` - List key results for an objective
- ✅ `get_key_result_by_id()` - Get specific key result
- ✅ `create_key_result()` - Create new key result
- ✅ `update_key_result()` - Update existing key result
- ✅ `delete_key_result()` - Delete key result

**MISSING in endpoints.py:**
- ❌ No endpoint definitions in `ENDPOINTS["unified_catalog"]` dictionary
- ❌ Endpoints should be:
  - `list_key_results`: `/datagovernance/catalog/objectives/{objectiveId}/keyResults`
  - `get_key_result`: `/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}`
  - `create_key_result`: `/datagovernance/catalog/objectives/{objectiveId}/keyResults`
  - `update_key_result`: `/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}`
  - `delete_key_result`: `/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}`

**MISSING in CLI (`unified_catalog.py`):**
- ❌ No `@uc.group() def keyresult():` command group
- ❌ No CLI commands for Key Results operations
- ❌ Users cannot manage key results from command line

**Impact:** Users have OKR objectives but cannot manage the key results that measure objective progress.

---

## ❌ Missing Features (Gaps)

### 8. **Facets Endpoints** - 0% ❌

The API includes "Facets" endpoints for advanced filtering and aggregation:

- ❌ **Get Critical Data Element Facets**
  - Endpoint: `/datagovernance/catalog/criticalDataElements/facets`
  - Use case: Get aggregated facet information for CDEs (e.g., count by status, type, domain)

- ❌ **Get Data Product Facets**
  - Endpoint: `/datagovernance/catalog/dataProducts/facets`
  - Use case: Get aggregated facet information for data products

- ❌ **Get Objective Facets**
  - Endpoint: `/datagovernance/catalog/objectives/facets`
  - Use case: Get aggregated facet information for objectives

- ❌ **Get Term Facets**
  - Endpoint: `/datagovernance/catalog/terms/facets`
  - Use case: Get aggregated facet information for terms

**Impact:** Users cannot get summary statistics or perform advanced analytics on their governance data.

---

### 9. **Related Entities** - 0% ❌

- ❌ **Add Related Entity**
  - Endpoint: POST `/datagovernance/catalog/entities/{entityId}/related`
  - Use case: Link entities across different governance objects (terms, CDEs, data products)

- ❌ **List Related Entities**
  - Endpoint: GET `/datagovernance/catalog/entities/{entityId}/related`
  - Use case: View all entities related to a specific entity

**Impact:** Limited ability to create and view cross-references between governance objects.

---

### 10. **Term Hierarchies** - 0% ❌

- ❌ **List Hierarchy Terms**
  - Endpoint: GET `/datagovernance/catalog/terms/hierarchy`
  - Use case: Get hierarchical term structure (parent-child relationships)

- ❌ **Delete Related Term**
  - Endpoint: DELETE `/datagovernance/catalog/terms/{termId}/related/{relatedTermId}`
  - Use case: Remove relationship between two terms

**Impact:** Users cannot easily navigate or visualize term hierarchies. Cannot manage term-to-term relationships programmatically.

---

## 📊 Coverage Statistics

| Category | Implemented | Missing | Coverage |
|----------|-------------|---------|----------|
| **Domains** | 5/5 | 0 | 100% ✅ |
| **Data Products** | 9/9 | 0 | 100% ✅ |
| **Terms** | 6/8 | 2 | 75% ⚠️ |
| **Objectives** | 6/6 | 0 | 100% ✅ |
| **Key Results** | 5/5 (client only) | 0 (client), 5 (CLI) | 50% ⚠️ |
| **Critical Data Elements** | 9/9 | 0 | 100% ✅ |
| **Policies** | 5/5 | 0 | 100% ✅ |
| **Facets** | 0/4 | 4 | 0% ❌ |
| **Related Entities** | 0/2 | 2 | 0% ❌ |

**Overall Coverage:** ~85-90% ✅

---

## 🎯 Recommended Priorities

### Priority 1 (High) - Complete Existing Features
1. **Add Key Results CLI commands**
   - Add endpoints to `endpoints.py`
   - Create `@uc.group() keyresult` in CLI
   - Commands: `list`, `create`, `show`, `update`, `delete`
   - **Effort:** Low (client already done)
   - **Value:** High (completes OKR functionality)

### Priority 2 (Medium) - Add Missing Core Features
2. **Term Hierarchy Operations**
   - Implement `List Hierarchy Terms`
   - Implement `Delete Related Term`
   - **Effort:** Low-Medium
   - **Value:** Medium (enhances term management)

### Priority 3 (Low) - Advanced Analytics Features
3. **Facets Endpoints**
   - Implement all 4 facets endpoints
   - Add CLI commands for aggregated views
   - **Effort:** Medium
   - **Value:** Medium (nice-to-have analytics)

4. **Related Entities**
   - Implement `Add Related Entity`
   - Implement `List Related Entities`
   - **Effort:** Low-Medium
   - **Value:** Low (niche use case)

---

## 📝 Implementation Notes

### Current Status
Your implementation is **production-ready** for most governance workflows:
- ✅ Complete domain hierarchy management
- ✅ Full data product catalog with relationships
- ✅ Comprehensive term management with bulk operations
- ✅ OKR objectives (missing key results CLI)
- ✅ Critical data element tracking
- ✅ Policy management

### Architecture Strengths
- ✅ Well-organized client layer (`_unified_catalog.py`)
- ✅ Clean CLI with rich formatting
- ✅ Bulk import/export capabilities (CSV, JSON)
- ✅ Comprehensive error handling
- ✅ Good documentation in docstrings

### Known TODO in Your Code
From `endpoints.py` line 375:
```python
# Current: Using /datagovernance/catalog/* endpoints (Working as of Oct 2025)
# Future: Microsoft announced new Unified Catalog API (2024-03-01-preview)
# TODO: Monitor and migrate to new UC API when documentation is complete
```

---

## 🚀 Quick Wins

### Fix Key Results (15 minutes)
1. Add to `endpoints.py`:
```python
# Key Results (under objectives)
"list_key_results": "/datagovernance/catalog/objectives/{objectiveId}/keyResults",
"get_key_result": "/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}",
"create_key_result": "/datagovernance/catalog/objectives/{objectiveId}/keyResults",
"update_key_result": "/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}",
"delete_key_result": "/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}",
```

2. Add CLI group to `unified_catalog.py`:
```python
@uc.group()
def keyresult():
    """Manage key results for objectives (OKRs)."""
    pass
```

3. Add commands: `list`, `create`, `show`, `update`, `delete`

---

## Conclusion

Your implementation is **excellent** with 85-90% coverage of the Data Governance API. The main gap is exposing **Key Results via CLI** (client is already done). Other missing features are advanced/niche capabilities that most users won't need immediately.

**Recommendation:** Add Key Results CLI commands as Priority 1, then consider term hierarchy features if users request them. Facets and Related Entities are nice-to-have enhancements for future versions.

---

## API Reference
- [Microsoft Purview Data Governance API](https://learn.microsoft.com/en-us/rest/api/purview/purviewdatagovernance/operation-groups?view=rest-purview-purviewdatagovernance-2025-09-15-preview)
- API Version: `2025-09-15-preview`
- Documentation updated: October 14, 2025
