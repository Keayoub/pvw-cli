# pvw search query
[Command Reference](../../../README.md#command-reference) > [search](./main.md) > query

## Description
Query catalog.

## Syntax
```
pvw search query [--keywords=<val> --limit=<val> --offset=<val> --filterFile=<val> --facets-file=<val>]
```

## Required Arguments
- `--keywords`: keywords parameter
- `--limit`: limit parameter
- `--offset`: offset parameter
- `--filterFile`: filterFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--entityType`: The entity type to browse as the root level entry point. (string)
- `--path`: The path to browse the next level child entities. (string)

## API Mapping
Discovery Data Plane > Search > [Query]()
```
 https://{accountName}.purview.azure.com/catalog/api/search/query
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