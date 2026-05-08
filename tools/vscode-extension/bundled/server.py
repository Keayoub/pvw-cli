"""
FastMCP Server for Microsoft Purview CLI

This server provides the same comprehensive access to Microsoft Purview operations
but with cleaner code, automatic validation, and better developer experience.

"""

import inspect
import logging
import os
import sys
import re
from typing import Optional, List, Dict, Any

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from tools.PurviewMCPServer.tools.microsoft_learn_tools import register_microsoft_learn_tools

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
mcp = FastMCP("purview-mcp-server")

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
    """
    client = await get_client()
    return await client.get_account_properties()
    

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
