# pvw account putResourceSetRule
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > putResourceSetRule

## Description
Create or update account.

## Syntax
```
pvw account putResourceSetRule --payloadFile=<val>
```

## Required Arguments
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the collection. (string)
- `--keyType`: The access key type. (string)
- `--friendlyName`: The friendly name for the azure resource. (string)
- `--parentCollection`: Gets or sets the parent collection reference. (string)

## API Mapping
Account Management > Account > [Putresourcesetrule]()
```
 https://{accountName}.purview.azure.com/account/api/putResourceSetRule
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