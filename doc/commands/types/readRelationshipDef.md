# pvw types readRelationshipDef
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > readRelationshipDef

## Description
Readrelationshipdef operation for types

## Syntax
```
pvw types readRelationshipDef (--guid=<val> | --name=<val>)
```

## Required Arguments
- `--guid`: guid parameter
- `--name`: name parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--type`: Typedef name as search filter (classification | entity | enum | relationship | struct). (string)

## API Mapping
 >  > []()
```
GET /api/types/readRelationshipDef
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