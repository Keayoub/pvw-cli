# pvw account getAccessKeys
[Command Reference](../../../README.md#command-reference) > [account](./main.md) > getAccessKeys

## Description
List the authorization keys associated with this account.

## Syntax
```
pvw account getAccessKeys
```

## Required Arguments
*None*

## Optional Arguments
*None*

## API Mapping
Account Data Plane > Accounts > [Get Access Keys](https://docs.microsoft.com/en-us/rest/api/purview/accountdataplane/accounts/get-access-keys)
```
POST https://{accountName}.purview.azure.com/account/listkeys
```

## Examples
Get access keys (e.g. Atlas Kafka endpoint connection strings).
```powershell
pvw account getAccessKeys
```

<details><summary>Sample response.</summary>
<p>

```json
{
    "atlasKafkaPrimaryEndpoint": "Endpoint=sb://atlas-YOUR_ENDPOINT.servicebus.windows.net/;SharedAccessKeyName=AlternateSharedAccessKey;SharedAccessKey=YOUR_KEY",
    "atlasKafkaSecondaryEndpoint": "Endpoint=sb://atlas-YOUR_ENDPOINT.servicebus.windows.net/;SharedAccessKeyName=AlternateSharedAccessKey;SharedAccessKey=YOUR_KEY"
}
```
</p>
</details>
