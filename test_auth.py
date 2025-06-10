#!/usr/bin/env python
"""
Test Azure authentication for Purview CLI
"""
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ClientAuthenticationError

def test_azure_auth():
    print("Testing Azure authentication...")
    
    try:
        # Test Azure authentication
        credential = DefaultAzureCredential()
        
        # Try to get a token for Purview
        scope = "https://purview.azure.net/.default"
        print(f"Getting token for scope: {scope}")
        
        token = credential.get_token(scope)
        print(f"✅ Authentication successful!")
        print(f"Token type: {type(token.token)}")
        print(f"Token expires: {token.expires_on}")
        
        return True
        
    except ClientAuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_azure_auth()
    if success:
        print("\n🎉 Authentication is working! The CLI should be able to connect to Azure Purview.")
        print("\nTo use the CLI:")
        print("1. Make sure you have access to a Purview account")
        print("2. Use the correct account name: pvw --account-name 'your-purview-account' account list")
        print("3. Ensure your Azure account has Purview permissions")
    else:
        print("\n⚠️  Authentication failed. Please ensure you are logged into Azure:")
        print("1. Run 'az login' to authenticate with Azure CLI")
        print("2. Or set environment variables: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET")
        print("3. Or ensure you're running in an environment with Managed Identity")
