# pvw share createAssetMapping
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > createAssetMapping

## Description
Create a new data share.

## Syntax
```
pvw share createAssetMapping --receivedShareName=<val> --assetMappingName=<val> --payloadFile=<val>
```

## Required Arguments
- `--receivedShareName`: receivedShareName parameter
- `--assetMappingName`: assetMappingName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--sentShareName`: The name of the sent share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetName`: The name of the asset. (string)
- `--invitationName`: The name of the invitation. (string)
- `--skipToken`: The continuation token to list the next page. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)

## API Mapping
Share Data Plane > Share > [Createassetmapping]()
```
 https://{accountName}.purview.azure.com/share/api/createAssetMapping
```

## Examples
DESCRIBE_EXAMPLE.
```powershell
EXAMPLE_COMMAND
```
<details><summary>Example payload.</summary>
<p>

```json
PASTE_JSON_HERE
```
</p>
</details>