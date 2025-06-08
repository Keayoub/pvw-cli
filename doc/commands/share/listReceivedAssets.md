# pvw share listReceivedAssets
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > listReceivedAssets

## Description
Listreceivedassets operation for share

## Syntax
```
pvw share listReceivedAssets --receivedShareName=<val> [--skipToken=<val>]
```

## Required Arguments
- `--receivedShareName`: receivedShareName parameter
- `--skipToken`: skipToken parameter

## Optional Arguments
- `--skipToken`: skipToken parameter (optional)
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--sentShareName`: The name of the sent share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--assetName`: The name of the asset. (string)
- `--invitationName`: The name of the invitation. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
 >  > []()
```
GET /api/share/listReceivedAssets
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