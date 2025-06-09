# pvw policystore readMetadataPolicies
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > readMetadataPolicies

## Description
Retrieve policy.

## Syntax
```
pvw policystore readMetadataPolicies
```

## Required Arguments
No required arguments.

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the Collection (e.g. friendlyName: Sales; name: afwbxs). (string)
- `--policyId`: The unique policy id. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Policy Data Plane > Policystore > [Readmetadatapolicies]()
```
 https://{accountName}.purview.azure.com/policystore/api/readMetadataPolicies
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