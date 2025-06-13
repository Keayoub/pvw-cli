# pvw glossary deleteCategory
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > deleteCategory

## Description
Delete glossary term or category.

## Syntax
```
pvw glossary deleteCategory --categoryGuid=<val>
```

## Required Arguments
- `--categoryGuid`: categoryGuid parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--glossaryGuid`: The globally unique identifier for glossary. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--limit`: The page size - by default there is no paging [default: 1000]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--operationGuid`: The globally unique identifier for async operation/job. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--sort`: ASC or DESC [default: ASC]. (string)
- `--termGuid`: The globally unique identifier for glossary term. (string)

## API Mapping
Catalog Data Plane > Glossary > [Deletecategory]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary/deleteCategory
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