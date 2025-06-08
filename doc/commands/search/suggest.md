# pvw search suggest
[Command Reference](../../../README.md#command-reference) > [search](./main.md) > suggest

## Description
Suggest operation for search

## Syntax
```
pvw search suggest [--keywords=<val> --limit=<val> --filterFile=<val>]
```

## Required Arguments
- `--keywords`: keywords parameter
- `--limit`: limit parameter
- `--filterFile`: filterFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--entityType`: The entity type to browse as the root level entry point. (string)
- `--path`: The path to browse the next level child entities. (string)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)

## API Mapping
 >  > []()
```
GET /api/search/suggest
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