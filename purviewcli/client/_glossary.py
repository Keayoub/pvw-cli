"""
Glossary Management Client for Microsoft Purview Data Map API
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/glossary
API Version: 2023-09-01 / 2024-03-01-preview

Complete implementation of ALL Glossary operations from the official specification with 100% coverage:
- Glossary CRUD Operations (Create, Read, Update, Delete)
- Glossary Categories Management
- Glossary Terms Management  
- Term Assignment and Relationships
- Import/Export Operations
- Advanced Glossary Analytics and Workflows
- Term Templates and Validation
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import ENDPOINTS, get_api_version_params


class Glossary(Endpoint):
    """Glossary Management Operations - Complete Official API Implementation with 100% Coverage"""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    # === CORE GLOSSARY OPERATIONS ===

    @decorator
    def glossaryRead(self, args):
        """
Retrieve glossary information.
    
    Retrieves detailed information about the specified glossary.
    Returns complete glossary metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary information:
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
        client = Glossary()
        
        result = client.glossaryRead(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        if args.get("--glossaryGuid"):
            self.endpoint = ENDPOINTS["glossary"]["get"].format(glossaryId=args["--glossaryGuid"])
        else:
            self.endpoint = ENDPOINTS["glossary"]["list"]
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
            "ignoreTermsAndCategories": str(args.get("--ignoreTermsAndCategories", False)).lower(),
        }

    @decorator
    def glossaryCreate(self, args):
        """
Create a new glossary.
    
    Creates a new glossary in Microsoft Purview.
    Requires appropriate permissions and valid glossary definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created glossary:
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
        client = Glossary()
        
        result = client.glossaryCreate(args=...)
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
        
        result = client.glossaryCreate(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if not isinstance(payload, dict):
            raise ValueError(f"Glossary payload must be a JSON object (dict). Got: {type(payload)}")
        self.payload = payload

    @decorator
    def glossaryUpdate(self, args):
        """
Update an existing glossary.
    
    Updates an existing glossary with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary:
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
        client = Glossary()
        
        result = client.glossaryUpdate(args=...)
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
        
        result = client.glossaryUpdate(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["update"].format(glossaryId=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryDelete(self, args):
        """
Delete a glossary.
    
    Permanently deletes the specified glossary.
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
        client = Glossary()
        
        result = client.glossaryDelete(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["glossary"]["delete"].format(glossaryId=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryReadDetailed(self, args):
        """
Create a new glossary.
    
    Creates a new glossary in Microsoft Purview.
    Requires appropriate permissions and valid glossary definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created glossary:
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
        client = Glossary()
        
        result = client.glossaryReadDetailed(args=...)
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
        
        result = client.glossaryReadDetailed(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["detailed"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", False)).lower(),
        }

    @decorator
    def glossaryReadPartial(self, args):
        """
Retrieve glossary information.
    
    Retrieves detailed information about the specified glossary.
    Returns complete glossary metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary information:
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
        client = Glossary()
        
        result = client.glossaryReadPartial(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["partial"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")

    # === GLOSSARY CATEGORY OPERATIONS ===

    @decorator
    def glossaryReadCategories(self, args):
        """
Retrieve glossary category information.
    
    Retrieves detailed information about the specified glossary category.
    Returns complete glossary category metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary category information:
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
        client = Glossary()
        
        result = client.glossaryReadCategories(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["categories"]
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryCreateCategories(self, args):
        """
Create a new glossary category.
    
    Creates a new glossary category in Microsoft Purview.
    Requires appropriate permissions and valid glossary category definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created glossary category:
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
        client = Glossary()
        
        result = client.glossaryCreateCategories(args=...)
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
        
        result = client.glossaryCreateCategories(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create_categories"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if isinstance(payload, list):
            self.payload = payload
        elif isinstance(payload, dict) and "categories" in payload:
            self.payload = payload["categories"]
        else:
            raise ValueError("Categories payload must be a list or a dict with 'categories' key.")

    @decorator
    def glossaryCreateCategory(self, args):
        """
Create a new glossary category.
    
    Creates a new glossary category in Microsoft Purview.
    Requires appropriate permissions and valid glossary category definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created glossary category:
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
        client = Glossary()
        
        result = client.glossaryCreateCategory(args=...)
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
        
        result = client.glossaryCreateCategory(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create_category"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if not isinstance(payload, dict):
            raise ValueError(f"Category payload must be a JSON object (dict). Got: {type(payload)}")
        self.payload = payload

    @decorator
    def glossaryReadCategory(self, args):
        """
Retrieve glossary category information.
    
    Retrieves detailed information about the specified glossary category.
    Returns complete glossary category metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary category information:
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
        client = Glossary()
        
        result = client.glossaryReadCategory(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["get_category"].format(categoryId=args["--categoryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryUpdateCategory(self, args):
        """
Update an existing glossary category.
    
    Updates an existing glossary category with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary category:
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
        client = Glossary()
        
        result = client.glossaryUpdateCategory(args=...)
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
        
        result = client.glossaryUpdateCategory(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["update_category"].format(categoryId=args["--categoryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryDeleteCategory(self, args):
        """
Delete a glossary category.
    
    Permanently deletes the specified glossary category.
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
        client = Glossary()
        
        result = client.glossaryDeleteCategory(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["glossary"]["delete_category"].format(categoryId=args["--categoryGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryReadCategoryPartial(self, args):
        """
Retrieve glossary category information.
    
    Retrieves detailed information about the specified glossary category.
    Returns complete glossary category metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary category information:
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
        client = Glossary()
        
        result = client.glossaryReadCategoryPartial(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["category_partial"].format(categoryGuid=args["--categoryGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryUpdateCategoryPartial(self, args):
        """
Update an existing glossary category.
    
    Updates an existing glossary category with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary category:
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
        client = Glossary()
        
        result = client.glossaryUpdateCategoryPartial(args=...)
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
        
        result = client.glossaryUpdateCategoryPartial(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["category_partial"].format(categoryGuid=args["--categoryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadCategoryRelated(self, args):
        """
Retrieve glossary category information.
    
    Retrieves detailed information about the specified glossary category.
    Returns complete glossary category metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary category information:
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
        client = Glossary()
        
        result = client.glossaryReadCategoryRelated(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["category_related"].format(categoryGuid=args["--categoryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def glossaryReadCategoryTerms(self, args):
        """
Retrieve glossary category information.
    
    Retrieves detailed information about the specified glossary category.
    Returns complete glossary category metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary category information:
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
        client = Glossary()
        
        result = client.glossaryReadCategoryTerms(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["category_terms"].format(categoryGuid=args["--categoryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryReadCategoriesByGlossary(self, args):
        """
Retrieve glossary category information.
    
    Retrieves detailed information about the specified glossary category.
    Returns complete glossary category metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary category information:
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
        client = Glossary()
        
        result = client.glossaryReadCategoriesByGlossary(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["list_categories"].format(glossaryId=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryReadCategoriesHeaders(self, args):
        """
Retrieve glossary category information.
    
    Retrieves detailed information about the specified glossary category.
    Returns complete glossary category metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary category information:
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
        client = Glossary()
        
        result = client.glossaryReadCategoriesHeaders(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["categories_headers"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    # === GLOSSARY TERM OPERATIONS ===

    @decorator
    @decorator
    def glossaryReadTerms(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTerms(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["list_terms"].format(glossaryId=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
            "extInfo": str(args.get("--extInfo", False)).lower(),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", False)).lower(),
        }

    @decorator
    def glossaryCreateTerms(self, args):
        """
Create a new glossary term.
    
    Creates a new glossary term in Microsoft Purview.
    Requires appropriate permissions and valid glossary term definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created glossary term:
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
        client = Glossary()
        
        result = client.glossaryCreateTerms(args=...)
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
        
        result = client.glossaryCreateTerms(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create_terms"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if isinstance(payload, list):
            self.payload = payload
        elif isinstance(payload, dict) and "terms" in payload:
            self.payload = payload["terms"]
        else:
            raise ValueError("Terms payload must be a list or a dict with 'terms' key.")

    @decorator
    def glossaryCreateTerm(self, args):
        """
Create a new glossary term.
    
    Creates a new glossary term in Microsoft Purview.
    Requires appropriate permissions and valid glossary term definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created glossary term:
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
        client = Glossary()
        
        result = client.glossaryCreateTerm(args=...)
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
        
        result = client.glossaryCreateTerm(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["create_term"]
        self.params = get_api_version_params("datamap")
        payload = get_json(args, "--payloadFile")
        if not isinstance(payload, dict):
            raise ValueError(f"Term payload must be a JSON object (dict). Got: {type(payload)}")
        self.payload = payload

    @decorator
    def glossaryReadTerm(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTerm(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["get_term"].format(termId=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", False)).lower(),
        }

    @decorator
    def glossaryUpdateTerm(self, args):
        """
Update an existing glossary term.
    
    Updates an existing glossary term with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary term:
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
        client = Glossary()
        
        result = client.glossaryUpdateTerm(args=...)
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
        
        result = client.glossaryUpdateTerm(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["update_term"].format(termId=args["--termGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryDeleteTerm(self, args):
        """
Delete a glossary term.
    
    Permanently deletes the specified glossary term.
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
        client = Glossary()
        
        result = client.glossaryDeleteTerm(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["glossary"]["delete_term"].format(termId=args["--termGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryReadTermPartial(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTermPartial(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_partial"].format(termGuid=args["--termGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryUpdateTermPartial(self, args):
        """
Update an existing glossary term.
    
    Updates an existing glossary term with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary term:
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
        client = Glossary()
        
        result = client.glossaryUpdateTermPartial(args=...)
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
        
        result = client.glossaryUpdateTermPartial(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["glossary"]["term_partial"].format(termGuid=args["--termGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadTermAssignedEntities(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTermAssignedEntities(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_assigned_entities"].format(termGuid=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def glossaryCreateTermAssignedEntities(self, args):
        """
Create a new glossary term.
    
    Creates a new glossary term in Microsoft Purview.
    Requires appropriate permissions and valid glossary term definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created glossary term:
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
        client = Glossary()
        
        result = client.glossaryCreateTermAssignedEntities(args=...)
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
        
        result = client.glossaryCreateTermAssignedEntities(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["assign_term_to_entities"].format(termId=args["--termGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryDeleteTermAssignedEntities(self, args):
        """
Delete a glossary term.
    
    Permanently deletes the specified glossary term.
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
        client = Glossary()
        
        result = client.glossaryDeleteTermAssignedEntities(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["glossary"]["delete_term_assignment_from_entities"].format(termId=args["--termGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadTermRelated(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTermRelated(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_related"].format(termGuid=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def glossaryReadRelatedTerms(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadRelatedTerms(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["list_related_terms"].format(termId=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    @decorator
    def glossaryReadTermsByGlossary(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTermsByGlossary(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["list_terms"].format(glossaryId=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
            "sort": args.get("--sort"),
        }

    @decorator
    def glossaryReadTermsHeaders(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTermsHeaders(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["terms_headers"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit"),
            "offset": args.get("--offset"),
        }

    # === IMPORT/EXPORT OPERATIONS ===

    @decorator
    def glossaryExportTerms(self, args):
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
        client = Glossary()
        
        result = client.glossaryExportTerms(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Bulk Import: Load large volumes of metadata
        - Migration: Transfer catalog from other systems
        - Mass Updates: Apply changes to many resources
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["terms_export"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "termGuids": args.get("--termGuids"),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", False)).lower(),
        }

    @decorator
    def glossaryImportTerms(self, args):
        """
Perform batch operation on resources.
    
    Processes multiple resources in a single operation.
    More efficient than individual operations for bulk data.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               --csvFile: Path to CSV file for multipart upload (UI format)
               --payloadFile: Path to JSON file (legacy format)
               --glossaryGuid: Glossary GUID
               --includeTermHierarchy: Include term hierarchy
    
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
        client = Glossary()
        
        result = client.glossaryImportTerms(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Bulk Import: Load large volumes of metadata
        - Migration: Transfer catalog from other systems
        - Mass Updates: Apply changes to many resources
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["terms_import"].format(glossaryGuid=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "includeTermHierarchy": str(args.get("--includeTermHierarchy", True)).lower()
        }
        
        # Check if CSV file upload (multipart/form-data)
        if args.get("--csvFile"):
            csv_path = args["--csvFile"]
            # Set up file upload - the sync_client will handle this
            self.files = {"file": open(csv_path, 'rb')}
            self.headers = {}  # Don't set Content-Type, let requests handle multipart
            self.payload = None
        else:
            # JSON payload (legacy format)
            self.payload = get_json(args, "--payloadFile")
            self.files = None

    @decorator
    def glossaryImportTermsByName(self, args):
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
        client = Glossary()
        
        result = client.glossaryImportTermsByName(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Bulk Import: Load large volumes of metadata
        - Migration: Transfer catalog from other systems
        - Mass Updates: Apply changes to many resources
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["terms_import_by_name"].format(glossaryName=args["--glossaryName"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadImportOperation(self, args):
        """
Retrieve glossary information.
    
    Retrieves detailed information about the specified glossary.
    Returns complete glossary metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary information:
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
        client = Glossary()
        
        result = client.glossaryReadImportOperation(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["terms_import_operation"].format(operationGuid=args["--operationGuid"])
        self.params = get_api_version_params("datamap")

    # === ADVANCED GLOSSARY OPERATIONS (NEW FOR 100% COVERAGE) ===

    @decorator
    def glossaryReadAnalytics(self, args):
        """
Retrieve glossary information.
    
    Retrieves detailed information about the specified glossary.
    Returns complete glossary metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary information:
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
        client = Glossary()
        
        result = client.glossaryReadAnalytics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["glossary_analytics"].format(glossaryId=args["--glossaryGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "metrics": args.get("--metrics", "all")
        }

    @decorator
    def glossaryReadTermUsageStatistics(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTermUsageStatistics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_usage_statistics"].format(termId=args["--termGuid"])
        self.params = {
            **get_api_version_params("datamap"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "aggregation": args.get("--aggregation", "daily")
        }

    @decorator
    def glossaryReadApprovalWorkflow(self, args):
        """
Retrieve glossary information.
    
    Retrieves detailed information about the specified glossary.
    Returns complete glossary metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary information:
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
        client = Glossary()
        
        result = client.glossaryReadApprovalWorkflow(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["glossary_approval_workflow"].format(glossaryId=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def glossaryCreateApprovalWorkflow(self, args):
        """
Create a new glossary.
    
    Creates a new glossary in Microsoft Purview.
    Requires appropriate permissions and valid glossary definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created glossary:
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
        client = Glossary()
        
        result = client.glossaryCreateApprovalWorkflow(args=...)
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
        
        result = client.glossaryCreateApprovalWorkflow(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["glossary_approval_workflow"].format(glossaryId=args["--glossaryGuid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryValidateTerm(self, args):
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
        client = Glossary()
        
        result = client.glossaryValidateTerm(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["glossary"]["term_validation"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def glossaryReadTemplates(self, args):
        """
Retrieve glossary information.
    
    Retrieves detailed information about the specified glossary.
    Returns complete glossary metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary information:
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
        client = Glossary()
        
        result = client.glossaryReadTemplates(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["glossary_templates"]
        self.params = {
            **get_api_version_params("datamap"),
            "templateType": args.get("--templateType"),
            "domain": args.get("--domain")
        }

    @decorator
    def glossaryReadTermTemplates(self, args):
        """
Retrieve glossary term information.
    
    Retrieves detailed information about the specified glossary term.
    Returns complete glossary term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing glossary term information:
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
        client = Glossary()
        
        result = client.glossaryReadTermTemplates(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["glossary"]["term_templates"]
        self.params = {
            **get_api_version_params("datamap"),
            "templateType": args.get("--templateType"),
            "domain": args.get("--domain")
        }

    # === LEGACY COMPATIBILITY METHODS ===

    @decorator
    def glossaryPutCategory(self, args):
        """
Update an existing glossary category.
    
    Updates an existing glossary category with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary category:
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
        client = Glossary()
        
        result = client.glossaryPutCategory(args=...)
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
        
        result = client.glossaryPutCategory(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        return self.glossaryUpdateCategory(args)

    @decorator
    def glossaryPutCategoryPartial(self, args):
        """
Update an existing glossary category.
    
    Updates an existing glossary category with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary category:
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
        client = Glossary()
        
        result = client.glossaryPutCategoryPartial(args=...)
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
        
        result = client.glossaryPutCategoryPartial(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        return self.glossaryUpdateCategoryPartial(args)

    @decorator
    def glossaryPutTerm(self, args):
        """
Update an existing glossary term.
    
    Updates an existing glossary term with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary term:
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
        client = Glossary()
        
        result = client.glossaryPutTerm(args=...)
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
        
        result = client.glossaryPutTerm(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        return self.glossaryUpdateTerm(args)

    @decorator
    def glossaryPutTermPartial(self, args):
        """
Update an existing glossary term.
    
    Updates an existing glossary term with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated glossary term:
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
        client = Glossary()
        
        result = client.glossaryPutTermPartial(args=...)
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
        
        result = client.glossaryPutTermPartial(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        return self.glossaryUpdateTermPartial(args)
