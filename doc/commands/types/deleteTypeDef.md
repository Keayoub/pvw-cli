# pvw types deleteTypeDef
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > deleteTypeDef

## Description
Delete type definition.

## Syntax
```
pvw types deleteTypeDef --name=<val>
```

## Required Arguments
- `--name`: name parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--guid`: The globally unique identifier. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--type`: Typedef name as search filter (classification | entity | enum | relationship | struct). (string)

## API Mapping
Catalog Data Plane > Types > [Deletetypedef]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/deleteTypeDef
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