# pvw lineage analyze
[Command Reference](../../../README.md#command-reference) > [lineage](./main.md) > analyze

## Description
Perform operation on lineage.

## Syntax
```
pvw lineage analyze --entity-guid=<val> [--direction=<val> --depth=<val> --output-file=<val>]
```

## Required Arguments
- `--direction`: direction parameter
- `--depth`: depth parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--guid`: The globally unique identifier of the entity. (string)
- `--limit`: The page size - by default there is no paging [default: -1]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--output`: Output format: json, table [default: json]. (string)
- `--template`: Template type: basic, etl, column-mapping [default: basic]. (string)

## API Mapping
Discovery Data Plane > Lineage > [Analyze]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/lineage/analyze
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