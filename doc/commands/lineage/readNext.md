# pvw lineage readNext
[Command Reference](../../../README.md#command-reference) > [lineage](./main.md) > readNext

## Description
Retrieve lineage.

## Syntax
```
pvw lineage readNext --guid=<val> [--direction<val> --offset=<val> --limit=<val>]
```

## Required Arguments
- `--guid`: guid parameter
- `--offset`: offset parameter
- `--limit`: limit parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--template`: Template type: basic, etl, column-mapping [default: basic]. (string)

## API Mapping
Discovery Data Plane > Lineage > [Readnext]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/lineage/readNext
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