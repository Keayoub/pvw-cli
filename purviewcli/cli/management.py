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
import click
from purviewcli.client._management import Management

@click.group()
def management():
    """
    Manage metastore operations in Microsoft Purview.
    """
    pass

def _invoke_management_method(method_name, **kwargs):
    client = Management()
    method = getattr(client, method_name)
    args = {f'--{k}': v for k, v in kwargs.items() if v is not None}
    try:
        result = method(args)
        click.echo(result)
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)

@management.command()
def listoperations():
    """List management operations"""
    _invoke_management_method('managementListOperations')

@management.command()
@click.option('--subscriptionId', required=True)
@click.option('--accountName', required=True)
def checknameavailability(subscriptionid, accountname):
    """Check account name availability"""
    _invoke_management_method('managementCheckNameAvailability', subscriptionId=subscriptionid, accountName=accountname)

@management.command()
@click.option('--subscriptionId', required=True)
@click.option('--resourceGroupName', required=False)
def readaccounts(subscriptionid, resourcegroupname):
    """Read all accounts or by resource group"""
    _invoke_management_method('managementReadAccounts', subscriptionId=subscriptionid, resourceGroupName=resourcegroupname)

@management.command()
@click.option('--subscriptionId', required=True)
@click.option('--resourceGroupName', required=True)
@click.option('--accountName', required=True)
def readaccount(subscriptionid, resourcegroupname, accountname):
    """Read a specific account"""
    _invoke_management_method('managementReadAccount', subscriptionId=subscriptionid, resourceGroupName=resourcegroupname, accountName=accountname)

@management.command()
@click.option('--subscriptionId', required=True)
@click.option('--resourceGroupName', required=True)
@click.option('--accountName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def createaccount(subscriptionid, resourcegroupname, accountname, payloadfile):
    """Create a new account"""
    _invoke_management_method('managementCreateAccount', subscriptionId=subscriptionid, resourceGroupName=resourcegroupname, accountName=accountname, payloadFile=payloadfile)

@management.command()
@click.option('--subscriptionId', required=True)
@click.option('--resourceGroupName', required=True)
@click.option('--accountName', required=True)
def deleteaccount(subscriptionid, resourcegroupname, accountname):
    """Delete an account"""
    _invoke_management_method('managementDeleteAccount', subscriptionId=subscriptionid, resourceGroupName=resourcegroupname, accountName=accountname)

@management.command()
@click.option('--subscriptionId', required=True)
@click.option('--resourceGroupName', required=True)
@click.option('--accountName', required=True)
def listkeys(subscriptionid, resourcegroupname, accountname):
    """List account keys"""
    _invoke_management_method('managementListKeys', subscriptionId=subscriptionid, resourceGroupName=resourcegroupname, accountName=accountname)

@management.command()
@click.option('--subscriptionId', required=True)
@click.option('--resourceGroupName', required=True)
@click.option('--accountName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def updateaccount(subscriptionid, resourcegroupname, accountname, payloadfile):
    """Update an account"""
    _invoke_management_method('managementUpdateAccount', subscriptionId=subscriptionid, resourceGroupName=resourcegroupname, accountName=accountname, payloadFile=payloadfile)

@management.command()
@click.option('--scopeTenantId', required=True)
@click.option('--scopeType', required=True)
@click.option('--scope', required=True)
def defaultaccount(scopetenantid, scopetype, scope):
    """Get the default account for a scope"""
    _invoke_management_method('managementDefaultAccount', scopeTenantId=scopetenantid, scopeType=scopetype, scope=scope)

@management.command()
@click.option('--subscriptionId', required=True)
@click.option('--resourceGroupName', required=True)
@click.option('--accountName', required=True)
@click.option('--scopeTenantId', required=True)
@click.option('--scopeType', required=True)
@click.option('--scope', required=True)
def setdefaultaccount(subscriptionid, resourcegroupname, accountname, scopetenantid, scopetype, scope):
    """Set the default account for a scope"""
    _invoke_management_method('managementSetDefaultAccount', subscriptionId=subscriptionid, resourceGroupName=resourcegroupname, accountName=accountname, scopeTenantId=scopetenantid, scopeType=scopetype, scope=scope)

@management.command()
@click.option('--scopeTenantId', required=True)
@click.option('--scopeType', required=True)
@click.option('--scope', required=True)
def removedefaultaccount(scopetenantid, scopetype, scope):
    """Remove the default account for a scope"""
    _invoke_management_method('managementRemoveDefaultAccount', scopeTenantId=scopetenantid, scopeType=scopetype, scope=scope)

__all__ = ['management']
