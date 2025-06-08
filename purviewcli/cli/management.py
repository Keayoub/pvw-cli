"""
usage: 
    pvw management addRootCollectionAdmin --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --objectId=<val>
    pvw management checkNameAvailability --subscriptionId=<val> --accountName=<val>
    pvw management createAccount --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --payloadFile=<val>
    pvw management defaultAccount --scopeTenantId=<val> --scopeType=<val> --scope=<val>
    pvw management deleteAccount --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val>
    pvw management deletePrivateEndpoint --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --privateEndpointConnectionName=<val>
    pvw management listKeys --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val>
    pvw management listOperations
    pvw management listPrivateLinkResources --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> [--groupId=<val>]
    pvw management putPrivateEndpoint --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --privateEndpointConnectionName=<val> --payloadFile=<val>
    pvw management readAccount --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val>
    pvw management readAccounts --subscriptionId=<val> [--resourceGroupName=<val>]
    pvw management readPrivateEndpoint --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --privateEndpointConnectionName=<val>
    pvw management readPrivateEndpoints --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val>
    pvw management removeDefaultAccount --scopeTenantId=<val> --scopeType=<val> --scope=<val>
    pvw management setDefaultAccount --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --scopeTenantId=<val> --scopeType=<val> --scope=<val>
    pvw management updateAccount --subscriptionId=<val> --resourceGroupName=<val> --accountName=<val> --payloadFile=<val>

options:
    --subscriptionId=<val>                  [string]  The subscription ID.
    --resourceGroupName=<val>               [string]  The name of the resource group.
    --accountName=<val>                     [string]  The name of the account.
    --scopeTenantId=<val>                   [string]  The scope tenant in which the default account is set.
    --scopeType=<val>                       [string]  The scope where the default account is set (Tenant or Subscription).
    --scope=<val>                           [string]  The scope object ID (e.g. sub ID or tenant ID).
    --groupId=<val>                         [string]  The group identifier.
    --privateEndpointConnectionName=<val>   [string]  The name of the private endpoint connection.
    --objectId=<val>                        [string]  Gets or sets the object identifier of the admin.

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
