# pvw types readTypeDef
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > readTypeDef

## Description
Retrieve type definition.

## Syntax
```
pvw types readTypeDef (--guid=<val> | --name=<val>)
```

## Required Arguments
- `--guid`: guid parameter
- `--name`: name parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--type`: Typedef name as search filter (classification | entity | enum | relationship | struct). (string)

## API Mapping
Catalog Data Plane > Types > [Readtypedef]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/readTypeDef
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