"""
Account Management Client for Microsoft Purview
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/accounts
API Version: 2019-11-01-preview

Official Account Operations:
1. Get Account Properties - GET /account  
2. Update Account Properties - PATCH /account
3. Get Access Keys - POST /account/keys
4. Regenerate Access Key - POST /account/keys/regenerate
"""

from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, DATAMAP_API_VERSION

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
        self.endpoint = ENDPOINTS['account']['base']
        self.params = {"api-version": DATAMAP_API_VERSION}

    @decorator
    def accountUpdateAccount(self, args):
        """Update Account Properties - Official API Operation"""
        self.method = 'PATCH'
        self.endpoint = ENDPOINTS['account']['settings']
        self.params = {"api-version": DATAMAP_API_VERSION}
        self.payload = get_json(args, '--payloadFile')

    # === ACCESS KEYS OPERATIONS ===
    
    @decorator
    def accountGetAccessKeys(self, args):
        """Get Access Keys - Official API Operation"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['account']['usage']
        self.params = {"api-version": DATAMAP_API_VERSION}

    @decorator
    def accountRegenerateAccessKeys(self, args):
        """Regenerate Access Key - Official API Operation"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['account']['usage']
        self.params = {"api-version": DATAMAP_API_VERSION}