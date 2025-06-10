# Purview CLI Documentation

Comprehensive documentation for the Purview CLI (`pvw`) tool.

Generated on: 2025-06-08 10:51:35

## Overview

The Purview CLI provides command-line access to Microsoft Purview functionality including:

- Entity management and bulk operations
- Glossary and vocabulary management
- Data lineage analysis and visualization
- Scanning and data source management
- Advanced analytics and insights
- Plugin system for extensibility

## Command Groups

- [entity](./entity/README.md) - 12 commands
- [types](./types/README.md) - 1 commands
- [main](./main/README.md) - Purview CLI with profile management and automation (0 commands)
- [profile](./profile/README.md) - Manage connection profiles (5 commands)
- [config](./config/README.md) - Configuration management (2 commands)
- [validate](./validate/README.md) - Data validation commands (1 commands)
- [lineage_csv](./lineage_csv/README.md) - CSV-based lineage operations (4 commands)
- [glossary](./glossary/README.md) - Glossary management operations (2 commands)
- [scanning](./scanning/README.md) - Advanced scanning operations and automation (2 commands)
- [governance](./governance/README.md) - Business rules and governance operations (2 commands)
- [monitoring](./monitoring/README.md) - Real-time monitoring and alerting (2 commands)
- [lineage](./lineage/README.md) - Advanced lineage analysis and visualization (2 commands)
- [plugins](./plugins/README.md) - Plugin management and operations (3 commands)

## Quick Start

1. **Install the CLI:**
   ```bash
   pip install purviewcli
   ```

2. **Configure authentication:**
   ```bash
   pvw profile add --name production --account-name my-purview-account
   ```

3. **List available commands:**
   ```bash
   pvw --help
   ```

## Additional Resources

- [Comprehensive Reference](./comprehensive_reference.md) - All commands in one place
- [API Mapping](./api_mapping.md) - CLI to REST API mapping
- [Configuration Guide](./configuration.md) - Setup and configuration

## Statistics

- **Total Command Groups:** 15
- **CSV-mapped Commands:** 13
- **CLI-analyzed Commands:** 30
- **Generation Source:** Combined CSV + CLI analysis
