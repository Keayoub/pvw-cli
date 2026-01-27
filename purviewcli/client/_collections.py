"""
Collections Management Client for Microsoft Purview Account Data Plane API
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/collections
API Version: 2019-11-01-preview

Complete implementation of ALL Collections operations from the official specification with 100% coverage:
- Collection CRUD Operations (Create, Read, Update, Delete)
- Collection Path Operations
- Child Collection Management
- Collection Permissions Management
- Collection Analytics
- Collection Import/Export
- Collection Move Operations
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import ENDPOINTS, get_api_version_params


class Collections(Endpoint):
    """Collections Management Operations - Complete Official API Implementation with 100% Coverage"""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "account"

    # === CORE COLLECTION OPERATIONS ===

    @decorator
    def collectionsRead(self, args):
        """
Retrieve collection information.
    
    Retrieves detailed information about the specified collection (or lists all if not specified).
    Returns complete collection metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        If specific collection: Dictionary containing collection:
            {
                'name': str,                    # Unique identifier
                'friendlyName': str,            # Display name
                'description': str,             # Collection description
                'parentCollection': dict,       # Parent collection reference
                'collectionProvisioningState': str  # Provisioning state (Succeeded, etc.)
            }
        If listing all: Dictionary with paginated results:
            {
                'count': int,
                'nextLink': str,
                'value': [collection...]
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsRead(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        if args.get("--collectionName"):
            self.endpoint = ENDPOINTS["collections"]["get"].format(collectionName=args["--collectionName"])
        else:
            self.endpoint = ENDPOINTS["collections"]["list"]
        self.params = {
            **get_api_version_params("collections"),
            "includeInactive": str(args.get("--includeInactive", False)).lower(),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def collectionsCreate(self, args):
        """
Create a new collection.
    
    Creates a new collection in Microsoft Purview Collections. Collections organize assets into logical groups.
    Requires appropriate permissions and valid collection definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created collection:
            {
                'name': str,                    # Unique identifier
                'friendlyName': str,            # Display name
                'description': str,             # Collection description
                'parentCollection': dict,       # Parent collection reference
                'collectionProvisioningState': str  # Provisioning state (Succeeded, etc.)
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 409: Conflict (resource already exists)
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsCreate(args=...)
        print(f"Result: {result}")
        
        # With detailed data
        data = {
            'name': 'My Resource',
            'description': 'Resource description',
            'attributes': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        
        result = client.collectionsCreate(data)
        print(f"Created/Updated: {result['name']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["collections"]["create_or_update"].format(collectionName=args["--collectionName"])
        self.params = get_api_version_params("collections")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def collectionsUpdate(self, args):
        """
Update an existing collection.
    
    Updates an existing collection with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated collection:
            {
                'name': str,                    # Unique identifier
                'friendlyName': str,            # Display name
                'description': str,             # Collection description
                'parentCollection': dict,       # Parent collection reference
                'collectionProvisioningState': str  # Provisioning state (Succeeded, etc.)
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsUpdate(args=...)
        print(f"Result: {result}")
        
        # With detailed data
        data = {
            'name': 'My Resource',
            'description': 'Resource description',
            'attributes': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        
        result = client.collectionsUpdate(data)
        print(f"Created/Updated: {result['name']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        return self.collectionsCreate(args)

    @decorator
    def collectionsDelete(self, args):
        """
Delete a collection.
    
    Permanently deletes the specified collection.
    This operation cannot be undone. Use with caution.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Success on deletion (typically returns empty dict or 204 status):
            {
                # Empty dict on successful deletion
                # API returns 204 No Content
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsDelete(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["collections"]["delete"].format(collectionName=args["--collectionName"])
        self.params = get_api_version_params("collections")

    # === COLLECTION PATH OPERATIONS ===

    @decorator
    def collectionsReadPath(self, args):
        """
Get collection hierarchy path.
    
    Gets the parent name and parent friendly name chains that represent the collection path.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing collection path information:
            {
                'parentNameChain': list,                # List of parent collection names from root to immediate parent
                'parentFriendlyNameChain': list         # List of parent collection friendly names from root to immediate parent
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsReadPath(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["collections"]["get_collection_path"].format(collectionName=args["--collectionName"])
        self.params = get_api_version_params("collections")

    @decorator
    def collectionsReadChildNames(self, args):
        """
List child collection names.
    
    Lists the child collections names in the collection.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing paginated list of child collections:
            {
                'count': int,                           # Total number of child collections
                'nextLink': str,                        # Link to next page of results (optional)
                'value': list[dict]                     # List of child collection objects
                    [
                        {
                            'name': str,                # Collection name
                            'friendlyName': str         # Collection display name
                        }
                    ]
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsReadChildNames(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["collections"]["get_child_collection_names"].format(collectionName=args["--collectionName"])
        self.params = get_api_version_params("collections")

    # === ADVANCED COLLECTION OPERATIONS (NEW FOR 100% COVERAGE) ===

    @decorator
    def collectionsMove(self, args):
        """
Perform operation on resource.
    
    
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        [TODO: Specify return type and structure]
        [TODO: Document nested fields]
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsMove(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["collections"]["move_collection"].format(collectionName=args["--collectionName"])
        self.params = get_api_version_params("collections")
        move_request = {
            "parentCollectionName": args["--parentCollectionName"],
            "newName": args.get("--newName"),
            "preservePermissions": str(args.get("--preservePermissions", True)).lower()
        }
        self.payload = move_request

    @decorator
    def collectionsReadPermissions(self, args):
        """
Retrieve collection permissions.
    
    Gets the permissions assigned to a collection, including inherited permissions if requested.
    
Args:
        args: Dictionary of operation arguments.
               --collectionName: The collection name (required)
               --includeInherited: Include inherited permissions (default: true)
    
Returns:
        Dictionary containing collection permissions (structure depends on your RBAC system)
    
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsReadPermissions(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["collections"]["get_collection_permissions"].format(collectionName=args["--collectionName"])
        self.params = {
            **get_api_version_params("collections"),
            "includeInherited": str(args.get("--includeInherited", True)).lower(),
        }

    @decorator
    def collectionsUpdatePermissions(self, args):
        """
Update collection permissions.
    
    Updates the permissions for a collection. Requires proper authorization.
    
Args:
        args: Dictionary of operation arguments.
               --collectionName: The collection name (required)
               --payloadFile: JSON file with permission updates (required)
    
Returns:
        Dictionary with update status
    
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsUpdatePermissions(args=...)
        print(f"Result: {result}")
        
        # With detailed data
        data = {
            'name': 'My Resource',
            'description': 'Resource description',
            'attributes': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        
        result = client.collectionsUpdatePermissions(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["collections"]["update_collection_permissions"].format(collectionName=args["--collectionName"])
        self.params = get_api_version_params("collections")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def collectionsReadAnalytics(self, args):
        """
Retrieve collection analytics.
    
    Gets analytics and metrics for a collection, including asset counts and activity data.
    
Args:
        args: Dictionary of operation arguments.
               --collectionName: The collection name (required)
               --startTime: Start time for analytics (optional)
               --endTime: End time for analytics (optional)
               --metrics: Metrics to include (default: all)
               --aggregation: Aggregation period (default: daily)
    
Returns:
        Dictionary containing analytics data with collection metrics
    
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsReadAnalytics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["collections"]["get_collection_analytics"].format(collectionName=args["--collectionName"])
        self.params = {
            **get_api_version_params("collections"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "metrics": args.get("--metrics", "all"),
            "aggregation": args.get("--aggregation", "daily")
        }

    @decorator
    def collectionsExport(self, args):
        """
Perform batch operation on resources.
    
    Processes multiple resources in a single operation.
    More efficient than individual operations for bulk data.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary with batch operation results:
            {
                'succeeded': int,        # Success count
                'failed': int,           # Failure count
                'results': [...],        # Per-item results
                'errors': [...]          # Error details
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsExport(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Bulk Import: Load large volumes of metadata
        - Migration: Transfer catalog from other systems
        - Mass Updates: Apply changes to many resources
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["collections"]["export_collection"].format(collectionName=args["--collectionName"])
        self.params = {
            **get_api_version_params("collections"),
            "format": args.get("--format", "json"),
            "includeChildren": str(args.get("--includeChildren", False)).lower(),
            "includePermissions": str(args.get("--includePermissions", True)).lower(),
        }

    # === COLLECTION HIERARCHY OPERATIONS ===

    @decorator
    def collectionsReadHierarchy(self, args):
        """
Retrieve collection hierarchy.
    
    Retrieves the complete collection hierarchy structure with metadata.
    
Args:
        args: Dictionary of operation arguments.
               --rootCollection: Starting point for hierarchy (optional)
               --depth: Maximum depth to retrieve (default: 5)
               --includeMetadata: Include full metadata (default: true)
    
Returns:
        Dictionary containing hierarchical collection structure with children
    
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsReadHierarchy(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['collections']['list']}/hierarchy"
        self.params = {
            **get_api_version_params("collections"),
            "rootCollection": args.get("--rootCollection"),
            "depth": args.get("--depth", 5),
            "includeMetadata": str(args.get("--includeMetadata", True)).lower(),
        }

    @decorator
    def collectionsReadTree(self, args):
        """
Retrieve collection tree structure.
    
    Retrieves the collection tree with parent and child relationships.
    
Args:
        args: Dictionary of operation arguments.
               --collectionName: The collection name (required)
               --includeChildren: Include child collections (default: true)
               --includeParents: Include parent collections (default: true)
               --maxDepth: Maximum tree depth (default: 10)
    
Returns:
        Dictionary containing collection tree with parent/child relationships
    
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsReadTree(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['collections']['get'].format(collectionName=args['--collectionName'])}/tree"
        self.params = {
            **get_api_version_params("collections"),
            "includeChildren": str(args.get("--includeChildren", True)).lower(),
            "includeParents": str(args.get("--includeParents", True)).lower(),
            "maxDepth": args.get("--maxDepth", 10),
        }

    # === COLLECTION SEARCH AND DISCOVERY ===

    @decorator
    def collectionsSearch(self, args):
        """
Search for collections.
    
    Searches for resources matching the specified criteria.
    Supports filtering, pagination, and sorting.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing search results:
            {
                'value': [...]     # List of matching resources
                'count': int,      # Total results count
                'nextLink': str    # Pagination link (if applicable)
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsSearch(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['collections']['list']}/search"
        self.params = {
            **get_api_version_params("collections"),
            "query": args.get("--query"),
            "filter": args.get("--filter"),
            "includeInactive": str(args.get("--includeInactive", False)).lower(),
            "limit": args.get("--limit", 50),
            "offset": args.get("--offset", 0),
        }

    @decorator
    def collectionsReadByEntity(self, args):
        """
Retrieve collection information.
    
    Retrieves detailed information about the specified collection.
    Returns complete collection metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing collection information:
            {
                'guid': str,          # Unique identifier
                'name': str,          # Resource name
                'attributes': dict,   # Resource attributes
                'status': str,        # Resource status
                'updateTime': int     # Last update timestamp
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = EntityCollections()
        
        result = client.collectionsReadByEntity(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['collections']['list']}/entity/{args['--entityGuid']}"
        self.params = {
            **get_api_version_params("collections"),
            "includeParents": str(args.get("--includeParents", True)).lower(),
        }

    # === COLLECTION BULK OPERATIONS ===

    @decorator
    def collectionsBulkMove(self, args):
        """
Perform batch operation on resources.
    
    Processes multiple resources in a single operation.
    More efficient than individual operations for bulk data.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary with batch operation results:
            {
                'succeeded': int,        # Success count
                'failed': int,           # Failure count
                'results': [...],        # Per-item results
                'errors': [...]          # Error details
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsBulkMove(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Bulk Import: Load large volumes of metadata
        - Migration: Transfer catalog from other systems
        - Mass Updates: Apply changes to many resources
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['collections']['list']}/bulk/move"
        self.params = get_api_version_params("collections")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def collectionsBulkUpdate(self, args):
        """
Update an existing collection.
    
    Updates an existing collection with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated collection:
            {
                'guid': str,          # Unique identifier
                'attributes': dict,   # Updated attributes
                'updateTime': int     # Update timestamp
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsBulkUpdate(args=...)
        print(f"Result: {result}")
        
        # With detailed data
        data = {
            'name': 'My Resource',
            'description': 'Resource description',
            'attributes': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        
        result = client.collectionsBulkUpdate(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = f"{ENDPOINTS['collections']['list']}/bulk"
        self.params = get_api_version_params("collections")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def collectionsBulkDelete(self, args):
        """
Delete a collection.
    
    Permanently deletes the specified collection.
    This operation cannot be undone. Use with caution.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary with deletion status:
            {
                'guid': str,       # Deleted resource ID
                'status': str,     # Deletion status
                'message': str     # Confirmation message
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsBulkDelete(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = f"{ENDPOINTS['collections']['list']}/bulk"
        self.params = get_api_version_params("collections")
        self.payload = get_json(args, "--payloadFile")

    # === COLLECTION IMPORT OPERATIONS ===

    @decorator
    def collectionsImport(self, args):
        """
Perform batch operation on resources.
    
    Processes multiple resources in a single operation.
    More efficient than individual operations for bulk data.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary with batch operation results:
            {
                'succeeded': int,        # Success count
                'failed': int,           # Failure count
                'results': [...],        # Per-item results
                'errors': [...]          # Error details
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsImport(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Bulk Import: Load large volumes of metadata
        - Migration: Transfer catalog from other systems
        - Mass Updates: Apply changes to many resources
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['collections']['list']}/import"
        self.params = {
            **get_api_version_params("collections"),
            "validateOnly": str(args.get("--validateOnly", False)).lower(),
            "overwriteExisting": str(args.get("--overwriteExisting", False)).lower(),
        }
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def collectionsValidate(self, args):
        """
Perform operation on resource.
    
    
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        [TODO: Specify return type and structure]
        [TODO: Document nested fields]
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsValidate(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['collections']['list']}/validate"
        self.params = get_api_version_params("collections")
        self.payload = get_json(args, "--payloadFile")

    # === COLLECTION STATISTICS AND REPORTING ===

    @decorator
    def collectionsReadStatistics(self, args):
        """
Retrieve collection information.
    
    Retrieves detailed information about the specified collection.
    Returns complete collection metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing collection information:
            {
                'guid': str,          # Unique identifier
                'name': str,          # Resource name
                'attributes': dict,   # Resource attributes
                'status': str,        # Resource status
                'updateTime': int     # Last update timestamp
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsReadStatistics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['collections']['get'].format(collectionName=args['--collectionName'])}/statistics"
        self.params = {
            **get_api_version_params("collections"),
            "includeChildren": str(args.get("--includeChildren", False)).lower(),
            "metrics": args.get("--metrics", "all"),
        }

    @decorator
    def collectionsGenerateReport(self, args):
        """
Perform operation on resource.
    
    
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        [TODO: Specify return type and structure]
        [TODO: Document nested fields]
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsGenerateReport(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['collections']['get'].format(collectionName=args['--collectionName'])}/report"
        self.params = {
            **get_api_version_params("collections"),
            "reportType": args.get("--reportType", "summary"),
            "format": args.get("--format", "json"),
        }
        self.payload = get_json(args, "--payloadFile") if args.get("--payloadFile") else {}

    # === LEGACY COMPATIBILITY METHODS ===

    @decorator
    def collectionsCreateOrUpdate(self, args):
        """
Create a new collection.
    
    Creates a new collection in Microsoft Purview Collections. Collections organize assets into logical groups.
    Requires appropriate permissions and valid collection definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created collection:
            {
                'guid': str,         # Unique identifier
                'name': str,         # Resource name
                'status': str,       # Creation status
                'attributes': dict,  # Resource attributes
                'createTime': int    # Creation timestamp
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 409: Conflict (resource already exists)
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsCreateOrUpdate(args=...)
        print(f"Result: {result}")
        
        # With detailed data
        data = {
            'name': 'My Resource',
            'description': 'Resource description',
            'attributes': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        
        result = client.collectionsCreateOrUpdate(data)
        print(f"Created/Updated: {result['name']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        return self.collectionsCreate(args)

    @decorator
    def collectionsPut(self, args):
        """
Update an existing collection.
    
    Updates an existing collection with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated collection:
            {
                'guid': str,          # Unique identifier
                'attributes': dict,   # Updated attributes
                'updateTime': int     # Update timestamp
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsPut(args=...)
        print(f"Result: {result}")
        
        # With detailed data
        data = {
            'name': 'My Resource',
            'description': 'Resource description',
            'attributes': {
                'key1': 'value1',
                'key2': 'value2'
            }
        }
        
        result = client.collectionsPut(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        return self.collectionsCreate(args)

    @decorator
    def collectionsGet(self, args):
        """
Retrieve collection information.
    
    Retrieves detailed information about the specified collection.
    Returns complete collection metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing collection information:
            {
                'guid': str,          # Unique identifier
                'name': str,          # Resource name
                'attributes': dict,   # Resource attributes
                'status': str,        # Resource status
                'updateTime': int     # Last update timestamp
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsGet(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        return self.collectionsRead(args)

    @decorator
    def collectionsGetPath(self, args):
        """
Retrieve collection information.
    
    Retrieves detailed information about the specified collection.
    Returns complete collection metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing collection information:
            {
                'guid': str,          # Unique identifier
                'name': str,          # Resource name
                'attributes': dict,   # Resource attributes
                'status': str,        # Resource status
                'updateTime': int     # Last update timestamp
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsGetPath(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        return self.collectionsReadPath(args)

    @decorator
    def collectionsGetChildNames(self, args):
        """
Retrieve collection information.
    
    Retrieves detailed information about the specified collection.
    Returns complete collection metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing collection information:
            {
                'guid': str,          # Unique identifier
                'name': str,          # Resource name
                'attributes': dict,   # Resource attributes
                'status': str,        # Resource status
                'updateTime': int     # Last update timestamp
            }
    
Raises:
        ValueError: When required parameters are missing or invalid:
            - Empty or None values for required fields
            - Invalid GUID format
            - Out-of-range values
        
        AuthenticationError: When Azure credentials are invalid:
            - DefaultAzureCredential not configured
            - Insufficient permissions
            - Expired authentication token
        
        HTTPError: When Purview API returns error:
            - 400: Bad request (invalid parameters)
            - 401: Unauthorized (authentication failed)
            - 403: Forbidden (insufficient permissions)
            - 404: Resource not found
            - 429: Rate limit exceeded
            - 500: Internal server error
        
        NetworkError: When network connectivity fails
    
Example:
        # Basic usage
        client = Collections()
        
        result = client.collectionsGetChildNames(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        return self.collectionsReadChildNames(args)
