# pvw share revokeAcceptedShare
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > revokeAcceptedShare

## Description
Revoke data share.

## Syntax
```
pvw share revokeAcceptedShare --sentShareName=<val> --acceptedSentShareName=<val>
```

## Required Arguments
- `--sentShareName`: sentShareName parameter
- `--acceptedSentShareName`: acceptedSentShareName parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--receivedShareName`: The name of the received share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--assetName`: The name of the asset. (string)
- `--invitationName`: The name of the invitation. (string)
- `--skipToken`: The continuation token to list the next page. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Share Data Plane > Share > [Revokeacceptedshare]()
```
 https://{accountName}.purview.azure.com/share/api/revokeAcceptedShare
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