# pvw entity addLabelsByUniqueAttribute
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > addLabelsByUniqueAttribute

## Description
Add LabelsByUniqueAttribute for entity.

## Syntax
```
pvw entity addLabelsByUniqueAttribute --typeName=<val> --qualifiedName=<val> --payloadFile=<val>
```

## Required Arguments
- `--typeName`: typeName parameter
- `--qualifiedName`: qualifiedName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--classificationName`: The name of the classification. (string)
- `--collection`: The collection unique name. (string)
- `--guid`: The globally unique identifier of the entity. (string)
- `--name`: The name of the attribute. (string)

## API Mapping
Catalog Data Plane > Entity > [Addlabelsbyuniqueattribute]()
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