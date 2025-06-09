# pvw policystore readDataPolicies
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > readDataPolicies

## Description
Retrieve policy.

## Syntax
```
pvw policystore readDataPolicies [--policyName=<val>]
```

## Required Arguments
- `--policyName`: policyName parameter

## Optional Arguments
- `--policyName`: policyName parameter (optional)
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the Collection (e.g. friendlyName: Sales; name: afwbxs). (string)
- `--policyId`: The unique policy id. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Policy Data Plane > Policystore > [Readdatapolicies]()
```
 https://{accountName}.purview.azure.com/policystore/api/readDataPolicies
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