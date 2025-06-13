# pvw policystore putDataPolicyScope
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > putDataPolicyScope

## Description
Create or update policy.

## Syntax
```
pvw policystore putDataPolicyScope --policyName=<val> --payloadFile=<val>
```

## Required Arguments
- `--policyName`: policyName parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--collectionName`: The technical name of the Collection (e.g. friendlyName: Sales; name: afwbxs). (string)
- `--policyId`: The unique policy id. (string)

## API Mapping
Policy Data Plane > Policystore > [Putdatapolicyscope]()
```
 https://{accountName}.purview.azure.com/policystore/api/putDataPolicyScope
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