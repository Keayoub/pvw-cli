# Microsoft Purview Advanced Search Guide

This guide demonstrates the enhanced search capabilities available in the Purview CLI, based on the Microsoft Purview Discovery Query API 2024-03-01-preview.

## Overview

The enhanced search functionality provides powerful capabilities for discovering and exploring your data catalog, including:

- **Advanced Filtering**: Complex AND/OR/NOT filter combinations
- **Faceted Search**: Explore data through categorical facets
- **Business Metadata Search**: Search based on custom business attributes
- **Time-based Search**: Filter by creation/modification dates
- **Entity Type Search**: Type-specific searches with attributes
- **Classification Search**: Find assets by data classifications
- **Fuzzy Search**: Intelligent suggestions with partial matching

## Command Categories

### 1. Basic Search Commands

#### Query Search

Standard keyword search with optional filters and facets.

```bash
# Basic keyword search
pvw search query --keywords "customer data" --limit 50

# Search with object type filter
pvw search query --keywords "financial" --objectTypes "Tables,Views" --limit 25

# Search with collection scope
pvw search query --keywords "sales" --collection "finance-data" --includeFacets

# Search with sorting
pvw search query --keywords "transactions" --orderBy "name" --sortDirection "desc"
```

#### AutoComplete

Get intelligent autocompletion suggestions.

```bash
# Basic autocomplete
pvw search autoComplete --keywords "cust" --limit 10

# Autocomplete with object type filter
pvw search autoComplete --keywords "sales" --objectType "Tables"
```

#### Suggestions

Get fuzzy search suggestions.

```bash
# Basic suggestions
pvw search suggest --keywords "customer dat" --limit 10

# Fuzzy suggestions
pvw search suggest --keywords "cusstomer" --fuzzy --limit 15
```

#### Browse

Hierarchical navigation of assets.

```bash
# Browse by entity type
pvw search browse --entityType "DataSet" --limit 20

# Browse with path
pvw search browse --path "/subscriptions/sub-123" --includeSubPaths

# Browse with collection context
pvw search browse --entityType "Tables" --collection "sales-data"
```

### 2. Advanced Search Commands

#### Advanced Query

Search with business metadata and complex filtering.

```bash
# Search with business metadata
pvw search advanced --keywords "customer" \
  --businessMetadata '{"Department":"Finance","Owner":"john.doe@company.com"}' \
  --classifications "PII,Confidential"

# Search with term assignments
pvw search advanced --keywords "financial data" \
  --termAssignments "Finance.CustomerData" \
  --objectTypes "Tables,Views"

# Load business metadata from file
pvw search advanced --keywords "sensitive" \
  --businessMetadata "examples/search_filters/business_metadata_example.json"
```

#### Faceted Search

Explore data through categorical facets.

```bash
# Basic faceted search
pvw search faceted --keywords "customer" \
  --facetFields "objectType,classification,assetType" \
  --facetCount 20

# Advanced faceted search with custom sort
pvw search faceted --keywords "sales data" \
  --facetFields "objectType,classification,term,contactId" \
  --facetCount 30 --facetSort "value"

# Collection-scoped faceted search
pvw search faceted --keywords "financial" \
  --collection "finance-department" \
  --facetFields "classification,term"
```

#### Time-based Search

Filter assets by creation or modification dates.

```bash
# Find recently created assets
pvw search timerange --keywords "customer" \
  --createdAfter "2024-01-01T00:00:00Z" \
  --limit 50

# Find assets modified in date range
pvw search timerange --keywords "sales" \
  --modifiedAfter "2024-06-01T00:00:00Z" \
  --modifiedBefore "2024-12-31T23:59:59Z"

# Combine time filters
pvw search timerange --keywords "financial" \
  --createdAfter "2024-01-01T00:00:00Z" \
  --modifiedAfter "2024-06-01T00:00:00Z" \
  --objectTypes "Tables,Views"
```

#### Entity Type Search

Search specific entity types with type-specific attributes.

```bash
# Search specific entity types
pvw search entitytype --keywords "transaction" \
  --entityTypes "Tables,Views" \
  --limit 30

# Search with type attributes
pvw search entitytype --keywords "customer data" \
  --entityTypes "Tables" \
  --typeAttributes "examples/search_filters/type_attributes_example.json"

# Collection-scoped entity search
pvw search entitytype --keywords "sales" \
  --entityTypes "DataSets,Reports" \
  --collection "sales-analytics"
```

## Filter Examples

### Complex Filter Files

#### Advanced Filter Example

File: `examples/search_filters/advanced_filter_example.json`

This demonstrates complex AND/OR logic for finding Tables or Views that have PII or Confidential classifications and contain "SQL" in the asset type.

```json
{
  "and": [
    {
      "condition": {
        "field": "objectType",
        "operator": "in",
        "value": ["Tables", "Views"]
      }
    },
    {
      "or": [
        {
          "condition": {
            "field": "classification",
            "operator": "eq",
            "value": "PII"
          }
        },
        {
          "condition": {
            "field": "classification",
            "operator": "eq",
            "value": "Confidential"
          }
        }
      ]
    },
    {
      "condition": {
        "field": "assetType",
        "operator": "contains",
        "value": "SQL"
      }
    }
  ]
}
```

Usage:

```bash
pvw search query --keywords "customer" --filterFile "examples/search_filters/advanced_filter_example.json"
```

#### Facets Configuration Example

File: `examples/search_filters/facets_example.json`

Configure multiple facets with different count limits and sorting.

```json
[
  {
    "field": "objectType",
    "count": 20,
    "sort": "count"
  },
  {
    "field": "classification",
    "count": 15,
    "sort": "count"
  },
  {
    "field": "assetType",
    "count": 25,
    "sort": "value"
  }
]
```

Usage:

```bash
pvw search query --keywords "data" --facets-file "examples/search_filters/facets_example.json"
```

#### Business Metadata Example

File: `examples/search_filters/business_metadata_example.json`

Search based on custom business attributes.

```json
{
  "Department": {
    "operator": "eq",
    "value": "Finance"
  },
  "Owner": {
    "operator": "eq",
    "value": "john.doe@company.com"
  },
  "DataClassification": {
    "operator": "in",
    "value": ["Sensitive", "Confidential"]
  }
}
```

Usage:

```bash
pvw search advanced --businessMetadata "examples/search_filters/business_metadata_example.json"
```

## Supported Object Types

- **Tables** - Database tables and views
- **Files** - Data files and documents
- **Views** - Database views and materialized views
- **Dashboards** - Business intelligence dashboards
- **Reports** - Analytical reports and documents
- **KPIs** - Key performance indicators
- **DataSets** - Logical groupings of data
- **DataFlows** - ETL and data processing workflows
- **DataSources** - Data source connections
- **Glossaries** - Business glossary containers
- **GlossaryTerms** - Individual glossary terms
- **Classifications** - Data classification labels

## Common Filter Fields

- **objectType** - Type of the asset
- **classification** - Data classification labels
- **term** - Glossary term assignments
- **contactId** - Asset contact/owner
- **assetType** - Specific asset type (e.g., "Azure SQL Database")
- **replicatedTo** - Replication target
- **replicatedFrom** - Replication source
- **label** - Custom labels

## Operators

- **eq** - Equals
- **ne** - Not equals
- **in** - In a list of values
- **nin** - Not in a list of values
- **contains** - Contains substring
- **startswith** - Starts with string
- **endswith** - Ends with string
- **gte** - Greater than or equal (for dates/numbers)
- **lte** - Less than or equal (for dates/numbers)
- **gt** - Greater than (for dates/numbers)
- **lt** - Less than (for dates/numbers)

## Best Practices

### Performance Optimization

1. **Use specific object types** when possible to reduce result set size
2. **Limit results** using `--limit` parameter (default: 50, max recommended: 1000)
3. **Use collections** to scope searches to relevant data domains
4. **Combine filters** to create precise searches rather than broad keyword searches

### Search Strategy

1. **Start broad, then narrow** - Begin with basic keyword search, then add filters
2. **Use faceted search** to explore unknown data domains
3. **Leverage business metadata** for organization-specific searches
4. **Use time-based filters** for data freshness analysis

### Filter Construction

1. **Test simple filters first** before building complex AND/OR logic
2. **Use the SearchFilterBuilder** programmatically for complex filters
3. **Validate JSON syntax** before using filter files
4. **Document filter logic** for reusable search patterns

## Troubleshooting

### Common Issues

1. **No results returned**

   - Check object type filters are correct
   - Verify collection access permissions
   - Try broader keyword searches
   - Check filter syntax

2. **Performance issues**

   - Reduce result limit
   - Add more specific filters
   - Use collection scoping
   - Avoid overly complex filter logic

3. **Invalid filter syntax**
   - Validate JSON syntax
   - Check operator names
   - Verify field names
   - Use the parameter validation feature

### Validation

```bash
# Validate search parameters before execution
pvw search query --keywords "test" --objectTypes "InvalidType" --limit 1500
# This will show warnings about invalid object type and excessive limit
```

### Debug Mode

```bash
# Enable debug mode for detailed logging
pvw --debug search query --keywords "customer data"
```

## Integration Examples

### Scripting

```bash
#!/bin/bash
# Find all PII data in finance collections

echo "Searching for PII data in finance collections..."
pvw search advanced \
  --keywords "*" \
  --classifications "PII" \
  --collection "finance-data" \
  --limit 100 \
  --output-file "pii_audit.json"

echo "Generating faceted analysis..."
pvw search faceted \
  --keywords "*" \
  --collection "finance-data" \
  --facetFields "objectType,classification,contactId" \
  --output-file "finance_analysis.json"
```

### PowerShell

```powershell
# Find recently modified customer data
$results = pvw search timerange `
  --keywords "customer" `
  --modifiedAfter "2024-06-01T00:00:00Z" `
  --objectTypes "Tables,Views" `
  --format "json"

$data = $results | ConvertFrom-Json
Write-Host "Found $($data.'@search.count') assets"
```

### Python Integration

```python
import subprocess
import json

# Execute advanced search
result = subprocess.run([
    'pvw', 'search', 'advanced',
    '--keywords', 'financial',
    '--businessMetadata', '{"Department":"Finance"}',
    '--format', 'json'
], capture_output=True, text=True)

data = json.loads(result.stdout)
print(f"Found {data['@search.count']} assets")

for asset in data.get('value', []):
    print(f"- {asset.get('name', 'Unknown')}: {asset.get('assetType', 'Unknown')}")
```

## API Compliance

This implementation is fully compliant with the Microsoft Purview Discovery Query API 2024-03-01-preview specification, supporting:

- ✅ Complex filter operations (AND/OR/NOT)
- ✅ Multiple object type filtering
- ✅ Advanced faceting and aggregation
- ✅ Business metadata attribute searches
- ✅ Classification and label filtering
- ✅ Time-based filtering with date ranges
- ✅ Pagination with continuation tokens
- ✅ Term assignment searches
- ✅ Asset type filtering
- ✅ Collection scoping
- ✅ Fuzzy search capabilities
- ✅ Type-specific attribute filtering

For the complete API specification, visit:
https://docs.microsoft.com/en-us/rest/api/purview/datamapdataplane/discovery
