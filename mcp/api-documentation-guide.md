# API Documentation Guide for MCP/LLM Integration

## Purpose
This guide explains how to document Purview CLI APIs so they can be effectively used by LLMs through the MCP (Model Context Protocol) server.

## Documentation Principles

### 1. Structured Docstrings
Every public method should have comprehensive docstrings with these sections:

```python
async def method_name(self, param1: str, param2: Optional[int] = None) -> Dict:
    """
    Brief one-line description of what the method does.
    
    Longer description explaining the purpose, context, and when to use this method.
    Include business context and common use cases.
    
    Args:
        param1: Description of param1 including:
               - Type information (if not in signature)
               - Valid values or constraints
               - Required vs optional
               - Default behavior
        param2: Description of param2 with examples:
               - Range: 1-1000 (default: 100)
               - Used for pagination or filtering
               
    Returns:
        Dictionary containing:
            - field1 (str): Description of field1
            - field2 (List[Dict]): Description of field2 structure
                - subfield1 (str): Description
                - subfield2 (int): Description
            - field3 (Optional[str]): Description, may be None if...
            
    Raises:
        ValueError: When param1 is empty or invalid
        HTTPError: When API returns 4xx/5xx status
        AuthenticationError: When credentials are invalid or expired
        
    Example:
        # Basic usage
        result = await client.method_name("example-value")
        print(f"Got {len(result['field2'])} items")
        
        # With optional parameters
        result = await client.method_name("example", param2=50)
        for item in result['field2']:
            print(f"{item['subfield1']}: {item['subfield2']}")
            
    Use Cases:
        - Data governance: Track data lineage and ownership
        - Compliance: Audit who accessed what data
        - Discovery: Find related datasets and documentation
    """
```

### 2. Module-Level Documentation
Each client module should have a comprehensive module docstring:

```python
"""
Module Name - Brief Description

This module provides [high-level purpose] for Microsoft Purview [API category].
Based on official API: [URL to Microsoft docs]
API Version: [version numbers]

Key Features:
- Feature 1: Description
- Feature 2: Description  
- Feature 3: Description

Common Workflows:
1. Workflow 1: Step by step
2. Workflow 2: Step by step

Example:
    from purviewcli.client import ModuleName
    
    client = ModuleName()
    result = await client.common_operation(...)

See Also:
    - Related Module 1: For [related functionality]
    - Related Module 2: For [related functionality]
"""
```

### 3. Class-Level Documentation
Each client class should document its purpose and initialization:

```python
class EntityClient(Endpoint):
    """
    Entity Management Operations - Complete Official API Implementation
    
    This client provides CRUD operations and advanced entity management for
    Microsoft Purview Data Map entities (assets, data sources, tables, etc.).
    
    Capabilities:
        - CRUD: Create, read, update, delete entities
        - Bulk Operations: Import/export via CSV, batch create/update
        - Classification: Assign and manage classifications
        - Business Metadata: Apply custom metadata attributes
        - Relationships: Link entities via lineage or associations
        
    Authentication:
        Requires Azure credentials with Purview Data Curator or Data Reader role.
        Uses DefaultAzureCredential for authentication.
        
    Rate Limits:
        - Read operations: 1000 requests/minute
        - Write operations: 100 requests/minute
        - Bulk operations: Rate-limited internally
        
    Example:
        client = EntityClient()
        
        # Get entity by GUID
        entity = await client.get_entity("abcd-1234-...")
        
        # Search for entities
        results = await client.search_entities(
            query="*",
            entity_type="DataSet"
        )
    """
```

### 4. Parameter Documentation Best Practices

#### For Complex Parameters
Document structure and valid values:

```python
"""
Args:
    entity_data: Entity definition dictionary with structure:
        {
            "typeName": str,  # Required. e.g., "DataSet", "azure_sql_table"
            "attributes": {   # Required. Type-specific attributes
                "qualifiedName": str,  # Required. Unique identifier
                "name": str,           # Required. Display name
                "description": str,    # Optional. Documentation
                "owner": str,          # Optional. Owner email/ID
                "createTime": int,     # Optional. Unix timestamp
                "updateTime": int      # Optional. Unix timestamp
            },
            "classifications": [  # Optional. Applied tags
                {
                    "typeName": str,        # e.g., "PII", "Confidential"
                    "attributes": dict      # Classification-specific attrs
                }
            ],
            "relationshipAttributes": {  # Optional. Related entities
                "inputTables": [guid1, guid2],  # Upstream entities
                "outputTables": [guid3]         # Downstream entities
            }
        }
"""
```

#### For Enums and Constrained Values
List all valid options:

```python
"""
Args:
    direction: Lineage direction to traverse:
               - "INPUT": Show upstream data sources
               - "OUTPUT": Show downstream consumers
               - "BOTH": Show full lineage graph (default)
               
    status: Entity status filter:
            - "ACTIVE": Published entities (default)
            - "DRAFT": Work-in-progress entities
            - "ARCHIVED": Deleted/historical entities
            - None: Show all statuses
"""
```

#### For Pagination and Filtering
Explain behavior and defaults:

```python
"""
Args:
    limit: Maximum number of results to return.
           Range: 1-1000 (default: 100)
           Used for pagination. Combine with offset for paging.
           
    offset: Number of results to skip.
            Default: 0
            Use with limit: offset=100, limit=100 gets results 100-199
            
    sort: Sort order for results.
          Format: "fieldName ASC" or "fieldName DESC"
          Examples: "name ASC", "updateTime DESC"
          Default: No sorting (natural order)
"""
```

### 5. Return Value Documentation

#### For Simple Returns
```python
"""
Returns:
    String containing the entity GUID (UUID format).
    Returns None if entity not found.
"""
```

#### For Dictionary Returns
Document nested structure:

```python
"""
Returns:
    Dictionary with entity information:
        {
            "guid": str,              # Entity unique identifier
            "typeName": str,          # Entity type (e.g., "DataSet")
            "attributes": {           # Type-specific attributes
                "qualifiedName": str, # Unique name
                "name": str,          # Display name
                ...                   # See entity type docs
            },
            "classifications": [      # Applied classifications (tags)
                {
                    "typeName": str,         # Classification name
                    "attributes": dict,      # Classification attrs
                    "entityGuid": str,       # Assigned entity
                    "validityPeriods": list  # Time ranges
                }
            ],
            "relationshipAttributes": dict,  # Related entities
            "status": str             # ACTIVE, DRAFT, or ARCHIVED
        }
"""
```

#### For List Returns
Document list item structure:

```python
"""
Returns:
    List of glossary term dictionaries, each containing:
        - guid (str): Term unique identifier
        - name (str): Term display name
        - qualifiedName (str): Full hierarchical name
        - definition (str): Term definition/description
        - status (str): DRAFT, APPROVED, or ALERT
        - assignedEntities (List[Dict]): Entities using this term
            - guid (str): Entity GUID
            - typeName (str): Entity type
            - displayText (str): Entity name
        - parentTerm (Optional[Dict]): Parent term if hierarchical
        - childTerms (List[Dict]): Child terms if hierarchical
    
    Returns empty list if no terms found.
"""
```

### 6. Error Documentation
Document all possible exceptions:

```python
"""
Raises:
    ValueError: When required parameters are missing or invalid:
        - entity_guid is None or empty string
        - direction not in ["INPUT", "OUTPUT", "BOTH"]
        
    AuthenticationError: When Azure credentials are invalid or expired:
        - DefaultAzureCredential not configured
        - Service principal permissions insufficient
        
    HTTPError: When Purview API returns error:
        - 400: Bad request (invalid entity structure)
        - 401: Unauthorized (auth token expired)
        - 403: Forbidden (insufficient permissions)
        - 404: Entity not found
        - 409: Conflict (entity already exists)
        - 429: Rate limit exceeded
        - 500: Purview internal server error
        
    NetworkError: When network connectivity fails
"""
```

### 7. Example Documentation
Provide runnable, realistic examples:

```python
"""
Example:
    # Basic entity retrieval
    client = EntityClient()
    entity = await client.get_entity("550e8400-e29b-41d4-a716-446655440000")
    print(f"Entity: {entity['attributes']['name']}")
    
    # Search for SQL tables
    results = await client.search_entities(
        query="*",
        entity_type="azure_sql_table",
        classification="PII",
        limit=50
    )
    
    for entity in results['entities']:
        print(f"Table: {entity['attributes']['qualifiedName']}")
        print(f"Classifications: {[c['typeName'] for c in entity.get('classifications', [])]}")
    
    # Create entity with classifications
    new_entity = await client.create_entity({
        "typeName": "DataSet",
        "attributes": {
            "qualifiedName": "sales_data@example",
            "name": "Sales Dataset",
            "description": "Quarterly sales records",
            "owner": "data-team@example.com"
        },
        "classifications": [
            {"typeName": "Confidential"},
            {"typeName": "Financial"}
        ]
    })
    print(f"Created entity: {new_entity['guid']}")
"""
```

### 8. Use Case Documentation
Explain when and why to use the method:

```python
"""
Use Cases:
    - Data Discovery: Find datasets by name, description, or classification
        Example: Search for all PII-tagged tables to audit compliance
        
    - Impact Analysis: Identify downstream consumers before schema changes
        Example: Find all reports using a table before modifying it
        
    - Data Governance: Track data ownership and documentation quality
        Example: List all undocumented datasets to prioritize documentation
        
    - Compliance Auditing: Find sensitive data across the organization
        Example: Locate all GDPR-classified datasets for retention policy
        
    - Metadata Management: Update entity descriptions, tags, and ownership
        Example: Bulk-update owner information during team reorganization
"""
```

## Client Module Checklist

For each client module (`_entity.py`, `_glossary.py`, etc.), ensure:

- [ ] Module docstring with purpose, features, examples
- [ ] Class docstring with capabilities, authentication, rate limits
- [ ] Every public method has comprehensive docstring
- [ ] All parameters documented with types, constraints, examples
- [ ] Return values document nested structure
- [ ] All exceptions documented with conditions
- [ ] Realistic, runnable examples provided
- [ ] Use cases explain when to use the method
- [ ] Cross-references to related methods

## MCP Server Integration

### Exposing Client Methods as MCP Tools

The MCP server exposes client methods as tools. For effective LLM use:

1. **Tool Name**: Clear, verb-based (e.g., "search_entities", "create_glossary_term")
2. **Tool Description**: One-line summary from method docstring
3. **Input Schema**: JSON schema derived from parameter documentation
4. **Examples**: Copied from method docstrings

Example tool definition:

```python
Tool(
    name="search_entities",
    description="Search for entities by query, type, or classification",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (wildcards supported: *)"
            },
            "entity_type": {
                "type": "string",
                "description": "Entity type filter (e.g., 'DataSet', 'azure_sql_table')"
            },
            "classification": {
                "type": "string",
                "description": "Classification filter (e.g., 'PII', 'Confidential')"
            },
            "limit": {
                "type": "integer",
                "description": "Max results (1-1000, default: 100)",
                "minimum": 1,
                "maximum": 1000,
                "default": 100
            }
        },
        "required": ["query"]
    }
)
```

## Documentation Workflow

### For New Methods
1. Write method implementation
2. Add comprehensive docstring following this guide
3. Test method with real API calls
4. Update examples with actual results
5. Cross-reference related methods
6. Update module-level documentation

### For Existing Methods
1. Review current docstring
2. Add missing sections (Args, Returns, Raises, Example, Use Cases)
3. Document all parameters with types and constraints
4. Add realistic examples from testing
5. Document return value structure in detail
6. List all possible exceptions

### For MCP Server
1. Review all exposed tools in `server.py`
2. Ensure underlying client methods are documented
3. Tool descriptions match method docstrings
4. Input schemas match parameter documentation
5. Add examples to MCP tool definitions

## Tools for Documentation

### Generating API Reference
```powershell
# Extract docstrings and generate markdown
python scripts/generate_api_docs.py

# Output: doc/reference/api/entity.md, glossary.md, etc.
```

### Validating Documentation
```python
# Check for missing docstrings
python scripts/validate_docs.py

# Output: List of methods without comprehensive docs
```

### Testing Examples
```python
# Run docstring examples as tests
python -m doctest purviewcli/client/_entity.py -v
```

## Best Practices Summary

✅ **DO:**
- Write clear, concise one-line summaries
- Document all parameters with types and constraints
- Provide realistic, runnable examples
- Explain use cases and when to use methods
- Document error conditions explicitly
- Use consistent formatting and structure
- Cross-reference related methods

❌ **DON'T:**
- Use vague descriptions like "does stuff"
- Omit parameter types or constraints
- Provide toy examples that don't run
- Forget to document exceptions
- Use inconsistent formatting
- Leave nested structures unexplained
- Assume readers know your domain

## Example: Well-Documented Method

```python
async def assign_term_to_entities(
    self, 
    term_guid: str, 
    entity_guids: List[str],
    relationship_type: str = "ASSIGNED"
) -> Dict[str, Any]:
    """
    Assign a glossary term to one or more entities for business context tagging.
    
    Creates relationships between a glossary term and entities, enabling:
    - Business terminology consistency
    - Data discovery by business terms
    - Governance policy application
    - Semantic layer construction
    
    Args:
        term_guid: GUID of the glossary term to assign.
                  Must be an existing, approved term.
                  Example: "550e8400-e29b-41d4-a716-446655440000"
                  
        entity_guids: List of entity GUIDs to tag with the term.
                     Each must be an existing entity GUID.
                     Supports bulk assignment (up to 1000 entities).
                     Example: ["guid1", "guid2", "guid3"]
                     
        relationship_type: Type of term-entity relationship.
                          Valid values: "ASSIGNED" (default), "SUGGESTED"
                          - ASSIGNED: Formal, approved assignment
                          - SUGGESTED: Recommended by system/user
                          
    Returns:
        Dictionary containing assignment results:
            {
                "term_guid": str,              # Assigned term GUID
                "assigned_count": int,         # Successfully assigned
                "failed_count": int,           # Failed assignments
                "assignments": [               # Per-entity results
                    {
                        "entity_guid": str,    # Target entity
                        "status": str,         # "SUCCESS" or "FAILED"
                        "message": str,        # Error message if failed
                        "relationship_guid": str  # Relationship ID if success
                    }
                ]
            }
            
    Raises:
        ValueError: When inputs are invalid:
            - term_guid is None or empty
            - entity_guids is empty list
            - relationship_type not in valid values
            
        AuthenticationError: When credentials are invalid
        
        HTTPError: When Purview API returns error:
            - 400: Invalid GUID format
            - 404: Term or entity not found
            - 409: Assignment already exists
            - 429: Rate limit exceeded (>100 assignments/minute)
            
    Example:
        # Assign "Customer Data" term to entities
        client = GlossaryClient()
        
        term_guid = "550e8400-e29b-41d4-a716-446655440000"
        entities = [
            "customer_table_guid",
            "orders_table_guid",
            "sales_view_guid"
        ]
        
        result = await client.assign_term_to_entities(
            term_guid=term_guid,
            entity_guids=entities,
            relationship_type="ASSIGNED"
        )
        
        print(f"Assigned to {result['assigned_count']} entities")
        
        # Check failures
        for assignment in result['assignments']:
            if assignment['status'] == 'FAILED':
                print(f"Failed: {assignment['entity_guid']} - {assignment['message']}")
                
    Use Cases:
        - Data Catalog Enrichment: Tag tables with business terms for discovery
        - Compliance Tagging: Mark PII/sensitive data with appropriate terms
        - Semantic Layer: Build business-friendly data dictionary
        - Governance Policies: Apply policies based on term assignments
        - Data Quality: Track data quality metrics by business term
    """
```

## Resources

- [Microsoft Purview REST API Reference](https://learn.microsoft.com/en-us/rest/api/purview/)
- [Python Docstring Conventions (PEP 257)](https://peps.python.org/pep-0257/)
- [Google Python Style Guide - Docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
