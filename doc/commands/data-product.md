# Data Product Command Group Documentation

## Overview

The `data-product` command group in PVW CLI provides advanced management for data products in Microsoft Purview, supporting operations such as creation, import, classification, labeling, glossary linking, lineage, and status management. This is part of the CLI's broader support for all major Purview APIs (entity, glossary, lineage, collections, search, etc.).

## Available Commands

- `import` — Import data products from a CSV file
- `create` — Create a new data product
- `show` — Show details of a data product
- `delete` — Delete a data product
- `list` — List all data products
- `add-classification` — Add a classification to a data product
- `remove-classification` — Remove a classification from a data product
- `add-label` — Add a label to a data product
- `remove-label` — Remove a label from a data product
- `link-glossary` — Link a glossary term to a data product
- `show-lineage` — Show lineage for a data product
- `set-status` — Set the status of a data product

## Usage Examples

### Import Data Products from CSV
```bash
pvw data-product import --csv-file=products.csv
```

### Create a Data Product
```bash
pvw data-product create --qualified-name="product.test.1" --name="Test Product" --description="A test data product"
```

### Add Classification
```bash
pvw data-product add-classification --qualified-name="product.test.1" --classification="PII"
```

### Add Label
```bash
pvw data-product add-label --qualified-name="product.test.1" --label="gold"
```

### Link Glossary Term
```bash
pvw data-product link-glossary --qualified-name="product.test.1" --term="Customer"
```

### Set Status
```bash
pvw data-product set-status --qualified-name="product.test.1" --status="active"
```

### Show Lineage
```bash
pvw data-product show-lineage --qualified-name="product.test.1"
```

### Delete Data Product
```bash
pvw data-product delete --qualified-name="product.test.1"
```

## Notes
- All commands require a valid Purview account and authentication (see main README for setup).
- The `data-product` group is part of a full-featured CLI supporting all Purview APIs, not a standalone tool.
- For more details on global CLI usage, see the main README and other command group docs.
