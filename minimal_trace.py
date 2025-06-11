#!/usr/bin/env python3
"""
Very granular trace to find import issue
"""
import sys
import os

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:", sys.path[:3])  # Show first 3 entries

# Add the project to Python path
project_path = r'c:\Dvlp\Purview\Purview_cli'
if project_path not in sys.path:
    sys.path.insert(0, project_path)
    print(f"Added {project_path} to Python path")

print("\n=== Starting Import Trace ===")

try:
    print("1. Importing standard libraries...")
    import json
    import requests
    print("   ✓ Standard libraries OK")
    
    print("2. Importing click...")
    import click
    print("   ✓ Click OK")
    
    print("3. Importing purviewcli.client.endpoint...")
    from purviewcli.client.endpoint import Endpoint
    print("   ✓ Endpoint OK")
    
    print("4. Importing purviewcli.client._collections...")
    from purviewcli.client._collection import Collections
    print("   ✓ Collections OK")
    
    print("5. Testing Collections instantiation...")
    collections = Collections()
    print(f"   ✓ Collections created, app={collections.app}")
    
    print("6. All imports successful!")
    
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Other error: {e}")
    import traceback
    traceback.print_exc()
    
print("Script completed.")
