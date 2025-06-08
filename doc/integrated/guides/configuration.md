# Configuration Guide

## Setting Up Authentication
Configure your Azure Purview connection settings.

### Using Environment Variables
```bash
export PURVIEW_ACCOUNT_NAME="your-account"
export PURVIEW_TENANT_ID="your-tenant-id"
```

### Using Configuration File
```bash
purview config set --account your-account --tenant your-tenant-id
```
