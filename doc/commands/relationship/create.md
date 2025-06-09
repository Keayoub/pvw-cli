# pvw relationship create
[Command Reference](../../../README.md#command-reference) > [relationship](./main.md) > create

## Description
Create a new relationship.

## Syntax
```
pvw relationship create --payloadFile=<val>
```

## Required Arguments
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--guid`: The globally unique identifier of the relationship. (string)

## API Mapping
Catalog Data Plane > Relationship > [Create]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship/create
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