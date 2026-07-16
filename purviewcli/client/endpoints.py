# SPDX-License-Identifier: Apache-2.0

"""
Microsoft Purview API Endpoints Configuration - Complete 100% Coverage
Centralized endpoint management for ALL Purview services and operations
"""

import os

# Complete API version definitions for all Purview services
# Based on official Microsoft documentation: https://learn.microsoft.com/rest/api/purview/
# Note: Account endpoint uses older API version as newer versions are not yet supported
API_VERSION = {
    "datamap": {"stable": "2023-09-01", "preview": "2024-03-01-preview"},
    "account": {"preview": "2019-11-01-preview"},  # Only preview version available
    "scanning": {"stable": "2023-09-01", "preview": "2023-09-01"},  # Scanning uses 2023-09-01 for both stable and preview
    "quality": {"preview": "2026-01-12-preview"},
    "workflow": {"preview": "2023-10-01-preview"},
    "devops_policies": {"preview": "2022-11-01-preview"},
    "self_service_policies": {"preview": "2022-12-01-preview"},
    "sharing": {"preview": "2023-05-30-preview"},
    "metadata_policies": {"preview": "2021-07-01-preview"},
    "pds": {"preview": "2023-02-15-preview"},
    # Unified Catalog API — https://learn.microsoft.com/rest/api/purview/unified-catalog-api-overview
    # 2026-03-20-preview adds Data Assets and Data Columns groups, plus Count operations.
    "unified_catalog": {"preview": "2026-03-20-preview"},
    # Data Quality API — https://learn.microsoft.com/rest/api/purview/unified-catalog-data-quality
    # 2026-01-12-preview is current GA-feature preview (alerts, asset DQ, observations).
    "data_quality": {"preview": "2026-01-12-preview"},
}

USE_PREVIEW = os.getenv("USE_PREVIEW", "true").lower() in ("1", "true", "yes")

# Catalog custom metadata list supports expired attributes in preview.
CATALOG_CUSTOM_METADATA_PATH = "/datagovernance/catalog/customMetadata"
CATALOG_LIST_DEFAULT_API_VERSION = "2026-03-20-preview"
# Convenience alias used by UC client code
UC_API_VERSION = CATALOG_LIST_DEFAULT_API_VERSION


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
DATAQUALITY_API_VERSION = get_api_version("data_quality")

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
        "list_data_sources": "/scan/datasources",
        "create_data_source": "/scan/datasources/{dataSourceName}",
        "get_data_source": "/scan/datasources/{dataSourceName}",
        "update_data_source": "/scan/datasources/{dataSourceName}",
        "delete_data_source": "/scan/datasources/{dataSourceName}",
        # Scan configuration
        "list_scans": "/scan/datasources/{dataSourceName}/scans",
        "create_scan": "/scan/datasources/{dataSourceName}/scans/{scanName}",
        "get_scan": "/scan/datasources/{dataSourceName}/scans/{scanName}",
        "update_scan": "/scan/datasources/{dataSourceName}/scans/{scanName}",
        "delete_scan": "/scan/datasources/{dataSourceName}/scans/{scanName}",
        # Scan execution
        "run_scan": "/scan/datasources/{dataSourceName}/scans/{scanName}/run",
        "get_scan_result": "/scan/datasources/{dataSourceName}/scans/{scanName}/runs/{runId}",
        "list_scan_results": "/scan/datasources/{dataSourceName}/scans/{scanName}/runs",
        "cancel_scan": "/scan/datasources/{dataSourceName}/scans/{scanName}/runs/{runId}/cancel",
        # Integration runtime management
        "list_integration_runtimes": "/scan/integrationruntimes",
        "get_integration_runtime": "/scan/integrationruntimes/{integrationRuntimeName}",
        "delete_integration_runtime": "/scan/integrationruntimes/{integrationRuntimeName}",
        "get_integration_runtime_status": "/scan/integrationruntimes/{integrationRuntimeName}/status",
        # Scan rules and filters
        "list_scan_rule_sets": "/scan/scanrulesets",
        "create_scan_rule_set": "/scan/scanrulesets/{scanRulesetName}",
        "get_scan_rule_set": "/scan/scanrulesets/{scanRulesetName}",
        "update_scan_rule_set": "/scan/scanrulesets/{scanRulesetName}",
        "delete_scan_rule_set": "/scan/scanrulesets/{scanRulesetName}",
        # Classification rules
        "list_classification_rules": "/scan/classificationrules",
        "create_classification_rule": "/scan/classificationrules/{classificationRuleName}",
        "get_classification_rule": "/scan/classificationrules/{classificationRuleName}",
        "update_classification_rule": "/scan/classificationrules/{classificationRuleName}",
        "delete_classification_rule": "/scan/classificationrules/{classificationRuleName}",
        "list_classification_rule_versions": "/scan/classificationrules/{classificationRuleName}/versions",
        "tag_classification_version": "/scan/classificationrules/{classificationRuleName}/versions/{classificationRuleVersion}/tag",
        # Advanced scanning operations (new for 100% coverage)
        "get_scan_analytics": "/scan/datasources/{dataSourceName}/scans/{scanName}/analytics",
        "get_scan_history": "/scan/datasources/{dataSourceName}/scans/{scanName}/history",
        "schedule_scan": "/scan/datasources/{dataSourceName}/scans/{scanName}/triggers",
        "get_scan_schedule": "/scan/datasources/{dataSourceName}/scans/{scanName}/triggers/{triggerId}",
        "update_scan_schedule": "/scan/datasources/{dataSourceName}/scans/{scanName}/triggers/{triggerId}",
        "delete_scan_schedule": "/scan/datasources/{dataSourceName}/scans/{scanName}/triggers/{triggerId}",
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
        # Workflow execution / runs
        "execute_workflow": "/workflows/{workflowId}/run",
        "workflow_execution": "/workflowruns/{workflowRunId}",
        "workflow_executions": "/workflows/{workflowId}/runs",
        "cancel_workflow_execution": "/workflowruns/{workflowRunId}/cancel",
        "workflow_runs": "/workflows/{workflowId}/runs",
        "workflow_run": "/workflowruns/{workflowRunId}",
        "workflow_history": "/workflows/{workflowId}/history",
        # Workflow tasks
        "workflow_tasks": "/workflowtasks",
        "workflow_task": "/workflowtasks/{taskId}",
        "complete_task": "/workflowtasks/{taskId}/complete",
        # User requests
        "submit_user_requests": "/userrequests",
        "get_workflow_run": "/workflowruns/{workflowRunId}",
        "list_workflow_runs": "/workflows/{workflowId}/runs",
        "cancel_workflow_run": "/workflowruns/{workflowRunId}/cancel",
        "approve_workflow_task": "/workflowtasks/{taskId}/approve",
        "reject_workflow_task": "/workflowtasks/{taskId}/reject",
        "reassign_workflow_task": "/workflowtasks/{taskId}/reassign",
        # Approval workflows
        "create_approval_workflow": "/workflows/approval",
        "approval_requests": "/approvalrequests",
        "approval_request": "/approvalrequests/{requestId}",
        "approve_request": "/approvalrequests/{requestId}/approve",
        "reject_request": "/approvalrequests/{requestId}/reject",
        # Workflow templates
        "workflow_templates": "/workflows/templates",
        "workflow_template": "/workflows/templates/{templateId}",
        "create_from_template": "/workflows/templates/{templateId}/create",
        "list_workflow_templates": "/workflows/templates",
        # Workflow analytics and logs
        "get_workflow_analytics": "/workflows/{workflowId}/analytics",
        "workflow_metrics": "/workflows/{workflowId}/metrics",
        "workflow_logs": "/workflows/{workflowId}/logs",
        "export_logs": "/workflows/{workflowId}/logs/export",
        # Workflow triggers and schedules
        "workflow_triggers": "/workflows/{workflowId}/triggers",
        "create_trigger": "/workflows/{workflowId}/triggers",
        "workflow_trigger": "/workflows/{workflowId}/triggers/{triggerId}",
        "schedule_workflow": "/workflows/{workflowId}/schedules",
        "workflow_schedules": "/workflows/{workflowId}/schedules",
        "workflow_schedule": "/workflows/{workflowId}/schedules/{scheduleId}",
        # Workflow actions, conditions, variables, versions
        "workflow_actions": "/workflows/actions",
        "workflow_conditions": "/workflows/conditions",
        "validate_workflow": "/workflows/validate",
        "workflow_variables": "/workflows/{workflowId}/variables",
        "workflow_versions": "/workflows/{workflowId}/versions",
        # Workflow integrations
        "workflow_integrations": "/workflows/integrations",
        "configure_integration": "/workflows/integrations/{integrationId}",
        "test_integration": "/workflows/integrations/{integrationId}/test",
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
        # entityId must be in the URL path (not a query param) for the DELETE to hit the correct resource
        "delete_data_product_relationship": "/datagovernance/catalog/dataproducts/{productId}/relationships/{entityId}",
        # Data product query
        "query_data_products": "/datagovernance/catalog/dataproducts/query",
        # Terms (UC specific)
        "list_terms": "/datagovernance/catalog/terms",
        "create_term": "/datagovernance/catalog/terms",
        "get_term": "/datagovernance/catalog/terms/{termId}",
        "update_term": "/datagovernance/catalog/terms/{termId}",
        "delete_term": "/datagovernance/catalog/terms/{termId}",
        # Term relationships (synonyms, related terms)
        "add_term_relationship": "/datagovernance/catalog/terms/{termId}/relationships",
        "delete_term_relationship": "/datagovernance/catalog/terms/{termId}/relationships/{entityId}",
        "list_related_entities": "/datagovernance/catalog/terms/{termId}/relationships",
        # Terms query
        "query_terms": "/datagovernance/catalog/terms/query",
        # Terms hierarchy
        "list_hierarchy_terms": "/datagovernance/catalog/terms/hierarchy",
        # Terms facets
        "get_term_facets": "/datagovernance/catalog/terms/facets",
        # CDE facets
        "get_cde_facets": "/datagovernance/catalog/criticalDataElements/facets",
        # Data Products facets
        "get_data_product_facets": "/datagovernance/catalog/dataProducts/facets",
        # Objectives facets
        "get_objective_facets": "/datagovernance/catalog/objectives/facets",
        # Objectives
        "list_objectives": "/datagovernance/catalog/objectives",
        "create_objective": "/datagovernance/catalog/objectives",
        "get_objective": "/datagovernance/catalog/objectives/{objectiveId}",
        "update_objective": "/datagovernance/catalog/objectives/{objectiveId}",
        "delete_objective": "/datagovernance/catalog/objectives/{objectiveId}",
        # Objectives query
        "query_objectives": "/datagovernance/catalog/objectives/query",
        # Key Results (OKRs - under objectives)
        "list_key_results": "/datagovernance/catalog/objectives/{objectiveId}/keyResults",
        "get_key_result": "/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}",
        "create_key_result": "/datagovernance/catalog/objectives/{objectiveId}/keyResults",
        "update_key_result": "/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}",
        "delete_key_result": "/datagovernance/catalog/objectives/{objectiveId}/keyResults/{keyResultId}",
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
            # CDE convenience aliases (used by _unified_catalog.py)
            "get_cde": "/datagovernance/catalog/criticalDataElements/{cdeId}",
            "list_cdes": "/datagovernance/catalog/criticalDataElements",
        # Policies
        "list_policies": "/datagovernance/catalog/policies",
        "create_policy": "/datagovernance/catalog/policies",
        "get_policy": "/datagovernance/catalog/policies/{policyId}",
        "update_policy": "/datagovernance/catalog/policies/{policyId}",
        "delete_policy": "/datagovernance/catalog/policies/{policyId}",
        # Custom Metadata
        "list_custom_metadata": "/datamap/api/atlas/v2/types/typedefs",
        "list_custom_metadata_catalog": CATALOG_CUSTOM_METADATA_PATH,
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
        # ── NEW in 2026-03-20-preview ─────────────────────────────────────────
        # Count operations (duplicate-name validation)
        # https://learn.microsoft.com/rest/api/purview/purview-unified-catalog
        "count_terms": "/datagovernance/catalog/terms/count",
        "count_critical_data_elements": "/datagovernance/catalog/criticalDataElements/count",
        "count_data_products": "/datagovernance/catalog/dataProducts/count",
        "count_objectives": "/datagovernance/catalog/objectives/count",
        # Data Assets  (full group, new in 2026-03-20-preview)
        "list_data_assets": "/datagovernance/catalog/dataAssets",
        "create_data_asset": "/datagovernance/catalog/dataAssets",
        "get_data_asset": "/datagovernance/catalog/dataAssets/{dataAssetId}",
        "update_data_asset": "/datagovernance/catalog/dataAssets/{dataAssetId}",
        "delete_data_asset": "/datagovernance/catalog/dataAssets/{dataAssetId}",
        "query_data_assets": "/datagovernance/catalog/dataAssets/query",
        "create_data_asset_relationship": "/datagovernance/catalog/dataAssets/{dataAssetId}/relationships",
        "list_data_asset_relationships": "/datagovernance/catalog/dataAssets/{dataAssetId}/relationships",
        "delete_data_asset_relationship": "/datagovernance/catalog/dataAssets/{dataAssetId}/relationships",
        # Data Columns  (full group, new in 2026-03-20-preview)
        "get_data_column": "/datagovernance/catalog/dataColumns/{id}",
        "ingest_data_column": "/datagovernance/catalog/dataColumns",
        "query_data_columns": "/datagovernance/catalog/dataColumns/query",
        "add_data_column_related_entity": "/datagovernance/catalog/dataColumns/{id}/relationships",
        "list_data_column_related_entities": "/datagovernance/catalog/dataColumns/{id}/relationships",
        "delete_data_column_related": "/datagovernance/catalog/dataColumns/{id}/relationships",
    },
    # ==================== DATA QUALITY API ENDPOINTS ====================
    # https://learn.microsoft.com/rest/api/purview/unified-catalog-data-quality
    # API version: 2026-01-12-preview
    # NOTE: Data Quality endpoints are scoped under business domains.
    # Data sources use domain-scoped paths:
    #   PUT /datagovernance/quality/business-domains/{domainId}/data-sources/{dataSourceId}
    # (The flat /connections aliases below are kept for backward compat but point to wrong paths.)
    "data_quality": {
        # Domain quality reporting
        "list_business_domains": "/datagovernance/quality/business-domains",
        "get_domain_report": "/datagovernance/quality/business-domains/{domainId}/report",
        "list_domain_data_sources": "/datagovernance/quality/business-domains/{domainId}/data-sources",
        "list_domain_schedules": "/datagovernance/quality/business-domains/{domainId}/schedules",
        "list_domain_alerts": "/datagovernance/quality/business-domains/{domainId}/alerts",
        "list_domain_assets": "/datagovernance/quality/business-domains/{domainId}/assets",
        # Data source connections (domain-scoped — correct paths per 2026-01-12-preview spec)
        "create_data_source": "/datagovernance/quality/business-domains/{domainId}/data-sources/{dataSourceId}",
        "get_data_source": "/datagovernance/quality/business-domains/{domainId}/data-sources/{dataSourceId}",
        "update_data_source": "/datagovernance/quality/business-domains/{domainId}/data-sources/{dataSourceId}",
        "delete_data_source": "/datagovernance/quality/business-domains/{domainId}/data-sources/{dataSourceId}",
        # Quality rules (domain-scoped)
        "list_rules": "/datagovernance/quality/business-domains/{domainId}/rules",
        "list_rules_by_domain": "/datagovernance/quality/business-domains/{domainId}/rules",
        "create_rule": "/datagovernance/quality/business-domains/{domainId}/rules",
        "get_rule": "/datagovernance/quality/business-domains/{domainId}/rules/{ruleId}",
        "update_rule": "/datagovernance/quality/business-domains/{domainId}/rules/{ruleId}",
        "delete_rule": "/datagovernance/quality/business-domains/{domainId}/rules/{ruleId}",
        "apply_rule": "/datagovernance/quality/business-domains/{domainId}/rules/{ruleId}/apply",
        # Schedules
        "list_scans": "/datagovernance/quality/business-domains/{domainId}/schedules",
        "create_scan": "/datagovernance/quality/business-domains/{domainId}/schedules",
        "get_scan": "/datagovernance/quality/business-domains/{domainId}/schedules/{scheduleId}",
        "update_scan": "/datagovernance/quality/business-domains/{domainId}/schedules/{scheduleId}",
        "delete_scan": "/datagovernance/quality/business-domains/{domainId}/schedules/{scheduleId}",
        "run_scan": "/datagovernance/quality/business-domains/{domainId}/schedules/{scheduleId}/run",
        "stop_scan": "/datagovernance/quality/business-domains/{domainId}/schedules/{scheduleId}/stop",
        "get_scan_results": "/datagovernance/quality/business-domains/{domainId}/schedules/{scheduleId}/results",
        # Scan runs
        "get_run_status": "/datagovernance/quality/runs/{runId}",
        "get_runs_for_schedule": "/datagovernance/quality/business-domains/{domainId}/schedules/{scheduleId}/runs",
        "cancel_scan_run": "/datagovernance/quality/runs/{runId}/cancel",
        # Alerts (new in 2026-01-12-preview)
        "get_alerts": "/datagovernance/quality/business-domains/{domainId}/alerts",
        "get_alert": "/datagovernance/quality/business-domains/{domainId}/alerts/{alertId}",
        "update_alert": "/datagovernance/quality/business-domains/{domainId}/alerts/{alertId}",
        "update_alert_status": "/datagovernance/quality/business-domains/{domainId}/alerts/{alertId}/status",
        "delete_alert": "/datagovernance/quality/business-domains/{domainId}/alerts/{alertId}",
        # Data profiling
        "run_profile": "/datagovernance/quality/business-domains/{domainId}/data-sources/{dataSourceId}/profile",
        "get_profile_results": "/datagovernance/quality/business-domains/{domainId}/data-sources/{dataSourceId}/profile/results",
        # Observations
        "list_observations": "/datagovernance/quality/business-domains/{domainId}/observations",
        "create_observation": "/datagovernance/quality/business-domains/{domainId}/observations",
        "delete_observation": "/datagovernance/quality/business-domains/{domainId}/observations/{observationId}",
        # Opinion trend (new in 2026-01-12-preview)
        "get_opinion_trend": "/datagovernance/quality/business-domains/{domainId}/opinionTrend",
        # Quality scores
        "get_quality_score": "/datagovernance/quality/assets/{assetId}/score",
        "list_asset_scores": "/datagovernance/quality/scores",
        "get_latest_snapshot": "/datagovernance/quality/business-domains/{domainId}/snapshots/latest",
        # Standalone Asset DQ (new in 2026-01-12-preview — no data product required)
        "create_asset_dq": "/datagovernance/quality/assetDQ",
        "get_asset_dq": "/datagovernance/quality/assetDQ/{assetDQId}",
        "clone_asset_dq": "/datagovernance/quality/assetDQ/{assetDQId}/clone",
        "delete_asset_dq": "/datagovernance/quality/assetDQ/{assetDQId}",
        "list_asset_dq": "/datagovernance/quality/assetDQ",
        "get_asset_dq_scores": "/datagovernance/quality/assetDQ/{assetDQId}/scores",
        "get_asset_dq_rules": "/datagovernance/quality/assetDQ/{assetDQId}/rules",
        "create_asset_dq_rule": "/datagovernance/quality/assetDQ/{assetDQId}/rules",
        "update_asset_dq_rule": "/datagovernance/quality/assetDQ/{assetDQId}/rules/{ruleId}",
        "delete_asset_dq_rule": "/datagovernance/quality/assetDQ/{assetDQId}/rules/{ruleId}",
        "get_asset_dq_latest_snapshot": "/datagovernance/quality/assetDQ/{assetDQId}/snapshots/latest",
        "list_asset_dq_runs": "/datagovernance/quality/assetDQ/{assetDQId}/runs",
        # Bulk / scoped asset metadata
        "get_bulk_asset_metadata": "/datagovernance/quality/bulkAssetMetadata",
        "create_bulk_asset_metadata": "/datagovernance/quality/bulkAssetMetadata",
        "get_scoped_asset_metadata": "/datagovernance/quality/scopedAssetMetadata/{assetId}",
        "update_scoped_asset_metadata": "/datagovernance/quality/scopedAssetMetadata/{assetId}",
        "delete_scoped_asset_metadata": "/datagovernance/quality/scopedAssetMetadata/{assetId}",
        # Observer
        "get_observer": "/datagovernance/quality/observers/{observerId}",
        "update_observer": "/datagovernance/quality/observers/{observerId}",
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
        # Account keys
        "access_keys": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/listkeys",
        "regenerate_access_key": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/regeneratekeys",
        # Private link resources
        "private_link_resources": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/privateLinkResources",
        "private_link_resource": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/privateLinkResources/{groupId}",
        # Private endpoint connections
        "private_endpoint_connections": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/privateEndpointConnections",
        "private_endpoint_connection": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/privateEndpointConnections/{privateEndpointConnectionName}",
        # Account features and settings
        "account_features": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/listFeatures",
        "ingestion_status": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/ingestionStatus",
        "resource_sets": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/resourceSetRuleConfigs/defaultResourceSetRuleConfig",
        "security_settings": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/networkPolicy",
        # Diagnostic settings (Azure Monitor)
        "diagnostic_settings": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/providers/microsoft.insights/diagnosticSettings",
        "diagnostic_setting": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/providers/microsoft.insights/diagnosticSettings/{name}",
        # Account usage, metrics, tags, status
        "account_usage": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/usages",
        "account_metrics": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/metrics",
        "account_tags": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/tags",
        "account_status": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/status",
        "account_health": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/health",
        "subscription_usage": "/subscriptions/{subscriptionId}/providers/Microsoft.Purview/usages",
        "validate_configuration": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}/validateConfiguration",
    },
    # ==================== LEGACY COMPATIBILITY ENDPOINTS ====================
    "scan": {
        # Legacy scan endpoints for compatibility
        "base": "/scan",
        "status": "/scan/status",
        "results": "/scan/results",
    },
    # ==================== SHARE (LEGACY) / ACCEPTED SHARES API ====================
    "share": {
        # Accepted sent shares (legacy in-product sharing via /sentShares/{name}/acceptedSentShares)
        "accepted_sent_shares": "/sentShares/{sentShareName}/acceptedSentShares",
        "accepted_sent_share": "/sentShares/{sentShareName}/acceptedSentShares/{acceptedSentShareName}",
        "reinstate_accepted_share": "/sentShares/{sentShareName}/acceptedSentShares/{acceptedSentShareName}:reinstate",
        "revoke_accepted_share": "/sentShares/{sentShareName}/acceptedSentShares/{acceptedSentShareName}:revoke",
        "update_expiration_accepted_share": "/sentShares/{sentShareName}/acceptedSentShares/{acceptedSentShareName}:updateExpiration",
        # Asset mappings
        "asset_mappings": "/receivedShares/{receivedShareName}/assetMappings",
        "asset_mapping": "/receivedShares/{receivedShareName}/assetMappings/{assetMappingName}",
        # Assets
        "assets": "/sentShares/{sentShareName}/assets",
        "asset": "/sentShares/{sentShareName}/assets/{assetName}",
        # Email activation
        "activate_email": "/receivedShares:activateEmail",
        # Received share operations
        "accepted_sent_shares_list": "/sentShares/{sentShareName}/acceptedSentShares",
    },
    # ==================== POLICYSTORE API ENDPOINTS ====================
    "policystore": {
        # Metadata policies (Account Data Plane)
        "metadata_roles": "/metadataRoles",
        "metadata_policies": "/metadataPolicies",
        "metadata_policy_by_id": "/metadataPolicies/{policyId}",
        "collection_metadata_policy": "/metadataPolicies",
        # Data policies
        "data_policies": "/policy/data-access-policies",
        "data_policy_by_name": "/policy/data-access-policies/{policyName}",
        "data_access_policy": "/policy/data-access-policies/{policyId}",
        "data_access_policies": "/policy/data-access-policies",
        # DevOps policies
        "devops_policies": "/policies",
        "devops_policy": "/policies/{policyId}",
        # Self-service policies
        "self_service_policies": "/policy/data-access-policies",
        "self_service_policy": "/policy/data-access-policies/{policyId}",
        # Advanced policy operations
        "policy_collections": "/policy/collections",
        "policy_assignments": "/policy/assignments",
        "policy_assignment": "/policy/assignments/{assignmentId}",
        "policy_effects": "/policy/effects",
        "evaluate_policies": "/policy/evaluate",
        "user_permissions": "/policy/users/{userId}/permissions",
        "check_access": "/policy/check-access",
        "policy_templates": "/policy/templates",
        "policy_definitions": "/policy/definitions",
        "policy_definition": "/policy/definitions/{definitionId}",
        "role_assignments": "/policy/role-assignments",
        "role_assignment": "/policy/role-assignments/{assignmentId}",
        "role_definitions": "/policy/role-definitions",
        "policy_audit_logs": "/policy/audit-logs",
        "compliance_report": "/policy/compliance-report",
        "bulk_policy_operations": "/policy/bulk-operations",
        "validate_policy": "/policy/validate",
        "simulate_policy": "/policy/simulate",
        "policy_changes": "/policy/changes/{changeId}",
        "export_policies": "/policy/export",
        "import_policies": "/policy/import",
    },
    # ==================== INSIGHT / ANALYTICS API ENDPOINTS ====================
    "insight": {
        # Asset distribution analytics (Map & Discover)
        "asset_distribution_by_data_source": "/mapanddiscover/reports/asset2/assetDistribution/dataSourceType/summary",
        "asset_distribution_by_type": "/mapanddiscover/reports/asset2/assetDistribution/assetTypeSummary",
        "asset_distribution_by_classification": "/mapanddiscover/reports/asset2/assetDistribution/classificationSummary",
        "asset_distribution_by_collection": "/mapanddiscover/reports/asset2/assetDistribution/collectionSummary",
        # File analytics
        "files_without_resource_set": "/mapanddiscover/reports/asset2/files/filesByResourceSet",
        "files_aggregation": "/mapanddiscover/reports/asset2/files/filesAggregation",
        "resource_set_summary": "/mapanddiscover/reports/asset2/files/resourceSetSummary",
        "resource_set_details": "/mapanddiscover/reports/asset2/files/resourceSetDetails",
        # Scan analytics
        "scan_status_summary": "/mapanddiscover/reports/asset2/scans/scanStatusSummary",
        "scan_status_summary_by_ts": "/mapanddiscover/reports/asset2/scans/scanStatusSummaryByTs",
        "scan_history": "/mapanddiscover/reports/asset2/scans/scanHistory",
        "active_scans": "/mapanddiscover/reports/asset2/scans/activeScans",
        "scan_performance": "/mapanddiscover/reports/asset2/scans/scanPerformance",
        # Sensitivity label analytics
        "sensitivity_labels": "/mapanddiscover/reports/asset2/sensitivityLabel/labelSummary",
        "label_insight": "/mapanddiscover/reports/asset2/sensitivityLabel/labelInsights",
        # Glossary / term analytics
        "glossary_usage": "/mapanddiscover/reports/asset2/glossary/glossaryUsage",
        "business_glossary_health": "/mapanddiscover/reports/asset2/glossary/glossaryHealth",
        "term_assignment_coverage": "/mapanddiscover/reports/asset2/glossary/termAssignment",
        # Data profile analytics
        "data_profile_summary": "/mapanddiscover/reports/asset2/dataProfile/dataProfileSummary",
        # User / activity analytics
        "user_activity": "/mapanddiscover/reports/asset2/userActivity/userActivitySummary",
        "collection_activity": "/mapanddiscover/reports/asset2/userActivity/collectionActivity",
        # Version history
        "version_history": "/mapanddiscover/reports/asset2/assetHealth/versionHistory",
        # Scheduled reports
        "scheduled_reports": "/mapanddiscover/reports/scheduled",
        "create_scheduled_report": "/mapanddiscover/reports/scheduled",
        # Asset popularity
        "asset_popularity": "/mapanddiscover/reports/asset2/assetHealth/assetPopularity",
        # Tags time series
        "tags_time_series": "/mapanddiscover/reports/asset2/tags/tagsTimeSeries",
        # Data quality insights
        "data_quality_overview": "/mapanddiscover/reports/asset2/dataQuality/dataQualityOverview",
        "data_quality_trends": "/mapanddiscover/reports/asset2/dataQuality/dataQualityTrends",
        "data_quality_by_source": "/mapanddiscover/reports/asset2/dataQuality/dataQualityBySource",
        # Classification distribution
        "classification_distribution": "/mapanddiscover/reports/asset2/classification/classificationDistribution",
        # Lineage analytics
        "lineage_coverage": "/mapanddiscover/reports/asset2/lineage/lineageCoverage",
        "lineage_complexity": "/mapanddiscover/reports/asset2/lineage/lineageComplexity",
        # Compliance and security
        "compliance_metrics": "/mapanddiscover/reports/asset2/compliance/complianceMetrics",
        "data_stewardship_health": "/mapanddiscover/reports/asset2/compliance/dataStewardshipHealth",
        "asset_health_score": "/mapanddiscover/reports/asset2/assetHealth/assetHealthScore",
        # System performance
        "system_performance": "/mapanddiscover/reports/asset2/system/systemPerformance",
        "real_time_metrics": "/mapanddiscover/reports/asset2/system/realTimeMetrics",
        # Optimization
        "optimization_recommendations": "/mapanddiscover/reports/asset2/optimization/recommendations",
        # Resource utilization
        "resource_utilization": "/mapanddiscover/reports/asset2/system/resourceUtilization",
        # Historical trends
        "historical_trends": "/mapanddiscover/reports/asset2/assetHealth/historicalTrends",
        "data_growth_trends": "/mapanddiscover/reports/asset2/assetHealth/dataGrowthTrends",
        # Search patterns
        "search_patterns": "/mapanddiscover/reports/asset2/userActivity/searchPatterns",
        # Data archival / movement
        "data_archival": "/mapanddiscover/reports/asset2/dataManagement/dataArchival",
        "data_movement_patterns": "/mapanddiscover/reports/asset2/dataManagement/dataMovement",
        # Access patterns
        "access_patterns": "/mapanddiscover/reports/asset2/userActivity/accessPatterns",
        "permission_usage": "/mapanddiscover/reports/asset2/userActivity/permissionUsage",
        # Live activity feed
        "live_activity_feed": "/mapanddiscover/reports/asset2/userActivity/liveActivityFeed",
        # Export
        "export_data": "/mapanddiscover/reports/asset2/export",
        # Custom report
        "custom_report": "/mapanddiscover/reports/custom",
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
        "quality": get_api_version("quality"),
        "workflow": WORKFLOW_API_VERSION,
        "devops_policies": get_api_version("devops_policies"),
        "self_service_policies": get_api_version("self_service_policies"),
        "sharing": get_api_version("sharing"),
        "metadata_policies": get_api_version("metadata_policies"),
        "unified_catalog": get_api_version("unified_catalog"),
        "data_quality": get_api_version("data_quality"),
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
        "unified_catalog": "unified_catalog",
        "data_quality": "data_quality",
        "management": "management",
    }

    return category_map.get(endpoint_name, "datamap")
