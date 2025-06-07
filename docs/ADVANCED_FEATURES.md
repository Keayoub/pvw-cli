# Enhanced Purview CLI v2.0 - Advanced Features Documentation

## Table of Contents
1. [Advanced Scanning Operations](#advanced-scanning-operations)
2. [Business Rules Engine](#business-rules-engine)
3. [Real-time Monitoring Dashboard](#real-time-monitoring-dashboard)
4. [Machine Learning Integration](#machine-learning-integration)
5. [Advanced Lineage Visualization](#advanced-lineage-visualization)
6. [Plugin System](#plugin-system)
7. [Testing Framework](#testing-framework)
8. [Performance Optimization](#performance-optimization)

---

## Advanced Scanning Operations

### Overview
The Advanced Scanning Operations module provides enterprise-grade scanning automation with bulk operations, monitoring, and optimization features.

### Key Features
- **Bulk Scan Management**: Execute and monitor multiple scans simultaneously
- **Scan Template System**: Reusable scan configurations for different data sources
- **Progress Monitoring**: Real-time tracking of scan progress and status
- **Automated Reporting**: Generate comprehensive scan reports with insights
- **Optimization Recommendations**: AI-powered suggestions for scan improvements

### CLI Commands

```bash
# Start a new scan
purview-cli scanning start-scan --datasource "my-sql-server" --template "sql-standard"

# Monitor scan progress
purview-cli scanning monitor-scan --scan-id "scan-123"

# Bulk scan operations
purview-cli scanning bulk-scan --datasources-file "datasources.json"

# Generate scan report
purview-cli scanning generate-report --scan-id "scan-123" --format "json"

# Create scan template
purview-cli scanning create-template --name "custom-template" --config "template-config.json"
```

### API Usage

```python
from purviewcli.client.scanning_operations import ScanningManager

# Initialize scanning manager
scanning_manager = ScanningManager(config)

# Start a scan
scan_result = await scanning_manager.start_scan(
    datasource_name="my-datasource",
    template_name="standard-template"
)

# Monitor scan progress
progress = await scanning_manager.monitor_scan_progress(scan_result['scanId'])

# Bulk scan operations
datasources = ["ds1", "ds2", "ds3"]
bulk_results = await scanning_manager.batch_scan_entities(datasources)
```

### Configuration

```json
{
    "scan_templates": {
        "sql-standard": {
            "scan_rule_set": "default",
            "incremental": true,
            "schedule": "daily",
            "filters": {
                "include_patterns": ["*"],
                "exclude_patterns": ["temp_*", "backup_*"]
            }
        }
    },
    "monitoring": {
        "progress_check_interval": 30,
        "timeout_minutes": 120,
        "notification_webhooks": ["https://webhook.example.com"]
    }
}
```

---

## Business Rules Engine

### Overview
The Business Rules Engine provides automated governance policy enforcement with customizable rules, compliance checking, and violation detection.

### Key Features
- **Rule Definition System**: Define custom governance rules using JSON or Python
- **Automated Compliance Checking**: Continuous monitoring of data governance policies
- **Violation Detection**: Identify and report policy violations with severity levels
- **Compliance Scoring**: Calculate governance health scores for entities and collections
- **Remediation Workflows**: Automated and manual remediation options

### Predefined Rules
- **Data Ownership**: Ensures all entities have assigned owners
- **Classification Requirements**: Validates proper data classification
- **Retention Policies**: Enforces data retention requirements
- **Naming Conventions**: Validates entity naming standards
- **Lineage Completeness**: Ensures complete data lineage documentation
- **GDPR Compliance**: Validates GDPR-specific requirements

### CLI Commands

```bash
# Check entity compliance
purview-cli governance check-compliance --entity-guid "entity-123"

# Generate compliance report
purview-cli governance compliance-report --collection "sales-data" --format "html"

# List all violations
purview-cli governance list-violations --severity "high" --type "ownership"

# Apply rule to collection
purview-cli governance apply-rule --rule "data-ownership" --collection "finance"

# Create custom rule
purview-cli governance create-rule --file "custom-rule.json"
```

### API Usage

```python
from purviewcli.client.business_rules import BusinessRulesEngine, ComplianceRule

# Initialize rules engine
rules_engine = BusinessRulesEngine(config)

# Create custom rule
custom_rule = ComplianceRule(
    name="critical_data_ownership",
    description="Critical data must have designated owners",
    rule_type="data_ownership",
    conditions={
        "classification_contains": ["Critical", "Confidential"],
        "required_field": "owner",
        "owner_format": "email"
    },
    severity="high"
)

rules_engine.add_rule(custom_rule)

# Check compliance
compliance_result = rules_engine.check_entity_compliance("entity-guid")

# Generate compliance report
report = rules_engine.generate_compliance_report(
    entity_guids=["guid1", "guid2"],
    include_recommendations=True
)
```

### Rule Definition Format

```json
{
    "name": "data_retention_policy",
    "description": "Enforce data retention policies",
    "rule_type": "retention",
    "severity": "medium",
    "conditions": {
        "classification_contains": ["PII"],
        "max_retention_days": 2555,
        "required_fields": ["retentionPolicy", "dataRetentionDate"]
    },
    "actions": {
        "violation": "flag_for_review",
        "remediation": "apply_retention_tag"
    }
}
```

---

## Real-time Monitoring Dashboard

### Overview
The Real-time Monitoring Dashboard provides comprehensive visibility into Purview operations with live metrics, alerting, and performance monitoring.

### Key Features
- **Live Metrics Collection**: Real-time data on scans, entities, and API performance
- **Customizable Dashboards**: Rich console-based dashboards with charts and tables
- **Alert Management**: Configurable thresholds with notification systems
- **Performance Monitoring**: Track API response times and system health
- **Automated Reporting**: Daily, weekly, and monthly reports

### Monitored Metrics
- **Scan Metrics**: Active scans, success rates, failure analysis
- **Entity Metrics**: Total entities, growth trends, classification coverage
- **API Performance**: Response times, error rates, throughput
- **Governance Health**: Compliance scores, rule violations, lineage completeness
- **System Resources**: Memory usage, CPU utilization, storage consumption

### CLI Commands

```bash
# Start live dashboard
purview-cli monitoring dashboard --refresh-interval 30

# Export current metrics
purview-cli monitoring export-metrics --format "json" --output "metrics.json"

# Configure alerts
purview-cli monitoring setup-alerts --config "alerts.json"

# Generate daily report
purview-cli monitoring daily-report --date "2024-01-15" --email "admin@company.com"

# Check system health
purview-cli monitoring health-check --verbose
```

### API Usage

```python
from purviewcli.client.monitoring_dashboard import MonitoringDashboard, AlertManager

# Initialize monitoring
dashboard = MonitoringDashboard(config)
alert_manager = AlertManager()

# Set up alerts
alert_manager.add_threshold("scan_failure_rate", max_value=0.1, severity="high")
alert_manager.add_threshold("api_response_time", max_value=2.0, severity="medium")

# Collect current metrics
metrics = dashboard.collect_metrics()

# Start live dashboard
dashboard.start_live_dashboard(refresh_interval=30)

# Generate report
report = dashboard.generate_daily_report(
    date="2024-01-15",
    include_charts=True,
    export_format="html"
)
```

### Dashboard Configuration

```json
{
    "dashboard": {
        "refresh_interval": 30,
        "panels": [
            {
                "name": "Scan Status",
                "type": "table",
                "metrics": ["active_scans", "completed_scans", "failed_scans"]
            },
            {
                "name": "Entity Growth",
                "type": "chart",
                "metrics": ["total_entities"],
                "time_range": "24h"
            }
        ]
    },
    "alerts": {
        "notification_channels": [
            {
                "type": "email",
                "recipients": ["admin@company.com"],
                "severity_threshold": "medium"
            },
            {
                "type": "webhook",
                "url": "https://hooks.slack.com/...",
                "severity_threshold": "high"
            }
        ]
    }
}
```

---

## Machine Learning Integration

### Overview
The ML Integration module brings intelligent automation to data governance through similarity analysis, anomaly detection, and predictive analytics.

### Key Components

#### 1. Intelligent Data Discovery
- **Entity Similarity Analysis**: Find similar entities based on schema, metadata, and usage patterns
- **Pattern Recognition**: Identify common data patterns and structures
- **Anomaly Detection**: Detect unusual entities or data patterns
- **Classification Prediction**: ML-powered data classification suggestions

#### 2. Recommendation Engine
- **Governance Recommendations**: Automated suggestions for data governance improvements
- **Optimization Advice**: Performance and efficiency recommendations
- **Policy Suggestions**: Recommended governance policies based on data analysis

#### 3. Predictive Analytics
- **Scan Failure Prediction**: Predict potential scan failures before they occur
- **Resource Usage Forecasting**: Predict resource requirements for operations
- **Compliance Risk Assessment**: Identify entities at risk of policy violations

### CLI Commands

```bash
# Find similar entities
purview-cli ml find-similar --entity-guid "entity-123" --threshold 0.8

# Detect anomalies
purview-cli ml detect-anomalies --collection "sales-data" --algorithm "isolation-forest"

# Generate recommendations
purview-cli ml recommendations --scope "governance" --entity-guid "entity-123"

# Predict scan failures
purview-cli ml predict-failures --datasource "sql-server" --timeframe "7d"

# Train classification model
purview-cli ml train-classifier --training-data "labeled-entities.json"
```

### API Usage

```python
from purviewcli.client.ml_integration import (
    IntelligentDataDiscovery, 
    MLRecommendationEngine, 
    PredictiveAnalytics
)

# Initialize ML components
data_discovery = IntelligentDataDiscovery(config)
recommendation_engine = MLRecommendationEngine(config)
predictive_analytics = PredictiveAnalytics(config)

# Find similar entities
similarity_results = data_discovery.find_similar_entities(
    entity_guid="target-entity",
    similarity_threshold=0.8,
    max_results=10
)

# Detect anomalies
anomalies = data_discovery.detect_anomalies(
    entity_guids=["entity1", "entity2", "entity3"],
    algorithm="isolation_forest"
)

# Generate recommendations
recommendations = recommendation_engine.generate_recommendations(
    entity_guids=["entity1", "entity2"],
    recommendation_types=["classification", "ownership", "retention"]
)

# Predict scan failures
failure_predictions = predictive_analytics.predict_scan_failures(
    datasource_name="my-datasource",
    prediction_window_days=7
)
```

### ML Model Configuration

```json
{
    "similarity_analysis": {
        "algorithm": "cosine_similarity",
        "features": [
            "schema_similarity",
            "name_similarity", 
            "metadata_similarity",
            "usage_patterns"
        ],
        "weights": {
            "schema_similarity": 0.4,
            "name_similarity": 0.3,
            "metadata_similarity": 0.2,
            "usage_patterns": 0.1
        }
    },
    "anomaly_detection": {
        "algorithm": "isolation_forest",
        "contamination": 0.1,
        "features": [
            "entity_size",
            "column_count",
            "data_types",
            "null_percentage"
        ]
    },
    "classification_prediction": {
        "model_type": "random_forest",
        "training_data_path": "models/classification_training.json",
        "confidence_threshold": 0.7
    }
}
```

---

## Advanced Lineage Visualization

### Overview
Advanced Lineage Visualization provides deep analysis of data lineage with impact assessment, gap detection, and interactive visualization capabilities.

### Key Features
- **Deep Lineage Analysis**: Traverse complex lineage graphs with unlimited depth
- **Impact Assessment**: Understand downstream effects of data changes
- **Critical Path Identification**: Find critical data flows and dependencies
- **Gap Detection**: Identify missing or incomplete lineage information
- **Rich Visualization**: Console-based trees, tables, and export capabilities

### Analysis Types

#### 1. Lineage Impact Analysis
- Analyze upstream and downstream dependencies
- Calculate impact scores and risk levels
- Identify critical paths and bottlenecks
- Generate impact reports with recommendations

#### 2. Lineage Gap Detection
- Find entities with missing lineage information
- Identify incomplete lineage chains
- Suggest lineage completion strategies
- Validate lineage data quality

#### 3. Relationship Inference
- Infer potential relationships based on data patterns
- Suggest missing lineage connections
- Validate existing relationships
- Recommend lineage improvements

### CLI Commands

```bash
# Analyze lineage impact
purview-cli lineage analyze-impact --entity-guid "entity-123" --depth 5

# Detect lineage gaps
purview-cli lineage detect-gaps --collection "sales-data" --report-format "html"

# Visualize lineage tree
purview-cli lineage visualize --entity-guid "entity-123" --direction "both" --max-depth 3

# Export lineage graph
purview-cli lineage export --entity-guid "entity-123" --format "graphml" --output "lineage.xml"

# Infer relationships
purview-cli lineage infer-relationships --entity-guids "entity1,entity2,entity3"
```

### API Usage

```python
from purviewcli.client.lineage_visualization import AdvancedLineageAnalyzer

# Initialize lineage analyzer
lineage_analyzer = AdvancedLineageAnalyzer(config)

# Analyze lineage impact
impact_analysis = lineage_analyzer.analyze_lineage_impact(
    entity_guid="target-entity",
    max_depth=5,
    include_risk_assessment=True
)

# Detect lineage gaps
gap_analysis = lineage_analyzer.detect_lineage_gaps(
    entity_guids=["entity1", "entity2", "entity3"],
    gap_types=["missing_upstream", "missing_downstream", "incomplete_chains"]
)

# Visualize lineage
lineage_tree = lineage_analyzer.visualize_lineage_tree(
    entity_guid="target-entity",
    direction="both",  # upstream, downstream, or both
    max_depth=3,
    show_attributes=True
)

# Export lineage graph
export_result = lineage_analyzer.export_lineage_graph(
    entity_guid="target-entity",
    export_format="graphml",  # graphml, json, csv
    include_metadata=True
)
```

### Impact Analysis Output

```json
{
    "entity_guid": "target-entity",
    "impact_analysis": {
        "impact_score": 0.85,
        "risk_level": "high",
        "affected_entities": 23,
        "critical_path": true,
        "upstream_entities": [
            {
                "guid": "upstream-1",
                "distance": 1,
                "relationship_type": "DataFlow",
                "impact_contribution": 0.4
            }
        ],
        "downstream_entities": [
            {
                "guid": "downstream-1", 
                "distance": 2,
                "relationship_type": "Derives",
                "impact_contribution": 0.6
            }
        ],
        "recommendations": [
            "Monitor downstream entity 'critical-report' closely",
            "Ensure data quality checks before modifications",
            "Consider impact testing for changes"
        ]
    }
}
```

---

## Plugin System

### Overview
The Plugin System provides an extensible architecture for adding custom functionality to the Enhanced Purview CLI through third-party plugins and extensions.

### Plugin Types

#### 1. Data Source Plugins
- Custom data source connectors
- Specialized scanning logic
- Authentication handlers
- Metadata extractors

#### 2. Classification Plugins
- Custom classification algorithms
- Domain-specific classifiers
- Machine learning models
- Rule-based classifiers

#### 3. Export Plugins
- Custom export formats
- Integration with external systems
- Data transformation pipelines
- Reporting engines

#### 4. Notification Plugins
- Custom notification channels
- Integration with messaging systems
- Alert formatters
- Escalation handlers

### Plugin Development

#### Base Plugin Structure

```python
from purviewcli.plugins.plugin_system import BasePlugin

class MyCustomPlugin(BasePlugin):
    name = "my_custom_plugin"
    version = "1.0.0"
    description = "Custom plugin for specific functionality"
    
    def execute(self, **kwargs):
        """Main plugin execution logic"""
        # Your custom logic here
        return {
            "status": "success",
            "result": "Plugin executed successfully",
            "data": {}
        }
    
    def validate_config(self, config):
        """Validate plugin configuration"""
        required_fields = ["api_key", "endpoint"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")
        return True
```

#### Data Source Plugin Example

```python
from purviewcli.plugins.plugin_system import DataSourcePlugin

class CustomDatabasePlugin(DataSourcePlugin):
    name = "custom_database_connector"
    version = "1.0.0"
    supported_types = ["custom_db"]
    
    def connect(self, connection_config):
        """Establish connection to data source"""
        # Custom connection logic
        pass
    
    def scan(self, scan_config):
        """Perform scan of data source"""
        # Custom scanning logic
        pass
    
    def extract_metadata(self, entity):
        """Extract metadata from entity"""
        # Custom metadata extraction
        pass
```

### CLI Commands

```bash
# List available plugins
purview-cli plugins list --category "datasource"

# Install plugin
purview-cli plugins install --plugin "custom-plugin.zip"

# Execute plugin
purview-cli plugins execute --name "my_plugin" --config "plugin-config.json"

# Plugin information
purview-cli plugins info --name "my_plugin"

# Uninstall plugin
purview-cli plugins uninstall --name "my_plugin"
```

### API Usage

```python
from purviewcli.plugins.plugin_system import PluginManager

# Initialize plugin manager
plugin_manager = PluginManager()

# Load plugin from file
plugin_manager.load_plugin_from_file("path/to/plugin.py")

# Register plugin instance
plugin_manager.register_plugin(MyCustomPlugin())

# Execute plugin
result = plugin_manager.execute_plugin(
    plugin_name="my_plugin",
    config={"api_key": "key123"},
    parameters={"action": "process_data"}
)

# List available plugins
available_plugins = plugin_manager.list_plugins()

# Get plugin information
plugin_info = plugin_manager.get_plugin_info("my_plugin")
```

### Plugin Configuration

```json
{
    "plugin_config": {
        "my_custom_plugin": {
            "enabled": true,
            "config": {
                "api_key": "your-api-key",
                "endpoint": "https://api.example.com",
                "timeout": 30
            },
            "execution": {
                "max_retries": 3,
                "timeout_seconds": 120,
                "async": false
            }
        }
    },
    "plugin_discovery": {
        "directories": [
            "./plugins",
            "/usr/local/share/purview-cli/plugins"
        ],
        "auto_load": true,
        "validate_signatures": true
    }
}
```

---

## Testing Framework

### Overview
Comprehensive testing framework with unit tests, integration tests, and performance tests for all Enhanced Purview CLI components.

### Test Categories

#### 1. Unit Tests
- Individual module functionality
- API client testing
- Data validation testing
- Configuration management

#### 2. Integration Tests  
- Module integration workflows
- End-to-end data governance scenarios
- CLI command testing
- Configuration consistency

#### 3. Performance Tests
- Load testing under high volume
- Memory usage analysis
- Concurrent operation testing
- Response time benchmarking

### Running Tests

```bash
# Run all tests
python tests/run_all_tests.py

# Run specific test suite
python tests/test_advanced_modules.py
python tests/test_integration.py
python tests/test_performance.py

# Run existing core tests
python test_functionality.py
python test_csv_functionality.py
```

### Test Configuration

```json
{
    "test_config": {
        "mock_purview_endpoint": "https://test-purview.purview.azure.com",
        "test_data_directory": "./tests/data",
        "performance_thresholds": {
            "max_response_time": 2.0,
            "max_memory_usage": 500,
            "min_success_rate": 0.95
        },
        "integration_test_timeout": 300,
        "load_test_duration": 60
    }
}
```

---

## Performance Optimization

### Overview
Performance optimization guidelines and best practices for Enhanced Purview CLI in production environments.

### Optimization Areas

#### 1. API Performance
- Connection pooling and reuse
- Request batching and pagination
- Caching frequently accessed data
- Async operations for concurrent requests

#### 2. Memory Management
- Streaming large datasets
- Garbage collection optimization
- Memory-efficient data structures
- Resource cleanup and disposal

#### 3. Scan Optimization
- Incremental scanning strategies
- Parallel scan execution
- Smart filtering and exclusions
- Resource throttling

#### 4. Monitoring Efficiency
- Metric aggregation and sampling
- Dashboard refresh optimization
- Alert batching and deduplication
- Report generation scheduling

### Configuration Recommendations

```json
{
    "performance_config": {
        "api_client": {
            "connection_pool_size": 20,
            "timeout_seconds": 30,
            "retry_attempts": 3,
            "batch_size": 100
        },
        "scanning": {
            "parallel_scans": 5,
            "chunk_size": 1000,
            "incremental_enabled": true,
            "progress_update_interval": 10
        },
        "monitoring": {
            "metrics_cache_ttl": 60,
            "dashboard_refresh_rate": 30,
            "alert_batch_size": 10,
            "report_generation_schedule": "0 2 * * *"
        },
        "ml_processing": {
            "similarity_batch_size": 50,
            "model_cache_size": 5,
            "feature_extraction_parallel": true,
            "prediction_threshold": 0.7
        }
    }
}
```

### Best Practices

1. **Use Async Operations**: Leverage async/await for I/O-bound operations
2. **Implement Caching**: Cache frequently accessed metadata and configuration
3. **Batch Processing**: Group operations to reduce API calls
4. **Resource Monitoring**: Monitor memory and CPU usage in production
5. **Optimize Queries**: Use filters and pagination for large result sets
6. **Connection Management**: Properly manage and reuse connections
7. **Error Handling**: Implement proper retry logic and circuit breakers

---

## Conclusion

The Enhanced Purview CLI v2.0 advanced features provide a comprehensive data governance automation platform with enterprise-grade capabilities. The modular architecture ensures scalability and extensibility while maintaining high performance and reliability.

For additional support and documentation, refer to:
- [API Reference](./api_reference.md)
- [Configuration Guide](./configuration_guide.md)
- [Troubleshooting Guide](./troubleshooting.md)
- [Migration Guide](./migration_guide.md)
