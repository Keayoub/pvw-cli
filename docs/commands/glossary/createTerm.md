# pvw glossary createTerm
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > createTerm

## Description
Create a new glossary term or category.

## Syntax
```
pvw glossary createTerm --payloadFile=<val> [--includeTermHierarchy]
```

## Required Arguments
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--categoryGuid`: The globally unique identifier of the category. (string)
- `--glossaryGuid`: The globally unique identifier for glossary. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--limit`: The page size - by default there is no paging [default: 1000]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--operationGuid`: The globally unique identifier for async operation/job. (string)
- `--sort`: ASC or DESC [default: ASC]. (string)
- `--termGuid`: The globally unique identifier for glossary term. (string)

## API Mapping
Catalog Data Plane > Glossary > [Createterm]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary/createTerm
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