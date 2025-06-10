# Comprehensive Command Reference

This document lists all available Purview CLI commands with their syntax and descriptions.

## CSV-Mapped Commands

### entity

#### importBusinessMetadata

**Syntax:** `pvw entity importBusinessMetadata --bmFile=<val>`

**Description:**  Import business metadata in bulk.

**API:** POST https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/businessmetadata/import

#### getBusinessMetadataTemplate

**Syntax:** `pvw entity getBusinessMetadataTemplate`

**Description:** Get a sample template for uploading/creating business metadata in bulk.

**API:** GET https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/businessmetadata/import/template

#### addOrUpdateBusinessMetadata

**Syntax:** `pvw entity addOrUpdateBusinessMetadata --guid=<val> --payloadFile=<val> [--isOverwrite]`

**Description:** Add or update business metadata to an entity.

**API:** POST https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata

#### deleteBusinessMetadata

**Syntax:** `pvw entity deleteBusinessMetadata --guid=<val>`

**Description:** Remove business metadata from an entity.

**API:** DELETE https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata

#### addOrUpdateBusinessAttribute

**Syntax:** `pvw entity addOrUpdateBusinessAttribute --guid=<val> --payloadFile=<val> --bmName=<val>`

**Description:** Add or update business attributes to an entity.

**API:** POST https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata/{bmName}

#### deleteBusinessAttribute

**Syntax:** `pvw entity deleteBusinessAttribute --guid=<val> --bmName=<val>`

**Description:** Delete business metadata from an entity.

**API:** DELETE https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/businessmetadata/{bmName}

#### addLabels

**Syntax:** `pvw entity addLabels --guid=<val> --payloadFile=<val>`

**Description:** Append labels to an entity.

**API:** PUT https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/labels

#### deleteLabels

**Syntax:** `pvw entity deleteLabels --guid=<val>`

**Description:** Delete label(s) from an entity.

**API:** DELETE https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/labels

#### setLabels

**Syntax:** `pvw entity setLabels --guid=<val> --payloadFile=<val>`

**Description:** Overwrite labels for an entity.

**API:** POST https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/guid/{guid}/labels

#### addLabelsByUniqueAttribute

**Syntax:** `pvw entity addLabelsByUniqueAttribute --typeName=<val> --qualifiedName=<val> --payloadFile=<val>`

**Description:** Append labels to an entity identified by its type and unique attributes.

**API:** PUT https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels

#### deleteLabelsByUniqueAttribute

**Syntax:** `pvw entity deleteLabelsByUniqueAttribute --typeName=<val> --qualifiedName=<val>`

**Description:** Delete label(s) from an entity identified by its type and unique attributes.

**API:** DELETE https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels

#### setLabelsByUniqueAttribute

**Syntax:** `pvw entity setLabelsByUniqueAttribute --typeName=<val> --qualifiedName=<val> --payloadFile=<val>`

**Description:** Overwrite labels for an entity identified by its type and unique attributes.

**API:** POST https://{accountName}.purview.azure.com/catalog/api/atlas/v2/entity/uniqueAttribute/type/{typeName}/labels

### types

#### readBusinessMetadataDef

**Syntax:** `pvw types readBusinessMetadataDef (--guid=<val> | --name=<val>)`

**Description:** Get the business metadata definition by GUID or its name (unique).

**API:** GET https://{accountName}.purview.azure.com/catalog/api/atlas/v2/types/businessmetadatadef/name/{name}

## CLI-Analyzed Commands

### profile

Manage connection profiles

#### add

**Syntax:** `pvw profile add --name=<value> --account-name=<value> [--tenant-id=<value>] [--region=<value>] [--batch-size=<value>] [--set-default=<value>]`

**Description:** Add a new connection profile

#### remove

**Syntax:** `pvw profile remove <name>`

**Description:** Remove a connection profile

#### list_profiles

**Syntax:** `pvw profile list_profiles`

**Description:** List all connection profiles

#### set_default

**Syntax:** `pvw profile set_default <name>`

**Description:** Set default profile

#### status

**Syntax:** `pvw profile status`

**Description:** Show current authentication status

### config

Configuration management

#### set

**Syntax:** `pvw config set <key> <value>`

**Description:** Set configuration value

### validate

Data validation commands

#### csv

**Syntax:** `pvw validate csv --csv-file=<value> [--template=<value>] [--output=<value>] [--format=<value>]`

**Description:** Validate CSV file for entity import

### lineage_csv

CSV-based lineage operations

#### process

**Syntax:** `pvw lineage_csv process <csv_file> [--batch-size=<value>] [--validate-entities=<value>] [--create-missing-entities=<value>] [--progress=<value>]`

**Description:** Process lineage relationships from CSV file

#### generate_sample

**Syntax:** `pvw lineage_csv generate_sample <output_file> [--num-samples=<value>] [--template=<value>]`

**Description:** Generate sample CSV file for lineage

#### validate

**Syntax:** `pvw lineage_csv validate <csv_file>`

**Description:** Validate CSV file format for lineage

#### templates

**Syntax:** `pvw lineage_csv templates`

**Description:** Show available CSV lineage templates

### glossary

Glossary management operations

#### import_terms

**Syntax:** `pvw glossary import_terms --csv-file=<value> --glossary-guid=<value>`

**Description:** Import glossary terms from CSV

#### assign_terms

**Syntax:** `pvw glossary assign_terms --csv-file=<value>`

**Description:** Assign glossary terms to entities from CSV

### scanning

Advanced scanning operations and automation

#### run_scan

**Syntax:** `pvw scanning run_scan --data-source=<value> --scan-name=<value> [--wait=<value>] [--output=<value>]`

**Description:** Run a scan and optionally wait for completion

#### generate_report

**Syntax:** `pvw scanning generate_report --output-file=<value> [--include-failed=<value>]`

**Description:** Generate comprehensive scanning report

### governance

Business rules and governance operations

#### check_compliance

**Syntax:** `pvw governance check_compliance --entity-guid=<value> [--rule-types=<value>] [--output=<value>]`

**Description:** Check entity compliance against business rules

#### compliance_report

**Syntax:** `pvw governance compliance_report --output-file=<value> [--entity-type=<value>]`

**Description:** Generate comprehensive compliance report

### monitoring

Real-time monitoring and alerting

#### dashboard

**Syntax:** `pvw monitoring dashboard [--refresh-interval=<value>]`

**Description:** Start real-time monitoring dashboard

#### export_metrics

**Syntax:** `pvw monitoring export_metrics --output-file=<value> [--format=<value>]`

**Description:** Export collected metrics

### lineage

Advanced lineage analysis and visualization

#### analyze

**Syntax:** `pvw lineage analyze --entity-guid=<value> [--direction=<value>] [--depth=<value>] [--output-file=<value>]`

**Description:** Analyze comprehensive lineage for an entity

#### impact

**Syntax:** `pvw lineage impact --entity-guid=<value> [--output-file=<value>]`

**Description:** Perform impact analysis for an entity

### plugins

Plugin management and operations

#### list_plugins

**Syntax:** `pvw plugins list_plugins`

**Description:** List all available plugins

#### info

**Syntax:** `pvw plugins info --plugin-name=<value>`

**Description:** Get detailed information about a plugin

#### execute

**Syntax:** `pvw plugins execute --plugin-name=<value> --operation=<value> [--params=<value>]`

**Description:** Execute a plugin operation

