from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints
import random
import string

def get_random_string(length):
    result_str = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))
    return result_str

class Account(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'account'

    @decorator
    def accountGetAccount(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.ACCOUNT['account']
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountUpdateAccount(self, args):
        self.method = 'PATCH'
        self.endpoint = PurviewEndpoints.ACCOUNT['account']
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = {
            "friendlyName": f"{args['--friendlyName']}"
        }

    @decorator
    def accountGetCollections(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.ACCOUNT['collections']
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountGetCollection(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ACCOUNT['collection'], collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountGetCollectionPath(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ACCOUNT['collection_path'], collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountGetChildCollectionNames(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.ACCOUNT['child_collection_names'], collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountDeleteCollection(self, args):
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.COLLECTIONS['collection'], collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountPutCollection(self, args):
        collectionName = args.get('--collectionName')
        if not collectionName:
            collectionName = get_random_string(6)
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.COLLECTIONS['collection'], collectionName=collectionName)
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = {
            "friendlyName": f"{args['--friendlyName']}",
            "name": f"{collectionName}",
            "parentCollection": {
                "referenceName": f"{args['--parentCollection']}",
                "type": "CollectionReference"
            }
        }
    
    @decorator
    def accountCreateCollection(self, args):
        """Create a new collection with specified parameters"""
        collectionName = args.get('--collectionName') or get_random_string(6)
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.COLLECTIONS['collection'], collectionName=collectionName)
        self.params = {"api-version": "2019-11-01-preview"}
        payload_data = get_json(args, '--payloadFile') if args.get('--payloadFile') else {}
        self.payload = {
            "friendlyName": args.get('--friendlyName', collectionName),
            "name": collectionName,
            "parentCollection": {
                "referenceName": args.get('--parentCollection', 'root'),
                "type": "CollectionReference"
            },
            **payload_data
        }
    
    @decorator
    def accountUpdateCollection(self, args):
        """Update an existing collection"""
        self.method = 'PATCH'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.COLLECTIONS['collection'], collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')
    
    @decorator
    def accountMoveCollection(self, args):
        """Move entities to a different collection"""
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.COLLECTIONS['collection_move'], collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')
    
    @decorator
    def accountGetCollectionAdmins(self, args):
        """Get collection administrators"""
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.COLLECTIONS['collection_admins'], collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}
    
    @decorator
    def accountAddCollectionAdmin(self, args):
        """Add collection administrator"""
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.COLLECTIONS['collection_admin_add'], 
                                                        collectionName=args['--collectionName'],
                                                        adminObjectId=args['--adminObjectId'])
        self.params = {"api-version": "2019-11-01-preview"}
    
    @decorator
    def accountRemoveCollectionAdmin(self, args):
        """Remove collection administrator"""
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(PurviewEndpoints.COLLECTIONS['collection_admin_remove'], 
                                                        collectionName=args['--collectionName'],
                                                        adminObjectId=args['--adminObjectId'])
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountGetAccessKeys(self, args):
        self.method = 'POST'
        self.endpoint = f"/listkeys"
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountRegenerateAccessKeys(self, args):
        self.method = 'POST'
        self.endpoint = f"/regeneratekeys"
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = {
            "keyType": f"{args['--keyType']}"
        }

    @decorator
    def accountGetResourceSetRules(self, args):
        self.method = 'GET'
        self.endpoint = f"/resourceSetRuleConfigs"
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountDeleteResourceSetRule(self, args):
        self.method = 'DELETE'
        self.endpoint = f"/resourceSetRuleConfigs/defaultResourceSetRuleConfig"
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountGetResourceSetRule(self, args):
        self.method = 'GET'
        self.endpoint = f"/resourceSetRuleConfigs/defaultResourceSetRuleConfig"
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def accountPutResourceSetRule(self, args):
        self.method = 'PUT'
        self.endpoint = f"/resourceSetRuleConfigs/defaultResourceSetRuleConfig"
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')
