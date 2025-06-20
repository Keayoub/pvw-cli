"""
Microsoft Purview API Endpoints Configuration
Centralized endpoint management for all Purview services
"""

import os

# Simplified and modularized endpoint definitions for Purview Data Map API

API_VERSION = {"datamap": {"stable": "2023-09-01", "preview": "2024-03-01-preview"}}

USE_PREVIEW = os.getenv("USE_PREVIEW", "true").lower() in ("1", "true", "yes")

DATAMAP_API_VERSION = (
    API_VERSION["datamap"]["preview"] if USE_PREVIEW else API_VERSION["datamap"]["stable"]
)

ENDPOINTS = {
    "entity": {
        # Core entity operations - based on /atlas/v2/entity paths
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
    },
    "glossary": {
        # Core glossary operations
        "base": "/datamap/api/atlas/v2/glossary",
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
    },
    "lineage": {
        # Lineage operations
        "get": "/datamap/api/atlas/v2/lineage/{guid}",
        "get_by_unique_attribute": "/datamap/api/atlas/v2/lineage/uniqueAttribute/type/{typeName}",
        "get_next_page": "/datamap/api/lineage/{guid}/next",
    },
    "relationship": {
        # Relationship operations
        "create": "/datamap/api/atlas/v2/relationship",
        "update": "/datamap/api/atlas/v2/relationship",
        "get": "/datamap/api/atlas/v2/relationship/guid/{guid}",
        "delete": "/datamap/api/atlas/v2/relationship/guid/{guid}",
    },
    "types": {
        # Type definitions operations
        "list": "/datamap/api/atlas/v2/types/typedefs",
        "list_headers": "/datamap/api/atlas/v2/types/typedefs/headers",
        "bulk_create": "/datamap/api/atlas/v2/types/typedefs",
        "bulk_update": "/datamap/api/atlas/v2/types/typedefs",
        "bulk_delete": "/datamap/api/atlas/v2/types/typedefs",
        # Type by GUID
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
    },
    "discovery": {
        # Search and discovery operations
        "query": "/datamap/api/search/query",
        "suggest": "/datamap/api/search/suggest",
        "autocomplete": "/datamap/api/search/autocomplete",
        "navigate": "/datamap/api/navigate",
    },
    # Legacy/compatibility endpoints for existing functionality
    "search": {
        "query": "/datamap/api/search/query",
        "suggest": "/datamap/api/search/suggest",
        "autocomplete": "/datamap/api/search/autocomplete",
    },
    "account": {
        # These are not part of the Data Map API but kept for compatibility
        "base": "/account",
        "settings": "/account/settings",
        "usage": "/account/usage",
        "account": "/account",
        "account_update": "/account",
        "access_keys": "/account/access-keys",
        "regenerate_access_key": "/account/regenerate-access-key",
    },
    "collections": {
        # Collection management endpoints - Account Data Plane API
        "list": "/account/collections",
        "get": "/account/collections/{collectionName}",
        "create_or_update": "/account/collections/{collectionName}",
        "delete": "/account/collections/{collectionName}",
        "get_collection_path": "/account/collections/{collectionName}/getCollectionPath",
        "get_child_collection_names": "/account/collections/{collectionName}/getChildCollectionNames",
    },
    "scan": {
        # These are not part of the Data Map API but kept for compatibility
        "base": "/scan",
        "status": "/scan/status",
        "results": "/scan/results",
    },
    "share": {
        # These are not part of the Data Map API but kept for compatibility
        "base": "/share",
        "invitation": "/share/invitation",
        "accept": "/share/accept",
    },
    "management": {
        # Azure Resource Manager endpoints for Purview accounts
        "operations": "/providers/Microsoft.Purview/operations",
        "check_name_availability": "/subscriptions/{subscriptionId}/providers/Microsoft.Purview/checkNameAvailability",
        "accounts": "/subscriptions/{subscriptionId}/providers/Microsoft.Purview/accounts",
        "accounts_by_rg": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts",        "account": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Purview/accounts/{accountName}",
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
        api_type: The type of API ('datamap', 'account', 'collections', etc.)

    Returns:
        Dictionary containing the API version parameter
    """
    if api_type == "datamap":
        return {"api-version": DATAMAP_API_VERSION}
    elif api_type == "account":
        return {"api-version": "2019-11-01-preview"}
    elif api_type == "collections":
        return {"api-version": "2019-11-01-preview"}
    elif api_type == "management":
        # These APIs typically use different versioning schemes
        return {"api-version": "2021-07-01"}
    elif api_type == "scan":
        return {"api-version": "2018-12-01-preview"}
    else:
        # Default to datamap API version
        return {"api-version": DATAMAP_API_VERSION}
