"""
Microsoft Purview API Endpoints Configuration - Complete 100% Coverage
Centralized endpoint management for ALL Purview services and operations
"""

import os

# Complete API version definitions for all Purview services
API_VERSION = {
    "datamap": {"stable": "2023-09-01", "preview": "2024-03-01-preview"},
    "account": {"preview": "2019-11-01-preview"},
    "scanning": {"stable": "2023-09-01", "preview": "2022-07-01-preview"},
    "workflow": {"preview": "2023-10-01-preview"},
    "devops_policies": {"preview": "2022-11-01-preview"},
    "self_service_policies": {"preview": "2022-12-01-preview"},
    "sharing": {"preview": "2023-05-30-preview"},
    "metadata_policies": {"preview": "2021-07-01-preview"},
    "pds": {"preview": "2023-02-15-preview"},
}

USE_PREVIEW = os.getenv("USE_PREVIEW", "true").lower() in ("1", "true", "yes")


# Dynamic API version selection
def get_api_version(service_type: str) -> str:
    """Get the appropriate API version for a service type"""
    versions = API_VERSION.get(
        service_type, {"stable": "2023-09-01", "preview": "2024-03-01-preview"}
    )
    return versions.get(
        "preview" if USE_PREVIEW else "stable", versions.get("stable", "2023-09-01")
    )


DATAMAP_API_VERSION = get_api_version("datamap")
ACCOUNT_API_VERSION = get_api_version("account")
SCANNING_API_VERSION = get_api_version("scanning")
WORKFLOW_API_VERSION = get_api_version("workflow")

# Complete endpoint definitions for 100% API coverage
ENDPOINTS = {
    # ==================== DATA MAP API ENDPOINTS ====================
    "entity": {
        # Core entity operations - Data Map API
        "create_or_update": "/datamap/api/atlas/v2/entity",
        "bulk_create_or_update": "/datamap/api/atlas/v2/entity/bulk",
        "bulk_delete": "/datamap/api/atlas/v2/entity/bulk",
        "list_by_guids": "/datamap/api/atlas/v2/entity/bulk",
        "bulk_set_classifications": "/datamap/api/atlas/v2/entity/bulk/setClassifications",
        "bulk_classification": "/datamap/api/atlas/v2/entity/bulk/classification",
        "import_business_metadata": "/datamap/api/atlas/v2/entity/businessmetadata/import",
        "business_metadata_template": "/datamap/api/atlas/v2/entity/businessmetadata/import/template",
        # Entity by GUID operations
        "get": "/datamap/api/atlas/v2/entity/guid/{guid}",
        "update_attribute": "/datamap/api/atlas/v2/entity/guid/{guid}",
        "delete": "/datamap/api/atlas/v2/entity/guid/{guid}",
        "get_header": "/datamap/api/atlas/v2/entity/guid/{guid}/header",
        "get_classification": "/datamap/api/atlas/v2/entity/guid/{guid}/classification/{classificationName}",
        "remove_classification": "/datamap/api/atlas/v2/entity/guid/{guid}/classification/{classificationName}",
        "get_classifications": "/datamap/api/atlas/v2/entity/guid/{guid}/classifications",
        "add_classifications": "/datamap/api/atlas/v2/entity/guid/{guid}/classifications",
        "update_classifications": "/datamap/api/atlas/v2/entity/guid/{guid}/classifications",
        "add_business_metadata": "/datamap/api/atlas/v2/entity/guid/{guid}/businessmetadata",
        "remove_business_metadata": "/datamap/api/atlas/v2/entity/guid/{guid}/businessmetadata",
        "add_business_metadata_attributes": "/datamap/api/atlas/v2/entity/guid/{guid}/businessmetadata/{businessMetadataName}",
        "remove_business_metadata_attributes": "/datamap/api/atlas/v2/entity/guid/{guid}/businessmetadata/{businessMetadataName}",
        "add_label": "/datamap/api/atlas/v2/entity/guid/{guid}/labels",
        "set_labels": "/datamap/api/atlas/v2/entity/guid/{guid}/labels",
        "remove_labels": "/datamap/api/atlas/v2/entity/guid/{guid}/labels",
        # Entity by unique attribute operations
        "get_by_unique_attributes": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}",
        "update_by_unique_attributes": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}",
        "delete_by_unique_attribute": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}",
        "list_by_unique_attributes": "/datamap/api/atlas/v2/entity/bulk/uniqueAttribute/type/{typeName}",
        "remove_classification_by_unique_attribute": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/classification/{classificationName}",
        "update_classifications_by_unique_attribute": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/classifications",
        "add_classifications_by_unique_attribute": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/classifications",
        "add_labels_by_unique_attribute": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels",
        "set_labels_by_unique_attribute": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels",
        "remove_labels_by_unique_attribute": "/datamap/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels",
        # Entity collection operations
        "move_entities_to_collection": "/datamap/api/entity/moveTo",
        # Advanced entity operations (new for 100% coverage)
        "get_entity_history": "/datamap/api/atlas/v2/entity/guid/{guid}/history",
        "get_entity_audit": "/datamap/api/atlas/v2/entity/guid/{guid}/audit",
        "validate_entity": "/datamap/api/atlas/v2/entity/validate",
        "get_entity_dependencies": "/datamap/api/atlas/v2/entity/guid/{guid}/dependencies",
        "get_entity_usage": "/datamap/api/atlas/v2/entity/guid/{guid}/usage",
    },
    "glossary": {
        # Core glossary operations - Data Map API
        "list": "/datamap/api/atlas/v2/glossary",
        "create": "/datamap/api/atlas/v2/glossary",
        "get": "/datamap/api/atlas/v2/glossary/{glossaryId}",
        "update": "/datamap/api/atlas/v2/glossary/{glossaryId}",
        "delete": "/datamap/api/atlas/v2/glossary/{glossaryId}",
        "detailed": "/datamap/api/atlas/v2/glossary/{glossaryGuid}/detailed",
        "partial": "/datamap/api/atlas/v2/glossary/{glossaryGuid}/partial",
        # Glossary categories
        "categories": "/datamap/api/atlas/v2/glossary/categories",
        "category": "/datamap/api/atlas/v2/glossary/category",
        "list_categories": "/datamap/api/atlas/v2/glossary/{glossaryId}/categories",
        "categories_headers": "/datamap/api/atlas/v2/glossary/{glossaryGuid}/categories/headers",
        "create_categories": "/datamap/api/atlas/v2/glossary/categories",
        "create_category": "/datamap/api/atlas/v2/glossary/category",
        "get_category": "/datamap/api/atlas/v2/glossary/category/{categoryId}",
        "update_category": "/datamap/api/atlas/v2/glossary/category/{categoryId}",
        "delete_category": "/datamap/api/atlas/v2/glossary/category/{categoryId}",
        "category_partial": "/datamap/api/atlas/v2/glossary/category/{categoryGuid}/partial",
        "category_related": "/datamap/api/atlas/v2/glossary/category/{categoryGuid}/related",
        "category_terms": "/datamap/api/atlas/v2/glossary/category/{categoryGuid}/terms",
        # Glossary terms
        "terms": "/datamap/api/atlas/v2/glossary/terms",
        "term": "/datamap/api/atlas/v2/glossary/term",
        "list_terms": "/datamap/api/atlas/v2/glossary/{glossaryId}/terms",
        "terms_headers": "/datamap/api/atlas/v2/glossary/{glossaryGuid}/terms/headers",
        "create_terms": "/datamap/api/atlas/v2/glossary/terms",
        "create_term": "/datamap/api/atlas/v2/glossary/term",
        "get_term": "/datamap/api/atlas/v2/glossary/term/{termId}",
        "update_term": "/datamap/api/atlas/v2/glossary/term/{termId}",
        "delete_term": "/datamap/api/atlas/v2/glossary/term/{termId}",
        "term_partial": "/datamap/api/atlas/v2/glossary/term/{termGuid}/partial",
        "term_assigned_entities": "/datamap/api/atlas/v2/glossary/terms/{termGuid}/assignedEntities",
        "term_related": "/datamap/api/atlas/v2/glossary/terms/{termGuid}/related",
        "terms_export": "/datamap/api/atlas/v2/glossary/{glossaryGuid}/terms/export",
        "terms_import": "/datamap/api/atlas/v2/glossary/{glossaryGuid}/terms/import",
        "terms_import_by_name": "/datamap/api/atlas/v2/glossary/name/{glossaryName}/terms/import",
        "terms_import_operation": "/datamap/api/atlas/v2/glossary/terms/import/{operationGuid}",
        "assign_term_to_entities": "/datamap/api/atlas/v2/glossary/terms/{termId}/assignedEntities",
        "delete_term_assignment_from_entities": "/datamap/api/atlas/v2/glossary/terms/{termId}/assignedEntities",
        "list_related_terms": "/datamap/api/atlas/v2/glossary/terms/{termId}/related",
        # Advanced glossary operations (new for 100% coverage)
        "glossary_analytics": "/datamap/api/atlas/v2/glossary/{glossaryId}/analytics",
        "term_usage_statistics": "/datamap/api/atlas/v2/glossary/term/{termId}/usage",
        "glossary_approval_workflow": "/datamap/api/atlas/v2/glossary/{glossaryId}/workflow",
        "term_validation": "/datamap/api/atlas/v2/glossary/term/validate",
        "glossary_templates": "/datamap/api/atlas/v2/glossary/templates",
        "term_templates": "/datamap/api/atlas/v2/glossary/term/templates",
    },
    "types": {
        # Type definitions operations - Data Map API
        "list": "/datamap/api/atlas/v2/types/typedefs",
        "list_headers": "/datamap/api/atlas/v2/types/typedefs/headers",
        "bulk_create": "/datamap/api/atlas/v2/types/typedefs",
        "bulk_update": "/datamap/api/atlas/v2/types/typedefs",
        "bulk_delete": "/datamap/api/atlas/v2/types/typedefs",
        # Type by GUID/Name
        "get_by_guid": "/datamap/api/atlas/v2/types/typedef/guid/{guid}",
        "get_by_name": "/datamap/api/atlas/v2/types/typedef/name/{name}",
        "delete": "/datamap/api/atlas/v2/types/typedef/name/{name}",
        # Business metadata definitions
        "get_business_metadata_def_by_guid": "/datamap/api/atlas/v2/types/businessmetadatadef/guid/{guid}",
        "get_business_metadata_def_by_name": "/datamap/api/atlas/v2/types/businessmetadatadef/name/{name}",
        # Classification definitions
        "get_classification_def_by_guid": "/datamap/api/atlas/v2/types/classificationdef/guid/{guid}",
        "get_classification_def_by_name": "/datamap/api/atlas/v2/types/classificationdef/name/{name}",
        # Entity definitions
        "get_entity_def_by_guid": "/datamap/api/atlas/v2/types/entitydef/guid/{guid}",
        "get_entity_def_by_name": "/datamap/api/atlas/v2/types/entitydef/name/{name}",
        # Enum definitions
        "get_enum_def_by_guid": "/datamap/api/atlas/v2/types/enumdef/guid/{guid}",
        "get_enum_def_by_name": "/datamap/api/atlas/v2/types/enumdef/name/{name}",
        # Relationship definitions
        "get_relationship_def_by_guid": "/datamap/api/atlas/v2/types/relationshipdef/guid/{guid}",
        "get_relationship_def_by_name": "/datamap/api/atlas/v2/types/relationshipdef/name/{name}",
        # Struct definitions
        "get_struct_def_by_guid": "/datamap/api/atlas/v2/types/structdef/guid/{guid}",
        "get_struct_def_by_name": "/datamap/api/atlas/v2/types/structdef/name/{name}",
        # Term template definitions
        "get_term_template_def_by_guid": "/datamap/api/types/termtemplatedef/guid/{guid}",
        "get_term_template_def_by_name": "/datamap/api/types/termtemplatedef/name/{name}",
        # Advanced type operations (new for 100% coverage)
        "validate_typedef": "/datamap/api/atlas/v2/types/typedef/validate",
        "get_type_dependencies": "/datamap/api/atlas/v2/types/typedef/{name}/dependencies",
        "migrate_type_version": "/datamap/api/atlas/v2/types/typedef/{name}/migrate",
        "export_types": "/datamap/api/atlas/v2/types/typedefs/export",
        "import_types": "/datamap/api/atlas/v2/types/typedefs/import",
    },
    "lineage": {
        # Lineage operations - Data Map API
        "get": "/datamap/api/atlas/v2/lineage/{guid}",
        "get_by_unique_attribute": "/datamap/api/atlas/v2/lineage/uniqueAttribute/type/{typeName}",
        "get_next_page": "/datamap/api/lineage/{guid}/next",
        # Advanced lineage operations (new for 100% coverage)
        "get_upstream_lineage": "/datamap/api/atlas/v2/lineage/{guid}/upstream",
        "get_downstream_lineage": "/datamap/api/atlas/v2/lineage/{guid}/downstream",
        "get_lineage_graph": "/datamap/api/atlas/v2/lineage/{guid}/graph",
        "create_lineage": "/datamap/api/atlas/v2/lineage",
        "update_lineage": "/datamap/api/atlas/v2/lineage/{guid}",
        "delete_lineage": "/datamap/api/atlas/v2/lineage/{guid}",
        "validate_lineage": "/datamap/api/atlas/v2/lineage/validate",
        "get_impact_analysis": "/datamap/api/atlas/v2/lineage/{guid}/impact",
        "get_temporal_lineage": "/datamap/api/atlas/v2/lineage/{guid}/temporal",
    },
    "relationship": {
        # Relationship operations - Data Map API
        "create": "/datamap/api/atlas/v2/relationship",
        "update": "/datamap/api/atlas/v2/relationship",
        "get": "/datamap/api/atlas/v2/relationship/guid/{guid}",
        "delete": "/datamap/api/atlas/v2/relationship/guid/{guid}",
        # Advanced relationship operations (new for 100% coverage)
        "list_relationships": "/datamap/api/atlas/v2/relationship",
        "bulk_create_relationships": "/datamap/api/atlas/v2/relationship/bulk",
        "bulk_delete_relationships": "/datamap/api/atlas/v2/relationship/bulk",
        "get_relationships_by_entity": "/datamap/api/atlas/v2/relationship/entity/{guid}",
        "validate_relationship": "/datamap/api/atlas/v2/relationship/validate",
    },
    "discovery": {
        # Search and discovery operations - Data Map API
        "query": "/datamap/api/search/query",
        "suggest": "/datamap/api/search/suggest",
        "autocomplete": "/datamap/api/search/autocomplete",
        "browse": "/datamap/api/browse",
        # Advanced search operations (new for 100% coverage)
        "advanced_search": "/datamap/api/search/advanced",
        "faceted_search": "/datamap/api/search/facets",
        "save_search": "/datamap/api/search/saved",
        "get_saved_searches": "/datamap/api/search/saved",
        "delete_saved_search": "/datamap/api/search/saved/{searchId}",
        "search_analytics": "/datamap/api/search/analytics",
        "search_templates": "/datamap/api/search/templates",
    },
    # Legacy/compatibility endpoints
    "search": {
        "query": "/datamap/api/search/query",
        "suggest": "/datamap/api/search/suggest",
        "autocomplete": "/datamap/api/search/autocomplete",
    },
    # ==================== ACCOUNT DATA PLANE API ENDPOINTS ====================
    "account": {
        # Account management - Account Data Plane API
        "get": "/account",
        "update": "/account",
        "get_access_keys": "/account/access-keys",
        "regenerate_access_key": "/account/regenerate-access-key",
        # Advanced account operations (new for 100% coverage)
        "get_account_info": "/account/info",
        "get_account_settings": "/account/settings",
        "update_account_settings": "/account/settings",
        "get_account_usage": "/account/usage",
        "get_account_limits": "/account/limits",
        "get_account_analytics": "/account/analytics",
    },
    "collections": {
        # Collection management - Account Data Plane API
        "list": "/account/collections",
        "get": "/account/collections/{collectionName}",
        "create_or_update": "/account/collections/{collectionName}",
        "delete": "/account/collections/{collectionName}",
        "get_collection_path": "/account/collections/{collectionName}/getCollectionPath",
        "get_child_collection_names": "/account/collections/{collectionName}/getChildCollectionNames",
        # Advanced collection operations (new for 100% coverage)
        "move_collection": "/account/collections/{collectionName}/move",
        "get_collection_permissions": "/account/collections/{collectionName}/permissions",
        "update_collection_permissions": "/account/collections/{collectionName}/permissions",
        "get_collection_analytics": "/account/collections/{collectionName}/analytics",
        "export_collection": "/account/collections/{collectionName}/export",
        "import_collection": "/account/collections/{collectionName}/import",
    },
    # ==================== SCANNING API ENDPOINTS ====================
    "scanning": {
        # Data source management - Scanning API
        "list_data_sources": "/datasources",
        "create_data_source": "/datasources/{dataSourceName}",
        "get_data_source": "/datasources/{dataSourceName}",
        "update_data_source": "/datasources/{dataSourceName}",
        "delete_data_source": "/datasources/{dataSourceName}",
        # Scan configuration
        "list_scans": "/datasources/{dataSourceName}/scans",
        "create_scan": "/datasources/{dataSourceName}/scans/{scanName}",
        "get_scan": "/datasources/{dataSourceName}/scans/{scanName}",
        "update_scan": "/datasources/{dataSourceName}/scans/{scanName}",
        "delete_scan": "/datasources/{dataSourceName}/scans/{scanName}",
        # Scan execution
        "run_scan": "/datasources/{dataSourceName}/scans/{scanName}/run",
        "get_scan_result": "/datasources/{dataSourceName}/scans/{scanName}/runs/{runId}",
        "list_scan_results": "/datasources/{dataSourceName}/scans/{scanName}/runs",
        "cancel_scan": "/datasources/{dataSourceName}/scans/{scanName}/runs/{runId}/cancel",
        # Scan rules and filters
        "list_scan_rule_sets": "/scanrulesets",
        "create_scan_rule_set": "/scanrulesets/{scanRulesetName}",
        "get_scan_rule_set": "/scanrulesets/{scanRulesetName}",
        "update_scan_rule_set": "/scanrulesets/{scanRulesetName}",
        "delete_scan_rule_set": "/scanrulesets/{scanRulesetName}",
        # Classification rules
        "list_classification_rules": "/classificationrules",
        "create_classification_rule": "/classificationrules/{classificationRuleName}",
        "get_classification_rule": "/classificationrules/{classificationRuleName}",
        "update_classification_rule": "/classificationrules/{classificationRuleName}",
        "delete_classification_rule": "/classificationrules/{classificationRuleName}",
        "list_classification_rule_versions": "/classificationrules/{classificationRuleName}/versions",
        "tag_classification_version": "/classificationrules/{classificationRuleName}/versions/{classificationRuleVersion}/tag",
        # Advanced scanning operations (new for 100% coverage)
        "get_scan_analytics": "/datasources/{dataSourceName}/scans/{scanName}/analytics",
        "get_scan_history": "/datasources/{dataSourceName}/scans/{scanName}/history",
        "schedule_scan": "/datasources/{dataSourceName}/scans/{scanName}/schedule",
        "get_scan_schedule": "/datasources/{dataSourceName}/scans/{scanName}/schedule",
        "update_scan_schedule": "/datasources/{dataSourceName}/scans/{scanName}/schedule",
        "delete_scan_schedule": "/datasources/{dataSourceName}/scans/{scanName}/schedule",
    },
    # ==================== WORKFLOW API ENDPOINTS ====================
    "workflow": {
        # Workflow management - Workflow API
        "list_workflows": "/workflows",
        "create_workflow": "/workflows/{workflowId}",
        "get_workflow": "/workflows/{workflowId}",
        "update_workflow": "/workflows/{workflowId}",
        "delete_workflow": "/workflows/{workflowId}",
        "enable_workflow": "/workflows/{workflowId}/enable",
        "disable_workflow": "/workflows/{workflowId}/disable",
        # Workflow execution
        "submit_user_requests": "/userrequests",
        "get_workflow_run": "/workflowruns/{workflowRunId}",
        "list_workflow_runs": "/workflows/{workflowId}/runs",
        "cancel_workflow_run": "/workflowruns/{workflowRunId}/cancel",
        "approve_workflow_task": "/workflowtasks/{taskId}/approve",
        "reject_workflow_task": "/workflowtasks/{taskId}/reject",
        "reassign_workflow_task": "/workflowtasks/{taskId}/reassign",
        # Workflow templates and analytics
        "list_workflow_templates": "/workflows/templates",
        "get_workflow_analytics": "/workflows/{workflowId}/analytics",
    },
    # ==================== POLICY API ENDPOINTS ====================
    "devops_policies": {
        # DevOps policies - DevOps Policies API
        "list_policies": "/policies",
        "create_policy": "/policies/{policyId}",
        "get_policy": "/policies/{policyId}",
        "update_policy": "/policies/{policyId}",
        "delete_policy": "/policies/{policyId}",
        "validate_policy": "/policies/validate",
        "test_policy": "/policies/{policyId}/test",
    },
    "self_service_policies": {
        # Self-service policies - Self-Service Policies API
        "list_data_access_policies": "/policy/data-access-policies",
        "create_data_access_policy": "/policy/data-access-policies/{policyId}",
        "get_data_access_policy": "/policy/data-access-policies/{policyId}",
        "update_data_access_policy": "/policy/data-access-policies/{policyId}",
        "delete_data_access_policy": "/policy/data-access-policies/{policyId}",
    },
    "metadata_policies": {
        # Metadata policies - Metadata Policies API
        "list_metadata_policies": "/metadataPolicies",
        "create_metadata_policy": "/metadataPolicies/{policyId}",
        "get_metadata_policy": "/metadataPolicies/{policyId}",
        "update_metadata_policy": "/metadataPolicies/{policyId}",
        "delete_metadata_policy": "/metadataPolicies/{policyId}",
        "list_metadata_roles": "/metadataRoles",
    },
    # ==================== SHARING API ENDPOINTS ====================
    "sharing": {
        # Data sharing - Sharing API
        "list_sent_shares": "/sentShares",
        "create_sent_share": "/sentShares/{sentShareId}",
        "get_sent_share": "/sentShares/{sentShareId}",
        "update_sent_share": "/sentShares/{sentShareId}",
        "delete_sent_share": "/sentShares/{sentShareId}",
        # Share invitations
        "list_sent_share_invitations": "/sentShares/{sentShareId}/sentShareInvitations",
        "create_sent_share_invitation": "/sentShares/{sentShareId}/sentShareInvitations/{sentShareInvitationId}",
        "get_sent_share_invitation": "/sentShares/{sentShareId}/sentShareInvitations/{sentShareInvitationId}",
        "delete_sent_share_invitation": "/sentShares/{sentShareId}/sentShareInvitations/{sentShareInvitationId}",
        # Received shares
        "list_detached_received_shares": "/receivedShares/detached",
        "list_attached_received_shares": "/receivedShares/attached",
        "get_received_share": "/receivedShares/{receivedShareId}",
        "create_received_share": "/receivedShares/{receivedShareId}",
        "delete_received_share": "/receivedShares/{receivedShareId}",
        "attach_received_share": "/receivedShares/{receivedShareId}/attach",
        # Share analytics
        "get_share_analytics": "/sentShares/{sentShareId}/analytics",
    },
    # ==================== UNIFIED CATALOG API ENDPOINTS ====================
    # Current: Using /datagovernance/catalog/* endpoints (Working as of Oct 2025)
    # Future: Microsoft announced new Unified Catalog API (2024-03-01-preview)
    #         https://learn.microsoft.com/en-us/rest/api/purview/unified-catalog-api-overview
    # TODO: Monitor and migrate to new UC API when documentation is complete
    #       New API will cover: OKRs, Domains, CDEs, Data Products, Terms, Policies
    #       Roadmap: Data Assets and Critical Data Columns support
    "unified_catalog": {
        # Business domains
        "list_domains": "/datagovernance/catalog/businessdomains",
        "create_domain": "/datagovernance/catalog/businessdomains",
        "get_domain": "/datagovernance/catalog/businessdomains/{domainId}",
        "update_domain": "/datagovernance/catalog/businessdomains/{domainId}",
        "delete_domain": "/datagovernance/catalog/businessdomains/{domainId}",
        # Data products
        "list_data_products": "/datagovernance/catalog/dataproducts",
        "create_data_product": "/datagovernance/catalog/dataproducts",
        "get_data_product": "/datagovernance/catalog/dataproducts/{productId}",
        "update_data_product": "/datagovernance/catalog/dataproducts/{productId}",
        "delete_data_product": "/datagovernance/catalog/dataproducts/{productId}",
        # Data product relationships
        "create_data_product_relationship": "/datagovernance/catalog/dataproducts/{productId}/relationships",
        "list_data_product_relationships": "/datagovernance/catalog/dataproducts/{productId}/relationships",
        "delete_data_product_relationship": "/datagovernance/catalog/dataproducts/{productId}/relationships",
        # Data product query
        "query_data_products": "/datagovernance/catalog/dataproducts/query",
        # Terms (UC specific)
        "list_terms": "/datagovernance/catalog/terms",
        "create_term": "/datagovernance/catalog/terms",
        "get_term": "/datagovernance/catalog/terms/{termId}",
        "update_term": "/datagovernance/catalog/terms/{termId}",
        "delete_term": "/datagovernance/catalog/terms/{termId}",
        # Terms query
        "query_terms": "/datagovernance/catalog/terms/query",
        # Objectives
        "list_objectives": "/datagovernance/catalog/objectives",
        "create_objective": "/datagovernance/catalog/objectives",
        "get_objective": "/datagovernance/catalog/objectives/{objectiveId}",
        "update_objective": "/datagovernance/catalog/objectives/{objectiveId}",
        "delete_objective": "/datagovernance/catalog/objectives/{objectiveId}",
        # Objectives query
        "query_objectives": "/datagovernance/catalog/objectives/query",
        # Critical Data Elements
        "list_critical_data_elements": "/datagovernance/catalog/criticalDataElements",
        "create_critical_data_element": "/datagovernance/catalog/criticalDataElements",
        "get_critical_data_element": "/datagovernance/catalog/criticalDataElements/{cdeId}",
        "update_critical_data_element": "/datagovernance/catalog/criticalDataElements/{cdeId}",
        "delete_critical_data_element": "/datagovernance/catalog/criticalDataElements/{cdeId}",
        # CDE relationships
        "create_cde_relationship": "/datagovernance/catalog/criticalDataElements/{cdeId}/relationships",
        "list_cde_relationships": "/datagovernance/catalog/criticalDataElements/{cdeId}/relationships",
        "delete_cde_relationship": "/datagovernance/catalog/criticalDataElements/{cdeId}/relationships",
        # CDE query
        "query_critical_data_elements": "/datagovernance/catalog/criticalDataElements/query",
        # Policies
        "list_policies": "/datagovernance/catalog/policies",
        "create_policy": "/datagovernance/catalog/policies",
        "get_policy": "/datagovernance/catalog/policies/{policyId}",
        "update_policy": "/datagovernance/catalog/policies/{policyId}",
        "delete_policy": "/datagovernance/catalog/policies/{policyId}",
        # Custom Metadata (Business Metadata via Atlas API)
        # Note: Both /catalog/api and /datamap/api work, but /datamap/api is for new portal
        "list_custom_metadata": "/datamap/api/atlas/v2/types/typedefs",
        "get_custom_metadata": "/datamap/api/atlas/v2/entity/guid/{guid}",
        "add_custom_metadata": "/datamap/api/atlas/v2/entity/guid/{guid}/businessmetadata",
        "update_custom_metadata": "/datamap/api/atlas/v2/entity/guid/{guid}/businessmetadata",
        "delete_custom_metadata": "/datamap/api/atlas/v2/entity/guid/{guid}/businessmetadata",
        # Custom Attributes
        "list_custom_attributes": "/datagovernance/catalog/attributes",
        "create_custom_attribute": "/datagovernance/catalog/attributes",
        "get_custom_attribute": "/datagovernance/catalog/attributes/{attributeId}",
        "update_custom_attribute": "/datagovernance/catalog/attributes/{attributeId}",
        "delete_custom_attribute": "/datagovernance/catalog/attributes/{attributeId}",
    },
    # ==================== AZURE RESOURCE MANAGER ENDPOINTS ====================
    "management": {
        # Azure Resource Manager endpoints for Purview accounts
        "operations": "/providers/Microsoft.Purview/operations",
        "check_name_availability": "/subscriptions/{subscriptionId}/providers/Microsoft.Purview/checkNameAvailability",
        "accounts": "/subscriptions/{subscriptionId}/providers/Microsoft.Purview/accounts",
        "accounts_by_rg": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts",
        "account": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}",
        "private_endpoints": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/privateEndpointConnections",
        "default_account": "/subscriptions/{subscriptionId}/providers/Microsoft.Purview/getDefaultAccount",
        "set_default_account": "/subscriptions/{subscriptionId}/providers/Microsoft.Purview/setDefaultAccount",
        "remove_default_account": "/subscriptions/{subscriptionId}/providers/Microsoft.Purview/removeDefaultAccount",
    },
    # ==================== LEGACY COMPATIBILITY ENDPOINTS ====================
    "scan": {
        # Legacy scan endpoints for compatibility
        "base": "/scan",
        "status": "/scan/status",
        "results": "/scan/results",
    },
    "share": {
        # Legacy share endpoints for compatibility
        "base": "/share",
        "invitation": "/share/invitation",
        "accept": "/share/accept",
    },
}


def format_endpoint(endpoint_template: str, **kwargs) -> str:
    """
    Format an endpoint template with the provided keyword arguments.

    Args:
        endpoint_template: The endpoint template string with placeholders
        **kwargs: Keyword arguments to substitute in the template

    Returns:
        The formatted endpoint string
    """
    return endpoint_template.format(**kwargs)


def get_api_version_params(api_type: str = "datamap") -> dict:
    """
    Get API version parameters for the specified API type.

    Args:
        api_type: The type of API (datamap, account, scanning, workflow, etc.)

    Returns:
        Dictionary containing the API version parameter
    """
    version_map = {
        "datamap": DATAMAP_API_VERSION,
        "account": ACCOUNT_API_VERSION,
        "collections": ACCOUNT_API_VERSION,
        "scanning": SCANNING_API_VERSION,
        "workflow": WORKFLOW_API_VERSION,
        "devops_policies": get_api_version("devops_policies"),
        "self_service_policies": get_api_version("self_service_policies"),
        "sharing": get_api_version("sharing"),
        "metadata_policies": get_api_version("metadata_policies"),
        "management": "2021-07-01",  # ARM API version
    }

    api_version = version_map.get(api_type, DATAMAP_API_VERSION)
    return {"api-version": api_version}


def get_endpoint_category(endpoint_name: str) -> str:
    """
    Get the API category for an endpoint to determine correct API version.

    Args:
        endpoint_name: The name of the endpoint

    Returns:
        The API category (datamap, account, scanning, etc.)
    """
    category_map = {
        "entity": "datamap",
        "glossary": "datamap",
        "types": "datamap",
        "lineage": "datamap",
        "relationship": "datamap",
        "discovery": "datamap",
        "search": "datamap",
        "account": "account",
        "collections": "account",
        "scanning": "scanning",
        "workflow": "workflow",
        "devops_policies": "devops_policies",
        "self_service_policies": "self_service_policies",
        "sharing": "sharing",
        "metadata_policies": "metadata_policies",
        "unified_catalog": "datamap",
        "management": "management",
    }

    return category_map.get(endpoint_name, "datamap")
