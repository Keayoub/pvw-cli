# pvw share createSentShare
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > createSentShare

## Description
Create a new data share.

## Syntax
```
pvw share createSentShare --sentShareName=<val> --payloadFile=<val>
```

## Required Arguments
- `--sentShareName`: sentShareName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--receivedShareName`: The name of the received share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--assetName`: The name of the asset. (string)
- `--invitationName`: The name of the invitation. (string)
- `--skipToken`: The continuation token to list the next page. (string)
- `--filter`: Filters the results using OData syntax. (string)
- `--orderBy`: Sorts the results using OData syntax. (string)

## API Mapping
Share Data Plane > Share > [Createsentshare]()
```
 https://{accountName}.purview.azure.com/share/api/createSentShare
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