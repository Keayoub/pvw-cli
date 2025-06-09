# pvw management listPrivateLinkResources
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > listPrivateLinkResources

## Description
List all Purview accounts.

## Syntax
```
pvw management listPrivateLinkResources --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> [--groupId=<val>]
```

## Required Arguments
- `--subscriptionId`: subscriptionId parameter
- `--resourceGroupName`: resourceGroupName parameter
- `--accountName`: accountName parameter
- `--groupId`: groupId parameter

## Optional Arguments
- `--groupId`: groupId parameter (optional)
- `--scopeTenantId`: The scope tenant in which the default account is set. (string)
- `--scopeType`: The scope where the default account is set (Tenant or Subscription). (string)
- `--scope`: The scope object ID (e.g. sub ID or tenant ID). (string)
- `--privateEndpointConnectionName`: The name of the private endpoint connection. (string)
- `--objectId`: Gets or sets the object identifier of the admin. (string)

## API Mapping
Management Data Plane > Management > [Listprivatelinkresources]()
```
 https://management.azure.com/subscriptions/{subscriptionId}/providers/Microsoft.Purview/listPrivateLinkResources
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