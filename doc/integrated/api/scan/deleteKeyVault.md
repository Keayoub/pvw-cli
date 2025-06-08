# pvw scan deleteKeyVault
[Command Reference](../../../README.md#command-reference) > [scan](./main.md) > deleteKeyVault

## Description
Deletes the key vault connection associated with the account

## Syntax
```
pvw scan deleteKeyVault --keyVaultName=<val>
```

## Required Arguments
`--keyVaultName` (string)  
The data source name.

## Optional Arguments
*None*

## API Mapping
Scanning Data Plane > Key Vault Connections > [Delete](https://docs.microsoft.com/en-us/rest/api/purview/scanningdataplane/key-vault-connections/delete)
```
DELETE https://{accountName}.purview.azure.com/scan/azureKeyVaults/{keyVaultName}
```

## Examples
Delete a key vault connection by name.
```powershell
pvw scan deleteKeyVault --keyVaultName "MyKeyVault"
```
