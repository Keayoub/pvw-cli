# pvw types readStatistics
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > readStatistics

## Description
Retrieve type definition.

## Syntax
```
pvw types readStatistics
```

## Required Arguments
No required arguments.

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--guid`: The globally unique identifier. (string)
- `--name`: The name of the definition. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--type`: Typedef name as search filter (classification | entity | enum | relationship | struct). (string)

## API Mapping
Catalog Data Plane > Types > [Readstatistics]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/readStatistics
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