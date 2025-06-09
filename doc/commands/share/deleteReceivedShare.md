# pvw share deleteReceivedShare
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > deleteReceivedShare

## Description
Delete data share.

## Syntax
```
pvw share deleteReceivedShare --receivedShareName=<val>
```

## Required Arguments
- `--receivedShareName`: receivedShareName parameter

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
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Share Data Plane > Share > [Deletereceivedshare]()
```
 https://{accountName}.purview.azure.com/share/api/deleteReceivedShare
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