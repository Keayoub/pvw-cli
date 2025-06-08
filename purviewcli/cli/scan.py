"""
usage: 
    pvw scan cancelScan --dataSourceName=<val> --scanName=<val> --runId=<val>
    pvw scan deleteClassificationRule --classificationRuleName=<val>
    pvw scan deleteCredential --credentialName=<val>
    pvw scan deleteDataSource --dataSourceName=<val>
    pvw scan deleteKeyVault --keyVaultName=<val>
    pvw scan deleteScan --dataSourceName=<val> --scanName=<val>
    pvw scan deleteScanRuleset --scanRulesetName=<val>
    pvw scan deleteTrigger --dataSourceName=<val> --scanName=<val>
    pvw scan putClassificationRule --classificationRuleName=<val> --payloadFile=<val>
    pvw scan putCredential --credentialName=<val> --payloadFile=<val>
    pvw scan putDataSource --dataSourceName=<val> --payloadFile=<val>
    pvw scan putFilter --dataSourceName=<val> --scanName=<val> --payloadFile=<val>
    pvw scan putKeyVault --keyVaultName=<val> --payloadFile=<val>
    pvw scan putScan --dataSourceName=<val> --scanName=<val> --payloadFile=<val>
    pvw scan putScanRuleset --scanRulesetName=<val> --payloadFile=<val>
    pvw scan putTrigger --dataSourceName=<val> --scanName=<val> --payloadFile=<val>
    pvw scan readClassificationRule --classificationRuleName=<val>
    pvw scan readClassificationRuleVersions --classificationRuleName=<val>
    pvw scan readClassificationRules
    pvw scan readCredential [--credentialName=<val>]
    pvw scan readDataSource --dataSourceName=<val>
    pvw scan readDataSources [--collectionName=<val>]
    pvw scan readFilters --dataSourceName=<val> --scanName=<val>
    pvw scan readKeyVault --keyVaultName=<val>
    pvw scan readKeyVaults
    pvw scan readScan --dataSourceName=<val> --scanName=<val>
    pvw scan readScanHistory --dataSourceName=<val> --scanName=<val>
    pvw scan readScanRuleset --scanRulesetName=<val>
    pvw scan readScanRulesets
    pvw scan readScans --dataSourceName=<val>
    pvw scan readSystemScanRuleset --dataSourceType=<val>
    pvw scan readSystemScanRulesetLatest --dataSourceType=<val>
    pvw scan readSystemScanRulesetVersion --version=<val> --dataSourceType=<val>
    pvw scan readSystemScanRulesetVersions --dataSourceType=<val>
    pvw scan readSystemScanRulesets
    pvw scan readTrigger --dataSourceName=<val> --scanName=<val>
    pvw scan runScan --dataSourceName=<val> --scanName=<val> [--scanLevel=<val>]
    pvw scan tagClassificationVersion --classificationRuleName=<val> --classificationRuleVersion=<val> --action=<val>

options:
    --purviewName=<val>                 [string]  Azure Purview account name.
    --action=<val>                      [string] Allowed values: Delete or Keep.
    --classificationRuleName=<val>      [string]  Name of the classification rule.
    --classificationRuleVersion=<val>   [integer] Version of the classification rule.    
    --dataSourceName=<val>              [string]  Name of the data source.
    --scanName=<val>                    [string]  Name of the scan.
    --scanRulesetName=<val>             [string]  Name of the scan ruleset.
    --keyVaultName=<val>                [string]  Name of the key vault.
    --runId=<val>                       [string]  The unique identifier of the run.
    --dataSourceType=<val>              [string]  Type of data source.
    --scanLevel=<val>                   [string]  Allowed values: Full or Incremental [default: Full].
    --collectionName=<val>              [string]  The unique collection name.
    --credentialName=<val>              [string]  The name of the credential.

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
