# pvw management checkNameAvailability
[Command Reference](../../../README.md#command-reference) > [management](./main.md) > checkNameAvailability

## Description
Checknameavailability operation for management

## Syntax
```
pvw management checkNameAvailability --subscriptionId=<val> --accountName=<val>
```

## Required Arguments
- `--subscriptionId`: subscriptionId parameter
- `--accountName`: accountName parameter

## Optional Arguments
- `--resourceGroupName`: The name of the resource group. (string)
- `--scopeTenantId`: The scope tenant in which the default account is set. (string)
- `--scopeType`: The scope where the default account is set (Tenant or Subscription). (string)
- `--scope`: The scope object ID (e.g. sub ID or tenant ID). (string)
- `--groupId`: The group identifier. (string)
- `--privateEndpointConnectionName`: The name of the private endpoint connection. (string)
- `--objectId`: Gets or sets the object identifier of the admin. (string)

## API Mapping
 >  > []()
```
GET /api/management/checkNameAvailability
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