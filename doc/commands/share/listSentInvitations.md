# pvw share listSentInvitations
[Command Reference](../../../README.md#command-reference) > [share](./main.md) > listSentInvitations

## Description
List all data shares.

## Syntax
```
pvw share listSentInvitations --sentShareName=<val> [--skipToken=<val> --filter=<val> --orderBy=<val>]
```

## Required Arguments
- `--sentShareName`: sentShareName parameter
- `--skipToken`: skipToken parameter
- `--filter`: filter parameter
- `--orderBy`: orderBy parameter

## Optional Arguments
- `--purviewName`: The name of the Microsoft Purview account. (string)
- `--receivedShareName`: The name of the received share. (string)
- `--acceptedSentShareName`: The name of the accepted sent share. (string)
- `--assetMappingName`: The name of the asset mapping. (string)
- `--assetName`: The name of the asset. (string)
- `--invitationName`: The name of the invitation. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Share Data Plane > Share > [Listsentinvitations]()
```
 https://{accountName}.purview.azure.com/share/api/listSentInvitations
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