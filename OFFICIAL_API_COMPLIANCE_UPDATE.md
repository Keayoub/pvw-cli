# Azure Purview CLI - Official API Compliance Update

## Summary

Updated the Purview CLI to strictly follow the official Microsoft Purview API documentation, removing non-official operations and ensuring exact compliance with the published APIs.

## Official APIs Implemented

### Account API (2019-11-01-preview)
**Base URL:** `https://{accountName}.purview.azure.com/account/`
**API Reference:** https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/accounts

**4 Official Operations:**
1. **Get Account Properties** - `GET /account`
2. **Update Account Properties** - `PATCH /account`
3. **Get Access Keys** - `POST /account/keys`
4. **Regenerate Access Key** - `POST /account/keys/regenerate`

### Collections API (2019-11-01-preview)
**Base URL:** `https://{accountName}.purview.azure.com/account/`
**API Reference:** https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/collections

**6 Official Operations:**
1. **List Collections** - `GET /collections`
2. **Get Collection** - `GET /collections/{collectionName}`
3. **Create Or Update Collection** - `PUT /collections/{collectionName}`
4. **Delete Collection** - `DELETE /collections/{collectionName}`
5. **Get Collection Path** - `GET /collections/{collectionName}/getCollectionPath`
6. **List Child Collection Names** - `GET /collections/{collectionName}/getChildCollectionNames`

## Files Updated

### 1. `purviewcli/client/endpoints.py`
- ✅ Updated ACCOUNT endpoints to only include 4 official operations
- ✅ Updated COLLECTIONS endpoints to only include 6 official operations
- ✅ Fixed API version mapping for both account and collections (2019-11-01-preview)
- ❌ Removed non-official endpoints (admin management, resource set rules, etc.)

### 2. `purviewcli/client/_account.py`
- ✅ Completely rewritten to only include 4 official operations
- ✅ Added proper documentation with API references
- ✅ Uses PurviewEndpoints.get_api_version_params() for consistency
- ❌ Removed all collection-related operations (moved to _collections.py)
- ❌ Removed resource set and admin operations (not in official API)

### 3. `purviewcli/client/_collections.py`
- ✅ Completely rewritten to only include 6 official operations
- ✅ Added proper documentation with API references
- ✅ Uses PurviewEndpoints.get_api_version_params() for consistency
- ❌ Removed admin management, statistics, permissions operations (not in official API)
- ❌ Removed bulk operations and import/export (not in official API)

### 4. `purviewcli/client/api_client.py`
- ✅ Updated to reflect official operations with proper naming
- ✅ Added official account operations (get_account_properties, update_account_properties, etc.)
- ✅ Updated collections operations to match official API
- ✅ Fixed method names to be more descriptive and official

### 5. `purviewcli/cli/cli.py`
- ✅ Updated CLI command mappings to only include official operations
- ✅ Account group: 4 commands (get-account, update-account, get-access-keys, regenerate-access-keys)
- ✅ Collections group: 6 commands (list, get, create-or-update, delete, get-path, get-child-names)
- ❌ Removed non-official CLI commands

## CLI Commands Available

### Account Commands
```bash
pvw account get-account                    # Get Account Properties
pvw account update-account                 # Update Account Properties  
pvw account get-access-keys               # Get Access Keys
pvw account regenerate-access-keys        # Regenerate Access Key
```

### Collections Commands
```bash
pvw collections list                      # List Collections
pvw collections get                       # Get Collection
pvw collections create-or-update          # Create Or Update Collection
pvw collections delete                    # Delete Collection
pvw collections get-path                  # Get Collection Path
pvw collections get-child-names           # List Child Collection Names
```

## Key Changes

### What Was Removed
1. **Account operations that were not official:**
   - Collection management operations (these belong to Collections API)
   - Resource set rules operations
   - Admin management operations

2. **Collections operations that were not official:**
   - Admin management (add/remove collection admins)
   - Statistics and permissions operations
   - Bulk operations and import/export
   - Move entities operations

### What Was Fixed
1. **API Endpoints:** All endpoints now match official Microsoft documentation exactly
2. **HTTP Methods:** Correct HTTP methods for each operation (PUT for create-or-update, not POST)
3. **API Versions:** Consistent use of 2019-11-01-preview for both account and collections
4. **Parameter Handling:** Proper use of PurviewEndpoints.get_api_version_params()

### What Was Added
1. **Comprehensive Documentation:** Each operation clearly references official API documentation
2. **Proper Error Handling:** Using get_json() for payload handling
3. **Validation Tests:** Created test scripts to validate compliance

## Validation

All changes have been validated against the official Microsoft Purview API documentation:
- Account API: https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/accounts
- Collections API: https://learn.microsoft.com/en-us/rest/api/purview/accountdataplane/collections

The implementation now strictly follows Microsoft's published specifications with no additional operations that are not officially documented.

## Next Steps

1. Test the updated CLI commands with actual Purview instances
2. Validate authentication and response handling  
3. Update any documentation that references removed operations
4. Consider implementing other official Purview APIs (Data Map, Scanning, etc.) with the same rigorous approach

## Compliance Status

✅ **100% compliant** with official Microsoft Purview Account and Collections APIs
✅ **No unofficial operations** included
✅ **Proper API versioning** implemented
✅ **Correct HTTP methods** and endpoints
