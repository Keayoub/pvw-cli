# pvw lineage read
[Command Reference](../../../README.md#command-reference) > [lineage](./main.md) > read

## Description
Read operation for lineage

## Syntax
```
pvw lineage read --guid=<val> [--depth=<val> --width=<val> --direction=<val>]
```

## Required Arguments
- `--guid`: guid parameter
- `--depth`: depth parameter
- `--width`: width parameter
- `--direction`: direction parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--limit`: The page size - by default there is no paging [default: -1]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--template`: Template type: basic, etl, column-mapping [default: basic]. (string)

## API Mapping
 >  > []()
```
GET /api/lineage/read
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