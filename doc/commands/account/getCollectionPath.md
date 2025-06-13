# pvw account getCollectionPath
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > getCollectionPath

## Description
Get account.

## Syntax
```
pvw account getCollectionPath --collectionName=<val>
```

## Required Arguments
- `--collectionName`: collectionName parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--keyType`: The access key type. (string)
- `--friendlyName`: The friendly name for the azure resource. (string)
- `--parentCollection`: Gets or sets the parent collection reference. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Account Management > Account > [Getcollectionpath]()
```
 https://{accountName}.purview.azure.com/account/api/getCollectionPath
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