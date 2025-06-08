"""
usage: 
    pvw relationship create --payloadFile=<val>
    pvw relationship delete --guid=<val>
    pvw relationship put --payloadFile=<val>
    pvw relationship read --guid=<val> [--extendedInfo]

options:
    --purviewName=<val>           [string]  Azure Purview account name.
    --extendedInfo                [boolean] Limits whether includes extended information [default: false].
    --guid=<val>                  [string]  The globally unique identifier of the relationship.
    --payloadFile=<val>           [string]  File path to a valid JSON document.

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
