.# Configure Service Principal for Purview CLI
# Usage: .\setup-service-principal.ps1

param(
    [string]$ClientId,
    [string]$ClientSecret,
    [string]$TenantId,
    [string]$PurviewName = "pview-prod-01",
    [string]$AccountId = "your-tenant-purview-account-id",
    [string]$ResourceGroup = "rg-purview-prod01"
)

# If parameters not provided, prompt for them
if (-not $ClientId) {
    $ClientId = Read-Host "Enter Service Principal Client ID"
}

if (-not $ClientSecret) {
    $SecureSecret = Read-Host "Enter Service Principal Client Secret" -AsSecureString
    $ClientSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToCoTaskMemUnicode($SecureSecret))
}

if (-not $TenantId) {
    $TenantId = Read-Host "Enter Tenant ID"
}

Write-Host "Configuring Service Principal credentials..." -ForegroundColor Green

# Set environment variables
$env:AZURE_CLIENT_ID = $ClientId
$env:AZURE_CLIENT_SECRET = $ClientSecret
$env:AZURE_TENANT_ID = $TenantId
$env:PURVIEW_NAME = $PurviewName
$env:PURVIEW_ACCOUNT_NAME = $PurviewName
$env:PURVIEW_ACCOUNT_ID = $AccountId
$env:PURVIEW_RESOURCE_GROUP = $ResourceGroup
$env:PURVIEW_AUTH_SCOPE = "https://purview.azure.net/.default"

Write-Host "[OK] Environment variables configured" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration Summary:" -ForegroundColor Cyan
Write-Host "  AZURE_CLIENT_ID: $($ClientId.Substring(0, [Math]::Min(8, $ClientId.Length)))..."
Write-Host "  AZURE_TENANT_ID: $TenantId"
Write-Host "  PURVIEW_NAME: $PurviewName"
Write-Host "  PURVIEW_ACCOUNT_ID: $AccountId"
Write-Host "  PURVIEW_AUTH_SCOPE: https://purview.azure.net/.default"
Write-Host ""

# Test the connection
Write-Host "Testing connection to Purview..." -ForegroundColor Yellow
$result = & pvw account get-account 2>&1

if ($result | Select-String -Pattern "status.*error" -Quiet) {
    Write-Host "[FAILED] Authentication failed" -ForegroundColor Red
    Write-Host "Error: $result" -ForegroundColor Red
    exit 1
} elseif ($result | Select-String -Pattern "friendlyName" -Quiet) {
    Write-Host "[OK] Successfully connected to Purview!" -ForegroundColor Green
    $accountName = $result | ConvertFrom-Json | Select-Object -ExpandProperty name
    Write-Host "Account Name: $accountName" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "[UNKNOWN] Could not determine connection status" -ForegroundColor Yellow
    Write-Host "Output: $result"
    exit 2
}
