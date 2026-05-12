# pvw relationship put
[Command Reference](../../../README.md#command-reference) > [relationship](./main.md) > put

## Description
Create or update relationship.

## Syntax
```
pvw relationship put --payloadFile=<val>
```

## Required Arguments
- `--payloadFile`: Path to a JSON file containing the relationship definition (create or update).

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)

## API Mapping
Catalog Data Plane > Relationship > [Put]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship/put
```

## Examples

=== "Create or update from JSON file"
    ```powershell
    pvw relationship put --payloadFile=relationship.json
    ```

    Where `relationship.json` contains:
    ```json
    {
      "typeName": "Objet Information_Table_Has",
      "end1": {
        "guid": "d286692e-30bb-48ba-ac49-f7372b12d225",
        "typeName": "Objet Information"
      },
      "end2": {
        "guid": "90d14acb-cf75-4729-9245-68f6f6f60000",
        "typeName": "mssql_table"
      }
    }
    ```

## Response

Returns the created or updated relationship:
```json
{
  "typeName": "Objet Information_Table_Has",
  "end1": {
    "guid": "d286692e-30bb-48ba-ac49-f7372b12d225",
    "typeName": "Objet Information",
    "displayText": "Business Asset Name"
  },
  "end2": {
    "guid": "90d14acb-cf75-4729-9245-68f6f6f60000",
    "typeName": "mssql_table",
    "displayText": "dbo.SalesLT.SalesOrderDetail"
  }
}
```

## Notes

- **PUT vs CREATE**: The PUT endpoint (idempotent) creates the relationship if it doesn't exist, or updates it if it does.
- **Difference from POST**: POST (create) fails if the relationship already exists, while PUT (put) succeeds either way.

## Related Commands

- [`pvw relationship create`](./create.md) — Create a new relationship
- [`pvw relationship read`](./read.md) — Read a relationship by GUID
- [`pvw relationship delete`](./delete.md) — Delete a relationship