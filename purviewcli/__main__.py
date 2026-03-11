#!/usr/bin/env python3
"""
Main entry point for the purviewcli package.
Legacy module entry point.
Preferred user command: pvw
"""

from purviewcli.cli.cli import main

if __name__ == '__main__':
    import sys
    if '--version' in sys.argv:
        from purviewcli import __version__
        print(f"Purview CLI version: {__version__}")
        sys.exit(0)
    main()
