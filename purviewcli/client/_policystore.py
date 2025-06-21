"""
Microsoft Purview Policy Store Client - Complete API Coverage
Handles Metadata Policies, Data Policies, DevOps Policies, Self-Service Policies, and more
"""

from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, format_endpoint, get_api_version_params

class Policystore(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'policystore'

    # ========== Metadata Policies ==========
    
    @decorator
    def policystoreReadMetadataRoles(self, args):
        """Get all metadata roles"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['metadata_roles']
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreReadMetadataPolicy(self, args):
        """Get metadata policy by ID or collection"""
        self.method = 'GET'
        if args.get("--policyId"):
            self.endpoint = format_endpoint(ENDPOINTS['policystore']['metadata_policy_by_id'], 
                                          policyId=args["--policyId"])
        elif args.get("--collectionName"):
            self.endpoint = format_endpoint(ENDPOINTS['policystore']['collection_metadata_policy'], 
                                          collectionName=args["--collectionName"])
        else:
            raise ValueError("Either --policyId or --collectionName must be provided")
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreReadMetadataPolicies(self, args):
        """List all metadata policies"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['metadata_policies']
        self.params = get_api_version_params('metadata_policies')
        if args.get('--collectionName'):
            self.params['collectionName'] = args['--collectionName']

    @decorator
    def policystorePutMetadataPolicy(self, args):
        """Create or update a metadata policy"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['metadata_policy_by_id'], 
                                      policyId=args["--policyId"])
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreDeleteMetadataPolicy(self, args):
        """Delete a metadata policy"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['metadata_policy_by_id'], 
                                      policyId=args["--policyId"])
        self.params = get_api_version_params('metadata_policies')

    # ========== Data Policies ==========
    
    @decorator
    def policystoreReadDataPolicies(self, args):
        """List data policies or get specific policy by name"""
        self.method = 'GET'
        if args.get('--policyName'):
            self.endpoint = format_endpoint(ENDPOINTS['policystore']['data_policy_by_name'], 
                                          policyName=args['--policyName'])
        else:
            self.endpoint = ENDPOINTS['policystore']['data_policies']
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreCreateDataPolicy(self, args):
        """Create a new data policy"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['data_policy_by_name'], 
                                      policyName=args['--policyName'])
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreUpdateDataPolicy(self, args):
        """Update an existing data policy"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['data_policy_by_name'], 
                                      policyName=args['--policyName'])
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreDeleteDataPolicy(self, args):
        """Delete a data policy"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['data_policy_by_name'], 
                                      policyName=args['--policyName'])
        self.params = get_api_version_params('metadata_policies')

    # ========== DevOps Policies ==========
    
    @decorator
    def policystoreListDevOpsPolicies(self, args):
        """List all DevOps policies"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['devops_policies']
        self.params = get_api_version_params('devops_policies')

    @decorator
    def policystoreGetDevOpsPolicy(self, args):
        """Get a specific DevOps policy"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['devops_policy'], 
                                      policyName=args['--policyName'])
        self.params = get_api_version_params('devops_policies')

    @decorator
    def policystoreCreateDevOpsPolicy(self, args):
        """Create a new DevOps policy"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['devops_policy'], 
                                      policyName=args['--policyName'])
        self.params = get_api_version_params('devops_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreUpdateDevOpsPolicy(self, args):
        """Update a DevOps policy"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['devops_policy'], 
                                      policyName=args['--policyName'])
        self.params = get_api_version_params('devops_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreDeleteDevOpsPolicy(self, args):
        """Delete a DevOps policy"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['devops_policy'], 
                                      policyName=args['--policyName'])
        self.params = get_api_version_params('devops_policies')

    # ========== Self-Service Policies ==========
    
    @decorator
    def policystoreListSelfServicePolicies(self, args):
        """List all self-service policies"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['self_service_policies']
        self.params = get_api_version_params('self_service_policies')

    @decorator
    def policystoreGetSelfServicePolicy(self, args):
        """Get a specific self-service policy"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['self_service_policy'], 
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('self_service_policies')

    @decorator
    def policystoreCreateSelfServicePolicy(self, args):
        """Create a new self-service policy"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['self_service_policy'], 
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('self_service_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreUpdateSelfServicePolicy(self, args):
        """Update a self-service policy"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['self_service_policy'], 
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('self_service_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreDeleteSelfServicePolicy(self, args):
        """Delete a self-service policy"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['self_service_policy'], 
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('self_service_policies')

    # ========== Policy Collections and Assignments ==========
    
    @decorator
    def policystoreGetPolicyCollections(self, args):
        """Get policy collections"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['policy_collections']
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreGetPolicyAssignments(self, args):
        """Get policy assignments for a collection"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['policy_assignments'], 
                                      collectionName=args['--collectionName'])
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreCreatePolicyAssignment(self, args):
        """Create a policy assignment"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['policy_assignment'], 
                                      collectionName=args['--collectionName'],
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreDeletePolicyAssignment(self, args):
        """Delete a policy assignment"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['policy_assignment'], 
                                      collectionName=args['--collectionName'],
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('metadata_policies')

    # ========== Policy Effects and Evaluation ==========
    
    @decorator
    def policystoreGetPolicyEffects(self, args):
        """Get policy effects for a resource"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['policystore']['policy_effects']
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreEvaluatePolicies(self, args):
        """Evaluate policies for a specific context"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['policystore']['evaluate_policies']
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    # ========== Access Control and Permissions ==========
    
    @decorator
    def policystoreGetUserPermissions(self, args):
        """Get user permissions for a resource"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['user_permissions'], 
                                      userId=args['--userId'])
        self.params = get_api_version_params('metadata_policies')
        if args.get('--resourcePath'):
            self.params['resourcePath'] = args['--resourcePath']

    @decorator
    def policystoreCheckAccess(self, args):
        """Check access permissions for a user"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['policystore']['check_access']
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    # ========== Policy Templates and Definitions ==========
    
    @decorator
    def policystoreGetPolicyTemplates(self, args):
        """Get available policy templates"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['policy_templates']
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreGetPolicyDefinitions(self, args):
        """Get policy definitions"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['policy_definitions']
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreCreatePolicyDefinition(self, args):
        """Create a new policy definition"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['policy_definition'], 
                                      definitionId=args['--definitionId'])
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    # ========== Role Assignments and RBAC ==========
    
    @decorator
    def policystoreListRoleAssignments(self, args):
        """List role assignments"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['role_assignments']
        self.params = get_api_version_params('metadata_policies')
        if args.get('--scope'):
            self.params['scope'] = args['--scope']

    @decorator
    def policystoreCreateRoleAssignment(self, args):
        """Create a role assignment"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['role_assignment'], 
                                      roleAssignmentId=args['--roleAssignmentId'])
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreDeleteRoleAssignment(self, args):
        """Delete a role assignment"""
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['role_assignment'], 
                                      roleAssignmentId=args['--roleAssignmentId'])
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreGetRoleDefinitions(self, args):
        """Get role definitions"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['role_definitions']
        self.params = get_api_version_params('metadata_policies')

    # ========== Data Access Policies ==========
    
    @decorator
    def policystoreListDataAccessPolicies(self, args):
        """List data access policies"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['data_access_policies']
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreGetDataAccessPolicy(self, args):
        """Get a specific data access policy"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['data_access_policy'], 
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreCreateDataAccessPolicy(self, args):
        """Create a data access policy"""
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['data_access_policy'], 
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    # ========== Policy Audit and Compliance ==========
    
    @decorator
    def policystoreGetPolicyAuditLogs(self, args):
        """Get policy audit logs"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['policy_audit_logs']
        self.params = get_api_version_params('metadata_policies')
        if args.get('--startTime'):
            self.params['startTime'] = args['--startTime']
        if args.get('--endTime'):
            self.params['endTime'] = args['--endTime']

    @decorator
    def policystoreGetComplianceReport(self, args):
        """Get compliance report"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['compliance_report']
        self.params = get_api_version_params('metadata_policies')
        if args.get('--reportType'):
            self.params['reportType'] = args['--reportType']

    # ========== Advanced Policy Operations ==========
    
    @decorator
    def policystoreBulkPolicyOperation(self, args):
        """Perform bulk policy operations"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['policystore']['bulk_policy_operations']
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreValidatePolicy(self, args):
        """Validate a policy definition"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['policystore']['validate_policy']
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreSimulatePolicy(self, args):
        """Simulate policy effects"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['policystore']['simulate_policy']
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreGetPolicyChanges(self, args):
        """Get policy change history"""
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['policystore']['policy_changes'], 
                                      policyId=args['--policyId'])
        self.params = get_api_version_params('metadata_policies')

    @decorator
    def policystoreExportPolicies(self, args):
        """Export policies to a file format"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['policystore']['export_policies']
        self.params = get_api_version_params('metadata_policies')
        self.payload = {
            'format': args.get('--format', 'json'),
            'includeAssignments': args.get('--includeAssignments', True)
        }

    @decorator
    def policystoreImportPolicies(self, args):
        """Import policies from a file"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['policystore']['import_policies']
        self.params = get_api_version_params('metadata_policies')
        self.payload = get_json(args, '--payloadFile')
