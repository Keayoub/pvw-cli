# pvw glossary readTermsHeaders
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > readTermsHeaders

## Description
Retrieve glossary term or category.

## Syntax
```
pvw glossary readTermsHeaders --glossaryGuid=<val> [--limit=<val> --offset=<val> --sort=<val>]
```

## Required Arguments
- `--glossaryGuid`: glossaryGuid parameter
- `--limit`: limit parameter
- `--offset`: offset parameter
- `--sort`: sort parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--categoryGuid`: The globally unique identifier of the category. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--operationGuid`: The globally unique identifier for async operation/job. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--termGuid`: The globally unique identifier for glossary term. (string)

## API Mapping
Catalog Data Plane > Glossary > [Readtermsheaders]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/glossary/readTermsHeaders
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