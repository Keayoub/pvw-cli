"""
usage: 
    pvw insight assetDistribution
    pvw insight filesAggregation
    pvw insight filesWithoutResourceSet
    pvw insight scanStatusSummary [--numberOfDays=<val>]
    pvw insight scanStatusSummaryByTs [--numberOfDays=<val>]
    pvw insight tags
    pvw insight tagsTimeSeries

options:
    --purviewName=<val>          [string]  Azure Purview account name.
    --numberOfDays=<val>         [integer] Trailing time period in days [default: 30].

"""
from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
