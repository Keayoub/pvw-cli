#!/usr/bin/env python3
"""
Consolidated Documentation Generator for Purview CLI
Combines CSV data with CLI analysis to generate comprehensive documentation
matching the existing doc/commands structure with individual .md files per operation
"""
import ast
import csv
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

class ConsolidatedDocGenerator:
    """Consolidated documentation generator for Purview CLI"""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent.parent
        self.cli_dir = self.base_dir / "purviewcli" / "cli"
        self.client_dir = self.base_dir / "purviewcli" / "client"
        self.output_dir = self.base_dir / "doc" / "commands"
        self.boilerplate_dir = self.base_dir / "doc" / "boilerplate"
        
        # Load template
        self.template_path = self.boilerplate_dir / "template.md"
        self.template_content = self._load_template()
        
        # CLI command data
        self.cli_commands = {}
        self.csv_commands = {}
        self.client_methods = {}
        
    def _load_template(self) -> str:
        """Load the markdown template"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            return self._get_default_template()
    
    def _get_default_template(self) -> str:
        """Default template if file doesn't exist"""
        return """# pvw {{COMMAND}} {{ACTION}}
[Command Reference](../../../README.md#command-reference) > [{{COMMAND}}](./main.md) > {{ACTION}}

## Description
{{DESCRIPTION}}

## Syntax
```
{{SYNTAX}}
```

{{HTTP_METHOD}} {{ENDPOINT}}

## Parameters
{{PARAMETERS}}

## Examples
{{EXAMPLES}}

{{H1}}
{{H2}}
{{H3}}
"""
    
    def load_csv_data(self):
        """Load command data from CSV file"""
        csv_path = self.boilerplate_dir / "boilerplate.csv"
        if not csv_path.exists():
            print(f"CSV file not found: {csv_path}")
            return
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    syntax = row.get('Syntax', '').strip()
                    h1 = row.get('H1', '').strip()
                    h2 = row.get('H2', '').strip()
                    h3 = row.get('H3', '').strip()
                    description = row.get('Description', '').strip()
                    doc_link = row.get('Doc Link', '').strip()
                    http_method = row.get('HTTP Method', '').strip()
                    endpoint = row.get('Endpoint', '').strip()
                    
                    if syntax and syntax.startswith('pvw '):
                        split_syntax = syntax.split(' ')
                        if len(split_syntax) >= 3:
                            cmd = split_syntax[1]
                            action = split_syntax[2]
                            
                            if cmd not in self.csv_commands:
                                self.csv_commands[cmd] = {}
                            
                            self.csv_commands[cmd][action] = {
                                'h1': h1,
                                'h2': h2,
                                'h3': h3,
                                'syntax': syntax,
                                'description': description,
                                'doc_link': doc_link,
                                'http_method': http_method,
                                'endpoint': endpoint
                            }
        except Exception as e:
            print(f"Error loading CSV data: {e}")
    
    def analyze_cli_module(self, module_path: Path) -> Dict[str, Any]:
        """Analyze a CLI module to extract command information from docstrings"""
        if not module_path.exists():
            return {}
            
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse docopt-style commands from module docstring
            commands = self._parse_docopt_commands(content, module_path.stem)
            
            return commands
            
        except Exception as e:
            print(f"Error analyzing {module_path}: {e}")
            return {}
    
    def _parse_docopt_commands(self, content: str, module_name: str) -> Dict[str, Any]:
        """Parse docopt-style commands from module docstring"""
        commands = {}
        
        # Extract the docstring (first triple-quoted string)
        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if not docstring_match:
            return commands
        
        docstring_content = docstring_match.group(1)
        
        # Parse usage lines
        usage_section = False
        options_section = False
        current_options = {}
        
        for line in docstring_content.split('\n'):
            line = line.strip()
            
            if line.startswith('usage:'):
                usage_section = True
                options_section = False
                continue
            elif line.startswith('options:'):
                usage_section = False
                options_section = True
                continue
            elif line == '' and usage_section:
                usage_section = False
                continue
            elif line == '' and options_section:
                options_section = False
                continue
            
            # Parse usage lines
            if usage_section and line.startswith('pvw'):
                # Parse command line: pvw <command> <action> [options]
                parts = line.split()
                if len(parts) >= 3 and parts[0] == 'pvw':
                    command = parts[1]
                    action = parts[2]
                    
                    # Only include if this matches the current module
                    if command == module_name:
                        # Extract options from the rest of the line
                        options_part = ' '.join(parts[3:]) if len(parts) > 3 else ''
                        
                        commands[action] = {
                            'name': action,
                            'command': command,
                            'syntax': line,
                            'description': f"{action.title()} operation for {command}",
                            'docstring': f"Execute {action} operation on {command}",
                            'options': self._parse_command_options(options_part),
                            'module': module_name
                        }
            
            # Parse options section
            elif options_section and line.startswith('--'):
                # Parse option definition: --optionName=<val>    [type] Description
                option_match = re.match(r'--(\w+)=<val>\s+\[(\w+)\]\s+(.*)', line)
                if option_match:
                    option_name, option_type, description = option_match.groups()
                    current_options[option_name] = {
                        'name': option_name,
                        'type': option_type,
                        'description': description.strip(),
                        'required': False  # Default to optional
                    }
        
        # Add parsed options to all commands in this module
        for cmd_name in commands:
            commands[cmd_name]['available_options'] = current_options
        
        return commands
    
    def _parse_command_options(self, options_part: str) -> List[Dict[str, Any]]:
        """Parse options from a command usage line"""
        options = []
        
        # Find all --option=<val> patterns
        option_matches = re.findall(r'--(\w+)=<val>', options_part)
        for option_name in option_matches:
            options.append({
                'name': option_name,
                'required': True,  # If it's in the usage line, it's typically required
                'type': 'string',
                'description': f'{option_name} parameter'
            })
        
        # Find optional parameters in brackets
        optional_matches = re.findall(r'\[--(\w+)=<val>\]', options_part)
        for option_name in optional_matches:
            options.append({
                'name': option_name,
                'required': False,
                'type': 'string',
                'description': f'{option_name} parameter (optional)'
            })
        
        return options
    
    def analyze_client_module(self, module_path: Path) -> Dict[str, Any]:
        """Analyze a client module to extract method information"""
        if not module_path.exists():
            return {}
            
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            methods = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    method_name = node.name
                    
                    # Skip private methods
                    if method_name.startswith('_'):
                        continue
                    
                    # Extract docstring
                    docstring = ast.get_docstring(node) or ""
                    
                    # Extract arguments
                    args = []
                    for arg in node.args.args:
                        if arg.arg != 'self':
                            args.append(arg.arg)
                    
                    methods[method_name] = {
                        'name': method_name,
                        'docstring': docstring,
                        'arguments': args,
                        'module': module_path.stem
                    }
            
            return methods
            
        except Exception as e:
            print(f"Error analyzing client module {module_path}: {e}")
            return {}
    
    def scan_all_modules(self):
        """Scan all CLI and client modules"""
        print("Scanning CLI modules...")
        
        # Scan CLI modules
        for cli_file in self.cli_dir.glob("*.py"):
            if cli_file.name == "__init__.py":
                continue
                
            module_commands = self.analyze_cli_module(cli_file)
            if module_commands:
                command_group = cli_file.stem
                self.cli_commands[command_group] = module_commands
                print(f"Found {len(module_commands)} commands in {command_group}")
        
        # Scan client modules
        print("Scanning client modules...")
        for client_file in self.client_dir.glob("*.py"):
            if client_file.name == "__init__.py":
                continue
                
            module_methods = self.analyze_client_module(client_file)
            if module_methods:
                self.client_methods[client_file.stem] = module_methods
                print(f"Found {len(module_methods)} methods in {client_file.stem}")
    
    def generate_documentation(self):
        """Generate markdown documentation for all commands"""
        print("Generating documentation...")
        
        total_generated = 0
        
        for command_group, commands in self.cli_commands.items():
            group_dir = self.output_dir / command_group
            group_dir.mkdir(parents=True, exist_ok=True)
            
            for action_name, command_info in commands.items():
                # Generate individual command documentation
                doc_content = self._generate_command_doc(command_group, action_name, command_info)
                
                # Write to file
                doc_file = group_dir / f"{action_name}.md"
                with open(doc_file, 'w', encoding='utf-8') as f:
                    f.write(doc_content)
                
                total_generated += 1
                print(f"Generated: {command_group}/{action_name}.md")
        
        print(f"Total documentation files generated: {total_generated}")
    def _generate_command_doc(self, command: str, action: str, command_info: Dict[str, Any]) -> str:
        """Generate documentation for a single command"""
        # Start with template
        content = self.template_content
        
        # Get CSV data if available
        csv_data = {}
        if command in self.csv_commands and action in self.csv_commands[command]:
            csv_data = self.csv_commands[command][action]
        
        # Basic replacements
        content = content.replace('{{COMMAND}}', command)
        content = content.replace('{{ACTION}}', action)
        
        # Description - prefer CSV, fall back to generated
        description = csv_data.get('description', command_info.get('description', f'{action.title()} operation for {command}'))
        content = content.replace('{{DESCRIPTION}}', description)
        
        # Syntax
        syntax = command_info.get('syntax', f'pvw {command} {action}')
        content = content.replace('{{SYNTAX}}', syntax)
        
        # HTTP method and endpoint
        http_method = csv_data.get('http_method', 'GET')
        endpoint = csv_data.get('endpoint', f'/api/{command}/{action}')
        content = content.replace('{{METHOD}}', http_method)
        content = content.replace('{{ENDPOINT}}', endpoint)
        
        # Parameters
        required_args, optional_args = self._generate_args_sections(command_info)
        content = content.replace('{{REQUIRED_ARGS}}', required_args)
        content = content.replace('{{OPTIONAL_ARGS}}', optional_args)
        
        # Additional sections from CSV
        content = content.replace('{{H1}}', csv_data.get('h1', ''))
        content = content.replace('{{H2}}', csv_data.get('h2', ''))
        content = content.replace('{{H3}}', csv_data.get('h3', ''))
        content = content.replace('{{DOC_LINK}}', csv_data.get('doc_link', ''))
        
        return content
    
    def _generate_args_sections(self, command_info: Dict[str, Any]) -> Tuple[str, str]:
        """Generate the required and optional arguments sections"""
        required_args = []
        optional_args = []
        
        # Add command-specific options
        for option in command_info.get('options', []):
            arg_text = f"- `--{option['name']}`: {option.get('description', 'Parameter')}"
            if option.get('required', False):
                required_args.append(arg_text)
            else:
                optional_args.append(arg_text)
        
        # Add available options from docstring
        available_options = command_info.get('available_options', {})
        for option_name, option_info in available_options.items():
            if not any(opt['name'] == option_name for opt in command_info.get('options', [])):
                arg_text = f"- `--{option_name}`: {option_info.get('description', 'Parameter')} ({option_info.get('type', 'string')})"
                optional_args.append(arg_text)
        
        required_text = '\n'.join(required_args) if required_args else "No required arguments."
        optional_text = '\n'.join(optional_args) if optional_args else "No optional arguments."
        
        return required_text, optional_text
    
    def _generate_parameters_section(self, command_info: Dict[str, Any]) -> str:
        """Generate the parameters section"""
        parameters = []
        
        # Add command-specific options
        for option in command_info.get('options', []):
            required_text = " (required)" if option.get('required', False) else " (optional)"
            parameters.append(f"- `--{option['name']}`: {option.get('description', 'Parameter')}{required_text}")
        
        # Add available options from docstring
        available_options = command_info.get('available_options', {})
        for option_name, option_info in available_options.items():
            if not any(opt['name'] == option_name for opt in command_info.get('options', [])):
                parameters.append(f"- `--{option_name}`: {option_info.get('description', 'Parameter')} ({option_info.get('type', 'string')})")
        
        return '\n'.join(parameters) if parameters else "No additional parameters."
    
    def _generate_examples_section(self, command: str, action: str, command_info: Dict[str, Any]) -> str:
        """Generate the examples section"""
        examples = []
        syntax = command_info.get('syntax', f'pvw {command} {action}')
        
        # Basic example
        examples.append(f"```bash\n{syntax}\n```")
        
        # Add example with common parameters if available
        options = command_info.get('options', [])
        if options:
            example_with_params = syntax
            for option in options[:2]:  # Show first 2 options as example
                if option.get('required', False):
                    example_with_params += f" --{option['name']}=<value>"
            
            if example_with_params != syntax:
                examples.append(f"```bash\n{example_with_params}\n```")
        
        return '\n\n'.join(examples)
    
    def run(self):
        """Run the complete documentation generation process"""
        print("Starting consolidated documentation generation...")
        print(f"Base directory: {self.base_dir}")
        print(f"CLI directory: {self.cli_dir}")
        print(f"Output directory: {self.output_dir}")
        
        # Load CSV data
        self.load_csv_data()
        print(f"Loaded CSV data for {len(self.csv_commands)} command groups")
        
        # Scan all modules
        self.scan_all_modules()
        print(f"Found {len(self.cli_commands)} CLI command groups")
        print(f"Found {len(self.client_methods)} client modules")
        
        # Generate documentation
        self.generate_documentation()
        
        print("Documentation generation completed!")
        
        # Print summary
        total_commands = sum(len(commands) for commands in self.cli_commands.values())
        print(f"\nSummary:")
        print(f"- Command groups: {len(self.cli_commands)}")
        print(f"- Total commands: {total_commands}")
        print(f"- Output directory: {self.output_dir}")

def main():
    """Main function"""
    # Allow custom base directory
    base_dir = sys.argv[1] if len(sys.argv) > 1 else None
    
    generator = ConsolidatedDocGenerator(base_dir)
    generator.run()

if __name__ == "__main__":
    main()
