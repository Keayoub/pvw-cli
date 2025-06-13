"""
Manage policy store operations in Microsoft Purview using modular Click-based commands.

Usage:
  policystore deleteDataPolicy         Delete a data policy
  policystore deleteDataPolicyScope    Delete a data policy scope
  policystore putDataPolicy            Create or update a data policy
  policystore putDataPolicyScope       Create or update a data policy scope
  policystore putMetadataPolicy        Create or update a metadata policy
  policystore readDataPolicies         Read data policies
  policystore readDataPolicyScopes     Read data policy scopes
  policystore readMetadataPolicies     Read metadata policies
  policystore readMetadataPolicy       Read a metadata policy by collection or policyId
  policystore readMetadataRoles        Read metadata roles
  policystore --help                   Show this help message and exit

Options:
  -h --help                            Show this help message and exit
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

@policystore.command()
@click.option('--policyName', required=True)
def deletedatapolicy(policyname):
    """Delete a data policy"""
    _invoke_policystore_method('policystoreDeleteDataPolicy', policyName=policyname)

@policystore.command()
@click.option('--policyName', required=True)
@click.option('--datasource', required=True)
def deletedatapolicyscope(policyname, datasource):
    """Delete a data policy scope"""
    _invoke_policystore_method('policystoreDeleteDataPolicyScope', policyName=policyname, datasource=datasource)

@policystore.command()
@click.option('--policyName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putdatapolicy(policyname, payloadfile):
    """Create or update a data policy"""
    _invoke_policystore_method('policystorePutDataPolicy', policyName=policyname, payloadFile=payloadfile)

@policystore.command()
@click.option('--policyName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putdatapolicyscope(policyname, payloadfile):
    """Create or update a data policy scope"""
    _invoke_policystore_method('policystorePutDataPolicyScope', policyName=policyname, payloadFile=payloadfile)

@policystore.command()
@click.option('--policyId', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putmetadatapolicy(policyid, payloadfile):
    """Create or update a metadata policy"""
    _invoke_policystore_method('policystorePutMetadataPolicy', policyId=policyid, payloadFile=payloadfile)

@policystore.command()
@click.option('--policyName', required=False)
def readdatapolicies(policyname):
    """Read data policies"""
    _invoke_policystore_method('policystoreReadDataPolicies', policyName=policyname)

@policystore.command()
@click.option('--policyName', required=True)
def readdatapolicyscopes(policyname):
    """Read data policy scopes"""
    _invoke_policystore_method('policystoreReadDataPolicyScopes', policyName=policyname)

@policystore.command()
def readmetadatapolicies():
    """Read metadata policies"""
    _invoke_policystore_method('policystoreReadMetadataPolicies')

@policystore.command()
@click.option('--collectionName', required=False)
@click.option('--policyId', required=False)
def readmetadatapolicy(collectionname, policyid):
    """Read a metadata policy by collection or policyId"""
    _invoke_policystore_method('policystoreReadMetadataPolicy', collectionName=collectionname, policyId=policyid)

@policystore.command()
def readmetadataroles():
    """Read metadata roles"""
    _invoke_policystore_method('policystoreReadMetadataRoles')

__all__ = ['policystore']
