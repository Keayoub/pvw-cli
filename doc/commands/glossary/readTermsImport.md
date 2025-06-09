# pvw glossary readTermsImport
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > readTermsImport

## Description
Retrieve glossary term or category.

## Syntax
```
pvw glossary readTermsImport --operationGuid=<val>
```

## Required Arguments
- `--operationGuid`: operationGuid parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--categoryGuid`: The globally unique identifier of the category. (string)
- `--glossaryGuid`: The globally unique identifier for glossary. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--limit`: The page size - by default there is no paging [default: 1000]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--sort`: ASC or DESC [default: ASC]. (string)
- `--termGuid`: The globally unique identifier for glossary term. (string)

## API Mapping
Catalog Data Plane > Glossary > [Readtermsimport]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary/readTermsImport
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