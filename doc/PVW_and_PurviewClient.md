# PVW CLI & PurviewClient: Advanced Azure Purview Automation

## Overview

**PVW CLI** and the **PurviewClient** Python library provide a powerful, developer-friendly, and automation-focused complement to the Azure Purview web UI. They enable advanced data catalog management, bulk operations, and deep integration with CI/CD, scripting, and data engineering workflows.

---

## What is PVW CLI?

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

## What is PurviewClient?

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

## Installation

### Install PVW CLI
```bash
pip install pvw-cli
```

Or for development:
```bash
git clone https://github.com/your-org/pvw-cli.git
cd pvw-cli
pip install -r requirements.txt
pip install -e .
```

### Install PurviewClient (as a library)
If using as a Python library in your own scripts:
```bash
pip install pvw-cli  # PurviewClient is included
```
Or copy `purviewcli/client/client.py` into your project and install dependencies from `requirements.txt`.

---

## Getting Started

### 1. Configure Authentication
Set environment variables for your Purview account:
```bash
export PURVIEW_ACCOUNT_NAME=your-purview-account
export AZURE_REGION=  # (optional: 'china', 'usgov', etc.)
```
Authenticate using Azure CLI (`az login`), Managed Identity, or Service Principal.

### 2. Using PVW CLI

List all available commands:
```bash
pvw --help
```

**Basic Operations:**
```bash
# Import entities from CSV
pvw entity import-csv --csv-file datasets.csv --template dataset

# Export entities
pvw entity export-csv --query "name:customer*" --output-file exported.csv

# Validate a CSV before import
pvw validate csv --csv-file datasets.csv --template dataset
```

**Advanced Features:**
```bash
# Business Rules & Governance
pvw governance check-compliance --entity-guid "entity-123"
pvw governance compliance-report --collection "sales-data"

# Real-time Monitoring
pvw monitoring dashboard --refresh-interval 30
pvw monitoring export-metrics --format "json"

# Advanced Lineage Analysis
pvw lineage analyze-impact --entity-guid "entity-123" --depth 5
pvw lineage visualize --entity-guid "entity-123" --direction "both"

# Plugin System
pvw plugins list --category "datasource"
pvw plugins execute --name "my_plugin" --config "config.json"

# CSV Lineage Processing
pvw lineage_csv process --input-file "lineage.csv"
pvw lineage_csv templates --output-dir "templates"

# Web UI Interface
pvw ui start --port 8080
```

### 3. Using PurviewClient in Python

**Basic Usage:**
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

**Advanced Features Integration:**
```python
from purviewcli.client.business_rules import BusinessRulesEngine
from purviewcli.client.monitoring_dashboard import MonitoringDashboard
from purviewcli.client.lineage_visualization import AdvancedLineageAnalyzer

# Business Rules Engine
rules_engine = BusinessRulesEngine(client.config)
compliance_result = rules_engine.check_entity_compliance("entity-guid")

# Monitoring Dashboard
dashboard = MonitoringDashboard(client.config)
metrics = dashboard.collect_metrics()

# Advanced Lineage
lineage_analyzer = AdvancedLineageAnalyzer(client.config)
impact_analysis = lineage_analyzer.analyze_lineage_impact("entity-guid", max_depth=5)
```

---

## Advanced Features & Enhancements

### PVW CLI

**Core Features:**
- **Profile Management**: Easily switch between multiple Purview accounts/environments
- **Bulk CSV Lineage**: Create hundreds of lineage relationships from a CSV
- **Glossary Automation**: Import/export terms, assign terms in bulk
- **Data Quality Validation**: Check for schema, required fields, and data quality before import
- **Progress & Error Reporting**: Real-time progress bars, detailed error logs
- **CI/CD Integration**: Use in DevOps pipelines for automated catalog management

**Advanced Features (v2.0):**
- **Business Rules Engine**: Automated governance policy enforcement with customizable rules
- **Real-time Monitoring Dashboard**: Live metrics collection with alerting and performance monitoring
- **Advanced Lineage Visualization**: Deep lineage analysis with impact assessment and gap detection
- **Plugin System**: Extensible architecture for adding custom functionality and integrations
- **CSV Lineage Processing**: Bulk lineage creation and management from CSV files
- **Web UI Interface**: Modern web-based dashboard for visual data governance operations

### PurviewClient

**Core Features:**
- **Async & Parallel Operations**: Use `http_request_async` and `bulk_operation` for high throughput
- **Retry & Rate Limiting**: Automatic handling of throttling and transient errors
- **Comprehensive Logging**: File and console logs for all operations
- **Custom Error Handling**: Detailed diagnostics for 403/429 and other errors
- **File Download Support**: Handles CSV and binary downloads automatically
- **Health Checks**: Programmatically check Purview service health

**Advanced Integrations (v2.0):**
- **Business Rules API**: Programmatic access to governance rules and compliance checking
- **Monitoring API**: Real-time metrics collection and dashboard management
- **Lineage Analysis API**: Advanced lineage traversal and impact analysis
- **Plugin Management API**: Dynamic loading and execution of custom plugins

---

## When to Use PVW CLI & PurviewClient
- **Bulk Operations**: When you need to import/export/update thousands of entities, terms, or relationships
- **Automation**: For scheduled, repeatable, or CI/CD-driven catalog management
- **Validation**: To ensure data quality before making changes
- **Integration**: When integrating Purview with other data tools, ETL, or governance workflows
- **Advanced Diagnostics**: For troubleshooting, auditing, and advanced error handling

---

## PVW & PurviewClient vs. Purview UI
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

## Resources
- [Official Documentation](https://pvw-cli.readthedocs.io/)
- [GitHub Repository](https://github.com/your-org/pvw-cli)
- [Azure Purview Docs](https://learn.microsoft.com/en-us/azure/purview/)

---

**PVW CLI and PurviewClient empower data engineers, stewards, and architects to automate, scale, and enhance their Azure Purview experience far beyond the web UI.**
