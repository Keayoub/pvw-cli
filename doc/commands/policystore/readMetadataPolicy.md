# pvw policystore readMetadataPolicy
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > readMetadataPolicy

## Description
Retrieve policy.

## Syntax
```
pvw policystore readMetadataPolicy (--collectionName=<val> | --policyId=<val>)
```

## Required Arguments
- `--collectionName`: collectionName parameter
- `--policyId`: policyId parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Policy Data Plane > Policystore > [Readmetadatapolicy]()
```
 https://{accountName}.purview.azure.com/policystore/api/readMetadataPolicy
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