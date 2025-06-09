# pvw entity put
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > put

## Description
Create or update entity.

## Syntax
```
pvw entity put --guid=<val> --attrName=<val> --attrValue=<val>
```

## Required Arguments
- `--guid`: guid parameter
- `--attrName`: attrName parameter
- `--attrValue`: attrValue parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--classificationName`: The name of the classification. (string)
- `--collection`: The collection unique name. (string)
- `--name`: The name of the attribute. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--qualifiedName`: The qualified name of the entity. (string)
- `--typeName`: The name of the type. (string)

## API Mapping
Catalog Data Plane > Entity > [Put]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/put
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