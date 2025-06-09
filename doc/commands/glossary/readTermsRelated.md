# pvw glossary readTermsRelated
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > readTermsRelated

## Description
Retrieve glossary term or category.

## Syntax
```
pvw glossary readTermsRelated --termGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
```

## Required Arguments
- `--termGuid`: termGuid parameter
- `--limit`: limit parameter
- `--offset`: offset parameter
- `--sort`: sort parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--categoryGuid`: The globally unique identifier of the category. (string)
- `--glossaryGuid`: The globally unique identifier for glossary. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--operationGuid`: The globally unique identifier for async operation/job. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Catalog Data Plane > Glossary > [Readtermsrelated]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary/readTermsRelated
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