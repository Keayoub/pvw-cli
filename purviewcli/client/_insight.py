"""
Microsoft Purview Insight Client - Complete API Coverage
Handles Analytics, Reports, Asset Distribution, and Business Intelligence operations
"""

from .endpoint import Endpoint, decorator, get_json
from .endpoints import ENDPOINTS, format_endpoint, get_api_version_params
from datetime import datetime, timedelta

class Insight(Endpoint):
    def __init__(self):
        Endpoint.__init__(self)
        self.app = 'mapanddiscover'

    # ========== Asset Distribution and Analytics ==========
    
    @decorator
    def insightAssetDistribution(self, args):
        """Get asset distribution by data source"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['asset_distribution_by_data_source']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightAssetDistributionByType(self, args):
        """Get asset distribution by asset type"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['asset_distribution_by_type']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightAssetDistributionByClassification(self, args):
        """Get asset distribution by classification"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['asset_distribution_by_classification']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightAssetDistributionByCollection(self, args):
        """Get asset distribution by collection"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['asset_distribution_by_collection']
        self.params = get_api_version_params('datamap')

    # ========== File and Resource Set Analytics ==========
    
    @decorator
    def insightFilesWithoutResourceSet(self, args):
        """Get files without resource set grouping"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['files_without_resource_set']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightFilesAggregation(self, args):
        """Get files aggregation statistics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['files_aggregation']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightResourceSetDetails(self, args):
        """Get detailed resource set analytics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['resource_set_details']
        self.params = get_api_version_params('datamap')
        if args.get('--resourceSetName'):
            self.params['resourceSetName'] = args['--resourceSetName']

    @decorator
    def insightResourceSetSummary(self, args):
        """Get resource set summary statistics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['resource_set_summary']
        self.params = get_api_version_params('datamap')

    # ========== Tag and Label Analytics ==========
    
    @decorator
    def insightTags(self, args):
        """Get tag insights and distribution"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['label_insight']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightTagsTimeSeries(self, args):
        """Get tags time series analysis"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['tags_time_series']
        self.params = get_api_version_params('datamap')
        if args.get('--window'):
            self.params['window'] = args['--window']

    @decorator
    def insightClassificationDistribution(self, args):
        """Get classification distribution across assets"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['classification_distribution']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightSensitivityLabels(self, args):
        """Get sensitivity label insights"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['sensitivity_labels']
        self.params = get_api_version_params('datamap')

    # ========== Scan Status and Performance ==========
    
    @decorator
    def insightScanStatusSummary(self, args):
        """Get scan status summary"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['scan_status_summary']
        self.params = get_api_version_params('datamap')
        if args.get('--numberOfDays'):
            self.params['window'] = args['--numberOfDays']

    @decorator
    def insightScanStatusSummaryByTs(self, args):
        """Get scan status summary by timestamp"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['scan_status_summary_by_ts']
        self.params = get_api_version_params('datamap')
        if args.get('--numberOfDays'):
            self.params['window'] = args['--numberOfDays']

    @decorator
    def insightScanPerformance(self, args):
        """Get scan performance metrics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['scan_performance']
        self.params = get_api_version_params('datamap')
        if args.get('--scanName'):
            self.params['scanName'] = args['--scanName']

    @decorator
    def insightScanHistory(self, args):
        """Get scan history and trends"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['scan_history']
        self.params = get_api_version_params('datamap')
        if args.get('--startTime'):
            self.params['startTime'] = args['--startTime']
        if args.get('--endTime'):
            self.params['endTime'] = args['--endTime']

    # ========== Data Quality Insights ==========
    
    @decorator
    def insightDataQualityOverview(self, args):
        """Get data quality overview"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['data_quality_overview']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightDataQualityBySource(self, args):
        """Get data quality metrics by data source"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['data_quality_by_source']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightDataQualityTrends(self, args):
        """Get data quality trends over time"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['data_quality_trends']
        self.params = get_api_version_params('datamap')
        if args.get('--timeRange'):
            self.params['timeRange'] = args['--timeRange']

    @decorator
    def insightDataProfileSummary(self, args):
        """Get data profiling summary"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['data_profile_summary']
        self.params = get_api_version_params('datamap')

    # ========== Glossary and Business Analytics ==========
    
    @decorator
    def insightGlossaryUsage(self, args):
        """Get glossary term usage statistics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['glossary_usage']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightBusinessGlossaryHealth(self, args):
        """Get business glossary health metrics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['business_glossary_health']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightTermAssignmentCoverage(self, args):
        """Get term assignment coverage across assets"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['term_assignment_coverage']
        self.params = get_api_version_params('datamap')

    # ========== Lineage Analytics ==========
    
    @decorator
    def insightLineageCoverage(self, args):
        """Get lineage coverage statistics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['lineage_coverage']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightLineageComplexity(self, args):
        """Get lineage complexity metrics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['lineage_complexity']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightDataMovementPatterns(self, args):
        """Get data movement patterns analysis"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['data_movement_patterns']
        self.params = get_api_version_params('datamap')

    # ========== User Activity and Engagement ==========
    
    @decorator
    def insightUserActivity(self, args):
        """Get user activity insights"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['user_activity']
        self.params = get_api_version_params('datamap')
        if args.get('--timeRange'):
            self.params['timeRange'] = args['--timeRange']

    @decorator
    def insightSearchPatterns(self, args):
        """Get search patterns and popular queries"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['search_patterns']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightAssetPopularity(self, args):
        """Get asset popularity metrics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['asset_popularity']
        self.params = get_api_version_params('datamap')

    # ========== Collection and Access Analytics ==========
    
    @decorator
    def insightCollectionActivity(self, args):
        """Get collection activity insights"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['collection_activity']
        self.params = get_api_version_params('datamap')
        if args.get('--collectionName'):
            self.params['collectionName'] = args['--collectionName']

    @decorator
    def insightAccessPatterns(self, args):
        """Get data access patterns"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['access_patterns']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightPermissionUsage(self, args):
        """Get permission usage analytics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['permission_usage']
        self.params = get_api_version_params('datamap')

    # ========== Custom Analytics and Reporting ==========
    
    @decorator
    def insightCustomReport(self, args):
        """Generate custom insight report"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['insight']['custom_report']
        self.params = get_api_version_params('datamap')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def insightScheduledReports(self, args):
        """Get scheduled reports list"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['scheduled_reports']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightCreateScheduledReport(self, args):
        """Create a scheduled report"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['insight']['create_scheduled_report']
        self.params = get_api_version_params('datamap')
        self.payload = get_json(args, '--payloadFile')

    @decorator
    def insightExportData(self, args):
        """Export insight data to various formats"""
        self.method = 'POST'
        self.endpoint = ENDPOINTS['insight']['export_data']
        self.params = get_api_version_params('datamap')
        self.payload = {
            'reportType': args.get('--reportType'),
            'format': args.get('--format', 'csv'),
            'filters': get_json(args, '--filtersFile') if args.get('--filtersFile') else {}
        }

    # ========== Advanced Analytics ==========
    
    @decorator
    def insightDataGrowthTrends(self, args):
        """Get data growth trends analysis"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['data_growth_trends']
        self.params = get_api_version_params('datamap')
        if args.get('--timeRange'):
            self.params['timeRange'] = args['--timeRange']

    @decorator
    def insightComplianceMetrics(self, args):
        """Get compliance metrics and scores"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['compliance_metrics']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightDataStewardshipHealth(self, args):
        """Get data stewardship health metrics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['data_stewardship_health']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightAssetHealthScore(self, args):
        """Get asset health scores"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['asset_health_score']
        self.params = get_api_version_params('datamap')
        if args.get('--assetType'):
            self.params['assetType'] = args['--assetType']

    # ========== Performance and Optimization ==========
    
    @decorator
    def insightSystemPerformance(self, args):
        """Get system performance metrics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['system_performance']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightResourceUtilization(self, args):
        """Get resource utilization statistics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['resource_utilization']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightOptimizationRecommendations(self, args):
        """Get optimization recommendations"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['optimization_recommendations']
        self.params = get_api_version_params('datamap')

    # ========== Real-time Analytics ==========
    
    @decorator
    def insightRealTimeMetrics(self, args):
        """Get real-time system metrics"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['real_time_metrics']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightLiveActivityFeed(self, args):
        """Get live activity feed"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['live_activity_feed']
        self.params = get_api_version_params('datamap')
        if args.get('--limit'):
            self.params['limit'] = args['--limit']

    @decorator
    def insightActiveScans(self, args):
        """Get currently active scans"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['active_scans']
        self.params = get_api_version_params('datamap')

    # ========== Historical Analysis ==========
    
    @decorator
    def insightHistoricalTrends(self, args):
        """Get historical trends analysis"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['historical_trends']
        self.params = get_api_version_params('datamap')
        if args.get('--startDate'):
            self.params['startDate'] = args['--startDate']
        if args.get('--endDate'):
            self.params['endDate'] = args['--endDate']
        if args.get('--granularity'):
            self.params['granularity'] = args['--granularity']

    @decorator
    def insightDataArchival(self, args):
        """Get data archival insights"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['data_archival']
        self.params = get_api_version_params('datamap')

    @decorator
    def insightVersionHistory(self, args):
        """Get version history analysis"""
        self.method = 'GET'
        self.endpoint = ENDPOINTS['insight']['version_history']
        self.params = get_api_version_params('datamap')
        if args.get('--assetId'):
            self.params['assetId'] = args['--assetId']
