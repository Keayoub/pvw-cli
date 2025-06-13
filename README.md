# PURVIEW CLI v2.0 - Microsoft Purview Automation & Data Governance

> **LATEST UPDATE (June 2025):**
> - Major: Advanced Data Product Management (see new `data-product` command group)
> - Enhanced Discovery Query/Search support (see below for usage).

---

## What is PVW CLI?

**PVW CLI v2.0** is a modern, full-featured command-line interface and Python library for Microsoft Purview. It enables automation and management of *all major Purview APIs* including:

- Entity management (create, update, bulk, import/export)
- Glossary and term management
- Lineage operations
- Collection and account management
- Advanced search and discovery
- Data product management (new, see below)
- Classification, label, and status management
- And more (see command reference)

The CLI is designed for data engineers, stewards, architects, and platform teams to automate, scale, and enhance their Microsoft Purview experience.

---

## Quick Start (pip install)

Get started with PVW CLI in minutes:

1. **Install the CLI**

   ```bash
   pip install pvw-cli
   ```

2. **Set Environment Variables**

   ```bash
   set PURVIEW_ACCOUNT_NAME=your-purview-account
   set AZURE_REGION=  # (optional, e.g. 'china', 'usgov')
   ```

3. **Authenticate**

   - Run `az login` (recommended)
   - Or set Service Principal credentials as environment variables

4. **Run Your First Search**

   ```bash
   pvw search query --keywords="customer" --limit=5
   ```

5. **See All Commands**

   ```bash
   pvw --help
   ```

For more advanced usage, see the sections below or visit the [documentation](https://pvw-cli.readthedocs.io/).

---

## Overview

**PVW CLI v2.0** is a modern command-line interface and Python library for Microsoft Purview, enabling:

- Advanced data catalog search and discovery
- Bulk import/export of entities, glossary terms, and lineage
- Real-time monitoring and analytics
- Automated governance and compliance
- Extensible plugin system

---

## Installation

You can install PVW CLI in two ways:

1. **From PyPI (recommended for most users):**

   ```bash
   pip install pvw-cli
   ```

2. **Directly from the GitHub repository (for latest/dev version):**

   ```bash
   pip install git+https://github.com/Keayoub/Purview_cli.git
   ```

Or for development (editable install):

```bash
git clone https://github.com/Keayoub/Purview_cli.git
cd Purview_cli
pip install -r requirements.txt
pip install -e .
```

---

## Requirements

- Python 3.8+
- Azure CLI (`az login`) or Service Principal credentials
- Microsoft Purview account

---

## Getting Started

1. **Install**

   ```bash
   pip install pvw-cli
   ```

2. **Set Environment Variables**

   ```bash
   set PURVIEW_ACCOUNT_NAME=your-purview-account
   set AZURE_REGION=  # (optional, e.g. 'china', 'usgov')
   ```

3. **Authenticate**

   - Azure CLI: `az login`

   - Or set Service Principal credentials as environment variables

4. **Run a Command**

   ```bash
   pvw search query --keywords="customer" --limit=5
   ```

5. **See All Commands**

   ```bash
   pvw --help
   ```

---

## Authentication

PVW CLI supports multiple authentication methods for connecting to Microsoft Purview, powered by Azure Identity's `DefaultAzureCredential`. This allows you to use the CLI securely in local development, CI/CD, and production environments.

### 1. Azure CLI Authentication (Recommended for Interactive Use)

- Run `az login` to authenticate interactively with your Azure account.
- The CLI will automatically use your Azure CLI credentials.

### 2. Service Principal Authentication (Recommended for Automation/CI/CD)

Set the following environment variables before running any PVW CLI command:

- `AZURE_CLIENT_ID` (your Azure AD app registration/client ID)
- `AZURE_TENANT_ID` (your Azure AD tenant ID)
- `AZURE_CLIENT_SECRET` (your client secret)

**Example (Windows):**

```cmd
set AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
set AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
set AZURE_CLIENT_SECRET=your-client-secret
```

**Example (Linux/macOS):**

```bash
export AZURE_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export AZURE_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
export AZURE_CLIENT_SECRET=your-client-secret
```

### 3. Managed Identity (for Azure VMs, App Services, etc.)

If running in Azure with a managed identity, no extra configuration is needed. The CLI will use the managed identity automatically.

### 4. Visual Studio/VS Code Authentication

If you are signed in to Azure in Visual Studio or VS Code, `DefaultAzureCredential` can use those credentials as a fallback.

---

**Note:**
- The CLI will try all supported authentication methods in order. The first one that works will be used.
- For most automation and CI/CD scenarios, service principal authentication is recommended.
- For local development, Azure CLI authentication is easiest.

For more details, see the [Azure Identity documentation](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python).

---

## Search Command (Discovery Query API)

The PVW CLI provides advanced search using the latest Microsoft Purview Discovery Query API:

- Search for assets, tables, files, and more with flexible filters
- Use autocomplete and suggestion endpoints
- Perform faceted, time-based, and entity-type-specific queries

### CLI Usage Examples

```bash
# Basic search for assets with keyword 'customer'
pvw search query --keywords="customer" --limit=5

# Advanced search with classification filter
pvw search query --keywords="sales" --classification="PII" --objectType="Tables" --limit=10

# Autocomplete suggestions for partial keyword
pvw search autocomplete --keywords="ord" --limit=3

# Get search suggestions (fuzzy matching)
pvw search suggest --keywords="prod" --limit=2

# Faceted search with aggregation
pvw search query --keywords="finance" --facetFields="objectType,classification" --limit=5

# Browse entities by type and path
pvw search browse --entityType="Tables" --path="/root/finance" --limit=2

# Time-based search for assets created after a date
pvw search query --keywords="audit" --createdAfter="2024-01-01" --limit=1

# Entity type specific search
pvw search query --entityTypes="Files,Tables" --limit=2
```

### Python Usage Example

```python
from purviewcli.client._search import Search

search = Search()
args = {"--keywords": "customer", "--limit": 5}
search.searchQuery(args)
print(search.payload)  # Shows the constructed search payload
```

### Test Examples

See `tests/test_search_examples.py` for ready-to-run pytest examples covering all search scenarios:

- Basic query
- Advanced filter
- Autocomplete
- Suggest
- Faceted search
- Browse
- Time-based search
- Entity type search

---

## Data Product Management (Advanced)

PVW CLI now includes a powerful `data-product` command group for advanced data product lifecycle management. This is in addition to the CLI's support for all core Purview APIs.

See [`doc/commands/data-product.md`](doc/commands/data-product.md) for full documentation and examples.

### Example Commands

```bash
# Create a data product
pvw data-product create --qualified-name="product.test.1" --name="Test Product" --description="A test data product"

# Add classification and label
pvw data-product add-classification --qualified-name="product.test.1" --classification="PII"
pvw data-product add-label --qualified-name="product.test.1" --label="gold"

# Link glossary term
data-product link-glossary --qualified-name="product.test.1" --term="Customer"

# Set status and show lineage
data-product set-status --qualified-name="product.test.1" --status="active"
data-product show-lineage --qualified-name="product.test.1"
```

---

## Core Features

- **Discovery Query/Search**: Flexible, advanced search for all catalog assets
- **Entity Management**: Bulk import/export, update, and validation
- **Glossary Management**: Import/export terms, assign terms in bulk
- **Lineage Operations**: Lineage discovery, CSV-based bulk lineage
- **Monitoring & Analytics**: Real-time dashboards, metrics, and reporting
- **Plugin System**: Extensible with custom plugins

---

## Contributing & Support

- [Documentation](https://github.com/Keayoub/Purview_cli/blob/main/doc/README.md)
- [Issue Tracker](https://github.com/Keayoub/Purview_cli/issues)
- [Email Support](mailto:keayoub@msn.com)

---

**PVW CLI empowers data engineers, stewards, and architects to automate, scale, and enhance their Microsoft Purview experience with powerful command-line and programmatic capabilities.**
