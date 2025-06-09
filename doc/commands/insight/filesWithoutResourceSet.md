# pvw insight filesWithoutResourceSet
[Command Reference](../../../README.md#command-reference) > [insight](./main.md) > filesWithoutResourceSet

## Description
Perform operation on analytics insights.

## Syntax
```
pvw insight filesWithoutResourceSet
```

## Required Arguments
No required arguments.

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--numberOfDays`: Trailing time period in days [default: 30]. (integer)

## API Mapping
Analytics Data Plane > Insight > [Fileswithoutresourceset]()
```
 https://{accountName}.purview.azure.com/catalog/api/browse/filesWithoutResourceSet
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