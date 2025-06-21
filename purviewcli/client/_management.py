"""
Microsoft Purview Management Client - Complete API Coverage
Handles all Account Management, Resource Provider, and Azure Management operations
"""

import uuid
from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, format_endpoint, get_api_version_params

class Management(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'management'

    # ========== Resource Provider Operations ==========
    
    @decorator
    def managementListOperations(self, args):
        """List all available Resource Provider operations"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['management']['operations']
        self.params = get_api_version_params('account')

    # ========== Account Management ==========
    
    @decorator
    def managementCheckNameAvailability(self, args):
        """Check if account name is available"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['management']['check_name_availability'], 
                                      subscriptionId=args["--subscriptionId"])
        self.params = get_api_version_params('account')
        self.payload = {
            'name': args['--accountName'], 
            'type': 'Microsoft.Purview/accounts'
        }
    
    @decorator
    def managementReadAccounts(self, args):
        """List Purview accounts by subscription or resource group"""
        self.method = 'GET'
        if args.get("--resourceGroupName") is None:
            self.endpoint = format_endpoint(ENDPOINTS['management']['accounts'], 
                                          subscriptionId=args["--subscriptionId"])
        else:
            self.endpoint = format_endpoint(ENDPOINTS['management']['accounts_by_rg'], 
                                          subscriptionId=args["--subscriptionId"], 
                                          resourceGroupName=args["--resourceGroupName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementReadAccount(self, args):
        """Get details of a specific Purview account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
    
    @decorator
    def managementCreateAccount(self, args):
        """Create a new Purview account"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def managementUpdateAccount(self, args):
        """Update an existing Purview account"""
        self.method = 'PATCH'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def managementDeleteAccount(self, args):
        """Delete a Purview account"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    # ========== Account Keys Management ==========
    
    @decorator
    def managementGetAccessKeys(self, args):
        """Get access keys for a Purview account"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['management']['access_keys'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementRegenerateAccessKey(self, args):
        """Regenerate access keys for a Purview account"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['management']['regenerate_access_key'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = {'keyType': args.get('--keyType', 'PrimaryAccessKey')}

    # ========== Private Link Resources ==========
    
    @decorator
    def managementListPrivateLinkResources(self, args):
        """List private link resources for a Purview account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_link_resources'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementGetPrivateLinkResource(self, args):
        """Get details of a specific private link resource"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_link_resource'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"],
                                      privateLinkResourceName=args["--privateLinkResourceName"])
        self.params = get_api_version_params('account')

    # ========== Private Endpoint Connections ==========
    
    @decorator
    def managementListPrivateEndpointConnections(self, args):
        """List private endpoint connections for a Purview account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_endpoint_connections'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementGetPrivateEndpointConnection(self, args):
        """Get details of a specific private endpoint connection"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_endpoint_connection'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"],
                                      privateEndpointConnectionName=args["--privateEndpointConnectionName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementCreateOrUpdatePrivateEndpointConnection(self, args):
        """Create or update a private endpoint connection"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_endpoint_connection'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"],
                                      privateEndpointConnectionName=args["--privateEndpointConnectionName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def managementDeletePrivateEndpointConnection(self, args):
        """Delete a private endpoint connection"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_endpoint_connection'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"],
                                      privateEndpointConnectionName=args["--privateEndpointConnectionName"])
        self.params = get_api_version_params('account')

    # ========== Account Features and Configuration ==========
    
    @decorator
    def managementGetAccountFeatures(self, args):
        """Get account features and configurations"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_features'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementUpdateAccountFeatures(self, args):
        """Update account features and configurations"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_features'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    # ========== Account Ingestion Operations ==========
    
    @decorator
    def managementGetIngestionStatus(self, args):
        """Get ingestion status for the account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['ingestion_status'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementListResourceSets(self, args):
        """List resource sets for the account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['resource_sets'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    # ========== Account Security and Compliance ==========
    
    @decorator
    def managementGetSecuritySettings(self, args):
        """Get security settings for the account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['security_settings'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementUpdateSecuritySettings(self, args):
        """Update security settings for the account"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['management']['security_settings'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    # ========== Account Monitoring and Diagnostics ==========
    
    @decorator
    def managementGetDiagnosticSettings(self, args):
        """Get diagnostic settings for the account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['diagnostic_settings'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementCreateOrUpdateDiagnosticSettings(self, args):
        """Create or update diagnostic settings"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['management']['diagnostic_setting'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"],
                                      diagnosticSettingName=args["--diagnosticSettingName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def managementDeleteDiagnosticSetting(self, args):
        """Delete a diagnostic setting"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['management']['diagnostic_setting'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"],
                                      diagnosticSettingName=args["--diagnosticSettingName"])
        self.params = get_api_version_params('account')

    # ========== Account Usage and Metrics ==========
    
    @decorator
    def managementGetAccountUsage(self, args):
        """Get account usage metrics"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_usage'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementGetAccountMetrics(self, args):
        """Get account metrics"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_metrics'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        if args.get('--timespan'):
            self.params['timespan'] = args['--timespan']
        if args.get('--metricNames'):
            self.params['metricnames'] = args['--metricNames']

    # ========== Account Tags and Metadata ==========
    
    @decorator
    def managementGetAccountTags(self, args):
        """Get tags for a Purview account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_tags'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementUpdateAccountTags(self, args):
        """Update tags for a Purview account"""
        self.method = 'PATCH'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = {'tags': get_json(args, '--tagsFile')}

    # ========== Subscription and Tenant Operations ==========
    
    @decorator
    def managementListAccountsBySubscription(self, args):
        """List all Purview accounts in a subscription"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['accounts'], 
                                      subscriptionId=args["--subscriptionId"])
        self.params = get_api_version_params('account')

    @decorator
    def managementGetSubscriptionUsage(self, args):
        """Get Purview usage for a subscription"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['subscription_usage'], 
                                      subscriptionId=args["--subscriptionId"])
        self.params = get_api_version_params('account')

    # ========== Advanced Management Operations ==========
    
    @decorator
    def managementGetAccountStatus(self, args):
        """Get detailed status of a Purview account"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_status'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementValidateAccountConfiguration(self, args):
        """Validate account configuration"""
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['management']['validate_configuration'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def managementGetAccountHealth(self, args):
        """Get account health status"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_health'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
