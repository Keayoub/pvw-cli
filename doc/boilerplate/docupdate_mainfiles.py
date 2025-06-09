#!/usr/bin/env python3

import csv
import os
from collections import defaultdict

def read_csv_commands():
    """Read all commands from the CSV file and organize by command group"""
    commands_by_group = defaultdict(list)
    
    csv_file = r'c:\Dvlp\Purview\Purview_cli\doc\boilerplate\boilerplate.csv'
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            h1 = row['H1']
            h2 = row['H2']
            h3 = row['H3']
            syntax = row['Syntax']
            description = row['Description']
              # Extract command group from syntax (e.g., "pvw account deleteCollection" -> "account")
            if syntax.startswith('pvw '):
                parts = syntax.split()
                if len(parts) >= 2:
                    group = parts[1]
                    
                    # For complex commands with subcommands, create a more descriptive action name
                    if len(parts) >= 4 and group == 'lineage' and parts[2] == 'csv':
                        # Handle lineage csv subcommands like "pvw lineage csv process" -> "csv-process"
                        action = f"{parts[2]}-{parts[3]}"
                    elif len(parts) >= 3:
                        # For most commands, use the third part as action
                        action = parts[2].lower()
                    else:
                        # Fallback to H3
                        action = h3.lower()
                    
                    commands_by_group[group].append({
                        'action': action,
                        'description': description,
                        'syntax': syntax
                    })
    
    return commands_by_group

def get_group_description(group):
    """Get appropriate description for each command group"""
    descriptions = {
        'account': 'Commands for managing account operations in Azure Purview.',
        'entity': 'Commands for managing entity operations in Azure Purview.',
        'glossary': 'Commands for managing glossary operations in Azure Purview.',
        'insight': 'Commands for performing analytics insights operations in Azure Purview.',
        'lineage': 'Commands for managing lineage operations in Azure Purview.',
        'management': 'Commands for managing metastore operations in Azure Purview.',
        'policystore': 'Commands for managing policy store operations in Azure Purview.',
        'relationship': 'Commands for managing relationship operations in Azure Purview.',
        'scan': 'Commands for managing scanning operations in Azure Purview.',
        'search': 'Commands for performing search operations in Azure Purview.',
        'share': 'Commands for managing share operations in Azure Purview.',
        'types': 'Commands for managing type operations in Azure Purview.'
    }
    return descriptions.get(group, f'Commands for managing {group} operations in Azure Purview.')

def generate_main_md(group, commands):
    """Generate main.md content for a command group"""
    description = get_group_description(group)
    
    content = f"""# pvw {group}
[Command Reference](../../README.md#command-reference) > {group}

## Description
{description}

## Syntax
```
pvw {group} <action> [options]
```

## Available Actions

"""
    
    # Sort commands by action name
    sorted_commands = sorted(commands, key=lambda x: x['action'])
    
    for cmd in sorted_commands:
        action = cmd['action']
        desc = cmd['description']
        content += f"### [{action}](./{action}.md)\n{desc}\n\n"
    
    content += f"""## Examples

```bash
# List available actions
pvw {group} --help

# Get help for specific action
pvw {group} <action> --help
```

## See Also

- [Command Reference](../../README.md#command-reference)
- [API Documentation](../api/index.html)
"""
    
    return content

def update_main_md_files():
    """Update all main.md files in the command folders"""
    commands_by_group = read_csv_commands()
    base_path = r'c:\Dvlp\Purview\Purview_cli\doc\commands'
    
    print("Updating main.md files for command groups...")
    
    for group, commands in commands_by_group.items():
        group_dir = os.path.join(base_path, group)
        main_md_path = os.path.join(group_dir, 'main.md')
        
        if os.path.exists(group_dir):
            print(f"Updating {group}/main.md with {len(commands)} commands...")
            
            # Generate new content
            new_content = generate_main_md(group, commands)
            
            # Write to file
            with open(main_md_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            
            print(f"  ✓ Updated {main_md_path}")
        else:
            print(f"  ⚠ Directory not found: {group_dir}")
    
    print(f"\nCompleted updating main.md files for {len(commands_by_group)} command groups.")

if __name__ == "__main__":
    update_main_md_files()
