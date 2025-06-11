"""
Enhanced Test Suite for Microsoft Purview Search Client
Tests the new Discovery Query API 2024-03-01-preview capabilities
"""

import os
import unittest
import json
from purviewcli.client import _search

class TestSearch(unittest.TestCase):
    """Test suite for enhanced Purview search functionality"""
    
    PURVIEW_ACCOUNT_NAME = None

    def setUp(self):
        """Set up test fixtures"""
        self.search = _search.Search()
        self.base_args = {
            '--purviewName': self.PURVIEW_ACCOUNT_NAME
        }

    def test_basic_query(self):
        """Test basic search query functionality"""
        args = {
            '--keywords': '*',
            '--limit': 10,
            '--offset': 0,
            '--filterFile': None,
            '--facets-file': None,
            **self.base_args
        }
        data = self.search.searchQuery(args)
        self.assertGreaterEqual(data['@search.count'], 0)

    def test_advanced_query_with_business_metadata(self):
        """Test advanced search with business metadata"""
        business_metadata = {
            "Department": "Finance",
            "Owner": "john.doe@company.com"
        }
        
        args = {
            '--keywords': 'financial',
            '--limit': 20,
            '--businessMetadata': json.dumps(business_metadata),
            '--classifications': 'PII,Confidential',
            **self.base_args
        }
        data = self.search.searchAdvancedQuery(args)
        self.assertIsInstance(data, dict)
        self.assertIn('@search.count', data)

    def test_faceted_search(self):
        """Test faceted search with multiple facet fields"""
        args = {
            '--keywords': 'customer',
            '--facetFields': 'objectType,classification,assetType',
            '--facetCount': 25,
            '--facetSort': 'count',
            '--limit': 50,
            **self.base_args
        }
        data = self.search.searchFaceted(args)
        self.assertIsInstance(data, dict)
        if '@search.facets' in data:
            self.assertIsInstance(data['@search.facets'], dict)

    def test_time_based_search(self):
        """Test time-based search with date range filters"""
        args = {
            '--keywords': 'data',
            '--createdAfter': '2024-01-01T00:00:00Z',
            '--modifiedAfter': '2024-06-01T00:00:00Z',
            '--limit': 30,
            **self.base_args
        }
        data = self.search.searchByTime(args)
        self.assertIsInstance(data, dict)

    def test_entity_type_search(self):
        """Test entity type specific search"""
        args = {
            '--keywords': 'table',
            '--entityTypes': 'Tables,Views',
            '--limit': 25,
            **self.base_args
        }
        data = self.search.searchByEntityType(args)
        self.assertIsInstance(data, dict)

    def test_enhanced_autocomplete(self):
        """Test enhanced autocomplete functionality"""
        args = {
            '--keywords': 'cust',
            '--limit': 10,
            '--objectType': 'Tables',
            **self.base_args
        }
        data = self.search.searchAutoComplete(args)
        self.assertIsInstance(data, dict)

    def test_enhanced_suggestions(self):
        """Test enhanced search suggestions"""
        args = {
            '--keywords': 'customer dat',
            '--limit': 10,
            '--fuzzy': True,
            **self.base_args
        }
        data = self.search.searchSuggest(args)
        self.assertIsInstance(data, dict)

    def test_enhanced_browse(self):
        """Test enhanced browse functionality"""
        args = {
            '--entityType': 'DataSet',
            '--path': '/subscriptions',
            '--limit': 20,
            '--offset': 0,
            '--includeSubPaths': True,
            **self.base_args
        }
        data = self.search.searchBrowse(args)
        self.assertIsInstance(data, dict)

    def test_filter_builder(self):
        """Test the SearchFilterBuilder functionality"""
        filter_builder = self.search.create_filter_builder()
        
        # Build complex filter
        filter_obj = (filter_builder
                     .add_and_filter('objectType', 'Tables')
                     .add_and_filter('classification', ['PII', 'Confidential'])
                     .add_or_filter('assetType', 'Azure SQL Database')
                     .build())
        
        self.assertIsInstance(filter_obj, dict)
        self.assertIn('and', filter_obj)

    def test_search_parameter_validation(self):
        """Test search parameter validation"""
        args = {
            '--objectTypes': 'Tables,InvalidType',
            '--limit': 1500,  # Over recommended limit
            '--keywords': 'x' * 600,  # Too long
            **self.base_args
        }
        
        warnings = self.search.validate_search_parameters(args)
        self.assertGreater(len(warnings), 0)
        self.assertTrue(any('InvalidType' in warning for warning in warnings))
        self.assertTrue(any('1000' in warning for warning in warnings))
        self.assertTrue(any('500' in warning for warning in warnings))

    def test_supported_object_types(self):
        """Test getting supported object types"""
        object_types = self.search.get_supported_object_types()
        self.assertIsInstance(object_types, list)
        self.assertIn('Tables', object_types)
        self.assertIn('Files', object_types)
        self.assertIn('Dashboards', object_types)

    def test_common_filter_fields(self):
        """Test getting common filter fields"""
        filter_fields = self.search.get_common_filter_fields()
        self.assertIsInstance(filter_fields, list)
        self.assertIn('objectType', filter_fields)
        self.assertIn('classification', filter_fields)
        self.assertIn('term', filter_fields)


class TestSearchFilterBuilder(unittest.TestCase):
    """Test suite for SearchFilterBuilder class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.builder = _search.SearchFilterBuilder()

    def test_single_and_filter(self):
        """Test adding a single AND filter"""
        filter_obj = self.builder.add_and_filter('objectType', 'Tables').build()
        
        expected = {
            'field': 'objectType',
            'operator': 'eq',
            'value': 'Tables'
        }
        self.assertEqual(filter_obj, expected)

    def test_multiple_and_filters(self):
        """Test adding multiple AND filters"""
        filter_obj = (self.builder
                     .add_and_filter('objectType', 'Tables')
                     .add_and_filter('classification', 'PII')
                     .build())
        
        self.assertIn('and', filter_obj)

    def test_or_filter(self):
        """Test adding OR filters"""
        filter_obj = (self.builder
                     .add_and_filter('objectType', 'Tables')
                     .add_or_filter('objectType', 'Views')
                     .build())
        
        self.assertIn('or', filter_obj)

    def test_not_filter(self):
        """Test adding NOT filters"""
        filter_obj = self.builder.add_not_filter('classification', 'Internal').build()
        
        self.assertIn('not', filter_obj)

    def test_list_value_filter(self):
        """Test filter with list values"""
        filter_obj = self.builder.add_and_filter('classification', ['PII', 'Confidential']).build()
        
        self.assertEqual(filter_obj['operator'], 'in')
        self.assertEqual(filter_obj['value'], ['PII', 'Confidential'])

    def test_empty_builder(self):
        """Test empty filter builder"""
        filter_obj = self.builder.build()
        self.assertIsNone(filter_obj)


if __name__ == "__main__":
    TestSearch.PURVIEW_ACCOUNT_NAME = os.environ.get('PURVIEW_ACCOUNT_NAME')
    unittest.main()