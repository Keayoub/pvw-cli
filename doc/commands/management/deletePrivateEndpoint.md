# pvw management deletePrivateEndpoint
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > deletePrivateEndpoint

## Description
Delete Purview account.

## Syntax
```
pvw management deletePrivateEndpoint --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --privateEndpointConnectionName=<val>
```

## Required Arguments
- `--subscriptionId`: subscriptionId parameter
- `--resourceGroupName`: resourceGroupName parameter
- `--accountName`: accountName parameter
- `--privateEndpointConnectionName`: privateEndpointConnectionName parameter

## Optional Arguments
- `--scopeTenantId`: The scope tenant in which the default account is set. (string)
- `--scopeType`: The scope where the default account is set (Tenant or Subscription). (string)
- `--scope`: The scope object ID (e.g. sub ID or tenant ID). (string)
- `--groupId`: The group identifier. (string)
- `--objectId`: Gets or sets the object identifier of the admin. (string)

## API Mapping
Management Data Plane > Management > [Deleteprivateendpoint]()
```
 https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Purview/deletePrivateEndpoint
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