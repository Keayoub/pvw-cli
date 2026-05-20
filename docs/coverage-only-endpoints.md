# Coverage-Only Endpoint Candidates

This document tracks endpoint keys in [purviewcli/client/endpoints.py](../purviewcli/client/endpoints.py) that were introduced for coverage completeness and are likely not official/stable Purview REST surface.

Source: static report from scripts/_gap_analysis.py, section "NEW FOR 100% COVERAGE OPS".

Status tags:
- client: YES = referenced by at least one client method
- client: NO = currently not referenced by client methods

## account
- get_account_info -> /account/info (client: YES)
- get_account_settings -> /account/settings (client: YES)
- update_account_settings -> /account/settings (client: YES)
- get_account_usage -> /account/usage (client: YES)
- get_account_limits -> /account/limits (client: YES)
- get_account_analytics -> /account/analytics (client: YES)

## collections
- move_collection -> /account/collections/{collectionName}/move (client: YES)
- get_collection_permissions -> /account/collections/{collectionName}/permissions (client: YES)
- update_collection_permissions -> /account/collections/{collectionName}/permissions (client: YES)
- get_collection_analytics -> /account/collections/{collectionName}/analytics (client: YES)
- export_collection -> /account/collections/{collectionName}/export (client: YES)
- import_collection -> /account/collections/{collectionName}/import (client: NO)

## discovery
- advanced_search -> /datamap/api/search/advanced (client: YES)
- faceted_search -> /datamap/api/search/facets (client: YES)
- save_search -> /datamap/api/search/saved (client: YES)
- get_saved_searches -> /datamap/api/search/saved (client: YES)
- delete_saved_search -> /datamap/api/search/saved/{searchId} (client: YES)
- search_analytics -> /datamap/api/search/analytics (client: YES)
- search_templates -> /datamap/api/search/templates (client: YES)

## entity
- get_entity_history -> /datamap/api/atlas/v2/entity/guid/{guid}/history (client: YES)
- get_entity_audit -> /datamap/api/atlas/v2/entity/guid/{guid}/audit (client: YES)
- validate_entity -> /datamap/api/atlas/v2/entity/validate (client: YES)
- get_entity_dependencies -> /datamap/api/atlas/v2/entity/guid/{guid}/dependencies (client: YES)
- get_entity_usage -> /datamap/api/atlas/v2/entity/guid/{guid}/usage (client: YES)

## glossary
- glossary_analytics -> /datamap/api/atlas/v2/glossary/{glossaryId}/analytics (client: YES)
- term_usage_statistics -> /datamap/api/atlas/v2/glossary/term/{termId}/usage (client: YES)
- glossary_approval_workflow -> /datamap/api/atlas/v2/glossary/{glossaryId}/workflow (client: YES)
- term_validation -> /datamap/api/atlas/v2/glossary/term/validate (client: YES)
- glossary_templates -> /datamap/api/atlas/v2/glossary/templates (client: YES)
- term_templates -> /datamap/api/atlas/v2/glossary/term/templates (client: YES)

## lineage
- get_upstream_lineage -> /datamap/api/atlas/v2/lineage/{guid}/upstream (client: YES)
- get_downstream_lineage -> /datamap/api/atlas/v2/lineage/{guid}/downstream (client: YES)
- get_lineage_graph -> /datamap/api/atlas/v2/lineage/{guid}/graph (client: YES)
- create_lineage -> /datamap/api/atlas/v2/lineage (client: YES)
- update_lineage -> /datamap/api/atlas/v2/lineage/{guid} (client: YES)
- delete_lineage -> /datamap/api/atlas/v2/lineage/{guid} (client: YES)
- validate_lineage -> /datamap/api/atlas/v2/lineage/validate (client: YES)
- get_impact_analysis -> /datamap/api/atlas/v2/lineage/{guid}/impact (client: YES)
- get_temporal_lineage -> /datamap/api/atlas/v2/lineage/{guid}/temporal (client: YES)

## relationship
- list_relationships -> /datamap/api/atlas/v2/relationship (client: YES)
- bulk_create_relationships -> /datamap/api/atlas/v2/relationship/bulk (client: YES)
- bulk_delete_relationships -> /datamap/api/atlas/v2/relationship/bulk (client: YES)
- get_relationships_by_entity -> /datamap/api/atlas/v2/relationship/entity/{guid} (client: YES)
- validate_relationship -> /datamap/api/atlas/v2/relationship/validate (client: YES)

## scanning
- get_scan_analytics -> /scan/datasources/{dataSourceName}/scans/{scanName}/analytics (client: YES)
- get_scan_history -> /scan/datasources/{dataSourceName}/scans/{scanName}/history (client: NO)
- schedule_scan -> /scan/datasources/{dataSourceName}/scans/{scanName}/triggers (client: YES)
- get_scan_schedule -> /scan/datasources/{dataSourceName}/scans/{scanName}/triggers/{triggerId} (client: YES)
- update_scan_schedule -> /scan/datasources/{dataSourceName}/scans/{scanName}/triggers/{triggerId} (client: YES)
- delete_scan_schedule -> /scan/datasources/{dataSourceName}/scans/{scanName}/triggers/{triggerId} (client: YES)

## types
- validate_typedef -> /datamap/api/atlas/v2/types/typedef/validate (client: YES)
- get_type_dependencies -> /datamap/api/atlas/v2/types/typedef/{name}/dependencies (client: YES)
- migrate_type_version -> /datamap/api/atlas/v2/types/typedef/{name}/migrate (client: YES)
- export_types -> /datamap/api/atlas/v2/types/typedefs/export (client: YES)
- import_types -> /datamap/api/atlas/v2/types/typedefs/import (client: YES)

Total: 55 candidate operations.
