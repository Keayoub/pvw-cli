#!/usr/bin/env pwsh
<#
.SYNOPSIS
Collections API Permissions Diagnostic Tool

.DESCRIPTION
This script helps diagnose permission issues when running 'pvw collections create'.
It checks:
1. Azure authentication configuration
2. Azure RBAC roles on Purview account
3. Purview account-level permissions
4. Network connectivity to Purview endpoints

.EXAMPLE
./diagnose_collections_permissions.ps1
#>

param(
    [switch]$SkipNetworkCheck,
    [switch]$Verbose
)

$script:ErrorCount = 0
$script:WarningCount = 0

function Write-Check {
    param(
        [bool]$Status,
        [string]$Message,
        [string]$Details = ""
    )
    
    $icon = if ($Status) { "✓" } else { "✗" }
    $color = if ($Status) { "Green" } else { "Red" }
    
    Write-Host "$icon " -ForegroundColor $color -NoNewline
    Write-Host $Message
    
    if ($Details) {
        Write-Host "  → $Details" -ForegroundColor Yellow
    }
    
    if (-not $Status) {
        $script:ErrorCount++
    }
}

function Write-Section {
    param([string]$Title)
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue -BackgroundColor Black
    Write-Host "► $Title" -ForegroundColor Blue -BackgroundColor Black
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Blue -BackgroundColor Black
    Write-Host ""
}

function Test-AzureCLI {
    try {
        $version = az --version 2>&1 | Select-Object -First 1
        Write-Check $true "Azure CLI installed" $version
        return $true
    }
    catch {
        Write-Check $false "Azure CLI not found" "Install from https://docs.microsoft.com/cli/azure/install-azure-cli"
        return $false
    }
}

function Test-AzureLogin {
    try {
        $account = az account show -o json 2>&1 | ConvertFrom-Json -ErrorAction Stop
        $userName = $account.user.name
        Write-Check $true "Logged in as: $userName" "Subscription: $($account.name)"
        return $true
    }
    catch {
        Write-Check $false "Not logged in to Azure" "Run: az login"
        return $false
    }
}

function Test-ServicePrincipalEnv {
    $required = @("AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_CLIENT_SECRET")
    $all_set = $true
    $env_vars = @{}
    
    foreach ($var in $required) {
        if ([Environment]::GetEnvironmentVariable($var)) {
            if ($var -eq "AZURE_CLIENT_SECRET") {
                Write-Check $true "$var is set" "***HIDDEN***"
            }
            else {
                $value = [Environment]::GetEnvironmentVariable($var)
                Write-Check $true "$var is set" $value
            }
            $env_vars[$var] = $true
        }
        else {
            Write-Check $false "$var not set"
            $all_set = $false
        }
    }
    
    return $all_set, $env_vars
}

function Test-PurviewEnv {
    $account_name = [Environment]::GetEnvironmentVariable("PURVIEW_ACCOUNT_NAME")
    
    if ($account_name) {
        if ($account_name -match "\." -or $account_name -match "://") {
            Write-Check $false "PURVIEW_ACCOUNT_NAME has wrong format" "Should be account name only, not URL"
            return $false, $account_name
        }
        Write-Check $true "PURVIEW_ACCOUNT_NAME is set" $account_name
        return $true, $account_name
    }
    else {
        Write-Check $false "PURVIEW_ACCOUNT_NAME not set"
        return $false, $null
    }
}

function Get-ServicePrincipalObjectId {
    param([string]$ClientId)
    
    try {
        $sp = az ad sp show --id $ClientId --query "id" -o tsv 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $sp
        }
        return $null
    }
    catch {
        return $null
    }
}

function Test-PurviewAccountExists {
    param([string]$AccountName)
    
    try {
        $accounts = az purview account list --query "[?name=='$AccountName']" -o json 2>&1 | ConvertFrom-Json -ErrorAction Stop
        
        if ($accounts.Count -gt 0) {
            $account = $accounts[0]
            Write-Check $true "Purview account '$AccountName' found" "ID: $($account.id)"
            return $true, $account
        }
        else {
            Write-Check $false "Purview account '$AccountName' not found"
            return $false, $null
        }
    }
    catch {
        Write-Check $false "Failed to query Purview accounts" $_.Exception.Message
        return $false, $null
    }
}

function Test-AzureRBACRoles {
    param(
        [string]$SpObjectId,
        [string]$AccountResourceId
    )
    
    try {
        $assignments = az role assignment list `
            --assignee-object-id $SpObjectId `
            --scope $AccountResourceId `
            --output json 2>&1 | ConvertFrom-Json -ErrorAction Stop
        
        if ($assignments.Count -eq 0) {
            Write-Check $false "No Azure RBAC role assignments found" "Need: Contributor or Owner role"
            return $false
        }
        
        $required_roles = @("Owner", "Contributor", "Data Admin")
        $has_required = $false
        
        foreach ($assignment in $assignments) {
            $role_name = $assignment.roleDefinitionName
            $is_required = $role_name -in $required_roles
            Write-Check $is_required "Azure RBAC Role: $role_name"
            if ($is_required) { $has_required = $true }
        }
        
        return $has_required
    }
    catch {
        Write-Check $false "Failed to query role assignments" $_.Exception.Message
        return $false
    }
}

function Test-PurviewPermissions {
    param([string]$AccountName)
    
    try {
        $result = pvw collections list 2>&1
        Write-Check $true "Can list collections (Purview permissions OK)"
        return $true
    }
    catch {
        if ($_ -match "403" -or $_ -match "Forbidden") {
            Write-Check $false "Access denied listing collections" "May lack Purview Data Source Administrator role"
        }
        else {
            Write-Check $false "Failed to list collections" ($_.Exception.Message.Substring(0, 100))
        }
        return $false
    }
}

function Test-NetworkConnectivity {
    $endpoints = @(
        @{Host = "management.azure.com"; Port = 443},
        @{Host = "graph.microsoft.com"; Port = 443}
    )
    
    $all_connected = $true
    
    foreach ($endpoint in $endpoints) {
        try {
            $socket = New-Object System.Net.Sockets.TcpClient
            $socket.Connect($endpoint.Host, $endpoint.Port)
            $socket.Close()
            Write-Check $true "Can reach $($endpoint.Host):$($endpoint.Port)"
        }
        catch {
            Write-Check $false "Cannot reach $($endpoint.Host):$($endpoint.Port)" $_.Exception.Message
            $all_connected = $false
        }
    }
    
    return $all_connected
}

function Show-Recommendations {
    param([hashtable]$Checks)
    
    Write-Section "Recommendations"
    
    $issues = @()
    
    if (-not $Checks["azure_cli"]) {
        $issues += "1. Install Azure CLI: https://docs.microsoft.com/cli/azure/install-azure-cli"
    }
    
    if (-not $Checks["azure_auth"]) {
        $issues += "2. Login to Azure:"
        $issues += "   az login"
        $issues += "   OR set Service Principal environment variables:"
        $issues += "   `$env:AZURE_CLIENT_ID = '<your-client-id>'"
        $issues += "   `$env:AZURE_TENANT_ID = '<your-tenant-id>'"
        $issues += "   `$env:AZURE_CLIENT_SECRET = '<your-client-secret>'"
    }
    
    if (-not $Checks["purview_env"]) {
        $issues += "3. Set Purview account:"
        $issues += "   `$env:PURVIEW_ACCOUNT_NAME = '<your-account-name>'"
    }
    
    if (-not $Checks["azure_rbac"]) {
        $issues += "4. Assign Azure RBAC role (Contributor) to Service Principal:"
        $issues += "   `$spObjectId = '<sp-object-id>'"
        $issues += "   `$purviewResourceId = '<purview-resource-id>'"
        $issues += "   az role assignment create ``"
        $issues += "     --role 'Contributor' ``"
        $issues += "     --assignee-object-id `$spObjectId ``"
        $issues += "     --scope `$purviewResourceId"
    }
    
    if (-not $Checks["purview_perms"]) {
        $issues += "5. Assign Purview role via Azure Portal:"
        $issues += "   a. Go to Purview Account > Access Control (IAM)"
        $issues += "   b. Click '+ Add' > 'Add role assignment'"
        $issues += "   c. Select 'Purview Data Source Administrator'"
        $issues += "   d. Select your Service Principal"
        $issues += "   e. Click 'Review + Assign'"
    }
    
    if ($issues.Count -gt 0) {
        foreach ($issue in $issues) {
            Write-Host $issue
        }
        
        Write-Host ""
        Write-Host "Additional Help:" -ForegroundColor Blue
        Write-Host "  • Full guide: doc/COLLECTIONS_PERMISSIONS.md"
        Write-Host "  • Enable debug: `$env:LOGLEVEL = 'DEBUG'; pvw collections create ..."
        Write-Host "  • Wait 5-10 minutes for Azure role propagation"
        Write-Host "  • Retry after: az logout && az login"
    }
    else {
        Write-Host "✓ All checks passed! You should be able to create collections." -ForegroundColor Green
    }
}

# Main Diagnostic Run
function Main {
    Write-Host ""
    Write-Host "PVW Collections Permissions Diagnostic Tool" -ForegroundColor Blue -BackgroundColor Black
    Write-Host ""
    
    $checks = @{
        "azure_cli" = $false
        "azure_auth" = $false
        "service_principal" = $false
        "purview_env" = $false
        "purview_account_exists" = $false
        "azure_rbac" = $false
        "purview_perms" = $false
        "network" = $false
    }
    
    # Section 1: Azure CLI
    Write-Section "1. Azure CLI & Authentication"
    if (-not (Test-AzureCLI)) {
        Write-Host "Cannot proceed without Azure CLI. Please install it first." -ForegroundColor Red
        exit 1
    }
    
    # Check authentication
    $has_azure_login = Test-AzureLogin
    $sp_env_ok, $sp_env_vars = Test-ServicePrincipalEnv
    
    if (-not $has_azure_login -and -not $sp_env_ok) {
        Write-Host "No authentication method configured!" -ForegroundColor Red
        exit 1
    }
    
    $checks["azure_auth"] = $has_azure_login -or $sp_env_ok
    
    # Section 2: Purview Configuration
    Write-Section "2. Purview Configuration"
    $purview_env_ok, $account_name = Test-PurviewEnv
    $checks["purview_env"] = $purview_env_ok
    
    if (-not $purview_env_ok) {
        Show-Recommendations $checks
        exit 1
    }
    
    # Section 3: Purview Account
    Write-Section "3. Purview Account Verification"
    $account_exists, $account_info = Test-PurviewAccountExists $account_name
    $checks["purview_account_exists"] = $account_exists
    
    if (-not $account_exists) {
        Show-Recommendations $checks
        exit 1
    }
    
    # Section 4: Azure RBAC
    Write-Section "4. Azure RBAC Roles"
    $sp_object_id = $null
    if ($sp_env_ok) {
        $client_id = [Environment]::GetEnvironmentVariable("AZURE_CLIENT_ID")
        $sp_object_id = Get-ServicePrincipalObjectId $client_id
        if ($sp_object_id) {
            Write-Host "Service Principal Object ID: $sp_object_id" -ForegroundColor Gray
        }
    }
    
    if ($sp_object_id -and $account_info) {
        $rbac_ok = Test-AzureRBACRoles $sp_object_id $account_info.id
        $checks["azure_rbac"] = $rbac_ok
    }
    
    # Section 5: Purview Permissions
    Write-Section "5. Purview Account Permissions"
    $purview_perms_ok = Test-PurviewPermissions $account_name
    $checks["purview_perms"] = $purview_perms_ok
    
    # Section 6: Network
    if (-not $SkipNetworkCheck) {
        Write-Section "6. Network Connectivity"
        $network_ok = Test-NetworkConnectivity
        $checks["network"] = $network_ok
    }
    
    # Section 7: Recommendations
    Show-Recommendations $checks
    
    # Summary
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
    if ($script:ErrorCount -eq 0) {
        Write-Host "✓ All diagnostics passed!" -ForegroundColor Green
    }
    else {
        Write-Host "✗ Found $($script:ErrorCount) issue(s) to fix" -ForegroundColor Red
    }
    Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
}

# Run main function
Main
