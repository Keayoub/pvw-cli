# pvw types readTypeDefs
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > readTypeDefs

## Description
Retrieve type definition.

## Syntax
```
pvw types readTypeDefs [--includeTermTemplate --type=<val>]
```

## Required Arguments
- `--type`: type parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--guid`: The globally unique identifier. (string)
- `--name`: The name of the definition. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Catalog Data Plane > Types > [Readtypedefs]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/readTypeDefs
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