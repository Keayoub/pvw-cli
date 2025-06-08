# pvw policystore deleteDataPolicy
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > deleteDataPolicy

## Description
Delete a data policy.

## Syntax
```
pvw policystore deleteDataPolicy --policyName=<val>
```

## Required Arguments
`--policyName` (string)  
The name of the data policy.

## Optional Arguments
*None*

## API Mapping
Delete a data policy.
```
DELETE https://{accountName}.purview.azure.com/policystore/dataPolicies/{policyName}
```

## Examples
Delete a data policy.
```powershell
pvw policystore deleteDataPolicy --policyName "new-policy"
```
