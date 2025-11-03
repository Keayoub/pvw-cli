"""
Microsoft Purview Unified Catalog API Client
Implements comprehensive Unified Catalog functionality
"""

from .endpoint import Endpoint, decorator, get_json, no_api_call_decorator
from .endpoints import ENDPOINTS, get_api_version_params
import os
import json


class UnifiedCatalogClient(Endpoint):
    """Client for Microsoft Purview Unified Catalog API."""

    def __init__(self):
        """Initialize the Unified Catalog client."""
        Endpoint.__init__(self)
        self.app = "datagovernance"  # Use datagovernance app for UC endpoints

    # ========================================
    # GOVERNANCE DOMAINS
    # ========================================
    @decorator
    def get_governance_domains(self, args):
        """
        Get all governance domains in the Unified Catalog.
        
        Retrieves a list of all governance domains that organize business data assets
        into logical business units. Domains represent organizational structures like
        departments, business functions, or data products.
        
        Args:
            args: Dictionary of operation arguments (currently no filters supported).
                  Future versions may support status, type, or name filters.
        
        Returns:
            List of governance domain dictionaries, each containing:
                - id (str): Unique domain identifier (GUID)
                - name (str): Domain name (e.g., "Sales", "Marketing")
                - description (str): Domain description and purpose
                - type (str): Domain type ("BusinessUnit", "FunctionalUnit", "DataProduct")
                - status (str): Domain status ("Draft", "Active", "Deprecated")
                - parentId (str): Parent domain ID for hierarchical domains
                - createdBy (str): Creator user ID
                - createdAt (str): Creation timestamp (ISO 8601)
                - updatedBy (str): Last modifier user ID
                - updatedAt (str): Last update timestamp (ISO 8601)
            
            Returns empty list if no domains exist.
        
        Raises:
            AuthenticationError: When Azure credentials are invalid or expired
            
            HTTPError: When Purview API returns error:
                - 401: Unauthorized (authentication failed)
                - 403: Forbidden (requires Data Curator role)
                - 429: Rate limit exceeded
                - 500: Purview internal server error
            
            NetworkError: When network connectivity fails
        
        Example:
            # List all governance domains
            client = UnifiedCatalogClient()
            args = {}
            domains = client.get_governance_domains(args)
            
            print(f"Found {len(domains)} domains")
            for domain in domains:
                print(f"  - {domain['name']} ({domain['type']}): {domain['status']}")
                if domain.get('parentId'):
                    print(f"    Parent: {domain['parentId']}")
            
            # Find active business units
            active_business_units = [
                d for d in domains 
                if d['type'] == 'BusinessUnit' and d['status'] == 'Active'
            ]
            print(f"Active business units: {len(active_business_units)}")
        
        Use Cases:
            - Domain Discovery: Browse organizational structure in catalog
            - Hierarchy Visualization: Build domain tree for navigation
            - Governance Reporting: List all domains for compliance reports
            - Domain Selection: Show domains in UI dropdowns for term assignment
            - Impact Analysis: Identify which domains contain specific data
        """
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_domains"]
        self.params = {}

    @decorator
    def get_governance_domain_by_id(self, args):
        """
        Get a specific governance domain by its ID.
        
        Retrieves detailed information about a single governance domain including
        its metadata, hierarchical relationships, and associated terms/assets.
        
        Args:
            args: Dictionary containing:
                  - '--domain-id' (str): Required. Domain unique identifier (GUID).
                                        Format: UUID (e.g., 'abcd1234-...')
        
        Returns:
            Dictionary with complete domain information:
                {
                    'id': str,               # Domain unique identifier
                    'name': str,             # Domain name
                    'description': str,      # Domain description
                    'type': str,             # "BusinessUnit", "FunctionalUnit", "DataProduct"
                    'status': str,           # "Draft", "Active", "Deprecated"
                    'parentId': str,         # Parent domain ID (None if root)
                    'parentName': str,       # Parent domain name (if applicable)
                    'childDomains': [        # Child domains (if any)
                        {
                            'id': str,
                            'name': str,
                            'type': str
                        }
                    ],
                    'termCount': int,        # Number of terms in this domain
                    'assetCount': int,       # Number of assets tagged with domain terms
                    'owners': [              # Domain owners/stewards
                        {
                            'id': str,       # Entra Object ID (GUID)
                            'name': str,     # Display name
                            'email': str     # Email address
                        }
                    ],
                    'createdBy': str,        # Creator user ID
                    'createdAt': str,        # Creation timestamp (ISO 8601)
                    'updatedBy': str,        # Last modifier
                    'updatedAt': str         # Last update timestamp
                }
        
        Raises:
            ValueError: When domain-id is missing or invalid GUID format
            
            AuthenticationError: When Azure credentials invalid
            
            HTTPError: When Purview API returns error:
                - 400: Invalid domain ID format
                - 401: Unauthorized
                - 403: Forbidden (insufficient permissions)
                - 404: Domain not found
                - 429: Rate limit exceeded
                - 500: Internal server error
        
        Example:
            # Get domain details
            client = UnifiedCatalogClient()
            args = {'--domain-id': ['abcd1234-5678-90ab-cdef-1234567890ab']}
            domain = client.get_governance_domain_by_id(args)
            
            print(f"Domain: {domain['name']}")
            print(f"Type: {domain['type']}, Status: {domain['status']}")
            print(f"Terms: {domain['termCount']}, Assets: {domain['assetCount']}")
            
            # Show hierarchy
            if domain.get('parentName'):
                print(f"Parent: {domain['parentName']}")
            if domain.get('childDomains'):
                print(f"Children: {[c['name'] for c in domain['childDomains']]}")
            
            # Show owners
            print(f"Owners: {[o['name'] for o in domain.get('owners', [])]}")
        
        Use Cases:
            - Domain Details View: Display domain information in UI
            - Hierarchy Navigation: Show parent/child relationships
            - Access Control: Check domain owners before operations
            - Metrics Dashboard: Display domain term/asset counts
            - Validation: Verify domain exists before creating terms
        """
        domain_id = args.get("--domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_domain"].format(domainId=domain_id)
        self.params = {}

    @decorator
    def create_governance_domain(self, args):
        """
        Create a new governance domain in the Unified Catalog.
        
        Creates a governance domain to organize business terms, policies, and data assets
        into logical business units. Domains can be hierarchical (parent/child) to represent
        organizational structure.
        
        Args:
            args: Dictionary containing either:
                  Option 1 - Via payload file:
                  - '--payloadFile' (str): Path to JSON file with domain definition
                  
                  Option 2 - Via CLI arguments:
                  - '--name' (str): Required. Domain name (e.g., "Sales", "Marketing")
                  - '--description' (str): Optional. Domain purpose and scope
                  - '--type' (str): Optional. Domain type. Valid values:
                                   - "BusinessUnit" (default) - Department or division
                                   - "FunctionalUnit" - Cross-cutting function (IT, Legal)
                                   - "DataProduct" - Data product domain
                  - '--status' (str): Optional. Initial status. Valid values:
                                     - "Draft" (default) - Under development
                                     - "Active" - Published and in use
                  - '--parent-domain-id' (str): Optional. Parent domain GUID for hierarchy
                  
                  Domain payload structure (JSON):
                  {
                      "name": str,            # Required: Unique domain name
                      "description": str,     # Recommended: Purpose description
                      "type": str,            # Optional: See types above (default: "BusinessUnit")
                      "status": str,          # Optional: "Draft" or "Active" (default: "Draft")
                      "parentId": str,        # Optional: Parent domain GUID for sub-domains
                      "owners": [             # Optional: Domain stewards/owners
                          {
                              "id": str       # Entra Object ID (GUID) - not email!
                          }
                      ]
                  }
        
        Returns:
            Dictionary containing created domain:
                {
                    'id': str,               # New domain unique identifier (GUID)
                    'name': str,             # Domain name
                    'description': str,      # Domain description
                    'type': str,             # Domain type
                    'status': str,           # Domain status
                    'parentId': str,         # Parent ID if hierarchical
                    'createdBy': str,        # Creator user ID
                    'createdAt': str         # Creation timestamp (ISO 8601)
                }
        
        Raises:
            ValueError: When required fields are missing:
                - name is empty or None
                - invalid type or status value
                - parentId format invalid
                
            AuthenticationError: When Azure credentials invalid
            
            HTTPError: When Purview API returns error:
                - 400: Invalid domain structure (missing name, invalid type)
                - 401: Unauthorized
                - 403: Forbidden (requires Data Curator role)
                - 404: Parent domain not found
                - 409: Domain name already exists
                - 429: Rate limit exceeded
                - 500: Internal server error
        
        Example:
            # Create root domain via CLI args
            client = UnifiedCatalogClient()
            args = {
                '--name': ['Sales'],
                '--description': ['Sales department data assets'],
                '--type': ['BusinessUnit'],
                '--status': ['Active']
            }
            domain = client.create_governance_domain(args)
            print(f"Created domain: {domain['id']}")
            
            # Create child domain via JSON file
            subdomain_data = {
                "name": "North America Sales",
                "description": "Sales data for North American region",
                "type": "BusinessUnit",
                "status": "Draft",
                "parentId": domain['id'],  # Use parent domain ID
                "owners": [
                    {"id": "0360aff3-add5-4b7c-b172-52add69b0199"}  # Entra Object ID
                ]
            }
            
            with open('subdomain.json', 'w') as f:
                json.dump(subdomain_data, f)
            
            args = {'--payloadFile': ['subdomain.json']}
            subdomain = client.create_governance_domain(args)
            print(f"Created subdomain: {subdomain['name']} under {domain['name']}")
        
        Use Cases:
            - Organizational Structure: Model company departments as domains
            - Data Product Setup: Create domain for new data product
            - Regional Hierarchy: Create geographic sub-domains (EMEA, APAC, Americas)
            - Functional Groups: Create cross-cutting domains (Data Quality, Privacy)
            - Migration: Programmatically create domains from existing systems
        
        See Also:
            - update_governance_domain: Modify existing domain
            - delete_governance_domain: Remove domain
            - get_governance_domains: List all domains
        """
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_domains"]
        # Allow payload file to fully control creation; otherwise build payload from flags
        payload = get_json(args, "--payloadFile")
        if not payload:
            payload = {
                "name": args.get("--name", [""])[0],
                "description": args.get("--description", [""])[0],
                "type": args.get("--type", ["FunctionalUnit"])[0],
                "status": args.get("--status", ["Draft"])[0],
            }
            # Support parent domain ID passed via CLI as --parent-domain-id
            parent_id = args.get("--parent-domain-id", [""])[0]
            if parent_id:
                payload["parentId"] = parent_id

        # If payload file contains parentId or parentDomainId, keep it as-is
        self.payload = payload

    @decorator
    def update_governance_domain(self, args):
        """
        Update an existing governance domain.
        
        Modifies properties of a governance domain such as name, description, status,
        or type. Commonly used to activate draft domains, update descriptions, or
        change ownership.
        
        Args:
            args: Dictionary containing:
                  Required:
                  - '--domain-id' (str): Domain unique identifier (GUID)
                  
                  Update options (provide via --payloadFile or CLI args):
                  - '--payloadFile' (str): Path to JSON with updates
                  - '--name' (str): New domain name
                  - '--description' (str): New description
                  - '--type' (str): New type ("BusinessUnit", "FunctionalUnit", "DataProduct")
                  - '--status' (str): New status ("Draft", "Active", "Deprecated")
                  
                  Update payload structure:
                  {
                      "name": str,            # Optional: Update name
                      "description": str,     # Optional: Update description
                      "type": str,            # Optional: Change type
                      "status": str,          # Optional: Change status
                      "owners": [...]         # Optional: Update owners
                  }
                  
                  Note: Only include fields you want to update. Omitted fields unchanged.
        
        Returns:
            Dictionary containing updated domain:
                {
                    'id': str,               # Domain ID (unchanged)
                    'name': str,             # Updated or existing name
                    'description': str,      # Updated or existing description
                    'type': str,             # Updated or existing type
                    'status': str,           # Updated or existing status
                    'updatedBy': str,        # User who made update
                    'updatedAt': str         # Update timestamp (ISO 8601)
                }
        
        Raises:
            ValueError: When domain-id is missing or fields are invalid
            
            AuthenticationError: When Azure credentials invalid
            
            HTTPError: When Purview API returns error:
                - 400: Invalid update data
                - 401: Unauthorized
                - 403: Forbidden (not domain owner or Data Curator)
                - 404: Domain not found
                - 409: Name conflicts with existing domain
                - 429: Rate limit exceeded
                - 500: Internal server error
        
        Example:
            # Activate a draft domain
            client = UnifiedCatalogClient()
            args = {
                '--domain-id': ['abcd1234-...'],
                '--status': ['Active']
            }
            domain = client.update_governance_domain(args)
            print(f"Domain {domain['name']} is now {domain['status']}")
            
            # Update name and description via JSON
            updates = {
                "name": "Sales & Marketing",
                "description": "Combined sales and marketing data domain"
            }
            
            with open('updates.json', 'w') as f:
                json.dump(updates, f)
            
            args = {
                '--domain-id': ['abcd1234-...'],
                '--payloadFile': ['updates.json']
            }
            updated = client.update_governance_domain(args)
            print(f"Updated: {updated['name']}")
        
        Use Cases:
            - Domain Activation: Promote draft domain to active status
            - Reorganization: Rename domains during business restructuring
            - Deprecation: Mark obsolete domains as deprecated
            - Ownership Transfer: Update domain owners/stewards
            - Description Updates: Keep domain documentation current
        
        See Also:
            - create_governance_domain: Create new domain
            - delete_governance_domain: Remove domain
            - get_governance_domain_by_id: View current domain details
        """
        domain_id = args.get("--domain-id", [""])[0]
        self.method = "PUT"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_domain"].format(domainId=domain_id)
        self.payload = get_json(args, "--payloadFile") or {
            "name": args.get("--name", [""])[0],
            "description": args.get("--description", [""])[0],
            "type": args.get("--type", [""])[0],
            "status": args.get("--status", [""])[0],
        }

    @decorator
    def delete_governance_domain(self, args):
        """
        Delete a governance domain from the Unified Catalog.
        
        Permanently removes a governance domain. This operation will fail if the domain:
        - Contains active terms (must delete/move terms first)
        - Has child domains (must delete children first)
        - Is referenced by policies or workflows
        
        Use with caution - this operation cannot be undone.
        
        Args:
            args: Dictionary containing:
                  - '--domain-id' (str): Required. Domain unique identifier (GUID) to delete.
        
        Returns:
            Dictionary with deletion confirmation:
                {
                    'id': str,               # Deleted domain ID
                    'status': str,           # 'Deleted'
                    'message': str,          # Confirmation message
                    'deletedAt': str,        # Deletion timestamp (ISO 8601)
                    'deletedBy': str         # User who deleted domain
                }
        
        Raises:
            ValueError: When domain-id is missing or invalid
            
            AuthenticationError: When Azure credentials invalid
            
            HTTPError: When Purview API returns error:
                - 400: Cannot delete domain (has dependencies)
                - 401: Unauthorized
                - 403: Forbidden (not domain owner or Data Curator)
                - 404: Domain not found (already deleted)
                - 409: Conflict (domain has active terms or child domains)
                - 429: Rate limit exceeded
                - 500: Internal server error
        
        Example:
            # Delete empty domain
            client = UnifiedCatalogClient()
            args = {'--domain-id': ['abcd1234-5678-90ab-cdef-1234567890ab']}
            
            # Check domain is empty first
            domain = client.get_governance_domain_by_id(args)
            if domain['termCount'] > 0:
                print(f"Cannot delete: Domain has {domain['termCount']} terms")
            elif domain.get('childDomains'):
                print(f"Cannot delete: Domain has {len(domain['childDomains'])} children")
            else:
                result = client.delete_governance_domain(args)
                print(f"Deleted domain: {result['id']}")
            
            # Cascade delete: Remove children first, then parent
            def delete_domain_cascade(client, domain_id):
                domain = client.get_governance_domain_by_id({'--domain-id': [domain_id]})
                
                # Delete children first
                for child in domain.get('childDomains', []):
                    delete_domain_cascade(client, child['id'])
                
                # Then delete this domain
                client.delete_governance_domain({'--domain-id': [domain_id]})
                print(f"Deleted: {domain['name']}")
        
        Use Cases:
            - Cleanup: Remove test or obsolete domains
            - Reorganization: Delete old domains after restructuring
            - Decommissioning: Remove domains for discontinued business units
            - Error Correction: Delete mistakenly created domains
        
        Important Notes:
            - Cannot be undone - consider setting status to "Deprecated" instead
            - Must delete or move all terms first
            - Must delete all child domains first
            - Deletion is immediate and permanent
        
        See Also:
            - update_governance_domain: Set status to "Deprecated" instead of deleting
            - get_governance_domain_by_id: Check domain has no dependencies
        """
        domain_id = args.get("--domain-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_domain"].format(domainId=domain_id)
        self.params = {}

    # ========================================
    # DATA PRODUCTS
    # ========================================
    @decorator
    def get_data_products(self, args):
        """
Retrieve data product information.
    
    Retrieves detailed information about the specified data product.
    Returns complete data product metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing data product information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_data_products(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_data_products"]
        
        # Add optional filters
        domain_id = args.get("--governance-domain-id", [""])[0] or args.get("--domain-id", [""])[0]
        self.params = {"domainId": domain_id} if domain_id else {}
        
        if args.get("--status"):
            self.params["status"] = args["--status"][0]

    @decorator
    def get_data_product_by_id(self, args):
        """
Retrieve data product information.
    
    Retrieves detailed information about the specified data product.
    Returns complete data product metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing data product information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_data_product_by_id(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        product_id = args.get("--product-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_data_product"].format(productId=product_id)
        self.params = {}

    @decorator
    def create_data_product(self, args):
        """
Create a new data product.
    
    Creates a new data product in Microsoft Purview.
    Requires appropriate permissions and valid data product definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created data product:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_data_product(args=...)
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
        
        result = client.create_data_product(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_data_products"]
        
        # Get domain ID
        domain_id = args.get("--governance-domain-id", [""])[0] or args.get("--domain-id", [""])[0]
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        business_use = args.get("--business-use", [""])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Type mapping for data products
        dp_type = args.get("--type", ["Dataset"])[0]
        
        # Build contacts field
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id, "description": ""})
        
        payload = {
            "name": name,
            "description": description,
            "domain": domain_id,
            "type": dp_type,
            "businessUse": business_use,
            "status": status,
        }
        
        if owners:
            payload["contacts"] = {"owner": owners}
        
        # Optional fields
        if args.get("--audience"):
            payload["audience"] = args["--audience"]
        if args.get("--terms-of-use"):
            payload["termsOfUse"] = args["--terms-of-use"]
        if args.get("--documentation"):
            payload["documentation"] = args["--documentation"]
        if args.get("--update-frequency"):
            payload["updateFrequency"] = args["--update-frequency"][0]
        if args.get("--endorsed"):
            payload["endorsed"] = args["--endorsed"][0]
        
        self.payload = payload

    @decorator
    def update_data_product(self, args):
        """
Update an existing data product.
    
    Updates an existing data product with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated data product:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.update_data_product(args=...)
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
        
        result = client.update_data_product(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        product_id = args.get("--product-id", [""])[0]
        
        # First, get the current data product
        get_args = {"--product-id": [product_id]}
        current_product = self.get_data_product_by_id(get_args)
        
        if not current_product or (isinstance(current_product, dict) and current_product.get("error")):
            raise ValueError(f"Failed to retrieve data product {product_id} for update")
        
        # Start with current product as base
        payload = dict(current_product)
        
        # Update only the fields that were provided
        if args.get("--name"):
            payload["name"] = args.get("--name")[0]
        if "--description" in args:
            payload["description"] = args.get("--description")[0]
        if args.get("--domain-id") or args.get("--governance-domain-id"):
            payload["domain"] = args.get("--governance-domain-id", [""])[0] or args.get("--domain-id", [""])[0]
        if args.get("--type"):
            payload["type"] = args.get("--type")[0]
        if args.get("--status"):
            payload["status"] = args.get("--status")[0]
        if "--business-use" in args:
            payload["businessUse"] = args.get("--business-use")[0]
        if args.get("--update-frequency"):
            payload["updateFrequency"] = args.get("--update-frequency")[0]
        if args.get("--endorsed"):
            payload["endorsed"] = args.get("--endorsed")[0] == "true"
        
        # Handle owner updates
        owner_ids = args.get("--owner-id", [])
        if owner_ids:
            owners = [{"id": owner_id, "description": "Owner"} for owner_id in owner_ids]
            if "contacts" not in payload:
                payload["contacts"] = {}
            payload["contacts"]["owner"] = owners
        
        # Now perform the PUT request
        self.method = "PUT"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_data_product"].format(productId=product_id)
        self.payload = payload

    @decorator
    def delete_data_product(self, args):
        """
Delete a data product.
    
    Permanently deletes the specified data product.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_data_product(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        product_id = args.get("--product-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_data_product"].format(productId=product_id)
        self.params = {}

    @decorator
    def create_data_product_relationship(self, args):
        """
Create a new resource.
    
    Creates a new resource in Microsoft Purview Unified Catalog.
    Requires appropriate permissions and valid resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_data_product_relationship(args=...)
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
        
        result = client.create_data_product_relationship(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        product_id = args.get("--product-id", [""])[0]
        entity_type = args.get("--entity-type", [""])[0]  # e.g., "CRITICALDATACOLUMN"
        entity_id = args.get("--entity-id", [""])[0]
        asset_id = args.get("--asset-id", [""])[0] if args.get("--asset-id") else entity_id
        relationship_type = args.get("--relationship-type", ["Related"])[0]
        description = args.get("--description", [""])[0]
        
        # Build request body
        payload = {
            "relationship1": {
                "description": description,
                "relationshipType": relationship_type,
                "assetId": asset_id,
                "entityId": entity_id
            }
        }
        
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["create_data_product_relationship"].format(
            productId=product_id
        )
        self.params = {"entityType": entity_type.upper()}
        self.payload = payload

    @decorator
    def get_data_product_relationships(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_data_product_relationships(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        product_id = args.get("--product-id", [""])[0]
        entity_type = args.get("--entity-type", [""])[0] if args.get("--entity-type") else None
        
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_data_product_relationships"].format(
            productId=product_id
        )
        
        # Entity type is optional filter
        if entity_type:
            self.params = {"entityType": entity_type.upper()}
        else:
            self.params = {}

    @decorator
    def delete_data_product_relationship(self, args):
        """
Delete a resource.
    
    Permanently deletes the specified resource from Unified Catalog.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_data_product_relationship(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        product_id = args.get("--product-id", [""])[0]
        entity_type = args.get("--entity-type", [""])[0]
        entity_id = args.get("--entity-id", [""])[0]
        
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["delete_data_product_relationship"].format(
            productId=product_id
        )
        self.params = {
            "entityType": entity_type.upper(),
            "entityId": entity_id
        }

    @decorator
    def query_data_products(self, args):
        """
Search for resources.
    
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.query_data_products(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        # Build query payload from args
        payload = {}
        
        # IDs and domain filters
        if args.get("--ids"):
            payload["ids"] = args["--ids"]
        if args.get("--domain-ids"):
            payload["domainIds"] = args["--domain-ids"]
        
        # Name/keyword search
        if args.get("--name-keyword"):
            payload["nameKeyword"] = args["--name-keyword"][0]
        
        # Owner filter
        if args.get("--owners"):
            payload["owners"] = args["--owners"]
        
        # Status filters
        if args.get("--status"):
            payload["status"] = args["--status"][0]
        if args.get("--multi-status"):
            payload["multiStatus"] = args["--multi-status"]
        
        # Type filters
        if args.get("--type"):
            payload["type"] = args["--type"][0]
        if args.get("--types"):
            payload["types"] = args["--types"]
        
        # Pagination
        if args.get("--skip"):
            payload["skip"] = int(args["--skip"][0])
        if args.get("--top"):
            payload["top"] = int(args["--top"][0])
        
        # Sorting
        if args.get("--order-by-field"):
            payload["orderby"] = [{
                "field": args["--order-by-field"][0],
                "direction": args.get("--order-by-direction", ["asc"])[0]
            }]
        
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["query_data_products"]
        self.params = {}
        self.payload = payload

    # ========================================
    # GLOSSARY TERMS
    # ========================================

    @decorator
    def get_terms(self, args):
        """
Retrieve Unified Catalog term information.
    
    Retrieves detailed information about the specified Unified Catalog term.
    Returns complete Unified Catalog term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing Unified Catalog term information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_terms(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        domain_id = args.get("--governance-domain-id", [""])[0]
        
        self.method = "GET"
        
        if domain_id:
            # Use Unified Catalog terms API with domainId filter
            self.endpoint = ENDPOINTS["unified_catalog"]["list_terms"]
            self.params = {"domainId": domain_id}
        else:
            # List all UC terms
            self.endpoint = ENDPOINTS["unified_catalog"]["list_terms"]
            self.params = {}

    # Keeping old Data Map glossary-based implementation for reference/fallback
    def get_terms_from_glossary(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = GlossaryUnifiedCatalogClient()
        
        result = client.get_terms_from_glossary(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        domain_id = args.get("--governance-domain-id", [""])[0]

        # If no domain provided, list all glossaries via the Glossary client
        from ._glossary import Glossary

        gclient = Glossary()

        # Helper to normalize glossary list responses
        def _normalize_glossary_list(resp):
            if isinstance(resp, dict):
                return resp.get("value", []) or []
            elif isinstance(resp, (list, tuple)):
                return resp
            return []

        try:
            if not domain_id:
                glossaries = gclient.glossaryRead({})
                normalized = _normalize_glossary_list(glossaries)
                if os.getenv("PURVIEWCLI_DEBUG"):
                    try:
                        print("[PURVIEWCLI DEBUG] get_terms returning (no domain_id):", json.dumps(normalized, default=str, indent=2))
                    except Exception:
                        print("[PURVIEWCLI DEBUG] get_terms returning (no domain_id): (could not serialize)")
                return normalized

            # 1) Get governance domain info to obtain a human-readable name
            # Note: Nested domains may not be directly fetchable via /businessdomains/{id}
            # If fetch fails, we'll match by domain_id in qualifiedName
            domain_info = None
            domain_name = None
            try:
                domain_info = self.get_governance_domain_by_id({"--domain-id": [domain_id]})
                if isinstance(domain_info, dict):
                    domain_name = domain_info.get("name") or domain_info.get("displayName") or domain_info.get("qualifiedName")
            except Exception as e:
                if os.getenv("PURVIEWCLI_DEBUG"):
                    print(f"[PURVIEWCLI DEBUG] Could not fetch domain by ID (may be nested): {e}")
                # Continue without domain_name; will match by domain_id in qualifiedName

            # If explicit glossary GUID provided, fetch that glossary directly
            explicit_guid_list = args.get("--glossary-guid")
            if explicit_guid_list:
                # Extract the GUID string from the list
                explicit_guid = explicit_guid_list[0] if isinstance(explicit_guid_list, list) else explicit_guid_list
                if os.getenv("PURVIEWCLI_DEBUG"):
                    print(f"[PURVIEWCLI DEBUG] get_terms: Using explicit glossary GUID: {explicit_guid}")
                # Pass as string, not list, to glossary client
                detailed = gclient.glossaryReadDetailed({"--glossaryGuid": explicit_guid})
                if isinstance(detailed, dict):
                    return [{
                        "guid": explicit_guid,
                        "name": detailed.get("name") or detailed.get("qualifiedName"),
                        "terms": detailed.get("terms") or [],
                    }]
                return []

            # 2) List all glossaries and try to find ones that look associated
            all_glossaries_resp = gclient.glossaryRead({})
            all_glossaries = _normalize_glossary_list(all_glossaries_resp)

            if os.getenv("PURVIEWCLI_DEBUG"):
                try:
                    print("[PURVIEWCLI DEBUG] get_terms: domain_id=", domain_id, "domain_name=", domain_name)
                    print("[PURVIEWCLI DEBUG] all_glossaries:", json.dumps(all_glossaries, default=str, indent=2))
                except Exception:
                    print("[PURVIEWCLI DEBUG] get_terms: (could not serialize glossary list)")

            matched = []
            for g in all_glossaries:
                if not isinstance(g, dict):
                    continue
                g_name = g.get("name") or g.get("qualifiedName") or ""
                g_guid = g.get("guid") or g.get("id") or g.get("glossaryGuid")
                qn = str(g.get("qualifiedName", ""))
                
                # For nested domains, look for domain_id in qualifiedName
                # Pattern: "Domain Name@domain-id" or similar
                if domain_id and domain_id in qn:
                    matched.append((g_guid, g))
                    continue
                
                # Match by exact name if we have domain_name
                if domain_name and domain_name.lower() == str(g_name).lower():
                    matched.append((g_guid, g))
                    continue
                    
                # Match if domain_name appears in qualifiedName
                if domain_name and domain_name.lower() in qn.lower():
                    matched.append((g_guid, g))
                    continue

            # 3) For matched glossaries, fetch detailed glossary (which contains terms)
            results = []
            for guid, base_g in matched:
                if not guid:
                    continue
                detailed = gclient.glossaryReadDetailed({"--glossaryGuid": [guid]})
                # glossaryReadDetailed should return a dict representing the glossary
                if isinstance(detailed, dict):
                    # some endpoints return the glossary inside 'data' or as raw dict
                    glossary_obj = detailed
                else:
                    glossary_obj = None

                # Ensure 'terms' key exists and is a list of term objects
                terms = []
                if isinstance(glossary_obj, dict):
                    terms = glossary_obj.get("terms") or []
                results.append({
                    "guid": guid,
                    "name": base_g.get("name") or base_g.get("qualifiedName"),
                    "terms": terms,
                })

            if os.getenv("PURVIEWCLI_DEBUG"):
                try:
                    print("[PURVIEWCLI DEBUG] get_terms matched results:", json.dumps(results, default=str, indent=2))
                except Exception:
                    print("[PURVIEWCLI DEBUG] get_terms matched results: (could not serialize)")
            return results

        except Exception as e:
            # If anything fails, return an empty list rather than crashing
            print(f"Warning: failed to list glossaries/terms for domain {domain_id}: {e}")
            return []

    @decorator
    def get_term_by_id(self, args):
        """
Retrieve Unified Catalog term information.
    
    Retrieves detailed information about the specified Unified Catalog term.
    Returns complete Unified Catalog term metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing Unified Catalog term information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_term_by_id(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        term_id = args.get("--term-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_term"].format(termId=term_id)
        self.params = {}

    @decorator
    def create_term(self, args):
        """
Create a new Unified Catalog term.
    
    Creates a new Unified Catalog term in Microsoft Purview.
    Requires appropriate permissions and valid Unified Catalog term definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created Unified Catalog term:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_term(args=...)
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
        
        result = client.create_term(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_terms"]

        # Build Unified Catalog term payload
        domain_id = args.get("--governance-domain-id", [""])[0]
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})
        
        # Get acronyms if provided
        acronyms = args.get("--acronym", [])
        
        # Get resources if provided
        resources = []
        resource_names = args.get("--resource-name", [])
        resource_urls = args.get("--resource-url", [])
        if resource_names and resource_urls:
            for i in range(min(len(resource_names), len(resource_urls))):
                resources.append({
                    "name": resource_names[i],
                    "url": resource_urls[i]
                })
        
        payload = {
            "name": name,
            "description": description,
            "domain": domain_id,
            "status": status,
        }
        
        # Add parent_id if provided
        parent_id = args.get("--parent-id", [""])[0]
        if parent_id:
            payload["parentId"] = parent_id
        
        # Add optional fields
        if owners:
            payload["contacts"] = {"owner": owners}
        if acronyms:
            payload["acronyms"] = acronyms
        if resources:
            payload["resources"] = resources

        self.payload = payload

    def update_term(self, args):
        """
Update an existing Unified Catalog term.
    
    Updates an existing Unified Catalog term with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated Unified Catalog term:
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
        client = UnifiedCatalogClient()
        
        result = client.update_term(args=...)
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
        
        result = client.update_term(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        from purviewcli.client.endpoint import get_data
        
        term_id = args.get("--term-id", [""])[0]
        
        # First, fetch the existing term to get current values
        fetch_client = UnifiedCatalogClient()
        existing_term = fetch_client.get_term_by_id({"--term-id": [term_id]})
        
        if not existing_term or (isinstance(existing_term, dict) and existing_term.get("error")):
            return {"error": f"Could not fetch existing term {term_id}"}
        
        # Start with existing term data
        payload = {
            "id": term_id,
            "name": existing_term.get("name", ""),
            "description": existing_term.get("description", ""),
            "domain": existing_term.get("domain", ""),
            "status": existing_term.get("status", "Draft"),
        }
        
        # Update with provided values (only if explicitly provided)
        if args.get("--name"):
            payload["name"] = args["--name"][0]
        if "--description" in args:  # Allow empty string
            payload["description"] = args.get("--description", [""])[0]
        if args.get("--governance-domain-id"):
            payload["domain"] = args["--governance-domain-id"][0]
        if args.get("--parent-id"):
            payload["parentId"] = args["--parent-id"][0]
        if args.get("--status"):
            payload["status"] = args["--status"][0]
        
        # Handle owners - replace or add to existing
        contacts = existing_term.get("contacts") or {}
        existing_owners = contacts.get("owner", []) if isinstance(contacts, dict) else []
        if args.get("--owner-id"):
            # Replace owners
            owners = [{"id": oid} for oid in args["--owner-id"]]
            payload["contacts"] = {"owner": owners}
        elif args.get("--add-owner-id"):
            # Add to existing owners
            existing_owner_ids = set()
            if isinstance(existing_owners, list):
                for o in existing_owners:
                    if isinstance(o, dict) and o.get("id"):
                        existing_owner_ids.add(o.get("id"))
            new_owner_ids = args["--add-owner-id"]
            combined_owner_ids = existing_owner_ids.union(set(new_owner_ids))
            owners = [{"id": oid} for oid in combined_owner_ids]
            payload["contacts"] = {"owner": owners}
        elif existing_owners:
            # Keep existing owners
            payload["contacts"] = {"owner": existing_owners}
        
        # Handle acronyms - replace or add to existing
        existing_acronyms = existing_term.get("acronyms", []) or []
        if args.get("--acronym"):
            # Replace acronyms
            payload["acronyms"] = list(args["--acronym"])
        elif args.get("--add-acronym"):
            # Add to existing acronyms
            combined_acronyms = list(set(existing_acronyms + list(args["--add-acronym"])))
            payload["acronyms"] = combined_acronyms
        elif existing_acronyms:
            # Keep existing acronyms
            payload["acronyms"] = existing_acronyms
        
        # Handle resources - replace with new ones if provided
        existing_resources = existing_term.get("resources", []) or []
        resource_names = args.get("--resource-name", [])
        resource_urls = args.get("--resource-url", [])
        if resource_names and resource_urls:
            # Replace resources
            resources = []
            for i in range(min(len(resource_names), len(resource_urls))):
                resources.append({
                    "name": resource_names[i],
                    "url": resource_urls[i]
                })
            payload["resources"] = resources
        elif existing_resources:
            # Keep existing resources
            payload["resources"] = existing_resources

        # Now make the actual PUT request
        http_dict = {
            "app": "datagovernance",
            "method": "PUT",
            "endpoint": f"/datagovernance/catalog/terms/{term_id}",
            "params": {},
            "payload": payload,
            "files": None,
            "headers": {},
        }
        
        return get_data(http_dict)

    @decorator
    def delete_term(self, args):
        """
Delete a Unified Catalog term.
    
    Permanently deletes the specified Unified Catalog term.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_term(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        term_id = args.get("--term-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_term"].format(termId=term_id)
        self.params = {}

    @decorator
    def query_terms(self, args):
        """
Search for Unified Catalog terms.
    
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.query_terms(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        # Build query payload from args
        payload = {}
        
        # IDs and domain filters
        if args.get("--ids"):
            payload["ids"] = args["--ids"]
        if args.get("--domain-ids"):
            payload["domainIds"] = args["--domain-ids"]
        
        # Name/keyword search
        if args.get("--name-keyword"):
            payload["nameKeyword"] = args["--name-keyword"][0]
        
        # Acronym filter (terms-specific)
        if args.get("--acronyms"):
            payload["acronyms"] = args["--acronyms"]
        
        # Owner filter
        if args.get("--owners"):
            payload["owners"] = args["--owners"]
        
        # Status filters
        if args.get("--status"):
            payload["status"] = args["--status"][0]
        if args.get("--multi-status"):
            payload["multiStatus"] = args["--multi-status"]
        
        # Pagination
        if args.get("--skip"):
            payload["skip"] = int(args["--skip"][0])
        if args.get("--top"):
            payload["top"] = int(args["--top"][0])
        
        # Sorting
        if args.get("--order-by-field"):
            payload["orderby"] = [{
                "field": args["--order-by-field"][0],
                "direction": args.get("--order-by-direction", ["asc"])[0]
            }]
        
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["query_terms"]
        self.params = {}
        self.payload = payload

    def _get_or_create_glossary_for_domain(self, domain_id):
        """Get or create a default glossary for the domain."""
        # Improved implementation:
        # 1. Try to find existing glossaries associated with the domain using get_terms()
        # 2. If none found, attempt to create a new glossary (using the Glossary client) and return its GUID
        # 3. If anything fails, return None so callers don't send an invalid GUID to the API
        if not domain_id:
            return None

        try:
            # Try to list glossaries for this domain using the existing get_terms API
            glossaries = self.get_terms({"--governance-domain-id": [domain_id]})

            # Normalize response to a list of glossary objects
            if isinstance(glossaries, dict):
                candidates = glossaries.get("value", []) or []
            elif isinstance(glossaries, (list, tuple)):
                candidates = glossaries
            else:
                candidates = []

            # If we have candidate glossaries, prefer the first valid GUID we find
            for g in candidates:
                if not isinstance(g, dict):
                    continue
                guid = g.get("guid") or g.get("glossaryGuid") or g.get("id")
                if guid:
                    return guid

            # Nothing found -> attempt to create a glossary for this domain.
            # Try to fetch domain metadata to produce a sensible glossary name.
            # Note: For nested domains, the direct fetch may fail with 404
            domain_info = None
            domain_name = None
            try:
                domain_info = self.get_governance_domain_by_id({"--domain-id": [domain_id]})
                if isinstance(domain_info, dict):
                    domain_name = domain_info.get("name") or domain_info.get("displayName")
            except Exception as e:
                if os.getenv("PURVIEWCLI_DEBUG"):
                    print(f"[PURVIEWCLI DEBUG] Could not fetch domain for glossary creation (may be nested): {e}")
                # Continue without domain_name

            glossary_name = domain_name or f"Glossary for domain {domain_id[:8]}"
            payload = {
                "name": glossary_name,
                "qualifiedName": f"{glossary_name}@{domain_id}",
                "shortDescription": f"Auto-created glossary for governance domain {domain_name or domain_id}",
            }

            # Import Glossary client lazily to avoid circular imports
            from ._glossary import Glossary

            gclient = Glossary()
            created = gclient.glossaryCreate({"--payloadFile": payload})

            # Attempt to extract GUID from the created response
            if isinstance(created, dict):
                new_guid = created.get("guid") or created.get("id") or created.get("glossaryGuid")
                if new_guid:
                    return new_guid

        except Exception as e:
            # Log a helpful warning and continue to safe fallback
            print(f"Warning: error looking up/creating glossary for domain {domain_id}: {e}")

        # Final safe fallback: return None so create_term doesn't send an invalid GUID
        print(f"Warning: No glossary found or created for domain {domain_id}")
        return None

    # ========================================
    # OBJECTIVES AND KEY RESULTS (OKRs)
    # ========================================

    @decorator
    def get_objectives(self, args):
        """
Retrieve objective information.
    
    Retrieves detailed information about the specified objective.
    Returns complete objective metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing objective information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_objectives(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        domain_id = args.get("--governance-domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_objectives"]
        self.params = {"domainId": domain_id} if domain_id else {}

    @decorator
    def get_objective_by_id(self, args):
        """
Retrieve objective information.
    
    Retrieves detailed information about the specified objective.
    Returns complete objective metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing objective information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_objective_by_id(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_objective"].format(objectiveId=objective_id)
        self.params = {}

    @decorator
    def create_objective(self, args):
        """
Create a new objective.
    
    Creates a new objective in Microsoft Purview.
    Requires appropriate permissions and valid objective definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created objective:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_objective(args=...)
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
        
        result = client.create_objective(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_objectives"]

        domain_id = args.get("--governance-domain-id", [""])[0]
        definition = args.get("--definition", [""])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})

        payload = {
            "domain": domain_id,
            "definition": definition,
            "status": status,
        }

        if owners:
            payload["contacts"] = {"owner": owners}
        if args.get("--target-date"):
            payload["targetDate"] = args["--target-date"][0]

        self.payload = payload

    @decorator
    def update_objective(self, args):
        """
Update an existing objective.
    
    Updates an existing objective with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated objective:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.update_objective(args=...)
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
        
        result = client.update_objective(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "PUT"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_objective"].format(objectiveId=objective_id)

        domain_id = args.get("--governance-domain-id", [""])[0]
        definition = args.get("--definition", [""])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})

        payload = {
            "id": objective_id,
            "domain": domain_id,
            "definition": definition,
            "status": status,
        }

        if owners:
            payload["contacts"] = {"owner": owners}
        if args.get("--target-date"):
            payload["targetDate"] = args["--target-date"][0]

        self.payload = payload

    @decorator
    def delete_objective(self, args):
        """
Delete a objective.
    
    Permanently deletes the specified objective.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_objective(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_objective"].format(objectiveId=objective_id)
        self.params = {}

    @decorator
    def query_objectives(self, args):
        """
Search for objectives.
    
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.query_objectives(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        # Build query payload from args
        payload = {}
        
        # IDs and domain filters
        if args.get("--ids"):
            payload["ids"] = args["--ids"]
        if args.get("--domain-ids"):
            payload["domainIds"] = args["--domain-ids"]
        
        # Definition keyword search (objectives-specific)
        if args.get("--definition"):
            payload["definition"] = args["--definition"][0]
        
        # Owner filter
        if args.get("--owners"):
            payload["owners"] = args["--owners"]
        
        # Status filters
        if args.get("--status"):
            payload["status"] = args["--status"][0]
        if args.get("--multi-status"):
            payload["multiStatus"] = args["--multi-status"]
        
        # Pagination
        if args.get("--skip"):
            payload["skip"] = int(args["--skip"][0])
        if args.get("--top"):
            payload["top"] = int(args["--top"][0])
        
        # Sorting
        if args.get("--order-by-field"):
            payload["orderby"] = [{
                "field": args["--order-by-field"][0],
                "direction": args.get("--order-by-direction", ["asc"])[0]
            }]
        
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["query_objectives"]
        self.params = {}
        self.payload = payload

    # ========================================
    # KEY RESULTS (Part of OKRs)
    # ========================================

    @decorator
    def get_key_results(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_key_results(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_key_results"].format(objectiveId=objective_id)
        self.params = {}

    @decorator
    def get_key_result_by_id(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_key_result_by_id(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        objective_id = args.get("--objective-id", [""])[0]
        key_result_id = args.get("--key-result-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_key_result"].format(objectiveId=objective_id, keyResultId=key_result_id)
        self.params = {}

    @decorator
    def create_key_result(self, args):
        """
Create a new resource.
    
    Creates a new resource in Microsoft Purview Unified Catalog.
    Requires appropriate permissions and valid resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_key_result(args=...)
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
        
        result = client.create_key_result(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        objective_id = args.get("--objective-id", [""])[0]
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_key_results"].format(objectiveId=objective_id)

        domain_id = args.get("--governance-domain-id", [""])[0]
        progress = int(args.get("--progress", ["0"])[0])
        goal = int(args.get("--goal", ["100"])[0])
        max_value = int(args.get("--max", ["100"])[0])
        status = args.get("--status", ["OnTrack"])[0]
        definition = args.get("--definition", [""])[0]

        payload = {
            "progress": progress,
            "goal": goal,
            "max": max_value,
            "status": status,
            "definition": definition,
            "domainId": domain_id,
        }

        self.payload = payload

    @decorator
    def update_key_result(self, args):
        """
Update an existing resource.
    
    Updates an existing resource in Unified Catalog with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.update_key_result(args=...)
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
        
        result = client.update_key_result(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        objective_id = args.get("--objective-id", [""])[0]
        key_result_id = args.get("--key-result-id", [""])[0]
        self.method = "PUT"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_key_result"].format(objectiveId=objective_id, keyResultId=key_result_id)

        domain_id = args.get("--governance-domain-id", [""])[0]
        progress = int(args.get("--progress", ["0"])[0])
        goal = int(args.get("--goal", ["100"])[0])
        max_value = int(args.get("--max", ["100"])[0])
        status = args.get("--status", ["OnTrack"])[0]
        definition = args.get("--definition", [""])[0]

        payload = {
            "id": key_result_id,
            "progress": progress,
            "goal": goal,
            "max": max_value,
            "status": status,
            "definition": definition,
            "domainId": domain_id,
        }

        self.payload = payload

    @decorator
    def delete_key_result(self, args):
        """
Delete a resource.
    
    Permanently deletes the specified resource from Unified Catalog.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_key_result(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        objective_id = args.get("--objective-id", [""])[0]
        key_result_id = args.get("--key-result-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_key_result"].format(objectiveId=objective_id, keyResultId=key_result_id)
        self.params = {}

    # ========================================
    # CRITICAL DATA ELEMENTS (CDEs)
    # ========================================

    @decorator
    def get_critical_data_elements(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_critical_data_elements(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        domain_id = args.get("--governance-domain-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_cdes"]
        self.params = {"domainId": domain_id} if domain_id else {}

    @decorator
    def get_critical_data_element_by_id(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_critical_data_element_by_id(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        cde_id = args.get("--cde-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_cde"].format(cdeId=cde_id)
        self.params = {}

    @decorator
    def create_critical_data_element(self, args):
        """
Create a new resource.
    
    Creates a new resource in Microsoft Purview Unified Catalog.
    Requires appropriate permissions and valid resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_critical_data_element(args=...)
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
        
        result = client.create_critical_data_element(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_cdes"]

        domain_id = args.get("--governance-domain-id", [""])[0]
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        data_type = args.get("--data-type", ["Number"])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})

        payload = {
            "name": name,
            "description": description,
            "domain": domain_id,
            "dataType": data_type,
            "status": status,
        }

        if owners:
            payload["contacts"] = {"owner": owners}

        self.payload = payload

    @decorator
    def update_critical_data_element(self, args):
        """
Update an existing resource.
    
    Updates an existing resource in Unified Catalog with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.update_critical_data_element(args=...)
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
        
        result = client.update_critical_data_element(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        cde_id = args.get("--cde-id", [""])[0]
        self.method = "PUT"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_cde"].format(cdeId=cde_id)

        domain_id = args.get("--governance-domain-id", [""])[0]
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        data_type = args.get("--data-type", ["Number"])[0]
        status = args.get("--status", ["Draft"])[0]
        
        # Get owner IDs if provided
        owner_ids = args.get("--owner-id", [])
        owners = []
        if owner_ids:
            for owner_id in owner_ids:
                owners.append({"id": owner_id})

        payload = {
            "id": cde_id,
            "name": name,
            "description": description,
            "domain": domain_id,
            "dataType": data_type,
            "status": status,
        }

        if owners:
            payload["contacts"] = {"owner": owners}

        self.payload = payload

    @decorator
    def delete_critical_data_element(self, args):
        """
Delete a resource.
    
    Permanently deletes the specified resource from Unified Catalog.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_critical_data_element(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        cde_id = args.get("--cde-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_cde"].format(cdeId=cde_id)
        self.params = {}

    @decorator
    def query_critical_data_elements(self, args):
        """
Search for resources.
    
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.query_critical_data_elements(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Locate datasets by name or properties
        - Impact Analysis: Find all assets related to a term
        - Compliance: Identify sensitive data across catalog
    """
        # Build query payload from args
        payload = {}
        
        # IDs and domain filters
        if args.get("--ids"):
            payload["ids"] = args["--ids"]
        if args.get("--domain-ids"):
            payload["domainIds"] = args["--domain-ids"]
        
        # Name/keyword search
        if args.get("--name-keyword"):
            payload["nameKeyword"] = args["--name-keyword"][0]
        
        # Owner filter
        if args.get("--owners"):
            payload["owners"] = args["--owners"]
        
        # Status filters
        if args.get("--status"):
            payload["status"] = args["--status"][0]
        if args.get("--multi-status"):
            payload["multiStatus"] = args["--multi-status"]
        
        # Pagination
        if args.get("--skip"):
            payload["skip"] = int(args["--skip"][0])
        if args.get("--top"):
            payload["top"] = int(args["--top"][0])
        
        # Sorting
        if args.get("--order-by-field"):
            payload["orderby"] = [{
                "field": args["--order-by-field"][0],
                "direction": args.get("--order-by-direction", ["asc"])[0]
            }]
        
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["query_critical_data_elements"]
        self.params = {}
        self.payload = payload

    @decorator
    def create_cde_relationship(self, args):
        """
Create a new resource.
    
    Creates a new resource in Microsoft Purview Unified Catalog.
    Requires appropriate permissions and valid resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_cde_relationship(args=...)
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
        
        result = client.create_cde_relationship(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        cde_id = args.get("--cde-id", [""])[0]
        entity_type = args.get("--entity-type", [""])[0]  # e.g., "CRITICALDATACOLUMN"
        entity_id = args.get("--entity-id", [""])[0]
        asset_id = args.get("--asset-id", [""])[0] if args.get("--asset-id") else entity_id
        relationship_type = args.get("--relationship-type", ["Related"])[0]
        description = args.get("--description", [""])[0]
        
        # Build request body (same structure as data product relationships)
        payload = {
            "relationship1": {
                "description": description,
                "relationshipType": relationship_type,
                "assetId": asset_id,
                "entityId": entity_id
            }
        }
        
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["create_cde_relationship"].format(cdeId=cde_id)
        self.params = {"entityType": entity_type.upper()}
        self.payload = payload

    @decorator
    def get_cde_relationships(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_cde_relationships(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        cde_id = args.get("--cde-id", [""])[0]
        entity_type = args.get("--entity-type", [""])[0] if args.get("--entity-type") else None
        
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_cde_relationships"].format(cdeId=cde_id)
        
        # Entity type is optional filter
        if entity_type:
            self.params = {"entityType": entity_type.upper()}
        else:
            self.params = {}

    @decorator
    def delete_cde_relationship(self, args):
        """
Delete a resource.
    
    Permanently deletes the specified resource from Unified Catalog.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_cde_relationship(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        cde_id = args.get("--cde-id", [""])[0]
        entity_type = args.get("--entity-type", [""])[0]
        entity_id = args.get("--entity-id", [""])[0]
        
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["delete_cde_relationship"].format(cdeId=cde_id)
        self.params = {
            "entityType": entity_type.upper(),
            "entityId": entity_id
        }

    # ========================================
    # RELATIONSHIPS
    # ========================================
    
    @decorator
    def get_relationships(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_relationships(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        entity_type = args.get("--entity-type", [""])[0]  # Term, DataProduct, CriticalDataElement
        entity_id = args.get("--entity-id", [""])[0]
        filter_type = args.get("--filter-type", [""])[0]  # Optional: CustomMetadata, DataAsset, DataProduct, etc.
        
        # Map entity type to endpoint
        endpoint_map = {
            "Term": "terms",
            "DataProduct": "dataproducts", 
            "CriticalDataElement": "criticalDataElements",
        }
        
        endpoint_base = endpoint_map.get(entity_type)
        if not endpoint_base:
            raise ValueError(f"Invalid entity type: {entity_type}. Must be Term, DataProduct, or CriticalDataElement")
        
        self.method = "GET"
        self.endpoint = f"/datagovernance/catalog/{endpoint_base}/{entity_id}/relationships"
        
        # Add optional entity type filter
        if filter_type:
            valid_filters = ["CustomMetadata", "DataAsset", "DataProduct", "CriticalDataColumn", "CriticalDataElement", "Term"]
            if filter_type not in valid_filters:
                raise ValueError(f"Invalid filter type: {filter_type}. Must be one of: {', '.join(valid_filters)}")
            self.params = {"entityType": filter_type}
        else:
            self.params = {}

    @decorator
    def create_relationship(self, args):
        """
Create a new resource.
    
    Creates a new resource in Microsoft Purview Unified Catalog.
    Requires appropriate permissions and valid resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_relationship(args=...)
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
        
        result = client.create_relationship(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        entity_type = args.get("--entity-type", [""])[0]  # Term, DataProduct, CriticalDataElement
        entity_id = args.get("--entity-id", [""])[0]
        target_entity_id = args.get("--target-entity-id", [""])[0]
        relationship_type = args.get("--relationship-type", ["Related"])[0]  # Synonym, Related
        description = args.get("--description", [""])[0]
        
        # Map entity type to endpoint
        endpoint_map = {
            "Term": "terms",
            "DataProduct": "dataproducts",
            "CriticalDataElement": "criticalDataElements",
        }
        
        endpoint_base = endpoint_map.get(entity_type)
        if not endpoint_base:
            raise ValueError(f"Invalid entity type: {entity_type}. Must be Term, DataProduct, or CriticalDataElement")
        
        self.method = "POST"
        self.endpoint = f"/datagovernance/catalog/{endpoint_base}/{entity_id}/relationships"
        self.params = {"entityType": entity_type}
        
        self.payload = {
            "entityId": target_entity_id,
            "relationshipType": relationship_type,
            "description": description,
        }

    @decorator
    def delete_relationship(self, args):
        """
Delete a resource.
    
    Permanently deletes the specified resource from Unified Catalog.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_relationship(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        entity_type = args.get("--entity-type", [""])[0]
        entity_id = args.get("--entity-id", [""])[0]
        target_entity_id = args.get("--target-entity-id", [""])[0]
        relationship_type = args.get("--relationship-type", ["Related"])[0]
        
        # Map entity type to endpoint
        endpoint_map = {
            "Term": "terms",
            "DataProduct": "dataproducts",
            "CriticalDataElement": "criticalDataElements",
        }
        
        endpoint_base = endpoint_map.get(entity_type)
        if not endpoint_base:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        self.method = "DELETE"
        self.endpoint = f"/datagovernance/catalog/{endpoint_base}/{entity_id}/relationships"
        self.params = {
            "entityId": target_entity_id,
            "entityType": entity_type,
            "relationshipType": relationship_type,
        }

    # ========================================
    # DATA POLICIES (NEW)
    # ========================================

    @decorator
    @decorator
    def list_policies(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.list_policies(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_policies"]
        self.params = {}

    @decorator
    def get_policy(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_policy(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        policy_id = args.get("--policy-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_policy"].format(policyId=policy_id)
        self.params = {}

    @decorator
    def create_policy(self, args):
        """
Create a new resource.
    
    Creates a new resource in Microsoft Purview Unified Catalog.
    Requires appropriate permissions and valid resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_policy(args=...)
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
        
        result = client.create_policy(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_policies"]
        
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        policy_type = args.get("--type", ["Access"])[0]
        status = args.get("--status", ["Draft"])[0]
        
        payload = {
            "name": name,
            "description": description,
            "policyType": policy_type,
            "status": status,
        }
        
        self.payload = payload

    @decorator
    def update_policy(self, args):
        """
Update an existing resource.
    
    Updates an existing resource in Unified Catalog with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.update_policy(args=...)
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
        
        result = client.update_policy(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        policy_id = args.get("--policy-id", [""])[0]
        self.method = "PUT"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_policy"].format(policyId=policy_id)
        
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        policy_type = args.get("--type", ["Access"])[0]
        status = args.get("--status", ["Draft"])[0]
        
        payload = {
            "name": name,
            "description": description,
            "policyType": policy_type,
            "status": status,
        }
        
        self.payload = payload

    @decorator
    def delete_policy(self, args):
        """
Delete a resource.
    
    Permanently deletes the specified resource from Unified Catalog.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_policy(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        policy_id = args.get("--policy-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_policy"].format(policyId=policy_id)
        self.params = {}

    # ========================================
    # CUSTOM METADATA (NEW)
    # ========================================

    @decorator
    def list_custom_metadata(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.list_custom_metadata(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_custom_metadata"]
        self.params = {
            "type": "business_metadata",
            "includeTermTemplate": "true",
            "api-version": "2022-11-03"
        }

    @decorator
    def get_custom_metadata(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_custom_metadata(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        asset_id = args.get("--asset-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_custom_metadata"].format(guid=asset_id)
        self.params = {
            "api-version": "2023-09-01",
            "minExtInfo": "false",
            "ignoreRelationships": "true"
        }

    @decorator
    def add_custom_metadata(self, args):
        """
        Add custom metadata (business metadata) to an asset in Unified Catalog.
        
        Attaches custom business metadata attributes to a data asset using the Entity API.
        Business metadata allows you to add domain-specific attributes beyond the standard
        technical metadata, such as data quality scores, compliance classifications, or
        business ownership information.
        
        Args:
            args: Dictionary containing:
                  Required:
                  - '--asset-id' (str): Asset unique identifier (GUID)
                  - '--key' (str): Metadata attribute name (e.g., "DataClassification", "Owner")
                  - '--value' (str): Attribute value (e.g., "Confidential", "Sales Team")
                  
                  Optional:
                  - '--group' (str): Metadata group name (default: "Custom")
                                    Groups organize related attributes together
        
        Returns:
            Dictionary with operation result:
                {
                    'mutatedEntities': {
                        'UPDATE': [
                            {
                                'guid': str,         # Updated asset GUID
                                'typeName': str,     # Asset type
                                'businessAttributes': {
                                    'GroupName': {   # Your metadata group
                                        'key': str   # Added attribute
                                    }
                                }
                            }
                        ]
                    }
                }
        
        Raises:
            ValueError: When asset-id, key, or value is missing
            
            AuthenticationError: When Azure credentials invalid
            
            HTTPError: When Purview API returns error:
                - 400: Invalid metadata format or attribute name
                - 401: Unauthorized
                - 403: Forbidden (requires Data Curator role)
                - 404: Asset not found
                - 429: Rate limit exceeded
                - 500: Internal server error
        
        Example:
            # Add data classification metadata
            client = UnifiedCatalogClient()
            args = {
                '--asset-id': ['abcd1234-5678-90ab-cdef-1234567890ab'],
                '--key': ['DataClassification'],
                '--value': ['Confidential'],
                '--group': ['Compliance']
            }
            result = client.add_custom_metadata(args)
            print(f"Added metadata to: {result['mutatedEntities']['UPDATE'][0]['guid']}")
            
            # Add data quality score
            args = {
                '--asset-id': ['abcd1234-...'],
                '--key': ['QualityScore'],
                '--value': ['95'],
                '--group': ['DataQuality']
            }
            result = client.add_custom_metadata(args)
            
            # Add business owner
            args = {
                '--asset-id': ['abcd1234-...'],
                '--key': ['BusinessOwner'],
                '--value': ['Jane Smith'],
                '--group': ['Ownership']
            }
            result = client.add_custom_metadata(args)
        
        Use Cases:
            - Data Classification: Tag assets with sensitivity levels (Public, Internal, Confidential)
            - Compliance Tracking: Mark assets with regulatory requirements (GDPR, HIPAA, SOX)
            - Data Quality: Attach quality scores or validation status
            - Business Ownership: Associate business owners or stewards with assets
            - Custom Taxonomies: Apply organization-specific categorization schemes
        
        Notes:
            - Metadata is organized into groups for better organization
            - Multiple attributes can be added to the same group
            - POST operation adds new attributes without removing existing ones
            - Use update_custom_metadata() to modify existing attribute values
        
        See Also:
            - update_custom_metadata: Modify existing metadata values
            - delete_custom_metadata: Remove metadata from asset
            - get_custom_metadata: Retrieve asset's custom metadata
        """
        asset_id = args.get("--asset-id", [""])[0]
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["add_custom_metadata"].format(guid=asset_id)
        self.params = {"api-version": "2023-09-01"}
        
        # Build payload based on parameters
        key = args.get("--key", [""])[0]
        value = args.get("--value", [""])[0]
        group = args.get("--group", ["Custom"])[0]  # Default group name
        
        # Format: { "GroupName": { "attributeName": "value" } }
        payload = {
            group: {
                key: value
            }
        }
        
        self.payload = payload

    @decorator
    def update_custom_metadata(self, args):
        """
        Update custom metadata (business metadata) for an asset in Unified Catalog.
        
        Modifies existing business metadata attribute values on a data asset. This operation
        overwrites the specified attributes while preserving other attributes in the same
        group and other groups.
        
        Args:
            args: Dictionary containing:
                  Required:
                  - '--asset-id' (str): Asset unique identifier (GUID)
                  - '--key' (str): Metadata attribute name to update
                  - '--value' (str): New attribute value
                  
                  Optional:
                  - '--group' (str): Metadata group name (default: "Custom")
        
        Returns:
            Dictionary with update result:
                {
                    'mutatedEntities': {
                        'UPDATE': [
                            {
                                'guid': str,         # Updated asset GUID
                                'typeName': str,     # Asset type
                                'businessAttributes': {
                                    'GroupName': {   # Updated metadata group
                                        'key': str   # New attribute value
                                    }
                                }
                            }
                        ]
                    }
                }
        
        Raises:
            ValueError: When asset-id, key, or value is missing
            
            AuthenticationError: When Azure credentials invalid
            
            HTTPError: When Purview API returns error:
                - 400: Invalid metadata format or attribute name
                - 401: Unauthorized
                - 403: Forbidden (requires Data Curator role)
                - 404: Asset not found or attribute doesn't exist
                - 429: Rate limit exceeded
                - 500: Internal server error
        
        Example:
            # Update data classification level
            client = UnifiedCatalogClient()
            args = {
                '--asset-id': ['abcd1234-5678-90ab-cdef-1234567890ab'],
                '--key': ['DataClassification'],
                '--value': ['Public'],  # Changed from Confidential
                '--group': ['Compliance']
            }
            result = client.update_custom_metadata(args)
            print(f"Updated metadata on: {result['mutatedEntities']['UPDATE'][0]['guid']}")
            
            # Update quality score after validation
            args = {
                '--asset-id': ['abcd1234-...'],
                '--key': ['QualityScore'],
                '--value': ['98'],  # Improved from 95
                '--group': ['DataQuality']
            }
            result = client.update_custom_metadata(args)
            
            # Update business owner after transfer
            args = {
                '--asset-id': ['abcd1234-...'],
                '--key': ['BusinessOwner'],
                '--value': ['John Doe'],  # New owner
                '--group': ['Ownership']
            }
            result = client.update_custom_metadata(args)
        
        Use Cases:
            - Classification Updates: Change sensitivity level as data usage changes
            - Quality Score Refresh: Update quality metrics after validation runs
            - Ownership Transfer: Reassign business owners during reorganization
            - Compliance Status: Update certification or approval status
            - Lifecycle Management: Mark assets as certified, deprecated, or archived
        
        Notes:
            - Only updates the specified attribute; other attributes unchanged
            - Creates the attribute if it doesn't exist (behaves like add)
            - POST method is used, not PUT, to preserve other metadata
            - Changes are immediate and reflected in search/browse
        
        See Also:
            - add_custom_metadata: Add new metadata attributes
            - delete_custom_metadata: Remove metadata from asset
            - get_custom_metadata: Retrieve current metadata values
        """
        asset_id = args.get("--asset-id", [""])[0]
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["update_custom_metadata"].format(guid=asset_id)
        self.params = {"api-version": "2023-09-01"}
        
        key = args.get("--key", [""])[0]
        value = args.get("--value", [""])[0]
        group = args.get("--group", ["Custom"])[0]
        
        payload = {
            group: {
                key: value
            }
        }
        
        self.payload = payload

    @decorator
    def delete_custom_metadata(self, args):
        """
Delete a resource.
    
    Permanently deletes the specified resource from Unified Catalog.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_custom_metadata(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        asset_id = args.get("--asset-id", [""])[0]
        group = args.get("--group", [""])[0]
        
        if not group:
            raise ValueError("--group parameter is required to delete business metadata")
        
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["delete_custom_metadata"].format(guid=asset_id)
        self.params = {
            "api-version": "2023-09-01"
        }
        # Payload must contain the group with empty dict to delete entire group
        self.payload = {
            group: {}
        }

    # ========================================
    # CUSTOM ATTRIBUTES (NEW)
    # ========================================

    @decorator
    def list_custom_attributes(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.list_custom_attributes(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_custom_attributes"]
        self.params = {}

    @decorator
    def get_custom_attribute(self, args):
        """
Retrieve resource information.
    
    Retrieves detailed information about the specified resource from Unified Catalog.
    Returns complete resource metadata and properties.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing resource information:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.get_custom_attribute(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Discovery: Find and explore data assets
        - Compliance Auditing: Review metadata and classifications
        - Reporting: Generate catalog reports
    """
        attribute_id = args.get("--attribute-id", [""])[0]
        self.method = "GET"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_custom_attribute"].format(attributeId=attribute_id)
        self.params = {}

    @decorator
    def create_custom_attribute(self, args):
        """
Create a new resource.
    
    Creates a new resource in Microsoft Purview Unified Catalog.
    Requires appropriate permissions and valid resource definition.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing created resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.create_custom_attribute(args=...)
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
        
        result = client.create_custom_attribute(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Data Onboarding: Register new data sources in catalog
        - Metadata Management: Add descriptive metadata to assets
        - Automation: Programmatically populate catalog
    """
        self.method = "POST"
        self.endpoint = ENDPOINTS["unified_catalog"]["list_custom_attributes"]
        
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        data_type = args.get("--type", ["string"])[0]
        required = args.get("--required", ["false"])[0].lower() == "true"
        
        payload = {
            "name": name,
            "description": description,
            "dataType": data_type,
            "required": required,
        }
        
        self.payload = payload

    @decorator
    def update_custom_attribute(self, args):
        """
Update an existing resource.
    
    Updates an existing resource in Unified Catalog with new values.
    Only specified fields are modified; others remain unchanged.
    
Args:
        args: Dictionary of operation arguments.
               Contains operation-specific parameters.
               See method implementation for details.
    
Returns:
        Dictionary containing updated resource:
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.update_custom_attribute(args=...)
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
        
        result = client.update_custom_attribute(data)
        print(f"Created/Updated: {result['guid']}")
    
Use Cases:
        - Metadata Enrichment: Update descriptions and tags
        - Ownership Changes: Reassign data ownership
        - Classification: Apply or modify data classifications
    """
        attribute_id = args.get("--attribute-id", [""])[0]
        self.method = "PUT"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_custom_attribute"].format(attributeId=attribute_id)
        
        name = args.get("--name", [""])[0]
        description = args.get("--description", [""])[0]
        data_type = args.get("--type", ["string"])[0]
        required = args.get("--required", ["false"])[0].lower() == "true"
        
        payload = {
            "name": name,
            "description": description,
            "dataType": data_type,
            "required": required,
        }
        
        self.payload = payload

    @decorator
    def delete_custom_attribute(self, args):
        """
Delete a resource.
    
    Permanently deletes the specified resource from Unified Catalog.
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
        client = UnifiedCatalogUnifiedCatalogClient()
        
        result = client.delete_custom_attribute(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - Data Cleanup: Remove obsolete or test data
        - Decommissioning: Delete resources no longer in use
        - Testing: Clean up test environments
    """
        attribute_id = args.get("--attribute-id", [""])[0]
        self.method = "DELETE"
        self.endpoint = ENDPOINTS["unified_catalog"]["get_custom_attribute"].format(attributeId=attribute_id)
        self.params = {}

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
        client = UnifiedCatalogClient()
        
        result = client.help(args=...)
        print(f"Result: {result}")
    
Use Cases:
        - [TODO: Add specific use cases for this operation]
        - [TODO: Include business context]
        - [TODO: Explain when to use this method]
    """
        help_text = """
Microsoft Purview Unified Catalog Client

Available Operations:
- Governance Domains: list, get, create, update, delete
- Data Products: list, get, create, update, delete
- Terms: list, get, create, update, delete
- Objectives (OKRs): list, get, create, update, delete
- Key Results: list, get, create, update, delete
- Critical Data Elements: list, get, create, update, delete
- Data Policies: list, get, create, update, delete (NEW)
- Custom Metadata: list, get, add, update, delete (NEW)
- Custom Attributes: list, get, create, update, delete (NEW)
- Relationships: create, delete (between terms, data products, CDEs)

Use --payloadFile to provide JSON payload for create/update operations.
Use individual flags like --name, --description for simple operations.

Note: This client uses the Unified Catalog API (/datagovernance/catalog/*)
which is separate from the Data Map API (/catalog/api/atlas/*).
"""
        return {"message": help_text}
