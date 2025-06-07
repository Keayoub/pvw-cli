#!/usr/bin/env python3
"""
Enhanced Purview CLI v2.0 - Main Entry Point
"""

import sys
import asyncio
import argparse
from pathlib import Path
from rich.console import Console
from rich import print as rprint

# Add the parent directory to sys.path to enable imports
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Now we can import the modules
from purviewcli.cli.main_cli import pv
from purviewcli.cli import lineage
from purviewcli.client.config import config_manager

console = Console()

def main():
    """Main entry point for the Enhanced Purview CLI"""
    
    # Check if this is a lineage command that needs special handling
    if len(sys.argv) > 1 and sys.argv[1] == 'lineage':
        # Handle lineage commands directly
        if len(sys.argv) > 2 and sys.argv[2] == 'csv':
            # This is a CSV lineage command, handle with docopt
            from docopt import docopt
            arguments = docopt(lineage.__doc__)            # Initialize client from profile
            profile = config_manager.get_active_profile()
            if not profile:
                console.print("[red]No active Purview profile found. Please run 'pv config' to set up a profile.[/red]")
                return 1
            
            from purviewcli.client.api_client import EnhancedPurviewClient
            client = EnhancedPurviewClient(profile.account_name, profile.get_credential())
            
            # Handle CSV lineage commands
            if arguments.get('csv'):
                asyncio.run(lineage.handle_csv_lineage_commands(arguments, client))
                return 0
    
    # For all other commands, use the Click-based CLI
    try:
        pv()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
