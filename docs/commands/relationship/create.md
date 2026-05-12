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
- `--purviewName`: Microsoft Purview account name. (string)
- `--guid`: The globally unique identifier of the relationship. (string)

## API Mapping
Catalog Data Plane > Relationship > [Create]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship/create
```

## Examples

=== "Create from JSON file"
    ```powershell
    pvw relationship create --payloadFile=relationship.json
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

## Related Commands

- [`pvw relationship read`](./read.md) — Read a relationship by GUID
- [`pvw relationship put`](./put.md) — Update or create a relationship
- [`pvw relationship delete`](./delete.md) — Delete a relationship
- [`pvw relationship bulk-create-csv`](./bulk-create-csv.md) — Create multiple relationships from CSV