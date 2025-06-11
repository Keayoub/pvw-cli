#!/usr/bin/env python3
"""
Trace the execution path to find where CLI hangs
"""
import sys
import os
import traceback

# Add the project to Python path
sys.path.insert(0, r'c:\Dvlp\Purview\Purview_cli')

print("Starting execution trace...")

try:
    print("1. Importing click...")
    import click
    print("   ✓ Click imported successfully")
    
    print("2. Importing purviewcli modules...")
    from purviewcli.cli import cli
    print("   ✓ CLI module imported successfully")
    
    print("3. Checking if collections command exists...")
    # Get the CLI group
    cli_group = cli.cli
    print(f"   CLI group: {cli_group}")
    print(f"   Available commands: {list(cli_group.commands.keys())}")
    
    if 'collections' in cli_group.commands:
        collections_cmd = cli_group.commands['collections']
        print(f"   ✓ Collections command found: {collections_cmd}")
        print(f"   Collections subcommands: {list(collections_cmd.commands.keys()) if hasattr(collections_cmd, 'commands') else 'No subcommands'}")
    else:
        print("   ✗ Collections command not found")
    
    print("4. Testing collections import directly...")
    from purviewcli.client._collection import Collections
    print("   ✓ Collections class imported successfully")
    
    print("5. Creating Collections instance...")
    collections = Collections()
    print(f"   ✓ Collections instance created")
    print(f"   App parameter: {collections.app}")
    print(f"   Endpoint: {collections.endpoint}")
    
    print("6. Testing environment variables...")
    purview_name = os.getenv('PURVIEW_ACCOUNT_NAME')
    print(f"   PURVIEW_ACCOUNT_NAME: '{purview_name}' (length: {len(purview_name) if purview_name else 0})")
    
    print("7. Testing URL construction...")
    if hasattr(collections, 'get_endpoint'):
        try:
            endpoint_url = collections.get_endpoint()
            print(f"   Endpoint URL: {endpoint_url}")
        except Exception as e:
            print(f"   Error getting endpoint: {e}")
    
    print("8. All basic imports and setup completed successfully!")
    
except Exception as e:
    print(f"Error during execution: {e}")
    print("Full traceback:")
    traceback.print_exc()
