# pvw entity addLabels
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > addLabels

## Description
Add Labels for entity.

## Syntax
```
pvw entity addLabels --guid=<val> --payloadFile=<val>
```

## Required Arguments
- `--guid`: guid parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--classificationName`: The name of the classification. (string)
- `--collection`: The collection unique name. (string)
- `--name`: The name of the attribute. (string)
- `--qualifiedName`: The qualified name of the entity. (string)
- `--typeName`: The name of the type. (string)

## API Mapping
Catalog Data Plane > Entity > [Addlabels]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/labels
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