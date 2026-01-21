"""
Console utility for consistent Rich Console initialization across all CLI modules.

Provides smart terminal detection for Windows PowerShell compatibility.
"""

import os
import sys
from rich.console import Console


def get_console() -> Console:
    """
    Create a Rich Console with smart terminal detection.
    
    Features:
    - Respects NO_COLOR environment variable (industry standard)
    - Respects FORCE_COLOR environment variable
    - Auto-detects terminal capabilities
    - Disables colors when output is piped/redirected
    - Windows PowerShell compatible (no raw ANSI escape codes)
    
    Returns:
        Console: Configured Rich Console instance
    """
    force_terminal = os.getenv("FORCE_COLOR") == "1"
    no_color = os.getenv("NO_COLOR") == "1" or not sys.stdout.isatty()
    return Console(force_terminal=force_terminal, no_color=no_color, legacy_windows=False)
