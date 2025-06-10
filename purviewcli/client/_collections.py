"""
Collections Management Client for Azure Purview
Provides comprehensive collection lifecycle management operations
"""

from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints
import random
import string

def get_random_string(length):
    """Generate random string for collection names"""
    result_str = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(length))
    return result_str

class Collections(Endpoint):
    """Collections Management Operations"""
    
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'catalog'

    # Core Collection CRUD Operations
    @decorator
    def collectionsGetCollections(self, args):
        """List all collections in the account"""
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.COLLECTIONS['base']
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def collectionsGetCollection(self, args):
        """Get a specific collection by name"""
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection'], 
            collectionName=args['--collectionName']
        )
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def collectionsCreateCollection(self, args):
        """Create a new collection"""
        collection_name = args.get('--collectionName') or get_random_string(6)
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection'], 
            collectionName=collection_name
        )
        self.params = {"api-version": "2019-11-01-preview"}
        
        # Build payload from arguments or file
        if args.get('--payloadFile'):
            payload_data = get_json(args, '--payloadFile')
        else:
            payload_data = {}
        
        self.payload = {
            "friendlyName": args.get('--friendlyName', collection_name),
            "name": collection_name,
            "description": args.get('--description', ''),
            "parentCollection": {
                "referenceName": args.get('--parentCollection', 'root'),
                "type": "CollectionReference"
            },
            **payload_data
        }

    @decorator
    def collectionsUpdateCollection(self, args):
        """Update an existing collection"""
        self.method = 'PATCH'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection'], 
            collectionName=args['--collectionName']
        )
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def collectionsDeleteCollection(self, args):
        """Delete a collection"""
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection'], 
            collectionName=args['--collectionName']
        )
        self.params = {"api-version": "2019-11-01-preview"}

    # Collection Hierarchy Operations
    @decorator
    def collectionsGetCollectionPath(self, args):
        """Get the collection path (parent references)"""
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection_path'], 
            collectionName=args['--collectionName']
        )
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def collectionsGetChildCollectionNames(self, args):
        """Get child collections for a collection"""
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['child_collection_names'], 
            collectionName=args['--collectionName']
        )
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def collectionsMoveEntities(self, args):
        """Move entities to a different collection"""
        self.method = 'POST'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection_move'], 
            collectionName=args['--collectionName']
        )
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')

    # Collection Administration Operations
    @decorator
    def collectionsGetCollectionAdmins(self, args):
        """Get collection administrators"""
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection_admins'], 
            collectionName=args['--collectionName']
        )
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def collectionsAddCollectionAdmin(self, args):
        """Add collection administrator"""
        self.method = 'PUT'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection_admin_add'], 
            collectionName=args['--collectionName'],
            adminObjectId=args['--adminObjectId']
        )
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = {
            "objectId": args['--adminObjectId'],
            "type": args.get('--adminType', 'User')
        }

    @decorator
    def collectionsRemoveCollectionAdmin(self, args):
        """Remove collection administrator"""
        self.method = 'DELETE'
        self.endpoint = PurviewEndpoints.format_endpoint(
            PurviewEndpoints.COLLECTIONS['collection_admin_remove'], 
            collectionName=args['--collectionName'],
            adminObjectId=args['--adminObjectId']
        )
        self.params = {"api-version": "2019-11-01-preview"}

    # Advanced Collection Operations
    @decorator
    def collectionsGetCollectionStatistics(self, args):
        """Get statistics for a collection"""
        self.method = 'GET'
        self.endpoint = f"{PurviewEndpoints.COLLECTIONS['collection']}/statistics"
        self.endpoint = self.endpoint.format(collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def collectionsGetCollectionPermissions(self, args):
        """Get permissions for a collection"""
        self.method = 'GET'
        self.endpoint = f"{PurviewEndpoints.COLLECTIONS['collection']}/permissions"
        self.endpoint = self.endpoint.format(collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}

    @decorator
    def collectionsSetCollectionPermissions(self, args):
        """Set permissions for a collection"""
        self.method = 'PUT'
        self.endpoint = f"{PurviewEndpoints.COLLECTIONS['collection']}/permissions"
        self.endpoint = self.endpoint.format(collectionName=args['--collectionName'])
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def collectionsBulkOperations(self, args):
        """Perform bulk operations on collections"""
        self.method = 'POST'
        self.endpoint = f"{PurviewEndpoints.COLLECTIONS['base']}/bulk"
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def collectionsExportCollections(self, args):
        """Export collections configuration"""
        self.method = 'GET'
        self.endpoint = f"{PurviewEndpoints.COLLECTIONS['base']}/export"
        self.params = {
            "api-version": "2019-11-01-preview",
            "format": args.get('--format', 'json'),
            "includeChildren": args.get('--includeChildren', True)
        }

    @decorator
    def collectionsImportCollections(self, args):
        """Import collections configuration"""
        self.method = 'POST'
        self.endpoint = f"{PurviewEndpoints.COLLECTIONS['base']}/import"
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def collectionsValidateHierarchy(self, args):
        """Validate collection hierarchy"""
        self.method = 'POST'
        self.endpoint = f"{PurviewEndpoints.COLLECTIONS['base']}/validate-hierarchy"
        self.params = {"api-version": "2019-11-01-preview"}
        self.payload = get_json(args, '--payloadFile')
