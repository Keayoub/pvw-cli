# Relationship Commands

Manage relationships and connections between entities and metadata objects in your Purview catalog.

!!! tip "Quick Start"
    Create and inspect links between assets using typed relationships. Use `bulk-create-csv` for high-volume relationship ingestion from a spreadsheet.

## What You Can Do

- Read and inspect existing relationships between catalog entities
- Create typed relationships between any two entities
- Bulk-create relationships from a CSV mapping file
- Update relationship properties (status, attributes)
- Delete obsolete or incorrect relationships

## Quick Examples

=== "Read relationship"
    ```bash
    pvw relationship read --guid "3e8f0a1b-2c4d-5e6f-7a8b-9c0d1e2f3a4b"
    ```

=== "Create relationship"
    ```bash
    pvw relationship create --payload-file samples/json/relationship/create.json
    ```

=== "Update relationship"
    ```bash
    pvw relationship put \
      --payload-file samples/json/relationship/update.json
    ```

=== "Delete relationship"
    ```bash
    pvw relationship delete --guid "3e8f0a1b-2c4d-5e6f-7a8b-9c0d1e2f3a4b"
    ```

=== "Bulk create from CSV"
    ```bash
    # Validate first (no changes made)
    pvw relationship bulk-create-csv --csv-file samples/csv/entities_mapping_example.csv --dry-run

    # Live import
    pvw relationship bulk-create-csv --csv-file samples/csv/entities_mapping_example.csv
    ```

## Available Actions

| Command | Purpose |
| --- | --- |
| `create` | Create a new typed relationship between two entities |
| `read` | Get full details of a relationship by GUID |
| `put` | Create or update a relationship |
| `delete` | Remove a relationship by GUID |
| [`bulk-create-csv`](./bulk-create-csv.md) | Bulk-create relationships from a CSV mapping file |

## Relationship CSV Format

Use this column layout for `bulk-create-csv`:

```csv
info_object_guid,target_entity_guid,target_entity_type,relationship_type
<source-entity-guid>,<target-entity-guid>,azure_sql_table,process_dataset_outputs
```

| Column | Required | Description |
| --- | --- | --- |
| `info_object_guid` | ✅ | GUID of the source/origin entity |
| `target_entity_guid` | ✅ | GUID of the destination entity |
| `target_entity_type` | ✅ | Atlas type name of the target (e.g. `azure_sql_table`, `mssql_table`) |
| `relationship_type` | ✅ | Atlas relationship type (e.g. `process_dataset_outputs`, `dataset_process_inputs`) |

Download the sample: [entities_mapping_example.csv](https://github.com/Keayoub/pvw-cli/raw/main/samples/csv/entities_mapping_example.csv)

## Relationship JSON Payload

The `create` and `put` commands accept a JSON payload like this:

```json
{
  "end1": {
    "typeName": "adf_copy_activity",
    "uniqueAttributes": {
      "qualifiedName": "/subscriptions/.../factories/myADF/pipelines/copyPipeline/activities/copyActivity"
    }
  },
  "end2": {
    "typeName": "azure_sql_table",
    "uniqueAttributes": {
      "qualifiedName": "mssql://sqlserver.database.windows.net/mydb/schema/MyTable"
    }
  },
  "status": "ACTIVE",
  "typeName": "process_dataset_outputs"
}
```

Download the template: [relationship/create.json](https://github.com/Keayoub/pvw-cli/raw/main/samples/json/relationship/create.json)

## Relationship Types

Common Atlas relationship types you can use:

| Type Name | Connects |
| --- | --- |
| `process_dataset_outputs` | Process → output dataset |
| `dataset_process_inputs` | Dataset → consuming process |
| `DataSet_LinkedProcess` | Dataset ↔ process |
| `AtlasGlossaryTermAssignment` | Glossary term → entity |

!!! info "Discovering relationship types"
    Run `pvw types readTypeDefs --type-category RELATIONSHIP --output json` to list all relationship types available in your Purview instance.

## Related Topics

- [Entity commands](../entity/main.md) — find entity GUIDs to use in relationships
- [Lineage commands](../lineage/main.md) — higher-level lineage automation
- [Templates & Downloads](../../templates.md) — downloadable CSV and JSON templates
- [Relationship Automation Guide](../../relationship-automation-guide.md) — end-to-end bulk relationship workflows
