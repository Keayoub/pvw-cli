# pvw types readBusinessMetadataDef
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > readBusinessMetadataDef

## Description
Get the business metadata definition by GUID or its name (unique).

## Syntax
```
pvw types readBusinessMetadataDef (--guid=<val> | --name=<val>)
```

## Required Arguments
- `--guid`: guid parameter
- `--name`: name parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--type`: Typedef name as search filter (classification | entity | enum | relationship | struct). (string)

## API Mapping
 > Types > [Get the businessMetadata definition by it's name (unique).]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/businessmetadatadef/name/{name}
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