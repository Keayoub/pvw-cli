# PURVIEW CLI - Comprehensive Azure Purview Automation

## PVW CLI & PurviewClient: Advanced Azure Purview Automation

**PVW CLI** and the **PurviewClient** Python library provide a powerful, developer-friendly, and automation-focused complement to the Azure Purview web UI. They enable advanced data catalog management, bulk operations, and deep integration with CI/CD, scripting, and data engineering workflows.

---

### What is PVW CLI?

**PVW CLI** is an enhanced command-line interface for Azure Purview, designed to:

- Automate complex data catalog, lineage, and governance tasks
- Support bulk import/export, validation, and advanced CSV operations
- Manage Purview profiles, environments, and authentication
- Integrate seamlessly with CI/CD, scripting, and data engineering pipelines
- Provide rich output, progress tracking, and error reporting

**Key Added Value:**

- **Automation**: Script and schedule any Purview operation
- **Bulk Operations**: Import/export thousands of entities, relationships, or glossary terms in one go
- **Validation**: Built-in data quality and schema validation before import
- **Template System**: Reusable templates for common entity and lineage types
- **Developer Experience**: Rich CLI output, progress bars, and error diagnostics
- **Complement to UI**: Enables tasks not possible or practical in the web UI (e.g., mass updates, integration with other tools)

---

### What is PurviewClient?

**PurviewClient** is a Python library that provides:

- Full programmatic access to the latest Azure Purview REST APIs
- Advanced retry, rate limiting, and error handling
- Async and sync HTTP support for high-performance automation
- Bulk operation helpers for parallel processing
-  logging and diagnostics
- Easy integration with Python scripts, notebooks, and automation tools

**Key Enhancements Over SDK/UI:**

- **Comprehensive API Coverage**: Access all data plane and control plane APIs
- **Advanced Automation**: Retry logic, rate limiting, async support
- **Bulk & Parallel Operations**: Efficiently process large datasets
- **Custom Logging**: Detailed logs for debugging and auditing
- **Error Diagnostics**: Rich error messages and token diagnostics

---

### Installation

#### Install PVW CLI

```bash
pip install pvw-cli
```

Or for development:

```bash
git clone https://github.com/Keayoub/Purview_cli.git
cd Purview_cli
pip install -r requirements.txt
pip install -e .
```

#### Install PurviewClient (as a library)

If using as a Python library in your own scripts:

```bash
pip install pvw-cli  # PurviewClient is included
```

Or copy `purviewcli/client/client.py` into your project and install dependencies from `requirements.txt`.

---

### Getting Started

#### 1. Configure Authentication

Set environment variables for your Purview account:

```bash
export PURVIEW_NAME=your-purview-account
export AZURE_REGION=  # (optional: 'china', 'usgov', etc.)
```

Authenticate using Azure CLI (`az login`), Managed Identity, or Service Principal.

#### 2. Using PVW CLI

List all available commands:

```bash
pvw --help
```

Import entities from CSV:

```bash
pvw entity import-csv --csv-file datasets.csv --template dataset
```

Export entities:

```bash
pvw entity export-csv --query "name:customer*" --output-file exported.csv
```

Validate a CSV before import:

```bash
pvw validate csv --csv-file datasets.csv --template dataset
```

#### 3. Using PurviewClient in Python

```python
from purviewcli.client.client import PurviewClient

client = PurviewClient()
client.set_region('catalog')
client.set_account('catalog')
client.set_token('catalog')

# Example: List entities
response = client.http_request('catalog', 'GET', '/api/atlas/v2/entity/bulk?typeName=DataSet')
print(response)
```

---

### Advanced Features & Enhancements

#### PVW CLI

- **Profile Management**: Easily switch between multiple Purview accounts/environments
- **Bulk CSV Lineage**: Create hundreds of lineage relationships from a CSV
- **Glossary Automation**: Import/export terms, assign terms in bulk
- **Data Quality Validation**: Check for schema, required fields, and data quality before import
- **Progress & Error Reporting**: Real-time progress bars, detailed error logs
- **CI/CD Integration**: Use in DevOps pipelines for automated catalog management

#### PurviewClient

- **Async & Parallel Operations**: Use `http_request_async` and `bulk_operation` for high throughput
- **Retry & Rate Limiting**: Automatic handling of throttling and transient errors
- **Comprehensive Logging**: File and console logs for all operations
- **Custom Error Handling**: Detailed diagnostics for 403/429 and other errors
- **File Download Support**: Handles CSV and binary downloads automatically
- **Health Checks**: Programmatically check Purview service health

---

### When to Use PVW CLI & PurviewClient

- **Bulk Operations**: When you need to import/export/update thousands of entities, terms, or relationships
- **Automation**: For scheduled, repeatable, or CI/CD-driven catalog management
- **Validation**: To ensure data quality before making changes
- **Integration**: When integrating Purview with other data tools, ETL, or governance workflows
- **Advanced Diagnostics**: For troubleshooting, auditing, and advanced error handling

---

### PVW & PurviewClient vs. Purview UI

| Feature                | Purview UI | PVW CLI / PurviewClient |
|------------------------|:----------:|:----------------------:|
| Bulk Import/Export     |    ❌      |           ✅           |
| Automation/Scripting   |    ❌      |           ✅           |
| Data Quality Validation|    ❌      |           ✅           |
| CI/CD Integration      |    ❌      |           ✅           |
| Custom Logging         |    ❌      |           ✅           |
| Advanced Diagnostics   |    ❌      |           ✅           |
| Profile Management     |    ❌      |           ✅           |
| Async/Parallel Ops     |    ❌      |           ✅           |

---

### Resources

- [Official Documentation](https://pvw-cli.readthedocs.io/)
- [GitHub Repository](https://github.com/your-org/pvw-cli)
- [Azure Purview Docs](https://learn.microsoft.com/en-us/azure/purview/)

---

**PVW CLI and PurviewClient empower data engineers, stewards, and architects to automate, scale, and enhance their Azure Purview experience far beyond the web UI.**

## Key Features

### 🚀 **Comprehensive API Coverage**

- **Data Map API**: Complete entity lifecycle management
- **Data Estate Insights**: Advanced analytics and reporting
- **Glossary Management**: Terms, categories, and assignments
- **Lineage Operations**: Automated lineage discovery and mapping
- **Collections Management**: Hierarchical organization
- **Scanning & Discovery**: Source registration and scanning
- **Policy Management**: Data governance and access policies

### 📊 **Batch Operations & CSV Support**

- **Bulk Entity Import/Export**: Process thousands of entities efficiently
- **CSV Templates**: Predefined templates for common entity types
- **Custom Mappings**: Flexible attribute mapping configurations
- **Progress Tracking**: Real-time progress indicators
- **Error Handling**: Comprehensive error reporting and retry logic
- **Data Validation**: Schema validation before processing

### 🔗 ** CSV Lineage Processing** ⭐ NEW

- **Bulk Lineage Creation**: Process hundreds of lineage relationships from CSV files
- **Multiple Relationship Types**: DataFlow, ColumnMapping, Process, Derivation, Custom
- **Entity Validation**: Automatic validation and creation of missing entities
- **Batch Processing**: Configurable batch sizes for optimal performance
- **Progress Tracking**: Rich console output with progress bars and statistics
- **Template System**: Pre-built templates for ETL, column mapping, and basic lineage scenarios
- **Metadata Support**: Include custom metadata and confidence scores
- **Error Recovery**: Comprehensive error handling with detailed reporting

### 🎯 **Advanced Automation**

- **Template System**: Reusable configuration templates
- **Workflow Engine**: Multi-step automation workflows
- **Async Processing**: High-performance concurrent operations
- **Monitoring & Logging**: Detailed operation tracking
- **Configuration Profiles**: Multiple environment management

### 🛠️ **Developer-Friendly CLI**

- **Rich Output**: Beautiful tables, progress bars, and colored output
- **Interactive Mode**: Guided operations with prompts
- **Multiple Formats**: JSON, CSV, Table, YAML output support
- **Pipeline Integration**: Perfect for CI/CD workflows
- **Extensible Architecture**: Easy to add new operations

## Quick Start

### 1. Set Environment Variables

```bash
# Windows (Command Prompt)
set PURVIEW_NAME=your-purview-account
set AZURE_REGION=  # Leave empty for public Azure, use 'china' or 'usgov' for other clouds

# macOS/Linux (Terminal)
export PURVIEW_NAME=your-purview-account
export AZURE_REGION=  # Leave empty for public Azure

# PowerShell
$env:PURVIEW_NAME = "your-purview-account"
$env:AZURE_REGION = ""
```

### 2. Authentication

The CLI uses Azure DefaultAzureCredential, which supports multiple authentication methods:

- Azure CLI (`az login`)
- Visual Studio Code
- Managed Identity
- Service Principal
- Interactive browser login

### 3. Basic Usage

#### Entity Operations

```bash
# Get entity information
pvw entity get --guid "12345678-1234-1234-1234-123456789012"

# Import entities from CSV
pvw entity import-csv --csv-file datasets.csv --template dataset

# Export entities to CSV
pvw entity export-csv --query "name:customer*" --output-file exported_entities.csv

# Update entities from CSV
pvw entity update-csv --csv-file updated_datasets.csv --template dataset
```

#### Glossary Operations

```bash
# Import glossary terms
pvw glossary import-terms --csv-file terms.csv --glossary-guid "glossary-guid"

# Assign terms to entities
pvw glossary assign-terms --csv-file assignments.csv
```

#### Lineage Operations

```bash
# Get entity lineage
pvw lineage get --guid "entity-guid" --direction BOTH --depth 3
```

#### 🔗 CSV Lineage Processing (NEW!)

```bash
# Process lineage relationships from CSV file
pvw lineage csv process lineage_data.csv --batch-size 100 --validate-entities --progress

# Generate sample CSV templates
pvw lineage csv generate-sample sample_basic.csv --template basic --num-samples 10
pvw lineage csv generate-sample sample_etl.csv --template etl --num-samples 5
pvw lineage csv generate-sample sample_columns.csv --template column-mapping --num-samples 8

# Validate CSV format before processing
pvw lineage csv validate lineage_data.csv

# View available templates
pvw lineage csv templates
```

**CSV Lineage Features:**

- **Bulk Processing**: Create hundreds of lineage relationships efficiently
- **Multiple Templates**: Basic, ETL pipeline, and column mapping templates
- **Entity Validation**: Automatically validate source/target entities exist
- **Missing Entity Creation**: Create placeholder entities when needed
- **Progress Tracking**: Real-time progress with detailed statistics
- **Metadata Support**: Include custom metadata and confidence scores
- **Error Recovery**: Comprehensive error handling and reporting

**Required CSV Columns:**

- `source_entity_guid`, `target_entity_guid`
- `source_entity_name`, `target_entity_name` 
- `relationship_type` (DataFlow, ColumnMapping, Process, Derivation, Custom)

**Optional Columns:**

- `process_name`, `process_guid`, `confidence_score`, `metadata`

#### Insights and Analytics

```bash
# Get asset distribution
pvw insights asset-distribution --output table
```

## CSV Templates and Examples

### Dataset Import Template

Create a CSV file with the following columns:

```csv
name,description,owner_email,source_system,schema_json,tags,location,format,size_bytes,record_count
customer_data,Customer information,owner@company.com,CRM,"{""columns"":[]}","PII,Customer",s3://bucket/path,parquet,1024000,50000
```

### Table Import Template

```csv
table_name,database_name,cluster_name,description,owner,table_type,location,parameters
customers,retail_db,prod_cluster,Customer master table,team@company.com,MANAGED_TABLE,hdfs://path,"{""format"":""parquet""}"
```

### Glossary Terms Template

```csv
name,glossary_guid,description,short_description,status
Customer,glossary-guid,A person who purchases goods,Individual buyer,Active
```

## Advanced Configuration

### Custom Entity Templates

Create custom templates for specific entity types:

```json
{
  "name": "my_custom_template",
  "type_name": "CustomEntity",
  "qualified_name_template": "{name}@{system}.{environment}",
  "attribute_mappings": [
    {
      "csv_column": "name",
      "purview_attribute": "name",
      "data_type": "string",
      "required": true
    }
  ]
}
```

Use with:

```bash
pvw entity import-csv --csv-file data.csv --config-file custom_template.json
```

### Automation Scripts

Use the provided automation examples:

```python
from scripts.automation_examples import PurviewAutomation

automation = PurviewAutomation("your-account-name")

# Bulk import
await automation.bulk_entity_import("entities.csv", "dataset")

# Export data estate
await automation.data_estate_export("./exports")

# Setup glossary
await automation.bulk_glossary_setup("terms.csv", "assignments.csv")
```

## Performance and Scalability

### Batch Processing

- **Configurable batch sizes**: Optimize for your environment
- **Concurrent processing**: Async operations for maximum throughput
- **Memory efficient**: Streaming processing for large datasets
- **Retry logic**: Automatic retry with exponential backoff
- **Progress tracking**: Real-time progress indicators

### Error Handling

- **Comprehensive validation**: Schema and data validation
- **Detailed error reports**: Specific error messages with row numbers
- **Partial success handling**: Continue processing despite individual failures
- **Recovery options**: Resume from failures

## API Coverage

### Data Plane APIs

- ✅ **Atlas API v2**: Complete entity management
- ✅ **Glossary API**: Terms, categories, assignments
- ✅ **Lineage API**: Lineage discovery and creation
- ✅ **Search API**: Advanced search capabilities
- ✅ **Types API**: Type definitions and management
- ✅ **Relationship API**: Entity relationships
- ✅ **Discovery API**: Asset discovery operations

### Control Plane APIs

- ✅ **Account Management**: Collections, resource sets
- ✅ **Scanning**: Data source scanning operations
- ✅ **Policy Store**: Metadata policies and roles
- ✅ **Insights**: Data estate analytics
- ✅ **Share**: Data sharing capabilities

## Integration Examples

### CI/CD Pipeline Integration

```yaml
# Azure DevOps Pipeline Example
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.9'

- script: |
    pip install pvw-cli
    pvw entity import-csv --csv-file $(Pipeline.Workspace)/entities.csv --template dataset
  displayName: 'Import Data Catalog Entities'
  env:
    PURVIEW_NAME: $(PURVIEW_ACCOUNT_NAME)
```

### Jupyter Notebook Integration

```python
import asyncio
from purviewcli.client.api_client import EnhancedPurviewClient, PurviewConfig

config = PurviewConfig(account_name="your-account")

async with EnhancedPurviewClient(config) as client:
    entities = await client.search_entities("*", limit=100)
    print(f"Found {len(entities.get('value', []))} entities")
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/your-org/pvw-cli.git
cd pvw-cli
pip install -r requirements_enhanced.txt
pip install -e .

# Run tests
pytest tests/

# Format code  
black purviewcli/
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure you're logged in via `az login` or have proper credentials configured
2. **Permission Errors**: Verify your account has appropriate Purview permissions
3. **Network Issues**: Check firewall and proxy settings for Azure connectivity
4. **CSV Format Issues**: Validate CSV structure matches template requirements

### Debug Mode

Enable detailed logging:

```bash
export PURVIEW_CLI_DEBUG=true
pvw entity get --guid "your-guid"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://pvw-cli.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/your-org/pvw-cli/issues)
- 💬 [Discussions](https://github.com/your-org/pvw-cli/discussions)
- 📧 [Email Support](mailto:purview-cli@your-org.com)

## Changelog

### Version 2.0.0

- Complete rewrite with async support
-  CSV operations with templates
- Rich CLI interface with progress indicators
- Comprehensive error handling
- Performance optimizations
- Extended API coverage

### Version 1.x

- Basic Purview API operations
- Simple CLI interface
- Limited batch operations

---

### Made with ❤️ for the Azure Purview community
