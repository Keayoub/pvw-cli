# pvw entity deleteClassification
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > deleteClassification

## Description
Delete entity.

## Syntax
```
pvw entity deleteClassification --guid=<val> --classificationName=<val>
```

## Required Arguments
- `--guid`: guid parameter
- `--classificationName`: classificationName parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--collection`: The collection unique name. (string)
- `--name`: The name of the attribute. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--qualifiedName`: The qualified name of the entity. (string)
- `--typeName`: The name of the type. (string)

## API Mapping
Catalog Data Plane > Entity > [Deleteclassification]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/classification
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