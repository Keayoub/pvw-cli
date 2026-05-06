# pvw share updateExpirationAcceptedShare
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > updateExpirationAcceptedShare

## Description
Update an existing data share.

## Syntax
```
pvw share updateExpirationAcceptedShare --sentShareName=<val> --acceptedSentShareName=<val> --payloadFile=<val>
```

## Required Arguments
- `--sentShareName`: sentShareName parameter
- `--acceptedSentShareName`: acceptedSentShareName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--receivedShareName`: The name of the received share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--assetName`: The name of the asset. (string)
- `--invitationName`: The name of the invitation. (string)
- `--skipToken`: The continuation token to list the next page. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)

## API Mapping
Share Data Plane > Share > [Updateexpirationacceptedshare]()
```
 https://{accountName}.purview.azure.com/share/api/updateExpirationAcceptedShare
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