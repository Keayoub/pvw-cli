from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

class Policystore(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'policystore'

    # Metadata Policies
    @decorator
    def policystoreReadMetadataRoles(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.POLICYSTORE['metadata_roles']
        self.params = PurviewEndpoints.get_api_version_params('policystore')

    @decorator
    def policystoreReadMetadataPolicy(self, args):
        self.method = 'GET'
        if args["--policyId"] is None:
            self.endpoint = PurviewEndpoints.format_endpoint(
                PurviewEndpoints.POLICYSTORE['collection_metadata_policy'], 
                collectionName=args["--collectionName"]
            )
        else:
            self.endpoint = PurviewEndpoints.format_endpoint(
                PurviewEndpoints.POLICYSTORE['metadata_policy_by_id'], 
                policyId=args["--policyId"]
            )
        self.params = PurviewEndpoints.get_api_version_params('policystore')

    @decorator
    def policystoreReadMetadataPolicies(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.POLICYSTORE['metadata_policies']
        self.params = PurviewEndpoints.get_api_version_params('policystore')

    @decorator
    def policystorePutMetadataPolicy(self, args):
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.POLICYSTORE['metadata_policy_by_id'], 
            policyId=args["--policyId"]
        )
        self.params = PurviewEndpoints.get_api_version_params('policystore')
        self.payload = get_json(args, '--payloadFile')

    # Data Policies
    @decorator
    def policystoreReadDataPolicies(self, args):
        policyName = args['--policyName']
        self.method = 'GET'
        if args['--policyName']:
            self.endpoint = PurviewEndpoints.format_endpoint(
                PurviewEndpoints.POLICYSTORE['data_policy_by_name'], 
                policyName=policyName
            )
        else:
            self.endpoint = PurviewEndpoints.POLICYSTORE['data_policies']
        self.params = PurviewEndpoints.get_api_version_params('policystore_data')

    @decorator
    def policystorePutDataPolicy(self, args):
        policyName = args['--policyName']
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.POLICYSTORE['data_policy_by_name'], 
            policyName=policyName
        )
        self.params = PurviewEndpoints.get_api_version_params('policystore_data')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreReadDataPolicyScopes(self, args):
        policyName = args['--policyName']
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.POLICYSTORE['data_policy_scopes'], 
            policyName=policyName
        )
        self.params = PurviewEndpoints.get_api_version_params('policystore_data')

    @decorator
    def policystorePutDataPolicyScope(self, args):
        policyName = args['--policyName']
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.POLICYSTORE['data_policy_scopes'], 
            policyName=policyName
        )
        self.params = PurviewEndpoints.get_api_version_params('policystore_data')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreDeleteDataPolicyScope(self, args):
        policyName = args['--policyName']
        datasource = args['--datasource']
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.POLICYSTORE['data_policy_scope_by_datasource'], 
            policyName=policyName,
            datasource=datasource
        )
        self.params = PurviewEndpoints.get_api_version_params('policystore_data')

    @decorator
    def policystoreDeleteDataPolicy(self, args):
        policyName = args['--policyName']
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.POLICYSTORE['data_policy_by_name'], 
            policyName=policyName
        )
        self.params = PurviewEndpoints.get_api_version_params('policystore_data')
