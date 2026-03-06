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
from .console_utils import get_console

# Initialize console with smart terminal detection for Windows PowerShell compatibility
console = get_console()

# Import version for the CLI
try:
    from purviewcli import __version__
except ImportError:
    __version__ = "unknown"


# ============================================================================
# LAZY CLI MODULE REGISTRATION SYSTEM
# ============================================================================
# Module descriptors for lazy loading (reduces startup time)
_MODULE_MAP = {
    "lineage": "lineage",
    "account": "account",
    "entity": "entity",
    "insight": "insight",
    "glossary": "glossary",
    "management": "management",
    "policystore": "policystore",
    "relationship": "relationship",
    "scan": "scan",
    "search": "search",
    "share": "share",
    "types": "types",
    "collections": ("collections", "collections"),  # (module_name, command_name)
    "uc": ("unified_catalog", "uc"),
    "domain": "domain",
    "workflow": "workflow",
    "diagnostics": "diagnostics",  # Performance diagnostics and cache management
}


def _lazy_load_module(module_name: str, command_name: Optional[str] = None):
    """Load a CLI module on-demand (lazy loading)"""
    try:
        module = __import__(f"purviewcli.cli.{module_name}", fromlist=[command_name or module_name])
        command = getattr(module, command_name or module_name)
        return command
    except (ImportError, AttributeError) as e:
        console.print(f"[yellow][!] Could not import {module_name} CLI module: {e}[/yellow]")
        return None


class LazyGroup(click.Group):
    """Click Group that lazily loads subcommands on first access"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lazy_modules = _MODULE_MAP.copy()
        self._loaded_modules = set()
    
    def list_commands(self, ctx):
        """List all available commands (triggers lazy loads for help)"""
        self._load_all_modules()
        return super().list_commands(ctx)
    
    def get_command(self, ctx, name):
        """Get command, lazy-loading module if needed"""
        # First check if already loaded
        cmd = super().get_command(ctx, name)
        if cmd:
            return cmd
        
        # Check if this is a lazy module
        if name in self._lazy_modules:
            module_info = self._lazy_modules[name]
            if isinstance(module_info, tuple):
                module_name, command_name = module_info
            else:
                module_name = command_name = module_info
            
            # Load module only if not already loaded
            if name not in self._loaded_modules:
                cmd = _lazy_load_module(module_name, command_name)
                if cmd:
                    self.add_command(cmd, name=name)
                    self._loaded_modules.add(name)
                return cmd
        
        return None
    
    def _load_all_modules(self):
        """Load all modules (used for help/listing)"""
        for name, module_info in self._lazy_modules.items():
            if name not in self._loaded_modules:
                if isinstance(module_info, tuple):
                    module_name, command_name = module_info
                else:
                    module_name = command_name = module_info
                cmd = _lazy_load_module(module_name, command_name)
                if cmd:
                    self.add_command(cmd, name=name)
                    self._loaded_modules.add(name)


@click.command(cls=LazyGroup)
@click.version_option(version=__version__, prog_name="pvw")
@click.option("--profile", help="Configuration profile to use")
@click.option("--account-name", help="Override Purview account name")
@click.option(
    "--endpoint", help="Purview account endpoint (e.g. https://<your-account>.purview.azure.com)"
)
@click.option("--token", help="Azure AD access token for authentication")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--mock", is_flag=True, help="Mock mode - simulate commands without real API calls")
@click.pass_context
def main(ctx, profile, account_name, endpoint, token, debug, mock):
    """
    Purview CLI with profile management and automation.
    Modules are loaded dynamically on first use (lazy loading) for fast startup.
    """
    ctx.ensure_object(dict)

    if debug:
        console.print("[cyan]Debug mode enabled[/cyan]")
    if mock:
        console.print("[yellow]Mock mode enabled - commands will be simulated[/yellow]")

    # Store basic config
    ctx.obj["account_name"] = account_name
    ctx.obj["profile"] = profile or "default"
    ctx.obj["debug"] = debug
    ctx.obj["mock"] = mock
    ctx.obj["endpoint"] = endpoint
    ctx.obj["token"] = token

if __name__ == "__main__":
    main()
