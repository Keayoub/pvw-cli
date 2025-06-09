# pvw glossary deleteTerm
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > deleteTerm

## Description
Delete glossary term or category.

## Syntax
```
pvw glossary deleteTerm --termGuid=<val>
```

## Required Arguments
- `--termGuid`: termGuid parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--categoryGuid`: The globally unique identifier of the category. (string)
- `--glossaryGuid`: The globally unique identifier for glossary. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--limit`: The page size - by default there is no paging [default: 1000]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--operationGuid`: The globally unique identifier for async operation/job. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--sort`: ASC or DESC [default: ASC]. (string)

## API Mapping
Catalog Data Plane > Glossary > [Deleteterm]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary/deleteTerm
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