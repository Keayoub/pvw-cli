"""
MCP Server for Microsoft Purview CLI
Enables LLM-powered data governance workflows
"""

__version__ = "1.0.0"

from .server import PurviewMCPServer

__all__ = ["PurviewMCPServer", "__version__"]
