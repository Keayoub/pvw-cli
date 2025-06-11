"""
Account Management Client for Azure Purview
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/accounts
API Version: 2019-11-01-preview

Official Account Operations:
1. Get Account Properties - GET /account  
2. Update Account Properties - PATCH /account
3. Get Access Keys - POST /account/keys
4. Regenerate Access Key - POST /account/keys/regenerate
"""

from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

class Account(Endpoint):
    """Account Management Operations - Official API Operations Only"""
    
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'account'

    # === ACCOUNT PROPERTIES OPERATIONS ===
    
    @decorator
    def accountGetAccount(self, args):
        """Get Account Properties - Official API Operation"""
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.ACCOUNT['account']
        self.params = PurviewEndpoints.get_api_version_params('account')

    @decorator
    def accountUpdateAccount(self, args):
        """Update Account Properties - Official API Operation"""
        self.method = 'PATCH'
        self.endpoint = PurviewEndpoints.ACCOUNT['account_update']
        self.params = PurviewEndpoints.get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    # === ACCESS KEYS OPERATIONS ===
    
    @decorator
    def accountGetAccessKeys(self, args):
        """Get Access Keys - Official API Operation"""
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.ACCOUNT['access_keys']
        self.params = PurviewEndpoints.get_api_version_params('account')

    @decorator
    def accountRegenerateAccessKeys(self, args):
        """Regenerate Access Key - Official API Operation"""
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.ACCOUNT['regenerate_access_key']
        self.params = PurviewEndpoints.get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')