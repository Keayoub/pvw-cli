# pvw entity createOrUpdateCollectionBulk
[Command Reference](../../../README.md#command-reference) > [entity](./main.md) > createOrUpdateCollectionBulk

## Description
Createorupdatecollectionbulk operation for entity

## Syntax
```
pvw entity createOrUpdateCollectionBulk --collection=<val> --payloadFile=<val>
```

## Required Arguments
- `--collection`: collection parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--bmFile`: File path to a valid business metadata template CSV file. (string)
- `--bmName`: BusinessMetadata name. (string)
- `--classificationName`: The name of the classification. (string)
- `--guid`: The globally unique identifier of the entity. (string)
- `--name`: The name of the attribute. (string)
- `--qualifiedName`: The qualified name of the entity. (string)
- `--typeName`: The name of the type. (string)

## API Mapping
 >  > []()
```
GET /api/entity/createOrUpdateCollectionBulk
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