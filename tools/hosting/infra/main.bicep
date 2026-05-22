// SPDX-License-Identifier: Apache-2.0
// Bicep infrastructure for Purview MCP Server on Azure Functions (Flex Consumption plan)
//
// Resources:
//   - User-assigned managed identity  (used by the Function App)
//   - Storage Account                  (required by Azure Functions)
//   - Log Analytics Workspace
//   - Application Insights
//   - App Service Plan  (Flex Consumption)
//   - Function App      (Python 3.11, self-hosted MCP server)
//
// The Function App is granted the managed identity so it can authenticate to
// Purview via DefaultAzureCredential → ManagedIdentityCredential at runtime.
// Grant the identity the "Purview Data Curator" role in Microsoft Purview.

targetScope = 'resourceGroup'

// ---------------------------------------------------------------------------
// Parameters
// ---------------------------------------------------------------------------
@description('Azure region for all resources. Defaults to resource group location.')
param location string = resourceGroup().location

@description('Short environment tag used to name resources (e.g. dev, prod).')
@maxLength(16)
param environmentName string = 'dev'

@description('Purview account name the MCP server will connect to.')
param purviewAccountName string

@description('Azure Tenant ID for Purview authentication. Leave empty to use the deployment tenant.')
param azureTenantId string = tenant().tenantId

@description('Azure region override for special sovereign clouds. Leave empty for public Azure.')
param azureRegion string = ''

// ---------------------------------------------------------------------------
// Variables
// ---------------------------------------------------------------------------
var prefix = 'pvw-mcp-${environmentName}'
var storageAccountName = replace('st${prefix}', '-', '')
var functionAppName = '${prefix}-func'
var hostingPlanName = '${prefix}-plan'
var appInsightsName = '${prefix}-ai'
var logAnalyticsName = '${prefix}-law'
var identityName = '${prefix}-id'

// ---------------------------------------------------------------------------
// User-Assigned Managed Identity
// ---------------------------------------------------------------------------
resource identity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
}

// ---------------------------------------------------------------------------
// Storage Account (required by Azure Functions)
// ---------------------------------------------------------------------------
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: take(storageAccountName, 24)
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    accessTier: 'Hot'
  }
}

// ---------------------------------------------------------------------------
// Log Analytics Workspace
// ---------------------------------------------------------------------------
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ---------------------------------------------------------------------------
// Application Insights
// ---------------------------------------------------------------------------
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

// ---------------------------------------------------------------------------
// App Service Plan — Flex Consumption
// ---------------------------------------------------------------------------
resource hostingPlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: hostingPlanName
  location: location
  sku: {
    name: 'FC1'
    tier: 'FlexConsumption'
  }
  kind: 'functionapp'
  properties: {
    reserved: true  // Linux
  }
}

// ---------------------------------------------------------------------------
// Function App
// ---------------------------------------------------------------------------
resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  kind: 'functionapp,linux'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${identity.id}': {}
    }
  }
  properties: {
    serverFarmId: hostingPlan.id
    httpsOnly: true
    siteConfig: {
      pythonVersion: '3.11'
      appSettings: [
        {
          name: 'AzureWebJobsStorage__accountName'
          value: storageAccount.name
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsights.connectionString
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot/.python_packages/lib/site-packages'
        }
        {
          name: 'AZURE_CLIENT_ID'
          value: identity.properties.clientId
        }
        {
          name: 'PURVIEW_ACCOUNT_NAME'
          value: purviewAccountName
        }
        {
          name: 'AZURE_TENANT_ID'
          value: azureTenantId
        }
        {
          name: 'AZURE_REGION'
          value: azureRegion
        }
        {
          name: 'PURVIEW_MAX_RETRIES'
          value: '3'
        }
        {
          name: 'PURVIEW_TIMEOUT'
          value: '30'
        }
        {
          name: 'PURVIEW_BATCH_SIZE'
          value: '100'
        }
      ]
    }
    functionAppConfig: {
      deployment: {
        storage: {
          type: 'blobContainer'
          value: '${storageAccount.primaryEndpoints.blob}deploymentpackage'
          authentication: {
            type: 'UserAssignedIdentity'
            userAssignedIdentityResourceId: identity.id
          }
        }
      }
      scaleAndConcurrency: {
        maximumInstanceCount: 10
        instanceMemoryMB: 2048
      }
      runtime: {
        name: 'python'
        version: '3.11'
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Storage role assignments for the managed identity
// ---------------------------------------------------------------------------
var storageBlobDataOwnerRoleId = 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'

resource storageBlobRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, identity.id, storageBlobDataOwnerRoleId)
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', storageBlobDataOwnerRoleId)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------
output functionAppName string = functionApp.name
output functionAppHostName string = functionApp.properties.defaultHostName
output mcpEndpoint string = 'https://${functionApp.properties.defaultHostName}/mcp'
output managedIdentityClientId string = identity.properties.clientId
output managedIdentityPrincipalId string = identity.properties.principalId
output resourceGroupName string = resourceGroup().name
