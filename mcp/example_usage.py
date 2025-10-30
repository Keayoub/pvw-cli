"""
Example usage of the Purview MCP Server
This script demonstrates how to interact with the MCP server programmatically

Note: Make sure the purviewcli package is installed:
  pip install -e .  (from repository root)
  OR
  pip install pvw-cli  (from PyPI)
"""

import asyncio
import json
import os

from purviewcli.client.api_client import PurviewClient, PurviewConfig


async def example_entity_operations():
    """Example: Entity operations"""
    print("\n=== Entity Operations Example ===\n")
    
    # Configuration
    config = PurviewConfig(
        account_name=os.getenv("PURVIEW_ACCOUNT_NAME", "your-account"),
        azure_region=os.getenv("AZURE_REGION"),
    )
    
    async with PurviewClient(config) as client:
        # Example 1: Search for entities
        print("1. Searching for SQL entities...")
        try:
            results = await client.search_entities("SQL", limit=5)
            print(f"Found {len(results.get('value', []))} entities")
            print(json.dumps(results, indent=2)[:500] + "...")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nNote: The MCP server wraps these operations and exposes them as tools.")
        print("An LLM can call these tools through natural language requests.")


async def example_collection_operations():
    """Example: Collection operations"""
    print("\n=== Collection Operations Example ===\n")
    
    config = PurviewConfig(
        account_name=os.getenv("PURVIEW_ACCOUNT_NAME", "your-account"),
        azure_region=os.getenv("AZURE_REGION"),
    )
    
    async with PurviewClient(config) as client:
        # Example 2: List collections
        print("2. Listing collections...")
        try:
            collections = await client.list_collections()
            print(f"Found {len(collections.get('value', []))} collections")
            for col in collections.get('value', [])[:3]:
                print(f"  - {col.get('name')} ({col.get('friendlyName')})")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nNote: Through MCP, an LLM can ask 'List all collections' and get this data.")


async def example_glossary_operations():
    """Example: Glossary operations"""
    print("\n=== Glossary Operations Example ===\n")
    
    config = PurviewConfig(
        account_name=os.getenv("PURVIEW_ACCOUNT_NAME", "your-account"),
        azure_region=os.getenv("AZURE_REGION"),
    )
    
    async with PurviewClient(config) as client:
        # Example 3: Get glossary terms
        print("3. Getting glossary terms...")
        try:
            terms = await client.get_glossary_terms()
            print(f"Found glossary with {len(terms)} items")
            print(json.dumps(terms, indent=2)[:500] + "...")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\nNote: An LLM can create, update, and assign glossary terms through MCP.")


def print_mcp_info():
    """Print information about the MCP server"""
    print("\n" + "="*70)
    print(" Purview MCP Server - Example Usage")
    print("="*70)
    print()
    print("This script demonstrates the operations that the MCP server exposes.")
    print("When the MCP server is running, AI assistants can use these operations")
    print("through natural language requests.")
    print()
    print("Available Tools (20+):")
    print("  - Entity Operations: get, create, update, delete, search, batch")
    print("  - Lineage Operations: get lineage, create lineage")
    print("  - Collection Operations: list, get, create, delete, get path")
    print("  - Glossary Operations: get terms, create term, assign to entities")
    print("  - CSV Operations: import/export entities")
    print("  - Account Operations: get properties")
    print()
    print("To start the MCP server:")
    print("  python mcp/server.py")
    print()
    print("To use with Claude Desktop or Cline:")
    print("  See mcp/README.md for configuration instructions")
    print()
    print("="*70)


async def main():
    """Main function"""
    print_mcp_info()
    
    # Check if PURVIEW_ACCOUNT_NAME is set
    if not os.getenv("PURVIEW_ACCOUNT_NAME"):
        print("\nWARNING: PURVIEW_ACCOUNT_NAME environment variable not set.")
        print("Set it to run the examples:")
        print("  export PURVIEW_ACCOUNT_NAME=your-account")
        print("\nShowing examples without actual API calls...\n")
        return
    
    # Check authentication
    print("\nChecking Azure authentication...")
    print("Make sure you're logged in with: az login")
    print()
    
    try:
        # Run examples
        await example_entity_operations()
        await example_collection_operations()
        await example_glossary_operations()
        
        print("\n" + "="*70)
        print(" Examples completed successfully!")
        print("="*70)
        print()
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure:")
        print("1. PURVIEW_ACCOUNT_NAME is set correctly")
        print("2. You're authenticated (az login)")
        print("3. You have access to the Purview account")
        print()


if __name__ == "__main__":
    asyncio.run(main())
