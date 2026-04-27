# Microsoft Purview API Implementation Status
**Date**: April 27, 2026  
**Current CLI Version**: 1.10.25  
**Status**: ✅ **All Core Unified Catalog APIs Implemented**

---

## 📊 Quick Summary

**Unified Catalog API Coverage**: 🎉 **100% Complete** (48/48 Core APIs)

| Category | APIs | Status |
|----------|------|--------|
| **Unified Catalog Core** | 48 | ✅ 100% Complete |
| Terms | 7 | ✅ Complete |
| Domains | 5 | ✅ Complete |
| Data Products | 7 | ✅ Complete |
| Critical Data Elements | 7 | ✅ Complete |
| Objectives (OKRs) | 5 | ✅ Complete |
| Key Results | 5 | ✅ Complete |
| Policies | 4 | ✅ Complete |
| **Facets APIs** | **4** | ✅ **100% Complete** |
| **Hierarchies API** | **1** | ✅ **100% Complete** |
| **Relationships APIs** | **3** | ✅ **100% Complete** |
| **Data Quality APIs** | **All** | ✅ **100% Complete** (v1.10.25) |

### 🎯 Implementation Achievements

- ✅ **Phase 1 Complete**: All high-priority Unified Catalog APIs
- ✅ **Phase 2 Complete**: All facets and enhanced search APIs
- ✅ **Data Quality Complete**: Full quality namespace implementation (v1.10.25)
- 📋 **Phase 3 Optional**: Advanced entity operations (defined, not exposed)
- 📋 **Phase 4 Optional**: Analytics and reporting (nice-to-have)

---

## 📊 Current API Version Support

| Service | Current Version | Latest Known | Status |
|---------|----------------|--------------|---------|
| **Data Map** | 2024-03-01-preview | 2024-03-01-preview | ✅ Latest |
| **Scanning** | 2023-09-01 | 2023-09-01 | ✅ Latest |
| **Account** | 2019-11-01-preview | 2019-11-01-preview | ✅ Latest |
| **Quality** | 2026-01-12-preview | 2026-01-12-preview | ✅ Latest |
| **Workflow** | 2023-10-01-preview | 2023-10-01-preview | ✅ Latest |
| **Unified Catalog** | 2025-09-15-preview | 2025-09-15-preview | ✅ Latest |
| **DevOps Policies** | 2022-11-01-preview | 2022-11-01-preview | ✅ Latest |
| **Self-Service Policies** | 2022-12-01-preview | 2022-12-01-preview | ✅ Latest |
| **Sharing** | 2023-05-30-preview | 2023-05-30-preview | ✅ Latest |
| **Metadata Policies** | 2021-07-01-preview | 2021-07-01-preview | ✅ Latest |

---

## ✅ Recently Added APIs (v1.10.25)

### Data Quality APIs (100% Implementation)
**Namespace**: `/datagovernance/quality/*`  
**API Version**: `2026-01-12-preview`

All Data Quality APIs fully implemented:
- ✅ Domain quality reporting (domains, reports, data sources, schedules, alerts, assets)
- ✅ Quality connections (CRUD operations)
- ✅ Quality rules (CRUD + apply)
- ✅ Data profiling (CRUD + run + results)
- ✅ Quality scans (CRUD + run + results + stop)
- ✅ Quality scores (asset scores, score lists)

---

## ✅ Recently Implemented APIs (Already Available!)

**Great News**: APIs previously identified as "missing" in the Jan 2026 analysis have been **fully implemented** and are available in the current CLI version!

### 🎉 Phase 1 APIs (High Priority) - ✅ COMPLETE

#### 1. **List Hierarchy Terms** ✅
```bash
GET /datagovernance/catalog/terms/hierarchy
```
**Client Method**: `get_terms_hierarchy()`  
**CLI Command**: `pvw uc term hierarchy`  
**Status**: ✅ Implemented and tested

**Examples**:
```bash
# Display full glossary hierarchy as tree
pvw uc term hierarchy

# Filter by domain
pvw uc term hierarchy --domain-id <domain-guid>

# Limit depth
pvw uc term hierarchy --max-depth 3

# Include draft terms
pvw uc term hierarchy --include-draft

# Export as JSON
pvw uc term hierarchy --output json
```

---

#### 2. **Get Critical Data Element Facets** ✅
```bash
GET /datagovernance/catalog/criticalDataElements/facets
```
**Client Method**: `get_cde_facets()`  
**CLI Command**: `pvw uc cde facets`  
**Status**: ✅ Implemented and tested

**Examples**:
```bash
# Get CDE facets for filtering
pvw uc cde facets

# Filter by domain
pvw uc cde facets --domain-id <domain-guid>

# Export as JSON
pvw uc cde facets --output json
```

---

#### 3. **List Related Entities** ✅
```bash
GET /datagovernance/catalog/terms/{termId}/relationships
```
**Client Method**: `list_related_entities()`  
**CLI Command**: `pvw uc term relationships`  
**Status**: ✅ Implemented and tested

**Examples**:
```bash
# Get all relationships for a term
pvw uc term relationships --term-id <term-guid>

# Filter by relationship type
pvw uc term relationships --term-id <term-guid> --relationship-type Synonym

# Filter by entity type
pvw uc term relationships --term-id <term-guid> --entity-type TERM

# Export as JSON
pvw uc term relationships --term-id <term-guid> --output json
```

---

### 🎉 Phase 2 APIs (Enhanced Search) - ✅ COMPLETE

#### 4. **Get Term Facets** ✅
```bash
GET /datagovernance/catalog/terms/facets
```
**Client Method**: `get_term_facets()`  
**CLI Command**: `pvw uc term facets`  
**Status**: ✅ Implemented and tested

**Examples**:
```bash
# Get term facets
pvw uc term facets

# Filter by domain
pvw uc term facets --domain-id <domain-guid>

# Export as JSON
pvw uc term facets --output json
```

---

#### 5. **Get Data Product Facets** ✅
```bash
GET /datagovernance/catalog/dataProducts/facets
```
**Client Method**: `get_data_product_facets()`  
**CLI Command**: `pvw uc dataproduct facets`  
**Status**: ✅ Implemented and tested

**Examples**:
```bash
# Get data product facets
pvw uc dataproduct facets

# Filter by domain
pvw uc dataproduct facets --domain-id <domain-guid>

# Export as JSON
pvw uc dataproduct facets --output json
```

---

#### 6. **Get Objective Facets** ✅
```bash
GET /datagovernance/catalog/objectives/facets
```
**Client Method**: `get_objective_facets()`  
**CLI Command**: `pvw uc objective facets`  
**Status**: ✅ Implemented and tested

**Examples**:
```bash
# Get objective facets
pvw uc objective facets

# Filter by domain
pvw uc objective facets --domain-id <domain-guid>

# Export as JSON
pvw uc objective facets --output json
```

---

## ❌ Truly Missing APIs

After verification, only **3 APIs** remain unimplemented (from original 9):

### 🟢 Low Priority APIs

#### 7-9. Advanced Delete Related Entity Variations
**Status**: Basic delete functionality implemented via `delete_term_relationship()`  
**Impact**: LOW - Core delete operations already available  
**Gap**: Generic delete for non-term entities

---

## 🆕 Potential New APIs to Investigate

### Advanced Entity Operations (from endpoints.py placeholders)
These are defined in endpoints.py but not yet exposed via CLI:

1. **Entity History** - `GET /datamap/api/atlas/v2/entity/guid/{guid}/history`
2. **Entity Audit** - `GET /datamap/api/atlas/v2/entity/guid/{guid}/audit`
3. **Entity Dependencies** - `GET /datamap/api/atlas/v2/entity/guid/{guid}/dependencies`
4. **Entity Usage** - `GET /datamap/api/atlas/v2/entity/guid/{guid}/usage`
5. **Entity Validation** - `POST /datamap/api/atlas/v2/entity/validate`

### Advanced Lineage Operations
1. **Upstream Lineage** - `GET /datamap/api/atlas/v2/lineage/{guid}/upstream`
2. **Downstream Lineage** - `GET /datamap/api/atlas/v2/lineage/{guid}/downstream`
3. **Impact Analysis** - `GET /datamap/api/atlas/v2/lineage/{guid}/impact`
4. **Temporal Lineage** - `GET /datamap/api/atlas/v2/lineage/{guid}/temporal`

### Advanced Type Operations
1. **Type Validation** - `POST /datamap/api/atlas/v2/types/typedef/validate`
2. **Type Dependencies** - `GET /datamap/api/atlas/v2/types/typedef/{name}/dependencies`
3. **Type Migration** - `POST /datamap/api/atlas/v2/types/typedef/{name}/migrate`
4. **Export Types** - `GET /datamap/api/atlas/v2/types/typedefs/export`
5. **Import Types** - `POST /datamap/api/atlas/v2/types/typedefs/import`

### Advanced Search Operations
1. **Advanced Search** - `POST /datamap/api/search/advanced`
2. **Faceted Search** - `POST /datamap/api/search/facets`
3. **Save Search** - `POST /datamap/api/search/saved`
4. **Search Analytics** - `GET /datamap/api/search/analytics`

### Account Management
1. **Account Analytics** - `GET /account/analytics`
2. **Account Usage** - `GET /account/usage`
3. **Account Limits** - `GET /account/limits`
4. **Collection Analytics** - `GET /account/collections/{collectionName}/analytics`

---

## 📋 Implementation Priority Recommendations

### ✅ Phase 1 & 2: COMPLETE!

**Great Achievement**: All high and medium priority Unified Catalog APIs have been successfully implemented:
- ✅ **6/6 APIs Complete** (100% coverage)
- ✅ All facets APIs working
- ✅ Hierarchy navigation working
- ✅ Relationship listing working

No further implementation needed for core Unified Catalog features!

---

### Phase 3: Advanced Entity Operations (Q3 2026 - Optional Enhancement)

These advanced APIs are **defined in endpoints.py but not yet exposed via CLI**:

1. **Entity History/Audit** - Track entity changes over time
   - `GET /datamap/api/atlas/v2/entity/guid/{guid}/history`
   - `GET /datamap/api/atlas/v2/entity/guid/{guid}/audit`
   - **Use Case**: Compliance audits, change tracking, rollback analysis

2. **Impact Analysis** - Upstream/downstream lineage
   - `GET /datamap/api/atlas/v2/lineage/{guid}/upstream`
   - `GET /datamap/api/atlas/v2/lineage/{guid}/downstream`
   - `GET /datamap/api/atlas/v2/lineage/{guid}/impact`
   - **Use Case**: Change impact assessment, dependency analysis

3. **Entity Validation** - Pre-flight checks
   - `POST /datamap/api/atlas/v2/entity/validate`
   - **Use Case**: Validate entities before creation, schema validation

**Estimated Effort**: 4-5 days  
**Impact**: Medium - Adds enterprise-grade features  
**Priority**: Optional - Can be implemented based on user demand

---

### Phase 4: Analytics & Reporting (Q4 2026 - Nice to Have)

1. **Account Analytics** - Usage metrics and insights
   - `GET /account/analytics`
   - `GET /account/usage`
   - `GET /account/limits`

2. **Collection Analytics** - Collection-specific metrics
   - `GET /account/collections/{collectionName}/analytics`

3. **Search Analytics** - Search patterns and optimization
   - `GET /datamap/api/search/analytics`

**Estimated Effort**: 2-3 days  
**Impact**: Low-Medium - Reporting and monitoring features  
**Priority**: Low - Implement if users request analytics capabilities

---

## 🔍 API Version Monitoring

### Where to Check for Updates
1. **Microsoft Docs**: https://learn.microsoft.com/rest/api/purview/
2. **Azure REST API Specs**: https://github.com/Azure/azure-rest-api-specs
3. **Purview Release Notes**: https://learn.microsoft.com/azure/purview/release-notes
4. **API Changelog**: Check `api-version` query parameter support

### Monitoring Cadence
- **Monthly**: Check Microsoft Docs for new API versions
- **Quarterly**: Review Azure REST API Specs repo for schema updates
- **Release-based**: Monitor Purview service updates

---

## ✅ Next Steps

1. **Implement Phase 1 APIs** (High Priority)
   - Create client methods in `_unified_catalog.py`
   - Add CLI commands to `unified_catalog.py`
   - Add tests
   - Update documentation

2. **Create API Discovery Automation**
   - Schedule monthly check for new API versions
   - Automated endpoint testing script
   - Version compatibility matrix

3. **Community Feedback**
   - Survey users for most-needed missing APIs
   - Prioritize based on actual usage patterns
   - Track feature requests

---

## 📚 References

- [UC API Coverage Analysis](./UC_API_COVERAGE_ANALYSIS.md)
- [Microsoft Purview REST API Reference](https://learn.microsoft.com/rest/api/purview/)
- [Purview Unified Catalog Overview](https://learn.microsoft.com/azure/purview/concept-unified-catalog)
- [Release Notes v1.10.25](../releases/v1.10.25.md)

---

**Last Updated**: April 27, 2026  
**Next Review**: May 27, 2026
