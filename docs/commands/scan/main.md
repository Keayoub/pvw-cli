# Scan Commands

Configure data sources, set up scanning rules, manage credentials, and run scans against your data landscape in Microsoft Purview.

!!! tip "Quick Start"
    Define data sources, credentials, scan rulesets, filters, triggers, and execute scans to catalog your data assets.

## What You Can Do

- Register and manage data sources
- Store and manage credentials securely in Key Vault
- Create and configure scan rules and rulesets
- Set up scan schedules and triggers
- Apply filters to scan scope
- Execute and monitor scans
- Manage classification rules

## Quick Examples

=== "Register data source"
    ```bash
    pvw scan putdatasource --help
    ```

=== "Create scan"
    ```bash
    pvw scan putscan --help
    ```

=== "Run scan"
    ```bash
    pvw scan runscan --help
    ```

=== "Cancel scan"
    ```bash
    pvw scan cancelscan --help
    ```

## Available Actions

### Data Source Management

| Command | Purpose |
| --- | --- |
| `putdatasource` | Register or update data source |
| `readdatasource` | Get data source details |
| `readdatasources` | List all data sources |
| `deletedatasource` | Remove data source |

### Credential Management

| Command | Purpose |
| --- | --- |
| `putcredential` | Create or update credential |
| `readcredential` | Get credential details |
| `deletecredential` | Remove credential |
| `putkeyvault` | Configure Key Vault |
| `readkeyvault` | Get Key Vault config |
| `readkeyvaults` | List Key Vaults |
| `deletekeyvault` | Remove Key Vault config |

### Scan Configuration

| Command | Purpose |
| --- | --- |
| `putscan` | Create or update scan |
| `readscan` | Get scan details |
| `readscans` | List scans for data source |
| `deletescan` | Remove scan |
| `readscanhistory` | Get scan execution history |

### Scan Rulesets

| Command | Purpose |
| --- | --- |
| `putscanruleset` | Create or update ruleset |
| `readscanruleset` | Get ruleset |
| `readscanrulesets` | List rulesets |
| `deletescanruleset` | Remove ruleset |
| `readsystemscanruleset` | Get system ruleset |
| `readsystemscanrulesets` | List system rulesets |
| `readsystemscanrulesetversion` | Get system ruleset version |
| `readsystemscanrulesetversions` | List system ruleset versions |

### Scan Execution

| Command | Purpose |
| --- | --- |
| `runscan` | Execute scan |
| `cancelscan` | Cancel running scan |

### Classification Rules

| Command | Purpose |
| --- | --- |
| `putclassificationrule` | Create or update rule |
| `readclassificationrule` | Get classification rule |
| `readclassificationrules` | List rules |
| `readclassificationruleversions` | Get rule versions |
| `deleteClassificationRule` | Remove rule |
| `tagclassificationversion` | Tag rule version |

### Filters & Triggers

| Command | Purpose |
| --- | --- |
| `putfilter` | Create or update scan filter |
| `readfilters` | List filters |
| `puttrigger` | Set scan schedule/trigger |
| `readtrigger` | Get trigger config |
| `deletetrigger` | Remove trigger |

## Common Workflows

### Set Up a New Data Source Scan

```bash
# 1. Register data source
pvw scan putdatasource --help

# 2. Create credential (stored in Key Vault)
pvw scan putcredential --help

# 3. Create scan configuration
pvw scan putscan --help

# 4. Set up trigger/schedule
pvw scan puttrigger --help

# 5. Run scan
pvw scan runscan --help
```

### Manage Scan Rulesets

```bash
# Create custom ruleset
pvw scan putscanruleset --help

# List available rulesets
pvw scan readscanrulesets --help

# Get system ruleset for reference
pvw scan readsystemscanruleset --help
```

### Monitor Scans

```bash
# Get scan history
pvw scan readscanhistory --help

# Check current status
pvw scan readscan --help
```

## Related Topics

- [Create Tasks](../task-create.md)
- [Update Tasks](../task-update.md)
- [Delete Tasks](../task-delete.md)
- [Account commands](../account/main.md)
- [Authentication Troubleshooting](../../authentication-troubleshooting.md)
