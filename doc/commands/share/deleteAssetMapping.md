# pvw share deleteAssetMapping

[Command Reference](../../../README.md#command-reference) > [share](./main.md) >  deleteAssetMapping

## Description

Delete AssetMapping in a receivedShare.

## Syntax

```
pvw share deleteAssetMapping --receivedShareName=<val> --assetMappingName=<val>
```

## Required Arguments

`--receivedShareName` (string)
The name of the received share.

`--assetMappingName` (string)
The name of the asset mapping.

## Optional Arguments

*None*

## API Mapping

Share Data Plane > Asset Mappings > [Delete](https://docs.microsoft.com/en-us/rest/api/purview/sharedataplane/asset-mappings/delete)
```
DELETE https://{accountName}.purview.azure.com/share/receivedShares/{receivedShareName}/assetMappings/{assetMappingName}
```

## Examples

Delete an asset mapping for a particular received share.

```powershell
pvw share deleteAssetMapping --receivedShareName "NewShare" --assetMappingName "assetName"
```
