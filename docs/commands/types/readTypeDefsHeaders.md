# pvw types readTypeDefsHeaders
[Command Reference](../../../README.md#command-reference) > [types](./main.md) > readTypeDefsHeaders

## Description
Retrieve type definition.

## Syntax
```
pvw types readTypeDefsHeaders [--includeTermTemplate --type=<val>]
```

## Required Arguments
- `--type`: type parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--guid`: The globally unique identifier. (string)
- `--name`: The name of the definition. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Catalog Data Plane > Types > [Readtypedefsheaders]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/readTypeDefsHeaders
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