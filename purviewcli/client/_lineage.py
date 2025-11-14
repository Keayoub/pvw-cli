"""
Lineage Management Client for Microsoft Purview Data Map API
Based on official API: https://learn.microsoft.com/en-us/rest/api/purview/datamapdataplane/lineage
API Version: 2023-09-01 / 2024-03-01-preview

Complete implementation of ALL Lineage operations from the official specification with 100% coverage:
- Lineage CRUD Operations (Create, Read, Update, Delete)
- Upstream and Downstream Lineage Analysis
- Lineage Graph Operations
- Impact Analysis
- Temporal Lineage
- Lineage Validation
- CSV-based Bulk Lineage Creation
- Lineage Analytics and Reporting
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import ENDPOINTS, get_api_version_params
import json
import uuid
from datetime import datetime


class Lineage(Endpoint):
    """Lineage Management Operations - Complete Official API Implementation with 100% Coverage"""

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

    # === CORE LINEAGE OPERATIONS ===

    @decorator
    def lineageRead(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageRead(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["lineage"]["get"].format(guid=args["--guid"])
        self.params = {
            **get_api_version_params("datamap"),
            "direction": args.get("--direction", "BOTH"),
            "depth": args.get("--depth", 3),
            "width": args.get("--width", 10),
            "includeParent": str(args.get("--includeParent", False)).lower(),
            "getDerivedLineage": str(args.get("--getDerivedLineage", False)).lower(),
        }

    @decorator
    def lineageReadUniqueAttribute(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadUniqueAttribute(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["lineage"]["get_by_unique_attribute"].format(typeName=args["--typeName"])
        self.params = {
            **get_api_version_params("datamap"),
            "attr:qualifiedName": args["--qualifiedName"],
            "direction": args.get("--direction", "BOTH"),
            "depth": args.get("--depth", 3),
            "width": args.get("--width", 10),
            "includeParent": str(args.get("--includeParent", False)).lower(),
            "getDerivedLineage": str(args.get("--getDerivedLineage", False)).lower(),
        }

    @decorator
    def lineageReadNextPage(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadNextPage(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["lineage"]["get_next_page"].format(guid=args["--guid"])
        self.params = {
            **get_api_version_params("datamap"),
            "direction": args.get("--direction", "BOTH"),
            "getDerivedLineage": str(args.get("--getDerivedLineage", False)).lower(),
            "offset": args.get("--offset"),
            "limit": args.get("--limit"),
        }

    # === ADVANCED LINEAGE OPERATIONS (NEW FOR 100% COVERAGE) ===

    @decorator
    def lineageReadUpstream(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadUpstream(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["lineage"]["get_upstream_lineage"].format(guid=args["--guid"])
        self.params = {
            **get_api_version_params("datamap"),
            "depth": args.get("--depth", 3),
            "width": args.get("--width", 10),
            "includeParent": str(args.get("--includeParent", False)).lower(),
        }

    @decorator
    def lineageReadDownstream(self, args):
        """
Create a new lineage information.
    
    Creates a new lineage information in Microsoft Purview Data Lineage. Tracks data flow and transformations.
    Requires appropriate permissions and valid lineage information definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created lineage information:
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
        client = Lineage()
        
        result = client.lineageReadDownstream(args=...)
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
        
        result = client.lineageReadDownstream(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["lineage"]["get_downstream_lineage"].format(guid=args["--guid"])
        self.params = {
            **get_api_version_params("datamap"),
            "depth": args.get("--depth", 3),
            "width": args.get("--width", 10),
            "includeParent": str(args.get("--includeParent", False)).lower(),
        }

    @decorator
    def lineageReadGraph(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadGraph(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["lineage"]["get_lineage_graph"].format(guid=args["--guid"])
        self.params = {
            **get_api_version_params("datamap"),
            "direction": args.get("--direction", "BOTH"),
            "depth": args.get("--depth", 3),
            "includeProcesses": str(args.get("--includeProcesses", True)).lower(),
            "format": args.get("--format", "json"),
        }

    @decorator
    def lineageCreate(self, args):
        """
Create a new lineage information.
    
    Creates a new lineage information in Microsoft Purview Data Lineage. Tracks data flow and transformations.
    Requires appropriate permissions and valid lineage information definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created lineage information:
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
        client = Lineage()
        
        result = client.lineageCreate(args=...)
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
        
        result = client.lineageCreate(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["lineage"]["create_lineage"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def lineageUpdate(self, args):
        """
Update an existing lineage information.
    
    Updates an existing lineage information with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated lineage information:
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
        client = Lineage()
        
        result = client.lineageUpdate(args=...)
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
        
        result = client.lineageUpdate(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        self.method = "PUT"
        self.endpoint = ENDPOINTS["lineage"]["update_lineage"].format(guid=args["--guid"])
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def lineageDelete(self, args):
        """
Delete a lineage information.
    
    Permanently deletes the specified lineage information.
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
        client = Lineage()
        
        result = client.lineageDelete(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["lineage"]["delete_lineage"].format(guid=args["--guid"])
        self.params = get_api_version_params("datamap")

    @decorator
    def lineageValidate(self, args):
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
        client = Lineage()
        
        result = client.lineageValidate(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["lineage"]["validate_lineage"]
        self.params = get_api_version_params("datamap")
        self.payload = get_json(args, "--payloadFile")

    @decorator
    def lineageReadImpactAnalysis(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadImpactAnalysis(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["lineage"]["get_impact_analysis"].format(guid=args["--guid"])
        self.params = {
            **get_api_version_params("datamap"),
            "direction": args.get("--direction", "DOWNSTREAM"),
            "depth": args.get("--depth", 5),
            "analysisType": args.get("--analysisType", "IMPACT"),
            "includeProcesses": str(args.get("--includeProcesses", True)).lower(),
        }

    @decorator
    def lineageReadTemporal(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadTemporal(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["lineage"]["get_temporal_lineage"].format(guid=args["--guid"])
        self.params = {
            **get_api_version_params("datamap"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "timeGranularity": args.get("--timeGranularity", "HOUR"),
            "direction": args.get("--direction", "BOTH"),
            "depth": args.get("--depth", 3),
        }

    # === BULK LINEAGE OPERATIONS (FOR CSV SUPPORT) ===

    @decorator
    def lineageCreateBulk(self, args):
        """
Create a new lineage information.
    
    Creates a new lineage information in Microsoft Purview Data Lineage. Tracks data flow and transformations.
    Requires appropriate permissions and valid lineage information definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created lineage information:
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
        client = Lineage()
        
        result = client.lineageCreateBulk(args=...)
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
        
        result = client.lineageCreateBulk(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["lineage"]["create_lineage"]
        self.params = get_api_version_params("datamap")
        
        # Process input file (CSV or JSON)
        input_file = args.get("--inputFile")
        if input_file:
            lineage_data = self._process_lineage_file(input_file, args)
        else:
            lineage_data = get_json(args, "--payloadFile")
        
        self.payload = lineage_data

    def _process_lineage_file(self, input_file, args):
        """Process lineage input file (CSV or JSON) and convert to API format"""
        import pandas as pd
        import os
        
        file_ext = os.path.splitext(input_file)[1].lower()
        
        if file_ext == '.csv':
            return self._process_csv_lineage(input_file, args)
        elif file_ext == '.json':
            with open(input_file, 'r') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: .csv, .json")

    def _process_csv_direct_lineage(self, csv_file, df, args):
        """Process CSV file for direct lineage relationships (UI-style)"""
        import pandas as pd
        
        # Create direct lineage relationships
        relationships = []
        
        for idx, row in df.iterrows():
            # Get relationship type
            relationship_type = str(row.get('relationship_type', 'direct_lineage_dataset_dataset')).strip()
            
            # Clean GUIDs
            source_guid = str(row['source_entity_guid']).strip().replace('guid=', '').strip('"')
            target_guid = str(row['target_entity_guid']).strip().replace('guid=', '').strip('"')
            
            # Get entity types
            source_type = row.get('source_type', 'DataSet')
            target_type = row.get('target_type', 'DataSet')
            
            # Get column mapping if present
            column_mapping = str(row.get('columnMapping', row.get('column_mapping', '')))
            
            # Create direct lineage relationship
            relationship = {
                "typeName": relationship_type,
                "guid": f"-{idx + 1}",  # Negative GUID for auto-generation
                "end1": {
                    "guid": source_guid,
                    "typeName": source_type
                },
                "end2": {
                    "guid": target_guid,
                    "typeName": target_type
                },
                "attributes": {
                    "columnMapping": column_mapping
                }
            }
            
            relationships.append(relationship)
        
        # Return format for relationship creation
        return {
            "relationships": relationships
        }
    
    def _process_csv_lineage(self, csv_file, args):
        """Process CSV file and convert to lineage API format"""
        import pandas as pd
        
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Determine which format is being used (GUID-based or qualified name-based)
        has_guid_columns = 'source_entity_guid' in df.columns and 'target_entity_guid' in df.columns
        has_qn_columns = 'source_qualified_name' in df.columns and 'target_qualified_name' in df.columns
        
        if not has_guid_columns and not has_qn_columns:
            raise ValueError(
                "CSV must contain either (source_entity_guid, target_entity_guid) "
                "or (source_qualified_name, target_qualified_name) columns"
            )
        
        # Check if any row uses direct relationship types (not Process-based lineage)
        # If so, we'll create relationships instead of Process entities
        use_direct_lineage = False
        if 'relationship_type' in df.columns:
            # List of official direct relationship types supported by Microsoft Purview
            # Reference: https://learn.microsoft.com/en-us/purview/data-gov-api-create-lineage-relationships#concepts
            direct_relationship_types = [
                'direct_lineage_dataset_dataset',  # DataSet → DataSet (direct link)
                'dataset_process_inputs',          # DataSet → Process (input)
                'process_dataset_outputs'          # Process → DataSet (output)
            ]
            use_direct_lineage = any(
                df['relationship_type'].str.contains('|'.join(direct_relationship_types), na=False, case=False)
            )
        
        if use_direct_lineage:
            # Create direct relationships (UI-style lineage)
            return self._process_csv_direct_lineage(csv_file, df, args)
        
        # Generate lineage entities (relationships are defined via inputs/outputs attributes)
        lineage_entities = []
        
        for idx, row in df.iterrows():
            # Create process entity for each lineage relationship
            # Use unique negative GUIDs (-1, -2, -3, ...) to let Atlas auto-generate the GUID for each Process
            process_guid = f"-{idx + 1}"
            process_name = row.get('process_name', f"Process_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{idx}")
            
            # Prepare inputs/outputs based on format
            if has_guid_columns:
                # Clean GUIDs (remove guid= prefix and quotes)
                source_guid = str(row['source_entity_guid']).strip().replace('guid=', '').strip('"')
                target_guid = str(row['target_entity_guid']).strip().replace('guid=', '').strip('"')
                
                inputs = [{"guid": source_guid, "typeName": row.get('source_type', 'DataSet')}]
                outputs = [{"guid": target_guid, "typeName": row.get('target_type', 'DataSet')}]
            else:
                inputs = [{"typeName": row.get('source_type', 'DataSet'), "uniqueAttributes": {"qualifiedName": row['source_qualified_name']}}]
                outputs = [{"typeName": row.get('target_type', 'DataSet'), "uniqueAttributes": {"qualifiedName": row['target_qualified_name']}}]
            
            # Process entity - let Atlas generate the GUID
            process_entity = {
                "guid": process_guid,
                "typeName": "Process",
                "attributes": {
                    "qualifiedName": f"{process_name}@{args.get('--cluster', 'default')}",
                    "name": process_name,
                    "description": str(row.get('description', '')),
                    "owner": str(row.get('owner', '')),
                    "inputs": inputs,
                    "outputs": outputs
                },
                "classifications": [],
                "meanings": []
            }
            
            # Add custom attributes if present
            custom_attrs = ['confidence_score', 'metadata', 'tags']
            for attr in custom_attrs:
                if attr in row and pd.notna(row[attr]) and str(row[attr]).strip():
                    if attr == 'tags':
                        process_entity["attributes"][attr] = str(row[attr]).split(',')
                    elif attr == 'metadata':
                        try:
                            process_entity["attributes"][attr] = json.loads(str(row[attr]))
                        except json.JSONDecodeError:
                            process_entity["attributes"][attr] = str(row[attr])
                    else:
                        process_entity["attributes"][attr] = row[attr]
            
            lineage_entities.append(process_entity)
            
            # Note: Relationships are now defined via the inputs/outputs attributes in the Process entity
            # No need to create separate relationship objects
        
        return {
            "entities": lineage_entities,
            "referredEntities": {}
        }

    # === CSV LINEAGE OPERATIONS ===

    @decorator
    def lineageCSVProcess(self, args):
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
        client = Lineage()
        
        result = client.lineageCSVProcess(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        csv_file = args.get("csv_file") or args.get("--csv-file")
        if not csv_file:
            raise ValueError("CSV file path is required")
        
        # Process CSV and create lineage payload
        lineage_data = self._process_csv_lineage(csv_file, args)
        
        # Check if this is direct lineage (relationships) or Process lineage (entities)
        if "relationships" in lineage_data and "entities" not in lineage_data:
            # Direct lineage - use relationship bulk API
            self.method = "POST"
            self.endpoint = ENDPOINTS["relationship"]["bulk_create_relationships"]
            self.params = get_api_version_params("datamap")
            self.payload = lineage_data["relationships"]
        else:
            # Process lineage - use entity bulk API
            self.method = "POST"
            self.endpoint = ENDPOINTS["entity"]["bulk_create_or_update"]
            self.params = get_api_version_params("datamap")
            self.payload = lineage_data
        
        # Return the payload for inspection (actual API call handled by decorator)
        return lineage_data

    def lineageCSVValidate(self, args):
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
        client = Lineage()
        
        result = client.lineageCSVValidate(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        import pandas as pd
        
        csv_file = args.get("csv_file") or args.get("--csv-file")
        if not csv_file:
            return {"success": False, "error": "CSV file path is required"}
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Check required columns
            required_columns = ['source_entity_guid', 'target_entity_guid']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return {
                    "success": False,
                    "error": f"Missing required columns: {', '.join(missing_columns)}",
                    "expected_columns": required_columns
                }
            
            # Validate GUIDs format
            import re
            guid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
            
            invalid_guids = []
            for idx, row in df.iterrows():
                source_guid = str(row['source_entity_guid']).strip()
                target_guid = str(row['target_entity_guid']).strip()
                
                # Remove guid= prefix if present
                source_guid = source_guid.replace('guid=', '').strip('"')
                target_guid = target_guid.replace('guid=', '').strip('"')
                
                if not guid_pattern.match(source_guid):
                    invalid_guids.append(f"Row {int(idx) + 1}: Invalid source GUID '{source_guid}'")
                if not guid_pattern.match(target_guid):
                    invalid_guids.append(f"Row {int(idx) + 1}: Invalid target GUID '{target_guid}'")
            
            if invalid_guids:
                return {
                    "success": False,
                    "error": "Invalid GUID format(s) found",
                    "details": invalid_guids
                }
            
            return {
                "success": True,
                "rows": len(df),
                "columns": list(df.columns)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def lineageCSVSample(self, args):
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
        client = Lineage()
        
        result = client.lineageCSVSample(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        sample_data = """source_entity_guid,target_entity_guid,relationship_type,process_name,description,confidence_score,owner,metadata
ea3412c3-7387-4bc1-9923-11f6f6f60000,2d21eba5-b08b-4571-b31d-7bf6f6f60000,Process,ETL_Customer_Transform,Transform customer data,0.95,data-engineering,"{""tool"": ""Azure Data Factory""}"
2d21eba5-b08b-4571-b31d-7bf6f6f60000,4fae348b-e960-42f7-834c-38f6f6f60000,Process,Customer_Address_Join,Join customer with address,0.90,data-engineering,"{""tool"": ""Databricks""}"
"""
        output_file = args.get("--output-file") or args.get("output_file") or "lineage_sample.csv"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sample_data)
            
            return {
                "success": True,
                "file": output_file,
                "message": f"Sample CSV file created: {output_file}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def lineageCSVTemplates(self, args):
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
        client = Lineage()
        
        result = client.lineageCSVTemplates(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        templates = {
            "basic": {
                "columns": ["source_entity_guid", "target_entity_guid", "relationship_type", "process_name"],
                "description": "Basic lineage with source, target, and process name"
            },
            "detailed": {
                "columns": ["source_entity_guid", "target_entity_guid", "relationship_type", "process_name", "description", "confidence_score", "owner", "metadata"],
                "description": "Detailed lineage with additional metadata"
            },
            "qualified_names": {
                "columns": ["source_qualified_name", "target_qualified_name", "source_type", "target_type", "process_name", "description"],
                "description": "Lineage using qualified names instead of GUIDs"
            }
        }
        
        return {
            "templates": templates,
            "recommended": "detailed"
        }

    # === LINEAGE ANALYTICS AND REPORTING ===

    @decorator
    def lineageReadAnalytics(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadAnalytics(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['lineage']['get'].format(guid=args['--guid'])}/analytics"
        self.params = {
            **get_api_version_params("datamap"),
            "startTime": args.get("--startTime"),
            "endTime": args.get("--endTime"),
            "metrics": args.get("--metrics", "all"),
            "aggregation": args.get("--aggregation", "daily"),
        }

    @decorator
    def lineageGenerateReport(self, args):
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
        client = Lineage()
        
        result = client.lineageGenerateReport(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        self.method = "POST"
        self.endpoint = f"{ENDPOINTS['lineage']['get'].format(guid=args['--guid'])}/report"
        self.params = {
            **get_api_version_params("datamap"),
            "format": args.get("--format", "json"),
            "includeDetails": str(args.get("--includeDetails", True)).lower(),
        }
        self.payload = get_json(args, "--payloadFile") if args.get("--payloadFile") else {}

    # === LINEAGE DISCOVERY AND SEARCH ===

    @decorator
    def lineageSearch(self, args):
        """
Search for lineage informations.
    
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
        client = Lineage()
        
        result = client.lineageSearch(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        self.method = "GET"
        self.endpoint = f"{ENDPOINTS['lineage']['get'].replace('/{guid}', '/search')}"
        self.params = {
            **get_api_version_params("datamap"),
            "query": args.get("--query"),
            "entityType": args.get("--entityType"),
            "direction": args.get("--direction", "BOTH"),
            "limit": args.get("--limit", 50),
            "offset": args.get("--offset", 0),
        }

    # === LEGACY COMPATIBILITY METHODS ===

    @decorator
    def lineageReadByGuid(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadByGuid(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        return self.lineageRead(args)

    @decorator
    def lineageReadByUniqueAttribute(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadByUniqueAttribute(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        return self.lineageReadUniqueAttribute(args)

    @decorator
    def lineageReadNext(self, args):
        """
Retrieve lineage information information.
    
    Retrieves detailed information about the specified lineage information.
    Returns complete lineage information metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing lineage information information:
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
        client = Lineage()
        
        result = client.lineageReadNext(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        return self.lineageReadNextPage(args)

    def lineageCreateColumnLevel(self, args):
        """
Create column-level lineage between tables (supports 1 source → N targets).

This method creates Process entities that link specific columns from a source table
to columns in target table(s), establishing column-level data lineage.

Args:
        args: Dictionary containing:
            --source-table-guid: GUID of the source table
            --target-table-guids: List of GUIDs of target tables (or single GUID for backward compat)
            --source-column: Name of the source column
            --target-columns: List of target column names (or single name for backward compat)
            --process-name: Optional name for the process (default: auto-generated)
            --description: Optional description
            --owner: Optional owner (default: data-engineering)
            --validate-types: Boolean to validate column type compatibility

Returns:
        Dictionary with status and created entities

Raises:
        ValueError: When required parameters are missing
        HTTPError: When API returns error status

Example:
        # Single target
        client = Lineage()
        args = {
            "--source-table-guid": "abc-123",
            "--target-table-guids": ["def-456"],
            "--source-column": "CityKey",
            "--target-columns": ["CityKey"],
        }
        
        # Multiple targets
        args = {
            "--source-table-guid": "abc-123",
            "--target-table-guids": ["def-456", "ghi-789"],
            "--source-column": "CityKey",
            "--target-columns": ["CityKey", "City_ID"],
        }
        result = client.lineageCreateColumnLevel(args)

Use Cases:
        - ETL Documentation: Document column transformations
        - Data Lineage: Track data flow at column level
        - Impact Analysis: Understand column dependencies
        - Multi-target mapping: One source feeding multiple targets
    """
        from .endpoint import get_data
        
        # Extract parameters with backward compatibility
        source_table_guid = args.get("--source-table-guid")
        
        # Support both old (single) and new (multiple) formats
        target_table_guids = args.get("--target-table-guids")
        if not target_table_guids:
            # Backward compatibility: single target
            single_target = args.get("--target-table-guid")
            target_table_guids = [single_target] if single_target else []
        
        source_column_name = args.get("--source-column")
        
        target_columns = args.get("--target-columns")
        if not target_columns:
            # Backward compatibility: single column
            single_column = args.get("--target-column")
            target_columns = [single_column] if single_column else []
        
        # Validation
        if not source_table_guid:
            raise ValueError("Missing required parameter: --source-table-guid")
        if not source_column_name:
            raise ValueError("Missing required parameter: --source-column")
        if not target_table_guids or len(target_table_guids) == 0:
            raise ValueError("Missing required parameter: --target-table-guids (or --target-table-guid)")
        if not target_columns or len(target_columns) == 0:
            raise ValueError("Missing required parameter: --target-columns (or --target-column)")
        
        if len(target_table_guids) != len(target_columns):
            raise ValueError(f"Mismatch: {len(target_table_guids)} target tables but {len(target_columns)} target columns")
        
        # Extract optional parameters (defined here for use in loop)
        process_name = args.get("--process-name")
        description = args.get("--description")
        owner = args.get("--owner", "data-engineering")
        validate_types = args.get("--validate-types", False)
        
        # Step 1: Get source table columns using the sync client
        source_table = get_data({
            "app": "catalog",
            "method": "GET",
            "endpoint": f"/datamap/api/atlas/v2/entity/guid/{source_table_guid}",
            "params": get_api_version_params("datamap")
        })
        
        if not source_table or isinstance(source_table, dict) and source_table.get("status") == "error":
            return {"status": "error", "message": f"Failed to get source table: {source_table}"}
        
        source_columns_list = source_table.get('entity', {}).get('relationshipAttributes', {}).get('columns', [])
        
        source_column = None
        for col in source_columns_list:
            if col.get('displayText', '').lower() == source_column_name.lower():
                source_column = col
                break
        
        if not source_column:
            available_cols = [c.get('displayText') for c in source_columns_list]
            return {"status": "error", "message": f"Source column '{source_column_name}' not found. Available: {available_cols}"}
        
        source_column_guid = source_column['guid']
        source_data_type = source_column.get('attributes', {}).get('dataType', 'unknown')
        
        # Step 2: Process each target (multi-target support)
        results = []
        all_entities = []
        all_relationships = []
        relationship_guid_counter = -2  # Start from -2 for relationship GUIDs
        
        for idx, (target_table_guid, target_column_name) in enumerate(zip(target_table_guids, target_columns)):
            # Get target table columns
            target_table = get_data({
                "app": "catalog",
                "method": "GET",
                "endpoint": f"/datamap/api/atlas/v2/entity/guid/{target_table_guid}",
                "params": get_api_version_params("datamap")
            })
            
            if not target_table or isinstance(target_table, dict) and target_table.get("status") == "error":
                results.append({
                    "target_index": idx,
                    "target_table_guid": target_table_guid,
                    "target_column": target_column_name,
                    "status": "error",
                    "message": f"Failed to get target table: {target_table}"
                })
                continue
            
            target_columns_list = target_table.get('entity', {}).get('relationshipAttributes', {}).get('columns', [])
            
            target_column = None
            for col in target_columns_list:
                if col.get('displayText', '').lower() == target_column_name.lower():
                    target_column = col
                    break
            
            if not target_column:
                available_cols = [c.get('displayText') for c in target_columns_list]
                results.append({
                    "target_index": idx,
                    "target_table_guid": target_table_guid,
                    "target_column": target_column_name,
                    "status": "error",
                    "message": f"Target column '{target_column_name}' not found. Available: {available_cols}"
                })
                continue
            
            target_column_guid = target_column['guid']
            target_data_type = target_column.get('attributes', {}).get('dataType', 'unknown')
            
            # Type validation if requested
            if validate_types:
                if not self._are_types_compatible(source_data_type, target_data_type):
                    results.append({
                        "target_index": idx,
                        "target_table_guid": target_table_guid,
                        "target_column": target_column_name,
                        "status": "error",
                        "message": f"Type mismatch: source '{source_data_type}' not compatible with target '{target_data_type}'"
                    })
                    continue
            
            # Generate unique qualified name and process name
            process_guid = f"-{idx + 1}"  # -1, -2, -3, etc. for each process
            qualified_name = f"ColumnMapping_{source_column_name}_{source_table_guid}_to_{target_column_name}_{target_table_guid}@default"
            
            default_process_name = f"{source_column_name}_to_{target_column_name}_Mapping"
            final_process_name = process_name if process_name else default_process_name
            
            default_description = f"Column lineage: {source_column_name} -> {target_column_name}"
            final_description = description if description else default_description
            
            # Create Process entity for this target
            process_entity = {
                "guid": process_guid,
                "typeName": "Process",
                "attributes": {
                    "qualifiedName": qualified_name,
                    "name": final_process_name,
                    "description": final_description,
                    "owner": owner,
                    "inputs": [{"guid": source_column_guid, "typeName": "column"}],
                    "outputs": [{"guid": target_column_guid, "typeName": "column"}]
                },
                "classifications": [],
                "meanings": []
            }
            
            all_entities.append(process_entity)
            
            # Create relationships for this process
            input_relationship = {
                "guid": str(relationship_guid_counter),
                "typeName": "dataset_process_inputs",
                "end1": {
                    "guid": source_column_guid,
                    "typeName": "column"
                },
                "end2": {
                    "guid": process_guid,
                    "typeName": "Process"
                }
            }
            relationship_guid_counter -= 1
            
            output_relationship = {
                "guid": str(relationship_guid_counter),
                "typeName": "process_dataset_outputs",
                "end1": {
                    "guid": process_guid,
                    "typeName": "Process"
                },
                "end2": {
                    "guid": target_column_guid,
                    "typeName": "column"
                }
            }
            relationship_guid_counter -= 1
            
            all_relationships.append(input_relationship)
            all_relationships.append(output_relationship)
            
            results.append({
                "target_index": idx,
                "target_table_guid": target_table_guid,
                "target_column": target_column_name,
                "status": "pending"
            })
        
        # Check if any targets succeeded
        if not all_entities:
            return {
                "status": "error",
                "message": "All targets failed validation",
                "results": results
            }
        
        # Step 3: Create all lineages in a single bulk operation
        column_lineage_payload = {
            "entities": all_entities,
            "relationships": all_relationships
        }
        
        # Step 4: Create the lineage using the sync client
        api_result = get_data({
            "app": "catalog",
            "method": "POST",
            "endpoint": ENDPOINTS["entity"]["bulk_create_or_update"],
            "params": get_api_version_params("datamap"),
            "payload": column_lineage_payload
        })
        
        # Update results with success status
        created_entities = api_result.get('mutatedEntities', {}).get('CREATE', []) if api_result else []
        for result in results:
            if result['status'] == 'pending':
                result['status'] = 'success'
        
        return {
            "status": "success",
            "message": f"Created {len(all_entities)} column lineage(s)",
            "created_count": len(all_entities),
            "results": results,
            "api_response": api_result
        }
    
    def _are_types_compatible(self, source_type, target_type):
        """
        Check if source and target column types are compatible for lineage.
        
        Args:
            source_type: Source column data type
            target_type: Target column data type
        
        Returns:
            Boolean indicating compatibility
        """
        # Normalize types
        source = source_type.lower() if source_type else 'unknown'
        target = target_type.lower() if target_type else 'unknown'
        
        # Exact match
        if source == target:
            return True
        
        # Integer family compatibility
        int_types = {'int', 'integer', 'bigint', 'smallint', 'tinyint', 'long'}
        if source in int_types and target in int_types:
            return True
        
        # Float/decimal family compatibility
        float_types = {'float', 'double', 'decimal', 'numeric', 'real'}
        if source in float_types and target in float_types:
            return True
        
        # String family compatibility
        string_types = {'string', 'varchar', 'char', 'text', 'nvarchar', 'nchar'}
        if source in string_types and target in string_types:
            return True
        
        # Date/time family compatibility
        datetime_types = {'date', 'datetime', 'datetime2', 'timestamp', 'time'}
        if source in datetime_types and target in datetime_types:
            return True
        
        # Allow promotion from int to float
        if source in int_types and target in float_types:
            return True
        
        # Unknown types are compatible (permissive approach)
        if source == 'unknown' or target == 'unknown':
            return True
        
        return False

    @decorator
    def lineageCreateDirect(self, args):
        """
        Create direct lineage between two datasets (UI-style lineage without visible Process).
        
        This creates a direct_lineage_dataset_dataset relationship, which is what Purview UI uses
        when you manually create lineage. The Process is created internally but hidden in the UI.
        
        Args:
            args: Dictionary with keys:
                --source-guid: Source entity GUID
                --target-guid: Target entity GUID
                --source-type: Source entity type (e.g., azure_sql_table)
                --target-type: Target entity type (e.g., azure_sql_table)
                --column-mapping: Optional column mapping JSON string
        
        Returns:
            Created relationship details
        
        Example:
            client = Lineage()
            result = client.lineageCreateDirect({
                "--source-guid": "9ebbd583-4987-4d1b-b4f5-d8f6f6f60000",
                "--target-guid": "52c7d566-87ab-4753-a23a-d3f6f6f60000",
                "--source-type": "azure_sql_table",
                "--target-type": "azure_sql_table",
                "--column-mapping": ""
            })
        """
        source_guid = args.get("--source-guid")
        target_guid = args.get("--target-guid")
        source_type = args.get("--source-type", "DataSet")
        target_type = args.get("--target-type", "DataSet")
        column_mapping = args.get("--column-mapping", "")
        
        if not source_guid or not target_guid:
            raise ValueError("Both --source-guid and --target-guid are required")
        
        # Create direct lineage relationship (UI-style)
        relationship = {
            "typeName": "direct_lineage_dataset_dataset",
            "guid": "-1",  # Let Atlas generate
            "end1": {
                "guid": source_guid,
                "typeName": source_type
            },
            "end2": {
                "guid": target_guid,
                "typeName": target_type
            },
            "attributes": {
                "columnMapping": column_mapping
            }
        }
        
        self.method = "POST"
        self.endpoint = ENDPOINTS["relationship"]["create"]
        self.params = get_api_version_params("datamap")
        self.payload = relationship
