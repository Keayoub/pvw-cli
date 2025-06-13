# pvw policystore putMetadataPolicy
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > putMetadataPolicy

## Description
Create or update policy.

## Syntax
```
pvw policystore putMetadataPolicy --policyId=<val> --payloadFile=<val>
```

## Required Arguments
- `--policyId`: policyId parameter
- `--payloadFile`: payloadFile parameter

## Optional Arguments
- `--purviewName`: Microsoft Purview account name. (string)
- `--collectionName`: The technical name of the Collection (e.g. friendlyName: Sales; name: afwbxs). (string)

## API Mapping
Policy Data Plane > Policystore > [Putmetadatapolicy]()
```
 https://{accountName}.purview.azure.com/policystore/api/putMetadataPolicy
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