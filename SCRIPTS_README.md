# PVW CLI v2.0 Scripts and Automation

This directory contains automation scripts and examples for the PVW CLI v2.0 platform.

## Available Scripts

### Core Automation Scripts

- **`automation_examples.py`** - Comprehensive automation examples demonstrating:
  - Bulk entity operations and lineage creation
  - Business rules automation and compliance checking
  - ML-powered data discovery and recommendations
  - Real-time monitoring and alerting setup
  - Advanced lineage visualization and impact analysis
  - Plugin system integration and custom workflows

- **`deploy.py`** - Production deployment automation for:
  - Full-stack PVW CLI deployment (CLI + Web UI + Backend)
  - Docker containerization and orchestration
  - Environment configuration and secret management
  - Database initialization and migration

### Monitoring and Background Processing

- **`celery_workers.py`** - Celery background task workers for:
  - Asynchronous bulk operations processing
  - Real-time monitoring data collection
  - ML model training and inference
  - Business rules execution and compliance checking

- **`celery_workers.bat`** - Windows batch script for starting Celery workers
- **`celery_monitor.py`** - Celery monitoring and management utilities

### Quick Start and Setup

- **`quick-start.ps1`** - PowerShell quick start script for:
  - Environment setup and dependency installation
  - Authentication configuration
  - Initial data catalog setup
  - Sample data and lineage creation

- **`rebuilt-env.ps1`** - Environment rebuild and reset script
- **`verify-stack.ps1`** - Full stack verification and health checks

## Usage Examples

### Running Automation Scripts

```bash
# Run comprehensive automation examples
python scripts/automation_examples.py

# Deploy full stack environment
python scripts/deploy.py --environment production

# Start background workers
python scripts/celery_workers.py
```

### Quick Environment Setup

```powershell
# Quick start (PowerShell)
.\scripts\quick-start.ps1

# Verify installation
.\scripts\verify-stack.ps1
```

### Background Processing

```bash
# Start Celery workers for background processing
celery -A scripts.celery_workers worker --loglevel=info

# Monitor Celery tasks
python scripts/celery_monitor.py
```

## Script Configuration

All scripts use environment variables for configuration:

```bash
# Core PVW CLI Configuration
export PURVIEW_NAME="your-purview-account"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"

# Advanced Features Configuration
export PVW_WEB_UI_PORT="8080"
export PVW_BACKEND_PORT="8000"
export PVW_MONITORING_ENABLED="true"
export PVW_ML_ENABLED="true"
export PVW_BUSINESS_RULES_ENABLED="true"
```

## Integration with CI/CD

The scripts are designed for integration with CI/CD pipelines:

```yaml
# Example GitHub Actions integration
- name: Deploy PVW CLI Environment
  run: python scripts/deploy.py --environment staging

- name: Run Automation Tests
  run: python scripts/automation_examples.py --mode test

- name: Verify Deployment
  run: powershell scripts/verify-stack.ps1
```

## Advanced Features

### Business Rules Automation

- Automated compliance checking and governance
- Policy enforcement and violation detection
- Custom rule creation and management

### ML-Powered Operations

- Intelligent data discovery and cataloging
- Similarity analysis and data recommendations
- Anomaly detection and data quality monitoring

### Real-time Monitoring

- Live metrics collection and dashboard updates
- Performance monitoring and alerting
- Resource usage tracking and optimization

### Plugin System

- Custom plugin development and deployment
- Third-party integrations and extensions
- Workflow automation and orchestration

## Support and Documentation

For detailed documentation on each script and automation capability, see:

- `/doc/ADVANCED_FEATURES.md` - Comprehensive feature documentation
- `/doc/PVW_and_PurviewClient.md` - API and client library documentation
- `/doc/md/guide.md` - Getting started guide and examples

For technical support and feature requests, please refer to the main project documentation.