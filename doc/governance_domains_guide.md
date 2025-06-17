# Microsoft Purview Governance Domains Guide

This guide explains how to use the Microsoft Purview CLI to manage governance domains.

## What are Governance Domains?

Governance domains are business-level groupings for data stewardship, policy, and reporting in Microsoft Purview. They help organize assets across the catalog for different business units or logical domains.

## Prerequisites

1. A Microsoft Purview account
2. Authentication token for the Purview account

## Setting Up Authentication

Before running any command, set up your authentication:

```bash
# Option 1: Use environment variables
set PURVIEW_ENDPOINT=https://your-account.purview.azure.com
set PURVIEW_TOKEN=your-token-here

# Option 2: Provide endpoint and token with each command
pvw --endpoint https://your-account.purview.azure.com --token your-token-here domain list
```

## Working with Domains

### List All Domains

```bash
pvw domain list
```

### Create a New Domain

```bash
pvw domain create --domain-name engineering --friendly-name "Engineering Domain" --description "Domain for engineering assets"
```

### Get Information About a Domain

```bash
pvw domain get engineering
```

### Update a Domain

```bash
pvw domain update engineering --friendly-name "Engineering Data Domain" --description "Updated description"
```

### Delete a Domain

```bash
pvw domain delete engineering
```

## Associating Assets with Domains

After creating domains, you need to associate assets with them:

1. Use the entity CLI to update entities with a domain attribute:

   ```bash
   pvw entity set-attribute --guid ASSET_GUID --attribute-name "domain" --attribute-value "engineering"
   ```

2. Or bulk update entities:

   ```bash
   pvw entity bulk-update-attributes --csv your_assets.csv
   ```

## Best Practices

1. Create logical domains based on business units or data domains
2. Maintain consistent naming conventions for domains
3. Document domain purposes and stewards
4. Use collections and domains together for complete governance

## Troubleshooting

- Error "Endpoint and token must be set in context": Set the PURVIEW_ENDPOINT and PURVIEW_TOKEN environment variables or provide --endpoint and --token options
- Error "Access denied": Ensure your token has the right permissions for governance domain management
