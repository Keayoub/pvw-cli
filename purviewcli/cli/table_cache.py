"""
Rich Table Schema Caching
Caches Rich table column definitions and styles for reuse across similar commands.
Reduces table rendering overhead in report generation.
"""

from typing import Dict, Optional, List
from rich.table import Table
from rich.console import Console


class TableSchemaCache:
    """
    Cache and reuse Rich table schemas/templates.
    
    Stores table definitions (columns, styles) to avoid regenerating
    headers and formatting for repeated report commands.
    """
    
    def __init__(self):
        self._schemas: Dict[str, List[Dict[str, str]]] = {}
        self._console = Console()
    
    def register_schema(self, schema_name: str, columns: List[Dict[str, str]]) -> None:
        """
        Register a table schema for reuse.
        
        Args:
            schema_name: Unique name for this schema (e.g., "entity_list_table")
            columns: List of column definitions, each with:
                - "header": Column header text
                - "style": Rich style (e.g., "cyan", "green", "bold")
                - "no_wrap": Optional bool to prevent wrapping
        
        Example:
            cache.register_schema("entity_list", [
                {"header": "GUID", "style": "cyan"},
                {"header": "Type", "style": "green"},
                {"header": "Name", "style": "bold white"},
            ])
        """
        self._schemas[schema_name] = columns
    
    def create_table_from_schema(
        self, schema_name: str, title: Optional[str] = None
    ) -> Optional[Table]:
        """
        Create a new table from a cached schema.
        
        Args:
            schema_name: Name of registered schema
            title: Optional title for this table instance
        
        Returns:
            Configured Table with columns, or None if schema not found
        """
        if schema_name not in self._schemas:
            return None
        
        table = Table(title=title or schema_name)
        columns = self._schemas[schema_name]
        
        for col_def in columns:
            no_wrap = col_def.get("no_wrap", False)
            table.add_column(
                col_def["header"],
                style=col_def.get("style", ""),
                no_wrap=no_wrap,
            )
        
        return table
    
    def list_schemas(self) -> List[str]:
        """Get list of all registered schemas"""
        return list(self._schemas.keys())
    
    def get_schema(self, schema_name: str) -> Optional[List[Dict[str, str]]]:
        """Get schema definition by name"""
        return self._schemas.get(schema_name)


# Global table schema cache instance
_global_table_cache = TableSchemaCache()

# Pre-register common table schemas
_global_table_cache.register_schema(
    "entity_summary",
    [
        {"header": "GUID", "style": "cyan"},
        {"header": "Type", "style": "green"},
        {"header": "Name", "style": "bold white"},
        {"header": "Qualified Name", "style": "dim"},
    ],
)

_global_table_cache.register_schema(
    "entity_list",
    [
        {"header": "GUID", "style": "cyan"},
        {"header": "Type", "style": "green"},
        {"header": "Name", "style": "white"},
        {"header": "Status", "style": "yellow"},
    ],
)

_global_table_cache.register_schema(
    "glossary_terms",
    [
        {"header": "Term GUID", "style": "cyan"},
        {"header": "Term Name", "style": "bold white"},
        {"header": "Glossary", "style": "green"},
        {"header": "Status", "style": "yellow"},
        {"header": "Created", "style": "dim"},
    ],
)

_global_table_cache.register_schema(
    "classifications",
    [
        {"header": "Classification", "style": "cyan"},
        {"header": "Count", "style": "green"},
        {"header": "Percentage", "style": "yellow"},
    ],
)

_global_table_cache.register_schema(
    "lineage_graph",
    [
        {"header": "Entity", "style": "bold white"},
        {"header": "Type", "style": "green"},
        {"header": "Level", "style": "cyan"},
        {"header": "Direction", "style": "yellow"},
    ],
)

_global_table_cache.register_schema(
    "search_results",
    [
        {"header": "GUID", "style": "cyan"},
        {"header": "Type", "style": "green"},
        {"header": "Name", "style": "bold white"},
        {"header": "Owner", "style": "yellow"},
        {"header": "Score", "style": "dim"},
    ],
)


def get_table_cache() -> TableSchemaCache:
    """Get the global table schema cache instance"""
    return _global_table_cache


def create_cached_table(schema_name: str, title: Optional[str] = None) -> Optional[Table]:
    """
    Create a table from a registered schema.
    
    Args:
        schema_name: Name of registered schema (e.g., "entity_summary")
        title: Optional title override
    
    Returns:
        Configured Rich Table or None
    
    Example:
        from purviewcli.cli.table_cache import create_cached_table
        
        table = create_cached_table("entity_list", title="My Entities")
        table.add_row("123-guid", "DataSet", "MyDataset")
        console.print(table)
    """
    return _global_table_cache.create_table_from_schema(schema_name, title)
