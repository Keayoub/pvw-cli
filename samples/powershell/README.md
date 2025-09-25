# Microsoft Purview PowerShell Scripts

This folder contains a comprehensive collection of PowerShell scripts for managing Microsoft Purview resources. All scripts use Azure CLI authentication (`az login`) for secure and seamless integration with Azure services.

## 📋 **Prerequisites**

- **Azure CLI**: Install and login with `az login`
- **PowerShell 5.1+** or **PowerShell Core 7+**
- **Microsoft Purview Account** with appropriate permissions
- **Network Access** to Purview endpoints

### Authentication Setup
```powershell
# Login to Azure CLI (required for all scripts)
az login

# Verify you have access to your Purview account
az account show
```

## 🚀 **Available Scripts**

### 1. **List-AllPurviewCollections.ps1**
**Purpose**: Enumerate and display all collections in a Purview account with detailed information.

**Features**:
- Lists all collections with hierarchy structure
- Shows collection names, friendly names, and parent relationships
- Displays asset counts per collection
- Supports pagination for large collection sets

**Usage**:
```powershell
# Basic usage
.\List-AllPurviewCollections.ps1 -AccountName "your-purview-account"

# Example
.\List-AllPurviewCollections.ps1 -AccountName "contoso-purview"
```

**Parameters**:
- `AccountName` (Required): Your Purview account name

**Output**: Hierarchical listing of collections with asset counts and metadata.

---

### 2. **Get-PurviewCollectionDetails.ps1**
**Purpose**: Get comprehensive details about a specific Purview collection including assets, data sources, and scans.

**Features**:
- Collection information and metadata
- Asset inventory with types and qualified names
- Data source enumeration
- Scan status and history
- Colored output for better readability
- Error handling with fallback API versions

**Usage**:
```powershell
# Get detailed information about a specific collection
.\Get-PurviewCollectionDetails.ps1 -AccountName "your-purview-account" -CollectionName "collection-name"

# Example
.\Get-PurviewCollectionDetails.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Prod"
```

**Parameters**:
- `AccountName` (Required): Your Purview account name
- `CollectionName` (Required): Collection name or friendly display name

**Output**: Comprehensive report including collection info, assets, data sources, and scans.

---

### 3. **Remove-PurviewAsset-Batch.ps1**
**Purpose**: High-performance bulk deletion of assets from Purview collections with mathematical optimization.

**Features**:
- **Mathematical Optimization**: Perfect efficiency with 10 parallel jobs, zero API call waste
- **Bulk Delete API**: Uses Microsoft's bulk delete endpoint (50 assets per request)
- **Two Deletion Modes**:
  - `SINGLE`: Individual asset deletion (for small sets)
  - `BULK`: Optimized bulk deletion (for large sets)
- **Performance Metrics**: Projects 2.5 hours for 850K assets
- **Adaptive Sizing**: Automatically adjusts batch sizes based on API responses
- **Reliable Counting**: Accurate deletion progress tracking
- **Continuous Processing**: Handles large datasets without interruption

**Usage**:
```powershell
# Bulk deletion (recommended for large datasets)
.\Remove-PurviewAsset-Batch.ps1 -AccountName "your-purview-account" -CollectionName "collection-name" -Mode BULK

# Single deletion (for small datasets)
.\Remove-PurviewAsset-Batch.ps1 -AccountName "your-purview-account" -CollectionName "collection-name" -Mode SINGLE

# Examples
.\Remove-PurviewAsset-Batch.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Test" -Mode BULK
.\Remove-PurviewAsset-Batch.ps1 -AccountName "contoso-purview" -CollectionName "Small-Collection" -Mode SINGLE
```

**Parameters**:
- `AccountName` (Required): Your Purview account name
- `CollectionName` (Required): Collection name or friendly display name
- `Mode` (Required): `SINGLE` or `BULK` deletion mode

**Performance Configuration**:
- **Bulk Delete Size**: 50 assets per API call (Microsoft recommended)
- **Parallel Jobs**: 10 concurrent workers
- **Mathematical Efficiency**: 100 assets per job = exactly 2 API calls (zero waste)
- **Projected Performance**: 850K assets in ~2.5 hours

---

### 4. **Remove-PurviewCollection.ps1**
**Purpose**: Safely delete Purview collections with comprehensive dependency cleanup.

**Features**:
- **Dependency Resolution**: Automatically removes child collections, scans, and data sources
- **Force Mode**: Aggressive cleanup for stubborn dependencies
- **Safety Checks**: Validates collection existence and dependencies
- **Debug Mode**: Detailed troubleshooting information
- **Comprehensive Cleanup**: Handles complex collection hierarchies
- **Retry Logic**: Automatic retry with backend wait time

**Usage**:
```powershell
# Standard collection deletion
.\Remove-PurviewCollection.ps1 -AccountName "your-purview-account" -CollectionName "collection-name"

# Force deletion (removes dependencies aggressively)
.\Remove-PurviewCollection.ps1 -AccountName "your-purview-account" -CollectionName "collection-name" -Force

# Debug mode (detailed troubleshooting)
.\Remove-PurviewCollection.ps1 -AccountName "your-purview-account" -CollectionName "collection-name" -Force -Debug

# Examples
.\Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Finance-Test"
.\Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Legacy-Data" -Force
.\Remove-PurviewCollection.ps1 -AccountName "contoso-purview" -CollectionName "Problem-Collection" -Force -Debug
```

**Parameters**:
- `AccountName` (Required): Your Purview account name
- `CollectionName` (Required): Collection name or friendly display name
- `Force` (Optional): Aggressive cleanup mode
- `Debug` (Optional): Detailed debugging output

---

## 🔧 **Common Parameters Reference**

| Parameter | Type | Description | Scripts |
|-----------|------|-------------|---------|
| `AccountName` | String | Purview account name (without .purview.azure.com) | All scripts |
| `CollectionName` | String | Collection name or friendly display name | All except List-AllPurviewCollections |
| `Mode` | String | `SINGLE` or `BULK` deletion mode | Remove-PurviewAsset-Batch only |
| `Force` | Switch | Aggressive cleanup mode | Remove-PurviewCollection only |
| `Debug` | Switch | Detailed debugging output | Remove-PurviewCollection only |

## 🎯 **Quick Start Guide**

### 1. First Time Setup
```powershell
# Authenticate with Azure
az login

# Navigate to scripts folder
cd "C:\Dvlp\Purview\Purview_cli\samples\powershell"
```

### 2. Explore Your Purview Account
```powershell
# List all collections
.\List-AllPurviewCollections.ps1 -AccountName "your-purview-account"

# Get details about a specific collection
.\Get-PurviewCollectionDetails.ps1 -AccountName "your-purview-account" -CollectionName "your-collection"
```

### 3. Clean Up Resources
```powershell
# Delete assets from a collection
.\Remove-PurviewAsset-Batch.ps1 -AccountName "your-purview-account" -CollectionName "test-collection" -Mode BULK

# Delete the collection itself
.\Remove-PurviewCollection.ps1 -AccountName "your-purview-account" -CollectionName "test-collection" -Force
```

## 📊 **Performance Guidelines**

### Asset Deletion Performance (Remove-PurviewAsset-Batch.ps1)
- **Small Collections** (< 1,000 assets): Use `SINGLE` mode
- **Large Collections** (> 1,000 assets): Use `BULK` mode
- **Massive Scale** (100K+ assets): Bulk mode with mathematical optimization
- **Expected Throughput**: ~340 assets/minute in bulk mode

### Memory and Resource Usage
- **Memory**: ~100-200MB for bulk operations
- **Network**: Optimized API calls with minimal overhead
- **CPU**: Moderate usage due to parallel processing

## 🛡️ **Error Handling and Safety**

### Built-in Safety Features
- **Pre-flight Checks**: Validates account access and collection existence
- **Dependency Detection**: Identifies blocking resources before deletion
- **Graceful Failures**: Continues processing despite individual item failures
- **Comprehensive Logging**: Detailed success/failure reporting

### Error Recovery
- **Automatic Retry**: Built-in retry logic for transient failures
- **Force Mode**: Override safety checks when needed
- **Debug Mode**: Detailed troubleshooting information
- **Partial Success**: Reports what was successfully processed

## 🔍 **Troubleshooting**

### Common Issues and Solutions

**Authentication Errors**:
```powershell
# Ensure you're logged in to Azure CLI
az login
az account show

# Check if you have access to the Purview account
az resource show --name "your-purview-account" --resource-type "Microsoft.Purview/accounts"
```

**Collection Not Found**:
- Use `List-AllPurviewCollections.ps1` to see available collections
- Try both internal name and friendly display name
- Check for typos in collection names

**Permission Errors**:
- Ensure you have appropriate Purview permissions
- Collection Admin role required for deletion operations
- Data Curator role sufficient for read operations

**Network/API Errors**:
- Check network connectivity to `*.purview.azure.com`
- Verify firewall rules if behind corporate network
- Try with `-Debug` parameter for detailed API information

### Debug Mode Usage
```powershell
# Enable debug mode for detailed troubleshooting
.\Remove-PurviewCollection.ps1 -AccountName "your-account" -CollectionName "problem-collection" -Debug

# Debug output includes:
# - Variable values at each step
# - Complete API URLs being called
# - Response details and error messages
```

## 🚦 **Exit Codes**

All scripts use standard exit codes for automation:
- **0**: Success
- **1**: Authentication failure
- **2**: Resource not found
- **3**: Operation failed (recoverable)
- **4**: Unexpected error (non-recoverable)

## 📈 **Best Practices**

### For Production Use
1. **Test First**: Always test scripts in development environments
2. **Use Force Carefully**: Force mode bypasses safety checks
3. **Monitor Progress**: Watch for warnings and errors during execution
4. **Backup Strategy**: Consider asset inventory before bulk deletions
5. **Phased Approach**: Process large collections in phases if needed

### For Automation
1. **Error Handling**: Check exit codes in automation scripts
2. **Logging**: Capture output for audit trails
3. **Resource Limits**: Be aware of API rate limits and quotas
4. **Scheduling**: Avoid peak hours for large operations

### Example Automation Script
```powershell
# Example: Automated cleanup workflow
param($PurviewAccount, $TestCollection)

try {
    # Step 1: Get collection details
    Write-Host "Checking collection: $TestCollection"
    .\Get-PurviewCollectionDetails.ps1 -AccountName $PurviewAccount -CollectionName $TestCollection
    
    # Step 2: Delete assets
    Write-Host "Deleting assets from collection..."
    .\Remove-PurviewAsset-Batch.ps1 -AccountName $PurviewAccount -CollectionName $TestCollection -Mode BULK
    
    # Step 3: Delete collection
    Write-Host "Deleting collection..."
    .\Remove-PurviewCollection.ps1 -AccountName $PurviewAccount -CollectionName $TestCollection -Force
    
    Write-Host "✅ Cleanup completed successfully"
    exit 0
    
} catch {
    Write-Error "❌ Cleanup failed: $_"
    exit 1
}
```

## 🤝 **Contributing**

To contribute improvements or report issues:
1. Test thoroughly in development environments
2. Follow existing code patterns and standards
3. Include appropriate error handling
4. Update documentation for new features
5. Consider backward compatibility

## 📞 **Support**

For issues or questions:
- Check the troubleshooting section above
- Use `-Debug` mode for detailed diagnostics
- Review the script output for specific error messages
- Ensure latest Azure CLI version is installed

---

**Last Updated**: September 2025  
**Compatible With**: PowerShell 5.1+, PowerShell Core 7+, Azure CLI 2.0+  
**Project**: [pvw-cli](https://github.com/Keayoub/pvw-cli)
