# pvw insight tags
[Command Reference](../../../README.md#command-reference) > [insight](./main.md) > tags

## Description
Perform operation on analytics insights.

## Syntax
```
pvw insight tags
```

## Required Arguments
No required arguments.

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--numberOfDays`: Trailing time period in days [default: 30]. (integer)

## API Mapping
Analytics Data Plane > Insight > [Tags]()
```
 https://{accountName}.purview.azure.com/catalog/api/browse/tags
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