"""
Microsoft Purview Discovery Query API Client
Enhanced search capabilities based on the official 2024-03-01-preview API
Supports advanced filtering, faceting, business metadata search, and more
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any
from .endpoint import Endpoint, decorator, get_json
from .endpoints import PurviewEndpoints

# Configure logging for search operations
logger = logging.getLogger(__name__)


class SearchFilterBuilder:
    """
    Helper class to build complex search filters using AND/OR/NOT operations
    Based on Microsoft Purview Discovery Query API specifications
    """

    def __init__(self):
        self.filters = []

    def add_and_filter(
        self, field: str, value: Union[str, List[str]], operator: str = "eq"
    ) -> "SearchFilterBuilder":
        """Add an AND condition to the filter"""
        filter_condition = self._build_condition(field, value, operator)
        if self.filters:
            self.filters.append(
                {"and": [{"condition": self.filters[-1]}, {"condition": filter_condition}]}
            )
        else:
            self.filters.append(filter_condition)
        return self

    def add_or_filter(
        self, field: str, value: Union[str, List[str]], operator: str = "eq"
    ) -> "SearchFilterBuilder":
        """Add an OR condition to the filter"""
        filter_condition = self._build_condition(field, value, operator)
        if self.filters:
            self.filters.append(
                {"or": [{"condition": self.filters[-1]}, {"condition": filter_condition}]}
            )
        else:
            self.filters.append(filter_condition)
        return self

    def add_not_filter(
        self, field: str, value: Union[str, List[str]], operator: str = "eq"
    ) -> "SearchFilterBuilder":
        """Add a NOT condition to the filter"""
        filter_condition = self._build_condition(field, value, operator)
        self.filters.append({"not": {"condition": filter_condition}})
        return self

    def _build_condition(self, field: str, value: Union[str, List[str]], operator: str) -> Dict:
        """Build a filter condition"""
        if isinstance(value, list):
            return {"field": field, "operator": "in", "value": value}
        else:
            return {"field": field, "operator": operator, "value": value}

    def build(self) -> Optional[Dict]:
        """Build the final filter object"""
        if not self.filters:
            return None
        return (
            self.filters[-1]
            if len(self.filters) == 1
            else {"and": [{"condition": f} for f in self.filters]}
        )


class Search(Endpoint):
    """
    Enhanced Microsoft Purview Search Client
    Implements the full Discovery Query API 2024-03-01-preview capabilities
    """

    def __init__(self):
        Endpoint.__init__(self)
        self.app = "catalog"

        # Object types supported by Purview Discovery Query API
        self.supported_object_types = [
            "Tables",
            "Files",
            "Views",
            "Dashboards",
            "Reports",
            "KPIs",
            "DataSets",
            "DataFlows",
            "DataSources",
            "Glossaries",
            "GlossaryTerms",
            "Classifications",
        ]

        # Common filter fields for search operations
        self.common_filter_fields = [
            "objectType",
            "classification",
            "term",
            "contactId",
            "assetType",
            "replicatedTo",
            "replicatedFrom",
            "label",
        ]

    @decorator
    def searchQuery(self, args):
        """
        Enhanced search query with full Discovery Query API support
        Supports advanced filtering, faceting, sorting, and business metadata search
        """
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["query"]
        self.params = PurviewEndpoints.get_api_version_params("search")

        # Build comprehensive search payload
        self.payload = self._build_search_payload(args)

        logger.info(
            f"Executing advanced search query with keywords: {args.get('--keywords', 'N/A')}"
        )

    @decorator
    def searchAdvancedQuery(self, args):
        """
        Advanced search with business metadata and complex filtering
        Specialized method for complex enterprise search scenarios
        """
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["query"]
        self.params = PurviewEndpoints.get_api_version_params("search")

        payload = self._build_search_payload(args)

        # Add business metadata search support
        if args.get("--businessMetadata"):
            business_metadata = get_json(args, "--businessMetadata")
            if business_metadata:
                payload["businessMetadata"] = business_metadata

        # Add advanced classification filters
        if args.get("--classifications"):
            classifications = (
                args["--classifications"].split(",")
                if isinstance(args["--classifications"], str)
                else args["--classifications"]
            )
            payload["classification"] = classifications

        # Add term assignment filters
        if args.get("--termAssignments"):
            payload["termAssignment"] = args["--termAssignments"]

        self.payload = payload
        logger.info("Executing advanced business metadata search")

    @decorator
    def searchFaceted(self, args):
        """
        Faceted search with aggregation support
        Returns search results with facet counts for filtering
        """
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["query"]
        self.params = PurviewEndpoints.get_api_version_params("search")

        payload = self._build_search_payload(args)

        # Enhanced facet configuration
        facets = []
        if args.get("--facetFields"):
            facet_fields = (
                args["--facetFields"].split(",")
                if isinstance(args["--facetFields"], str)
                else args["--facetFields"]
            )
            for field in facet_fields:
                facets.append(
                    {
                        "field": field.strip(),
                        "count": args.get("--facetCount", 50),
                        "sort": args.get("--facetSort", "count"),
                    }
                )
        else:
            # Default facets for comprehensive search
            default_facets = ["objectType", "classification", "term", "assetType", "contactId"]
            for field in default_facets:
                facets.append({"field": field, "count": 20, "sort": "count"})

        payload["facets"] = facets
        self.payload = payload
        logger.info(f"Executing faceted search with {len(facets)} facet fields")

    @decorator
    def searchByTime(self, args):
        """
        Time-based search with date range filtering
        Search for assets modified or created within specific time ranges
        """
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["query"]
        self.params = PurviewEndpoints.get_api_version_params("search")

        payload = self._build_search_payload(args)

        # Add time-based filters
        time_filters = []
        if args.get("--createdAfter"):
            time_filters.append(
                {"field": "createTime", "operator": "gte", "value": args["--createdAfter"]}
            )

        if args.get("--createdBefore"):
            time_filters.append(
                {"field": "createTime", "operator": "lte", "value": args["--createdBefore"]}
            )

        if args.get("--modifiedAfter"):
            time_filters.append(
                {"field": "updateTime", "operator": "gte", "value": args["--modifiedAfter"]}
            )

        if args.get("--modifiedBefore"):
            time_filters.append(
                {"field": "updateTime", "operator": "lte", "value": args["--modifiedBefore"]}
            )

        if time_filters:
            existing_filter = payload.get("filter")
            if existing_filter:
                payload["filter"] = {
                    "and": [
                        {"condition": existing_filter},
                        {"and": [{"condition": f} for f in time_filters]},
                    ]
                }
            else:
                payload["filter"] = {"and": [{"condition": f} for f in time_filters]}

        self.payload = payload
        logger.info("Executing time-based search with date range filters")

    @decorator
    def searchByEntityType(self, args):
        """
        Entity type specific search with enhanced type filtering
        Search for specific types of assets with type-specific parameters
        """
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["query"]
        self.params = PurviewEndpoints.get_api_version_params("search")

        payload = self._build_search_payload(args)

        # Enhanced entity type filtering
        if args.get("--entityTypes"):
            entity_types = (
                args["--entityTypes"].split(",")
                if isinstance(args["--entityTypes"], str)
                else args["--entityTypes"]
            )
            payload["objectType"] = entity_types

        # Add type-specific attributes
        if args.get("--typeAttributes"):
            type_attributes = get_json(args, "--typeAttributes")
            if type_attributes:
                payload["typeAttributes"] = type_attributes

        self.payload = payload
        logger.info(f"Executing entity type search for types: {args.get('--entityTypes', 'All')}")

    @decorator
    def searchAutoComplete(self, args):
        """
        Enhanced autocomplete with intelligent suggestions
        Supports partial matching and contextual suggestions
        """
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["autocomplete"]
        self.params = PurviewEndpoints.get_api_version_params("search")

        self.payload = {
            "keywords": args.get("--keywords", ""),
            "limit": args.get("--limit", 10),
            "filter": get_json(args, "--filterFile") or self._build_simple_filter(args),
        }

        logger.info(f"Executing autocomplete for: {args.get('--keywords', '')}")

    @decorator
    def searchSuggest(self, args):
        """
        Enhanced search suggestions with fuzzy matching
        Provides intelligent search suggestions based on catalog content
        """
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["suggest"]
        self.params = PurviewEndpoints.get_api_version_params("search")

        self.payload = {
            "keywords": args.get("--keywords", ""),
            "limit": args.get("--limit", 10),
            "filter": get_json(args, "--filterFile") or self._build_simple_filter(args),
            "fuzzy": args.get("--fuzzy", True),
        }

        logger.info(f"Executing search suggestions for: {args.get('--keywords', '')}")

    @decorator
    def searchBrowse(self, args):
        """
        Enhanced browse functionality with hierarchical navigation
        Supports collection-based browsing and path navigation
        """
        self.method = "POST"
        self.endpoint = PurviewEndpoints.SEARCH["browse"]
        self.params = PurviewEndpoints.get_api_version_params("search")

        self.payload = {
            "entityType": args.get("--entityType"),
            "path": args.get("--path", ""),
            "limit": args.get("--limit", 50),
            "offset": args.get("--offset", 0),
        }

        # Add collection context if specified
        if args.get("--collection"):
            self.payload["collection"] = args["--collection"]

        # Add hierarchical browsing support
        if args.get("--includeSubPaths"):
            self.payload["includeSubPaths"] = args["--includeSubPaths"]

        logger.info(f"Executing browse for entity type: {args.get('--entityType', 'All')}")

    def _build_search_payload(self, args: Dict) -> Dict[str, Any]:
        """
        Build comprehensive search payload with all supported parameters
        Centralizes payload construction for consistency
        """
        payload = {}

        # Basic search parameters
        if args.get("--keywords"):
            payload["keywords"] = args["--keywords"]

        # Pagination
        payload["limit"] = args.get("--limit", 50)
        payload["offset"] = args.get("--offset", 0)

        # Continuation token for large result sets
        if args.get("--continuationToken"):
            payload["continuationToken"] = args["--continuationToken"]

        # Filters - support both file-based and programmatic filters
        filter_obj = get_json(args, "--filterFile")
        if not filter_obj:
            filter_obj = self._build_simple_filter(args)
        if filter_obj:
            payload["filter"] = filter_obj

        # Facets
        facets = get_json(args, "--facets-file")
        if facets:
            payload["facets"] = facets

        # Sorting
        if args.get("--orderBy"):
            payload["orderBy"] = [
                {"field": args["--orderBy"], "direction": args.get("--sortDirection", "asc")}
            ]

        # Object types
        if args.get("--objectTypes"):
            object_types = (
                args["--objectTypes"].split(",")
                if isinstance(args["--objectTypes"], str)
                else args["--objectTypes"]
            )
            payload["objectType"] = object_types

        # Collection scope
        if args.get("--collection"):
            payload["collection"] = args["--collection"]

        # Include facet results
        payload["includeFacets"] = args.get("--includeFacets", True)

        return payload

    def _build_simple_filter(self, args: Dict) -> Optional[Dict]:
        """
        Build simple filters from command line arguments
        Provides a programmatic way to create basic filters
        """
        filter_builder = SearchFilterBuilder()
        has_filters = False

        # Object type filter
        if args.get("--objectType"):
            filter_builder.add_and_filter("objectType", args["--objectType"])
            has_filters = True

        # Classification filter
        if args.get("--classification"):
            classifications = (
                args["--classification"].split(",")
                if isinstance(args["--classification"], str)
                else [args["--classification"]]
            )
            filter_builder.add_and_filter("classification", classifications)
            has_filters = True

        # Term filter
        if args.get("--term"):
            filter_builder.add_and_filter("term", args["--term"])
            has_filters = True

        # Asset type filter
        if args.get("--assetType"):
            filter_builder.add_and_filter("assetType", args["--assetType"])
            has_filters = True

        # Contact filter
        if args.get("--contactId"):
            filter_builder.add_and_filter("contactId", args["--contactId"])
            has_filters = True

        return filter_builder.build() if has_filters else None

    def create_filter_builder(self) -> SearchFilterBuilder:
        """
        Factory method to create a new filter builder
        Allows for programmatic filter construction
        """
        return SearchFilterBuilder()

    def get_supported_object_types(self) -> List[str]:
        """Return list of supported object types for search"""
        return self.supported_object_types.copy()

    def get_common_filter_fields(self) -> List[str]:
        """Return list of common filter fields"""
        return self.common_filter_fields.copy()

    def validate_search_parameters(self, args: Dict) -> List[str]:
        """
        Validate search parameters and return list of warnings/errors
        Helps ensure proper API usage
        """
        warnings = []

        # Check object types
        if args.get("--objectTypes"):
            object_types = (
                args["--objectTypes"].split(",")
                if isinstance(args["--objectTypes"], str)
                else args["--objectTypes"]
            )
            for obj_type in object_types:
                if obj_type not in self.supported_object_types:
                    warnings.append(f"Unsupported object type: {obj_type}")

        # Check pagination limits
        limit = args.get("--limit", 0)
        if limit > 1000:
            warnings.append("Limit should not exceed 1000 for optimal performance")

        # Check keyword length
        keywords = args.get("--keywords", "")
        if len(keywords) > 500:
            warnings.append("Keywords should be under 500 characters for best results")

        return warnings
