# pvw lineage read
[Command Reference](../../../README.md#command-reference) > [lineage](./main.md) > read

## Description
Retrieve lineage.

## Syntax
```
pvw lineage read --guid=<val> [--depth=<val> --width=<val> --direction=<val> --output=<val>]
```

## Required Arguments
- `--guid`: guid parameter
- `--depth`: depth parameter
- `--width`: width parameter
- `--direction`: direction parameter
- `--output`: output parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--limit`: The page size - by default there is no paging [default: -1]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--template`: Template type: basic, etl, column-mapping [default: basic]. (string)

## API Mapping
Discovery Data Plane > Lineage > [Read]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/lineage/read
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