# pvw account getCollections
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > getCollections

## Description
Get account.

## Syntax
```
pvw account getCollections
```

## Required Arguments
No required arguments.

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--collectionName`: The technical name of the collection. (string)
- `--keyType`: The access key type. (string)
- `--friendlyName`: The friendly name for the azure resource. (string)
- `--parentCollection`: Gets or sets the parent collection reference. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Account Management > Account > [Getcollections]()
```
 https://{accountName}.purview.azure.com/account/api/getCollections
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