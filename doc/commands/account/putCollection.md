# pvw account putCollection
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > putCollection

## Description
Create or update account.

## Syntax
```
pvw account putCollection --friendlyName=<val> --parentCollection=<val>
```

## Required Arguments
- `--friendlyName`: friendlyName parameter
- `--parentCollection`: parentCollection parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the collection. (string)
- `--keyType`: The access key type. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Account Management > Account > [Putcollection]()
```
 https://{accountName}.purview.azure.com/account/api/putCollection
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