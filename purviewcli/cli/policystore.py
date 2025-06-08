"""
usage: 
    pvw policystore deleteDataPolicy --policyName=<val>
    pvw policystore deleteDataPolicyScope --policyName=<val> --datasource=<val>
    pvw policystore putDataPolicy --policyName=<val> --payloadFile=<val>
    pvw policystore putDataPolicyScope --policyName=<val> --payloadFile=<val>
    pvw policystore putMetadataPolicy --policyId=<val> --payloadFile=<val>
    pvw policystore readDataPolicies [--policyName=<val>]
    pvw policystore readDataPolicyScopes --policyName=<val>
    pvw policystore readMetadataPolicies
    pvw policystore readMetadataPolicy (--collectionName=<val> | --policyId=<val>)
    pvw policystore readMetadataRoles

options:
    --purviewName=<val>           [string]  Azure Purview account name.
    --collectionName=<val>        [string]  The technical name of the Collection (e.g. friendlyName: Sales; name: afwbxs).
    --policyId=<val>              [string]  The unique policy id.
    --payloadFile=<val>           [string]  File path to a valid JSON document.

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
