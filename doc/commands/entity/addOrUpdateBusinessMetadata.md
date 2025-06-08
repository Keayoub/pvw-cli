# pvw entity addOrUpdateBusinessMetadata
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > addOrUpdateBusinessMetadata

## Description
Add or update business metadata to an entity.

## Syntax
```
pvw entity addOrUpdateBusinessMetadata --guid=<val> --payloadFile=<val> [--isOverwrite]
```

## Required Arguments
- `--guid`: guid parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--classificationName`: The name of the classification. (string)
- `--collection`: The collection unique name. (string)
- `--name`: The name of the attribute. (string)
- `--qualifiedName`: The qualified name of the entity. (string)
- `--typeName`: The name of the type. (string)

## API Mapping
 > Entity > [Add Or Update Business Metadata]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata
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