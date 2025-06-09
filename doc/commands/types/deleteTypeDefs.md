# pvw types deleteTypeDefs
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > deleteTypeDefs

## Description
Delete type definition.

## Syntax
```
pvw types deleteTypeDefs --payloadFile=<val>
```

## Required Arguments
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--guid`: The globally unique identifier. (string)
- `--name`: The name of the definition. (string)
- `--type`: Typedef name as search filter (classification | entity | enum | relationship | struct). (string)

## API Mapping
Catalog Data Plane > Types > [Deletetypedefs]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/deleteTypeDefs
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