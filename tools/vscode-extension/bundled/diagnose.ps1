Write-Host "=== Purview MCP Server Diagnostics ===" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()
$passed = @()

# Check 1: server.py
if (Test-Path "server.py") {
    $passed += "server.py found"
} else {
    $errors += "server.py not found"
}

# Check 2: Python
try {
    $pyVersion = python --version 2>&1
    $passed += "Python available: $pyVersion"
} catch {
    $errors += "Python not found"
}

# Check 3: MCP package
try {
    python -c "import mcp" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $passed += "mcp package installed"
    } else {
        $errors += "mcp package not installed"
    }
} catch {
    $errors += "mcp package not installed"
}

# Check 4: Azure Identity
try {
    python -c "import azure.identity" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $passed += "azure-identity package installed"
    } else {
        $errors += "azure-identity package not installed"
    }
} catch {
    $errors += "azure-identity package not installed"
}

# Check 5: pvw-cli
try {
    python -c "import purviewcli" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $passed += "purviewcli package installed"
    } else {
        $warnings += "purviewcli package not installed (will install on first run)"
    }
} catch {
    $warnings += "purviewcli package not installed (will install on first run)"
}

# Check 6: Azure CLI authentication
try {
    $azAccount = az account show 2>$null | ConvertFrom-Json
    if ($azAccount) {
        $passed += "Azure CLI authenticated"
        $passed += "  Subscription: $($azAccount.name)"
    } else {
        $warnings += "Azure CLI not authenticated"
    }
} catch {
    $warnings += "Azure CLI not authenticated"
}

# Check 7: requirements.txt
if (Test-Path "requirements.txt") {
    $passed += "requirements.txt found"
} else {
    $warnings += "requirements.txt not found"
}

# Check 8: VS Code extension installed
try {
    $extensions = code --list-extensions 2>$null
    if ($extensions -match "keayoub.purview-mcp") {
        $passed += "VS Code extension installed"
    } else {
        $warnings += "VS Code extension not installed"
    }
} catch {
    $warnings += "Could not check VS Code extensions"
}

# Display results
if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "❌ Errors:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
}

if ($warnings.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️  Warnings:" -ForegroundColor Yellow
    foreach ($warn in $warnings) {
        Write-Host "  - $warn" -ForegroundColor Yellow
    }
}

if ($passed.Count -gt 0) {
    Write-Host ""
    Write-Host "✅ Checks Passed:" -ForegroundColor Green
    foreach ($p in $passed) {
        Write-Host "  - $p" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════" -ForegroundColor Cyan

if ($errors.Count -eq 0) {
    Write-Host "✅ All checks passed! Ready to start the MCP server." -ForegroundColor Green
} else {
    Write-Host "❌ Found $($errors.Count) error(s). Please fix them before starting." -ForegroundColor Red
}
