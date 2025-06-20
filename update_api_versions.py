import re
import os

# List of files to update
files_to_update = [
    'purviewcli/client/_management.py',
    'purviewcli/client/_search.py', 
    'purviewcli/client/_share.py'
]

def update_file(filepath):
    """Update a file to use get_api_version_params instead of hardcoded API version"""
    print(f"Updating {filepath}...")
    
    # Read the file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return False
    
    # Check if file already imports get_api_version_params
    if 'get_api_version_params' not in content:
        # Update import statement
        content = re.sub(
            r'from \.endpoints import ENDPOINTS, (format_endpoint, )?DATAMAP_API_VERSION',
            r'from .endpoints import ENDPOINTS, DATAMAP_API_VERSION, format_endpoint, get_api_version_params',
            content
        )
    
    # Replace hardcoded API version patterns
    content = re.sub(
        r"self\.params = \{'api-version': DATAMAP_API_VERSION\}",
        r"self.params = get_api_version_params('datamap')",
        content
    )
    
    # Write back the file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Successfully updated {filepath}")
        return True
    except Exception as e:
        print(f"Error writing {filepath}: {e}")
        return False

# Update all files
for filepath in files_to_update:
    if os.path.exists(filepath):
        update_file(filepath)
    else:
        print(f"File not found: {filepath}")

print("Update completed!")
