from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints
from datetime import datetime, timedelta

class Insight(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'mapanddiscover'

    # Asset
    @decorator
    def insightAssetDistribution(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.INSIGHT['asset_distribution_by_data_source']

    @decorator
    def insightFilesWithoutResourceSet(self, args):
        self.method = 'GET'
        self.endpoint = '/mapanddiscover/reports/serverless/asset2/filesWithoutResourceSet/getSnapshot'

    @decorator
    def insightFilesAggregation(self, args):
        self.method = 'GET'
        self.endpoint = '/mapanddiscover/reports/serverless/asset2/filesAggregation/getSnapshot'

    @decorator
    def insightTags(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.INSIGHT['label_insight']

    @decorator
    def insightTagsTimeSeries(self, args):
        self.method = 'GET'
        self.endpoint = PurviewEndpoints.INSIGHT['tags_time_series']

    # Scan
    @decorator
    def insightScanStatusSummary(self, args):
        self.method = 'GET'
        self.endpoint = '/mapanddiscover/reports/scanstatus2/summaries'
        self.params = { 'window': args['--numberOfDays'] }

    @decorator
    def insightScanStatusSummaryByTs(self, args):
        self.method = 'GET'
        self.endpoint = '/mapanddiscover/reports/scanstatus2/summariesbyts'
        self.params = { 'window': args['--numberOfDays'] }