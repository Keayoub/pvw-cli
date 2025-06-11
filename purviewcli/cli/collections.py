"""
usage: 
    pvw collection create --collectionName=<val> [--friendlyName=<val> --description=<val> --parentCollection=<val> --payloadFile=<val>]
    pvw collection create-or-update --collectionName=<val> [--friendlyName=<val> --description=<val> --parentCollection=<val> --payloadFile=<val>]
    pvw collection delete --collectionName=<val>
    pvw collection export-csv [--output-file=<val> --include-hierarchy --include-metadata]
    pvw collection get --collectionName=<val>
    pvw collection get-child-names --collectionName=<val>
    pvw collection get-path --collectionName=<val>
    pvw collection import --csv-file=<val>
    pvw collection list
    pvw collection update --collectionName=<val> [--friendlyName=<val> --description=<val> --parentCollection=<val> --payloadFile=<val>]

options:
    --purviewName=<val>         [string]  Azure Purview account name.
    --collectionName=<val>      [string]  The unique name of the collection.
    --csv-file=<val>            [string]  File path to a valid CSV file for import operations.
    --description=<val>         [string]  Description of the collection.
    --friendlyName=<val>        [string]  The friendly name of the collection.
    --include-hierarchy         [boolean] Include collection hierarchy in export [default: true].
    --include-metadata          [boolean] Include collection metadata in export [default: true].
    --output-file=<val>         [string]  Output file path for CSV export operations.
    --parentCollection=<val>    [string]  The reference name of the parent collection [default: root].
    --payloadFile=<val>         [string]  File path to a valid JSON document.

"""

from docopt import docopt

if __name__ == "__main__":
    arguments = docopt(__doc__)
