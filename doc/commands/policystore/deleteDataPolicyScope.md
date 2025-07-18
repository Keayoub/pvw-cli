# pvw policystore deleteDataPolicyScope
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > deleteDataPolicyScope

## Description
Delete policy.

## Syntax
```
pvw policystore deleteDataPolicyScope --policyName=<val> --datasource=<val>
```

## Required Arguments
- `--policyName`: policyName parameter
- `--datasource`: datasource parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--collectionName`: The technical name of the Collection (e.g. friendlyName: Sales; name: afwbxs). (string)
- `--policyId`: The unique policy id. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Policy Data Plane > Policystore > [Deletedatapolicyscope]()
```
 https://{accountName}.purview.azure.com/policystore/api/deleteDataPolicyScope
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