from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, DATAMAP_API_VERSION

class Policystore(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'policystore'

    # Metadata Policies
    @decorator
    def policystoreReadMetadataRoles(self, args):
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['metadata_roles']
        self.params = {'api-version': DATAMAP_API_VERSION}

    @decorator
    def policystoreReadMetadataPolicy(self, args):
        self.method = 'GET'
        if args["--policyId"] is None:
            self.endpoint = ENDPOINTS['policystore']['collection_metadata_policy'].format(
                collectionName=args["--collectionName"]
            )
        else:
            self.endpoint = ENDPOINTS['policystore']['metadata_policy_by_id'].format(
                policyId=args["--policyId"]
            )
        self.params = {'api-version': DATAMAP_API_VERSION}

    @decorator
    def policystoreReadMetadataPolicies(self, args):
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['metadata_policies']
        self.params = {'api-version': DATAMAP_API_VERSION}

    @decorator
    def policystorePutMetadataPolicy(self, args):
        self.method = 'PUT'
        self.endpoint = ENDPOINTS['policystore']['metadata_policy_by_id'].format(
            policyId=args["--policyId"]
        )
        self.params = {'api-version': DATAMAP_API_VERSION}
        self.payload = get_json(args, '--payloadFile')

    # Data Policies
    @decorator
    def policystoreReadDataPolicies(self, args):
        policyName = args['--policyName']
        self.method = 'GET'
        if args['--policyName']:
            self.endpoint = ENDPOINTS['policystore']['data_policy_by_name'].format(
                policyName=policyName
            )
        else:
            self.endpoint = ENDPOINTS['policystore']['data_policies']
        self.params = {'api-version': DATAMAP_API_VERSION}

    @decorator
    def policystorePutDataPolicy(self, args):
        policyName = args['--policyName']
        self.method = 'PUT'
        self.endpoint = ENDPOINTS['policystore']['data_policy_by_name'].format(
            policyName=policyName
        )
        self.params = {'api-version': DATAMAP_API_VERSION}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreReadDataPolicyScopes(self, args):
        policyName = args['--policyName']
        self.method = 'GET'
        self.endpoint = ENDPOINTS['policystore']['data_policy_scopes'].format(
            policyName=policyName
        )
        self.params = {'api-version': DATAMAP_API_VERSION}

    @decorator
    def policystorePutDataPolicyScope(self, args):
        policyName = args['--policyName']
        self.method = 'PUT'
        self.endpoint = ENDPOINTS['policystore']['data_policy_scopes'].format(
            policyName=policyName
        )
        self.params = {'api-version': DATAMAP_API_VERSION}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def policystoreDeleteDataPolicyScope(self, args):
        policyName = args['--policyName']
        datasource = args['--datasource']
        self.method = 'DELETE'
        self.endpoint = ENDPOINTS['policystore']['data_policy_scope_by_datasource'].format(
            policyName=policyName,
            datasource=datasource
        )
        self.params = {'api-version': DATAMAP_API_VERSION}

    @decorator
    def policystoreDeleteDataPolicy(self, args):
        policyName = args['--policyName']
        self.method = 'DELETE'
        self.endpoint = ENDPOINTS['policystore']['data_policy_by_name'].format(
            policyName=policyName
        )
        self.params = {'api-version': DATAMAP_API_VERSION}
