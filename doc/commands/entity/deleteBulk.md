# pvw entity deleteBulk
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > deleteBulk

## Description
Deletebulk operation for entity

## Syntax
```
pvw entity deleteBulk --guid=<val>...
```

## Required Arguments
- `--guid`: guid parameter

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
 >  > []()
```
GET /api/entity/deleteBulk
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