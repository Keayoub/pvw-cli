# pvw relationship delete
[Command Reference](../../../README.md#command-reference) > [relationship](./main.md) > delete

## Description
Delete relationship.

## Syntax
```
pvw relationship delete --guid=<val>
```

## Required Arguments
- `--guid`: The globally unique identifier (GUID) of the relationship to delete.

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)

## API Mapping
Catalog Data Plane > Relationship > [Delete]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship/delete
```

## Examples

=== "Delete relationship"
    ```powershell
    pvw relationship delete --guid d286692e-30bb-48ba-ac49-f7372b12d225
    ```

## Response

Returns success status:
```json
{
  "status": "success"
}
```

Or on error:
```json
{
  "status": "error",
  "message": "Relationship not found"
}
```

## Related Commands

- [`pvw relationship read`](./read.md) — Read a relationship by GUID
- [`pvw relationship create`](./create.md) — Create a new relationship
- [`pvw search query`](../search/main.md) — Find relationship GUIDs