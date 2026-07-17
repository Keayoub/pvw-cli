# pvw relationship read
[Command Reference](../../../README.md#command-reference) > [relationship](./main.md) > read

## Description
Retrieve relationship.

## Syntax
```
pvw relationship read --guid=<val> [--extendedInfo]
```

## Required Arguments
- `--guid`: guid parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Catalog Data Plane > Relationship > [Read]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship/read
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