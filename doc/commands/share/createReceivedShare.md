# pvw share createReceivedShare
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > createReceivedShare

## Description
Createreceivedshare operation for share

## Syntax
```
pvw share createReceivedShare --receivedShareName=<val> --payloadFile=<val>
```

## Required Arguments
- `--receivedShareName`: receivedShareName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--sentShareName`: The name of the sent share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--assetName`: The name of the asset. (string)
- `--invitationName`: The name of the invitation. (string)
- `--skipToken`: The continuation token to list the next page. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)

## API Mapping
 >  > []()
```
GET /api/share/createReceivedShare
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