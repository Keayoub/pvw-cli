# pvw search browse
[Command Reference](../../../README.md#command-reference) > [search](./main.md) > browse

## Description
Browse catalog.

## Syntax
```
pvw search browse  (--entityType=<val> | --path=<val>) [--limit=<val> --offset=<val>]
```

## Required Arguments
- `--entityType`: entityType parameter
- `--path`: path parameter
- `--limit`: limit parameter
- `--offset`: offset parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--keywords`: The keywords applied to all searchable fields. (string)
- `--filterFile`: File path to a filter json file. (string)

## API Mapping
Discovery Data Plane > Search > [Browse]()
```
 https://{accountName}.purview.azure.com/catalog/api/search/browse
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