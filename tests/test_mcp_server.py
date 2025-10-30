"""
Tests for MCP Server
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMCPServerStructure:
    """Test MCP server structure and initialization"""

    def test_server_file_exists(self):
        """Test that server.py file exists"""
        server_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mcp", "server.py"
        )
        assert os.path.exists(server_path), "server.py should exist"

    def test_package_json_exists(self):
        """Test that package.json file exists"""
        package_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mcp", "package.json"
        )
        assert os.path.exists(package_path), "package.json should exist"

    def test_readme_exists(self):
        """Test that README.md file exists"""
        readme_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mcp", "README.md"
        )
        assert os.path.exists(readme_path), "README.md should exist"

    def test_requirements_exists(self):
        """Test that requirements.txt file exists"""
        req_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mcp", "requirements.txt"
        )
        assert os.path.exists(req_path), "requirements.txt should exist"

    def test_init_exists(self):
        """Test that __init__.py file exists"""
        init_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mcp", "__init__.py"
        )
        assert os.path.exists(init_path), "__init__.py should exist"


class TestMCPServerConfiguration:
    """Test MCP server configuration"""

    @patch.dict(os.environ, {"PURVIEW_ACCOUNT_NAME": "test-account"})
    def test_get_config_with_env_vars(self):
        """Test configuration from environment variables"""
        # Skip if MCP not installed
        pytest.importorskip("mcp")
        
        from mcp.server import PurviewMCPServer
        
        server = PurviewMCPServer()
        config = server._get_config()
        
        assert config.account_name == "test-account"
        assert config.max_retries == 3
        assert config.timeout == 30
        assert config.batch_size == 100

    def test_get_config_missing_account_name(self):
        """Test configuration fails without PURVIEW_ACCOUNT_NAME"""
        # Skip if MCP not installed
        pytest.importorskip("mcp")
        
        from mcp.server import PurviewMCPServer
        
        # Clear the environment variable
        with patch.dict(os.environ, {}, clear=True):
            server = PurviewMCPServer()
            with pytest.raises(ValueError, match="PURVIEW_ACCOUNT_NAME"):
                server._get_config()

    @patch.dict(
        os.environ,
        {
            "PURVIEW_ACCOUNT_NAME": "test-account",
            "PURVIEW_MAX_RETRIES": "5",
            "PURVIEW_TIMEOUT": "60",
            "PURVIEW_BATCH_SIZE": "200",
        },
    )
    def test_get_config_with_custom_values(self):
        """Test configuration with custom values"""
        # Skip if MCP not installed
        pytest.importorskip("mcp")
        
        from mcp.server import PurviewMCPServer
        
        server = PurviewMCPServer()
        config = server._get_config()
        
        assert config.account_name == "test-account"
        assert config.max_retries == 5
        assert config.timeout == 60
        assert config.batch_size == 200


class TestMCPServerTools:
    """Test MCP server tool definitions"""

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test that tools are properly defined"""
        # Skip if MCP not installed
        pytest.importorskip("mcp")
        
        from mcp.server import PurviewMCPServer
        
        with patch.dict(os.environ, {"PURVIEW_ACCOUNT_NAME": "test-account"}):
            server = PurviewMCPServer()
            
            # Get the list_tools handler
            # Note: This is a simplified test - in practice, MCP handlers are more complex
            # We're just verifying the structure is correct
            
            # Check that server has the expected structure
            assert hasattr(server, "server")
            assert hasattr(server, "client")
            assert hasattr(server, "_get_config")
            assert hasattr(server, "_ensure_client")
            assert hasattr(server, "_setup_handlers")
            assert hasattr(server, "_execute_tool")

    def test_tool_names_are_documented(self):
        """Test that all tools mentioned in README are implemented"""
        readme_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "mcp", "README.md"
        )
        
        with open(readme_path, "r") as f:
            readme_content = f.read()
        
        # Check for key tool names in README
        expected_tools = [
            "get_entity",
            "create_entity",
            "search_entities",
            "get_lineage",
            "list_collections",
            "get_glossary_terms",
            "import_entities_from_csv",
            "export_entities_to_csv",
            "get_account_properties",
        ]
        
        for tool in expected_tools:
            assert tool in readme_content, f"Tool {tool} should be documented in README"


class TestMCPServerExecution:
    """Test MCP server tool execution"""

    @pytest.mark.asyncio
    async def test_execute_tool_get_entity(self):
        """Test execute_tool for get_entity"""
        # Skip if MCP not installed
        pytest.importorskip("mcp")
        
        from mcp.server import PurviewMCPServer
        
        with patch.dict(os.environ, {"PURVIEW_ACCOUNT_NAME": "test-account"}):
            server = PurviewMCPServer()
            
            # Mock the client
            server.client = AsyncMock()
            server.client.get_entity = AsyncMock(return_value={"guid": "test-guid"})
            
            result = await server._execute_tool("get_entity", {"guid": "test-guid"})
            
            assert result == {"guid": "test-guid"}
            server.client.get_entity.assert_called_once_with("test-guid")

    @pytest.mark.asyncio
    async def test_execute_tool_search_entities(self):
        """Test execute_tool for search_entities"""
        # Skip if MCP not installed
        pytest.importorskip("mcp")
        
        from mcp.server import PurviewMCPServer
        
        with patch.dict(os.environ, {"PURVIEW_ACCOUNT_NAME": "test-account"}):
            server = PurviewMCPServer()
            
            # Mock the client
            server.client = AsyncMock()
            server.client.search_entities = AsyncMock(return_value={"value": []})
            
            result = await server._execute_tool(
                "search_entities",
                {"query": "test", "limit": 50, "offset": 0}
            )
            
            assert result == {"value": []}
            server.client.search_entities.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_tool_unknown_tool(self):
        """Test execute_tool with unknown tool name"""
        # Skip if MCP not installed
        pytest.importorskip("mcp")
        
        from mcp.server import PurviewMCPServer
        
        with patch.dict(os.environ, {"PURVIEW_ACCOUNT_NAME": "test-account"}):
            server = PurviewMCPServer()
            server.client = AsyncMock()
            
            with pytest.raises(ValueError, match="Unknown tool"):
                await server._execute_tool("nonexistent_tool", {})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
