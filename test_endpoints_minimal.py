"""
Minimal test of endpoints module
"""

print("Starting endpoints test...")

import os
print("os imported")

# Test individual parts
API_VERSION = {
    "datamap": {
        "stable": "2023-09-01",
        "preview": "2024-03-01-preview"
    }
}
print("API_VERSION defined")

USE_PREVIEW = os.getenv("USE_PREVIEW", "true").lower() in ("1", "true", "yes")
print("USE_PREVIEW defined:", USE_PREVIEW)

DATAMAP_API_VERSION = API_VERSION["datamap"]["preview"] if USE_PREVIEW else API_VERSION["datamap"]["stable"]
print("DATAMAP_API_VERSION defined:", DATAMAP_API_VERSION)

# Test simple endpoint
ENDPOINTS = {
    "entity": {
        "get": "/datamap/api/atlas/v2/entity/guid/{guid}",
    }
}
print("ENDPOINTS defined")

print("All imports successful!")
