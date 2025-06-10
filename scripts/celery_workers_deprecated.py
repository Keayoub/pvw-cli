#!/usr/bin/env python3
"""
NOTE: This script is deprecated and no longer used.
Celery worker management has been moved to the separate Purview_WebUI project.
This file is kept for reference only.

Former: Celery Worker Startup Script for Purview CLI Backend
"""

import sys
import warnings

def main():
    warnings.warn(
        "celery_workers.py is deprecated. "
        "Celery worker management has been moved to the Purview_WebUI project.",
        DeprecationWarning,
        stacklevel=2
    )
    print("This script has been deprecated.")
    print("Celery worker management is now in the separate Purview_WebUI project.")
    print("Please refer to that project for backend and task management functionality.")
    sys.exit(1)

if __name__ == "__main__":
    main()
