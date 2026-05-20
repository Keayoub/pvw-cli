# SPDX-License-Identifier: Apache-2.0

"""
FastMCP Server for Microsoft Purview CLI

This server provides the same comprehensive access to Microsoft Purview operations
but with cleaner code, automatic validation, and better developer experience.

"""

import inspect
import logging
import os
import re
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from tools.microsoft_learn_tools import register_microsoft_learn_tools

# Add parent directory to path to import purviewcli
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.client.api_client import PurviewClient, PurviewConfig
from purviewcli.client import (
    Entity,
    Glossary,
    UnifiedCatalogClient,
    Collections,
    Lineage,
    Search,
    Types,
    Relationship,
)

# Initialize FastMCP
mcp = FastMCP(
    "purview-mcp-server",
    instructions="""
# Microsoft Purview MCP Server - Usage Guidelines

You are interacting with the Microsoft Purview MCP Server, providing comprehensive access to Microsoft Purview's data governance and catalog capabilities. Follow these guidelines to maximize effectiveness.

## Core Capabilities

### 1. Data Catalog Management (Entity Operations)
- **Create, Read, Update, Delete entities** (datasets, tables, processes, columns)
- **Bulk operations** - Import/export entities from CSV files with templates
- **Entity types**: DataSet, azure_sql_table, azure_datalake_gen2_path, Process, Column
- **Classifications & Labels** - Add PII, Confidential, and custom tags
- **Business Metadata** - Attach custom business context to entities

### 2. Business Glossary (Glossary Operations)
- **Manage business terminology** - Create terms, categories, hierarchies
- **Term relationships** - Related terms, synonyms, acronyms
- **Bulk import** - Import glossary terms from CSV files
- **Term assignments** - Link glossary terms to entities and columns

### 3. Unified Catalog (Modern Governance Features)
- **Governance Domains** - Organizational contexts for data assets (86% API coverage)
- **Data Products** - Curated data asset collections with lifecycle tracking
- **Business Metadata Terms** - Business vocabulary with full metadata
- **Business Metadata Cleanup** - List metadata defs, resolve attribute names, cleanup/delete definitions, remove asset assignments
- **Objectives & Key Results (OKRs)** - Data governance goal tracking
- **Critical Data Elements (CDEs)** - Important data element definitions
- **Policies** - Governance and RBAC policies management
- **Relationships** - Link data products/CDEs/terms to entities
- **Query APIs** - Advanced OData filtering with multi-criteria search

### 4. Data Lineage
- **Trace data flow** - Upstream and downstream lineage analysis
- **Create lineage** - Define process entities with inputs/outputs
- **CSV Import** - Bulk lineage creation from CSV files
- **Impact analysis** - Understand data dependencies

### 5. Search & Discovery
- **Keyword search** - Find entities across the catalog
- **Faceted search** - Filter by type, classification, collection
- **Autocomplete & Suggest** - Search suggestions for entity discovery
- **Browse catalog** - Navigate by entity type and hierarchy

### 6. Collections & Account
- **Collection hierarchy** - Organize assets in collections
- **Access management** - Collection-based permissions
- **Account properties** - Get Purview account configuration

## Best Practices

### Entity Operations
1. **Always use qualifiedName for updates** - It's the unique identifier
   - Format varies by type: `mssql://server/db/schema/table`, `https://account.dfs.core.windows.net/container/path/`
2. **Specify typeName** - Required for entity creation (e.g., `DataSet`, `azure_sql_table`)
3. **Use batch operations for bulk work** - More efficient than individual calls
4. **Preview with dry-run** - Test CSV imports before applying changes
5. **Use appropriate batch sizes**:
   - Small (< 100 entities): 50-100
   - Medium (100-1000): 100-200
   - Large (> 1000): 200-500

### Glossary Terms
1. **Create hierarchies** - Use parent-child relationships for term organization
2. **Add rich metadata** - Include acronyms, resources, contacts for context
3. **Link to entities** - Connect terms to data assets for discoverability
4. **Use status workflow** - Draft → Approved → Alert → Expired

### Unified Catalog Operations
1. **Start with domains** - Organize governance by business domain
2. **Use business metadata terms** - Create standardized vocabulary
3. **Define data products** - Curate and track data asset collections
4. **Link relationships** - Connect data products/CDEs to physical entities
5. **Query with filters** - Use advanced OData queries for precise searches
6. **Manage policies** - Define governance and RBAC policies

### Lineage Creation
1. **Use Process entities** - Represent ETL jobs, transformations, pipelines
2. **Define inputs and outputs** - Link source entities to target entities
3. **Include meaningful names** - Process names should describe the transformation
4. **CSV import for bulk** - Efficient for creating multiple lineage relationships
5. **Validate lineage paths** - Ensure entities exist before creating lineage

### Search & Discovery
1. **Start broad, then filter** - Use keyword search + filters for precision
2. **Use entity types for scoping** - Filter by DataSet, Table, Column, etc.
3. **Leverage classifications** - Find PII, Confidential data by classification
4. **Browse for exploration** - Use browse API for hierarchical navigation

### CSV Bulk Operations
1. **Use templates** - Predefined CSV structures for common operations
   - `basic` - Basic entity attributes
   - `etl` - ETL process entities
   - `column-mapping` - Column-level mapping
2. **Validate before import** - Check CSV format matches template
3. **Use error handling** - Save failed rows to error CSV for retry
4. **Test with small batches first** - Validate logic before full import

## Common Workflows

### Workflow 1: Catalog New Data Source
```
1. search_entities - Check if assets already exist
2. create_entity or batch_create_entities - Register data assets
3. create_glossary_term (if needed) - Define business terms
4. assign_term_to_entities - Link terms to entities
5. create_lineage (if applicable) - Define data flow
```

### Workflow 2: Build Business Glossary
```
1. uc_create_domain - Create governance domain
2. uc_create_term - Add business metadata terms
3. search_entities - Find related data assets
4. Assign terms to entities via relationships
```

### Workflow 3: Implement Data Governance
```
1. uc_list_domains - Review existing domains
2. uc_create_domain (if needed) - Create new domain
3. uc_create_term - Define governance terminology
4. uc_policy_create - Define governance policies
5. uc_dataproduct_create - Curate data products
6. Link relationships to physical entities
```

### Workflow 4: Data Discovery
```
1. search_entities - Keyword search
2. search_browse - Browse by type hierarchy
3. get_entity - Get detailed entity information
4. get_lineage - Understand data flow
5. get_glossary_terms - View assigned terms
```

### Workflow 5: Bulk Data Onboarding
```
1. Prepare CSV with entity data
2. import_entities_from_csv - Preview with dry-run
3. import_entities_from_csv - Execute import
4. import_lineage_from_csv (if applicable) - Add lineage
5. Export results for validation
```

## Entity Type Reference

### Common Entity Types
- **DataSet** - Generic dataset/file
- **azure_sql_table** - Azure SQL table
- **azure_sql_column** - Azure SQL column
- **azure_datalake_gen2_path** - ADLS Gen2 folder/file
- **azure_datalake_gen2_resource_set** - ADLS Gen2 resource set
- **Process** - ETL job, transformation, pipeline
- **Column** - Generic column
- **ColumnLineage** - Column-level lineage

### QualifiedName Patterns
- **SQL**: `mssql://server.database.windows.net/database/schema/table`
- **ADLS Gen2**: `https://account.dfs.core.windows.net/container/path/to/file`
- **Generic**: `//source/path/to/asset@account`

## Advanced Features

### Business Metadata
- Use `add_or_update_business_metadata` for custom attributes
- Supported scopes: Entity, Column, Classification
- Proper applicableEntityTypes configuration required

### Custom Attributes
- Create extensible attribute definitions
- Define custom properties for UC resources
- Use for organization-specific metadata

### Relationships API
- Link data products to physical entities
- Connect CDEs to columns with qualified names
- Create associations between UC and Atlas resources

### Query APIs
- Advanced OData filtering: `$filter`, `$top`, `$skip`
- Multi-criteria searches across resources
- Pagination support for large result sets

## Error Handling

### Common Issues
1. **404 Not Found** - Entity/term doesn't exist, check GUID/ID
2. **400 Bad Request** - Invalid payload, check required fields
3. **403 Forbidden** - Insufficient permissions, check RBAC
4. **409 Conflict** - Entity already exists, use update instead
5. **429 Too Many Requests** - Rate limited, reduce batch size

### Recovery Strategies
- Use error CSV files to track failed operations
- Retry with smaller batch sizes
- Validate entity existence before updates
- Check RBAC permissions for operations

## Output Formats

- **JSON** - Structured data for programmatic processing
- **JSONC** - JSON with comments for readability
- **Table** - Human-readable console output
- **CSV** - Bulk data export for Excel/analysis

## API Coverage

The server provides 86% coverage of Purview Unified Catalog APIs (45/52 operations):
- ✅ Business Domains: 100% (5/5)
- ✅ Data Products: 90% (9/10)
- ✅ Glossary Terms: 73% (8/11)
- ✅ OKRs: 92% (11/12)
- ✅ CDEs: 90% (9/10)
- ✅ Policies: 100% (5/5)
- ✅ Relationships: 100% (6/6)
- ✅ Query: 100% (4/4)
- ✅ Custom Metadata: 100% (5/5)
- ✅ Custom Attributes: 100% (5/5)

## Tips for LLM Usage

1. **Chain operations** - Combine search → get → update workflows
2. **Use bulk operations** - More efficient than individual calls
3. **Validate assumptions** - Check entity existence before operations
4. **Leverage search first** - Discover before creating duplicates
5. **Use UC for modern governance** - Unified Catalog provides richer features
6. **Preview with dry-run** - Always test bulk operations first
7. **Export for analysis** - Use CSV exports for data validation
8. **Follow naming conventions** - Consistent qualifiedNames for reliability

## Microsoft Learn Integration

The server includes Microsoft Learn documentation tools:
- `search_learn_microsoft_content` - Search official docs
- `get_learn_microsoft_content` - Get specific documentation
- `get_learn_microsoft_modules` - Browse learning modules
- `get_learn_microsoft_paths` - Explore learning paths

Use these to supplement Purview operations with official Microsoft guidance.

## Authentication

Set these environment variables:
- `PURVIEW_ACCOUNT_NAME` - Your Purview account name (required)
- `AZURE_TENANT_ID` - Azure tenant ID (optional)
- `AZURE_REGION` - Azure region for special clouds (optional)
- `PURVIEW_MAX_RETRIES` - Max retry attempts (default: 3)
- `PURVIEW_TIMEOUT` - Request timeout in seconds (default: 30)
- `PURVIEW_BATCH_SIZE` - Default batch size (default: 100)

The client uses Azure DefaultAzureCredential for authentication (supports Azure CLI, Service Principal, Managed Identity).

---

For detailed documentation, refer to the comprehensive guides in the `doc/` folder of the Purview CLI repository.
"""
)

# Global client instance
_purview_client: Optional[PurviewClient] = None


# Pydantic Models for Request Validation
class EntityRequest(BaseModel):
    """Request model for entity operations"""
    entity_data: Dict[str, Any] = Field(..., description="Entity data with typeName and attributes")


class SearchRequest(BaseModel):
    """Request model for search operations"""
    query: str = Field(..., description="Search query string")
    filter: Optional[Dict[str, Any]] = Field(None, description="Optional filter criteria")
    limit: int = Field(50, description="Maximum number of results")
    offset: int = Field(0, description="Offset for pagination")


class LineageRequest(BaseModel):
    """Request model for lineage operations"""
    guid: str = Field(..., description="Entity GUID")
    direction: str = Field("BOTH", description="Lineage direction: INPUT, OUTPUT, or BOTH")
    depth: int = Field(3, description="Lineage depth")


class UCDomainRequest(BaseModel):
    """Request model for UC domain creation"""
    name: str = Field(..., description="Domain name")
    description: Optional[str] = Field(None, description="Domain description")
    owner_id: str = Field(..., description="Owner Entra Object ID")


class UCTermRequest(BaseModel):
    """Request model for UC term creation"""
    name: str = Field(..., description="Term name")
    definition: str = Field(..., description="Term definition")
    owner_id: str = Field(..., description="Owner Entra Object ID")
    parent_term_id: Optional[str] = Field(None, description="Parent term ID")
    description: Optional[str] = Field(None, description="Additional description")


# Helper Functions
def get_config() -> PurviewConfig:
    """Get Purview configuration from environment variables"""
    account_name = os.getenv("PURVIEW_ACCOUNT_NAME")
    if not account_name:
        raise ValueError("PURVIEW_ACCOUNT_NAME environment variable is required")

    return PurviewConfig(
        account_name=account_name,
        tenant_id=os.getenv("AZURE_TENANT_ID"),
        azure_region=os.getenv("AZURE_REGION"),
        max_retries=int(os.getenv("PURVIEW_MAX_RETRIES", "3")),
        timeout=int(os.getenv("PURVIEW_TIMEOUT", "30")),
        batch_size=int(os.getenv("PURVIEW_BATCH_SIZE", "100")),
    )


@mcp.tool()
def get_prompt_instructions() -> str:
    """
    Return the curated prompt instructions to guide LLMs when calling the Purview MCP Server.

    This reads `prompt_instructions.md` distributed with the server tools and returns its
    contents as a string so remote agents can fetch guidance programmatically.
    """
    try:
        root = Path(__file__).parent
        prompt_file = root / "prompt_instructions.md"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return """
        Prompt instructions file not found. Please ensure `prompt_instructions.md` is present
        in the PurviewMCPServer tools directory.
        """
    except Exception as e:
        logging.exception("Failed to read prompt instructions")
        return f"Error reading prompt instructions: {e}"


async def get_client() -> PurviewClient:
    """Get or initialize Purview client"""
    global _purview_client
    if _purview_client is None:
        config = get_config()
        _purview_client = PurviewClient(config)
        await _purview_client.__aenter__()
    return _purview_client


# ============================================================================
# ENTITY OPERATIONS
# ============================================================================

@mcp.tool()
async def get_entity(guid: str) -> Dict[str, Any]:
    """
    Get a Purview entity by GUID.
    
    Returns entity details including attributes, classifications, and relationships.
    
    Args:
        guid: The unique GUID of the entity
        
    Returns:
        Entity details with all metadata
    """
    client = await get_client()
    return await client.get_entity(guid)


@mcp.tool()
async def create_entity(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new entity in Purview catalog.
    
    Args:
        entity_data: Entity data with typeName and attributes
        
    Returns:
        Created entity with assigned GUID
    """
    client = await get_client()
    return await client.create_entity(entity_data)


@mcp.tool()
async def update_entity(entity_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing entity in Purview catalog.
    
    Args:
        entity_data: Entity data with guid and updated attributes
        
    Returns:
        Updated entity details
    """
    client = await get_client()
    return await client.update_entity(entity_data)


@mcp.tool()
async def delete_entity(guid: str) -> Dict[str, Any]:
    """
    Delete an entity from Purview catalog by GUID.
    
    Args:
        guid: The unique GUID of the entity to delete
        
    Returns:
        Deletion confirmation
    """
    client = await get_client()
    return await client.delete_entity(guid)


@mcp.tool()
async def search_entities(
    query: str,
    filter: Optional[Dict[str, Any]] = None,
    limit: int = 50,
    offset: int = 0
) -> Dict[str, Any]:
    """
    Search for entities in Purview catalog.
    
    Supports keyword search with filters and facets.
    
    Args:
        query: Search query string (keywords)
        filter: Optional filter criteria
        limit: Maximum number of results (default: 50)
        offset: Offset for pagination (default: 0)
        
    Returns:
        Search results with matching entities
    """
    client = await get_client()
    return await client.search_entities(query=query, filter=filter, limit=limit, offset=offset)


@mcp.tool()
async def batch_create_entities(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create multiple entities in batches.
    
    Efficient for bulk operations.
    
    Args:
        entities: Array of entity data objects
        
    Returns:
        Batch creation results
    """
    client = await get_client()
    return await client.batch_create_entities(entities)


@mcp.tool()
async def batch_update_entities(entities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Update multiple entities in batches.
    
    Efficient for bulk operations.
    
    Args:
        entities: Array of entity data objects with guids
        
    Returns:
        Batch update results
    """
    client = await get_client()
    return await client.batch_update_entities(entities)


# ============================================================================
# LINEAGE OPERATIONS
# ============================================================================

@mcp.tool()
async def get_lineage(
    guid: str,
    direction: str = "BOTH",
    depth: int = 3
) -> Dict[str, Any]:
    """
    Get lineage information for an entity.
    
    Shows upstream and downstream relationships.
    
    Args:
        guid: Entity GUID to get lineage for
        direction: Lineage direction: INPUT, OUTPUT, or BOTH
        depth: Lineage depth (default: 3)
        
    Returns:
        Lineage graph with related entities
    """
    client = await get_client()
    return await client.get_lineage(guid=guid, direction=direction, depth=depth)


@mcp.tool()
async def create_lineage(lineage_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a lineage relationship between entities.
    
    Args:
        lineage_data: Lineage relationship data
        
    Returns:
        Created lineage relationship
    """
    client = await get_client()
    return await client.create_lineage(lineage_data)


# ============================================================================
# COLLECTION OPERATIONS
# ============================================================================

@mcp.tool()
async def list_collections() -> Dict[str, Any]:
    """
    List all collections in the Purview account.
    
    Returns:
        List of all collections with metadata
    """
    client = await get_client()
    return await client.list_collections()


@mcp.tool()
async def get_collection(collection_name: str) -> Dict[str, Any]:
    """
    Get details of a specific collection by name.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection details
    """
    client = await get_client()
    return await client.get_collection(collection_name)


@mcp.tool()
async def create_collection(
    collection_name: str,
    collection_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a new collection in Purview.
    
    Args:
        collection_name: Name for the new collection
        collection_data: Collection data with friendlyName, description, parentCollection
        
    Returns:
        Created collection details
    """
    client = await get_client()
    return await client.create_collection(collection_name, collection_data)


@mcp.tool()
async def delete_collection(collection_name: str) -> Dict[str, Any]:
    """
    Delete a collection from Purview.
    
    Args:
        collection_name: Name of the collection to delete
        
    Returns:
        Deletion confirmation
    """
    client = await get_client()
    return await client.delete_collection(collection_name)


@mcp.tool()
async def get_collection_path(collection_name: str) -> Dict[str, Any]:
    """
    Get the hierarchical path of a collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Collection path hierarchy
    """
    client = await get_client()
    return await client.get_collection_path(collection_name)


# ============================================================================
# GLOSSARY OPERATIONS
# ============================================================================

@mcp.tool()
async def get_glossary_terms(glossary_guid: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all glossary terms or terms from a specific glossary.
    
    Args:
        glossary_guid: Optional GUID of a specific glossary
        
    Returns:
        List of glossary terms
    """
    client = await get_client()
    return await client.get_glossary_terms(glossary_guid)


@mcp.tool()
async def create_glossary_term(term_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new glossary term.
    
    Args:
        term_data: Glossary term data with name, description, etc.
        
    Returns:
        Created glossary term
    """
    client = await get_client()
    return await client.create_glossary_term(term_data)


@mcp.tool()
async def assign_term_to_entities(
    term_guid: str,
    entity_guids: List[str]
) -> Dict[str, Any]:
    """
    Assign a glossary term to multiple entities.
    
    Args:
        term_guid: GUID of the glossary term
        entity_guids: Array of entity GUIDs to assign the term to
        
    Returns:
        Assignment results
    """
    client = await get_client()
    return await client.assign_term_to_entities(term_guid, entity_guids)


# ============================================================================
# UNIFIED CATALOG OPERATIONS (Business Metadata)
# ============================================================================

def _mcp_extract_error_message(response: Any) -> str:
    """Extract a readable error message from varied API response shapes."""
    if not isinstance(response, dict):
        return "Unknown error"

    for key in ("message", "errorMessage", "error", "detail"):
        value = response.get(key)
        if isinstance(value, str) and value.strip():
            return value

    data = response.get("data")
    if isinstance(data, dict):
        for key in ("message", "errorMessage", "error", "detail"):
            value = data.get(key)
            if isinstance(value, str) and value.strip():
                return value

    return "Unknown error"


def _mcp_resolve_business_metadata_definition_name(name: str) -> Dict[str, Any]:
    """Resolve a user-provided name to a business metadata definition name."""
    uc_client = UnifiedCatalogClient()
    response = uc_client.list_custom_metadata({})

    groups = []
    if isinstance(response, dict):
        groups = response.get("businessMetadataDefs", []) or []

    name_lower = name.lower()

    # Exact definition match
    for group in groups:
        group_name = group.get("name")
        if isinstance(group_name, str) and group_name.lower() == name_lower:
            return {
                "resolved_name": group_name,
                "resolution_type": "definition",
                "note": None,
            }

    # Attribute-name match
    matched_groups: List[str] = []
    for group in groups:
        group_name = group.get("name")
        for attr in group.get("attributeDefs", []) or []:
            attr_name = attr.get("name")
            if isinstance(attr_name, str) and attr_name.lower() == name_lower and group_name:
                matched_groups.append(group_name)

    unique_groups = sorted(set(matched_groups))
    if len(unique_groups) == 1:
        resolved_name = unique_groups[0]
        return {
            "resolved_name": resolved_name,
            "resolution_type": "attribute",
            "note": f"Resolved attribute '{name}' to business metadata definition '{resolved_name}'",
        }

    if len(unique_groups) > 1:
        groups_str = ", ".join(unique_groups)
        raise ValueError(
            f"Attribute name '{name}' exists in multiple definitions: {groups_str}. "
            "Use the definition name instead."
        )

    return {
        "resolved_name": name,
        "resolution_type": "none",
        "note": None,
    }


def _mcp_delete_business_metadata_definition(types_client: Types, name: str) -> Dict[str, Any]:
    """Delete business metadata definition with robust endpoint fallback."""
    args = {"--name": name}

    # Primary path for Business Metadata definitions.
    response = types_client.deleteBusinessMetadataDef(args)
    if not (isinstance(response, dict) and response.get("status") == "error"):
        return response

    # Fallback to typedef delete-by-name in case endpoint behavior differs.
    message = _mcp_extract_error_message(response).lower()
    if any(token in message for token in ("not found", "invalid", "unsupported", "method", "404", "405")):
        return types_client.typesDeleteDef(args)

    return response


@mcp.tool()
def uc_list_custom_metadata_defs() -> Dict[str, Any]:
    """List business metadata definitions and attributes."""
    uc_client = UnifiedCatalogClient()
    return uc_client.list_custom_metadata({})


@mcp.tool()
def uc_delete_metadata_from_asset(asset_id: str, group: str) -> Dict[str, Any]:
    """Remove a business metadata group assignment from a specific asset."""
    uc_client = UnifiedCatalogClient()
    args = {
        "--asset-id": [asset_id],
        "--group": [group],
    }
    response = uc_client.delete_custom_metadata(args)
    return {
        "status": "success",
        "asset_id": asset_id,
        "group": group,
        "response": response,
    }


@mcp.tool()
def uc_delete_metadata_definition(
    name: str,
    dry_run: bool = False,
    resolve_attribute_name: bool = True,
) -> Dict[str, Any]:
    """Delete a business metadata definition by name.

    If resolve_attribute_name is true, an attribute name can be provided and will
    be resolved to its parent definition when unambiguous.
    """
    resolved_name = name
    resolution_note = None
    if resolve_attribute_name:
        resolution = _mcp_resolve_business_metadata_definition_name(name)
        resolved_name = resolution["resolved_name"]
        resolution_note = resolution.get("note")

    if dry_run:
        return {
            "status": "dry-run",
            "input_name": name,
            "resolved_name": resolved_name,
            "note": resolution_note,
            "message": "Would delete business metadata definition",
        }

    types_client = Types()
    response = _mcp_delete_business_metadata_definition(types_client, resolved_name)

    if isinstance(response, dict) and response.get("status") == "error":
        return {
            "status": "error",
            "input_name": name,
            "resolved_name": resolved_name,
            "note": resolution_note,
            "message": _mcp_extract_error_message(response),
            "raw": response,
        }

    return {
        "status": "success",
        "input_name": name,
        "resolved_name": resolved_name,
        "note": resolution_note,
        "response": response,
    }


@mcp.tool()
def uc_cleanup_metadata_definition(
    name: str,
    check_only: bool = False,
    dry_run: bool = False,
    resolve_attribute_name: bool = True,
) -> Dict[str, Any]:
    """Safely cleanup a business metadata definition.

    Flow:
    1) Resolve name (optionally from attribute to definition)
    2) Verify definition exists/readable
    3) Optionally delete when not check-only/dry-run
    """
    resolved_name = name
    resolution_note = None
    if resolve_attribute_name:
        resolution = _mcp_resolve_business_metadata_definition_name(name)
        resolved_name = resolution["resolved_name"]
        resolution_note = resolution.get("note")

    types_client = Types()

    read_args = {"--name": resolved_name}
    definition = types_client.typesReadBusinessMetadataDefByName(read_args)
    if isinstance(definition, dict) and definition.get("status") == "error":
        return {
            "status": "error",
            "input_name": name,
            "resolved_name": resolved_name,
            "note": resolution_note,
            "message": _mcp_extract_error_message(definition),
            "raw": definition,
        }

    if check_only:
        return {
            "status": "check-only",
            "input_name": name,
            "resolved_name": resolved_name,
            "note": resolution_note,
            "message": "Definition exists and delete was not executed",
            "definition": definition,
        }

    if dry_run:
        return {
            "status": "dry-run",
            "input_name": name,
            "resolved_name": resolved_name,
            "note": resolution_note,
            "message": "Would attempt cleanup delete",
        }

    delete_response = _mcp_delete_business_metadata_definition(types_client, resolved_name)
    if isinstance(delete_response, dict) and delete_response.get("status") == "error":
        message = _mcp_extract_error_message(delete_response)
        message_lower = message.lower()
        blocked = any(
            token in message_lower
            for token in ("reference", "referenced", "in use", "assigned", "constraint")
        )
        return {
            "status": "blocked" if blocked else "error",
            "input_name": name,
            "resolved_name": resolved_name,
            "note": resolution_note,
            "message": message,
            "raw": delete_response,
        }

    return {
        "status": "success",
        "input_name": name,
        "resolved_name": resolved_name,
        "note": resolution_note,
        "response": delete_response,
    }

@mcp.tool()
def uc_list_domains() -> Dict[str, Any]:
    """
    List all governance domains in the Unified Catalog.
    
    Domains organize business terms hierarchically.
    
    Returns:
        List of governance domains
    """
    uc_client = UnifiedCatalogClient()
    return uc_client.get_governance_domains({})


@mcp.tool()
def uc_get_domain(domain_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific governance domain by ID.
    
    Args:
        domain_id: The unique ID of the governance domain
        
    Returns:
        Governance domain details
    """
    uc_client = UnifiedCatalogClient()
    return uc_client.get_governance_domain_by_id({"--domain-id": domain_id})


@mcp.tool()
def uc_create_domain(
    name: str,
    description: Optional[str] = None,
    owner_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new governance domain in the Unified Catalog.
    
    For organizing business terms.
    
    Args:
        name: Domain name
        description: Domain description
        owner_id: Owner Entra Object ID
        
    Returns:
        Created governance domain
    """
    uc_client = UnifiedCatalogClient()
    args = {
        "--name": name,
        "--description": description,
        "--owner-id": owner_id,
    }
    return uc_client.create_governance_domain(args)


@mcp.tool()
def uc_list_terms(domain_id: str) -> Dict[str, Any]:
    """
    List all business metadata terms in a governance domain.
    
    Terms define standardized business vocabulary.
    
    Args:
        domain_id: The governance domain ID to list terms from
        
    Returns:
        List of business metadata terms
    """
    uc_client = UnifiedCatalogClient()
    return uc_client.get_terms({"--governance-domain-id": [domain_id]})


@mcp.tool()
def uc_get_term(domain_id: str, term_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific business metadata term.
    
    Args:
        domain_id: The governance domain ID
        term_id: The term ID
        
    Returns:
        Business metadata term details
    """
    uc_client = UnifiedCatalogClient()
    args = {
        "--governance-domain-id": domain_id,
        "--term-id": term_id,
    }
    return uc_client.get_term_by_id(args)


@mcp.tool()
def uc_create_term(
    domain_id: str,
    name: str,
    definition: str,
    owner_id: str,
    parent_term_id: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new business metadata term in a governance domain.
    
    Args:
        domain_id: The governance domain ID
        name: Term name
        definition: Term definition
        owner_id: Owner Entra Object ID
        parent_term_id: Optional parent term ID for hierarchy
        description: Optional additional description
        
    Returns:
        Created business metadata term
    """
    uc_client = UnifiedCatalogClient()
    args = {
        "--governance-domain-id": domain_id,
        "--name": name,
        "--definition": definition,
        "--owner-id": owner_id,
    }
    if parent_term_id:
        args["--parent-term-id"] = parent_term_id
    if description:
        args["--description"] = description
    return uc_client.create_term(args)


@mcp.tool()
def uc_search_terms(search_query: str, limit: int = 50) -> Dict[str, Any]:
    """
    Search for business metadata terms across all domains.
    
    Uses keyword query.
    
    Args:
        search_query: Search query string (keywords to find in term names/definitions)
        limit: Maximum number of results (default: 50)
        
    Returns:
        Search results with matching terms
    """
    # Use general search for now - UC doesn't have dedicated term search yet
    uc_client = UnifiedCatalogClient()
    # Get all terms and filter locally
    all_terms = uc_client.get_terms({"--governance-domain-id": [""]})
    
    # Simple keyword matching
    if isinstance(all_terms, dict) and 'value' in all_terms:
        terms = all_terms['value']
        filtered = [
            t for t in terms
            if search_query.lower() in t.get('name', '').lower() 
            or search_query.lower() in t.get('definition', '').lower()
        ]
        return {"value": filtered[:limit], "count": len(filtered)}
    
    return all_terms


# ============================================================================
# ADVANCED SEARCH OPERATIONS
# ============================================================================

@mcp.tool()
def search_suggest(keywords: str, limit: int = 5) -> Dict[str, Any]:
    """
    Get search suggestions/autocomplete for a query string.
    
    Useful for building search UIs.
    
    Args:
        keywords: Partial keyword string for autocomplete
        limit: Maximum number of suggestions (default: 5)
        
    Returns:
        Search suggestions
    """
    search_client = Search()
    args = {
        "--keywords": keywords,
        "--limit": limit,
    }
    return search_client.searchSuggest(args)


@mcp.tool()
def search_browse(
    entity_type: str,
    path: Optional[str] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Browse the Purview catalog by entity type.
    
    Returns aggregated counts by type, classification, etc.
    
    Args:
        entity_type: Entity type to browse (e.g., 'DataSet', 'azure_sql_table')
        path: Browse path for hierarchical navigation
        limit: Maximum results (default: 50)
        
    Returns:
        Browse results with aggregations
    """
    search_client = Search()
    args = {
        "--entityType": entity_type,
        "--path": path,
        "--limit": limit,
    }
    return search_client.searchBrowse(args)


# ============================================================================
# TYPE DEFINITION OPERATIONS
# ============================================================================

@mcp.tool()
def get_typedef(type_name: str) -> Dict[str, Any]:
    """
    Get type definition by name.
    
    Returns entity type schema including attributes and relationships.
    
    Args:
        type_name: Name of the type (e.g., 'DataSet', 'azure_sql_table')
        
    Returns:
        Type definition schema
    """
    types_client = Types()
    args = {"--name": type_name}
    return types_client.typesRead(args)


@mcp.tool()
def list_typedefs(type_category: Optional[str] = None) -> Dict[str, Any]:
    """
    List all type definitions in Purview.
    
    Optionally filter by type category.
    
    Args:
        type_category: Optional filter: entity, classification, relationship, enum
        
    Returns:
        List of type definitions
    """
    types_client = Types()
    args = {"--type": type_category}
    return types_client.typesList(args)


# ============================================================================
# RELATIONSHIP OPERATIONS
# ============================================================================

@mcp.tool()
def create_relationship(relationship_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a relationship between two entities.
    
    E.g., parent-child, lineage.
    
    Args:
        relationship_data: Relationship data with typeName, end1 (entity GUID), end2 (entity GUID)
        
    Returns:
        Created relationship
    """
    relationship_client = Relationship()
    args = {
        "--typeName": relationship_data.get("typeName"),
        "--end1": relationship_data.get("end1"),
        "--end2": relationship_data.get("end2"),
    }
    return relationship_client.relationshipCreate(args)


@mcp.tool()
def get_relationship(relationship_guid: str) -> Dict[str, Any]:
    """
    Get relationship details by GUID.
    
    Args:
        relationship_guid: The relationship GUID
        
    Returns:
        Relationship details
    """
    relationship_client = Relationship()
    args = {"--guid": relationship_guid}
    return relationship_client.relationshipRead(args)


@mcp.tool()
def delete_relationship(relationship_guid: str) -> Dict[str, Any]:
    """
    Delete a relationship between entities.
    
    Args:
        relationship_guid: The relationship GUID to delete
        
    Returns:
        Deletion confirmation
    """
    relationship_client = Relationship()
    args = {"--guid": relationship_guid}
    return relationship_client.relationshipDelete(args)


# ============================================================================
# CSV OPERATIONS
# ============================================================================

@mcp.tool()
async def import_entities_from_csv(
    csv_file_path: str,
    mapping_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Import entities from a CSV file with mapping configuration.
    
    Args:
        csv_file_path: Path to the CSV file
        mapping_config: Mapping configuration for CSV columns to entity attributes
        
    Returns:
        Import results
    """
    client = await get_client()
    return await client.import_entities_from_csv(csv_file_path, mapping_config)


@mcp.tool()
async def export_entities_to_csv(
    query: str,
    csv_file_path: str,
    columns: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Export entities to a CSV file based on a search query.
    
    Args:
        query: Search query to find entities to export
        csv_file_path: Path for the output CSV file
        columns: Optional list of columns to include
        
    Returns:
        Export results
    """
    client = await get_client()
    return await client.export_entities_to_csv(query, csv_file_path, columns)


# ============================================================================
# ACCOUNT OPERATIONS
# ============================================================================

@mcp.tool()
async def get_account_properties() -> Dict[str, Any]:
    """
    Get properties of the Purview account.
    
    Returns:
        Account properties and configuration
    """
    client = await get_client()
    return await client.get_account_properties()


# ============================================================================
# OPERATION REGISTRY
# ============================================================================

_CLIENT_OPERATION_NAMESPACES = {
    "purview": {
        "label": "PurviewClient",
        "factory": None,
        "use_async_client": True,
    },
    "uc": {
        "label": "UnifiedCatalogClient",
        "factory": UnifiedCatalogClient,
        "use_async_client": False,
    },
    "collections": {
        "label": "Collections",
        "factory": Collections,
        "use_async_client": False,
    },
    "lineage": {
        "label": "Lineage",
        "factory": Lineage,
        "use_async_client": False,
    },
    "search": {
        "label": "Search",
        "factory": Search,
        "use_async_client": False,
    },
    "types": {
        "label": "Types",
        "factory": Types,
        "use_async_client": False,
    },
    "relationship": {
        "label": "Relationship",
        "factory": Relationship,
        "use_async_client": False,
    },
    "glossary": {
        "label": "Glossary",
        "factory": Glossary,
        "use_async_client": False,
    },
    "entity": {
        "label": "Entity",
        "factory": Entity,
        "use_async_client": False,
    },
}


def _to_snake_case(name: str) -> str:
    """Convert a method name to a stable tool-friendly snake_case name."""
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.replace("-", "_").lower()


def _summarize_docstring(docstring: Optional[str]) -> str:
    """Return the first line of a docstring or a fallback summary."""
    if not docstring:
        return "No description available."
    summary = docstring.strip().splitlines()[0].strip()
    return summary or "No description available."


def _get_call_style(method: Any) -> str:
    """Summarize how a client method accepts arguments."""
    parameters = list(inspect.signature(method).parameters.values())
    if not parameters:
        return "no-args"

    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters):
        return "kwargs"

    if any(parameter.kind == inspect.Parameter.VAR_POSITIONAL for parameter in parameters):
        return "positional"

    if len(parameters) == 1:
        return "payload"

    return "kwargs"


def _build_operation_catalog() -> Dict[str, Any]:
    """Build a live catalog of public client methods."""
    catalog: Dict[str, Any] = {}
    for namespace, namespace_info in _CLIENT_OPERATION_NAMESPACES.items():
        method_source = PurviewClient if namespace_info["use_async_client"] else namespace_info["factory"]

        operations = []
        for method_name, method in inspect.getmembers(method_source, predicate=inspect.isfunction):
            if method_name.startswith("_"):
                continue

            operations.append(
                {
                    "tool_name": f"{namespace}_{_to_snake_case(method_name)}",
                    "method_name": method_name,
                    "client": namespace_info["label"],
                    "call_style": _get_call_style(method),
                    "signature": str(inspect.signature(method)),
                    "description": _summarize_docstring(inspect.getdoc(method)),
                }
            )

        catalog[namespace] = {
            "client": namespace_info["label"],
            "operation_count": len(operations),
            "operations": sorted(operations, key=lambda item: item["tool_name"]),
        }

    return catalog


def _invoke_method(method: Any, arguments: Any) -> Any:
    """Invoke a client method using the argument style it expects."""
    if arguments is None:
        return method()

    if isinstance(arguments, dict):
        if not arguments:
            return method()

        try:
            return method(**arguments)
        except TypeError:
            return method(arguments)

    if isinstance(arguments, (list, tuple)):
        return method(*arguments)

    return method(arguments)


async def _resolve_namespace_client(namespace: str) -> Any:
    """Get the client instance for a namespace."""
    if namespace not in _CLIENT_OPERATION_NAMESPACES:
        raise ValueError(
            f"Unknown namespace '{namespace}'. Available namespaces: {', '.join(sorted(_CLIENT_OPERATION_NAMESPACES))}"
        )

    if namespace == "purview":
        return await get_client()

    factory = _CLIENT_OPERATION_NAMESPACES[namespace]["factory"]
    return factory()


@mcp.tool()
def list_available_operations(namespace: Optional[str] = None) -> Dict[str, Any]:
    """
    List the live Purview client methods that can be invoked through the MCP server.

    Use this when you need the full operation surface instead of the curated MCP tools.
    """
    catalog = _build_operation_catalog()
    if namespace:
        if namespace not in catalog:
            raise ValueError(
                f"Unknown namespace '{namespace}'. Available namespaces: {', '.join(sorted(catalog))}"
            )
        return {namespace: catalog[namespace]}
    return catalog


@mcp.tool()
async def invoke_operation(
    namespace: str,
    method_name: str,
    arguments: Any = None,
) -> Any:
    """
    Invoke any public Purview client method by namespace and method name.

    The `arguments` payload can be an object, a list, or a single scalar value depending on the method.
    """
    client = await _resolve_namespace_client(namespace)

    if not hasattr(client, method_name):
        raise ValueError(
            f"Namespace '{namespace}' does not expose method '{method_name}'. "
            f"Use list_available_operations() to inspect the current surface."
        )

    method = getattr(client, method_name)
    result = _invoke_method(method, arguments)
    if inspect.isawaitable(result):
        result = await result
    return result

def main() -> None:
    register_microsoft_learn_tools(mcp)

    # Run the FastMCP server
    logging.info("Starting Purview MCP Server")
    mcp.run()


if __name__ == "__main__":
    main()
