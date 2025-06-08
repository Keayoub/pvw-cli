# pvw lineage csv
[Command Reference](../../../README.md#command-reference) > [lineage](./main.md) > csv

## Description
Csv operation for lineage

## Syntax
```
pvw lineage csv templates
```

## Required Arguments
No required arguments.

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--guid`: The globally unique identifier of the entity. (string)
- `--limit`: The page size - by default there is no paging [default: -1]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--template`: Template type: basic, etl, column-mapping [default: basic]. (string)

## API Mapping
 >  > []()
```
GET /api/lineage/csv
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