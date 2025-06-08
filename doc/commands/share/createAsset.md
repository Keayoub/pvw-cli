# pvw share createAsset
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > createAsset

## Description
Createasset operation for share

## Syntax
```
pvw share createAsset --sentShareName=<val> --assetName=<val> --payloadFile=<val>
```

## Required Arguments
- `--sentShareName`: sentShareName parameter
- `--assetName`: assetName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--receivedShareName`: The name of the received share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--invitationName`: The name of the invitation. (string)
- `--skipToken`: The continuation token to list the next page. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)

## API Mapping
 >  > []()
```
GET /api/share/createAsset
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