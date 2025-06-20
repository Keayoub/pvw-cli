# pvw types readClassificationDef
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > readClassificationDef

## Description
Retrieve type definition.

## Syntax
```
pvw types readClassificationDef (--guid=<val> | --name=<val>)
```

## Required Arguments
- `--guid`: guid parameter
- `--name`: name parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--type`: Typedef name as search filter (classification | entity | enum | relationship | struct). (string)

## API Mapping
Catalog Data Plane > Types > [Readclassificationdef]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/readClassificationDef
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