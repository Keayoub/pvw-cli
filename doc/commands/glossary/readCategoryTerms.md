# pvw glossary readCategoryTerms
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > readCategoryTerms

## Description
Retrieve glossary term or category.

## Syntax
```
pvw glossary readCategoryTerms --categoryGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
```

## Required Arguments
- `--categoryGuid`: categoryGuid parameter
- `--limit`: limit parameter
- `--offset`: offset parameter
- `--sort`: sort parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--glossaryGuid`: The globally unique identifier for glossary. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--operationGuid`: The globally unique identifier for async operation/job. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--termGuid`: The globally unique identifier for glossary term. (string)

## API Mapping
Catalog Data Plane > Glossary > [Readcategoryterms]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary/readCategoryTerms
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