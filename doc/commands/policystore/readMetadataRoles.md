# pvw policystore readMetadataRoles
[Command Reference](../../../README.md#command-reference) > [policystore](./main.md) > readMetadataRoles

## Description
Retrieve policy.

## Syntax
```
pvw policystore readMetadataRoles
```

## Required Arguments
No required arguments.

## Optional Arguments
- `--purviewName`: Azure Purview account name. (string)
- `--collectionName`: The technical name of the Collection (e.g. friendlyName: Sales; name: afwbxs). (string)
- `--policyId`: The unique policy id. (string)
- `--payloadFile`: File path to a valid JSON document. (string)

## API Mapping
Policy Data Plane > Policystore > [Readmetadataroles]()
```
 https://{accountName}.purview.azure.com/policystore/api/readMetadataRoles
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