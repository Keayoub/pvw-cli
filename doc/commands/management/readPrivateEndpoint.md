# pvw management readPrivateEndpoint
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > readPrivateEndpoint

## Description
Readprivateendpoint operation for management

## Syntax
```
pvw management readPrivateEndpoint --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --privateEndpointConnectionName=<val>
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
 >  > []()
```
GET /api/management/readPrivateEndpoint
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