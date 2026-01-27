"""
Manage scan operations in Microsoft Purview using modular Click-based commands.

Usage:
  scan cancel-scan                      Cancel a scan run
  scan delete-classification-rule       Delete a classification rule
  scan delete-data-source               Delete a data source
  scan delete-scan                      Delete a scan
  scan delete-scan-ruleset              Delete a scan ruleset
  scan put-classification-rule          Create or update a classification rule
  scan put-data-source                  Create or update a data source
  scan put-scan                         Create or update a scan
  scan put-scan-ruleset                 Create or update a scan ruleset
  scan read-classification-rule         Read a classification rule
  scan read-classification-rule-versions Read classification rule versions
  scan read-data-source                 Read a data source
  scan read-data-sources                Read data sources
  scan read-scan                        Read a scan
  scan read-scans                       Read scans
  scan read-scan-history                Read scan history
  scan read-scan-ruleset                Read a scan ruleset
  scan run-scan                         Run a scan
  scan tag-classification-version       Tag a classification version
  scan --help                           Show this help message and exit

Options:
  -h --help                             Show this help message and exit
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

# === SCAN EXECUTION ===

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
@click.option('--runId', required=True)
def cancelscan(datasourcename, scanname, runid):
    """Cancel a running scan"""
    _invoke_scan_method('scanCancel', dataSourceName=datasourcename, scanName=scanname, runId=runid)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
@click.option('--scanLevel', required=False, default='Full')
def runscan(datasourcename, scanname, scanlevel):
    """Run a scan"""
    _invoke_scan_method('scanRun', dataSourceName=datasourcename, scanName=scanname, scanLevel=scanlevel)

# === DATA SOURCE MANAGEMENT ===

@scan.command()
@click.option('--dataSourceName', required=True)
def deletedatasource(datasourcename):
    """Delete a data source"""
    _invoke_scan_method('scanDataSourceDelete', dataSourceName=datasourcename)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putdatasource(datasourcename, payloadfile):
    """Create or update a data source"""
    _invoke_scan_method('scanPutDataSource', dataSourceName=datasourcename, payloadFile=payloadfile)

@scan.command()
@click.option('--dataSourceName', required=True)
def readdatasource(datasourcename):
    """Read a data source"""
    _invoke_scan_method('scanDataSourceRead', dataSourceName=datasourcename)

@scan.command()
@click.option('--collectionName', required=False)
def readdatasources(collectionname):
    """Read all data sources or by collection"""
    _invoke_scan_method('scanDataSourcesRead', collectionName=collectionname)

# === SCAN CONFIGURATION ===

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def deletescan(datasourcename, scanname):
    """Delete a scan"""
    _invoke_scan_method('scanDelete', dataSourceName=datasourcename, scanName=scanname)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putscan(datasourcename, scanname, payloadfile):
    """Create or update a scan"""
    _invoke_scan_method('scanCreate', dataSourceName=datasourcename, scanName=scanname, payloadFile=payloadfile)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def readscan(datasourcename, scanname):
    """Read a scan"""
    _invoke_scan_method('scanRead', dataSourceName=datasourcename, scanName=scanname)

@scan.command()
@click.option('--dataSourceName', required=True)
def readscans(datasourcename):
    """Read all scans for a data source"""
    _invoke_scan_method('scanRead', dataSourceName=datasourcename)

@scan.command()
@click.option('--dataSourceName', required=True)
@click.option('--scanName', required=True)
def readscanhistory(datasourcename, scanname):
    """Read scan history"""
    _invoke_scan_method('scanReadHistory', dataSourceName=datasourcename, scanName=scanname)

# === SCAN RULESETS ===

@scan.command()
@click.option('--scanRulesetName', required=True)
def deletescanruleset(scanrulesetname):
    """Delete a scan ruleset"""
    _invoke_scan_method('scanRuleSetDelete', scanRulesetName=scanrulesetname)

@scan.command()
@click.option('--scanRulesetName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putscanruleset(scanrulesetname, payloadfile):
    """Create or update a scan ruleset"""
    _invoke_scan_method('scanRuleSetCreate', scanRulesetName=scanrulesetname, payloadFile=payloadfile)

@scan.command()
@click.option('--scanRulesetName', required=True)
def readscanruleset(scanrulesetname):
    """Read a scan ruleset"""
    _invoke_scan_method('scanRuleSetRead', scanRulesetName=scanrulesetname)

# === CLASSIFICATION RULES ===

@scan.command()
@click.option('--classificationRuleName', required=True)
def deleteclassificationrule(classificationrulename):
    """Delete a classification rule"""
    _invoke_scan_method('scanClassificationRuleDelete', classificationRuleName=classificationrulename)

@scan.command()
@click.option('--classificationRuleName', required=True)
@click.option('--payloadFile', required=True, type=click.Path(exists=True))
def putclassificationrule(classificationrulename, payloadfile):
    """Create or update a classification rule"""
    _invoke_scan_method('scanClassificationRuleCreate', classificationRuleName=classificationrulename, payloadFile=payloadfile)

@scan.command()
@click.option('--classificationRuleName', required=True)
def readclassificationrule(classificationrulename):
    """Read a classification rule"""
    _invoke_scan_method('scanClassificationRuleRead', classificationRuleName=classificationrulename)

@scan.command()
@click.option('--classificationRuleName', required=True)
def readclassificationruleversions(classificationrulename):
    """Read classification rule versions"""
    _invoke_scan_method('scanClassificationRuleReadVersions', classificationRuleName=classificationrulename)

@scan.command()
@click.option('--classificationRuleName', required=True)
@click.option('--classificationRuleVersion', required=True, type=int)
@click.option('--action', required=True)
def tagclassificationversion(classificationrulename, classificationruleversion, action):
    """Tag a classification rule version"""
    _invoke_scan_method('scanClassificationRuleTagVersion', classificationRuleName=classificationrulename, classificationRuleVersion=classificationruleversion, action=action)

__all__ = ['scan']
