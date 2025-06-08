## Getting Started

[Home](../../README.md) > Getting Started

## Overview

[![YouTube](../image/purviewcli_youtube.png)](https://www.youtube.com/watch?v=ycr1G5iMM6U)

## Requirements

The purviewcli package works on Python versions:

* Python 3.6+
* Python 3.7+
* Python 3.8+
* Python 3.9+

## Local Installation

```
pip install purviewcli
```

## Enhanced PVW CLI Installation

For the enhanced PVW CLI with advanced features:

```
pip install -r requirements.txt
```

## Run container on Docker Desktop (Alternative)

Alternatively, you can run Purview CLI inside a self-enclosed Docker Container.

1. Build container image locally.
```
docker build -t purviewcli https://raw.githubusercontent.com/tayganr/purviewcli/master/docker/Dockerfile
```

2. Start container by injecting environment variables. Note: You will need to update the environment variables.
```
docker run --name pvw-cli-docker -d -e "PURVIEW_NAME=<your_purview_account_name>" -e "AZURE_CLIENT_ID=<your_client_id>" -e "AZURE_CLIENT_SECRET=<your_client_secret>" -e "AZURE_TENANT_ID=<your_azure_tenant_id>" purviewcli
```

3. Start a bash shell in the container.
```
docker exec -it pvw-cli-docker bash
```

## Quick Start

1. Install purviewcli (e.g. `pip install purviewcli`).

2. [OPTIONAL] Set environment variable(s).
    *  `PURVIEW_NAME`
    * `AZURE_CLIENT_ID`
    * `AZURE_TENANT_ID`
    * `AZURE_CLIENT_SECRET`

   Note #1: The environment variables related to authentication are optional as there are several methods in which we can pass credentials to purviewcli in order to authenticate with an instance of Azure Purview. See [Authentication](#authentication) for more details. 

   Note #2: While an Azure Purview account name ***must*** be specified, you can provide this value within the command itself (as opposed to via an environment variable). Simply add `--purviewName=<val>` at the end of any command.

3. Execute a command (e.g. `pvw glossary read --purviewName PURVIEW_ACCOUNT_NAME`).

Snippet of an example Python-based notebook below.  
Note: If you are executing purviewcli commands within a Python notebook, you will need to prefix the command with an exclamation mark `!`. This will ensure the command is passed to the shell (not the Python interpreter).

![purviewcli](https://raw.githubusercontent.com/tayganr/purviewcli/master/doc/image/purviewcli_notebook.png)

## Advanced Features

The enhanced PVW CLI v2.0 includes powerful new capabilities:

### Business Rules Engine
Automate governance policy enforcement with customizable rules:
```bash
# Check entity compliance
pvw governance check-compliance --entity-guid "entity-123"

# Generate compliance report
pvw governance compliance-report --collection "sales-data"
```

### Machine Learning Integration
Leverage AI for intelligent data discovery and recommendations:
```bash
# Find similar entities
pvw ml find-similar --entity-guid "entity-123" --threshold 0.8

# Detect data anomalies
pvw ml detect-anomalies --collection "sales-data"
```

### Real-time Monitoring Dashboard
Monitor your data governance operations in real-time:
```bash
# Start live monitoring dashboard
pvw monitoring dashboard --refresh-interval 30

# Export current metrics
pvw monitoring export-metrics --format "json"
```

### Advanced Lineage Visualization
Analyze data lineage with impact assessment:
```bash
# Analyze lineage impact
pvw lineage analyze-impact --entity-guid "entity-123" --depth 5

# Visualize lineage tree
pvw lineage visualize --entity-guid "entity-123" --direction "both"
```

### Plugin System
Extend functionality with custom plugins:
```bash
# List available plugins
pvw plugins list --category "datasource"

# Execute custom plugin
pvw plugins execute --name "my_plugin" --config "plugin-config.json"
```

### CSV Lineage Processing
Process lineage data from CSV files:
```bash
# Process CSV lineage
pvw lineage_csv process --input-file "lineage.csv"

# Generate lineage templates
pvw lineage_csv templates --output-dir "templates"
```

### Web UI Interface
Access a modern web interface for visual data governance:
```bash
# Start web UI
pvw ui start --port 8080

# Access dashboard at http://localhost:8080
```

For comprehensive documentation on advanced features, see [Advanced Features Guide](../ADVANCED_FEATURES.md).

## Authentication

The purviewcli package leverages the `DefaultAzureCredential` method from [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defaultazurecredential). This provides purviewcli a variety of credential sources it can use to attempt authentication (e.g. Environment Variables, Managed Identity, Visual Studio Code, Azure CLI, Interactive). For example, if you are signed into Azure within Visual Studio Code, purviewcli will leverage those existing credentials when executing a command. This negates the need to store and manage credentials specific to the purviewcli package by leveraging what exists already. Read the [azure-identity](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity#defaultazurecredential) documentation to understand the authentication hierarchy.

## Authorization

The identity executing Azure Purview CLI commands will need the following role assignments:  

* `Data Curator` (read/write on catalog objects)
* `Data Source Admin` (read/write on sources/scans)
* `Collection Admin` (assign roles/manage collections)

For more information, check out [Access control in Azure Purview](https://docs.microsoft.com/en-us/azure/purview/catalog-permissions).