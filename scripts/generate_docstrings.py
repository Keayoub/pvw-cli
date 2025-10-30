#!/usr/bin/env python3
"""
Python Docstring Generator for Purview Client APIs
Generates comprehensive docstring boilerplate for client methods
to support MCP/LLM integration
"""

import ast
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class DocstringGenerator:
    """Generate comprehensive docstrings for client API methods"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.client_dir = self.base_dir / "purviewcli" / "client"
        self.output_dir = self.base_dir / "doc" / "boilerplate" / "generated_docstrings"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load API mapping data if available
        self.csv_file = self.base_dir / "doc" / "boilerplate" / "boilerplate.csv"
        self.api_mapping = self._load_api_mapping()
        
    def _load_api_mapping(self) -> Dict[str, Dict]:
        """Load API mapping from CSV"""
        mapping = {}
        try:
            import csv
            with open(self.csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Extract method name from syntax
                    syntax = row.get('Syntax', '')
                    if 'pvw' in syntax:
                        parts = syntax.split()
                        if len(parts) >= 3:
                            command = parts[1]
                            action = parts[2]
                            key = f"{command}_{action}"
                            mapping[key] = {
                                'description': row.get('Description', ''),
                                'method': row.get('Method', ''),
                                'endpoint': row.get('Endpoint', ''),
                                'doc_link': row.get('Doc', ''),
                                'category': row.get('H1', ''),
                                'syntax': syntax
                            }
        except Exception as e:
            print(f"Warning: Could not load API mapping: {e}")
        return mapping
    
    def generate_docstring_template(
        self, 
        method_name: str,
        parameters: List[str],
        is_async: bool = False,
        api_info: Optional[Dict] = None
    ) -> str:
        """Generate comprehensive docstring template"""
        
        # Determine operation type from method name
        operation = self._infer_operation_type(method_name)
        
        # Build docstring sections
        docstring_parts = []
        
        # Description section
        description = self._generate_description(method_name, operation, api_info)
        docstring_parts.append(description)
        
        # Args section
        if parameters:
            args_section = self._generate_args_section(parameters, method_name, api_info)
            docstring_parts.append(args_section)
        
        # Returns section
        returns_section = self._generate_returns_section(operation, method_name)
        docstring_parts.append(returns_section)
        
        # Raises section
        raises_section = self._generate_raises_section(operation)
        docstring_parts.append(raises_section)
        
        # Example section
        example_section = self._generate_example_section(method_name, parameters, is_async)
        docstring_parts.append(example_section)
        
        # Use Cases section
        use_cases_section = self._generate_use_cases_section(operation, method_name)
        docstring_parts.append(use_cases_section)
        
        # Combine all sections
        docstring = '    """\n'
        docstring += '\n    \n'.join(docstring_parts)
        docstring += '\n    """'
        
        return docstring
    
    def _infer_operation_type(self, method_name: str) -> str:
        """Infer operation type from method name"""
        name_lower = method_name.lower()
        
        if any(x in name_lower for x in ['create', 'add', 'post']):
            return 'create'
        elif any(x in name_lower for x in ['read', 'get', 'list', 'retrieve', 'fetch']):
            return 'read'
        elif any(x in name_lower for x in ['update', 'put', 'patch', 'modify', 'set']):
            return 'update'
        elif any(x in name_lower for x in ['delete', 'remove', 'purge']):
            return 'delete'
        elif any(x in name_lower for x in ['search', 'query', 'find', 'browse']):
            return 'search'
        elif any(x in name_lower for x in ['import', 'export', 'bulk']):
            return 'batch'
        else:
            return 'custom'
    
    def _generate_description(
        self, 
        method_name: str, 
        operation: str, 
        api_info: Optional[Dict]
    ) -> str:
        """Generate description section"""
        
        # Use API mapping description if available
        if api_info and api_info.get('description'):
            base_desc = api_info['description']
        else:
            # Generate generic description based on operation
            operation_desc = {
                'create': 'Create a new resource',
                'read': 'Retrieve resource information',
                'update': 'Update an existing resource',
                'delete': 'Delete a resource',
                'search': 'Search for resources',
                'batch': 'Perform batch operation on resources'
            }
            base_desc = operation_desc.get(operation, 'Perform operation on resource')
        
        # Enhanced description with context
        desc = f"{base_desc}.\n    \n    "
        
        # Add operation-specific guidance
        if operation == 'create':
            desc += "Creates a new resource in Microsoft Purview.\n    "
            desc += "Requires appropriate permissions and valid resource definition."
        elif operation == 'read':
            desc += "Retrieves detailed information about the specified resource.\n    "
            desc += "Returns complete resource metadata and properties."
        elif operation == 'update':
            desc += "Updates an existing resource with new values.\n    "
            desc += "Only specified fields are modified; others remain unchanged."
        elif operation == 'delete':
            desc += "Permanently deletes the specified resource.\n    "
            desc += "This operation cannot be undone. Use with caution."
        elif operation == 'search':
            desc += "Searches for resources matching the specified criteria.\n    "
            desc += "Supports filtering, pagination, and sorting."
        elif operation == 'batch':
            desc += "Processes multiple resources in a single operation.\n    "
            desc += "More efficient than individual operations for bulk data."
        
        if api_info and api_info.get('doc_link'):
            desc += f"\n    \n    Official API: {api_info['doc_link']}"
        
        return desc
    
    def _generate_args_section(
        self, 
        parameters: List[str], 
        method_name: str,
        api_info: Optional[Dict]
    ) -> str:
        """Generate Args section"""
        args = "Args:\n"
        
        for param in parameters:
            if param == 'self':
                continue
            
            # Infer parameter purpose
            param_lower = param.lower()
            
            if 'guid' in param_lower or 'id' in param_lower:
                args += f"        {param}: Unique identifier (GUID) of the resource.\n"
                args += f"               Format: UUID (e.g., '550e8400-e29b-41d4-a716-446655440000')\n"
                args += f"               Required: Yes\n"
            
            elif 'name' in param_lower:
                args += f"        {param}: Name of the resource.\n"
                args += f"               Must be unique within the scope.\n"
                args += f"               Required: Yes\n"
            
            elif 'payload' in param_lower or 'data' in param_lower or 'body' in param_lower:
                args += f"        {param}: Resource definition dictionary.\n"
                args += f"               Structure depends on resource type.\n"
                args += f"               See API documentation for schema.\n"
                args += f"               Required: Yes\n"
            
            elif 'limit' in param_lower:
                args += f"        {param}: Maximum number of results to return.\n"
                args += f"               Range: 1-1000 (default: 100)\n"
                args += f"               Used for pagination.\n"
            
            elif 'offset' in param_lower or 'skip' in param_lower:
                args += f"        {param}: Number of results to skip.\n"
                args += f"               Default: 0\n"
                args += f"               Use with limit for pagination.\n"
            
            elif 'filter' in param_lower:
                args += f"        {param}: Filter criteria for results.\n"
                args += f"               Supports field-based filtering.\n"
                args += f"               Optional.\n"
            
            elif 'sort' in param_lower or 'order' in param_lower:
                args += f"        {param}: Sort order for results.\n"
                args += f"               Format: 'fieldName ASC' or 'fieldName DESC'\n"
                args += f"               Optional.\n"
            
            elif 'args' in param_lower:
                args += f"        {param}: Dictionary of operation arguments.\n"
                args += f"               Contains operation-specific parameters.\n"
                args += f"               See method implementation for details.\n"
            
            else:
                args += f"        {param}: [TODO: Add parameter description]\n"
                args += f"               [TODO: Specify type and constraints]\n"
                args += f"               [TODO: Indicate if required or optional]\n"
        
        return args.rstrip()
    
    def _generate_returns_section(self, operation: str, method_name: str) -> str:
        """Generate Returns section"""
        returns = "Returns:\n"
        
        if operation == 'create':
            returns += "        Dictionary containing created resource:\n"
            returns += "            {\n"
            returns += "                'guid': str,         # Unique identifier\n"
            returns += "                'name': str,         # Resource name\n"
            returns += "                'status': str,       # Creation status\n"
            returns += "                'attributes': dict,  # Resource attributes\n"
            returns += "                'createTime': int    # Creation timestamp\n"
            returns += "            }\n"
        
        elif operation == 'read':
            if 'list' in method_name.lower() or 'search' in method_name.lower():
                returns += "        List of resource dictionaries, each containing:\n"
                returns += "            - guid (str): Unique identifier\n"
                returns += "            - name (str): Resource name\n"
                returns += "            - attributes (dict): Resource attributes\n"
                returns += "            - status (str): Resource status\n"
                returns += "        \n"
                returns += "        Returns empty list if no resources found.\n"
            else:
                returns += "        Dictionary containing resource information:\n"
                returns += "            {\n"
                returns += "                'guid': str,          # Unique identifier\n"
                returns += "                'name': str,          # Resource name\n"
                returns += "                'attributes': dict,   # Resource attributes\n"
                returns += "                'status': str,        # Resource status\n"
                returns += "                'updateTime': int     # Last update timestamp\n"
                returns += "            }\n"
        
        elif operation == 'update':
            returns += "        Dictionary containing updated resource:\n"
            returns += "            {\n"
            returns += "                'guid': str,          # Unique identifier\n"
            returns += "                'attributes': dict,   # Updated attributes\n"
            returns += "                'updateTime': int     # Update timestamp\n"
            returns += "            }\n"
        
        elif operation == 'delete':
            returns += "        Dictionary with deletion status:\n"
            returns += "            {\n"
            returns += "                'guid': str,       # Deleted resource ID\n"
            returns += "                'status': str,     # Deletion status\n"
            returns += "                'message': str     # Confirmation message\n"
            returns += "            }\n"
        
        elif operation == 'search':
            returns += "        Dictionary containing search results:\n"
            returns += "            {\n"
            returns += "                'value': [...]     # List of matching resources\n"
            returns += "                'count': int,      # Total results count\n"
            returns += "                'nextLink': str    # Pagination link (if applicable)\n"
            returns += "            }\n"
        
        elif operation == 'batch':
            returns += "        Dictionary with batch operation results:\n"
            returns += "            {\n"
            returns += "                'succeeded': int,        # Success count\n"
            returns += "                'failed': int,           # Failure count\n"
            returns += "                'results': [...],        # Per-item results\n"
            returns += "                'errors': [...]          # Error details\n"
            returns += "            }\n"
        
        else:
            returns += "        [TODO: Specify return type and structure]\n"
            returns += "        [TODO: Document nested fields]\n"
        
        return returns.rstrip()
    
    def _generate_raises_section(self, operation: str) -> str:
        """Generate Raises section"""
        raises = "Raises:\n"
        raises += "        ValueError: When required parameters are missing or invalid:\n"
        raises += "            - Empty or None values for required fields\n"
        raises += "            - Invalid GUID format\n"
        raises += "            - Out-of-range values\n"
        raises += "        \n"
        raises += "        AuthenticationError: When Azure credentials are invalid:\n"
        raises += "            - DefaultAzureCredential not configured\n"
        raises += "            - Insufficient permissions\n"
        raises += "            - Expired authentication token\n"
        raises += "        \n"
        raises += "        HTTPError: When Purview API returns error:\n"
        raises += "            - 400: Bad request (invalid parameters)\n"
        raises += "            - 401: Unauthorized (authentication failed)\n"
        raises += "            - 403: Forbidden (insufficient permissions)\n"
        raises += "            - 404: Resource not found\n"
        
        if operation == 'create':
            raises += "            - 409: Conflict (resource already exists)\n"
        
        raises += "            - 429: Rate limit exceeded\n"
        raises += "            - 500: Internal server error\n"
        raises += "        \n"
        raises += "        NetworkError: When network connectivity fails\n"
        
        return raises.rstrip()
    
    def _generate_example_section(
        self, 
        method_name: str, 
        parameters: List[str],
        is_async: bool
    ) -> str:
        """Generate Example section"""
        example = "Example:\n"
        
        # Determine client type from method name
        if 'entity' in method_name.lower():
            client_name = "EntityClient"
        elif 'glossary' in method_name.lower():
            client_name = "GlossaryClient"
        elif 'collection' in method_name.lower():
            client_name = "CollectionsClient"
        elif 'lineage' in method_name.lower():
            client_name = "LineageClient"
        else:
            client_name = "Client"
        
        example += f"        # Basic usage\n"
        example += f"        client = {client_name}()\n"
        example += f"        \n"
        
        # Generate sample call
        await_prefix = "await " if is_async else ""
        
        # Build sample arguments
        sample_args = []
        for param in parameters:
            if param == 'self':
                continue
            
            param_lower = param.lower()
            
            if 'guid' in param_lower or 'id' in param_lower:
                sample_args.append(f'{param}="550e8400-e29b-41d4-a716-446655440000"')
            elif 'name' in param_lower:
                sample_args.append(f'{param}="example-resource"')
            elif 'payload' in param_lower or 'data' in param_lower:
                sample_args.append(f'{param}={{...}}')
            elif 'limit' in param_lower:
                sample_args.append(f'{param}=50')
            else:
                sample_args.append(f'{param}=...')
        
        args_str = ', '.join(sample_args[:3])  # Limit to first 3 args
        
        example += f"        result = {await_prefix}client.{method_name}({args_str})\n"
        example += f"        print(f\"Result: {{result}}\")\n"
        
        # Add more detailed example if create/update operation
        operation = self._infer_operation_type(method_name)
        if operation in ['create', 'update']:
            example += f"        \n"
            example += f"        # With detailed data\n"
            example += f"        data = {{\n"
            example += f"            'name': 'My Resource',\n"
            example += f"            'description': 'Resource description',\n"
            example += f"            'attributes': {{\n"
            example += f"                'key1': 'value1',\n"
            example += f"                'key2': 'value2'\n"
            example += f"            }}\n"
            example += f"        }}\n"
            example += f"        \n"
            example += f"        result = {await_prefix}client.{method_name}(data)\n"
            example += f"        print(f\"Created/Updated: {{result['guid']}}\")\n"
        
        return example.rstrip()
    
    def _generate_use_cases_section(self, operation: str, method_name: str) -> str:
        """Generate Use Cases section"""
        use_cases = "Use Cases:\n"
        
        if operation == 'create':
            use_cases += "        - Data Onboarding: Register new data sources in catalog\n"
            use_cases += "        - Metadata Management: Add descriptive metadata to assets\n"
            use_cases += "        - Automation: Programmatically populate catalog\n"
        
        elif operation == 'read':
            use_cases += "        - Data Discovery: Find and explore data assets\n"
            use_cases += "        - Compliance Auditing: Review metadata and classifications\n"
            use_cases += "        - Reporting: Generate catalog reports\n"
        
        elif operation == 'update':
            use_cases += "        - Metadata Enrichment: Update descriptions and tags\n"
            use_cases += "        - Ownership Changes: Reassign data ownership\n"
            use_cases += "        - Classification: Apply or modify data classifications\n"
        
        elif operation == 'delete':
            use_cases += "        - Data Cleanup: Remove obsolete or test data\n"
            use_cases += "        - Decommissioning: Delete resources no longer in use\n"
            use_cases += "        - Testing: Clean up test environments\n"
        
        elif operation == 'search':
            use_cases += "        - Data Discovery: Locate datasets by name or properties\n"
            use_cases += "        - Impact Analysis: Find all assets related to a term\n"
            use_cases += "        - Compliance: Identify sensitive data across catalog\n"
        
        elif operation == 'batch':
            use_cases += "        - Bulk Import: Load large volumes of metadata\n"
            use_cases += "        - Migration: Transfer catalog from other systems\n"
            use_cases += "        - Mass Updates: Apply changes to many resources\n"
        
        else:
            use_cases += "        - [TODO: Add specific use cases for this operation]\n"
            use_cases += "        - [TODO: Include business context]\n"
            use_cases += "        - [TODO: Explain when to use this method]\n"
        
        return use_cases.rstrip()
    
    def generate_for_method(
        self,
        module_path: Path,
        class_name: str,
        method_name: str,
        method_node: ast.FunctionDef
    ) -> str:
        """Generate docstring for a specific method"""
        
        # Extract parameters
        parameters = [arg.arg for arg in method_node.args.args]
        
        # Check if async
        is_async = isinstance(method_node, ast.AsyncFunctionDef)
        
        # Look up API info
        api_key = f"{class_name.lower()}_{method_name}"
        api_info = self.api_mapping.get(api_key)
        
        # Generate docstring
        docstring = self.generate_docstring_template(
            method_name=method_name,
            parameters=parameters,
            is_async=is_async,
            api_info=api_info
        )
        
        return docstring
    
    def generate_for_module(self, module_file: str) -> Dict[str, str]:
        """Generate docstrings for all methods in a module"""
        module_path = self.client_dir / module_file
        
        with open(module_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        docstrings = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name
                
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not item.name.startswith('_'):  # Public methods only
                            method_key = f"{class_name}.{item.name}"
                            docstring = self.generate_for_method(
                                module_path, class_name, item.name, item
                            )
                            docstrings[method_key] = docstring
        
        return docstrings
    
    def save_docstrings_to_file(self, module_file: str, docstrings: Dict[str, str]):
        """Save generated docstrings to file"""
        output_file = self.output_dir / f"{module_file}.docstrings.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Generated Docstrings for {module_file}\n")
            f.write(f"# Copy these to your Python source file\n\n")
            
            for method_key, docstring in docstrings.items():
                f.write(f"## {method_key}\n")
                f.write(f"{docstring}\n\n")
                f.write("=" * 80 + "\n\n")
        
        print(f"✓ Saved docstrings to {output_file}")
        return output_file


def main():
    """Main entry point"""
    import sys
    
    generator = DocstringGenerator()
    
    if len(sys.argv) > 1:
        # Generate for specific module
        module_file = sys.argv[1]
        print(f"Generating docstrings for {module_file}...")
        
        docstrings = generator.generate_for_module(module_file)
        output_file = generator.save_docstrings_to_file(module_file, docstrings)
        
        print(f"\nGenerated {len(docstrings)} docstrings")
        print(f"Output: {output_file}")
    else:
        # Generate for common modules
        priority_modules = [
            "_entity.py",
            "_glossary.py",
            "_collections.py",
            "_unified_catalog.py",
            "_lineage.py",
            "_search.py"
        ]
        
        print("Generating docstrings for priority modules...")
        print("=" * 60)
        
        for module in priority_modules:
            module_path = generator.client_dir / module
            if module_path.exists():
                print(f"\n{module}:")
                docstrings = generator.generate_for_module(module)
                generator.save_docstrings_to_file(module, docstrings)
                print(f"  Generated {len(docstrings)} docstrings")
            else:
                print(f"  Skipped (not found)")
        
        print("\n" + "=" * 60)
        print("Complete! Review generated files in:")
        print(f"  {generator.output_dir}")


if __name__ == "__main__":
    main()
