"""
QUICK FIX FOR PURVIEW CLI CONNECTION
===================================

The error "Tenant not registered" typically means you need to specify 
the correct Purview account name.

PROBLEM:
You ran: pvw glossary list
This doesn't specify which Purview account to connect to.

SOLUTION:
You need to run: pvw --account-name YOUR_PURVIEW_ACCOUNT_NAME glossary list

STEPS TO FIX:
"""

print("🔧 PURVIEW CLI QUICK FIX GUIDE")
print("=" * 40)

print("\n1️⃣ FIND YOUR PURVIEW ACCOUNT NAME")
print("   Run this command to find your Purview accounts:")
print("   az purview account list --query '[].name' --output table")
print()

print("2️⃣ TEST WITH MOCK MODE FIRST")
print("   python purviewcli\\cli\\cli.py --account-name YOUR_ACCOUNT_NAME --mock glossary list")
print()

print("3️⃣ RUN WITH REAL API CALL")
print("   python purviewcli\\cli\\cli.py --account-name YOUR_ACCOUNT_NAME glossary list")
print()

print("4️⃣ COMMON PURVIEW ACCOUNT NAME PATTERNS:")
print("   - company-purview")
print("   - yourorg-pv")
print("   - purview-prod")
print("   - pv-development")
print()

print("5️⃣ IF YOU DON'T KNOW THE ACCOUNT NAME:")
print("   Check Azure Portal:")
print("   - Go to portal.azure.com")
print("   - Search for 'Purview'")
print("   - Look at your Purview account name")
print()

print("6️⃣ EXAMPLE WORKING COMMANDS:")
print("   # If your account is named 'contoso-purview':")
print("   python purviewcli\\cli\\cli.py --account-name contoso-purview glossary list")
print("   python purviewcli\\cli\\cli.py --account-name contoso-purview entity read --guid some-guid")
print()

print("7️⃣ DEBUGGING:")
print("   Add --debug flag to see detailed information:")
print("   python purviewcli\\cli\\cli.py --account-name YOUR_ACCOUNT --debug glossary list")
print()

print("💡 The CLI is working correctly - you just need the right account name!")
