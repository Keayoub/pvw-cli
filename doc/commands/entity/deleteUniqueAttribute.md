# pvw entity deleteUniqueAttribute
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > deleteUniqueAttribute

## Description
Delete entity.

## Syntax
```
pvw entity deleteUniqueAttribute --typeName=<val> --qualifiedName=<val>
```

## Required Arguments
- `--typeName`: typeName parameter
- `--qualifiedName`: qualifiedName parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--classificationName`: The name of the classification. (string)
- `--collection`: The collection unique name. (string)
- `--guid`: The globally unique identifier of the entity. (string)
- `--name`: The name of the attribute. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Catalog Data Plane > Entity > [Deleteuniqueattribute]()
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