#!/usr/bin/env python3
"""
Simple Glossary Test - Find the exact 404 issue
"""

import sys
import os
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_glossary_read_method():
    """Test the glossaryRead method directly"""
    print("🔍 Testing glossaryRead method directly")
    print("=" * 40)
    
    try:
        from purviewcli.client._glossary import Glossary
        
        glossary = Glossary()
        
        # Test args that would come from CLI
        test_args = {
            "--glossaryGuid": None,  # This should trigger the list all glossaries
            "--limit": 1000,
            "--offset": 0,
            "--sort": "ASC",
            "--ignoreTermsAndCategories": False
        }
        
        print("Test args:", test_args)
        
        # Call the method
        glossary.glossaryRead(test_args)
        
        print(f"✅ Method executed successfully")
        print(f"   App: {glossary.app}")
        print(f"   Method: {glossary.method}")
        print(f"   Endpoint: {glossary.endpoint}")
        print(f"   Params: {glossary.params}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_construction():
    """Test the exact URL that would be called"""
    print("\n🌐 Testing URL Construction")
    print("=" * 40)
    
    # Sample account names to test
    test_accounts = ["test-account", "contoso-purview", "demo-purview"]
    
    for account in test_accounts:
        base_url = f"https://{account}.purview.azure.com"
        endpoint = "/api/atlas/v2/glossary"
        full_url = f"{base_url}{endpoint}"
        
        print(f"Account: {account}")
        print(f"   Full URL: {full_url}")
        print(f"   This URL should list all glossaries")

def test_cli_parameter_conversion():
    """Test how CLI parameters get converted"""
    print("\n🔧 Testing CLI Parameter Conversion")
    print("=" * 40)
    
    # Simulate what happens when user runs: pvw glossary list
    kwargs = {}  # No additional parameters provided
    
    # This is what the CLI does:
    method_args = {}
    method_args['--glossaryGuid'] = kwargs.get('glossary_guid')  # This will be None
    method_args['--limit'] = kwargs.get('limit', 1000)
    method_args['--offset'] = kwargs.get('offset', 0)
    method_args['--sort'] = kwargs.get('sort', 'ASC')
    method_args['--ignoreTermsAndCategories'] = kwargs.get('ignore_terms_and_categories', False)
    
    print("CLI kwargs:", kwargs)
    print("Converted method_args:", method_args)
    print(f"--glossaryGuid is None: {method_args['--glossaryGuid'] is None}")

def main():
    """Main test function"""
    print("Glossary 404 Issue Diagnosis")
    print("=" * 50)
    
    # Test 1: Direct method call
    method_ok = test_glossary_read_method()
    
    # Test 2: URL construction
    test_url_construction()
    
    # Test 3: Parameter conversion
    test_cli_parameter_conversion()
    
    print("\n" + "=" * 50)
    print("DIAGNOSIS RESULTS:")
    
    if method_ok:
        print("✅ The glossaryRead method works correctly")
        print("✅ The endpoint '/api/atlas/v2/glossary' should list all glossaries")
        print("\n🔧 The 404 issue is likely caused by:")
        print("   1. Incorrect account name")
        print("   2. Account doesn't exist or no access")
        print("   3. Authentication issues")
        print("   4. Network/firewall blocking the request")
        
        print("\n💡 SOLUTIONS TO TRY:")
        print("   1. Verify your account name with: az purview account list")
        print("   2. Test with: python purviewcli\\cli\\cli.py --account-name YOUR_ACCOUNT --debug glossary list")
        print("   3. Try mock mode first: python purviewcli\\cli\\cli.py --account-name YOUR_ACCOUNT --mock glossary list")
    else:
        print("❌ There's an issue with the glossaryRead method itself")

if __name__ == '__main__':
    main()
