"""
Purview CLI (pvw) - Production Version
======================================

A comprehensive, automation-friendly command-line interface for Microsoft Purview.
"""

import json
import sys
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich.console import Console

console = Console()

# ============================================================================
# INDIVIDUAL CLI MODULE REGISTRATION SYSTEM
# ============================================================================

def register_individual_cli_modules(main_group):
    """
    Register all CLI command groups as modular Click-based modules for full visibility and maintainability.
    Each group is implemented in its own file in purviewcli/cli/ and exposes all real subcommands.
    """
    try:
        from purviewcli.cli.lineage import lineage
        main_group.add_command(lineage)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import lineage CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.account import account
        main_group.add_command(account)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import account CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.entity import entity
        main_group.add_command(entity)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import entity CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.insight import insight
        main_group.add_command(insight)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import insight CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.glossary import glossary
        main_group.add_command(glossary)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import glossary CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.management import management
        main_group.add_command(management)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import management CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.policystore import policystore
        main_group.add_command(policystore)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import policystore CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.relationship import relationship
        main_group.add_command(relationship)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import relationship CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.scan import scan
        main_group.add_command(scan)
        
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import scan CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.search import search
        main_group.add_command(search)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import search CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.share import share
        main_group.add_command(share)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import share CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.types import types
        main_group.add_command(types)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import types CLI module: {e}[/yellow]")    
    try:
        from purviewcli.cli.collections import collections
        main_group.add_command(collections, name="collections")
        # Removed domain alias to avoid conflicts with dedicated domain module
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import collections CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.data_product import data_product
        main_group.add_command(data_product)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import data_product CLI module: {e}[/yellow]")
    try:
        from purviewcli.cli.domain import domain
        main_group.add_command(domain)
    except ImportError as e:
        console.print(f"[yellow]⚠ Could not import domain CLI module: {e}[/yellow]")


@click.group()
@click.option("--version", is_flag=True, help="Show the current version and exit.")
@click.option("--profile", help="Configuration profile to use")
@click.option("--account-name", help="Override Purview account name")
@click.option("--endpoint", help="Purview account endpoint (e.g. https://<your-account>.purview.azure.com)")
@click.option("--token", help="Azure AD access token for authentication")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--mock", is_flag=True, help="Mock mode - simulate commands without real API calls")
@click.pass_context
def main(ctx, version, profile, account_name, endpoint, token, debug, mock):
    """
    Purview CLI with profile management and automation.
    All command groups are registered as modular Click-based modules for full CLI visibility.
    """
    if version:
        try:
            from purviewcli import __version__
            click.echo(f"Purview CLI version: {__version__}")
        except ImportError:
            click.echo("Purview CLI version: unknown")
        ctx.exit()
    ctx.ensure_object(dict)

    if debug:
        console.print("[cyan]Debug mode enabled[/cyan]")
    if mock:
        console.print("[yellow]Mock mode enabled - commands will be simulated[/yellow]")

    # Store basic config
    ctx.obj["account_name"] = account_name
    ctx.obj["profile"] = profile
    ctx.obj["debug"] = debug
    ctx.obj["mock"] = mock
    ctx.obj["endpoint"] = endpoint
    ctx.obj["token"] = token

# Register all Click-based CLI modules after main is defined
register_individual_cli_modules(main)

if __name__ == "__main__":
    main()
