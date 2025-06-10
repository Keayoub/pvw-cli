# Purview CLI Complete Reference Guide

## Overview

The Purview CLI (`pvw`) is a comprehensive command-line interface for Microsoft Purview that provides automation-friendly access to all major functionality including entity management, glossary operations, lineage analysis, scanning, and advanced analytics.

## Architecture

The CLI is built with a modular architecture featuring:

- **Core CLI Module** (`purviewcli.cli.cli`) - Main command structure and routing
- **Client Library** (`purviewcli.client.*`) - API clients and operation handlers  
- **Plugin System** (`purviewcli.plugins.*`) - Extensible plugin architecture
- **Advanced Modules** - Monitoring, business rules, governance features, etc.

## Main Command Groups

### Core Data Management

#### entity
Entity management and bulk operations
- **Purpose**: Manage Atlas entities (datasets, tables, processes, etc.)
- **Key Features**: Bulk CSV import/export, entity lifecycle management
- **Common Operations**: create, read, update, delete, list, import/export

#### glossary  
Business glossary and vocabulary management
- **Purpose**: Manage business terms, categories, and vocabulary
- **Key Features**: Term relationships, bulk operations, category management
- **Common Operations**: create terms/categories, assign to entities, bulk import

#### lineage
Data lineage analysis and visualization
- **Purpose**: Analyze data flow and dependencies between entities
- **Key Features**: Advanced lineage analysis, impact assessment, visualization
- **Common Operations**: trace lineage, impact analysis, relationship mapping

#### relationship
Entity relationship management
- **Purpose**: Define and manage relationships between entities
- **Key Features**: Custom relationship types, bulk relationship creation
- **Common Operations**: create/delete relationships, bulk assignment

#### types
Atlas type definition management  
- **Purpose**: Manage custom entity types and attributes
- **Key Features**: Type definition CRUD, attribute management
- **Common Operations**: create/update type definitions, manage attributes

### Platform Management

#### account
Data plane account and collection management
- **Purpose**: Manage Purview account settings and collections
- **Key Features**: Collection hierarchy, access management
- **Common Operations**: collection CRUD, permission management

#### management
Control plane resource management
- **Purpose**: Manage Purview account resources and configuration
- **Key Features**: Account lifecycle, resource monitoring
- **Common Operations**: account configuration, resource monitoring

#### policystore
Metadata policies and access control
- **Purpose**: Manage data access policies and roles
- **Key Features**: Policy definition, role-based access control
- **Common Operations**: policy CRUD, role assignment

### Data Discovery & Insights

#### search
Search data assets and metadata
- **Purpose**: Discover and search across the data catalog
- **Key Features**: Advanced search, faceted navigation, bulk operations
- **Common Operations**: keyword search, faceted search, bulk queries

#### insight
Data estate insights and analytics
- **Purpose**: Generate insights about the data estate
- **Key Features**: Asset distribution, usage patterns, quality metrics
- **Common Operations**: generate reports, asset analytics

#### scan
Scanning and data source management
- **Purpose**: Manage data sources and scanning operations
- **Key Features**: Automated scanning, classification rules, credentials
- **Common Operations**: create sources, configure scans, manage credentials

### Advanced Features

#### governance
Business rules and compliance
- **Purpose**: Implement governance policies and compliance checking
- **Key Features**: Business rule engine, compliance reporting
- **Common Operations**: compliance checks, rule validation, reporting

#### monitoring
Real-time monitoring and alerting
- **Purpose**: Monitor Purview operations and generate alerts
- **Key Features**: Real-time dashboard, metric collection, alerting
- **Common Operations**: start dashboard, export metrics, configure alerts

#### plugins
Plugin system management
- **Purpose**: Manage and execute custom plugins
- **Key Features**: Plugin registry, custom operations, extensibility
- **Common Operations**: list plugins, execute operations, plugin info

### Utility Commands

#### profile
Connection profile management
- **Purpose**: Manage authentication profiles for different environments
- **Key Features**: Multi-environment support, secure credential storage
- **Common Operations**: add/remove profiles, set default, check status

#### config
Configuration management
- **Purpose**: Manage CLI configuration settings
- **Key Features**: Key-value configuration, environment-specific settings
- **Common Operations**: set/get config values, list all settings

#### validate
Data validation and quality checks
- **Purpose**: Validate data quality and consistency
- **Key Features**: Quality rule validation, data profiling
- **Common Operations**: validate CSV files, run quality checks

## Command Syntax Patterns

### Basic Pattern
```bash
pvw <group> <command> [arguments] [options]
```

### Common Options
- `--help` - Show command help
- `--output-file <file>` - Specify output file
- `--format <format>` - Output format (json, csv, table)
- `--profile <name>` - Use specific connection profile
- `--debug` - Enable debug mode

### Authentication Options
- `--account-name <name>` - Override Purview account name
- `--tenant-id <id>` - Specify Azure tenant ID
- `--region <region>` - Specify Azure region (china, usgov)

## CSV Operations

The CLI provides extensive CSV support for bulk operations:

### Entity Templates
- `basic` - Basic entity attributes
- `etl` - ETL process entities
- `column-mapping` - Column-level mapping
- `custom` - Custom templates via configuration

### CSV Import/Export
```bash
# Import entities from CSV
pvw entity import-csv --csv-file data.csv --template basic

# Export entities to CSV  
pvw entity export-csv --output-file export.csv --template basic

# Update entities from CSV
pvw entity update-csv --csv-file updates.csv --template basic
```

### Lineage CSV Operations
```bash
# Import lineage from CSV
pvw lineage import-csv --csv-file lineage.csv --template basic

# Validate lineage CSV
pvw lineage validate-csv --csv-file lineage.csv --template basic

# Generate lineage report
pvw lineage generate-report --output-file lineage-report.json
```

## Advanced Features

### Business Rules Engine
```bash
# Check entity compliance
pvw governance check-compliance --entity-guid <guid>

# Generate compliance report
pvw governance compliance-report --output-file compliance.json
```

### Real-time Monitoring
```bash
# Start monitoring dashboard
pvw monitoring dashboard --refresh-interval 30

# Export metrics
pvw monitoring export-metrics --output-file metrics.json
```

### Advanced Scanning
```bash
# Create data sources from config
pvw scanning create-sources --config-file sources.json

# Generate scan report
pvw scanning report --output-file scan-report.json --days 30
```

### Plugin System
```bash
# List available plugins
pvw plugins list

# Get plugin information
pvw plugins info --plugin-name my-plugin

# Execute plugin operation
pvw plugins execute --plugin-name my-plugin --operation analyze
```

## Configuration Management

### Profile Management
```bash
# Add new profile
pvw profile add --name prod --account-name my-account

# List profiles
pvw profile list

# Set default profile
pvw profile set-default prod

# Check authentication status
pvw profile status
```

### Configuration Settings
```bash
# Set configuration value
pvw config set debug true

# Get configuration value
pvw config get debug

# List all settings
pvw config list
```

## Error Handling and Troubleshooting

### Common Error Patterns
- **Authentication Errors**: Check profile configuration and Azure login status
- **Permission Errors**: Verify account permissions and role assignments
- **Rate Limiting**: CLI includes automatic retry with exponential backoff
- **Network Issues**: Check connectivity and firewall settings

### Debug Mode
```bash
# Enable debug mode for detailed logging
pvw --debug <command>

# Or set via configuration
pvw config set debug true
```

### Validation
```bash
# Validate CSV files before import
pvw validate csv --csv-file data.csv --template basic

# Validate configuration
pvw validate config --profile <name>
```

## Integration Patterns

### CI/CD Integration
```bash
# Automated entity management
pvw entity import-csv --csv-file "${WORKSPACE}/entities.csv" --template basic

# Generate reports
pvw insight generate-report --output-file "${BUILD_ARTIFACTSTAGINGDIRECTORY}/insights.json"
```

### Scripting and Automation
```bash
# Batch operations with error handling
pvw entity import-csv --csv-file batch1.csv --template basic || exit 1
pvw entity import-csv --csv-file batch2.csv --template basic || exit 1
```

### Data Pipeline Integration
```bash
# Update lineage after ETL completion
pvw lineage import-csv --csv-file "${PIPELINE_LINEAGE}" --template etl

# Generate data quality report
pvw governance compliance-report --output-file "${QA_REPORTS}/compliance.json"
```

## Performance Optimization

### Batch Operations
- Use CSV operations for bulk data management
- Configure appropriate batch sizes via profiles
- Utilize parallel processing where available

### Connection Management
- Use connection profiles for environment-specific settings
- Configure timeouts and retry policies
- Implement connection pooling for high-volume operations

### Resource Management
- Monitor memory usage for large CSV operations
- Use streaming operations for large datasets
- Implement proper error handling and cleanup

## Security Considerations

### Authentication Methods
1. **Azure CLI** (`az login`) - Recommended for development
2. **Service Principal** - Recommended for automation
3. **Managed Identity** - Recommended for Azure-hosted automation
4. **Environment Variables** - For containerized environments

### Credential Management
- Store sensitive data in secure credential stores
- Use profile-based configuration for different environments
- Implement proper access controls and audit logging

### Network Security
- Use private endpoints where available
- Implement proper firewall rules
- Consider VPN or ExpressRoute for on-premises connectivity

## Best Practices

### Development
- Use descriptive profile names for different environments
- Validate CSV files before import operations
- Implement proper error handling in scripts
- Use debug mode for troubleshooting

### Production
- Use service principals for automated operations
- Implement monitoring and alerting
- Use batch operations for performance
- Implement proper backup and recovery procedures

### Maintenance
- Regularly update CLI to latest version
- Monitor API usage and rate limits
- Implement log rotation and archival
- Regularly review and update profiles

## API Reference

The CLI provides direct mapping to Microsoft Purview REST APIs:

### Atlas API
- Entity operations → `/api/atlas/v2/entity/*`
- Type operations → `/api/atlas/v2/types/*`
- Lineage operations → `/api/atlas/v2/lineage/*`
- Search operations → `/api/atlas/v2/search/*`

### Account API  
- Collection operations → `/api/account/collections/*`
- Resource operations → `/api/account/resourceSets/*`

### Scanning API
- Data source operations → `/api/scan/datasources/*`
- Scan operations → `/api/scan/scans/*`
- Classification operations → `/api/scan/classificationrules/*`

### Catalog API
- Browse operations → `/api/catalog/browse/*`
- Search operations → `/api/catalog/search/*`

## Version Information

This documentation covers the comprehensive Purview CLI with all major feature groups and advanced capabilities. For the most current information and updates, refer to the official documentation and release notes.

**Generated**: {{GENERATION_TIME}}
**CLI Version**: Latest
**API Coverage**: Complete Microsoft Purview REST API surface
