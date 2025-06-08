# pvw account updateAccount
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > updateAccount

## Description
Updateaccount operation for account

## Syntax
```
pvw account updateAccount --friendlyName=<val>
```

## Required Arguments
- `--friendlyName`: friendlyName parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the collection. (string)
- `--keyType`: The access key type. (string)
- `--parentCollection`: Gets or sets the parent collection reference. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
 >  > []()
```
GET /api/account/updateAccount
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