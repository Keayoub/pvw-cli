# pvw lineage read-next
[Command Reference](../../../README.md#command-reference) > [lineage](./main.md) > read-next

## Description
Retrieve lineage.

## Syntax
```
pvw lineage read-next --guid=<val> [--direction=<val> --offset=<val> --limit=<val> --output=<val>]
```

## Required Arguments
- `--guid`: guid parameter
- `--direction`: direction parameter
- `--offset`: offset parameter
- `--limit`: limit parameter
- `--output`: output parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--template`: Template type: basic, etl, column-mapping [default: basic]. (string)

## API Mapping
Discovery Data Plane > Lineage > [Read-Next]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/lineage/read-next
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