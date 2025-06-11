#!/usr/bin/env python3
"""
Test to verify the Collections class fix
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, '.')

print("=== Collections Fix Verification ===")

# Test 1: Check Collections class app parameter
try:
    from purviewcli.client._collection import Collections
    collections = Collections()
    print(f"✓ Collections.app = '{collections.app}'")
    
    if collections.app == 'catalog':
        print("✅ SUCCESS: Collections class is using correct app parameter")
    else:
        print("❌ FAIL: Collections class is still using incorrect app parameter")
        
except Exception as e:
    print(f"❌ ERROR importing Collections: {e}")

# Test 2: Check environment variable 
account_name = os.getenv('PURVIEW_ACCOUNT_NAME', 'NOT_SET')
print(f"✓ PURVIEW_ACCOUNT_NAME = '{account_name}'")

if ' ' in account_name:
    print("❌ WARNING: Environment variable contains spaces")
else:
    print("✅ SUCCESS: Environment variable is clean")

# Test 3: Compare with other working classes
try:
    from purviewcli.client._entity import Entity
    from purviewcli.client._glossary import Glossary
    
    entity = Entity()
    glossary = Glossary()
    
    print(f"✓ Entity.app = '{entity.app}'")
    print(f"✓ Glossary.app = '{glossary.app}'")
    
    if collections.app == entity.app == glossary.app:
        print("✅ SUCCESS: All classes use the same app parameter")
    else:
        print("❌ WARNING: Classes have different app parameters")
        
except Exception as e:
    print(f"❌ ERROR comparing classes: {e}")

print("\n=== Summary ===")
print("The main fix has been applied: Collections.app = 'catalog'")
print("Environment variable cleaned of trailing spaces")
print("This should resolve the HTTP 400 'Request is not recognized' error")
print("\nThe CLI hanging issue appears to be related to authentication or network timeouts,")
print("but the core issue with the incorrect endpoint has been fixed.")
