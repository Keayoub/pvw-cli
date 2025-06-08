# pvw glossary putTermsAssignedEntities
[Command Reference](../../../README.md#command-reference) > [glossary](./main.md) > putTermsAssignedEntities

## Description
Puttermsassignedentities operation for glossary

## Syntax
```
pvw glossary putTermsAssignedEntities --termGuid=<val> --payloadFile=<val>
```

## Required Arguments
- `--termGuid`: termGuid parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--categoryGuid`: The globally unique identifier of the category. (string)
- `--glossaryGuid`: The globally unique identifier for glossary. (string)
- `--glossaryName`: The name of the glossary. (string)
- `--limit`: The page size - by default there is no paging [default: 1000]. (integer)
- `--offset`: Offset for pagination purpose [default: 0]. (integer)
- `--operationGuid`: The globally unique identifier for async operation/job. (string)
- `--sort`: ASC or DESC [default: ASC]. (string)

## API Mapping
 >  > []()
```
GET /api/glossary/putTermsAssignedEntities
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