#!/usr/bin/env python3
"""
CSV Generator for All Purview CLI Commands
==========================================

This script extracts all CLI commands from the purviewcli modules and generates
a comprehensive CSV file with all entities and operations.
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

class CSVGenerator:
    """Generate comprehensive CSV from CLI modules"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent
        self.cli_dir = self.base_dir / "purviewcli" / "cli"
        self.output_file = self.base_dir / "doc" / "boilerplate" / "boilerplate.csv"
        
        # Command group to API category mapping
        self.category_mapping = {
            'account': 'Account Management',
            'entity': 'Catalog Data Plane',
            'glossary': 'Catalog Data Plane',
            'types': 'Catalog Data Plane',
            'relationship': 'Catalog Data Plane',
            'search': 'Discovery Data Plane',
            'lineage': 'Discovery Data Plane',
            'scan': 'Scanning Data Plane',
            'management': 'Management Data Plane',
            'policystore': 'Policy Data Plane',
            'insight': 'Analytics Data Plane',
            'share': 'Share Data Plane'
        }
        
        # Method mapping based on command patterns
        self.method_mapping = {
            'create': 'POST',
            'put': 'PUT',
            'update': 'PUT',
            'add': 'POST',
            'set': 'POST',
            'delete': 'DELETE',
            'remove': 'DELETE',
            'cancel': 'POST',
            'run': 'POST',
            'read': 'GET',
            'get': 'GET',
            'list': 'GET',
            'browse': 'GET',
            'query': 'GET',
            'suggest': 'GET',
            'autocomplete': 'GET',
            'regenerate': 'POST',
            'check': 'GET',
            'import': 'POST',
            'export': 'GET',
            'tag': 'POST',
            'reinstate': 'POST',
            'revoke': 'DELETE',
            'reject': 'DELETE',
            'activate': 'POST',
            'register': 'POST'
        }
    
    def extract_all_commands(self) -> List[Dict[str, Any]]:
        """Extract all commands from CLI modules"""
        all_commands = []
        
        for cli_file in self.cli_dir.glob("*.py"):
            if cli_file.name == "__init__.py" or cli_file.name == "cli.py":
                continue
                
            commands = self._parse_cli_module(cli_file)
            all_commands.extend(commands)
        
        return all_commands
    
    def _parse_cli_module(self, module_path: Path) -> List[Dict[str, Any]]:
        """Parse a single CLI module for commands"""
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the docstring
            docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if not docstring_match:
                return []
            
            docstring_content = docstring_match.group(1)
            module_name = module_path.stem
            
            commands = []
            usage_section = False
            
            for line in docstring_content.split('\n'):
                line = line.strip()
                
                if line.startswith('usage:'):
                    usage_section = True
                    continue
                elif line.startswith('options:') or (line == '' and usage_section):
                    if line.startswith('options:'):
                        usage_section = False
                    continue
                
                if usage_section and line.startswith('pvw'):
                    command_info = self._parse_command_line(line, module_name)
                    if command_info:
                        commands.append(command_info)
            
            return commands
            
        except Exception as e:
            print(f"Error parsing {module_path}: {e}")
            return []
    
    def _parse_command_line(self, line: str, module_name: str) -> Dict[str, Any]:
        """Parse a single command line"""
        parts = line.split()
        if len(parts) < 3 or parts[0] != 'pvw' or parts[1] != module_name:
            return None
        
        action = parts[2]
        full_syntax = line
        
        # Determine HTTP method
        method = self._determine_method(action)
        
        # Generate endpoint
        endpoint = self._generate_endpoint(module_name, action)
        
        # Generate description
        description = self._generate_description(action, module_name)
        
        # Get category info
        h1 = self.category_mapping.get(module_name, 'Data Plane')
        h2 = module_name.title()
        h3 = action.title().replace('_', ' ')
        
        # Generate documentation link
        doc_link = self._generate_doc_link(module_name, action)
        
        return {
            'H1': h1,
            'H2': h2,
            'H3': h3,
            'Syntax': full_syntax,
            'Description': description,
            'Doc': doc_link,
            'Method': method,
            'Endpoint': endpoint
        }
    
    def _determine_method(self, action: str) -> str:
        """Determine HTTP method based on action name"""
        action_lower = action.lower()
        
        # Check for exact matches first
        for pattern, method in self.method_mapping.items():
            if action_lower.startswith(pattern):
                return method
        
        # Default to GET for read operations, POST for others
        if any(read_word in action_lower for read_word in ['read', 'get', 'list', 'browse', 'query', 'search']):
            return 'GET'
        elif any(write_word in action_lower for write_word in ['create', 'add', 'put', 'update', 'set', 'import']):
            return 'POST'
        elif any(delete_word in action_lower for delete_word in ['delete', 'remove', 'cancel']):
            return 'DELETE'
        else:
            return 'GET'  # Default
    
    def _generate_endpoint(self, module_name: str, action: str) -> str:
        """Generate API endpoint URL"""
        base_patterns = {
            'account': 'https://{accountName}.purview.azure.com/account/api',
            'entity': 'https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity',
            'glossary': 'https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary',
            'types': 'https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types',
            'relationship': 'https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship',
            'search': 'https://{accountName}.purview.azure.com/catalog/api/search',
            'lineage': 'https://{accountName}.purview.azure.com/catalog/api/atlas/v2/lineage',
            'scan': 'https://{accountName}.purview.azure.com/scan/api',
            'management': 'https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Purview',
            'policystore': 'https://{accountName}.purview.azure.com/policystore/api',
            'insight': 'https://{accountName}.purview.azure.com/catalog/api/browse',
            'share': 'https://{accountName}.purview.azure.com/share/api'
        }
        
        base_url = base_patterns.get(module_name, f'https://{{accountName}}.purview.azure.com/{module_name}/api')
        
        # Add action-specific path
        if module_name == 'entity':
            if 'bulk' in action.lower():
                return f"{base_url}/bulk"
            elif 'uniqueattribute' in action.lower():
                return f"{base_url}/uniqueAttribute"
            elif 'businessmetadata' in action.lower():
                return f"{base_url}/businessmetadata"
            elif 'classification' in action.lower():
                return f"{base_url}/classification"
            elif 'label' in action.lower():
                return f"{base_url}/labels"
            else:
                return f"{base_url}/{action}"
        
        return f"{base_url}/{action}"
    
    def _generate_description(self, action: str, module_name: str) -> str:
        """Generate human-readable description"""
        action_descriptions = {
            'create': 'Create a new',
            'put': 'Create or update',
            'update': 'Update an existing',
            'add': 'Add',
            'set': 'Set',
            'delete': 'Delete',
            'remove': 'Remove',
            'read': 'Retrieve',
            'get': 'Get',
            'list': 'List all',
            'browse': 'Browse',
            'query': 'Query',
            'search': 'Search for',
            'suggest': 'Get suggestions for',
            'cancel': 'Cancel',
            'run': 'Execute',
            'import': 'Import',
            'export': 'Export',
            'regenerate': 'Regenerate',
            'check': 'Check',
            'activate': 'Activate',
            'register': 'Register',
            'reinstate': 'Reinstate',
            'revoke': 'Revoke',
            'reject': 'Reject'
        }
        
        # Find matching action prefix
        action_lower = action.lower()
        description_prefix = None
        
        for prefix, desc in action_descriptions.items():
            if action_lower.startswith(prefix):
                description_prefix = desc
                break
        
        if not description_prefix:
            description_prefix = "Perform operation on"
        
        # Add context based on module
        module_context = {
            'account': 'account',
            'entity': 'entity',
            'glossary': 'glossary term or category',
            'types': 'type definition',
            'relationship': 'relationship',
            'search': 'catalog',
            'lineage': 'lineage',
            'scan': 'data source scan',
            'management': 'Purview account',
            'policystore': 'policy',
            'insight': 'analytics insights',
            'share': 'data share'
        }
        
        context = module_context.get(module_name, module_name)
        
        # Create full description
        if description_prefix.endswith('all'):
            return f"{description_prefix} {context}s."
        elif description_prefix in ['Add', 'Set', 'Remove']:
            return f"{description_prefix} {action.replace(description_prefix.lower(), '').strip()} for {context}."
        else:
            return f"{description_prefix} {context}."
    
    def _generate_doc_link(self, module_name: str, action: str) -> str:
        """Generate Microsoft documentation link"""
        base_doc_url = "https://docs.microsoft.com/en-us/rest/api/purview"
        
        api_sections = {
            'account': 'accounts',
            'entity': 'catalogdataplane/entity',
            'glossary': 'catalogdataplane/glossary',
            'types': 'catalogdataplane/types',
            'relationship': 'catalogdataplane/relationship',
            'search': 'catalogdataplane/discovery',
            'lineage': 'catalogdataplane/lineage',
            'scan': 'scanningdataplane',
            'management': 'accounts',
            'policystore': 'policystore',
            'insight': 'catalogdataplane/browse',
            'share': 'share'
        }
        
        section = api_sections.get(module_name, module_name)
        action_slug = action.lower().replace('_', '-')
        
        return f"{base_doc_url}/{section}/{action_slug}"
    
    def generate_csv(self):
        """Generate the complete CSV file"""
        print("Extracting all CLI commands...")
        commands = self.extract_all_commands()
        
        print(f"Found {len(commands)} commands across all modules")
        
        # Write to CSV
        with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['H1', 'H2', 'H3', 'Syntax', 'Description', 'Doc', 'Method', 'Endpoint']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Sort commands by module and action
            commands.sort(key=lambda x: (x['H2'], x['H3']))
            
            # Write all commands
            for command in commands:
                writer.writerow(command)
        
        print(f"Generated complete CSV file: {self.output_file}")
        print(f"Total entries: {len(commands)}")
        
        # Print summary by module
        module_counts = {}
        for command in commands:
            module = command['H2']
            module_counts[module] = module_counts.get(module, 0) + 1
        
        print("\nCommands per module:")
        for module, count in sorted(module_counts.items()):
            print(f"  {module}: {count}")

def main():
    """Main function"""
    generator = CSVGenerator()
    generator.generate_csv()

if __name__ == "__main__":
    main()
