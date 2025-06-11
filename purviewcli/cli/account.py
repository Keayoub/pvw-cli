"""
usage: 
    pvw account deleteCollection --collectionName=<val>
    pvw account deleteResourceSetRule
    pvw account getAccessKeys
    pvw account getAccount
    pvw account getChildCollectionNames --collectionName=<val>
    pvw account getCollection --collectionName=<val>
    pvw account getCollectionPath --collectionName=<val>
    pvw account getCollections
    pvw account getResourceSetRule
    pvw account getResourceSetRules
    pvw account putCollection --friendlyName=<val> --parentCollection=<val>
    pvw account putResourceSetRule --payloadFile=<val>
    pvw account regenerateAccessKeys --keyType=<val>
    pvw account updateAccount --friendlyName=<val>

options:
    --purviewName=<val>           [string] Azure Purview account name.
    --collectionName=<val>        [string] The technical name of the collection.
    --keyType=<val>               [string] The access key type.
    --friendlyName=<val>          [string] The friendly name for the azure resource.
    --parentCollection=<val>      [string] Gets or sets the parent collection reference.
    --payloadFile=<val>           [string] File path to a valid JSON document.

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
