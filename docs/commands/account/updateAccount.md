# pvw account updateAccount
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > updateAccount

## Description
Update an existing account.

## Syntax
```
pvw account updateAccount --friendlyName=<val>
```

## Required Arguments
- `--friendlyName`: friendlyName parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--collectionName`: The technical name of the collection. (string)
- `--keyType`: The access key type. (string)
- `--parentCollection`: Gets or sets the parent collection reference. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Account Management > Account > [Updateaccount]()
```
 https://{accountName}.purview.azure.com/account/api/updateAccount
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