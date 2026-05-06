# pvw share listAssetMappings
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > listAssetMappings

## Description
List all data shares.

## Syntax
```
pvw share listAssetMappings --receivedShareName=<val> [--skipToken=<val> --filter=<val> --orderBy=<val>]
```

## Required Arguments
- `--receivedShareName`: receivedShareName parameter
- `--skipToken`: skipToken parameter
- `--filter`: filter parameter
- `--orderBy`: orderBy parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--sentShareName`: The name of the sent share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--assetName`: The name of the asset. (string)
- `--invitationName`: The name of the invitation. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Share Data Plane > Share > [Listassetmappings]()
```
 https://{accountName}.purview.azure.com/share/api/listAssetMappings
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