"""List all entity types and find sample entities"""
import os
import requests  
from azure.identity import DefaultAzureCredential
import json

os.environ['PURVIEW_ACCOUNT_NAME'] = 'kaydemopurview'
os.environ['PURVIEW_ACCOUNT_ID'] = 'c869cf92-11d8-4fbc-a7cf-6114d160dd71'

credential = DefaultAzureCredential()
uc_token = credential.get_token("73c2949e-da2d-457a-9607-fcc665198967/.default")

account_id = os.environ['PURVIEW_ACCOUNT_ID']
uc_base_url = f"https://{account_id}-api.purview-service.microsoft.com"

headers = {
    "Authorization": f"Bearer {uc_token.token}",
    "Content-Type": "application/json"
}

print("Getting entity types from Purview...\n")

# List all type definitions
try:
    response = requests.get(
        f"{uc_base_url}/datamap/api/atlas/v2/types/typedefs/headers",
        headers=headers,
        params={"api-version": "2023-09-01"},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        entity_defs = data.get('entityDefs', [])
        
        print(f"Found {len(entity_defs)} entity types\n")
        print("Sample entity types:")
        for i, entity_def in enumerate(entity_defs[:20], 1):
            name = entity_def.get('name', 'N/A')
            category = entity_def.get('category', 'N/A')
            print(f"  {i}. {name} ({category})")
    else:
        print(f"Error: {response.status_code} - {response.text[:300]}")
        
except Exception as e:
    print(f"Failed: {e}")

# Try to browse entities instead of searching
print("\n\nTrying browse endpoint...")
try:
    response = requests.post(
        f"{uc_base_url}/datamap/api/browse",
        headers=headers,
        json={"path": "/", "limit": 10},
        params={"api-version": "2023-09-01"},
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Browse result: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"Response: {response.text[:300]}")
except Exception as e:
    print(f"Failed: {str(e)[:200]}")
