# Enhanced Purview CLI - Comprehensive Azure Purview Automation

## Overview

The Enhanced Purview CLI is a comprehensive command-line tool that leverages the latest Azure Purview REST API specifications to provide powerful automation capabilities for managing your data catalog, governance policies, and data estate operations.

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

## Installation

### Standard Installation
```bash
pip install purviewcli-enhanced
```

### Development Installation
```bash
git clone https://github.com/your-org/purviewcli-enhanced.git
cd purviewcli-enhanced
pip install -r requirements_enhanced.txt
pip install -e .
```

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
pv-enhanced entity get --guid "12345678-1234-1234-1234-123456789012"

# Import entities from CSV
pv-enhanced entity import-csv --csv-file datasets.csv --template dataset

# Export entities to CSV
pv-enhanced entity export-csv --query "name:customer*" --output-file exported_entities.csv

# Update entities from CSV
pv-enhanced entity update-csv --csv-file updated_datasets.csv --template dataset
```

#### Glossary Operations
```bash
# Import glossary terms
pv-enhanced glossary import-terms --csv-file terms.csv --glossary-guid "glossary-guid"

# Assign terms to entities
pv-enhanced glossary assign-terms --csv-file assignments.csv
```

#### Lineage Operations
```bash
# Get entity lineage
pv-enhanced lineage get --guid "entity-guid" --direction BOTH --depth 3
```

#### Insights and Analytics
```bash
# Get asset distribution
pv-enhanced insights asset-distribution --output table
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
pv-enhanced entity import-csv --csv-file data.csv --config-file custom_template.json
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
    pip install purviewcli-enhanced
    pv-enhanced entity import-csv --csv-file $(Pipeline.Workspace)/entities.csv --template dataset
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
git clone https://github.com/your-org/purviewcli-enhanced.git
cd purviewcli-enhanced
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
pv-enhanced entity get --guid "your-guid"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://purviewcli-enhanced.readthedocs.io/)
- 🐛 [Issue Tracker](https://github.com/your-org/purviewcli-enhanced/issues)
- 💬 [Discussions](https://github.com/your-org/purviewcli-enhanced/discussions)
- 📧 [Email Support](mailto:purview-cli@your-org.com)

## Changelog

### Version 2.0.0
- Complete rewrite with async support
- Enhanced CSV operations with templates
- Rich CLI interface with progress indicators
- Comprehensive error handling
- Performance optimizations
- Extended API coverage

### Version 1.x
- Basic Purview API operations
- Simple CLI interface
- Limited batch operations

---

**Made with ❤️ for the Azure Purview community**
