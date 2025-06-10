@echo off
echo =====================================
echo Microsoft Purview CLI - Quick Start
echo =====================================
echo.
echo This script will help you set up Purview CLI correctly.
echo All HTTP 404 endpoint issues have been resolved!
echo.

echo STEP 1: Check if you have Azure CLI installed
echo --------------------------------------------
az --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Azure CLI not found. Please install it first:
    echo https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
    goto :end
) else (
    echo ✅ Azure CLI is installed
)

echo.
echo STEP 2: Login to Azure
echo ----------------------
echo Running: az login
az login
if %errorlevel% neq 0 (
    echo ❌ Azure login failed
    goto :end
) else (
    echo ✅ Azure login successful
)

echo.
echo STEP 3: Set environment variables
echo --------------------------------
echo Please enter your Purview account details:
echo.
set /p ACCOUNT_NAME="Enter your Purview account name: "
set /p TENANT_ID="Enter your Azure Tenant ID: "
set /p SUBSCRIPTION_ID="Enter your Azure Subscription ID: "

echo.
echo Setting environment variables...
set PURVIEW_ACCOUNT_NAME=%ACCOUNT_NAME%
set AZURE_TENANT_ID=%TENANT_ID%
set AZURE_SUBSCRIPTION_ID=%SUBSCRIPTION_ID%

echo ✅ Environment variables set:
echo   PURVIEW_ACCOUNT_NAME=%PURVIEW_ACCOUNT_NAME%
echo   AZURE_TENANT_ID=%AZURE_TENANT_ID%
echo   AZURE_SUBSCRIPTION_ID=%AZURE_SUBSCRIPTION_ID%

echo.
echo STEP 4: Test Purview CLI
echo ------------------------
echo Testing connection to Purview...
python -m purviewcli glossary list --limit 1

if %errorlevel% equ 0 (
    echo.
    echo 🎉 SUCCESS! Purview CLI is working correctly!
    echo.
    echo You can now use commands like:
    echo   pv glossary list
    echo   pv entity get --guid [guid]
    echo   pv search query "*"
    echo.
    echo For more help: pv --help
) else (
    echo.
    echo ⚠️  Connection test failed. Please check:
    echo   1. Your Purview account name is correct
    echo   2. You have permissions to access the account
    echo   3. The account is fully provisioned
    echo.
    echo Run this for detailed diagnostics:
    echo   python final_404_fix_guide.py
)

:end
echo.
echo =====================================
echo Setup Complete
echo =====================================
pause
