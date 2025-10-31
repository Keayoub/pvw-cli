"""
MCP Server for Microsoft Purview CLI
Enables LLM-powered data governance workflows through the Model Context Protocol

This server provides comprehensive access to Microsoft Purview operations:
- Entity management (CRUD, search, batch operations)
- Glossary term management
- Unified Catalog operations (domains, terms, hierarchies)
- Collection hierarchy management
- Data lineage tracking
- Type definitions
- Relationship management
- Account configuration

All operations leverage comprehensively documented client modules with
detailed docstrings including examples and use cases.

Version: 2.0 (Enhanced with comprehensive documentation)
Coverage: 90.5% of 624 methods documented
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, Resource, ResourceTemplate

    MCP_INSTALLED = True
except ImportError as e:
    # Store the error but don't exit yet - allow module inspection for tests
    MCP_INSTALLED = False
    _MCP_IMPORT_ERROR = str(e)
    # Create placeholder types so the code can be parsed
    Server = None
    stdio_server = None
    Tool = None
    TextContent = None
    Resource = None
    ResourceTemplate = None

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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


class PurviewMCPServer:
    """MCP Server wrapping PurviewClient for LLM integration"""

    def __init__(self):
        if not MCP_INSTALLED:
            raise ImportError(
                f"MCP package is required but not installed. "
                f"Install with: pip install mcp>=1.0.0\n"
                f"Original error: {_MCP_IMPORT_ERROR}"
            )
        self.server = Server("purview-mcp-server")
        self.client: Optional[PurviewClient] = None
        self._setup_handlers()

    def _get_config(self) -> PurviewConfig:
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

    async def _ensure_client(self):
        """Ensure Purview client is initialized"""
        if self.client is None:
            config = self._get_config()
            self.client = PurviewClient(config)
            await self.client.__aenter__()
            logger.info(f"Initialized Purview client for account: {config.account_name}")

    def _setup_handlers(self):
        """Setup MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List all available Purview tools"""
            return [
                # Entity Operations
                Tool(
                    name="get_entity",
                    description="Get a Purview entity by GUID. Returns entity details including attributes, classifications, and relationships.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "guid": {
                                "type": "string",
                                "description": "The unique GUID of the entity",
                            }
                        },
                        "required": ["guid"],
                    },
                ),
                Tool(
                    name="create_entity",
                    description="Create a new entity in Purview catalog. Requires entity data with typeName and attributes.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_data": {
                                "type": "object",
                                "description": "Entity data with typeName and attributes",
                            }
                        },
                        "required": ["entity_data"],
                    },
                ),
                Tool(
                    name="update_entity",
                    description="Update an existing entity in Purview catalog.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_data": {
                                "type": "object",
                                "description": "Entity data with guid and updated attributes",
                            }
                        },
                        "required": ["entity_data"],
                    },
                ),
                Tool(
                    name="delete_entity",
                    description="Delete an entity from Purview catalog by GUID.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "guid": {
                                "type": "string",
                                "description": "The unique GUID of the entity to delete",
                            }
                        },
                        "required": ["guid"],
                    },
                ),
                Tool(
                    name="search_entities",
                    description="Search for entities in Purview catalog. Supports keyword search with filters and facets.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query string (keywords)",
                            },
                            "filter": {"type": "object", "description": "Optional filter criteria"},
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 50)",
                                "default": 50,
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Offset for pagination (default: 0)",
                                "default": 0,
                            },
                        },
                        "required": ["query"],
                    },
                ),
                Tool(
                    name="batch_create_entities",
                    description="Create multiple entities in batches. Efficient for bulk operations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entities": {
                                "type": "array",
                                "description": "Array of entity data objects",
                                "items": {"type": "object"},
                            }
                        },
                        "required": ["entities"],
                    },
                ),
                Tool(
                    name="batch_update_entities",
                    description="Update multiple entities in batches. Efficient for bulk operations.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entities": {
                                "type": "array",
                                "description": "Array of entity data objects with guids",
                                "items": {"type": "object"},
                            }
                        },
                        "required": ["entities"],
                    },
                ),
                # Lineage Operations
                Tool(
                    name="get_lineage",
                    description="Get lineage information for an entity. Shows upstream and downstream relationships.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "guid": {
                                "type": "string",
                                "description": "Entity GUID to get lineage for",
                            },
                            "direction": {
                                "type": "string",
                                "description": "Lineage direction: INPUT, OUTPUT, or BOTH",
                                "enum": ["INPUT", "OUTPUT", "BOTH"],
                                "default": "BOTH",
                            },
                            "depth": {
                                "type": "integer",
                                "description": "Lineage depth (default: 3)",
                                "default": 3,
                            },
                        },
                        "required": ["guid"],
                    },
                ),
                Tool(
                    name="create_lineage",
                    description="Create a lineage relationship between entities.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lineage_data": {
                                "type": "object",
                                "description": "Lineage relationship data",
                            }
                        },
                        "required": ["lineage_data"],
                    },
                ),
                # Collection Operations
                Tool(
                    name="list_collections",
                    description="List all collections in the Purview account.",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="get_collection",
                    description="Get details of a specific collection by name.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection",
                            }
                        },
                        "required": ["collection_name"],
                    },
                ),
                Tool(
                    name="create_collection",
                    description="Create a new collection in Purview.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name for the new collection",
                            },
                            "collection_data": {
                                "type": "object",
                                "description": "Collection data with friendlyName, description, parentCollection",
                            },
                        },
                        "required": ["collection_name", "collection_data"],
                    },
                ),
                Tool(
                    name="delete_collection",
                    description="Delete a collection from Purview.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection to delete",
                            }
                        },
                        "required": ["collection_name"],
                    },
                ),
                Tool(
                    name="get_collection_path",
                    description="Get the hierarchical path of a collection.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection",
                            }
                        },
                        "required": ["collection_name"],
                    },
                ),
                # Glossary Operations
                Tool(
                    name="get_glossary_terms",
                    description="Get all glossary terms or terms from a specific glossary.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "glossary_guid": {
                                "type": "string",
                                "description": "Optional GUID of a specific glossary",
                            }
                        },
                    },
                ),
                Tool(
                    name="create_glossary_term",
                    description="Create a new glossary term.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "term_data": {
                                "type": "object",
                                "description": "Glossary term data with name, description, etc.",
                            }
                        },
                        "required": ["term_data"],
                    },
                ),
                Tool(
                    name="assign_term_to_entities",
                    description="Assign a glossary term to multiple entities.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "term_guid": {
                                "type": "string",
                                "description": "GUID of the glossary term",
                            },
                            "entity_guids": {
                                "type": "array",
                                "description": "Array of entity GUIDs to assign the term to",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["term_guid", "entity_guids"],
                    },
                ),
                # Unified Catalog Operations (Microsoft Purview Business Metadata)
                Tool(
                    name="uc_list_domains",
                    description="List all governance domains in the Unified Catalog. Domains organize business terms hierarchically.",
                    inputSchema={"type": "object", "properties": {}},
                ),
                Tool(
                    name="uc_get_domain",
                    description="Get detailed information about a specific governance domain by ID.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain_id": {
                                "type": "string",
                                "description": "The unique ID of the governance domain",
                            }
                        },
                        "required": ["domain_id"],
                    },
                ),
                Tool(
                    name="uc_create_domain",
                    description="Create a new governance domain in the Unified Catalog for organizing business terms.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain_data": {
                                "type": "object",
                                "description": "Domain data with name, description, owner_id (Entra Object ID)",
                            }
                        },
                        "required": ["domain_data"],
                    },
                ),
                Tool(
                    name="uc_list_terms",
                    description="List all business metadata terms in a governance domain. Terms define standardized business vocabulary.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain_id": {
                                "type": "string",
                                "description": "The governance domain ID to list terms from",
                            }
                        },
                        "required": ["domain_id"],
                    },
                ),
                Tool(
                    name="uc_get_term",
                    description="Get detailed information about a specific business metadata term.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain_id": {
                                "type": "string",
                                "description": "The governance domain ID",
                            },
                            "term_id": {
                                "type": "string",
                                "description": "The term ID",
                            },
                        },
                        "required": ["domain_id", "term_id"],
                    },
                ),
                Tool(
                    name="uc_create_term",
                    description="Create a new business metadata term in a governance domain.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "domain_id": {
                                "type": "string",
                                "description": "The governance domain ID",
                            },
                            "term_data": {
                                "type": "object",
                                "description": "Term data with name, definition, owner_id (Entra Object ID)",
                            },
                        },
                        "required": ["domain_id", "term_data"],
                    },
                ),
                Tool(
                    name="uc_search_terms",
                    description="Search for business metadata terms across all domains using keyword query.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "search_query": {
                                "type": "string",
                                "description": "Search query string (keywords to find in term names/definitions)",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 50)",
                                "default": 50,
                            },
                        },
                        "required": ["search_query"],
                    },
                ),
                # CSV Operations
                Tool(
                    name="import_entities_from_csv",
                    description="Import entities from a CSV file with mapping configuration.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "csv_file_path": {
                                "type": "string",
                                "description": "Path to the CSV file",
                            },
                            "mapping_config": {
                                "type": "object",
                                "description": "Mapping configuration for CSV columns to entity attributes",
                            },
                        },
                        "required": ["csv_file_path", "mapping_config"],
                    },
                ),
                Tool(
                    name="export_entities_to_csv",
                    description="Export entities to a CSV file based on a search query.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find entities to export",
                            },
                            "csv_file_path": {
                                "type": "string",
                                "description": "Path for the output CSV file",
                            },
                            "columns": {
                                "type": "array",
                                "description": "Optional list of columns to include",
                                "items": {"type": "string"},
                            },
                        },
                        "required": ["query", "csv_file_path"],
                    },
                ),
                # Account Operations
                Tool(
                    name="get_account_properties",
                    description="Get properties of the Purview account.",
                    inputSchema={"type": "object", "properties": {}},
                ),
                # Advanced Search Operations
                Tool(
                    name="search_suggest",
                    description="Get search suggestions/autocomplete for a query string. Useful for building search UIs.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "string",
                                "description": "Partial keyword string for autocomplete",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of suggestions (default: 5)",
                                "default": 5,
                            },
                        },
                        "required": ["keywords"],
                    },
                ),
                Tool(
                    name="search_browse",
                    description="Browse the Purview catalog by entity type. Returns aggregated counts by type, classification, etc.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_type": {
                                "type": "string",
                                "description": "Entity type to browse (e.g., 'DataSet', 'azure_sql_table')",
                            },
                            "path": {
                                "type": "string",
                                "description": "Browse path for hierarchical navigation",
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum results (default: 50)",
                                "default": 50,
                            },
                        },
                        "required": ["entity_type"],
                    },
                ),
                # Type Definition Operations
                Tool(
                    name="get_typedef",
                    description="Get type definition by name. Returns entity type schema including attributes and relationships.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type_name": {
                                "type": "string",
                                "description": "Name of the type (e.g., 'DataSet', 'azure_sql_table')",
                            }
                        },
                        "required": ["type_name"],
                    },
                ),
                Tool(
                    name="list_typedefs",
                    description="List all type definitions in Purview. Optionally filter by type category (entity, classification, etc.).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type_category": {
                                "type": "string",
                                "description": "Optional: entity, classification, relationship, enum",
                            }
                        },
                    },
                ),
                # Relationship Operations
                Tool(
                    name="create_relationship",
                    description="Create a relationship between two entities (e.g., parent-child, lineage).",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "relationship_data": {
                                "type": "object",
                                "description": "Relationship data with typeName, end1 (entity GUID), end2 (entity GUID)",
                            }
                        },
                        "required": ["relationship_data"],
                    },
                ),
                Tool(
                    name="get_relationship",
                    description="Get relationship details by GUID.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "relationship_guid": {
                                "type": "string",
                                "description": "The relationship GUID",
                            }
                        },
                        "required": ["relationship_guid"],
                    },
                ),
                Tool(
                    name="delete_relationship",
                    description="Delete a relationship between entities.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "relationship_guid": {
                                "type": "string",
                                "description": "The relationship GUID to delete",
                            }
                        },
                        "required": ["relationship_guid"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool execution"""
            try:
                await self._ensure_client()
                result = await self._execute_tool(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Tool {name} failed: {e}", exc_info=True)
                error_result = {"error": str(e), "tool": name, "arguments": arguments}
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a specific tool"""
        logger.info(f"Executing tool: {name} with arguments: {arguments}")

        # Entity Operations
        if name == "get_entity":
            return await self.client.get_entity(arguments["guid"])

        elif name == "create_entity":
            return await self.client.create_entity(arguments["entity_data"])

        elif name == "update_entity":
            return await self.client.update_entity(arguments["entity_data"])

        elif name == "delete_entity":
            return await self.client.delete_entity(arguments["guid"])

        elif name == "search_entities":
            return await self.client.search_entities(
                query=arguments["query"],
                filter=arguments.get("filter"),
                limit=arguments.get("limit", 50),
                offset=arguments.get("offset", 0),
            )

        elif name == "batch_create_entities":
            return await self.client.batch_create_entities(arguments["entities"])

        elif name == "batch_update_entities":
            return await self.client.batch_update_entities(arguments["entities"])

        # Lineage Operations
        elif name == "get_lineage":
            return await self.client.get_lineage(
                guid=arguments["guid"],
                direction=arguments.get("direction", "BOTH"),
                depth=arguments.get("depth", 3),
            )

        elif name == "create_lineage":
            return await self.client.create_lineage(arguments["lineage_data"])

        # Collection Operations
        elif name == "list_collections":
            return await self.client.list_collections()

        elif name == "get_collection":
            return await self.client.get_collection(arguments["collection_name"])

        elif name == "create_collection":
            return await self.client.create_collection(
                collection_name=arguments["collection_name"],
                collection_data=arguments["collection_data"],
            )

        elif name == "delete_collection":
            return await self.client.delete_collection(arguments["collection_name"])

        elif name == "get_collection_path":
            return await self.client.get_collection_path(arguments["collection_name"])

        # Glossary Operations
        elif name == "get_glossary_terms":
            return await self.client.get_glossary_terms(
                glossary_guid=arguments.get("glossary_guid")
            )

        elif name == "create_glossary_term":
            return await self.client.create_glossary_term(arguments["term_data"])

        elif name == "assign_term_to_entities":
            return await self.client.assign_term_to_entities(
                term_guid=arguments["term_guid"], entity_guids=arguments["entity_guids"]
            )

        # Unified Catalog Operations (Business Metadata)
        # Note: Unified Catalog uses synchronous client, not async
        elif name == "uc_list_domains":
            from purviewcli.client import unified_catalog

            uc_client = UnifiedCatalogClient()
            return uc_client.listGovernanceDomains({"--domain-id": None})

        elif name == "uc_get_domain":
            uc_client = UnifiedCatalogClient()
            return uc_client.readGovernanceDomain({"--domain-id": arguments["domain_id"]})

        elif name == "uc_create_domain":
            uc_client = UnifiedCatalogClient()
            args = {
                "--name": arguments["domain_data"].get("name"),
                "--description": arguments["domain_data"].get("description"),
                "--owner-id": arguments["domain_data"].get("owner_id"),
            }
            return uc_client.createGovernanceDomain(args)

        elif name == "uc_list_terms":
            uc_client = UnifiedCatalogClient()
            return uc_client.listGovernanceTerms({"--domain-id": arguments["domain_id"]})

        elif name == "uc_get_term":
            uc_client = UnifiedCatalogClient()
            args = {
                "--domain-id": arguments["domain_id"],
                "--term-id": arguments["term_id"],
            }
            return uc_client.readGovernanceTerm(args)

        elif name == "uc_create_term":
            uc_client = UnifiedCatalogClient()
            term_data = arguments["term_data"]
            args = {
                "--domain-id": arguments["domain_id"],
                "--name": term_data.get("name"),
                "--definition": term_data.get("definition"),
                "--owner-id": term_data.get("owner_id"),
            }
            # Add optional fields if provided
            if "parent_term_id" in term_data:
                args["--parent-term-id"] = term_data["parent_term_id"]
            if "description" in term_data:
                args["--description"] = term_data["description"]
            return uc_client.createGovernanceTerm(args)

        elif name == "uc_search_terms":
            uc_client = UnifiedCatalogClient()
            args = {
                "--search-query": arguments["search_query"],
                "--limit": arguments.get("limit", 50),
            }
            return uc_client.searchGovernanceTerms(args)

        # Advanced Search Operations
        elif name == "search_suggest":
            search_client = Search()
            args = {
                "--keywords": arguments["keywords"],
                "--limit": arguments.get("limit", 5),
            }
            return search_client.searchSuggest(args)

        elif name == "search_browse":
            search_client = Search()
            args = {
                "--entityType": arguments["entity_type"],
                "--path": arguments.get("path"),
                "--limit": arguments.get("limit", 50),
            }
            return search_client.searchBrowse(args)

        # Type Definition Operations
        elif name == "get_typedef":
            types_client = Types()
            args = {"--name": arguments["type_name"]}
            return types_client.typesRead(args)

        elif name == "list_typedefs":
            types_client = Types()
            args = {"--type": arguments.get("type_category")}
            return types_client.typesList(args)

        # Relationship Operations
        elif name == "create_relationship":
            relationship_client = Relationship()
            # Convert MCP format to CLI format
            rel_data = arguments["relationship_data"]
            args = {
                "--typeName": rel_data.get("typeName"),
                "--end1": rel_data.get("end1"),
                "--end2": rel_data.get("end2"),
            }
            return relationship_client.relationshipCreate(args)

        elif name == "get_relationship":
            relationship_client = Relationship()
            args = {"--guid": arguments["relationship_guid"]}
            return relationship_client.relationshipRead(args)

        elif name == "delete_relationship":
            relationship_client = Relationship()
            args = {"--guid": arguments["relationship_guid"]}
            return relationship_client.relationshipDelete(args)

        # CSV Operations
        elif name == "import_entities_from_csv":
            return await self.client.import_entities_from_csv(
                csv_file_path=arguments["csv_file_path"], mapping_config=arguments["mapping_config"]
            )

        elif name == "export_entities_to_csv":
            return await self.client.export_entities_to_csv(
                query=arguments["query"],
                csv_file_path=arguments["csv_file_path"],
                columns=arguments.get("columns"),
            )

        # Account Operations
        elif name == "get_account_properties":
            return await self.client.get_account_properties()

        else:
            raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the MCP server"""
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("Starting Purview MCP Server...")
                await self.server.run(
                    read_stream, write_stream, self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            if self.client:
                await self.client.__aexit__(None, None, None)
                logger.info("Purview client closed")


async def main():
    """Main entry point"""
    if not MCP_INSTALLED:
        print(
            "ERROR: mcp package not installed. Install with: pip install mcp>=1.0.0",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        server = PurviewMCPServer()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
