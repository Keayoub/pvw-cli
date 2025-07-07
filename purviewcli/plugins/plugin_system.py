"""
Plugin System for  Purview CLI
Provides extensible architecture for third-party integrations and custom functionality
"""

import asyncio
import importlib
import inspect
import json
import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Type, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class PluginType(Enum):
    """Types of plugins supported"""
    DATA_SOURCE = "data_source"
    CLASSIFICATION = "classification"
    LINEAGE = "lineage"
    EXPORT = "export"
    NOTIFICATION = "notification"
    VALIDATION = "validation"
    ENRICHMENT = "enrichment"
    CUSTOM = "custom"

class PluginStatus(Enum):
    """Plugin status"""
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"

@dataclass
class PluginMetadata:
    """Plugin metadata information"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = field(default_factory=list)
    configuration_schema: Dict[str, Any] = field(default_factory=dict)
    supported_operations: List[str] = field(default_factory=list)
    entry_point: str = "main"
    min_cli_version: str = "1.0.0"
    max_cli_version: str = ""

@dataclass
class PluginConfig:
    """Plugin configuration"""
    plugin_name: str
    enabled: bool = True
    configuration: Dict[str, Any] = field(default_factory=dict)
    priority: int = 100
    
class PluginInterface(ABC):
    """Base interface that all plugins must implement"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.console = Console()
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin. Return True if successful."""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup plugin resources"""
        pass
    
    @abstractmethod
    async def execute(self, operation: str, **kwargs) -> Any:
        """Execute a plugin operation"""
        pass
    
    def validate_configuration(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate plugin configuration. Return (is_valid, error_messages)"""
        return True, []

class DataSourcePlugin(PluginInterface):
    """Base class for data source plugins"""
    
    @abstractmethod
    async def discover_assets(self, connection_info: Dict) -> List[Dict]:
        """Discover assets from the data source"""
        pass
    
    @abstractmethod
    async def extract_metadata(self, asset_info: Dict) -> Dict:
        """Extract metadata from a specific asset"""
        pass
    
    @abstractmethod
    async def test_connection(self, connection_info: Dict) -> bool:
        """Test connection to the data source"""
        pass

class ClassificationPlugin(PluginInterface):
    """Base class for classification plugins"""
    
    @abstractmethod
    async def classify_entity(self, entity_data: Dict) -> List[str]:
        """Return list of suggested classifications for an entity"""
        pass
    
    @abstractmethod
    async def get_classification_confidence(self, entity_data: Dict, classification: str) -> float:
        """Return confidence score (0.0-1.0) for a classification"""
        pass

class ExportPlugin(PluginInterface):
    """Base class for export plugins"""
    
    @abstractmethod
    async def export_data(self, data: Any, export_config: Dict) -> str:
        """Export data to external system. Return export identifier."""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return list of supported export formats"""
        pass

class NotificationPlugin(PluginInterface):
    """Base class for notification plugins"""
    
    @abstractmethod
    async def send_notification(self, message: str, recipients: List[str], **kwargs) -> bool:
        """Send notification. Return True if successful."""
        pass
    
    @abstractmethod
    def get_supported_channels(self) -> List[str]:
        """Return list of supported notification channels"""
        pass

class PluginManager:
    """Main plugin management system"""
    
    def __init__(self, plugins_directory: str = "plugins"):
        self.plugins_directory = Path(plugins_directory)
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_configs: Dict[str, PluginConfig] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.plugin_status: Dict[str, PluginStatus] = {}
        self.console = Console()
        
        # Create plugins directory if it doesn't exist
        self.plugins_directory.mkdir(exist_ok=True)
    
    async def load_plugins(self, config_file: Optional[str] = None):
        """Load all plugins from the plugins directory"""
        
        # Load plugin configurations
        if config_file:
            await self._load_plugin_configurations(config_file)
        
        # Discover plugin files
        plugin_files = list(self.plugins_directory.glob("**/*.py"))
        plugin_files.extend(list(self.plugins_directory.glob("**/*.yaml")))
        
        for plugin_file in plugin_files:
            if plugin_file.name.startswith("__"):
                continue
                
            try:
                await self._load_single_plugin(plugin_file)
            except Exception as e:
                self.console.print(f"[red]Failed to load plugin {plugin_file}: {e}[/red]")
                continue
        
        self.console.print(f"[green]Loaded {len(self.loaded_plugins)} plugins[/green]")
    
    async def _load_plugin_configurations(self, config_file: str):
        """Load plugin configurations from file"""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                if config_path.suffix.lower() == '.yaml':
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                else:
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                
                for plugin_name, plugin_config in config_data.get('plugins', {}).items():
                    self.plugin_configs[plugin_name] = PluginConfig(
                        plugin_name=plugin_name,
                        enabled=plugin_config.get('enabled', True),
                        configuration=plugin_config.get('configuration', {}),
                        priority=plugin_config.get('priority', 100)
                    )
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load plugin config: {e}[/yellow]")
    
    async def _load_single_plugin(self, plugin_file: Path):
        """Load a single plugin file"""
        
        if plugin_file.suffix == '.py':
            await self._load_python_plugin(plugin_file)
        elif plugin_file.suffix in ['.yaml', '.yml']:
            await self._load_yaml_plugin(plugin_file)
    
    async def _load_python_plugin(self, plugin_file: Path):
        """Load a Python plugin"""
        
        try:
            # Add plugin directory to Python path
            plugin_dir = plugin_file.parent
            if str(plugin_dir) not in sys.path:
                sys.path.insert(0, str(plugin_dir))
            
            # Import the plugin module
            module_name = plugin_file.stem
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, PluginInterface) and 
                    obj != PluginInterface and 
                    not inspect.isabstract(obj)):
                    
                    # Get plugin configuration
                    plugin_config = self.plugin_configs.get(name, PluginConfig(name))
                    
                    if not plugin_config.enabled:
                        self.plugin_status[name] = PluginStatus.DISABLED
                        continue
                    
                    # Create plugin instance
                    plugin_instance = obj(plugin_config.configuration)
                    
                    # Get metadata
                    metadata = plugin_instance.get_metadata()
                    self.plugin_metadata[name] = metadata
                    
                    # Initialize plugin
                    if await plugin_instance.initialize():
                        self.loaded_plugins[name] = plugin_instance
                        self.plugin_status[name] = PluginStatus.ACTIVE
                        self.console.print(f"[green]✓ Loaded plugin: {name} v{metadata.version}[/green]")
                    else:
                        self.plugin_status[name] = PluginStatus.ERROR
                        self.console.print(f"[red]✗ Failed to initialize plugin: {name}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]Error loading Python plugin {plugin_file}: {e}[/red]")
    
    async def _load_yaml_plugin(self, plugin_file: Path):
        """Load a YAML-based plugin configuration"""
        
        try:
            with open(plugin_file, 'r') as f:
                plugin_spec = yaml.safe_load(f)
            
            plugin_name = plugin_spec.get('name')
            if not plugin_name:
                return
            
            # Create metadata from YAML
            metadata = PluginMetadata(
                name=plugin_name,
                version=plugin_spec.get('version', '1.0.0'),
                description=plugin_spec.get('description', ''),
                author=plugin_spec.get('author', ''),
                plugin_type=PluginType(plugin_spec.get('type', 'custom')),
                dependencies=plugin_spec.get('dependencies', []),
                configuration_schema=plugin_spec.get('configuration_schema', {}),
                supported_operations=plugin_spec.get('supported_operations', [])
            )
            
            self.plugin_metadata[plugin_name] = metadata
            self.plugin_status[plugin_name] = PluginStatus.LOADED
            
        except Exception as e:
            self.console.print(f"[red]Error loading YAML plugin {plugin_file}: {e}[/red]")
    
    async def execute_plugin_operation(
        self, 
        plugin_name: str, 
        operation: str, 
        **kwargs
    ) -> Any:
        """Execute an operation on a specific plugin"""
        
        if plugin_name not in self.loaded_plugins:
            raise ValueError(f"Plugin '{plugin_name}' not found or not loaded")
        
        plugin = self.loaded_plugins[plugin_name]
        
        try:
            result = await plugin.execute(operation, **kwargs)
            return result
        except Exception as e:
            self.console.print(f"[red]Error executing {operation} on {plugin_name}: {e}[/red]")
            raise
    
    async def execute_plugin_chain(
        self, 
        plugin_type: PluginType, 
        operation: str, 
        data: Any,
        **kwargs
    ) -> List[Any]:
        """Execute an operation across all plugins of a specific type"""
        
        results = []
        
        # Get plugins of the specified type, sorted by priority
        type_plugins = [
            (name, plugin) for name, plugin in self.loaded_plugins.items()
            if self.plugin_metadata[name].plugin_type == plugin_type
        ]
        
        # Sort by priority (lower numbers = higher priority)
        type_plugins.sort(key=lambda x: self.plugin_configs.get(x[0], PluginConfig(x[0])).priority)
        
        for plugin_name, plugin in type_plugins:
            try:
                result = await plugin.execute(operation, data=data, **kwargs)
                results.append({
                    'plugin_name': plugin_name,
                    'result': result,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'plugin_name': plugin_name,
                    'result': None,
                    'success': False,
                    'error': str(e)
                })
                self.console.print(f"[yellow]Warning: Plugin {plugin_name} failed: {e}[/yellow]")
        
        return results
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[str]:
        """Get list of plugin names by type"""
        return [
            name for name, metadata in self.plugin_metadata.items()
            if metadata.plugin_type == plugin_type and name in self.loaded_plugins
        ]
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific plugin"""
        
        if plugin_name not in self.plugin_metadata:
            return None
        
        metadata = self.plugin_metadata[plugin_name]
        status = self.plugin_status.get(plugin_name, PluginStatus.ERROR)
        config = self.plugin_configs.get(plugin_name, PluginConfig(plugin_name))
        
        return {
            'name': metadata.name,
            'version': metadata.version,
            'description': metadata.description,
            'author': metadata.author,
            'type': metadata.plugin_type.value,
            'status': status.value,
            'enabled': config.enabled,
            'dependencies': metadata.dependencies,
            'supported_operations': metadata.supported_operations,
            'configuration': config.configuration
        }
    
    def list_plugins(self) -> Table:
        """Create a table listing all plugins"""
        
        table = Table(title="Loaded Plugins", show_header=True, header_style="bold magenta")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Status", style="blue")
        table.add_column("Description")
        
        for plugin_name in sorted(self.plugin_metadata.keys()):
            metadata = self.plugin_metadata[plugin_name]
            status = self.plugin_status.get(plugin_name, PluginStatus.ERROR)
            
            # Set status color
            status_color = {
                PluginStatus.ACTIVE: "green",
                PluginStatus.LOADED: "yellow",
                PluginStatus.INACTIVE: "blue",
                PluginStatus.ERROR: "red",
                PluginStatus.DISABLED: "gray"
            }.get(status, "white")
            
            table.add_row(
                plugin_name,
                metadata.version,
                metadata.plugin_type.value,
                f"[{status_color}]{status.value}[/{status_color}]",
                metadata.description[:50] + "..." if len(metadata.description) > 50 else metadata.description
            )
        
        return table
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        
        try:
            # Cleanup existing plugin
            if plugin_name in self.loaded_plugins:
                await self.loaded_plugins[plugin_name].cleanup()
                del self.loaded_plugins[plugin_name]
            
            # Find and reload plugin file
            plugin_files = list(self.plugins_directory.glob(f"**/{plugin_name}.py"))
            plugin_files.extend(list(self.plugins_directory.glob(f"**/{plugin_name}.yaml")))
            
            if plugin_files:
                await self._load_single_plugin(plugin_files[0])
                return plugin_name in self.loaded_plugins
            
            return False
            
        except Exception as e:
            self.console.print(f"[red]Error reloading plugin {plugin_name}: {e}[/red]")
            return False
    
    async def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a disabled plugin"""
        
        if plugin_name in self.plugin_configs:
            self.plugin_configs[plugin_name].enabled = True
        else:
            self.plugin_configs[plugin_name] = PluginConfig(plugin_name, enabled=True)
        
        return await self.reload_plugin(plugin_name)
    
    async def disable_plugin(self, plugin_name: str) -> bool:
        """Disable an active plugin"""
        
        try:
            if plugin_name in self.loaded_plugins:
                await self.loaded_plugins[plugin_name].cleanup()
                del self.loaded_plugins[plugin_name]
            
            if plugin_name in self.plugin_configs:
                self.plugin_configs[plugin_name].enabled = False
            else:
                self.plugin_configs[plugin_name] = PluginConfig(plugin_name, enabled=False)
            
            self.plugin_status[plugin_name] = PluginStatus.DISABLED
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error disabling plugin {plugin_name}: {e}[/red]")
            return False
    
    async def cleanup_all_plugins(self):
        """Cleanup all loaded plugins"""
        
        for plugin_name, plugin in self.loaded_plugins.items():
            try:
                await plugin.cleanup()
            except Exception as e:
                self.console.print(f"[yellow]Warning: Error cleaning up {plugin_name}: {e}[/yellow]")
        
        self.loaded_plugins.clear()
    
    def export_plugin_configuration(self, output_path: str):
        """Export current plugin configuration to file"""
        
        config_data = {
            'plugins': {}
        }
        
        for plugin_name, config in self.plugin_configs.items():
            config_data['plugins'][plugin_name] = {
                'enabled': config.enabled,
                'configuration': config.configuration,
                'priority': config.priority
            }
        
        output_file = Path(output_path)
        
        if output_file.suffix.lower() == '.yaml':
            with open(output_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False)
        else:
            with open(output_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        
        self.console.print(f"[green]Plugin configuration exported to {output_path}[/green]")

class PluginRegistry:
    """Registry for discovering and managing available plugins"""
    
    def __init__(self):
        self.console = Console()
        self.registry_url = "https://pvw-cli-plugins.registry.example.com"  # Example URL
    
    def search_plugins(self, query: str, plugin_type: Optional[PluginType] = None) -> List[Dict]:
        """Search for plugins in the registry"""
        
        # This would normally query a remote registry
        # For now, return mock data
        
        mock_plugins = [
            {
                'name': 'snowflake-connector',
                'version': '1.2.0',
                'description': 'Snowflake data source connector',
                'type': 'data_source',
                'author': 'Community',
                'downloads': 1250,
                'rating': 4.5
            },
            {
                'name': 'pii-classifier',
                'version': '2.1.0',
                'description': 'Advanced PII classification plugin',
                'type': 'classification',
                'author': 'Security Team',
                'downloads': 890,
                'rating': 4.8
            },
            {
                'name': 'teams-notifications',
                'version': '1.0.3',
                'description': 'Microsoft Teams notification plugin',
                'type': 'notification',
                'author': 'Integration Team',
                'downloads': 650,
                'rating': 4.2
            }
        ]
        
        # Filter by query
        if query:
            query_lower = query.lower()
            mock_plugins = [
                p for p in mock_plugins 
                if query_lower in p['name'].lower() or query_lower in p['description'].lower()
            ]
        
        # Filter by type
        if plugin_type:
            mock_plugins = [
                p for p in mock_plugins 
                if p['type'] == plugin_type.value
            ]
        
        return mock_plugins
    
    def install_plugin(self, plugin_name: str, version: str = "latest") -> bool:
        """Install a plugin from the registry"""
        
        try:
            # This would normally download and install the plugin
            self.console.print(f"[green]✓ Plugin '{plugin_name}' v{version} installed successfully[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]✗ Failed to install plugin '{plugin_name}': {e}[/red]")
            return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin"""
        
        try:
            # This would normally remove the plugin files
            self.console.print(f"[green]✓ Plugin '{plugin_name}' uninstalled successfully[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]✗ Failed to uninstall plugin '{plugin_name}': {e}[/red]")
            return False
    
    def update_plugin(self, plugin_name: str) -> bool:
        """Update a plugin to the latest version"""
        
        try:
            # This would normally check for updates and install them
            self.console.print(f"[green]✓ Plugin '{plugin_name}' updated successfully[/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]✗ Failed to update plugin '{plugin_name}': {e}[/red]")
            return False

# Example plugin implementations

class ExampleDataSourcePlugin(DataSourcePlugin):
    """Example data source plugin implementation"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="example-datasource",
            version="1.0.0",
            description="Example data source plugin for demonstration",
            author="CLI Team",
            plugin_type=PluginType.DATA_SOURCE,
            supported_operations=["discover_assets", "extract_metadata", "test_connection"]
        )
    
    async def initialize(self) -> bool:
        self.console.print("[green]Example DataSource Plugin initialized[/green]")
        return True
    
    async def cleanup(self):
        self.console.print("[yellow]Example DataSource Plugin cleaned up[/yellow]")
    
    async def execute(self, operation: str, **kwargs) -> Any:
        if operation == "discover_assets":
            return await self.discover_assets(kwargs.get('connection_info', {}))
        elif operation == "extract_metadata":
            return await self.extract_metadata(kwargs.get('asset_info', {}))
        elif operation == "test_connection":
            return await self.test_connection(kwargs.get('connection_info', {}))
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def discover_assets(self, connection_info: Dict) -> List[Dict]:
        # Mock asset discovery
        return [
            {"name": "table1", "type": "table", "schema": "public"},
            {"name": "table2", "type": "table", "schema": "public"}
        ]
    
    async def extract_metadata(self, asset_info: Dict) -> Dict:
        # Mock metadata extraction
        return {
            "columns": [
                {"name": "id", "type": "integer"},
                {"name": "name", "type": "varchar"}
            ],
            "row_count": 1000
        }
    
    async def test_connection(self, connection_info: Dict) -> bool:
        # Mock connection test
        return True

class ExampleClassificationPlugin(ClassificationPlugin):
    """Example classification plugin implementation"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="example-classifier",
            version="1.0.0",
            description="Example classification plugin for demonstration",
            author="CLI Team",
            plugin_type=PluginType.CLASSIFICATION,
            supported_operations=["classify_entity", "get_classification_confidence"]
        )
    
    async def initialize(self) -> bool:
        self.console.print("[green]Example Classification Plugin initialized[/green]")
        return True
    
    async def cleanup(self):
        self.console.print("[yellow]Example Classification Plugin cleaned up[/yellow]")
    
    async def execute(self, operation: str, **kwargs) -> Any:
        if operation == "classify_entity":
            return await self.classify_entity(kwargs.get('entity_data', {}))
        elif operation == "get_classification_confidence":
            return await self.get_classification_confidence(
                kwargs.get('entity_data', {}),
                kwargs.get('classification', '')
            )
        else:
            raise ValueError(f"Unsupported operation: {operation}")
    
    async def classify_entity(self, entity_data: Dict) -> List[str]:
        # Mock classification logic
        entity_name = entity_data.get('name', '').lower()
        
        classifications = []
        if 'customer' in entity_name:
            classifications.append('CustomerData')
        if 'email' in entity_name:
            classifications.append('PersonalData')
        if 'financial' in entity_name or 'money' in entity_name:
            classifications.append('FinancialData')
        
        return classifications or ['GeneralData']
    
    async def get_classification_confidence(self, entity_data: Dict, classification: str) -> float:
        # Mock confidence calculation
        entity_name = entity_data.get('name', '').lower()
        
        confidence_map = {
            'CustomerData': 0.9 if 'customer' in entity_name else 0.1,
            'PersonalData': 0.8 if 'email' in entity_name else 0.2,
            'FinancialData': 0.85 if any(term in entity_name for term in ['financial', 'money']) else 0.15
        }
        
        return confidence_map.get(classification, 0.5)
