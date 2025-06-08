# pvw account regenerateAccessKeys
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > regenerateAccessKeys

## Description
Regenerateaccesskeys operation for account

## Syntax
```
pvw account regenerateAccessKeys --keyType=<val>
```

## Required Arguments
- `--keyType`: keyType parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the collection. (string)
- `--friendlyName`: The friendly name for the azure resource. (string)
- `--parentCollection`: Gets or sets the parent collection reference. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
 >  > []()
```
GET /api/account/regenerateAccessKeys
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