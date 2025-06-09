# pvw glossary putPartial
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > putPartial

## Description
Create or update glossary term or category.

## Syntax
```
pvw glossary putPartial --glossaryGuid=<val> --payloadFile=<val> [--includeTermHierarchy]
```

## Required Arguments
- `--glossaryGuid`: glossaryGuid parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--categoryGuid`: The globally unique identifier of the category. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--limit`: The page size - by default there is no paging [default: 1000]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--operationGuid`: The globally unique identifier for async operation/job. (string)
- `--sort`: ASC or DESC [default: ASC]. (string)
- `--termGuid`: The globally unique identifier for glossary term. (string)

## API Mapping
Catalog Data Plane > Glossary > [Putpartial]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary/putPartial
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