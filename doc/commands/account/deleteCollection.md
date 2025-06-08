# pvw account deleteCollection
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > deleteCollection

## Description
Deletecollection operation for account

## Syntax
```
pvw account deleteCollection --collectionName=<val>
```

## Required Arguments
- `--collectionName`: collectionName parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--keyType`: The access key type. (string)
- `--friendlyName`: The friendly name for the azure resource. (string)
- `--parentCollection`: Gets or sets the parent collection reference. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
 >  > []()
```
GET /api/account/deleteCollection
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