"""
Health API Client for Microsoft Purview Unified Catalog
Provides governance health monitoring and recommendations
"""

from .endpoint import Endpoint, decorator, no_api_call_decorator


class Health(Endpoint):
    """Health API operations for governance monitoring.
    
    API Version: 2024-02-01-preview
    Base Path: /datagovernance/health
    """

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "datagovernance"

    # ========================================
    # HEALTH ACTIONS
    # ========================================

    @decorator
    def query_health_actions(self, args):
        """
Search for health metrics.
    
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
        client = Health()
        
        result = client.query_health_actions(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "POST"
        self.endpoint = "/datagovernance/health/actions/query"
        self.params = {"api-version": "2024-02-01-preview"}
        
        # Build filter payload
        payload = {}
        
        domain_id = args.get("--domain-id", [""])[0]
        if domain_id:
            payload["domainId"] = domain_id
        
        severity = args.get("--severity", [""])[0]
        if severity:
            payload["severity"] = severity
        
        status = args.get("--status", [""])[0]
        if status:
            payload["status"] = status
        
        finding_type = args.get("--finding-type", [""])[0]
        if finding_type:
            payload["findingType"] = finding_type
        
        target_type = args.get("--target-entity-type", [""])[0]
        if target_type:
            payload["targetEntityType"] = target_type
        
        self.payload = payload

    @decorator
    def get_health_action(self, args):
        """
Retrieve health metric information.
    
    Retrieves detailed information about the specified health metric.
    Returns complete health metric metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing health metric information:
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
        client = Health()
        
        result = client.get_health_action(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        action_id = args.get("--action-id", [""])[0]
        
        self.method = "GET"
        self.endpoint = f"/datagovernance/health/actions/{action_id}"
        self.params = {"api-version": "2024-02-01-preview"}

    @decorator
    def update_health_action(self, args):
        """
Update an existing health metric.
    
    Updates an existing health metric with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated health metric:
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
        client = Health()
        
        result = client.update_health_action(args=...)
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
        
        result = client.update_health_action(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        action_id = args.get("--action-id", [""])[0]
        
        self.method = "PUT"
        self.endpoint = f"/datagovernance/health/actions/{action_id}"
        self.params = {"api-version": "2024-02-01-preview"}
        
        payload = {}
        
        status = args.get("--status", [""])[0]
        if status:
            payload["status"] = status
        
        assigned_to = args.get("--assigned-to", [""])[0]
        if assigned_to:
            payload["assignedTo"] = [assigned_to] if assigned_to else []
        
        reason = args.get("--reason", [""])[0]
        if reason:
            payload["reason"] = reason
        
        self.payload = payload

    @decorator
    def delete_health_action(self, args):
        """
Delete a health metric.
    
    Permanently deletes the specified health metric.
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
        client = Health()
        
        result = client.delete_health_action(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        action_id = args.get("--action-id", [""])[0]
        
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/health/actions/{action_id}"
        self.params = {"api-version": "2024-02-01-preview"}

    # ========================================
    # STATISTICS & SUMMARIES
    # ========================================

    @decorator
    def get_health_summary(self, args):
        """
Retrieve health metric information.
    
    Retrieves detailed information about the specified health metric.
    Returns complete health metric metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing health metric information:
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
        client = Health()
        
        result = client.get_health_summary(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        domain_id = args.get("--domain-id", [""])[0]
        
        self.method = "GET"
        self.endpoint = "/datagovernance/health/summary"
        self.params = {
            "api-version": "2024-02-01-preview",
            "domainId": domain_id
        }

    # ========================================
    # UTILITY METHODS
    # ========================================

    @no_api_call_decorator
    def help(self, args):
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
        client = Health()
        
        result = client.help(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        help_text = """
Microsoft Purview Health API Client

OVERVIEW:
The Health API provides automated governance monitoring and recommendations.
It identifies gaps in metadata, governance policies, and data quality.

OPERATIONS:
- query_health_actions: List all health findings with filters
- get_health_action: Get details of a specific finding
- update_health_action: Update status or assignment
- delete_health_action: Delete a finding
- get_health_summary: Get health statistics for a domain

HEALTH FINDING TYPES:
- Estate Curation: Critical data identification, classification
- Access and Use: Terms of use, compliant data use
- Discoverability: Data cataloging, term assignment
- Trusted Data: Data quality enablement
- Value Creation: Business OKRs alignment
- Metadata Quality Management: Description quality, completeness

SEVERITY LEVELS:
- High: Critical governance gaps
- Medium: Important improvements needed
- Low: Nice-to-have enhancements

STATUS VALUES:
- NotStarted: No action taken
- InProgress: Being addressed
- Resolved: Completed
- Dismissed: Acknowledged but not acting

FILTERS:
--domain-id: Filter by governance domain
--severity: High, Medium, Low
--status: NotStarted, InProgress, Resolved, Dismissed
--finding-type: Estate Curation, Access and Use, etc.
--target-entity-type: BusinessDomain, DataProduct, Term, etc.

EXAMPLES:
# List all health actions
pvcli health query

# List high severity issues
pvcli health query --severity High

# List actions for a specific domain
pvcli health query --domain-id xxx

# Get details of a specific action
pvcli health show --action-id xxx

# Mark action as in progress
pvcli health update --action-id xxx --status InProgress

# Assign action to a user
pvcli health update --action-id xxx --assigned-to user@domain.com

API VERSION: 2024-02-01-preview
"""
        return {"message": help_text}
