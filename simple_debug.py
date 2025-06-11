#!/usr/bin/env python3
"""
Simple debug script to test URL construction
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

print("=== URL Debug Test ===")
account_name = os.getenv('PURVIEW_ACCOUNT_NAME', 'test-account')
print(f"Account name: '{account_name}'")
print(f"Account name repr: {repr(account_name)}")

# Test URL construction
from purviewcli.client.sync_client import SyncPurviewConfig, SyncPurviewClient

config = SyncPurviewConfig(
    account_name=account_name,
    azure_region=os.getenv('AZURE_REGION', 'public')
)

client = SyncPurviewClient(config)
print(f"Base URL: {client.base_url}")
print(f"Expected URL: https://fabricpurviewdemoaccount.purview.azure.com")

# Test if there's still a space
if ' ' in client.base_url:
    print("ERROR: Space found in base URL!")
    print(f"URL with spaces marked: {client.base_url.replace(' ', '[SPACE]')}")
else:
    print("✓ No spaces found in base URL")

# Test Collections class
from purviewcli.client._collection import Collections
collections = Collections()
print(f"Collections app: {collections.app}")
