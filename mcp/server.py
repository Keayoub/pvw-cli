"""
MCP Server for Microsoft Purview CLI
Enables LLM-powered data governance workflows through the Model Context Protocol
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
    from mcp.types import Tool, TextContent
except ImportError:
    print("ERROR: mcp package not installed. Install with: pip install mcp>=1.0.0", file=sys.stderr)
    sys.exit(1)

# Add parent directory to path to import purviewcli
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from purviewcli.client.api_client import PurviewClient, PurviewConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)


class PurviewMCPServer:
    """MCP Server wrapping PurviewClient for LLM integration"""

    def __init__(self):
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
            batch_size=int(os.getenv("PURVIEW_BATCH_SIZE", "100"))
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
                                "description": "The unique GUID of the entity"
                            }
                        },
                        "required": ["guid"]
                    }
                ),
                Tool(
                    name="create_entity",
                    description="Create a new entity in Purview catalog. Requires entity data with typeName and attributes.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_data": {
                                "type": "object",
                                "description": "Entity data with typeName and attributes"
                            }
                        },
                        "required": ["entity_data"]
                    }
                ),
                Tool(
                    name="update_entity",
                    description="Update an existing entity in Purview catalog.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "entity_data": {
                                "type": "object",
                                "description": "Entity data with guid and updated attributes"
                            }
                        },
                        "required": ["entity_data"]
                    }
                ),
                Tool(
                    name="delete_entity",
                    description="Delete an entity from Purview catalog by GUID.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "guid": {
                                "type": "string",
                                "description": "The unique GUID of the entity to delete"
                            }
                        },
                        "required": ["guid"]
                    }
                ),
                Tool(
                    name="search_entities",
                    description="Search for entities in Purview catalog. Supports keyword search with filters and facets.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query string (keywords)"
                            },
                            "filter": {
                                "type": "object",
                                "description": "Optional filter criteria"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 50)",
                                "default": 50
                            },
                            "offset": {
                                "type": "integer",
                                "description": "Offset for pagination (default: 0)",
                                "default": 0
                            }
                        },
                        "required": ["query"]
                    }
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
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["entities"]
                    }
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
                                "items": {"type": "object"}
                            }
                        },
                        "required": ["entities"]
                    }
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
                                "description": "Entity GUID to get lineage for"
                            },
                            "direction": {
                                "type": "string",
                                "description": "Lineage direction: INPUT, OUTPUT, or BOTH",
                                "enum": ["INPUT", "OUTPUT", "BOTH"],
                                "default": "BOTH"
                            },
                            "depth": {
                                "type": "integer",
                                "description": "Lineage depth (default: 3)",
                                "default": 3
                            }
                        },
                        "required": ["guid"]
                    }
                ),
                Tool(
                    name="create_lineage",
                    description="Create a lineage relationship between entities.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lineage_data": {
                                "type": "object",
                                "description": "Lineage relationship data"
                            }
                        },
                        "required": ["lineage_data"]
                    }
                ),
                # Collection Operations
                Tool(
                    name="list_collections",
                    description="List all collections in the Purview account.",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_collection",
                    description="Get details of a specific collection by name.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection"
                            }
                        },
                        "required": ["collection_name"]
                    }
                ),
                Tool(
                    name="create_collection",
                    description="Create a new collection in Purview.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name for the new collection"
                            },
                            "collection_data": {
                                "type": "object",
                                "description": "Collection data with friendlyName, description, parentCollection"
                            }
                        },
                        "required": ["collection_name", "collection_data"]
                    }
                ),
                Tool(
                    name="delete_collection",
                    description="Delete a collection from Purview.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection to delete"
                            }
                        },
                        "required": ["collection_name"]
                    }
                ),
                Tool(
                    name="get_collection_path",
                    description="Get the hierarchical path of a collection.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection_name": {
                                "type": "string",
                                "description": "Name of the collection"
                            }
                        },
                        "required": ["collection_name"]
                    }
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
                                "description": "Optional GUID of a specific glossary"
                            }
                        }
                    }
                ),
                Tool(
                    name="create_glossary_term",
                    description="Create a new glossary term.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "term_data": {
                                "type": "object",
                                "description": "Glossary term data with name, description, etc."
                            }
                        },
                        "required": ["term_data"]
                    }
                ),
                Tool(
                    name="assign_term_to_entities",
                    description="Assign a glossary term to multiple entities.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "term_guid": {
                                "type": "string",
                                "description": "GUID of the glossary term"
                            },
                            "entity_guids": {
                                "type": "array",
                                "description": "Array of entity GUIDs to assign the term to",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["term_guid", "entity_guids"]
                    }
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
                                "description": "Path to the CSV file"
                            },
                            "mapping_config": {
                                "type": "object",
                                "description": "Mapping configuration for CSV columns to entity attributes"
                            }
                        },
                        "required": ["csv_file_path", "mapping_config"]
                    }
                ),
                Tool(
                    name="export_entities_to_csv",
                    description="Export entities to a CSV file based on a search query.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find entities to export"
                            },
                            "csv_file_path": {
                                "type": "string",
                                "description": "Path for the output CSV file"
                            },
                            "columns": {
                                "type": "array",
                                "description": "Optional list of columns to include",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["query", "csv_file_path"]
                    }
                ),
                # Account Operations
                Tool(
                    name="get_account_properties",
                    description="Get properties of the Purview account.",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
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
                error_result = {
                    "error": str(e),
                    "tool": name,
                    "arguments": arguments
                }
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
                offset=arguments.get("offset", 0)
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
                depth=arguments.get("depth", 3)
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
                collection_data=arguments["collection_data"]
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
                term_guid=arguments["term_guid"],
                entity_guids=arguments["entity_guids"]
            )

        # CSV Operations
        elif name == "import_entities_from_csv":
            return await self.client.import_entities_from_csv(
                csv_file_path=arguments["csv_file_path"],
                mapping_config=arguments["mapping_config"]
            )

        elif name == "export_entities_to_csv":
            return await self.client.export_entities_to_csv(
                query=arguments["query"],
                csv_file_path=arguments["csv_file_path"],
                columns=arguments.get("columns")
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
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
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
