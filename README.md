# PURVIEW CLI v2.0 - Azure Purview Automation & Data Governance

> **LATEST UPDATE (June 2025):**
> - Enhanced Discovery Query/Search support (see below for usage).

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

**PVW CLI v2.0** is a modern command-line interface and Python library for Azure Purview, enabling:

- Advanced data catalog search and discovery
- Bulk import/export of entities, glossary terms, and lineage
- Real-time monitoring and analytics
- Automated governance and compliance
- Extensible plugin system

---

## Installation

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

## Core Features

- **Discovery Query/Search**: Flexible, advanced search for all catalog assets
- **Entity Management**: Bulk import/export, update, and validation
- **Glossary Management**: Import/export terms, assign terms in bulk
- **Lineage Operations**: Lineage discovery, CSV-based bulk lineage
- **Monitoring & Analytics**: Real-time dashboards, metrics, and reporting
- **Plugin System**: Extensible with custom plugins

---

## Contributing & Support

- [Documentation](https://github.com/Keayoub/Purview_cli/blob/main/README.md)
- [Issue Tracker](https://github.com/Keayoub/Purview_cli/issues)
- [Email Support](mailto:keayoub@msn.com)

---

**PVW CLI empowers data engineers, stewards, and architects to automate, scale, and enhance their Azure Purview experience with powerful command-line and programmatic capabilities.**
