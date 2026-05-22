using './main.bicep'

param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'dev')
param location = readEnvironmentVariable('AZURE_LOCATION', 'eastus')
param purviewAccountName = readEnvironmentVariable('PURVIEW_ACCOUNT_NAME', '')
param azureTenantId = readEnvironmentVariable('AZURE_TENANT_ID', '')
param azureRegion = readEnvironmentVariable('AZURE_REGION', '')
