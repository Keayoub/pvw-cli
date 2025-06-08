# pvw share getAsset
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > getAsset

## Description
Getasset operation for share

## Syntax
```
pvw share getAsset --sentShareName=<val> --assetName=<val>
```

## Required Arguments
- `--sentShareName`: sentShareName parameter
- `--assetName`: assetName parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--receivedShareName`: The name of the received share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--invitationName`: The name of the invitation. (string)
- `--skipToken`: The continuation token to list the next page. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
 >  > []()
```
GET /api/share/getAsset
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