# pvw entity importBusinessMetadata
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > importBusinessMetadata

## Description
Import entity.

## Syntax
```
pvw entity importBusinessMetadata --bmFile=<val>
```

## Required Arguments
- `--bmFile`: bmFile parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--classificationName`: The name of the classification. (string)
- `--collection`: The collection unique name. (string)
- `--guid`: The globally unique identifier of the entity. (string)
- `--name`: The name of the attribute. (string)
- `--payloadFile`: File path to a valid JSON document. (string)
- `--qualifiedName`: The qualified name of the entity. (string)
- `--typeName`: The name of the type. (string)

## API Mapping
Catalog Data Plane > Entity > [Importbusinessmetadata]()
```
 https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/businessmetadata
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