# Unified Catalog

The `pvw uc` command group is the modern governance surface in `pvw-cli` for Microsoft Purview Unified Catalog.

It helps you work with:

- Governance domains
- Business glossary terms
- Data products
- Objectives and key results (OKRs)
- Critical data elements (CDEs)
- Workflow and governance automation features

## Before You Start

Make sure you have:

1. Installed `pvw-cli`
2. Signed in with `az login` or configured a service principal
3. Set these environment variables:

```bash
PURVIEW_ACCOUNT_NAME
PURVIEW_ACCOUNT_ID
PURVIEW_RESOURCE_GROUP
```

If you have not done that yet, start with [Getting Started](getting-started.md).

## Unified Catalog Command Groups

Main entry point:

```bash
pvw uc --help
```

Core subcommands:

```text
pvw uc domain
pvw uc term
pvw uc dataproduct
pvw uc objective
pvw uc cde
```

## Quick Start

List governance domains:

```bash
pvw uc domain list
```

Search glossary terms:

```bash
pvw uc term search --query "customer"
```

List data products:

```bash
pvw uc dataproduct list
```

List objectives:

```bash
pvw uc objective list
```

List critical data elements:

```bash
pvw uc cde list
```

## Common Workflows

### Governance Domains

Use domains to define organizational or governance boundaries.

```bash
pvw uc domain list
pvw uc domain create --name "Finance" --description "Financial data domain"
pvw uc domain show --domain-id "<domain-id>"
```

### Glossary Terms

Use terms to define business vocabulary and synchronize governance language.

```bash
pvw uc term list --domain-id "<domain-id>"
pvw uc term create --name "Customer ID" --description "Unique customer identifier" --domain-id "<domain-id>"
pvw uc term search --query "customer"
```

Classic glossary sync is also available:

```bash
pvw uc term sync-classic --domain-id "<domain-id>" --glossary-guid "<glossary-guid>" --dry-run
```

### Data Products

Use data products to represent curated, governed data assets.

```bash
pvw uc dataproduct list
pvw uc dataproduct create --name "Customer 360" --description "Complete customer analytics" --domain-id "<domain-id>"
pvw uc dataproduct show --product-id "<product-id>"
```

### Objectives and Key Results

Use objectives to track governance goals and progress.

```bash
pvw uc objective list
pvw uc objective create --definition "Achieve 95% data quality" --domain-id "<domain-id>"
pvw uc objective update --objective-id "<objective-id>" --progress 75
```

### Critical Data Elements

Use CDEs to define high-value data elements that need extra governance attention.

```bash
pvw uc cde list
pvw uc cde create --name "Social Security Number" --description "US SSN" --domain-id "<domain-id>" --data-type "String"
```

## Recommended Learning Path

1. Create or inspect domains with `pvw uc domain`
2. Add terminology with `pvw uc term`
3. Organize governed assets with `pvw uc dataproduct`
4. Track governance goals with `pvw uc objective`
5. Define sensitive or high-value fields with `pvw uc cde`

## Related Documentation

- [Getting Started](getting-started.md)
- [Quick Reference](quick-reference.md)
- [Unified Catalog Command Reference](commands/unified-catalog.md)
- [Full Documentation Catalog](documentation-catalog.md)
