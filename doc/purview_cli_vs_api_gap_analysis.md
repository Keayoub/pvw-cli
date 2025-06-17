# Purview CLI vs. Purview API (Atlas) Gap Analysis

_Last updated: 2025-06-16_

## Overview
This document compares the current Purview CLI implementation with the Apache Atlas (Purview Data Map) API surface, highlighting covered areas, gaps, and recommendations for improvement.

---

## 1. Resource Area Coverage Table

| Resource Area   | Atlas API Endpoints (examples) | CLI Module(s)         | Coverage | Notes/Gaps |
|-----------------|-------------------------------|-----------------------|----------|------------|
| Entity          | /v2/entity, /v2/entity/bulk, /v2/entity/guid/{guid}, /v2/entity/uniqueAttribute/type/{typeName}, /v2/entity/guid/{guid}/classifications, ... | entity.py              | High     | Check for audit, all bulk ops, uniqueAttribute, business metadata, labels |
| Glossary        | /v2/glossary, /v2/glossary/category, /v2/glossary/term, /v2/glossary/import, ... | glossary.py            | High     | Ensure import/export, assignment, related terms/categories supported |
| Lineage         | /v2/lineage/{guid}, /v2/lineage/uniqueAttribute/type/{typeName} | lineage.py, entity.py  | Medium   | Confirm support for all lineage query types |
| Relationship    | /v2/relationship, /v2/relationship/guid/{guid} | relationship.py         | Medium   | Check for full CRUD, bulk, and advanced relationship ops |
| Types           | /v2/types/typedefs, /v2/types/entitydef, /v2/types/classificationdef, ... | types.py                | Medium   | Ensure all type CRUD, headers, business metadata defs |
| Search          | /v2/search/basic, /v2/search/dsl, /v2/search/fulltext, /v2/search/attribute, ... | search.py               | Medium   | Add support for DSL, saved, download, suggestions |
| Collections     | (Purview-specific)             | collections.py         | High     | N/A |
| Data Product    | (Purview-specific)             | data_product.py        | High     | N/A |
| Account         | (Purview-specific)             | account.py             | High     | N/A |
| Insight, Scan, Share, Policystore, Management | (Purview-specific) | insight.py, scan.py, share.py, policystore.py, management.py | Medium   | Review for completeness |
| IndexRecovery   | /v2/indexrecovery              | (none)                 | None     | Not exposed |
| Notification    | /v2/notification/topic/{topicName} | (none)                 | None     | Not exposed |

---

## 2. Detailed Gaps & Recommendations

### Entity
- **Gaps:** Audit endpoints, some bulk operations, uniqueAttribute endpoints, business metadata, label management.
- **Recommendation:** Add missing endpoints, especially for audit and business metadata.

### Glossary
- **Gaps:** Ensure import/export, assignment, related terms/categories, and template endpoints are fully supported.
- **Recommendation:** Review and add missing glossary endpoints.

### Lineage
- **Gaps:** Confirm support for all lineage query types (by GUID, by attribute).
- **Recommendation:** Add missing lineage query support.

### Relationship
- **Gaps:** Full CRUD, bulk, and advanced relationship operations.
- **Recommendation:** Expand relationship command coverage.

### Types
- **Gaps:** CRUD for all type definitions, headers, business metadata defs.
- **Recommendation:** Ensure all type endpoints are mapped.

### Search
- **Gaps:** DSL search, saved searches, download, suggestions.
- **Recommendation:** Add advanced search features.

### Other (IndexRecovery, Notification)
- **Gaps:** Not exposed in CLI.
- **Recommendation:** Consider if needed for your use cases.

---

## 3. General Recommendations
- Regularly sync CLI with upstream API changes.
- Ensure all CLI commands delegate to business logic in `purviewcli/client/`.
- Encapsulate Azure/Purview-specific logic in `integrations/`.
- Add/expand tests in `tests/`, mirroring CLI and client structure.
- Improve CLI help and documentation for discoverability.
- Follow project and Azure best practices for error handling, extensibility, and code quality.

---

## 4. References
- [Apache Atlas REST API](https://atlas.apache.org/api/v2/index.html)
- [Purview Documentation](https://learn.microsoft.com/en-us/azure/purview/)

---

_This document is auto-generated. Please update as the CLI and API evolve._
