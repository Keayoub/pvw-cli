# pvw entity deleteUniqueAttributeClassification
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > deleteUniqueAttributeClassification

## Description
Delete entity.

## Syntax
```
pvw entity deleteUniqueAttributeClassification --typeName=<val> --qualifiedName=<val> --classificationName=<val>
```

## Required Arguments
- `--typeName`: typeName parameter
- `--qualifiedName`: qualifiedName parameter
- `--classificationName`: classificationName parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--collection`: The collection unique name. (string)
- `--guid`: The globally unique identifier of the entity. (string)
- `--name`: The name of the attribute. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Catalog Data Plane > Entity > [Deleteuniqueattributeclassification]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/uniqueAttribute
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