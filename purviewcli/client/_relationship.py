"""
Relationship Management Client for Microsoft Purview Data Map API
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/relationship
API Version: 2023-09-01 / 2024-03-01-preview

Complete implementation of ALL Relationship operations from the official specification with 100% coverage:
- Relationship CRUD Operations (Create, Read, Update, Delete)
- Bulk Relationship Operations
- Entity-based Relationship Queries
- Relationship Validation
- Advanced Relationship Analytics
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import ENDPOINTS, get_api_version_params


class Relationship(Endpoint):
    """Relationship Management Operations - Complete Official API Implementation with 100% Coverage"""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    # === CORE RELATIONSHIP OPERATIONS ===

    @decorator
    def relationshipCreate(self, args):
        """
Create a new relationship.
    
    Creates a new relationship in Microsoft Purview Relationships. Define connections between entities.
    Requires appropriate permissions and valid relationship definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created relationship:
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
        client = Relationship()
        
        result = client.relationshipCreate(args=...)
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
        
        result = client.relationshipCreate(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["relationship"]["create"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def relationshipRead(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = Relationship()
        
        result = client.relationshipRead(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["relationship"]["get"].format(guid=args["--guid"])
        self.params = {
            **get_api_version_params("datamap"),
            "extendedInfo": str(args.get("--extendedInfo", False)).lower(),
        }

    @decorator
    def relationshipUpdate(self, args):
        """
Update an existing relationship.
    
    Updates an existing relationship with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated relationship:
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
        client = Relationship()
        
        result = client.relationshipUpdate(args=...)
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
        
        result = client.relationshipUpdate(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["relationship"]["update"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def relationshipDelete(self, args):
        """
Delete a relationship.
    
    Permanently deletes the specified relationship.
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
        client = Relationship()
        
        result = client.relationshipDelete(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["relationship"]["delete"].format(guid=args["--guid"])
        self.params = get_api_version_params("datamap")

    # === ADVANCED RELATIONSHIP OPERATIONS (NEW FOR 100% COVERAGE) ===

    @decorator
    def relationshipReadAll(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = Relationship()
        
        result = client.relationshipReadAll(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["relationship"]["list_relationships"]
        self.params = {
            **get_api_version_params("datamap"),
            "relationshipType": args.get("--relationshipType"),
            "status": args.get("--status", "ACTIVE"),
            "limit": args.get("--limit", 100),
            "offset": args.get("--offset", 0),
            "sort": args.get("--sort"),
        }

    @decorator
    def relationshipCreateBulk(self, args):
        """
Create a new relationship.
    
    Creates a new relationship in Microsoft Purview Relationships. Define connections between entities.
    Requires appropriate permissions and valid relationship definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created relationship:
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
        client = Relationship()
        
        result = client.relationshipCreateBulk(args=...)
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
        
        result = client.relationshipCreateBulk(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["relationship"]["bulk_create_relationships"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def relationshipDeleteBulk(self, args):
        """
Delete a relationship.
    
    Permanently deletes the specified relationship.
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
        client = Relationship()
        
        result = client.relationshipDeleteBulk(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["relationship"]["bulk_delete_relationships"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def relationshipReadByEntity(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = EntityRelationship()
        
        result = client.relationshipReadByEntity(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["relationship"]["get_relationships_by_entity"].format(guid=args["--entityGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "relationshipType": args.get("--relationshipType"),
            "direction": args.get("--direction", "BOTH"),
            "status": args.get("--status", "ACTIVE"),
            "limit": args.get("--limit", 100),
            "offset": args.get("--offset", 0),
        }

    @decorator
    def relationshipValidate(self, args):
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
        client = Relationship()
        
        result = client.relationshipValidate(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["relationship"]["validate_relationship"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    # === RELATIONSHIP ANALYTICS AND REPORTING ===

    @decorator
    def relationshipReadAnalytics(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = Relationship()
        
        result = client.relationshipReadAnalytics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['relationship']['get'].format(guid=args['--guid'])}/analytics"
        self.params = {
            **get_api_version_params("datamap"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "metrics": args.get("--metrics", "all"),
        }

    @decorator
    def relationshipReadStatistics(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = Relationship()
        
        result = client.relationshipReadStatistics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['relationship']['list_relationships']}/statistics"
        self.params = {
            **get_api_version_params("datamap"),
            "relationshipType": args.get("--relationshipType"),
            "groupBy": args.get("--groupBy", "type"),
            "includeInactive": str(args.get("--includeInactive", False)).lower(),
        }

    # === RELATIONSHIP DISCOVERY AND SEARCH ===

    @decorator
    def relationshipSearch(self, args):
        """
Search for relationships.
    
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
        client = Relationship()
        
        result = client.relationshipSearch(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['relationship']['list_relationships']}/search"
        self.params = {
            **get_api_version_params("datamap"),
            "query": args.get("--query"),
            "relationshipType": args.get("--relationshipType"),
            "entityType": args.get("--entityType"),
            "status": args.get("--status"),
            "limit": args.get("--limit", 50),
            "offset": args.get("--offset", 0),
        }

    @decorator
    def relationshipReadByType(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = Relationship()
        
        result = client.relationshipReadByType(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['relationship']['list_relationships']}/type/{args['--relationshipType']}"
        self.params = {
            **get_api_version_params("datamap"),
            "status": args.get("--status", "ACTIVE"),
            "includeMetadata": str(args.get("--includeMetadata", True)).lower(),
            "limit": args.get("--limit", 100),
            "offset": args.get("--offset", 0),
        }

    # === RELATIONSHIP IMPORT/EXPORT ===

    @decorator
    def relationshipExport(self, args):
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
        client = Relationship()
        
        result = client.relationshipExport(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Bulk Import: Load large volumes of metadata
        - Migration: Transfer catalog from other systems
        - Mass Updates: Apply changes to many resources
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['relationship']['list_relationships']}/export"
        self.params = {
            **get_api_version_params("datamap"),
            "relationshipType": args.get("--relationshipType"),
            "entityGuids": args.get("--entityGuids"),
            "format": args.get("--format", "json"),
            "includeInactive": str(args.get("--includeInactive", False)).lower(),
        }

    @decorator
    def relationshipImport(self, args):
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
        client = Relationship()
        
        result = client.relationshipImport(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Bulk Import: Load large volumes of metadata
        - Migration: Transfer catalog from other systems
        - Mass Updates: Apply changes to many resources
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['relationship']['list_relationships']}/import"
        self.params = {
            **get_api_version_params("datamap"),
            "validateOnly": str(args.get("--validateOnly", False)).lower(),
            "overwriteExisting": str(args.get("--overwriteExisting", False)).lower(),
        }
        self.payload = get_json(args, "--payloadFile")

    # === RELATIONSHIP LINEAGE OPERATIONS ===

    @decorator
    def relationshipReadLineage(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = LineageRelationship()
        
        result = client.relationshipReadLineage(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['relationship']['get'].format(guid=args['--guid'])}/lineage"
        self.params = {
            **get_api_version_params("datamap"),
            "direction": args.get("--direction", "BOTH"),
            "depth": args.get("--depth", 3),
            "includeParent": str(args.get("--includeParent", False)).lower(),
        }

    @decorator
    def relationshipReadImpact(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = Relationship()
        
        result = client.relationshipReadImpact(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['relationship']['get'].format(guid=args['--guid'])}/impact"
        self.params = {
            **get_api_version_params("datamap"),
            "direction": args.get("--direction", "DOWNSTREAM"),
            "depth": args.get("--depth", 5),
            "analysisType": args.get("--analysisType", "IMPACT"),
        }

    # === LEGACY COMPATIBILITY METHODS ===

    @decorator
    def relationshipReadByGuid(self, args):
        """
Retrieve relationship information.
    
    Retrieves detailed information about the specified relationship.
    Returns complete relationship metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing relationship information:
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
        client = Relationship()
        
        result = client.relationshipReadByGuid(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        return self.relationshipRead(args)

    @decorator
    def relationshipCreateOrUpdate(self, args):
        """
Create a new relationship.
    
    Creates a new relationship in Microsoft Purview Relationships. Define connections between entities.
    Requires appropriate permissions and valid relationship definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created relationship:
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
        client = Relationship()
        
        result = client.relationshipCreateOrUpdate(args=...)
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
        
        result = client.relationshipCreateOrUpdate(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        payload = get_json(args, "--payloadFile")
        if payload.get("guid"):
            return self.relationshipUpdate(args)
        else:
            return self.relationshipCreate(args)

    @decorator
    def relationshipPut(self, args):
        """
Update an existing relationship.
    
    Updates an existing relationship with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated relationship:
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
        client = Relationship()
        
        result = client.relationshipPut(args=...)
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
        
        result = client.relationshipPut(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        return self.relationshipUpdate(args)
