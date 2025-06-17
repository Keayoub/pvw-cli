#!/usr/bin/env python3
"""
Main entry point for the purviewcli package.
Allows the CLI to be executed with: python -m purviewcli
"""

from purviewcli.cli.cli import main

if __name__ == '__main__':
    import sys
    if '--version' in sys.argv:
        from purviewcli import __version__
        print(f"Purview CLI version: {__version__}")
        sys.exit(0)
    main()
