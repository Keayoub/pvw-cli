"""Test script to diagnose Purview connection issues"""
import os
import requests
from azure.identity import DefaultAzureCredential

# Set environment variables
os.environ['PURVIEW_ACCOUNT_NAME'] = 'kaydemopurview'
os.environ['PURVIEW_ACCOUNT_ID'] = 'c869cf92-11d8-4fbc-a7cf-6114d160dd71'
os.environ['AZURE_TENANT_ID'] = 'c869cf92-11d8-4fbc-a7cf-6114d160dd71'

print("=== Testing Purview Connection ===\n")

# Test 1: Get authentication token
print("1. Getting authentication token...")
try:
    credential = DefaultAzureCredential()
    token = credential.get_token("https://purview.azure.net/.default")
    print(f"   ✓ Token obtained (length: {len(token.token)})\n")
except Exception as e:
    print(f"   ✗ Failed: {e}\n")
    exit(1)

# Test 2: Test regular Purview API endpoint
print("2. Testing regular Purview API endpoint...")
account_name = os.environ['PURVIEW_ACCOUNT_NAME']
base_url = f"https://{account_name}.purview.azure.com"
print(f"   URL: {base_url}")

try:
    response = requests.get(
        f"{base_url}/scan/datasources",
        headers={
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        },
        params={"api-version": "2023-09-01"},
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Regular API works!\n")
    else:
        print(f"   Response: {response.text[:200]}\n")
except Exception as e:
    print(f"   ✗ Connection failed: {e}\n")

# Test 3: Get Unified Catalog token
print("3. Getting Unified Catalog token...")
try:
    uc_token = credential.get_token("73c2949e-da2d-457a-9607-fcc665198967/.default")
    print(f"   ✓ UC Token obtained (length: {len(uc_token.token)})\n")
except Exception as e:
    print(f"   ✗ Failed: {e}\n")
    uc_token = None

# Test 4: Test Unified Catalog endpoint
if uc_token:
    print("4. Testing Unified Catalog endpoint...")
    account_id = os.environ['PURVIEW_ACCOUNT_ID']
    uc_base_url = f"https://{account_id}-api.purview-service.microsoft.com"
    print(f"   URL: {uc_base_url}")
    
    try:
        # Try a simple datamap endpoint
        response = requests.get(
            f"{uc_base_url}/datamap/api/atlas/v2/types/typedefs/headers",
            headers={
                "Authorization": f"Bearer {uc_token.token}",
                "Content-Type": "application/json"
            },
            params={"api-version": "2023-09-01"},
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Unified Catalog API works!\n")
        else:
            print(f"   Response: {response.text[:500]}\n")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}\n")

# Test 5: Test entity list endpoint
print("5. Testing entity list endpoint...")
try:
    response = requests.get(
        f"{uc_base_url}/datamap/api/atlas/v2/search/basic",
        headers={
            "Authorization": f"Bearer {uc_token.token}",
            "Content-Type": "application/json"
        },
        params={
            "api-version": "2023-09-01",
            "typeName": "DataSet",
            "limit": 5
        },
        timeout=30
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Search works! Found {len(data.get('value', []))} entities\n")
    else:
        print(f"   Response: {response.text[:500]}\n")
except Exception as e:
    print(f"   ✗ Failed: {e}\n")

print("=== Test Complete ===")
