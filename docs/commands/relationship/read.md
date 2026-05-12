# pvw relationship read
[Command Reference](../../../README.md#command-reference) > [relationship](./main.md) > read

## Description
Retrieve relationship.

## Syntax
```
pvw relationship read --guid=<val> [--extendedInfo]
```

## Required Arguments
- `--guid`: The globally unique identifier (GUID) of the relationship to retrieve.

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--extendedInfo`: Include extended information in the response. (boolean) [default: false]

## API Mapping
Catalog Data Plane > Relationship > [Read]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/relationship/read
```

## Examples

=== "Read relationship"
    ```powershell
    pvw relationship read --guid d286692e-30bb-48ba-ac49-f7372b12d225
    ```

=== "Read with extended info"
    ```powershell
    pvw relationship read --guid d286692e-30bb-48ba-ac49-f7372b12d225 --extendedInfo
    ```

## Output

Returns the relationship object:
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

## Related Commands

- [`pvw relationship create`](./create.md) — Create a new relationship
- [`pvw relationship delete`](./delete.md) — Delete a relationship
- [`pvw search query`](../search/main.md) — Find entity GUIDs