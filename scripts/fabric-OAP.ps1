param(
    [Parameter(Mandatory = $true)]
    [string]$WorkspaceId
)

Write-Host ""
Write-Host "========================================="
Write-Host " Fabric OAP Readiness Check"
Write-Host "========================================="
Write-Host ""

# Current known unsupported artifacts
# Verify periodically against:
# https://learn.microsoft.com/en-us/fabric/security/security-feature-availability

$KnownBlockers = @(
    "Dashboard",
    "Scorecard",
    "Datamart",
    "StreamingDataset",
    "StreamingDataflow",
    "Ontology",
    "AnomalyDetector",
    "DigitalTwinBuilder"
)

try {
    $response = fab api "workspaces/$WorkspaceId/items" --output_format json | ConvertFrom-Json
}
catch {
    Write-Error "Failed to call Fabric API. Verify: fab auth status"
    exit 1
}

# Handle different Fabric CLI output formats
$items = @()

if ($response.result -and $response.result.data) {
    $items = $response.result.data
}
elseif ($response.value) {
    $items = $response.value
}
elseif ($response.data) {
    $items = $response.data
}

if (-not $items -or $items.Count -eq 0) {
    Write-Warning "No items returned."

    Write-Host ""
    Write-Host "Debug output:"
    $response | ConvertTo-Json -Depth 20

    exit 1
}

$blockers = $items | Where-Object {
    $_.type -in $KnownBlockers
}

Write-Host "Workspace ID : $WorkspaceId"
Write-Host "Item Count   : $($items.Count)"
Write-Host ""

if ($blockers.Count -gt 0) {
    Write-Host "❌ OAP NOT READY" -ForegroundColor Red
    Write-Host ""

    $blockers |
    Sort-Object type, displayName |
    Select-Object displayName, type, id |
    Format-Table -AutoSize
}
else {
    Write-Host "✅ No known OAP blockers found" -ForegroundColor Green
    Write-Host ""
    Write-Host "Workspace appears OAP-ready."
}

Write-Host ""
Write-Host "Item Type Summary"
Write-Host "-----------------"

$items |
Group-Object type |
Sort-Object Count -Descending |
Select-Object Count, Name |
Format-Table -AutoSize

Write-Host ""
Write-Host "Checking Network Policy API..."
Write-Host ""

try {
    $policy = fab api "workspaces/$WorkspaceId/networking/communicationPolicy" --output_format json | ConvertFrom-Json

    if ($policy.status -eq "Success") {
        Write-Host "✅ Network policy endpoint accessible" -ForegroundColor Green
    }
    else {
        Write-Host "⚠ Network policy endpoint returned an unexpected result"
    }
}
catch {
    Write-Host "⚠ Unable to read networking policy"
    Write-Host "   Possible reasons:"
    Write-Host "   - Not Workspace Admin"
    Write-Host "   - OAP never configured"
    Write-Host "   - Tenant restrictions"
}