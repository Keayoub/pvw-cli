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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        List of resource dictionaries, each containing:
            - guid (str): Unique identifier
            - name (str): Resource name
            - attributes (dict): Resource attributes
            - status (str): Resource status
        
        Returns empty list if no resources found.
    
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
        client = Management()
        
        result = client.managementListOperations(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = ENDPOINTS['management']['operations']
        self.params = get_api_version_params('account')

    # ========== Account Management ==========
    
    @decorator
    def managementCheckNameAvailability(self, args):
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
        client = Management()
        
        result = client.managementCheckNameAvailability(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementReadAccounts(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementReadAccount(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
    
    @decorator
    def managementCreateAccount(self, args):
        """
Create a new management resource.
    
    Creates a new management resource in Microsoft Purview.
    Requires appropriate permissions and valid management resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created management resource:
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
        client = Management()
        
        result = client.managementCreateAccount(args=...)
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
        
        result = client.managementCreateAccount(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = 'PUT'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def managementUpdateAccount(self, args):
        """
Update an existing management resource.
    
    Updates an existing management resource with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated management resource:
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
        client = Management()
        
        result = client.managementUpdateAccount(args=...)
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
        
        result = client.managementUpdateAccount(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = 'PATCH'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def managementDeleteAccount(self, args):
        """
Delete a management resource.
    
    Permanently deletes the specified management resource.
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
        client = Management()
        
        result = client.managementDeleteAccount(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = 'DELETE'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    # ========== Account Keys Management ==========
    
    @decorator
    def managementGetAccessKeys(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetAccessKeys(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['management']['access_keys'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementRegenerateAccessKey(self, args):
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
        client = Management()
        
        result = client.managementRegenerateAccessKey(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        List of resource dictionaries, each containing:
            - guid (str): Unique identifier
            - name (str): Resource name
            - attributes (dict): Resource attributes
            - status (str): Resource status
        
        Returns empty list if no resources found.
    
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
        client = Management()
        
        result = client.managementListPrivateLinkResources(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_link_resources'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementGetPrivateLinkResource(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetPrivateLinkResource(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        List of resource dictionaries, each containing:
            - guid (str): Unique identifier
            - name (str): Resource name
            - attributes (dict): Resource attributes
            - status (str): Resource status
        
        Returns empty list if no resources found.
    
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
        client = Management()
        
        result = client.managementListPrivateEndpointConnections(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_endpoint_connections'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementGetPrivateEndpointConnection(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetPrivateEndpointConnection(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['private_endpoint_connection'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"],
                                      privateEndpointConnectionName=args["--privateEndpointConnectionName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementCreateOrUpdatePrivateEndpointConnection(self, args):
        """
Create a new management resource.
    
    Creates a new management resource in Microsoft Purview.
    Requires appropriate permissions and valid management resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created management resource:
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
        client = Management()
        
        result = client.managementCreateOrUpdatePrivateEndpointConnection(args=...)
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
        
        result = client.managementCreateOrUpdatePrivateEndpointConnection(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
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
        """
Delete a management resource.
    
    Permanently deletes the specified management resource.
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
        client = Management()
        
        result = client.managementDeletePrivateEndpointConnection(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetAccountFeatures(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_features'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementUpdateAccountFeatures(self, args):
        """
Update an existing management resource.
    
    Updates an existing management resource with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated management resource:
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
        client = Management()
        
        result = client.managementUpdateAccountFeatures(args=...)
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
        
        result = client.managementUpdateAccountFeatures(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetIngestionStatus(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['ingestion_status'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementListResourceSets(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        List of resource dictionaries, each containing:
            - guid (str): Unique identifier
            - name (str): Resource name
            - attributes (dict): Resource attributes
            - status (str): Resource status
        
        Returns empty list if no resources found.
    
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
        client = Management()
        
        result = client.managementListResourceSets(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['resource_sets'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    # ========== Account Security and Compliance ==========
    
    @decorator
    def managementGetSecuritySettings(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetSecuritySettings(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['security_settings'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementUpdateSecuritySettings(self, args):
        """
Update an existing management resource.
    
    Updates an existing management resource with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated management resource:
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
        client = Management()
        
        result = client.managementUpdateSecuritySettings(args=...)
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
        
        result = client.managementUpdateSecuritySettings(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetDiagnosticSettings(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['diagnostic_settings'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementCreateOrUpdateDiagnosticSettings(self, args):
        """
Create a new management resource.
    
    Creates a new management resource in Microsoft Purview.
    Requires appropriate permissions and valid management resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created management resource:
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
        client = Management()
        
        result = client.managementCreateOrUpdateDiagnosticSettings(args=...)
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
        
        result = client.managementCreateOrUpdateDiagnosticSettings(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
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
        """
Update an existing management resource.
    
    Updates an existing management resource with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated management resource:
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
        client = Management()
        
        result = client.managementDeleteDiagnosticSetting(args=...)
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
        
        result = client.managementDeleteDiagnosticSetting(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetAccountUsage(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_usage'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementGetAccountMetrics(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetAccountMetrics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetAccountTags(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_tags'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementUpdateAccountTags(self, args):
        """
Update an existing management resource.
    
    Updates an existing management resource with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated management resource:
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
        client = Management()
        
        result = client.managementUpdateAccountTags(args=...)
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
        
        result = client.managementUpdateAccountTags(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
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
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        List of resource dictionaries, each containing:
            - guid (str): Unique identifier
            - name (str): Resource name
            - attributes (dict): Resource attributes
            - status (str): Resource status
        
        Returns empty list if no resources found.
    
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
        client = Management()
        
        result = client.managementListAccountsBySubscription(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['accounts'], 
                                      subscriptionId=args["--subscriptionId"])
        self.params = get_api_version_params('account')

    @decorator
    def managementGetSubscriptionUsage(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetSubscriptionUsage(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['subscription_usage'], 
                                      subscriptionId=args["--subscriptionId"])
        self.params = get_api_version_params('account')

    # ========== Advanced Management Operations ==========
    
    @decorator
    def managementGetAccountStatus(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetAccountStatus(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_status'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')

    @decorator
    def managementValidateAccountConfiguration(self, args):
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
        client = Management()
        
        result = client.managementValidateAccountConfiguration(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        self.method = 'POST'
        self.endpoint = format_endpoint(ENDPOINTS['management']['validate_configuration'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def managementGetAccountHealth(self, args):
        """
Retrieve management resource information.
    
    Retrieves detailed information about the specified management resource.
    Returns complete management resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing management resource information:
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
        client = Management()
        
        result = client.managementGetAccountHealth(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = 'GET'
        self.endpoint = format_endpoint(ENDPOINTS['management']['account_health'], 
                                      subscriptionId=args["--subscriptionId"],
                                      resourceGroupName=args["--resourceGroupName"],
                                      accountName=args["--accountName"])
        self.params = get_api_version_params('account')
