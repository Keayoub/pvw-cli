# List-PurviewDataSourcesAndScans.ps1
# This script lists data sources and scans associated with a specific collection in Azure Purview
# Usage: .\List-PurviewDataSourcesAndScans.ps1 -AccountName <PurviewAccountName> -CollectionName <CollectionName>

param(
    [Parameter(Mandatory=$true)]
    [string]$AccountName,
    [Parameter(Mandatory=$true)]
    [string]$CollectionName
)

# Ensure Az.Accounts module is installed and imported
Write-Host "Checking for Az.Accounts module..."
if (-not (Get-Module -ListAvailable -Name Az.Accounts)) {
    Write-Host "Az.Accounts module not found. Installing..."
    Install-Module -Name Az.Accounts -Force -AllowClobber -Scope CurrentUser
}
if (-not (Get-Module -Name Az.Accounts)) {
    Write-Host "Importing Az.Accounts module..."
    Import-Module Az.Accounts
} else {
    Write-Host "Az.Accounts module already imported."
}

# Login to Azure if not already logged in
Write-Host "Checking Azure login context..."
try {
    $context = Get-AzContext
} catch {
    $context = $null
}
if (-not $context) {
    Write-Host "Logging in to Azure..."
    Connect-AzAccount -UseDeviceAuthentication -Force
} else {
    Write-Host "Already logged in to Azure."
}

# Get an access token for Purview using Azure CLI
Write-Host "Acquiring Azure access token for Purview using Azure CLI..."
try {
    $tokenJson = az account get-access-token --resource "https://purview.azure.net" --output json
    if ($LASTEXITCODE -eq 0) {
        $tokenData = $tokenJson | ConvertFrom-Json
        $accessToken = $tokenData.accessToken
        Write-Host "Successfully acquired token using Azure CLI."
    } else {
        throw "Azure CLI failed to get token"
    }
} catch {
    Write-Error "Failed to acquire token using Azure CLI: $_"
    exit 1
}

# Set up headers for API calls
$headers = @{
    'Authorization' = "Bearer $accessToken"
    'Content-Type' = 'application/json'
}

Write-Host "Searching for data sources and scans in collection '$CollectionName'..."

# List all data sources and filter by collection
$dsApiVersions = @("2023-09-01", "2022-07-01-preview")
$collectionDataSources = @()

foreach ($dsApiVersion in $dsApiVersions) {
    Write-Host "Trying API version $dsApiVersion for data sources..."
    $dsUri = "https://$AccountName.purview.azure.com/datasources?api-version=$dsApiVersion"
    
    try {
        $dsResponse = Invoke-RestMethod -Method GET -Uri $dsUri -Headers $headers
        $allDataSources = $dsResponse.value
        
        if ($allDataSources) {
            Write-Host "Found $($allDataSources.Count) total data sources. Filtering by collection..."
            
            # Filter data sources that belong to this collection
            foreach ($ds in $allDataSources) {
                # Check multiple possible collection reference formats
                $dsCollection = $null
                if ($ds.properties -and $ds.properties.collection) {
                    $dsCollection = $ds.properties.collection.referenceName
                } elseif ($ds.collection) {
                    $dsCollection = $ds.collection.referenceName
                }
                
                if ($dsCollection -eq $CollectionName -or $dsCollection -eq $AccountName) {
                    $collectionDataSources += $ds
                }
            }
            
            # Show results
            if ($collectionDataSources.Count -gt 0) {
                Write-Host "`nData sources found in collection '$CollectionName':"
                Write-Host "=" * 60
                $collectionDataSources | Format-Table -AutoSize name, kind, @{
                    Name="Collection"
                    Expression={
                        if ($_.properties.collection.referenceName) { 
                            $_.properties.collection.referenceName 
                        } else { 
                            "N/A" 
                        }
                    }
                }, @{
                    Name="ResourceGroup"
                    Expression={
                        if ($_.properties.resourceGroup) { 
                            $_.properties.resourceGroup 
                        } else { 
                            "N/A" 
                        }
                    }
                }
                break
            } else {
                Write-Host "`nNo data sources found in collection '$CollectionName'."
                Write-Host "`nDebugging: All data sources and their collections:"
                Write-Host "-" * 50
                $allDataSources | ForEach-Object { 
                    $collectionRef = "None"
                    if ($_.properties.collection.referenceName) { 
                        $collectionRef = $_.properties.collection.referenceName 
                    } elseif ($_.collection.referenceName) { 
                        $collectionRef = $_.collection.referenceName 
                    }
                    Write-Host "  - $($_.name) (Kind: $($_.kind)) -> Collection: $collectionRef"
                }
            }
        } else {
            Write-Host "No data sources found (API version $dsApiVersion)."
        }
    } catch {
        if ($_.Exception.Response.StatusCode.value__ -eq 404) {
            Write-Host "API version $dsApiVersion not available for data sources, trying next version..."
        } else {
            Write-Host "Failed to retrieve data sources (API version $dsApiVersion): $($_.Exception.Message)"
        }
    }
}

# List scans for collection-specific data sources
if ($collectionDataSources.Count -gt 0) {
    Write-Host "`nListing scans for data sources in collection '$CollectionName'..."
    Write-Host "=" * 60
    
    foreach ($ds in $collectionDataSources) {
        Write-Host "`nChecking scans for data source: $($ds.name)"
        Write-Host "-" * 40
        
        $scanApiVersions = @("2023-09-01", "2022-07-01-preview")
        $foundScans = $false
        
        foreach ($scanApiVersion in $scanApiVersions) {
            $scansUri = "https://$AccountName.purview.azure.com/datasources/$($ds.name)/scans?api-version=$scanApiVersion"
            try {
                $scansResponse = Invoke-RestMethod -Method GET -Uri $scansUri -Headers $headers
                $scans = $scansResponse.value
                
                if ($scans -and $scans.Count -gt 0) {
                    Write-Host "Found $($scans.Count) scan(s) for data source '$($ds.name)':"
                    $scans | Format-Table -AutoSize name, @{
                        Name="DataSource"
                        Expression={$ds.name}
                    }, @{
                        Name="Kind"
                        Expression={
                            if ($_.kind) { $_.kind } else { "N/A" }
                        }
                    }, @{
                        Name="Status"
                        Expression={
                            if ($_.properties.lastRun.result) { 
                                $_.properties.lastRun.result 
                            } else { 
                                "Never run" 
                            }
                        }
                    }, @{
                        Name="LastModified"
                        Expression={
                            if ($_.properties.lastModifiedAt) { 
                                $_.properties.lastModifiedAt 
                            } else { 
                                "N/A" 
                            }
                        }
                    }
                    $foundScans = $true
                    break
                } else {
                    Write-Host "No scans found for data source '$($ds.name)' (API version $scanApiVersion)."
                }
            } catch {
                if ($_.Exception.Response.StatusCode.value__ -eq 404) {
                    Write-Host "API version $scanApiVersion not available for scans, trying next version..."
                } else {
                    Write-Host "Failed to retrieve scans for data source '$($ds.name)': $($_.Exception.Message)"
                    break
                }
            }
        }
        
        if (-not $foundScans) {
            Write-Host "No scans configured for data source '$($ds.name)'."
        }
    }
} else {
    Write-Host "`nNo data sources found in collection '$CollectionName'."
    Write-Host "This could mean:"
    Write-Host "  1. No data sources are assigned to this collection"
    Write-Host "  2. The scanning endpoints are not available for this Purview account"
    Write-Host "  3. The collection name doesn't match the data source collection references"
}

Write-Host "`nScript completed."
