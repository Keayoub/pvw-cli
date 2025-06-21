"""
Manage policy store operations in Microsoft Purview using modular Click-based commands.

Usage:
  policystore delete-data-policy         Delete a data policy
  policystore delete-data-policy-scope   Delete a data policy scope
  policystore put-data-policy            Create or update a data policy
  policystore put-data-policy-scope      Create or update a data policy scope
  policystore put-metadata-policy        Create or update a metadata policy
  policystore read-data-policies         Read data policies
  policystore read-data-policy-scopes    Read data policy scopes
  policystore read-metadata-policies     Read metadata policies
  policystore read-metadata-policy       Read a metadata policy by collection or policyId
  policystore read-metadata-roles        Read metadata roles
  policystore --help                     Show this help message and exit

Options:
  -h --help                              Show this help message and exit
"""
import click
from purviewcli.client._policystore import Policystore

@click.group()
def policystore():
    """
    Manage policy store operations in Microsoft Purview.
    """
    pass

def _invoke_policystore_method(method_name, **kwargs):
    client = Policystore()
    method = getattr(client, method_name)
    args = {f'--{k}': v for k, v in kwargs.items() if v is not None}
    try:
        result = method(args)
        click.echo(result)
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)

@policystore.command(name='delete-data-policy')
@click.option('--policyName', required=True)
def delete_data_policy(policyname):
    """Delete a data policy"""
    _invoke_policystore_method('policystoreDeleteDataPolicy', policyName=policyname)

@policystore.command(name='delete-data-policy-scope')
@click.option('--policyName', required=True)
@click.option('--datasource', required=True)
def delete_data_policy_scope(policyname, datasource):
    """Delete a data policy scope"""
    _invoke_policystore_method('policystoreDeleteDataPolicyScope', policyName=policyname, datasource=datasource)

@policystore.command(name='put-data-policy')
@click.option('--policyName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def put_data_policy(policyname, payloadfile):
    """Create or update a data policy"""
    _invoke_policystore_method('policystorePutDataPolicy', policyName=policyname, payloadFile=payloadfile)

@policystore.command(name='put-data-policy-scope')
@click.option('--policyName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def put_data_policy_scope(policyname, payloadfile):
    """Create or update a data policy scope"""
    _invoke_policystore_method('policystorePutDataPolicyScope', policyName=policyname, payloadFile=payloadfile)

@policystore.command(name='put-metadata-policy')
@click.option('--policyId', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def put_metadata_policy(policyid, payloadfile):
    """Create or update a metadata policy"""
    _invoke_policystore_method('policystorePutMetadataPolicy', policyId=policyid, payloadFile=payloadfile)

@policystore.command(name='read-data-policies')
@click.option('--policyName', required=False)
def read_data_policies(policyname):
    """Read data policies"""
    _invoke_policystore_method('policystoreReadDataPolicies', policyName=policyname)

@policystore.command(name='read-data-policy-scopes')
@click.option('--policyName', required=True)
def read_data_policy_scopes(policyname):
    """Read data policy scopes"""
    _invoke_policystore_method('policystoreReadDataPolicyScopes', policyName=policyname)

@policystore.command(name='read-metadata-policies')
def read_metadata_policies():
    """Read metadata policies"""
    _invoke_policystore_method('policystoreReadMetadataPolicies')

@policystore.command(name='read-metadata-policy')
@click.option('--collectionName', required=False)
@click.option('--policyId', required=False)
def read_metadata_policy(collectionname, policyid):
    """Read a metadata policy by collection or policyId"""
    _invoke_policystore_method('policystoreReadMetadataPolicy', collectionName=collectionname, policyId=policyid)

@policystore.command(name='read-metadata-roles')
def read_metadata_roles():
    """Read metadata roles"""
    _invoke_policystore_method('policystoreReadMetadataRoles')

__all__ = ['policystore']
