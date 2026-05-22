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

from .config import PurviewMCPConfig
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
    DataQuality,
)
from purviewcli.client._account import Account
from purviewcli.client._insight import Insight
from purviewcli.client._scan import Scan as ScanClient
from purviewcli.client._management import Management
from purviewcli.client._policystore import Policystore
from purviewcli.client._workflow import Workflow
from purviewcli.client._share import Share
from purviewcli.client._health import Health

def _load_instructions() -> str:
    """Load MCP server instructions from PROMPT_INSTRUCTIONS.md."""
    path = Path(__file__).parent / "prompt_instructions.md"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "Purview MCP Server — see prompt_instructions.md for usage guidelines."


# Initialize FastMCP
mcp = FastMCP(
    "purview-mcp-server",
    instructions=_load_instructions(),
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
    cfg = PurviewMCPConfig.from_env()
    return PurviewConfig(
        account_name=cfg.account_name,
        tenant_id=cfg.tenant_id,
        azure_region=cfg.azure_region,
        max_retries=cfg.max_retries,
        timeout=cfg.timeout,
        batch_size=cfg.batch_size,
    )


@mcp.tool()
def get_prompt_instructions() -> str:
    """Return the curated prompt instructions for the Purview MCP Server."""
    return _load_instructions()


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
    "account": {
        "label": "Account",
        "factory": Account,
        "use_async_client": False,
    },
    "insight": {
        "label": "Insight",
        "factory": Insight,
        "use_async_client": False,
    },
    "scan": {
        "label": "Scan",
        "factory": ScanClient,
        "use_async_client": False,
    },
    "management": {
        "label": "Management",
        "factory": Management,
        "use_async_client": False,
    },
    "policystore": {
        "label": "Policystore",
        "factory": Policystore,
        "use_async_client": False,
    },
    "workflow": {
        "label": "Workflow",
        "factory": Workflow,
        "use_async_client": False,
    },
    "share": {
        "label": "Share",
        "factory": Share,
        "use_async_client": False,
    },
    "health": {
        "label": "Health",
        "factory": Health,
        "use_async_client": False,
    },
    "quality": {
        "label": "DataQuality",
        "factory": DataQuality,
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


# ============================================================================
# SCAN OPERATIONS
# ============================================================================

@mcp.tool()
def list_data_sources() -> Dict[str, Any]:
    """List all registered data sources in Purview."""
    return ScanClient().scanDataSourcesRead({})


@mcp.tool()
def get_data_source(data_source_name: str) -> Dict[str, Any]:
    """Get details of a specific registered data source.

    Args:
        data_source_name: The name of the data source
    """
    return ScanClient().scanDataSourceRead({"--dataSourceName": data_source_name})


@mcp.tool()
def create_data_source(data_source_name: str, data_source_data: Dict[str, Any]) -> Dict[str, Any]:
    """Register a new data source for scanning.

    Args:
        data_source_name: Unique name for the data source
        data_source_data: Data source definition (kind, properties, collection)
    """
    return ScanClient().scanDataSourceCreate({"--dataSourceName": data_source_name, "--payload": data_source_data})


@mcp.tool()
def delete_data_source(data_source_name: str) -> Dict[str, Any]:
    """Delete a registered data source.

    Args:
        data_source_name: Name of the data source to delete
    """
    return ScanClient().scanDataSourceDelete({"--dataSourceName": data_source_name})


@mcp.tool()
def list_scans(data_source_name: str) -> Dict[str, Any]:
    """List all scans configured for a data source.

    Args:
        data_source_name: The name of the data source
    """
    from purviewcli.client._scan import Scan as _Scan
    return _Scan().scanRead({"--dataSourceName": data_source_name})


@mcp.tool()
def run_scan(data_source_name: str, scan_name: str, scan_level: str = "Full") -> Dict[str, Any]:
    """Trigger a scan run for a data source.

    Args:
        data_source_name: The name of the data source
        scan_name: The name of the scan to run
        scan_level: Scan level: Full or Incremental (default: Full)
    """
    return ScanClient().scanRun({"--dataSourceName": data_source_name, "--scanName": scan_name, "--scanLevel": scan_level})


@mcp.tool()
def get_scan_history(data_source_name: str, scan_name: str) -> Dict[str, Any]:
    """Get the run history of a scan.

    Args:
        data_source_name: The name of the data source
        scan_name: The name of the scan
    """
    return ScanClient().scanReadHistory({"--dataSourceName": data_source_name, "--scanName": scan_name})


@mcp.tool()
def list_scan_rulesets() -> Dict[str, Any]:
    """List all custom scan rulesets defined in the account."""
    return ScanClient().scanReadRuleset({})


# ============================================================================
# INSIGHT OPERATIONS
# ============================================================================

@mcp.tool()
def get_asset_distribution() -> Dict[str, Any]:
    """Get asset counts distributed by type, classification, and collection."""
    return Insight().insightAssetDistribution({})


@mcp.tool()
def get_asset_distribution_by_type() -> Dict[str, Any]:
    """Get asset counts grouped by entity type."""
    return Insight().insightAssetDistributionByType({})


@mcp.tool()
def get_asset_distribution_by_classification() -> Dict[str, Any]:
    """Get asset counts grouped by classification label."""
    return Insight().insightAssetDistributionByClassification({})


@mcp.tool()
def get_scan_status_summary() -> Dict[str, Any]:
    """Get a summary of recent scan statuses across all data sources."""
    return Insight().insightScanStatusSummary({})


@mcp.tool()
def get_tags_summary() -> Dict[str, Any]:
    """Get a summary of classification/tag usage across the catalog."""
    return Insight().insightTags({})


@mcp.tool()
def get_data_quality_overview() -> Dict[str, Any]:
    """Get a high-level overview of data quality scores across the account."""
    return Insight().insightDataQualityOverview({})


@mcp.tool()
def get_lineage_coverage() -> Dict[str, Any]:
    """Get lineage coverage statistics showing how many assets have tracked lineage."""
    return Insight().insightLineageCoverage({})


@mcp.tool()
def get_glossary_usage() -> Dict[str, Any]:
    """Get statistics on glossary term assignment coverage across assets."""
    return Insight().insightGlossaryUsage({})


# ============================================================================
# ACCOUNT OPERATIONS (extended)
# ============================================================================

@mcp.tool()
def get_account_details() -> Dict[str, Any]:
    """Get full details of the Purview account including configuration and status."""
    return Account().accountRead({})


@mcp.tool()
def get_account_usage() -> Dict[str, Any]:
    """Get current resource usage statistics for the Purview account."""
    return Account().accountReadUsage({})


@mcp.tool()
def get_account_limits() -> Dict[str, Any]:
    """Get resource limits and quotas for the Purview account."""
    return Account().accountReadLimits({})


@mcp.tool()
def get_account_access_keys() -> Dict[str, Any]:
    """Get the access keys for the Purview account (Atlas API authentication)."""
    return Account().accountReadAccessKeys({})


# ============================================================================
# WORKFLOW OPERATIONS
# ============================================================================

@mcp.tool()
def list_workflows() -> Dict[str, Any]:
    """List all approval workflows defined in the Purview account."""
    return Workflow().workflowListWorkflows({})


@mcp.tool()
def get_workflow(workflow_id: str) -> Dict[str, Any]:
    """Get details of a specific workflow.

    Args:
        workflow_id: The workflow ID
    """
    return Workflow().workflowGetWorkflow({"--workflow-id": workflow_id})


@mcp.tool()
def list_workflow_runs(workflow_id: str) -> Dict[str, Any]:
    """List all execution runs for a workflow.

    Args:
        workflow_id: The workflow ID
    """
    return Workflow().workflowGetWorkflowRuns({"--workflow-id": workflow_id})


@mcp.tool()
def get_approval_requests() -> Dict[str, Any]:
    """List all pending approval requests requiring action."""
    return Workflow().workflowGetApprovalRequests({})


@mcp.tool()
def approve_workflow_request(request_id: str, comment: Optional[str] = None) -> Dict[str, Any]:
    """Approve a pending workflow approval request.

    Args:
        request_id: The approval request ID
        comment: Optional approval comment
    """
    args: Dict[str, Any] = {"--request-id": request_id}
    if comment:
        args["--comment"] = comment
    return Workflow().workflowApproveRequest(args)


@mcp.tool()
def reject_workflow_request(request_id: str, comment: Optional[str] = None) -> Dict[str, Any]:
    """Reject a pending workflow approval request.

    Args:
        request_id: The approval request ID
        comment: Optional rejection comment
    """
    args: Dict[str, Any] = {"--request-id": request_id}
    if comment:
        args["--comment"] = comment
    return Workflow().workflowRejectRequest(args)


@mcp.tool()
def list_workflow_templates() -> Dict[str, Any]:
    """List all available workflow templates for creating new workflows."""
    return Workflow().workflowListWorkflowTemplates({})


# ============================================================================
# POLICY STORE OPERATIONS
# ============================================================================

@mcp.tool()
def list_data_access_policies() -> Dict[str, Any]:
    """List all data access policies defined in the Purview policy store."""
    return Policystore().policystoreListDataAccessPolicies({})


@mcp.tool()
def list_metadata_policies() -> Dict[str, Any]:
    """List all metadata policies (collection-level role assignments)."""
    return Policystore().policystoreReadMetadataPolicies({})


@mcp.tool()
def get_metadata_policy(policy_id: str) -> Dict[str, Any]:
    """Get a specific metadata policy by ID.

    Args:
        policy_id: The metadata policy ID
    """
    return Policystore().policystoreReadMetadataPolicy({"--policy-id": policy_id})


@mcp.tool()
def list_metadata_roles() -> Dict[str, Any]:
    """List all available metadata roles that can be assigned in policies."""
    return Policystore().policystoreReadMetadataRoles({})


@mcp.tool()
def get_user_permissions() -> Dict[str, Any]:
    """Get the effective permissions for the currently authenticated user."""
    return Policystore().policystoreGetUserPermissions({})


# ============================================================================
# HEALTH OPERATIONS
# ============================================================================

@mcp.tool()
def get_health_summary() -> Dict[str, Any]:
    """Get a summary of Purview account health and service status."""
    return Health().get_health_summary({})


@mcp.tool()
def query_health_actions(
    filter_status: Optional[str] = None,
    filter_type: Optional[str] = None
) -> Dict[str, Any]:
    """Query health actions and recommendations for the Purview account.

    Args:
        filter_status: Optional status filter (e.g., Active, Resolved)
        filter_type: Optional type filter
    """
    args: Dict[str, Any] = {}
    if filter_status:
        args["--status"] = filter_status
    if filter_type:
        args["--type"] = filter_type
    return Health().query_health_actions(args)


# ============================================================================
# SHARE OPERATIONS (Purview Data Sharing)
# ============================================================================

@mcp.tool()
def list_sent_shares() -> Dict[str, Any]:
    """List all data shares you have sent to other recipients."""
    return Share().shareListSentShares({})


@mcp.tool()
def list_received_shares() -> Dict[str, Any]:
    """List all data shares you have received from other senders."""
    return Share().shareListReceivedShares({})


@mcp.tool()
def get_sent_share(sent_share_id: str) -> Dict[str, Any]:
    """Get details of a specific sent share.

    Args:
        sent_share_id: The sent share ID
    """
    return Share().shareGetSentShare({"--sent-share-id": sent_share_id})


@mcp.tool()
def get_received_share(received_share_id: str) -> Dict[str, Any]:
    """Get details of a specific received share.

    Args:
        received_share_id: The received share ID
    """
    return Share().shareGetReceivedShare({"--received-share-id": received_share_id})


@mcp.tool()
def list_sent_invitations(sent_share_id: str) -> Dict[str, Any]:
    """List invitations sent for a specific data share.

    Args:
        sent_share_id: The sent share ID
    """
    return Share().shareListSentInvitations({"--sent-share-id": sent_share_id})


@mcp.tool()
def list_received_invitations() -> Dict[str, Any]:
    """List all pending data share invitations you have received."""
    return Share().shareListReceivedInvitations({})


# ============================================================================
# DATA QUALITY OPERATIONS
# ============================================================================

@mcp.tool()
def list_quality_domains() -> Dict[str, Any]:
    """List all data quality domains configured in the account."""
    return DataQuality().list_domains({})


@mcp.tool()
def get_quality_domain_report(domain_id: str) -> Dict[str, Any]:
    """Get a quality report for a specific data quality domain.

    Args:
        domain_id: The data quality domain ID
    """
    return DataQuality().get_domain_report({"--domain-id": domain_id})


@mcp.tool()
def list_quality_connections(domain_id: str) -> Dict[str, Any]:
    """List all data source connections in a quality domain.

    Args:
        domain_id: The data quality domain ID
    """
    return DataQuality().list_connections({"--domain-id": domain_id})


@mcp.tool()
def list_quality_rules(domain_id: str) -> Dict[str, Any]:
    """List all data quality rules defined in a domain.

    Args:
        domain_id: The data quality domain ID
    """
    return DataQuality().list_rules({"--domain-id": domain_id})


@mcp.tool()
def get_quality_score(domain_id: str) -> Dict[str, Any]:
    """Get the overall data quality score for a domain.

    Args:
        domain_id: The data quality domain ID
    """
    return DataQuality().get_quality_score({"--domain-id": domain_id})


@mcp.tool()
def run_quality_scan(domain_id: str, scan_id: str) -> Dict[str, Any]:
    """Trigger a data quality scan run.

    Args:
        domain_id: The data quality domain ID
        scan_id: The scan configuration ID to run
    """
    return DataQuality().run_scan({"--domain-id": domain_id, "--scan-id": scan_id})


@mcp.tool()
def list_quality_scans(domain_id: str) -> Dict[str, Any]:
    """List all data quality scan configurations in a domain.

    Args:
        domain_id: The data quality domain ID
    """
    return DataQuality().list_scans({"--domain-id": domain_id})


def main() -> None:
    cfg = PurviewMCPConfig.from_env()

    if cfg.transport == "stdio":
        logging.info("Starting Purview MCP Server (transport=stdio)")
        mcp.run()
        return

    logging.info(
        "Starting Purview MCP Server (transport=%s, host=%s, port=%s)",
        cfg.transport,
        cfg.host,
        cfg.port,
    )
    mcp.run(transport=cfg.transport, host=cfg.host, port=cfg.port)


if __name__ == "__main__":
    main()
