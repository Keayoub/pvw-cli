"""
Manage scan operations in Azure Purview using modular Click-based commands.

All scan operations are exposed as modular Click-based commands for full CLI visibility and maintainability.

Usage:
  scan cancel-scan                 Cancel a scan run
  scan delete-classification-rule  Delete a classification rule
  scan delete-credential           Delete a credential
  scan delete-data-source          Delete a data source
  scan delete-key-vault            Delete a key vault
  scan delete-scan                 Delete a scan
  scan delete-scan-ruleset         Delete a scan ruleset
  scan delete-trigger              Delete a scan trigger
  scan put-classification-rule     Create or update a classification rule
  scan put-credential              Create or update a credential
  scan put-data-source             Create or update a data source
  scan put-filter                  Create or update a scan filter
  scan put-key-vault               Create or update a key vault
  scan put-scan                    Create or update a scan
  scan put-scan-ruleset            Create or update a scan ruleset
  scan put-trigger                 Create or update a scan trigger
  scan read-classification-rule    Read a classification rule
  scan read-classification-rules   Read classification rules
  scan read-credential             Read a credential
  scan read-data-source            Read a data source
  scan read-data-sources           Read data sources
  scan read-filters                Read scan filters
  scan read-key-vault              Read a key vault
  scan read-key-vaults             Read key vaults
  scan read-scan                   Read a scan
  scan read-scan-history           Read scan history
  scan read-scan-ruleset           Read a scan ruleset
  scan read-scan-rulesets          Read scan rulesets
  scan read-scans                  Read scans
  scan read-system-scan-ruleset    Read a system scan ruleset
  scan run-scan                    Run a scan
  scan tag-classification-version  Tag a classification version
  scan --help                      Show this help message and exit

Options:
  -h --help                        Show this help message and exit
"""
# Scan CLI for Purview Data Map API (Atlas v2)
"""
CLI for managing scans, scan rulesets, triggers, and scan runs
"""
import click
from purviewcli.client._scan import Scan

@click.group()
def scan():
    """Manage scans and related resources"""
    pass

# Helper to invoke Scan methods
def _invoke_scan_method(method_name, **kwargs):
    scan_client = Scan()
    method = getattr(scan_client, method_name)
    args = {f'--{k}': v for k, v in kwargs.items() if v is not None}
    try:
        result = method(args)
        click.echo(result)
    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
@click.option('--runId', required=True)
def cancelscan(datasourcename, scanname, runid):
    """Cancel a running scan"""
    _invoke_scan_method('scanCancelScan', dataSourceName=datasourcename, scanName=scanname, runId=runid)

@scan.command()
@click.option('--classificationRuleName', required=True)
def deleteclassificationrule(classificationrulename):
    """Delete a classification rule"""
    _invoke_scan_method('scanDeleteClassificationRule', classificationRuleName=classificationrulename)

@scan.command()
@click.option('--credentialName', required=True)
def deletecredential(credentialname):
    """Delete a credential"""
    _invoke_scan_method('scanDeleteCredential', credentialName=credentialname)

@scan.command()
@click.option('--dataSourceName', required=True)
def deletedatasource(datasourcename):
    """Delete a data source"""
    _invoke_scan_method('scanDeleteDataSource', dataSourceName=datasourcename)

@scan.command()
@click.option('--keyVaultName', required=True)
def deletekeyvault(keyvaultname):
    """Delete a key vault"""
    _invoke_scan_method('scanDeleteKeyVault', keyVaultName=keyvaultname)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def deletescan(datasourcename, scanname):
    """Delete a scan"""
    _invoke_scan_method('scanDeleteScan', dataSourceName=datasourcename, scanName=scanname)

@scan.command()
@click.option('--scanRulesetName', required=True)
def deletescanruleset(scanrulesetname):
    """Delete a scan ruleset"""
    _invoke_scan_method('scanDeleteScanRuleset', scanRulesetName=scanrulesetname)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def deletetrigger(datasourcename, scanname):
    """Delete a scan trigger"""
    _invoke_scan_method('scanDeleteTrigger', dataSourceName=datasourcename, scanName=scanname)

@scan.command()
@click.option('--classificationRuleName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putclassificationrule(classificationrulename, payloadfile):
    """Create or update a classification rule"""
    _invoke_scan_method('scanPutClassificationRule', classificationRuleName=classificationrulename, payloadFile=payloadfile)

@scan.command()
@click.option('--credentialName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putcredential(credentialname, payloadfile):
    """Create or update a credential"""
    _invoke_scan_method('scanPutCredential', credentialName=credentialname, payloadFile=payloadfile)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putdatasource(datasourcename, payloadfile):
    """Create or update a data source"""
    _invoke_scan_method('scanPutDataSource', dataSourceName=datasourcename, payloadFile=payloadfile)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putfilter(datasourcename, scanname, payloadfile):
    """Create or update a scan filter"""
    _invoke_scan_method('scanPutFilter', dataSourceName=datasourcename, scanName=scanname, payloadFile=payloadfile)

@scan.command()
@click.option('--keyVaultName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putkeyvault(keyvaultname, payloadfile):
    """Create or update a key vault"""
    _invoke_scan_method('scanPutKeyVault', keyVaultName=keyvaultname, payloadFile=payloadfile)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putscan(datasourcename, scanname, payloadfile):
    """Create or update a scan"""
    _invoke_scan_method('scanPutScan', dataSourceName=datasourcename, scanName=scanname, payloadFile=payloadfile)

@scan.command()
@click.option('--scanRulesetName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putscanruleset(scanrulesetname, payloadfile):
    """Create or update a scan ruleset"""
    _invoke_scan_method('scanPutScanRuleset', scanRulesetName=scanrulesetname, payloadFile=payloadfile)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def puttrigger(datasourcename, scanname, payloadfile):
    """Create or update a scan trigger"""
    _invoke_scan_method('scanPutTrigger', dataSourceName=datasourcename, scanName=scanname, payloadFile=payloadfile)

@scan.command()
@click.option('--classificationRuleName', required=True)
def readclassificationrule(classificationrulename):
    """Read a classification rule"""
    _invoke_scan_method('scanReadClassificationRule', classificationRuleName=classificationrulename)

@scan.command()
@click.option('--classificationRuleName', required=True)
def readclassificationruleversions(classificationrulename):
    """Read classification rule versions"""
    _invoke_scan_method('scanReadClassificationRuleVersions', classificationRuleName=classificationrulename)

@scan.command()
def readclassificationrules():
    """Read all classification rules"""
    _invoke_scan_method('scanReadClassificationRules')

@scan.command()
@click.option('--credentialName', required=False)
def readcredential(credentialname):
    """Read a credential or all credentials"""
    _invoke_scan_method('scanReadCredential', credentialName=credentialname)

@scan.command()
@click.option('--dataSourceName', required=True)
def readdatasource(datasourcename):
    """Read a data source"""
    _invoke_scan_method('scanReadDataSource', dataSourceName=datasourcename)

@scan.command()
@click.option('--collectionName', required=False)
def readdatasources(collectionname):
    """Read all data sources or by collection"""
    _invoke_scan_method('scanReadDataSources', collectionName=collectionname)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def readfilters(datasourcename, scanname):
    """Read scan filters"""
    _invoke_scan_method('scanReadFilters', dataSourceName=datasourcename, scanName=scanname)

@scan.command()
@click.option('--keyVaultName', required=True)
def readkeyvault(keyvaultname):
    """Read a key vault"""
    _invoke_scan_method('scanReadKeyVault', keyVaultName=keyvaultname)

@scan.command()
def readkeyvaults():
    """Read all key vaults"""
    _invoke_scan_method('scanReadKeyVaults')

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def readscanhistory(datasourcename, scanname):
    """Read scan history"""
    _invoke_scan_method('scanReadScanHistory', dataSourceName=datasourcename, scanName=scanname)

@scan.command()
@click.option('--scanRulesetName', required=True)
def readscanruleset(scanrulesetname):
    """Read a scan ruleset"""
    _invoke_scan_method('scanReadScanRuleset', scanRulesetName=scanrulesetname)

@scan.command()
def readscanrulesets():
    """Read all scan rulesets"""
    _invoke_scan_method('scanReadScanRulesets')

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def readscan(datasourcename, scanname):
    """Read a scan"""
    _invoke_scan_method('scanReadScan', dataSourceName=datasourcename, scanName=scanname)

@scan.command()
@click.option('--dataSourceName', required=True)
def readscans(datasourcename):
    """Read all scans for a data source"""
    _invoke_scan_method('scanReadScans', dataSourceName=datasourcename)

@scan.command()
@click.option('--dataSourceType', required=True)
def readsystemscanruleset(datasourcetype):
    """Read a system scan ruleset"""
    _invoke_scan_method('scanReadSystemScanRuleset', dataSourceType=datasourcetype)

@scan.command()
@click.option('--dataSourceType', required=True)
def readsystemscanrulesetlatest(datasourcetype):
    """Read latest system scan ruleset"""
    _invoke_scan_method('scanReadSystemScanRulesetLatest', dataSourceType=datasourcetype)

@scan.command()
@click.option('--version', required=True)
@click.option('--dataSourceType', required=True)
def readsystemscanrulesetversion(version, datasourcetype):
    """Read a specific version of a system scan ruleset"""
    _invoke_scan_method('scanReadSystemScanRulesetVersion', version=version, dataSourceType=datasourcetype)

@scan.command()
@click.option('--dataSourceType', required=True)
def readsystemscanrulesetversions(datasourcetype):
    """Read all versions of a system scan ruleset"""
    _invoke_scan_method('scanReadSystemScanRulesetVersions', dataSourceType=datasourcetype)

@scan.command()
def readsystemscanrulesets():
    """Read all system scan rulesets"""
    _invoke_scan_method('scanReadSystemScanRulesets')

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def readtrigger(datasourcename, scanname):
    """Read a scan trigger"""
    _invoke_scan_method('scanReadTrigger', dataSourceName=datasourcename, scanName=scanname)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
@click.option('--scanLevel', required=False, default='Full')
def runscan(datasourcename, scanname, scanlevel):
    """Run a scan"""
    _invoke_scan_method('scanRunScan', dataSourceName=datasourcename, scanName=scanname, scanLevel=scanlevel)

@scan.command()
@click.option('--classificationRuleName', required=True)
@click.option('--classificationRuleVersion', required=True, type=int)
@click.option('--action', required=True)
def tagclassificationversion(classificationrulename, classificationruleversion, action):
    """Tag a classification rule version"""
    _invoke_scan_method('scanTagClassificationVersion', classificationRuleName=classificationrulename, classificationRuleVersion=classificationruleversion, action=action)

@scan.command()
def list():
    """List all scans (TODO: add filtering options)"""
    # TODO: Call Scan().scanReadScans()
    pass

@scan.command()
def read():
    """Read a scan by name"""
    # TODO: Call Scan().scanReadScan()
    pass

@scan.command()
def create():
    """Create a new scan"""
    # TODO: Call Scan().scanPutScan()
    pass

@scan.command()
def update():
    """Update an existing scan"""
    # TODO: Call Scan().scanPutScan()
    pass

@scan.command()
def delete():
    """Delete a scan by name"""
    # TODO: Call Scan().scanDeleteScan()
    pass

@scan.command()
def run():
    """Run a scan"""
    # TODO: Call Scan().scanRunScan()
    pass

@scan.command()
def cancel():
    """Cancel a running scan"""
    # TODO: Call Scan().scanCancelScan()
    pass

# TODO: Add commands for rulesets, triggers, scan history, etc.

__all__ = ['scan']
