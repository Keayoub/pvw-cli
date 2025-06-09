# pvw types putTypeDefs
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > putTypeDefs

## Description
Create or update type definition.

## Syntax
```
pvw types putTypeDefs --payloadFile=<val>
```

## Required Arguments
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--guid`: The globally unique identifier. (string)
- `--name`: The name of the definition. (string)
- `--type`: Typedef name as search filter (classification | entity | enum | relationship | struct). (string)

## API Mapping
Catalog Data Plane > Types > [Puttypedefs]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/putTypeDefs
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