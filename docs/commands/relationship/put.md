# pvw relationship put
[Command Reference](../../../README.md#command-reference) > [relationship](./main.md) > put

## Description
Create or update relationship.

## Syntax
```
pvw relationship put --payloadFile=<val>
```

## Required Arguments
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--guid`: The globally unique identifier of the relationship. (string)

## API Mapping
Catalog Data Plane > Relationship > [Put]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship/put
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