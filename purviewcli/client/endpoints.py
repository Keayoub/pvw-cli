"""
Microsoft Purview API Endpoints Configuration
Centralized endpoint management for all Purview services
"""

class PurviewEndpoints:
    """
    Centralized configuration for Microsoft Purview API endpoints
    Based on the latest Microsoft Purview REST API documentation
    """
    
    # Base API paths for different services
    DATAMAP_BASE = "/datamap/api"
    CATALOG_BASE = "/catalog/api"
    SCAN_BASE = "/scan"
    SEARCH_BASE = "/search/api"
    POLICYSTORE_BASE = "/policystore"
    SHARE_BASE = "/share"
    MANAGEMENT_BASE = ""  # Management uses Azure Resource Manager APIs
    
    # API Versions
    ATLAS_V2 = "atlas/v2"
    SEARCH_V1 = "v1"
    PREVIEW_VERSION = "2021-05-01-preview"
    MANAGEMENT_VERSION = "2021-07-01"
    
    # === ENTITY ENDPOINTS (Data Map) ===
    ENTITY = {
        'base': f"{DATAMAP_BASE}/{ATLAS_V2}/entity",
        'bulk': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/bulk",
        'bulk_classification': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/bulk/classification",
        'bulk_set_classifications': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/bulk/setClassifications",
        'guid': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/guid",
        'unique_attribute': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/uniqueAttribute/type",
        'classification': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/guid/{{guid}}/classification",
        'classifications': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/guid/{{guid}}/classifications",
        'header': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/guid/{{guid}}/header",
        'audit': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/{{guid}}/audit",
        'labels': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/guid/{{guid}}/labels",        'business_metadata': f"{DATAMAP_BASE}/{ATLAS_V2}/entity/guid/{{guid}}/businessmetadata"
    }
    
    # === GLOSSARY ENDPOINTS (Catalog) ===
    GLOSSARY = {
        'base': f"{CATALOG_BASE}/{ATLAS_V2}/glossary",
        'categories': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/categories",
        'category': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/category",
        'terms': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/terms",
        'term': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/term",
        'detailed': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/{{glossaryGuid}}/detailed",
        'partial': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/{{glossaryGuid}}/partial",
        'category_partial': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/category/{{categoryGuid}}/partial",
        'term_partial': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/term/{{termGuid}}/partial",
        'category_related': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/category/{{categoryGuid}}/related",
        'category_terms': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/category/{{categoryGuid}}/terms",
        'term_assigned_entities': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/terms/{{termGuid}}/assignedEntities",
        'term_related': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/terms/{{termGuid}}/related",
        'categories_headers': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/{{glossaryGuid}}/categories/headers",
        'terms_headers': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/{{glossaryGuid}}/terms/headers",
        'terms_export': f"{CATALOG_BASE}/{ATLAS_V2}/glossary/{{glossaryGuid}}/terms/export",        # Special endpoints for import operations
        'terms_import': f"{CATALOG_BASE}/glossary/{{glossaryGuid}}/terms/import",
        'terms_import_by_name': f"{CATALOG_BASE}/glossary/name/{{glossaryName}}/terms/import",
        'terms_import_operation': f"{CATALOG_BASE}/glossary/terms/import/{{operationGuid}}"
    }
    
    # === TYPES ENDPOINTS (Data Map) ===
    TYPES = {
        'base': f"{DATAMAP_BASE}/{ATLAS_V2}/types",
        'businessmetadatadef': f"{DATAMAP_BASE}/{ATLAS_V2}/types/businessmetadatadef",
        'classificationdef': f"{DATAMAP_BASE}/{ATLAS_V2}/types/classificationdef",
        'entitydef': f"{DATAMAP_BASE}/{ATLAS_V2}/types/entitydef",
        'enumdef': f"{DATAMAP_BASE}/{ATLAS_V2}/types/enumdef",
        'relationshipdef': f"{DATAMAP_BASE}/{ATLAS_V2}/types/relationshipdef",
        'structdef': f"{DATAMAP_BASE}/{ATLAS_V2}/types/structdef",
        'typedef': f"{DATAMAP_BASE}/{ATLAS_V2}/types/typedef"
    }
    
    # === RELATIONSHIP ENDPOINTS (Data Map) ===
    RELATIONSHIP = {
        'base': f"{DATAMAP_BASE}/{ATLAS_V2}/relationship",
        'guid': f"{DATAMAP_BASE}/{ATLAS_V2}/relationship/guid/{{guid}}"
    }
    
    # === LINEAGE ENDPOINTS (Data Map) ===
    LINEAGE = {
        'guid': f"{DATAMAP_BASE}/{ATLAS_V2}/lineage/{{guid}}",
        'unique_attribute': f"{DATAMAP_BASE}/{ATLAS_V2}/lineage/uniqueAttribute/type/{{typeName}}"
    }
    
    # === SEARCH ENDPOINTS ===
    SEARCH = {
        'query': f"{SEARCH_BASE}/query",
        'suggest': f"{SEARCH_BASE}/suggest", 
        'autocomplete': f"{SEARCH_BASE}/autocomplete",
        'browse': f"{SEARCH_BASE}/browse"
    }
    
    # === SCAN ENDPOINTS ===
    SCAN = {
        'datasources': f"{SCAN_BASE}/datasources",
        'datasource': f"{SCAN_BASE}/datasources/{{dataSourceName}}",
        'scans': f"{SCAN_BASE}/datasources/{{dataSourceName}}/scans",
        'scan': f"{SCAN_BASE}/datasources/{{dataSourceName}}/scans/{{scanName}}",
        'scan_runs': f"{SCAN_BASE}/datasources/{{dataSourceName}}/scans/{{scanName}}/runs",
        'scan_run': f"{SCAN_BASE}/datasources/{{dataSourceName}}/scans/{{scanName}}/runs/{{runId}}",
        'filters': f"{SCAN_BASE}/datasources/{{dataSourceName}}/scans/{{scanName}}/filters/custom",
        'triggers': f"{SCAN_BASE}/datasources/{{dataSourceName}}/scans/{{scanName}}/triggers/default",
        'classification_rules': f"{SCAN_BASE}/classificationrules",
        'classification_rule': f"{SCAN_BASE}/classificationrules/{{classificationRuleName}}",
        'classification_rule_versions': f"{SCAN_BASE}/classificationrules/{{classificationRuleName}}/versions",
        'key_vaults': f"{SCAN_BASE}/azureKeyVaults",
        'key_vault': f"{SCAN_BASE}/azureKeyVaults/{{keyVaultName}}",
        'system_scan_rulesets': f"{SCAN_BASE}/systemScanRulesets",
        'system_scan_ruleset': f"{SCAN_BASE}/systemScanRulesets/{{dataSourceType}}",
        'system_scan_ruleset_versions': f"{SCAN_BASE}/systemScanRulesets/{{dataSourceType}}/versions",
        'system_scan_ruleset_version': f"{SCAN_BASE}/systemScanRulesets/{{dataSourceType}}/versions/{{version}}",
        'collections_list_datasources': f"{SCAN_BASE}/collections/{{collectionName}}/listDataSources",
        'integration_runtimes': f"{SCAN_BASE}/integrationruntimes",
        'integration_runtime': f"{SCAN_BASE}/integrationruntimes/{{integrationRuntimeName}}",
        'integration_runtime_auth': f"{SCAN_BASE}/integrationruntimes/{{integrationRuntimeName}}/listAuthKeys"
    }
    
    # === ACCOUNT ENDPOINTS (Catalog) ===
    ACCOUNT = {
        'account': f"{CATALOG_BASE}/account",
        'collections': f"{CATALOG_BASE}/collections",
        'collection': f"{CATALOG_BASE}/collections/{{collectionName}}",
        'collection_path': f"{CATALOG_BASE}/collections/{{collectionName}}/getCollectionPath", 
        'child_collection_names': f"{CATALOG_BASE}/collections/{{collectionName}}/getChildCollectionNames",
        'access_keys': f"{CATALOG_BASE}/account/keys",
        'resource_set_rules': f"{CATALOG_BASE}/account/resourceSetRuleConfigs",
        'resource_set_rule': f"{CATALOG_BASE}/account/resourceSetRuleConfigs/defaultResourceSetRuleConfig"
    }
    
    # === INSIGHT ENDPOINTS (Catalog) ===
    INSIGHT = {
        'asset_distribution_by_data_source': f"{CATALOG_BASE}/atlas/v2/datamap/assetDistributionByDataSource",
        'asset_distribution_by_top_level_collection': f"{CATALOG_BASE}/atlas/v2/datamap/assetDistributionByTopLevelCollection", 
        'data_source_count_trend': f"{CATALOG_BASE}/atlas/v2/datamap/dataSourceCountTrend",
        'file_extension_count_trend': f"{CATALOG_BASE}/atlas/v2/datamap/fileExtensionCountTrend",
        'file_type_size_trend': f"{CATALOG_BASE}/atlas/v2/datamap/fileTypeSizeTrend",
        'top_file_extensions_by_size': f"{CATALOG_BASE}/atlas/v2/datamap/topFileExtensionsBySize",
        'classification_insight': f"{CATALOG_BASE}/atlas/v2/datamap/classificationInsight",
        'label_insight': f"{CATALOG_BASE}/atlas/v2/datamap/labelInsight",
        'tags_time_series': f"{CATALOG_BASE}/atlas/v2/datamap/tagsTimeSeries"
    }
      # === POLICYSTORE ENDPOINTS ===
    POLICYSTORE = {
        'metadata_policies': f"{POLICYSTORE_BASE}/metadataPolicies",
        'metadata_policy_by_id': f"{POLICYSTORE_BASE}/metadataPolicies/{{policyId}}",
        'collection_metadata_policy': f"{POLICYSTORE_BASE}/collections/{{collectionName}}/metadataPolicy",
        'metadata_roles': f"{POLICYSTORE_BASE}/metadataRoles",
        'data_policies': f"{POLICYSTORE_BASE}/dataPolicies",
        'data_policy_by_name': f"{POLICYSTORE_BASE}/dataPolicies/{{policyName}}",
        'data_policy_scopes': f"{POLICYSTORE_BASE}/dataPolicies/{{policyName}}/scopes",
        'data_policy_scope_by_datasource': f"{POLICYSTORE_BASE}/dataPolicies/{{policyName}}/scopes/{{datasource}}"
    }    # === SHARE ENDPOINTS ===
    SHARE = {
        'received_shares': f"{SHARE_BASE}/receivedShares",
        'received_share': f"{SHARE_BASE}/receivedShares/{{receivedShareName}}",
        'sent_shares': f"{SHARE_BASE}/sentShares", 
        'sent_share': f"{SHARE_BASE}/sentShares/{{sentShareName}}",
        'accepted_sent_shares': f"{SHARE_BASE}/sentShares/{{sentShareName}}/acceptedSentShares",
        'accepted_sent_share': f"{SHARE_BASE}/sentShares/{{sentShareName}}/acceptedSentShares/{{acceptedSentShareName}}",
        'reinstate_accepted_share': f"{SHARE_BASE}/sentShares/{{sentShareName}}/acceptedSentShares/{{acceptedSentShareName}}:reinstate",
        'revoke_accepted_share': f"{SHARE_BASE}/sentShares/{{sentShareName}}/acceptedSentShares/{{acceptedSentShareName}}:revoke",
        'update_expiration_accepted_share': f"{SHARE_BASE}/sentShares/{{sentShareName}}/acceptedSentShares/{{acceptedSentShareName}}:update-expiration",
        'asset_mappings': f"{SHARE_BASE}/receivedShares/{{receivedShareName}}/assetMappings",
        'asset_mapping': f"{SHARE_BASE}/receivedShares/{{receivedShareName}}/assetMappings/{{assetMappingName}}",
        'assets': f"{SHARE_BASE}/sentShares/{{sentShareName}}/assets",
        'asset': f"{SHARE_BASE}/sentShares/{{sentShareName}}/assets/{{assetName}}",
        'invitations': f"{SHARE_BASE}/sentShares/{{sentShareName}}/invitations",
        'invitation': f"{SHARE_BASE}/sentShares/{{sentShareName}}/invitations/{{invitationName}}",
        'activate_email': f"{SHARE_BASE}/activateEmail"
    }
    
    # === MANAGEMENT ENDPOINTS (Azure Resource Manager) ===
    MANAGEMENT = {
        'operations': "/providers/Microsoft.Purview/operations",
        'check_name_availability': "/subscriptions/{{subscriptionId}}/providers/Microsoft.Purview/checkNameAvailability",
        'accounts': "/subscriptions/{{subscriptionId}}/providers/Microsoft.Purview/accounts",
        'accounts_by_rg': "/subscriptions/{{subscriptionId}}/resourceGroups/{{resourceGroupName}}/providers/Microsoft.Purview/accounts",
        'account': "/subscriptions/{{subscriptionId}}/resourceGroups/{{resourceGroupName}}/providers/Microsoft.Purview/accounts/{{accountName}}",
        'account_keys': "/subscriptions/{{subscriptionId}}/resourceGroups/{{resourceGroupName}}/providers/Microsoft.Purview/accounts/{{accountName}}/listkeys",
        'private_endpoints': "/subscriptions/{{subscriptionId}}/resourceGroups/{{resourceGroupName}}/providers/Microsoft.Purview/accounts/{{accountName}}/privateEndpointConnections",
        'private_endpoint': "/subscriptions/{{subscriptionId}}/resourceGroups/{{resourceGroupName}}/providers/Microsoft.Purview/accounts/{{accountName}}/privateEndpointConnections/{{privateEndpointConnectionName}}",
        'default_account': "/providers/Microsoft.Purview/checkDefaultAccount",
        'set_default_account': "/providers/Microsoft.Purview/setDefaultAccount",
        'remove_default_account': "/providers/Microsoft.Purview/removeDefaultAccount"
    }
    
    @classmethod
    def format_endpoint(cls, endpoint_template: str, **kwargs) -> str:
        """
        Format an endpoint template with provided parameters
        
        Args:
            endpoint_template: Template string with placeholders like {guid}
            **kwargs: Parameters to substitute in the template
            
        Returns:
            Formatted endpoint string
        """
        return endpoint_template.format(**kwargs)
    
    @classmethod
    def get_api_version_params(cls, endpoint_type: str) -> dict:
        """
        Get appropriate API version parameters for different endpoint types
        
        Args:        Args:
            endpoint_type: Type of endpoint (search, management, scan, etc.)
            
        Returns:
            Dictionary with api-version parameter
        """
        version_map = {
            'search': {'api-version': cls.PREVIEW_VERSION},
            'management': {'api-version': cls.MANAGEMENT_VERSION},
            'scan': {},  # Scan endpoints don't use api-version in URL params
            'catalog': {},  # Catalog endpoints don't use api-version in URL params
            'datamap': {},  # Data map endpoints don't use api-version in URL params
            'policystore': {'api-version': '2021-07-01'},  # Metadata policies
            'policystore_data': {'api-version': '2021-01-01-preview'},  # Data policies
            'share': {'api-version': '2021-09-01-preview'}  # Share endpoints
        }
        return version_map.get(endpoint_type, {})
