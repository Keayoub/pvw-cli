"""
usage: 
    pvw entity addLabels --guid=<val> --payloadFile=<val>
    pvw entity addLabelsByUniqueAttribute --typeName=<val> --qualifiedName=<val> --payloadFile=<val>
    pvw entity addOrUpdateBusinessAttribute --guid=<val> --bmName=<val> --payloadFile=<val>
    pvw entity addOrUpdateBusinessMetadata --guid=<val> --payloadFile=<val> [--isOverwrite]
    pvw entity changeCollection --collection=<val> --payloadFile=<val>
    pvw entity create --payloadFile=<val>
    pvw entity createBulk --payloadFile=<val>
    pvw entity createBulkClassification --payloadFile=<val>
    pvw entity createBulkSetClassifications --payloadFile=<val>
    pvw entity createClassifications --guid=<val> --payloadFile=<val>
    pvw entity createOrUpdateCollection --collection=<val> --payloadFile=<val>
    pvw entity createOrUpdateCollectionBulk --collection=<val> --payloadFile=<val>
    pvw entity createUniqueAttributeClassifications --typeName=<val> --qualifiedName=<val> --payloadFile=<val>
    pvw entity delete --guid=<val>
    pvw entity deleteBulk --guid=<val>...
    pvw entity deleteBusinessAttribute --guid=<val> --bmName=<val> --payloadFile=<val>
    pvw entity deleteBusinessMetadata --guid=<val> --payloadFile=<val>
    pvw entity deleteClassification --guid=<val> --classificationName=<val>
    pvw entity deleteLabels --guid=<val> --payloadFile=<val>
    pvw entity deleteLabelsByUniqueAttribute --typeName=<val> --qualifiedName=<val> --payloadFile=<val>
    pvw entity deleteUniqueAttribute --typeName=<val> --qualifiedName=<val>
    pvw entity deleteUniqueAttributeClassification --typeName=<val> --qualifiedName=<val> --classificationName=<val>
    pvw entity getBusinessMetadataTemplate
    pvw entity importBusinessMetadata --bmFile=<val>
    pvw entity put --guid=<val> --attrName=<val> --attrValue=<val>
    pvw entity putClassifications --guid=<val> --payloadFile=<val>
    pvw entity putUniqueAttribute --typeName=<val> --qualifiedName=<val> --payloadFile=<val>
    pvw entity putUniqueAttributeClassifications --typeName=<val> --qualifiedName=<val> --payloadFile=<val>
    pvw entity read --guid=<val> [--ignoreRelationships --minExtInfo]
    pvw entity readBulk --guid=<val>... [--ignoreRelationships --minExtInfo]
    pvw entity readBulkUniqueAttribute --typeName=<val> --qualifiedName=<val>... [--ignoreRelationships --minExtInfo]
    pvw entity readClassification --guid=<val> --classificationName=<val>
    pvw entity readClassifications --guid=<val>
    pvw entity readHeader --guid=<val>
    pvw entity readUniqueAttribute --typeName=<val> --qualifiedName=<val> [--ignoreRelationships --minExtInfo]
    pvw entity setLabels --guid=<val> --payloadFile=<val>
    pvw entity setLabelsByUniqueAttribute --typeName=<val> --qualifiedName=<val> --payloadFile=<val>
    
options:
    --purviewName=<val>                 [string]  Azure Purview account name.
    --bmFile=<val>                      [string]  File path to a valid business metadata template CSV file.
    --bmName=<val>                      [string]  BusinessMetadata name.
    --classificationName=<val>          [string]  The name of the classification.
    --collection=<val>                  [string]  The collection unique name.
    --guid=<val>                        [string]  The globally unique identifier of the entity.
    --ignoreRelationships               [boolean] Whether to ignore relationship attributes [default: false].
    --isOverwrite                       [boolean] Whether to overwrite the existing business metadata on the entity or not [default: false].
    --minExtInfo                        [boolean] Whether to return minimal information for referred entities [default: false].
    --name=<val>                        [string]  The name of the attribute.
    --payloadFile=<val>                 [string]  File path to a valid JSON document.
    --qualifiedName=<val>               [string]  The qualified name of the entity.
    --typeName=<val>                    [string]  The name of the type.

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
