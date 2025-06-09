# pvw share getReceivedInvitation
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > getReceivedInvitation

## Description
Get data share.

## Syntax
```
pvw share getReceivedInvitation --invitationName=<val>
```

## Required Arguments
- `--invitationName`: invitationName parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--receivedShareName`: The name of the received share. (string)
- `--sentShareName`: The name of the sent share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--assetName`: The name of the asset. (string)
- `--skipToken`: The continuation token to list the next page. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Share Data Plane > Share > [Getreceivedinvitation]()
```
 https://{accountName}.purview.azure.com/share/api/getReceivedInvitation
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