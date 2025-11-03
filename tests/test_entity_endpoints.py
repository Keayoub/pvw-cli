"""Test entity retrieval with different endpoints"""
import os
import requests
from azure.identity import DefaultAzureCredential

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

print("Testing different entity endpoints...\n")

# Test 1: Get entity by GUID
print("1. Get entity by GUID:")
guid = "dcfc99ed-c74d-49aa-bd0b-72f6f6f60000"
try:
    response = requests.get(
        f"{uc_base_url}/datamap/api/atlas/v2/entity/guid/{guid}",
        headers=headers,
        params={"api-version": "2023-09-01"},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Entity found!")
    else:
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   ✗ Failed: {str(e)[:200]}")

# Test 2: Bulk get entities
print("\n2. Bulk get entities:")
try:
    response = requests.get(
        f"{uc_base_url}/datamap/api/atlas/v2/entity/bulk",
        headers=headers,
        params={
            "api-version": "2023-09-01",
            "guid": guid,
            "ignoreRelationships": "true"
        },
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Bulk get works!")
    else:
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   ✗ Failed: {str(e)[:200]}")

# Test 3: Search query (POST method)
print("\n3. Search query (POST):")
try:
    search_payload = {
        "keywords": "*",
        "limit": 5,
        "filter": {
            "entityType": "DataSet"
        }
    }
    response = requests.post(
        f"{uc_base_url}/datamap/api/search/query",
        headers=headers,
        json=search_payload,
        params={"api-version": "2023-09-01"},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Search works! Found {data.get('@search.count', 0)} results")
    else:
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   ✗ Failed: {str(e)[:200]}")

print("\nTest complete!")
