# pvw entity deleteBusinessAttribute
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > deleteBusinessAttribute

## Description
Delete business metadata from an entity.

## Syntax
```
pvw entity deleteBusinessAttribute --guid=<val> --bmName=<val> --payloadFile=<val>
```

## Required Arguments
- `--guid`: guid parameter
- `--bmName`: bmName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--classificationName`: The name of the classification. (string)
- `--collection`: The collection unique name. (string)
- `--name`: The name of the attribute. (string)
- `--qualifiedName`: The qualified name of the entity. (string)
- `--typeName`: The name of the type. (string)

## API Mapping
 > Entity > [Delete Business Attributes]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata/{bmName}
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