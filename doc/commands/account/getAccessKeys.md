# pvw account getAccessKeys
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > getAccessKeys

## Description
Get account.

## Syntax
```
pvw account getAccessKeys
```

## Required Arguments
No required arguments.

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the collection. (string)
- `--keyType`: The access key type. (string)
- `--friendlyName`: The friendly name for the azure resource. (string)
- `--parentCollection`: Gets or sets the parent collection reference. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Account Management > Account > [Getaccesskeys]()
```
 https://{accountName}.purview.azure.com/account/api/getAccessKeys
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