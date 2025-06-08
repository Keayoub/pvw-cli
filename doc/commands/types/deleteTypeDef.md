# pvw types deleteTypeDef
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > deleteTypeDef

## Description
Deletetypedef operation for types

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
 >  > []()
```
GET /api/types/deleteTypeDef
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