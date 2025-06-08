"""
usage: 
    pvw types createTypeDefs --payloadFile=<val>
    pvw types deleteTypeDef --name=<val>
    pvw types deleteTypeDefs --payloadFile=<val>
    pvw types putTypeDefs --payloadFile=<val>
    pvw types readClassificationDef (--guid=<val> | --name=<val>)
    pvw types readEntityDef (--guid=<val> | --name=<val>)
    pvw types readEnumDef (--guid=<val> | --name=<val>)
    pvw types readRelationshipDef (--guid=<val> | --name=<val>)
    pvw types readStatistics
    pvw types readStructDef (--guid=<val> | --name=<val>)
    pvw types readBusinessMetadataDef (--guid=<val> | --name=<val>)
    pvw types readTermTemplateDef (--guid=<val> | --name=<val>)
    pvw types readTypeDef (--guid=<val> | --name=<val>)
    pvw types readTypeDefs [--includeTermTemplate --type=<val>]
    pvw types readTypeDefsHeaders [--includeTermTemplate --type=<val>]

options:
  --purviewName=<val>     [string]  Azure Purview account name.
  --guid=<val>            [string]  The globally unique identifier.
  --includeTermTemplate   [boolean] Whether to include termtemplatedef [default: false].
  --name=<val>            [string]  The name of the definition.
  --payloadFile=<val>     [string]  File path to a valid JSON document.
  --type=<val>            [string]  Typedef name as search filter (classification | entity | enum | relationship | struct).

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
