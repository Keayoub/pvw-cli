# pvw relationship delete
[Command Reference](../../../README.md#command-reference) > [relationship](./main.md) > delete

## Description
Delete relationship.

## Syntax
```
pvw relationship delete --guid=<val>
```

## Required Arguments
- `--guid`: guid parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Catalog Data Plane > Relationship > [Delete]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship/delete
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