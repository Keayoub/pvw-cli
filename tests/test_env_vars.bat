@echo off
echo ========================================
echo Testing Environment Variable Updates
echo ========================================
echo.

echo Setting test environment variables...
set PURVIEW_ACCOUNT_NAME=test-purview-account
set AZURE_TENANT_ID=test-tenant-id
set AZURE_SUBSCRIPTION_ID=test-subscription-id

echo.
echo Environment variables set:
echo PURVIEW_ACCOUNT_NAME=%PURVIEW_ACCOUNT_NAME%
echo AZURE_TENANT_ID=%AZURE_TENANT_ID%
echo AZURE_SUBSCRIPTION_ID=%AZURE_SUBSCRIPTION_ID%

echo.
echo Testing Python import and endpoint configuration...
python -c "import sys; sys.path.insert(0, '.'); from purviewcli.client.endpoints import PurviewEndpoints; print('✓ Endpoints imported successfully'); print('Glossary base:', PurviewEndpoints.GLOSSARY['base']); print('Entity base:', PurviewEndpoints.ENTITY['base'])"

echo.
echo Testing environment variable access...
python -c "import os; print('PURVIEW_ACCOUNT_NAME from env:', os.getenv('PURVIEW_ACCOUNT_NAME', 'NOT SET')); print('Test completed successfully!')"

echo.
echo ========================================
echo Environment Variable Test Complete
echo ========================================
pause
