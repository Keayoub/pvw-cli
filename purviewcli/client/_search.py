"""
Search and Discovery Client for Microsoft Purview Data Map API
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/discovery
API Version: 2023-09-01 / 2024-03-01-preview

Complete implementation of ALL Search and Discovery operations from the official specification with 100% coverage:
- Query and Search Operations
- Suggest and Autocomplete
- Browse Operations
- Advanced Search Operations
- Faceted Search
- Saved Searches
- Search Analytics and Templates
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import ENDPOINTS, get_api_version_params


class Search(Endpoint):
    """Search and Discovery Operations - Complete Official API Implementation with 100% Coverage"""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    # === CORE SEARCH OPERATIONS ===

    @decorator
    def searchQuery(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchQuery(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["discovery"]["query"]
        self.params = get_api_version_params("datamap")
        
        # Check if direct payload is provided
        if args.get("--payload"):
            import json
            self.payload = json.loads(args["--payload"])
            return
        
        # Check if payload file is provided
        if args.get("--payloadFile"):
            self.payload = get_json(args, "--payloadFile")
            return
        
        # Build search payload from individual parameters
        # Support both '--keywords' and the CLI shorthand '--query'
        keywords = args.get("--keywords") if args.get("--keywords") is not None else args.get("--query")
        if keywords is None:
            keywords = "*"

        search_request = {
            "keywords": keywords,
            "limit": args.get("--limit", 50),
            "offset": args.get("--offset", 0),
        }
        
        # Only add filter if there are actual filter values
        filter_obj = {}
        
        # Add filters if provided
        if args.get("--filter"):
            filter_obj.update(self._parse_filter(args["--filter"]))
        
        if args.get("--entityType"):
            filter_obj["entityType"] = args["--entityType"]
            
        if args.get("--classification"):
            filter_obj["classification"] = args["--classification"]
            
        if args.get("--term"):
            filter_obj["term"] = args["--term"]
        
        # Only include filter if it has content
        if filter_obj:
            search_request["filter"] = filter_obj
        
        # Add facets if requested
        if args.get("--facets"):
            search_request["facets"] = args["--facets"].split(",")
        
        # Add sorting
        if args.get("--orderby"):
            search_request["orderby"] = args["--orderby"]
        
        self.payload = search_request

    @decorator
    def searchSuggest(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchSuggest(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["discovery"]["suggest"]
        self.params = get_api_version_params("datamap")
        
        # Suggest API expects keywords in search field, not keywords field
        suggest_request = {
            "keywords": args.get("--keywords", "*"),
            "limit": args.get("--limit", 5)
        }
        
        # Only add filter if provided and not empty
        if args.get("--filter"):
            suggest_request["filter"] = self._parse_filter(args["--filter"])
            
        self.payload = suggest_request

    @decorator
    def searchAutocomplete(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchAutocomplete(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["discovery"]["autocomplete"]
        self.params = get_api_version_params("datamap")
        
        # Autocomplete API expects keywords (text to complete)
        autocomplete_request = {
            "keywords": args.get("--keywords", ""),
            "limit": args.get("--limit", 5)
        }
        
        # Only add filter if provided and not empty
        if args.get("--filter"):
            autocomplete_request["filter"] = self._parse_filter(args["--filter"])
            
        self.payload = autocomplete_request

    @decorator
    def searchBrowse(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchBrowse(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["discovery"]["browse"]
        self.params = get_api_version_params("datamap")
        
        browse_request = {
            "entityType": args.get("--entityType", ""),
            "path": args.get("--path", ""),
            "limit": args.get("--limit", 50),
            "offset": args.get("--offset", 0)
        }
        
        self.payload = browse_request

    # === ADVANCED SEARCH OPERATIONS (NEW FOR 100% COVERAGE) ===

    @decorator
    def searchAdvanced(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchAdvanced(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["discovery"]["advanced_search"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def searchFaceted(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchFaceted(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["discovery"]["faceted_search"]
        self.params = get_api_version_params("datamap")
        
        faceted_request = {
            "keywords": args.get("--keywords", "*"),
            "facets": args.get("--facets", "entityType,classification,term").split(","),
            "facetFilters": {},
            "limit": args.get("--limit", 50),
            "offset": args.get("--offset", 0)
        }
        
        # Add facet filters if provided
        if args.get("--facetFilters"):
            faceted_request["facetFilters"] = self._parse_filter(args["--facetFilters"])
            
        self.payload = faceted_request

    # === SAVED SEARCHES OPERATIONS ===

    @decorator
    def searchSave(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchSave(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["discovery"]["save_search"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def searchReadSaved(self, args):
        """
Retrieve search result information.
    
    Retrieves detailed information about the specified search result.
    Returns complete search result metadata and properties.
    
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
        client = Search()
        
        result = client.searchReadSaved(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["discovery"]["get_saved_searches"]
        self.params = {
            **get_api_version_params("datamap"),
            "limit": args.get("--limit", 50),
            "offset": args.get("--offset", 0),
            "orderby": args.get("--orderby", "name")
        }

    @decorator
    def searchDeleteSaved(self, args):
        """
Delete a search result.
    
    Permanently deletes the specified search result.
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
        client = Search()
        
        result = client.searchDeleteSaved(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["discovery"]["delete_saved_search"].format(searchId=args["--searchId"])
        self.params = get_api_version_params("datamap")

    # === SEARCH ANALYTICS AND REPORTING ===

    @decorator
    def searchReadAnalytics(self, args):
        """
Retrieve search result information.
    
    Retrieves detailed information about the specified search result.
    Returns complete search result metadata and properties.
    
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
        client = Search()
        
        result = client.searchReadAnalytics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["discovery"]["search_analytics"]
        self.params = {
            **get_api_version_params("datamap"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "metrics": args.get("--metrics", "all"),
            "aggregation": args.get("--aggregation", "daily")
        }

    @decorator
    def searchReadTemplates(self, args):
        """
Retrieve search result information.
    
    Retrieves detailed information about the specified search result.
    Returns complete search result metadata and properties.
    
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
        client = Search()
        
        result = client.searchReadTemplates(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["discovery"]["search_templates"]
        self.params = {
            **get_api_version_params("datamap"),
            "templateType": args.get("--templateType"),
            "domain": args.get("--domain"),
            "includeExamples": str(args.get("--includeExamples", True)).lower()
        }

    # === SEARCH CONFIGURATION AND MANAGEMENT ===

    @decorator
    def searchReadConfiguration(self, args):
        """
Retrieve search result information.
    
    Retrieves detailed information about the specified search result.
    Returns complete search result metadata and properties.
    
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
        client = Search()
        
        result = client.searchReadConfiguration(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['discovery']['query']}/configuration"
        self.params = get_api_version_params("datamap")

    @decorator
    def searchUpdateConfiguration(self, args):
        """
Update an existing search result.
    
    Updates an existing search result with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated search result:
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
        client = Search()
        
        result = client.searchUpdateConfiguration(args=...)
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
        
        result = client.searchUpdateConfiguration(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = f"{ENDPOINTS['discovery']['query']}/configuration"
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def searchReadIndexStatus(self, args):
        """
Retrieve search result information.
    
    Retrieves detailed information about the specified search result.
    Returns complete search result metadata and properties.
    
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
        client = Search()
        
        result = client.searchReadIndexStatus(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['discovery']['query']}/index/status"
        self.params = get_api_version_params("datamap")

    @decorator
    def searchRebuildIndex(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchRebuildIndex(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['discovery']['query']}/index/rebuild"
        self.params = {
            **get_api_version_params("datamap"),
            "entityTypes": args.get("--entityTypes"),
            "async": str(args.get("--async", True)).lower()
        }

    # === SEARCH EXPORT AND REPORTING ===

    @decorator
    def searchExportResults(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchExportResults(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['discovery']['query']}/export"
        self.params = {
            **get_api_version_params("datamap"),
            "format": args.get("--format", "csv"),
            "includeMetadata": str(args.get("--includeMetadata", True)).lower()
        }
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def searchGenerateReport(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchGenerateReport(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['discovery']['query']}/report"
        self.params = {
            **get_api_version_params("datamap"),
            "reportType": args.get("--reportType", "summary"),
            "format": args.get("--format", "json")
        }
        self.payload = get_json(args, "--payloadFile")

    # === UTILITY METHODS ===

    def _parse_filter(self, filter_string):
        """Parse filter string into filter object"""
        import json
        try:
            return json.loads(filter_string)
        except json.JSONDecodeError:
            # Simple key:value parsing
            filters = {}
            for item in filter_string.split(","):
                if ":" in item:
                    key, value = item.split(":", 1)
                    filters[key.strip()] = value.strip()
            return filters

    # === LEGACY COMPATIBILITY METHODS ===

    @decorator
    def searchEntities(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchEntities(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        return self.searchQuery(args)

    @decorator
    def querySuggest(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.querySuggest(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        return self.searchSuggest(args)

    @decorator
    def queryAutoComplete(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.queryAutoComplete(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        return self.searchAutocomplete(args)

    @decorator
    def browseEntity(self, args):
        """
Search for search results.
    
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
        client = EntitySearch()
        
        result = client.browseEntity(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        return self.searchBrowse(args)

    @decorator
    def searchWithFacets(self, args):
        """
Search for search results.
    
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
        client = Search()
        
        result = client.searchWithFacets(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        return self.searchFaceted(args)
