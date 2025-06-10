#!/usr/bin/env python3
"""
Glossary Endpoint Diagnostic Tool
================================

This tool helps diagnose issues with Purview Glossary API endpoints
and verifies the URL construction and authentication.
"""

import sys
import os
import json
from pathlib import Path

# Add the project path to sys.path so we can import the client modules
sys.path.insert(0, str(Path(__file__).parent))

def test_endpoint_construction():
    """Test how endpoints are constructed"""
    print("🔍 Testing Glossary Endpoint Construction")
    print("=" * 50)
    
    try:
        from purviewcli.client._glossary import Glossary
        from purviewcli.client.sync_client import SyncPurviewConfig, SyncPurviewClient
        
        # Create a test glossary client
        glossary_client = Glossary()
        
        print("✅ Successfully imported Glossary client")
        
        # Test different argument scenarios
        test_cases = [
            {
                "name": "List all glossaries (no GUID)",
                "args": {
                    "--glossaryGuid": None,
                    "--limit": 1000,
                    "--offset": 0,
                    "--sort": "ASC",
                    "--ignoreTermsAndCategories": False
                }
            },
            {
                "name": "Get specific glossary (with GUID)", 
                "args": {
                    "--glossaryGuid": "test-guid-123",
                    "--limit": 1000,
                    "--offset": 0,
                    "--sort": "ASC", 
                    "--ignoreTermsAndCategories": False
                }
            }
        ]
        
        for test_case in test_cases:
            print(f"\n📋 Test Case: {test_case['name']}")
            print("-" * 30)
            
            try:
                # Call the glossaryRead method
                glossary_client.glossaryRead(test_case['args'])
                
                print(f"   App: {glossary_client.app}")
                print(f"   Method: {glossary_client.method}")
                print(f"   Endpoint: {glossary_client.endpoint}")
                print(f"   Params: {glossary_client.params}")
                
                # Test URL construction
                account_name = "test-account"
                base_url = f"https://{account_name}.purview.azure.com"
                full_url = f"{base_url}{glossary_client.endpoint}"
                print(f"   Full URL: {full_url}")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
        
    return True

def test_real_url_construction():
    """Test URL construction with real account name"""
    print("\n🌐 Testing Real URL Construction")
    print("=" * 50)
    
    # Try to get account name from user input or environment
    account_name = os.getenv('PURVIEW_ACCOUNT_NAME')
    
    if not account_name:
        print("Enter your Purview account name (or press Enter to use 'test-account'):")
        user_input = input().strip()
        account_name = user_input if user_input else "test-account"
    
    print(f"Using account name: {account_name}")
    
    # Test different endpoint patterns
    endpoints = [
        "/api/atlas/v2/glossary",
        "/api/atlas/v2/glossary/specific-guid",
        "/api/atlas/v2/glossary/categories",
        "/api/atlas/v2/glossary/terms"
    ]
    
    for endpoint in endpoints:
        base_url = f"https://{account_name}.purview.azure.com"
        full_url = f"{base_url}{endpoint}"
        print(f"   {full_url}")
    
    return account_name

def verify_authentication():
    """Verify authentication works"""
    print("\n🔐 Testing Authentication")
    print("=" * 30)
    
    try:
        from azure.identity import DefaultAzureCredential
        from azure.core.exceptions import ClientAuthenticationError
        
        credential = DefaultAzureCredential()
        scope = "https://purview.azure.net/.default"
        
        print(f"Getting token for scope: {scope}")
        token = credential.get_token(scope)
        
        print("✅ Authentication successful!")
        print(f"   Token expires: {token.expires_on}")
        return True
        
    except ClientAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_glossary_command_with_debug():
    """Test the actual CLI command with debug output"""
    print("\n🧪 Testing CLI Command with Debug")
    print("=" * 40)
    
    account_name = os.getenv('PURVIEW_ACCOUNT_NAME', 'test-account')
    
    commands_to_test = [
        f'python purviewcli\\cli\\cli.py --account-name {account_name} --mock --debug glossary list',
        f'python purviewcli\\cli\\cli.py --account-name {account_name} --debug glossary list'
    ]
    
    import subprocess
    
    for cmd in commands_to_test:
        print(f"\n🔧 Running: {cmd}")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            print(f"Return code: {result.returncode}")
            if result.stdout:
                print(f"STDOUT:\n{result.stdout}")
            if result.stderr:
                print(f"STDERR:\n{result.stderr}")
        except subprocess.TimeoutExpired:
            print("⏰ Command timed out")
        except Exception as e:
            print(f"❌ Error running command: {e}")

def main():
    """Main diagnostic function"""
    print("Purview Glossary Endpoint Diagnostics")
    print("=" * 50)
    
    # Step 1: Test endpoint construction
    endpoint_ok = test_endpoint_construction()
    
    # Step 2: Test URL construction  
    account_name = test_real_url_construction()
    
    # Step 3: Test authentication
    auth_ok = verify_authentication()
    
    # Step 4: Test CLI command
    test_glossary_command_with_debug()
    
    # Summary
    print("\n" + "=" * 50)
    print("DIAGNOSTIC SUMMARY:")
    print(f"✅ Endpoint Construction: {'OK' if endpoint_ok else 'FAILED'}")
    print(f"✅ Authentication: {'OK' if auth_ok else 'FAILED'}")
    print(f"📋 Account Name: {account_name}")
    
    print("\n🔧 RECOMMENDATIONS:")
    if not auth_ok:
        print("❌ Fix authentication first:")
        print("   - Run: az login")
        print("   - Or set environment variables")
    elif endpoint_ok:
        print("✅ Try these commands:")
        print(f"   python purviewcli\\cli\\cli.py --account-name {account_name} --mock glossary list")
        print(f"   python purviewcli\\cli\\cli.py --account-name {account_name} --debug glossary list")
    else:
        print("❌ Fix endpoint construction issues first")

if __name__ == '__main__':
    main()
