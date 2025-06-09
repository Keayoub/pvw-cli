# pvw policystore putDataPolicy
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > putDataPolicy

## Description
Create or update policy.

## Syntax
```
pvw policystore putDataPolicy --policyName=<val> --payloadFile=<val>
```

## Required Arguments
- `--policyName`: policyName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the Collection (e.g. friendlyName: Sales; name: afwbxs). (string)
- `--policyId`: The unique policy id. (string)

## API Mapping
Policy Data Plane > Policystore > [Putdatapolicy]()
```
 https://{accountName}.purview.azure.com/policystore/api/putDataPolicy
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