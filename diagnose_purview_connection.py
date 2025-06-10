#!/usr/bin/env python3
"""
Purview Connection Diagnostic Tool
=================================

This script helps diagnose and fix Purview CLI connection issues.
"""

import subprocess
import json
import sys
from pathlib import Path

def run_command(command, shell=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_azure_login():
    """Check if user is logged into Azure"""
    print("🔍 Checking Azure CLI authentication...")
    
    success, stdout, stderr = run_command("az account show")
    if success:
        try:
            account_info = json.loads(stdout)
            print(f"✅ Logged into Azure as: {account_info.get('user', {}).get('name', 'Unknown')}")
            print(f"   Subscription: {account_info.get('name', 'Unknown')} ({account_info.get('id', 'Unknown')})")
            print(f"   Tenant: {account_info.get('tenantId', 'Unknown')}")
            return True, account_info
        except json.JSONDecodeError:
            print("❌ Could not parse Azure account information")
            return False, None
    else:
        print("❌ Not logged into Azure CLI")
        print("   Run: az login")
        return False, None

def list_purview_accounts():
    """List available Purview accounts in the subscription"""
    print("\n🔍 Looking for Purview accounts in your subscription...")
    
    success, stdout, stderr = run_command("az purview account list")
    if success and stdout.strip():
        try:
            accounts = json.loads(stdout)
            if accounts:
                print(f"✅ Found {len(accounts)} Purview account(s):")
                for i, account in enumerate(accounts, 1):
                    name = account.get('name', 'Unknown')
                    resource_group = account.get('resourceGroup', 'Unknown')
                    location = account.get('location', 'Unknown')
                    print(f"   {i}. Name: {name}")
                    print(f"      Resource Group: {resource_group}")
                    print(f"      Location: {location}")
                    print(f"      Endpoint: https://{name}.purview.azure.com")
                    print()
                return accounts
            else:
                print("⚠️  No Purview accounts found in this subscription")
                return []
        except json.JSONDecodeError:
            print("❌ Could not parse Purview account list")
            return []
    else:
        print("❌ Could not list Purview accounts")
        if stderr:
            print(f"   Error: {stderr}")
        return []

def test_purview_cli_with_account(account_name):
    """Test the Purview CLI with a specific account name"""
    print(f"\n🧪 Testing Purview CLI with account: {account_name}")
    
    # Test with mock mode first
    print("   Testing with mock mode...")
    success, stdout, stderr = run_command(f'python purviewcli\\cli\\cli.py --account-name {account_name} --mock glossary list')
    
    if success:
        print("   ✅ Mock mode works - CLI structure is correct")
        
        # Now test real mode
        print("   Testing with real API call...")
        success, stdout, stderr = run_command(f'python purviewcli\\cli\\cli.py --account-name {account_name} glossary list')
        
        if success:
            print("   ✅ Real API call successful!")
            return True
        else:
            print(f"   ❌ Real API call failed: {stderr}")
            return False
    else:
        print(f"   ❌ Even mock mode failed: {stderr}")
        return False

def main():
    """Main diagnostic function"""
    print("Purview CLI Connection Diagnostics")
    print("=" * 40)
    
    # Step 1: Check Azure authentication
    azure_logged_in, account_info = check_azure_login()
    if not azure_logged_in:
        print("\n❌ Please log into Azure first:")
        print("   az login")
        return
    
    # Step 2: List Purview accounts
    purview_accounts = list_purview_accounts()
    
    if not purview_accounts:
        print("\n❌ No Purview accounts found. You need:")
        print("   1. A Purview account in your subscription")
        print("   2. Proper permissions to access it")
        print("   3. The account to be in the same tenant")
        return
    
    # Step 3: Test CLI with each account
    print("\n🧪 Testing CLI with discovered accounts...")
    working_accounts = []
    
    for account in purview_accounts:
        account_name = account.get('name')
        if account_name:
            if test_purview_cli_with_account(account_name):
                working_accounts.append(account_name)
    
    # Step 4: Provide recommendations
    print("\n" + "=" * 40)
    print("RECOMMENDATIONS:")
    
    if working_accounts:
        print("✅ Working Purview accounts found!")
        for account_name in working_accounts:
            print(f"\n   Use this command format:")
            print(f"   python purviewcli\\cli\\cli.py --account-name {account_name} glossary list")
            print(f"   python purviewcli\\cli\\cli.py --account-name {account_name} entity read --guid YOUR_GUID")
    else:
        print("❌ No working accounts found. Common issues:")
        print("   1. Account name mismatch")
        print("   2. Insufficient permissions")
        print("   3. Account not properly registered")
        print("   4. Network/firewall issues")
        
        if purview_accounts:
            print(f"\n   Try manually with the first account:")
            first_account = purview_accounts[0].get('name')
            print(f"   python purviewcli\\cli\\cli.py --account-name {first_account} --debug glossary list")

if __name__ == '__main__':
    main()
