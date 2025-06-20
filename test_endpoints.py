"""
Test endpoints module
"""

import os

# Simplified test
API_VERSION = {
    "datamap": {
        "stable": "2023-09-01",
        "preview": "2024-03-01-preview"
    }
}

USE_PREVIEW = os.getenv("USE_PREVIEW", "true").lower() in ("1", "true", "yes")
DATAMAP_API_VERSION = API_VERSION["datamap"]["preview"] if USE_PREVIEW else API_VERSION["datamap"]["stable"]

# Simple test endpoint
ENDPOINTS = {
    "entity": {
        "get": f"/datamap/api/atlas/v2/entity/guid/{{guid}}",
    }
}

print("Endpoints module loaded successfully")
