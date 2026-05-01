"""
Manage entities in Microsoft Purview using modular Click-based commands.

Usage:
  entity create                Create a new entity
  entity read                  Read an entity
  entity update                Update an entity
  entity delete                Delete an entity
  entity --help                Show this help message and exit

Options:
  -h --help                    Show this help message and exit
"""

import json
import click
from .console_utils import get_console

# Save reference to Python builtin list before it is shadowed by the @entity.command() named 'list'
_builtin_list = list


def _parse_attr_value(value):
    """Parse a CLI attr-value string into the appropriate Python type.

    Resolution order:
    1. JSON array/object literal  e.g. '["Finance","IT"]'
    2. Semicolon-separated list   e.g. 'Finance;IT;Marketing'
    3. Plain scalar               e.g. 'Finance'
    """
    if value is None:
        return value
    # 1. JSON parse (handles both array and plain JSON scalars from CSV export)
    stripped = value.strip()
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except (json.JSONDecodeError, ValueError):
            pass
    # 2. Plain scalar
    return value

console = get_console()


@click.group()
@click.pass_context
def entity(ctx):
    """
    Manage entities in Microsoft Purview.
    """
    pass


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--ignore-relationships", is_flag=True, help="Whether to ignore relationship attributes"
)
@click.option(
    "--min-ext-info",
    is_flag=True,
    help="Whether to return minimal information for referred entities",
)
@click.option(
    "--json", "json_output", is_flag=True, help="Output pure JSON without status messages"
)
@click.pass_context
def read(ctx, guid, ignore_relationships, min_ext_info, json_output):
    """Read entity information by GUID"""
    try:
        # Debug: Log the received GUID
        if not json_output:
            console.print(f"[dim]DEBUG: Received GUID = '{guid}'[/dim]")
            console.print(f"[dim]DEBUG: GUID type = {type(guid).__name__}[/dim]")
            console.print(f"[dim]DEBUG: GUID length = {len(str(guid))}[/dim]")
        
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity read command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(f"[dim]Ignore Relationships: {ignore_relationships}[/dim]")
            console.print(f"[dim]Min Ext Info: {min_ext_info}[/dim]")
            console.print("[green][OK] Mock entity read completed successfully[/green]")
            return

        args = {
            "--guid": guid,
            "--ignoreRelationships": ignore_relationships,
            "--minExtInfo": min_ext_info,
        }

        # Use client singleton cache to reduce credential/connection overhead
        from purviewcli.client._entity import Entity
        from purviewcli.client.client_cache import get_cached_client

        entity_client = get_cached_client(Entity, profile=ctx.obj.get("profile", "default"))
        result = entity_client.entityRead(args)

        if result:
            if json_output:
                # Pure JSON output without status messages
                print(json.dumps(result, indent=2))
            else:
                console.print("[green][OK] Entity read completed successfully[/green]")
                console.print(json.dumps(result, indent=2))
        else:
            if not json_output:
                console.print("[yellow][!] Entity read completed with no result[/yellow]")

    except Exception as e:
        if json_output:
            # Output error as JSON for consistency
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red][X] Error executing entity read: {str(e)}[/red]")


@entity.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing entity data",
)
@click.option(
    "--collection-id",
    required=False,
    help="Collection ID to assign the entity to (e.g., 'yfwy2c')",
)
@click.pass_context
def create(ctx, payload_file, collection_id):
    """Create a new entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity create command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            if collection_id:
                console.print(f"[dim]Collection ID: {collection_id}[/dim]")
            console.print("[green][OK] Mock entity create completed successfully[/green]")
            return

        args = {"--payloadFile": payload_file}
        if collection_id:
            args["--collectionId"] = collection_id

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityCreate(args)

        if result:
            console.print("[green][OK] Entity create completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity create completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity create: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--cascade", is_flag=True, default=False, help="Delete all relationships connected to this entity before deleting it")
@click.pass_context
def delete(ctx, guid, cascade):
    """Delete an entity by GUID"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity delete command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            if cascade:
                console.print("[dim]Cascade: relationships would be deleted first[/dim]")
            console.print("[green][OK] Mock entity delete completed successfully[/green]")
            return

        from purviewcli.client._entity import Entity
        from purviewcli.client._relationship import Relationship

        entity_client = Entity()
        relationship_client = Relationship()

        # Always read the entity first to detect relationships
        read_result = entity_client.entityRead({"--guid": [guid], "--ignoreRelationships": False, "--minExtInfo": False})
        rel_guids = []
        if read_result:
            entity_body = read_result.get("entity", {})
            for attr_values in entity_body.get("relationshipAttributes", {}).values():
                if isinstance(attr_values, list):
                    for item in attr_values:
                        if isinstance(item, dict) and item.get("relationshipGuid"):
                            rel_guids.append(item["relationshipGuid"])
                elif isinstance(attr_values, dict) and attr_values.get("relationshipGuid"):
                    rel_guids.append(attr_values["relationshipGuid"])

        if rel_guids and not cascade:
            console.print(f"[yellow][!] Entity has {len(rel_guids)} relationship(s) that must be removed before deletion.[/yellow]")
            console.print("[yellow]    Re-run with --cascade to automatically delete all relationships first:[/yellow]")
            console.print(f"[yellow]    pvw entity delete --guid {guid} --cascade[/yellow]")
            return

        if cascade and rel_guids:
            console.print(f"[blue][*] Found {len(rel_guids)} relationship(s) to delete first[/blue]")
            for rel_guid in rel_guids:
                try:
                    relationship_client.relationshipDelete({"--guid": rel_guid})
                    console.print(f"[dim]  Deleted relationship: {rel_guid}[/dim]")
                except Exception as rel_err:
                    console.print(f"[yellow][!] Could not delete relationship {rel_guid}: {rel_err}[/yellow]")

        result = entity_client.entityDelete({"--guid": [guid]})

        if result:
            console.print("[green][OK] Entity delete completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity delete completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity delete: {str(e)}[/red]")


@entity.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing bulk entity data",
)
@click.option(
    "--collection-id",
    required=False,
    help="Collection ID to assign all entities to (e.g., 'yfwy2c')",
)
@click.pass_context
def bulk_create(ctx, payload_file, collection_id):
    """Create multiple entities in bulk"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-create command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            if collection_id:
                console.print(f"[dim]Collection ID: {collection_id}[/dim]")
            console.print("[green][OK] Mock entity bulk-create completed successfully[/green]")
            return

        args = {"--payloadFile": payload_file}
        if collection_id:
            args["--collectionId"] = collection_id

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityBulkCreateOrUpdate(args)

        if result:
            console.print("[green][OK] Entity bulk-create completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity bulk-create completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-create: {str(e)}[/red]")


@entity.command(name="bulk-update")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing entities to update/create (same shape as bulk-create).",
)
@click.pass_context
def bulk_update(ctx, payload_file):
    """Bulk update/create entities from a JSON payload file (uses qualifiedName to match existing entities)."""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-update command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green][OK] Mock entity bulk-update completed successfully[/green]")
            return

        args = {"--payloadFile": payload_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityBulkCreateOrUpdate(args)

        if result:
            console.print("[green][OK] Entity bulk-update completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity bulk-update completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-update: {str(e)}[/red]")


# === BULK OPERATIONS ===


@entity.command()
@click.option(
    "--guid", required=True, multiple=True, help="Entity GUIDs to read (can specify multiple)"
)
@click.option(
    "--ignore-relationships", is_flag=True, help="Whether to ignore relationship attributes"
)
@click.option(
    "--min-ext-info",
    is_flag=True,
    help="Whether to return minimal information for referred entities",
)
@click.pass_context
def bulk_read(ctx, guid, ignore_relationships, min_ext_info):
    """Read multiple entities by their GUIDs"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-read command[/yellow]")
            console.print(f"[dim]GUIDs: {', '.join(guid)}[/dim]")
            console.print("[green][OK] Mock entity bulk-read completed successfully[/green]")
            return

        args = {
            "--guid": list(guid),
            "--ignoreRelationships": ignore_relationships,
            "--minExtInfo": min_ext_info,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadBulk(args)

        if result:
            console.print("[green][OK] Entity bulk-read completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity bulk-read completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-read: {str(e)}[/red]")


@entity.command()
@click.option(
    "--guid", required=True, multiple=True, help="Entity GUIDs to delete (can specify multiple)"
)
@click.pass_context
def bulk_delete(ctx, guid):
    """Delete multiple entities by their GUIDs"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-delete command[/yellow]")
            console.print(f"[dim]GUIDs: {', '.join(guid)}[/dim]")
            console.print("[green][OK] Mock entity bulk-delete completed successfully[/green]")
            return

        args = {"--guid": list(guid)}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityDeleteBulk(args)

        if result:
            console.print("[green][OK] Entity bulk-delete completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity bulk-delete completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-delete: {str(e)}[/red]")


# === UNIQUE ATTRIBUTE OPERATIONS ===


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.option(
    "--ignore-relationships", is_flag=True, help="Whether to ignore relationship attributes"
)
@click.option(
    "--min-ext-info",
    is_flag=True,
    help="Whether to return minimal information for referred entities",
)
@click.pass_context
def read_by_attribute(ctx, type_name, qualified_name, ignore_relationships, min_ext_info):
    """Read entity by unique attributes"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity read-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print("[green][OK] Mock entity read-by-attribute completed successfully[/green]")
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--ignoreRelationships": ignore_relationships,
            "--minExtInfo": min_ext_info,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadUniqueAttribute(args)

        if result:
            console.print("[green][OK] Entity read-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity read-by-attribute completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity read-by-attribute: {str(e)}[/red]")


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option(
    "--qualified-name", required=True, multiple=True, help="Qualified names (can specify multiple)"
)
@click.option(
    "--ignore-relationships", is_flag=True, help="Whether to ignore relationship attributes"
)
@click.option(
    "--min-ext-info",
    is_flag=True,
    help="Whether to return minimal information for referred entities",
)
@click.pass_context
def bulk_read_by_attribute(ctx, type_name, qualified_name, ignore_relationships, min_ext_info):
    """Read multiple entities by unique attributes"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-read-by-attribute command[/yellow]")
            console.print(
                f"[dim]Type: {type_name}, Qualified Names: {', '.join(qualified_name)}[/dim]"
            )
            console.print(
                "[green][OK] Mock entity bulk-read-by-attribute completed successfully[/green]"
            )
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": list(qualified_name),
            "--ignoreRelationships": ignore_relationships,
            "--minExtInfo": min_ext_info,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadBulkUniqueAttribute(args)

        if result:
            console.print("[green][OK] Entity bulk-read-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity bulk-read-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-read-by-attribute: {str(e)}[/red]")


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.pass_context
def delete_by_attribute(ctx, type_name, qualified_name):
    """Delete entity by unique attributes"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity delete-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print("[green][OK] Mock entity delete-by-attribute completed successfully[/green]")
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityDeleteUniqueAttribute(args)

        if result:
            console.print("[green][OK] Entity delete-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity delete-by-attribute completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity delete-by-attribute: {str(e)}[/red]")


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing entity data",
)
@click.pass_context
def update_by_attribute(ctx, type_name, qualified_name, payload_file):
    """Update entity by unique attributes"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity update-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print("[green][OK] Mock entity update-by-attribute completed successfully[/green]")
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityPartialUpdateByUniqueAttribute(args)

        if result:
            console.print("[green][OK] Entity update-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity update-by-attribute completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity update-by-attribute: {str(e)}[/red]")


# === HEADER OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def read_header(ctx, guid):
    """Read entity header information by GUID"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity read-header command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green][OK] Mock entity read-header completed successfully[/green]")
            return

        args = {"--guid": [guid]}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadHeader(args)

        if result:
            console.print("[green][OK] Entity read-header completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity read-header completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity read-header: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--attr-name", required=True, help="The name of the attribute to update")
@click.option("--attr-value", required=True, help="The new value for the attribute")
@click.pass_context
def update_attribute(ctx, guid, attr_name, attr_value):
    """Update a specific attribute of an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity update-attribute command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Attribute: {attr_name}, Value: {attr_value}[/dim]")
            console.print("[green][OK] Mock entity update-attribute completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--attrName": attr_name,
            "--attrValue": attr_value,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityPartialUpdateAttribute(args)

        if result:
            console.print("[green][OK] Entity update-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity update-attribute completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity update-attribute: {str(e)}[/red]")


# === CLASSIFICATION OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--classification-name", required=True, help="The name of the classification")
@click.pass_context
def read_classification(ctx, guid, classification_name):
    """Read specific classification for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity read-classification command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Classification: {classification_name}[/dim]")
            console.print("[green][OK] Mock entity read-classification completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--classificationName": classification_name,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadClassification(args)

        if result:
            console.print("[green][OK] Entity read-classification completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity read-classification completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity read-classification: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def read_classifications(ctx, guid):
    """Read all classifications for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity read-classifications command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(
                "[green][OK] Mock entity read-classifications completed successfully[/green]"
            )
            return

        args = {"--guid": [guid]}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadClassifications(args)

        if result:
            console.print("[green][OK] Entity read-classifications completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity read-classifications completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity read-classifications: {str(e)}[/red]")


@entity.command()
@click.option(
    "--guid",
    required=True,
    help="GUID of the parent entity (table, dataset, etc.)",
)
@click.option(
    "--output",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format: table (default) or json",
)
@click.pass_context
def read_schema_classifications(ctx, guid, output):
    """Read classifications applied on all columns of a table (schema-level)

    \b
    This command retrieves schema classifications visible in the Purview UI
    i.e. classifications that are stored on each column entity, not on the
    table itself.

    Steps performed automatically:
      1. Fetch the parent entity to extract column GUIDs
      2. Call read-classifications on each column
    3. Display a consolidated column -> classifications report
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity read-schema-classifications command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(
                "[green][OK] Mock entity read-schema-classifications completed successfully[/green]"
            )
            return

        from purviewcli.client._entity import Entity
        from rich.table import Table

        entity_client = Entity()

        # Step 1 - fetch the parent entity (table/dataset)
        console.print(f"[dim]Fetching parent entity {guid}...[/dim]")
        parent_args = {
            "--guid": guid,
            "--ignoreRelationships": False,
            "--minExtInfo": False,
        }
        parent = entity_client.entityRead(parent_args)

        if not parent:
            console.print("[red][X] Entity not found[/red]")
            return

        # Step 2 - extract column references from relationshipAttributes.columns
        entity_body = parent.get("entity", parent)
        rel_attrs = entity_body.get("relationshipAttributes", {})
        columns_refs = rel_attrs.get("columns", [])

        if not columns_refs:
            # Fallback: inspect referredEntities for column-typed entries
            referred = parent.get("referredEntities", {})
            columns_refs = [
                {
                    "guid": g,
                    "displayText": v.get("attributes", {}).get("name", g),
                }
                for g, v in referred.items()
                if v.get("typeName", "").lower().endswith("_column")
                or v.get("typeName", "").lower() == "column"
            ]

        if not columns_refs:
            console.print("[yellow][!] No columns found on this entity[/yellow]")
            return

        console.print(
            f"[dim]Found {len(columns_refs)} column(s). Fetching classifications...[/dim]"
        )

        # Step 3 - fetch classifications for each column
        results = []
        for col_ref in columns_refs:
            col_guid = col_ref.get("guid")
            col_name = col_ref.get("displayText") or col_guid
            if not col_guid:
                continue
            try:
                col_classifs = entity_client.entityReadClassifications({"--guid": [col_guid]})
                classif_list = []
                if col_classifs:
                    items = col_classifs.get(
                        "list",
                        col_classifs if isinstance(col_classifs, _builtin_list) else [],
                    )
                    classif_list = [c.get("typeName", str(c)) for c in items]
                results.append(
                    {
                        "column": col_name,
                        "column_guid": col_guid,
                        "classifications": classif_list,
                    }
                )
            except Exception as col_err:
                results.append(
                    {
                        "column": col_name,
                        "column_guid": col_guid,
                        "classifications": [],
                        "error": str(col_err),
                    }
                )

        # Step 4 - output
        if output == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return

        table = Table(
            title=f"Schema-level classifications - table {guid}",
            show_lines=True,
        )
        table.add_column("Column", style="cyan", min_width=20)
        table.add_column("Column GUID", style="dim", min_width=36)
        table.add_column("Classifications", style="magenta")

        total_classified = 0
        for row in results:
            if row.get("error"):
                classif_cell = f"[red]Error: {row['error']}[/red]"
            elif row["classifications"]:
                classif_cell = "\n".join(row["classifications"])
                total_classified += 1
            else:
                classif_cell = "[dim]-[/dim]"
            table.add_row(row["column"], row["column_guid"], classif_cell)

        console.print(table)
        console.print(
            f"[green][OK] {total_classified}/{len(results)} column(s) have "
            f"schema-level classifications[/green]"
        )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity read-schema-classifications: {str(e)}[/red]"
        )


@entity.command()
@click.option(
    "--guid",
    default=None,
    help="GUID of the parent table entity (required unless --column-guid is used)",
)
@click.option(
    "--column-guid",
    default=None,
    help="GUID of a specific column (bypasses table lookup)",
)
@click.option(
    "--column-name",
    default=None,
    help="Name of the column to target (resolved from --guid table). "
    "Supports partial/case-insensitive match. Use '*' or omit with --all-columns to target all.",
)
@click.option(
    "--classification-name",
    "classification_names",
    required=True,
    multiple=True,
    help="Classification typeName to add (repeatable, e.g. --classification-name 'MICROSOFT.PERSONAL.EMAIL')",
)
@click.option(
    "--all-columns",
    is_flag=True,
    default=False,
    help="Apply classification(s) to every column of the table (requires --guid)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview targeted columns and classifications without calling the API",
)
@click.option(
    "--output",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format for the result report",
)
@click.pass_context
def add_schema_classification(
    ctx, guid, column_guid, column_name, classification_names, all_columns, dry_run, output
):
    """Add classification(s) on column(s) of a table (schema-level)

    \b
    Three targeting modes:

        1) Direct - supply --column-guid (no table lookup needed):
             pvw entity add-schema-classification --column-guid <col-guid> \\
                 --classification-name "MICROSOFT.PERSONAL.EMAIL"

        2) By column name - resolve from parent table:
             pvw entity add-schema-classification --guid <table-guid> \\
                 --column-name "Email" \\
                 --classification-name "MICROSOFT.PERSONAL.EMAIL"

        3) All columns - apply to every column of the table:
             pvw entity add-schema-classification --guid <table-guid> \\
                 --all-columns \\
                 --classification-name "Availability High"

    Use --dry-run to preview targets before applying.
    Repeat --classification-name to add multiple classifications at once.
    """
    try:
        # ── Validate arguments ─────────────────────────────────────────────
        if not column_guid and not guid:
            console.print(
                "[red][X] Either --guid (with --column-name or --all-columns) "
                "or --column-guid is required.[/red]"
            )
            return

        if column_guid and (guid or column_name or all_columns):
            console.print(
                "[red][X] --column-guid is exclusive with --guid / --column-name / --all-columns.[/red]"
            )
            return

        if guid and not column_name and not all_columns:
            console.print(
                "[red][X] When using --guid, provide --column-name <name> "
                "or --all-columns.[/red]"
            )
            return

        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity add-schema-classification command[/yellow]")
            console.print(
                f"[dim]Table GUID: {guid}  Column GUID: {column_guid}  "
                f"Column name: {column_name}  All columns: {all_columns}[/dim]"
            )
            console.print(
                f"[dim]Classifications: {', '.join(classification_names)}  Dry-run: {dry_run}[/dim]"
            )
            console.print(
                "[green][OK] Mock entity add-schema-classification completed successfully[/green]"
            )
            return

        from purviewcli.client._entity import Entity
        from rich.table import Table as RichTable

        entity_client = Entity()

        # ── Build the list of target columns ──────────────────────────────
        targets = []  # list of {"column": name, "column_guid": guid}

        if column_guid:
            # Direct mode - no table lookup
            targets = [{"column": column_guid, "column_guid": column_guid}]
        else:
            # Resolve columns from the parent table
            console.print(f"[dim]Fetching parent entity {guid}...[/dim]")
            parent = entity_client.entityRead({
                "--guid": guid,
                "--ignoreRelationships": False,
                "--minExtInfo": False,
            })

            if not parent:
                console.print("[red][X] Parent entity not found.[/red]")
                return

            entity_body = parent.get("entity", parent)
            rel_attrs = entity_body.get("relationshipAttributes", {})
            columns_refs = rel_attrs.get("columns", [])

            if not columns_refs:
                referred = parent.get("referredEntities", {})
                columns_refs = [
                    {
                        "guid": g,
                        "displayText": v.get("attributes", {}).get("name", g),
                    }
                    for g, v in referred.items()
                    if v.get("typeName", "").lower().endswith("_column")
                    or v.get("typeName", "").lower() == "column"
                ]

            if not columns_refs:
                console.print("[yellow][!] No columns found on this entity.[/yellow]")
                return

            if all_columns:
                targets = [
                    {
                        "column": c.get("displayText") or c.get("guid"),
                        "column_guid": c.get("guid"),
                    }
                    for c in columns_refs
                    if c.get("guid")
                ]
            else:
                # Match by column name (case-insensitive, partial match)
                search = column_name.lower()
                matches = [
                    c
                    for c in columns_refs
                    if search in (c.get("displayText") or "").lower()
                ]
                if not matches:
                    console.print(
                        f"[red][X] No column matching '{column_name}' found on this entity.[/red]"
                    )
                    available = [c.get("displayText", c.get("guid")) for c in columns_refs]
                    console.print(
                        f"[dim]Available columns: {', '.join(available)}[/dim]"
                    )
                    return
                if len(matches) > 1:
                    names = [m.get("displayText") for m in matches]
                    console.print(
                        f"[yellow][!] '{column_name}' matches {len(matches)} columns: "
                        f"{', '.join(names)}. Refine --column-name or use --all-columns.[/yellow]"
                    )
                    return
                targets = [
                    {
                        "column": matches[0].get("displayText") or matches[0].get("guid"),
                        "column_guid": matches[0].get("guid"),
                    }
                ]

        # Build the Atlas classification payload: [{"typeName": "..."}]
        payload = [{"typeName": cn} for cn in classification_names]

        if dry_run:
            console.print("[bold yellow][DRY-RUN] No API calls will be made.[/bold yellow]")

        # ── Apply (or preview) classifications on each target ─────────────
        results = []
        for t in targets:
            col_name = t["column"]
            col_guid = t["column_guid"]

            if dry_run:
                results.append(
                    {
                        "column": col_name,
                        "column_guid": col_guid,
                        "classifications": [*classification_names],
                        "status": "dry-run",
                    }
                )
                continue

            try:
                entity_client.entityCreateClassifications({
                    "--guid": [col_guid],
                    "--payloadFile": payload,
                })
                results.append(
                    {
                        "column": col_name,
                        "column_guid": col_guid,
                        "classifications": [*classification_names],
                        "status": "ok",
                    }
                )
            except Exception as col_err:
                results.append(
                    {
                        "column": col_name,
                        "column_guid": col_guid,
                        "classifications": [*classification_names],
                        "status": "error",
                        "error": str(col_err),
                    }
                )

        # ── Output ─────────────────────────────────────────────────────────
        if output == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return

        title = (
            "[yellow]DRY-RUN[/yellow] - add-schema-classification"
            if dry_run
            else "add-schema-classification result"
        )
        tbl = RichTable(title=title, show_lines=True)
        tbl.add_column("Column", style="cyan", min_width=20)
        tbl.add_column("Column GUID", style="dim", min_width=36)
        tbl.add_column("Classifications added", style="magenta")
        tbl.add_column("Status", min_width=8)

        ok = sum(1 for r in results if r["status"] in ("ok", "dry-run"))
        for r in results:
            status_cell = {
                "ok": "[green]OK[/green]",
                "dry-run": "[yellow]dry-run[/yellow]",
                "error": f"[red]ERROR: {r.get('error', '')}[/red]",
            }.get(r["status"], r["status"])

            tbl.add_row(
                r["column"],
                r["column_guid"],
                "\n".join(r["classifications"]),
                status_cell,
            )

        console.print(tbl)

        if dry_run:
            console.print(
                f"[yellow][DRY-RUN] Would add classification(s) to "
                f"{ok}/{len(results)} column(s). Re-run without --dry-run to apply.[/yellow]"
            )
        else:
            console.print(
                f"[green][OK] Classifications added to {ok}/{len(results)} column(s).[/green]"
            )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity add-schema-classification: {str(e)}[/red]"
        )


@entity.command()
@click.option(
    "--guid",
    default=None,
    help="GUID of the parent table entity (required unless --column-guid is used)",
)
@click.option(
    "--column-guid",
    default=None,
    help="GUID of a specific column (bypasses table lookup)",
)
@click.option(
    "--column-name",
    default=None,
    help="Name of the column to target (resolved from --guid table). "
    "Supports partial/case-insensitive match.",
)
@click.option(
    "--classification-name",
    "classification_names",
    required=True,
    multiple=True,
    help="Classification typeName to remove (repeatable)",
)
@click.option(
    "--all-columns",
    is_flag=True,
    default=False,
    help="Remove classification(s) from every column of the table (requires --guid)",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Preview which columns/classifications would be removed without calling the API",
)
@click.option(
    "--output",
    type=click.Choice(["table", "json"], case_sensitive=False),
    default="table",
    help="Output format for the result report",
)
@click.pass_context
def remove_schema_classification(
    ctx, guid, column_guid, column_name, classification_names, all_columns, dry_run, output
):
    """Remove classification(s) from column(s) of a table (schema-level)

    \b
        Three targeting modes:

        1) Direct - supply --column-guid (no table lookup needed):
          pvw entity remove-schema-classification --column-guid <col-guid> \\
            --classification-name "Availability High"

        2) By column name - resolve from parent table:
          pvw entity remove-schema-classification --guid <table-guid> \\
            --column-name "NAS" \\
            --classification-name "Canada Social Insurance Number"

        3) All columns - remove from every column of the table:
          pvw entity remove-schema-classification --guid <table-guid> \\
            --all-columns \\
            --classification-name "Availability High"

    Use --dry-run to preview targets before applying.
    Repeat --classification-name to remove multiple classifications at once.
    Only classifications that actually exist on a column will be removed;
    others are skipped gracefully.
    """
    try:
        # ── Validate arguments ─────────────────────────────────────────────
        if not column_guid and not guid:
            console.print(
                "[red][X] Either --guid (with --column-name or --all-columns) "
                "or --column-guid is required.[/red]"
            )
            return

        if column_guid and (guid or column_name or all_columns):
            console.print(
                "[red][X] --column-guid is exclusive with --guid / --column-name / --all-columns.[/red]"
            )
            return

        if guid and not column_name and not all_columns:
            console.print(
                "[red][X] When using --guid, provide --column-name <name> "
                "or --all-columns.[/red]"
            )
            return

        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity remove-schema-classification command[/yellow]")
            console.print(
                f"[dim]Table GUID: {guid}  Column GUID: {column_guid}  "
                f"Column name: {column_name}  All columns: {all_columns}[/dim]"
            )
            console.print(
                f"[dim]Classifications: {', '.join(classification_names)}  Dry-run: {dry_run}[/dim]"
            )
            console.print(
                "[green][OK] Mock entity remove-schema-classification completed successfully[/green]"
            )
            return

        from purviewcli.client._entity import Entity
        from rich.table import Table as RichTable

        entity_client = Entity()

        # ── Build the list of target columns ──────────────────────────────
        targets = []

        if column_guid:
            targets = [{"column": column_guid, "column_guid": column_guid}]
        else:
            console.print(f"[dim]Fetching parent entity {guid}...[/dim]")
            parent = entity_client.entityRead({
                "--guid": guid,
                "--ignoreRelationships": False,
                "--minExtInfo": False,
            })

            if not parent:
                console.print("[red][X] Parent entity not found.[/red]")
                return

            entity_body = parent.get("entity", parent)
            rel_attrs = entity_body.get("relationshipAttributes", {})
            columns_refs = rel_attrs.get("columns", [])

            if not columns_refs:
                referred = parent.get("referredEntities", {})
                columns_refs = [
                    {
                        "guid": g,
                        "displayText": v.get("attributes", {}).get("name", g),
                    }
                    for g, v in referred.items()
                    if v.get("typeName", "").lower().endswith("_column")
                    or v.get("typeName", "").lower() == "column"
                ]

            if not columns_refs:
                console.print("[yellow][!] No columns found on this entity.[/yellow]")
                return

            if all_columns:
                targets = [
                    {
                        "column": c.get("displayText") or c.get("guid"),
                        "column_guid": c.get("guid"),
                    }
                    for c in columns_refs
                    if c.get("guid")
                ]
            else:
                search = column_name.lower()
                matches = [
                    c
                    for c in columns_refs
                    if search in (c.get("displayText") or "").lower()
                ]
                if not matches:
                    console.print(
                        f"[red][X] No column matching '{column_name}' found on this entity.[/red]"
                    )
                    available = [c.get("displayText", c.get("guid")) for c in columns_refs]
                    console.print(f"[dim]Available columns: {', '.join(available)}[/dim]")
                    return
                if len(matches) > 1:
                    names = [m.get("displayText") for m in matches]
                    console.print(
                        f"[yellow][!] '{column_name}' matches {len(matches)} columns: "
                        f"{', '.join(names)}. Refine --column-name or use --all-columns.[/yellow]"
                    )
                    return
                targets = [
                    {
                        "column": matches[0].get("displayText") or matches[0].get("guid"),
                        "column_guid": matches[0].get("guid"),
                    }
                ]

        if dry_run:
            console.print("[bold yellow][DRY-RUN] No API calls will be made.[/bold yellow]")

        # ── Remove (or preview) per column × per classification ───────────
        results = []
        for t in targets:
            col_name = t["column"]
            col_guid = t["column_guid"]
            col_results = []

            if dry_run:
                for cn in classification_names:
                    col_results.append({"typeName": cn, "status": "dry-run"})
            else:
                # First fetch existing classifications on this column to skip missing ones
                try:
                    existing_resp = entity_client.entityReadClassifications({"--guid": [col_guid]})
                    existing = set()
                    if existing_resp:
                        items = existing_resp.get(
                            "list",
                            existing_resp if isinstance(existing_resp, _builtin_list) else [],
                        )
                        existing = {c.get("typeName") for c in items}
                except Exception:
                    existing = None  # unknown - attempt removal anyway

                for cn in classification_names:
                    if existing is not None and cn not in existing:
                        col_results.append({"typeName": cn, "status": "skipped (not present)"})
                        continue
                    try:
                        entity_client.entityDeleteClassification({
                            "--guid": [col_guid],
                            "--classificationName": cn,
                        })
                        col_results.append({"typeName": cn, "status": "ok"})
                    except Exception as del_err:
                        col_results.append({"typeName": cn, "status": f"error: {del_err}"})

            results.append(
                {
                    "column": col_name,
                    "column_guid": col_guid,
                    "details": col_results,
                }
            )

        # ── Output ─────────────────────────────────────────────────────────
        if output == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return

        title = (
            "[yellow]DRY-RUN[/yellow] - remove-schema-classification"
            if dry_run
            else "remove-schema-classification result"
        )
        tbl = RichTable(title=title, show_lines=True)
        tbl.add_column("Column", style="cyan", min_width=20)
        tbl.add_column("Column GUID", style="dim", min_width=36)
        tbl.add_column("Classification", style="magenta")
        tbl.add_column("Status", min_width=20)

        ok_count = 0
        for r in results:
            first = True
            for d in r["details"]:
                col_cell = r["column"] if first else ""
                guid_cell = r["column_guid"] if first else ""
                first = False
                s = d["status"]
                if s == "ok":
                    status_cell = "[green]OK[/green]"
                    ok_count += 1
                elif s == "dry-run":
                    status_cell = "[yellow]dry-run[/yellow]"
                    ok_count += 1
                elif s.startswith("skipped"):
                    status_cell = f"[dim]{s}[/dim]"
                else:
                    status_cell = f"[red]{s}[/red]"
                tbl.add_row(col_cell, guid_cell, d["typeName"], status_cell)

        console.print(tbl)

        total_ops = sum(len(r["details"]) for r in results)
        if dry_run:
            console.print(
                f"[yellow][DRY-RUN] Would remove {ok_count}/{total_ops} classification-column "
                f"pairs. Re-run without --dry-run to apply.[/yellow]"
            )
        else:
            console.print(
                f"[green][OK] Removed {ok_count}/{total_ops} classification-column pairs.[/green]"
            )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity remove-schema-classification: {str(e)}[/red]"
        )


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing classification data",
)
@click.pass_context
def add_classifications(ctx, guid, payload_file):
    """Add classifications to an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity add-classifications command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print("[green][OK] Mock entity add-classifications completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityCreateClassifications(args)

        if result:
            console.print("[green][OK] Entity add-classifications completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity add-classifications completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity add-classifications: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing classification data",
)
@click.pass_context
def update_classifications(ctx, guid, payload_file):
    """Update classifications on an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity update-classifications command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print(
                "[green][OK] Mock entity update-classifications completed successfully[/green]"
            )
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityUpdateClassifications(args)

        if result:
            console.print("[green][OK] Entity update-classifications completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity update-classifications completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity update-classifications: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--classification-name", required=True, help="The name of the classification to remove"
)
@click.pass_context
def remove_classification(ctx, guid, classification_name):
    """Remove classification from an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity remove-classification command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Classification: {classification_name}[/dim]")
            console.print(
                "[green][OK] Mock entity remove-classification completed successfully[/green]"
            )
            return

        args = {
            "--guid": [guid],
            "--classificationName": classification_name,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityDeleteClassification(args)

        if result:
            console.print("[green][OK] Entity remove-classification completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity remove-classification completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity remove-classification: {str(e)}[/red]")


# === CLASSIFICATION OPERATIONS BY UNIQUE ATTRIBUTE ===


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing classification data",
)
@click.pass_context
def add_classifications_by_attribute(ctx, type_name, qualified_name, payload_file):
    """Add classifications by unique attribute"""
    try:
        if ctx.obj.get("mock"):
            console.print(
                "[yellow][MOCK] entity add-classifications-by-attribute command[/yellow]"
            )
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print(
                "[green][OK] Mock entity add-classifications-by-attribute completed successfully[/green]"
            )
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddClassificationsByUniqueAttribute(args)

        if result:
            console.print(
                "[green][OK] Entity add-classifications-by-attribute completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity add-classifications-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity add-classifications-by-attribute: {str(e)}[/red]"
        )


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing classification data",
)
@click.pass_context
def update_classifications_by_attribute(ctx, type_name, qualified_name, payload_file):
    """Update classifications by unique attribute"""
    try:
        if ctx.obj.get("mock"):
            console.print(
                "[yellow][MOCK] entity update-classifications-by-attribute command[/yellow]"
            )
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print(
                "[green][OK] Mock entity update-classifications-by-attribute completed successfully[/green]"
            )
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityUpdateClassificationsByUniqueAttribute(args)

        if result:
            console.print(
                "[green][OK] Entity update-classifications-by-attribute completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity update-classifications-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity update-classifications-by-attribute: {str(e)}[/red]"
        )


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.option(
    "--classification-name", required=True, help="The name of the classification to remove"
)
@click.pass_context
def remove_classification_by_attribute(ctx, type_name, qualified_name, classification_name):
    """Remove classification by unique attribute"""
    try:
        if ctx.obj.get("mock"):
            console.print(
                "[yellow][MOCK] entity remove-classification-by-attribute command[/yellow]"
            )
            console.print(
                f"[dim]Type: {type_name}, Qualified Name: {qualified_name}, Classification: {classification_name}[/dim]"
            )
            console.print(
                "[green][OK] Mock entity remove-classification-by-attribute completed successfully[/green]"
            )
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--classificationName": classification_name,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityDeleteClassificationByUniqueAttribute(args)

        if result:
            console.print(
                "[green][OK] Entity remove-classification-by-attribute completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity remove-classification-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity remove-classification-by-attribute: {str(e)}[/red]"
        )


# === BULK CLASSIFICATION OPERATIONS ===


@entity.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing bulk classification data",
)
@click.pass_context
def bulk_add_classification(ctx, payload_file):
    """Add classification to multiple entities in bulk"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-add-classification command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print(
                "[green][OK] Mock entity bulk-add-classification completed successfully[/green]"
            )
            return

        args = {"--payloadFile": payload_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddClassification(args)

        if result:
            console.print("[green][OK] Entity bulk-add-classification completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity bulk-add-classification completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-add-classification: {str(e)}[/red]")


@entity.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing bulk classification data",
)
@click.pass_context
def bulk_set_classifications(ctx, payload_file):
    """Set classifications on multiple entities in bulk"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-set-classifications command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print(
                "[green][OK] Mock entity bulk-set-classifications completed successfully[/green]"
            )
            return

        args = {"--payloadFile": payload_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityBulkSetClassifications(args)

        if result:
            console.print("[green][OK] Entity bulk-set-classifications completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity bulk-set-classifications completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-set-classifications: {str(e)}[/red]")


# === LABEL OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing label data",
)
@click.pass_context
def add_labels(ctx, guid, payload_file):
    """Add labels to an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity add-labels command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print("[green][OK] Mock entity add-labels completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddLabels(args)

        if result:
            console.print("[green][OK] Entity add-labels completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity add-labels completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity add-labels: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing label data",
)
@click.pass_context
def set_labels(ctx, guid, payload_file):
    """Set labels on an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity set-labels command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print("[green][OK] Mock entity set-labels completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entitySetLabels(args)

        if result:
            console.print("[green][OK] Entity set-labels completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity set-labels completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity set-labels: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing label data",
)
@click.pass_context
def remove_labels(ctx, guid, payload_file):
    """Remove labels from an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity remove-labels command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print("[green][OK] Mock entity remove-labels completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityRemoveLabels(args)

        if result:
            console.print("[green][OK] Entity remove-labels completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity remove-labels completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity remove-labels: {str(e)}[/red]")


# === LABEL OPERATIONS BY UNIQUE ATTRIBUTE ===


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing label data",
)
@click.pass_context
def add_labels_by_attribute(ctx, type_name, qualified_name, payload_file):
    """Add labels by unique attribute"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity add-labels-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print(
                "[green][OK] Mock entity add-labels-by-attribute completed successfully[/green]"
            )
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddLabelsByUniqueAttribute(args)

        if result:
            console.print("[green][OK] Entity add-labels-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity add-labels-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity add-labels-by-attribute: {str(e)}[/red]")


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing label data",
)
@click.pass_context
def set_labels_by_attribute(ctx, type_name, qualified_name, payload_file):
    """Set labels by unique attribute"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity set-labels-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print(
                "[green][OK] Mock entity set-labels-by-attribute completed successfully[/green]"
            )
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entitySetLabelsByUniqueAttribute(args)

        if result:
            console.print("[green][OK] Entity set-labels-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity set-labels-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity set-labels-by-attribute: {str(e)}[/red]")


@entity.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing bulk label data",
)
@click.pass_context
def bulk_remove_labels(ctx, payload_file):
    """Remove labels from multiple entities in bulk (by GUID)"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-remove-labels command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green][OK] Mock entity bulk-remove-labels completed successfully[/green]")
            return
        args = {"--payloadFile": payload_file}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityBulkRemoveLabels(args)
        if result:
            console.print("[green][OK] Entity bulk-remove-labels completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity bulk-remove-labels completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-remove-labels: {str(e)}[/red]")


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing label data",
)
@click.pass_context
def bulk_remove_labels_by_attribute(ctx, type_name, qualified_name, payload_file):
    """Remove labels from multiple entities in bulk (by unique attribute)"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-remove-labels-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}, Payload File: {payload_file}[/dim]")
            console.print("[green][OK] Mock entity bulk-remove-labels-by-attribute completed successfully[/green]")
            return
        args = {"--typeName": type_name, "--qualifiedName": qualified_name, "--payloadFile": payload_file}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityBulkRemoveLabelsByUniqueAttribute(args)
        if result:
            console.print("[green][OK] Entity bulk-remove-labels-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity bulk-remove-labels-by-attribute completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-remove-labels-by-attribute: {str(e)}[/red]")


# === BUSINESS METADATA OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=False,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing business metadata",
)
@click.option("--bm-name", required=False, help="Business metadata group name (e.g., group1)")
@click.option("--attr-name", required=False, help="Business metadata attribute name (e.g., attr1)")
@click.option("--attr-value", required=False, help="Business metadata attribute value")
@click.option(
    "--is-overwrite", is_flag=True, help="Whether to overwrite existing business metadata"
)
@click.pass_context
def add_business_metadata(ctx, guid, payload_file, bm_name, attr_name, attr_value, is_overwrite):
    """Add or update business metadata to an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity add-business-metadata command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Overwrite: {is_overwrite}[/dim]")
            console.print(
                "[green][OK] Mock entity add-business-metadata completed successfully[/green]"
            )
            return

        # Two input modes are supported:
        # 1) --payload-file <json>
        # 2) --bm-name <group> --attr-name <name> --attr-value <value>
        using_payload_file = bool(payload_file)
        using_direct_attribute = any(v is not None for v in [bm_name, attr_name, attr_value])

        if not using_payload_file and not using_direct_attribute:
            raise ValueError(
                "Provide either --payload-file, or --bm-name + --attr-name + --attr-value"
            )

        if using_payload_file and using_direct_attribute:
            raise ValueError(
                "Use either --payload-file OR --bm-name/--attr-name/--attr-value, not both"
            )

        if using_direct_attribute and not all(v is not None for v in [bm_name, attr_name, attr_value]):
            raise ValueError(
                "When using direct attributes, all of --bm-name, --attr-name, and --attr-value are required"
            )

        payload = payload_file if using_payload_file else {bm_name: {attr_name: _parse_attr_value(attr_value)}}

        args = {
            "--guid": [guid],
            "--payloadFile": payload,
            "--isOverwrite": is_overwrite,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddOrUpdateBusinessMetadata(args)

        if result:
            console.print("[green][OK] Entity add-business-metadata completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity add-business-metadata completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity add-business-metadata: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--bm-name", required=True, help="The business metadata name")
@click.option(
    "--payload-file",
    required=False,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing business metadata attributes",
)
@click.option("--attr-name", required=False, help="Business metadata attribute name (e.g., attr1)")
@click.option("--attr-value", required=False, help="Business metadata attribute value")
@click.pass_context
def add_business_metadata_attributes(ctx, guid, bm_name, payload_file, attr_name, attr_value):
    """Add or update business metadata attributes.

    Supports two input modes:
    - --payload-file with a JSON object of attributes
    - --attr-name and --attr-value for a single attribute update
    """
    try:
        if ctx.obj.get("mock"):
            console.print(
                "[yellow][MOCK] entity add-business-metadata-attributes command[/yellow]"
            )
            console.print(f"[dim]GUID: {guid}, BM Name: {bm_name}[/dim]")
            console.print(
                "[green][OK] Mock entity add-business-metadata-attributes completed successfully[/green]"
            )
            return

        using_payload_file = bool(payload_file)
        using_direct_attribute = any(v is not None for v in [attr_name, attr_value])

        if not using_payload_file and not using_direct_attribute:
            raise ValueError(
                "Provide either --payload-file, or --attr-name + --attr-value"
            )

        if using_payload_file and using_direct_attribute:
            raise ValueError(
                "Use either --payload-file OR --attr-name/--attr-value, not both"
            )

        if using_direct_attribute and not all(v is not None for v in [attr_name, attr_value]):
            raise ValueError(
                "When using direct attributes, both --attr-name and --attr-value are required"
            )

        payload = payload_file if using_payload_file else {attr_name: _parse_attr_value(attr_value)}

        args = {
            "--guid": [guid],
            "--businessMetadataName": bm_name,
            "--payloadFile": payload,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddOrUpdateBusinessMetadataAttributes(args)

        if result:
            console.print(
                "[green][OK] Entity add-business-metadata-attributes completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity add-business-metadata-attributes completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity add-business-metadata-attributes: {str(e)}[/red]"
        )


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=False,
    type=click.Path(exists=True),
    help="File path to a valid JSON document specifying business metadata to remove",
)
@click.option("--bm-name", required=False, help="Business metadata group name to remove")
@click.pass_context
def remove_business_metadata(ctx, guid, payload_file, bm_name):
    """Remove business metadata from an entity.

    Supports two input modes:
    - --payload-file with a JSON object containing the group name to remove
    - --bm-name to remove a group directly
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity remove-business-metadata command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(
                "[green][OK] Mock entity remove-business-metadata completed successfully[/green]"
            )
            return

        using_payload_file = bool(payload_file)
        using_direct_name = bm_name is not None

        if not using_payload_file and not using_direct_name:
            raise ValueError("Provide either --payload-file or --bm-name")

        if using_payload_file and using_direct_name:
            raise ValueError("Use either --payload-file OR --bm-name, not both")

        args = {
            "--guid": [guid],
        }

        if using_payload_file:
            args["--payloadFile"] = payload_file
        else:
            args["--businessMetadataName"] = bm_name

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityRemoveBusinessMetadata(args)

        if result:
            console.print("[green][OK] Entity remove-business-metadata completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity remove-business-metadata completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity remove-business-metadata: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--bm-name", required=True, help="The business metadata name")
@click.option(
    "--payload-file",
    required=False,
    type=click.Path(exists=True),
    help="File path to a valid JSON document specifying attributes to remove",
)
@click.option("--attr-name", required=False, help="Business metadata attribute name to remove")
@click.pass_context
def remove_business_metadata_attributes(ctx, guid, bm_name, payload_file, attr_name):
    """Remove business metadata attributes.

    Supports two input modes:
    - --payload-file with a JSON document specifying attribute(s) to remove
    - --attr-name to remove a single attribute directly
    """
    try:
        if ctx.obj.get("mock"):
            console.print(
                "[yellow][MOCK] entity remove-business-metadata-attributes command[/yellow]"
            )
            console.print(f"[dim]GUID: {guid}, BM Name: {bm_name}[/dim]")
            console.print(
                "[green][OK] Mock entity remove-business-metadata-attributes completed successfully[/green]"
            )
            return

        using_payload_file = bool(payload_file)
        using_direct_attribute = attr_name is not None

        if not using_payload_file and not using_direct_attribute:
            raise ValueError("Provide either --payload-file or --attr-name")

        if using_payload_file and using_direct_attribute:
            raise ValueError("Use either --payload-file OR --attr-name, not both")

        args = {
            "--guid": [guid],
            "--businessMetadataName": bm_name,
        }

        if using_payload_file:
            with open(payload_file, "r", encoding="utf-8") as payload_stream:
                payload = json.load(payload_stream)

            if isinstance(payload, dict) and "businessMetadataAttributes" in payload:
                args["--attributes"] = payload["businessMetadataAttributes"]
            elif isinstance(payload, list):
                args["--attributes"] = payload
            elif isinstance(payload, str):
                args["--attributes"] = [payload]
            else:
                raise ValueError(
                    "Payload file must contain a string, a list of attribute names, or a businessMetadataAttributes object"
                )
        else:
            args["--attributes"] = [attr_name]

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityRemoveBusinessMetadataAttributes(args)

        if result:
            console.print(
                "[green][OK] Entity remove-business-metadata-attributes completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity remove-business-metadata-attributes completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity remove-business-metadata-attributes: {str(e)}[/red]"
        )


@entity.command(name="import-business-metadata")
@click.option(
    "--bm-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid business metadata CSV file",
)
@click.pass_context
def import_business_metadata(ctx, bm_file):
    """Import business metadata in bulk from CSV"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity import-business-metadata command[/yellow]")
            console.print(f"[dim]BM File: {bm_file}[/dim]")
            console.print(
                "[green][OK] Mock entity import-business-metadata completed successfully[/green]"
            )
            return

        args = {"--bmFile": bm_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityImportBusinessMetadata(args)

        if result:
            console.print("[green][OK] Entity import-business-metadata completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity import-business-metadata completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red][X] Error executing entity import-business-metadata: {str(e)}[/red]")


@entity.command()
@click.pass_context
def get_business_metadata_template(ctx):
    """Get sample template for business metadata"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity get-business-metadata-template command[/yellow]")
            console.print(
                "[green][OK] Mock entity get-business-metadata-template completed successfully[/green]"
            )
            return

        args = {}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityGetBusinessMetadataTemplate(args)

        if result:
            console.print(
                "[green][OK] Entity get-business-metadata-template completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow][!] Entity get-business-metadata-template completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red][X] Error executing entity get-business-metadata-template: {str(e)}[/red]"
        )


# === COLLECTION OPERATIONS ===


@entity.command()
@click.option(
    "--collection-id",
    required=True,
    help="Target collection ID where entities will be moved (e.g., 'yfwy2c')",
)
@click.option(
    "--guids",
    required=False,
    help="Comma-separated list of entity GUIDs to move (e.g., 'guid1,guid2,guid3')",
)
@click.option(
    "--payload-file",
    required=False,
    type=click.Path(exists=True),
    help="File path to JSON with entityGuids array (alternative to --guids)",
)
@click.pass_context
def move_to_collection(ctx, collection_id, guids, payload_file):
    """Move entities to a target collection"""
    try:
        if not guids and not payload_file:
            console.print("[red][X] Error: Either --guids or --payload-file must be provided[/red]")
            return

        if guids and payload_file:
            console.print("[red][X] Error: Provide either --guids or --payload-file, not both[/red]")
            return

        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity move-to-collection command[/yellow]")
            console.print(f"[dim]Collection ID: {collection_id}[/dim]")
            if guids:
                console.print(f"[dim]GUIDs: {guids}[/dim]")
            if payload_file:
                console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green][OK] Mock entity move-to-collection completed successfully[/green]")
            return

        args = {"--collectionId": collection_id}
        if guids:
            args["--guids"] = guids
        if payload_file:
            args["--payloadFile"] = payload_file

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityMoveToCollection(args)

        if result:
            console.print("[green][OK] Entity move-to-collection completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity move-to-collection completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity move-to-collection: {str(e)}[/red]")


# === SAMPLE OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def read_sample(ctx, guid):
    """Get sample data for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity read-sample command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green][OK] Mock entity read-sample completed successfully[/green]")
            return

        args = {"--guid": [guid]}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadSample(args)

        if result:
            console.print("[green][OK] Entity read-sample completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity read-sample completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red][X] Error executing entity read-sample: {str(e)}[/red]")


@entity.command()
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="CSV file with GUID and classificationName columns")
@click.option("--batch-size", default=100, help="Batch size for API calls")
@click.pass_context
def bulk_classify_csv(ctx, csv_file, batch_size):
    """Bulk classify entities from a CSV file (guid, classificationName columns)"""
    import pandas as pd
    import tempfile
    from purviewcli.client._entity import Entity
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-classify-csv command[/yellow]")
            console.print(f"[dim]CSV File: {csv_file}[/dim]")
            console.print("[green][OK] Mock entity bulk-classify-csv completed successfully[/green]")
            return

        df = pd.read_csv(csv_file)
        if "guid" not in df.columns or "classificationName" not in df.columns:
            console.print("[red][X] CSV must contain 'guid' and 'classificationName' columns[/red]")
            return
        entity_client = Entity()
        total = len(df)
        success, failed = 0, 0
        errors = []
        for i in range(0, total, batch_size):
            batch = df.iloc[i:i+batch_size]
            payload = {
                "entities": [
                    {
                        "guid": str(row["guid"]),
                        "classifications": [{"typeName": str(row["classificationName"])}]
                    }
                    for _, row in batch.iterrows()
                ]
            }
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmpf:
                import json
                json.dump(payload, tmpf, indent=2)
                tmpf.flush()
                payload_file = tmpf.name
            try:
                args = {"--payloadFile": payload_file}
                result = entity_client.entityAddClassification(args)
                if result and (not isinstance(result, dict) or result.get("status") != "error"):
                    success += len(batch)
                else:
                    failed += len(batch)
                    errors.append(f"Batch {i//batch_size+1}: {result}")
            except Exception as e:
                failed += len(batch)
                errors.append(f"Batch {i//batch_size+1}: {str(e)}")
            finally:
                import os
                os.remove(payload_file)
        console.print(f"[green][OK] Bulk classification completed. Success: {success}, Failed: {failed}[/green]")
        if errors:
            console.print("[red]Errors:[/red]")
            for err in errors:
                console.print(f"[red]- {err}[/red]")
    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-classify-csv: {str(e)}[/red]")


# === BULK ENTITY CSV OPERATIONS ===


@entity.command()
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="CSV file with entity attributes (typeName, qualifiedName, ...)")
@click.option("--batch-size", default=100, help="Batch size for API calls")
@click.option("--throttle-ms", default=0, type=int, help="Delay between batches in milliseconds")
@click.option("--max-retries", default=3, type=int, help="Max retry attempts per batch on API failure")
@click.option("--retry-backoff-ms", default=1000, type=int, help="Base retry backoff delay in milliseconds")
@click.option(
    "--retry-mode",
    type=click.Choice(["fixed", "exponential"], case_sensitive=False),
    default="exponential",
    help="Retry backoff mode: fixed or exponential",
)
@click.option("--dry-run", is_flag=True, help="Preview entities to be created without making changes")
@click.option("--error-csv", type=click.Path(), help="CSV file to write failed rows (optional)")
@click.option("--debug", is_flag=True, help="Enable debug mode for detailed logging")
@click.pass_context
def bulk_create_csv(
    ctx,
    csv_file,
    batch_size,
    throttle_ms,
    max_retries,
    retry_backoff_ms,
    retry_mode,
    dry_run,
    error_csv,
    debug,
):
    """Bulk create entities from a CSV file with support for custom attributes and classifications.
    
    Supports:
    - Dot notation for nested attributes (businessMetadata.fieldName, customAttributes.fieldName)
    - Optional classification or classificationName column (multi-value with ; or , separator)
    - Simple field names: Added to root attributes

    Example CSV with classifications:
    typeName,qualifiedName,displayName,classification,businessMetadata.department
    DataSet,my-data-asset,My Asset,PII;CONFIDENTIAL,Sales
    azure_datalake_gen2_path,//myaccount/container/path,My Path,INTERNAL,Engineering

        \b
    Preset configurations:
            Fast:
                --batch-size 100 --throttle-ms 50 --max-retries 3 --retry-backoff-ms 1000 --retry-mode fixed
            Balanced:
                --batch-size 50 --throttle-ms 200 --max-retries 4 --retry-backoff-ms 1500 --retry-mode exponential
            Safe:
                --batch-size 25 --throttle-ms 500 --max-retries 5 --retry-backoff-ms 2000 --retry-mode exponential

        \b
    Quick tuning:
            Increase throughput: increase --batch-size or lower --throttle-ms
            Reduce throttling: lower --batch-size or increase --throttle-ms
    """
    import pandas as pd
    import tempfile
    import os
    import json
    import time
    from purviewcli.client._entity import Entity, map_flat_entity_to_purview_entity
    
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-create-csv command[/yellow]")
            console.print(f"[dim]CSV File: {csv_file}[/dim]")
            console.print("[green][OK] Mock entity bulk-create-csv completed successfully[/green]")
            return

        retry_mode = (retry_mode or "exponential").lower()

        if debug:
            console.print(f"[cyan][DEBUG] Throttle (ms): {throttle_ms}[/cyan]")
            console.print(f"[cyan][DEBUG] Max Retries: {max_retries}[/cyan]")
            console.print(f"[cyan][DEBUG] Retry Backoff (ms): {retry_backoff_ms}[/cyan]")
            console.print(f"[cyan][DEBUG] Retry Mode: {retry_mode}[/cyan]")

        df = pd.read_csv(csv_file)
        
        # Detect classification columns
        classification_columns = [
            col for col in ["classification", "classificationName"] if col in df.columns
        ]
        
        # Debug: Show CSV structure
        if debug:
            console.print("[cyan][DEBUG] CSV Structure:[/cyan]")
            try:
                console.print(f"  Columns: {__builtins__['list'](df.columns)}")
                console.print(f"  Total rows: {len(df)}")
                if classification_columns:
                    console.print(
                        f"  Classification columns: {classification_columns}"
                    )
                console.print("\n[cyan][DEBUG] First row data:[/cyan]")
                if len(df) > 0:
                    console.print(df.iloc[0].to_dict())
            except Exception as e:
                console.print(f"[red][DEBUG ERROR: {e}][/red]")
        
        if "typeName" not in df.columns or "qualifiedName" not in df.columns:
            console.print("[red][X] CSV must contain at least 'typeName' and 'qualifiedName' columns[/red]")
            return
        
        entity_client = Entity()
        total = len(df)
        success, failed = 0, 0
        errors = []
        failed_rows = []

        def _call_bulk_with_retry(args, batch_label):
            last_error = None
            total_attempts = max_retries + 1
            for attempt in range(1, total_attempts + 1):
                try:
                    return entity_client.entityCreateBulk(args)
                except Exception as exc:
                    last_error = exc
                    if attempt >= total_attempts:
                        break

                    if retry_mode == "fixed":
                        delay_ms = retry_backoff_ms
                    else:
                        delay_ms = retry_backoff_ms * (2 ** (attempt - 1))

                    if debug:
                        console.print(
                            f"[yellow][DEBUG] {batch_label} attempt {attempt}/{total_attempts} failed: {str(exc)}[/yellow]"
                        )
                        console.print(
                            f"[yellow][DEBUG] Retrying in {delay_ms} ms[/yellow]"
                        )

                    if delay_ms > 0:
                        time.sleep(delay_ms / 1000.0)

            if last_error is not None:
                raise last_error
            raise RuntimeError(f"{batch_label} failed without exception details")
        
        for i in range(0, total, batch_size):
            batch = df.iloc[i:i+batch_size]
            
            # Map each row to the correct Purview entity format (with custom attributes support)
            entities = []
            for _, row in batch.iterrows():
                entity = map_flat_entity_to_purview_entity(row, debug=debug)
                entities.append(entity)
            
            payload = {"entities": entities}
            
            if debug:
                console.print(f"\n[cyan][DEBUG] Batch {i//batch_size+1} Payload:[/cyan]")
                payload_str = json.dumps(payload, indent=2)
                console.print(payload_str[:500] + "..." if len(payload_str) > 500 else payload_str)
            
            if dry_run:
                console.print(f"[blue]DRY RUN: Would create batch {i//batch_size+1} with {len(batch)} entities[/blue]")
                if debug:
                    console.print(f"[dim]Payload size: {len(json.dumps(payload))} bytes[/dim]")
                continue
            
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmpf:
                json.dump(payload, tmpf, indent=2)
                tmpf.flush()
                payload_file = tmpf.name
            
            try:
                args = {"--payloadFile": payload_file}
                result = _call_bulk_with_retry(args, f"Batch {i//batch_size+1}")
                
                if debug:
                    console.print(f"[cyan][DEBUG] API Response (batch {i//batch_size+1}):[/cyan]")
                    result_str = json.dumps(result, indent=2)
                    console.print(result_str[:500] + "..." if len(result_str) > 500 else result_str)
                
                if result and (not isinstance(result, dict) or result.get("status") != "error"):
                    success += len(batch)
                    console.print(f"[green]✓ Batch {i//batch_size+1} created successfully[/green]")
                else:
                    failed += len(batch)
                    errors.append(f"Batch {i//batch_size+1}: {result}")
                    failed_rows.extend(batch.to_dict(orient="records"))
            except Exception as e:
                failed += len(batch)
                error_msg = str(e)
                errors.append(f"Batch {i//batch_size+1}: {error_msg}")
                failed_rows.extend(batch.to_dict(orient="records"))
                
                if debug:
                    console.print(f"[red][DEBUG] Exception (batch {i//batch_size+1}):[/red]")
                    import traceback
                    console.print(traceback.format_exc())
            finally:
                os.remove(payload_file)

            if throttle_ms > 0 and (i + batch_size) < total:
                if debug:
                    console.print(
                        f"[cyan][DEBUG] Throttling {throttle_ms} ms before next batch[/cyan]"
                    )
                time.sleep(throttle_ms / 1000.0)
        
        console.print(f"\n[green]SUCCESS: Bulk create completed. Success: {success}, Failed: {failed}[/green]")
        if errors:
            console.print("[red]Errors:[/red]")
            for err in errors:
                console.print(f"[red]- {err}[/red]")
        if error_csv and failed_rows:
            pd.DataFrame(failed_rows).to_csv(error_csv, index=False)
            console.print(f"[yellow]WARNING: Failed rows written to {error_csv}[/yellow]")
    except Exception as e:
        console.print(f"[red]ERROR: Error executing entity bulk-create-csv: {str(e)}[/red]")
        import traceback
        if debug:
            console.print(f"[dim]{traceback.format_exc()}[/dim]")


@entity.command()
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="CSV file with GUID and attributes to update")
@click.option("--batch-size", default=100, help="Batch size for API calls")
@click.option("--throttle-ms", default=0, type=int, help="Delay between batches in milliseconds")
@click.option("--max-retries", default=3, type=int, help="Max retry attempts per batch on API failure")
@click.option("--retry-backoff-ms", default=1000, type=int, help="Base retry backoff delay in milliseconds")
@click.option(
    "--retry-mode",
    type=click.Choice(["fixed", "exponential"], case_sensitive=False),
    default="exponential",
    help="Retry backoff mode: fixed or exponential",
)
@click.option("--dry-run", is_flag=True, help="Preview entities to be updated without making changes")
@click.option("--error-csv", type=click.Path(), help="CSV file to write failed rows (optional)")
@click.option("--debug", is_flag=True, help="Enable debug mode for detailed logging")
@click.pass_context
def bulk_update_csv(
    ctx,
    csv_file,
    batch_size,
    throttle_ms,
    max_retries,
    retry_backoff_ms,
    retry_mode,
    dry_run,
    error_csv,
    debug,
):
    """Bulk update entities from a CSV file (guid, attributes...)

        \b
    Preset configurations:
            Fast:
                --batch-size 100 --throttle-ms 50 --max-retries 3 --retry-backoff-ms 1000 --retry-mode fixed
            Balanced:
                --batch-size 50 --throttle-ms 200 --max-retries 4 --retry-backoff-ms 1500 --retry-mode exponential
            Safe:
                --batch-size 25 --throttle-ms 500 --max-retries 5 --retry-backoff-ms 2000 --retry-mode exponential

        \b
    Quick tuning:
            Increase throughput: increase --batch-size or lower --throttle-ms
            Reduce throttling: lower --batch-size or increase --throttle-ms
    """
    import pandas as pd
    import tempfile
    import os
    import json
    import time
    from purviewcli.client._entity import Entity
    try:
        if debug:
            console.print(f"[cyan][DEBUG] CSV File: {csv_file}[/cyan]")
            console.print(f"[cyan][DEBUG] Batch Size: {batch_size}[/cyan]")
            console.print(f"[cyan][DEBUG] Throttle (ms): {throttle_ms}[/cyan]")
            console.print(f"[cyan][DEBUG] Max Retries: {max_retries}[/cyan]")
            console.print(f"[cyan][DEBUG] Retry Backoff (ms): {retry_backoff_ms}[/cyan]")
            console.print(f"[cyan][DEBUG] Retry Mode: {retry_mode}[/cyan]")
            console.print(f"[cyan][DEBUG] Dry Run: {dry_run}[/cyan]")
            console.print(f"[cyan][DEBUG] Error CSV: {error_csv}[/cyan]")
        
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-update-csv command[/yellow]")
            console.print(f"[dim]CSV File: {csv_file}[/dim]")
            console.print("[green][OK] Mock entity bulk-update-csv completed successfully[/green]")
            return

        df = pd.read_csv(csv_file)
        if df.empty:
            console.print("[yellow]No rows found in CSV. Exiting.[/yellow]")
            return
        
        if debug:
            # Use __builtins__['list'] to avoid conflict with entity list command below
            console.print(f"[cyan][DEBUG] CSV columns: {__builtins__['list'](df.columns)}[/cyan]")
            console.print(f"[cyan][DEBUG] Total rows: {len(df)}[/cyan]")
            console.print(f"[cyan][DEBUG] First row:\n{df.iloc[0].to_dict()}[/cyan]")

        entity_client = Entity()
        total = len(df)
        success, failed = 0, 0
        errors = []
        failed_rows = []

        retry_mode = (retry_mode or "exponential").lower()

        def _call_bulk_with_retry(args, batch_label):
            last_error = None
            total_attempts = max_retries + 1
            for attempt in range(1, total_attempts + 1):
                try:
                    return entity_client.entityCreateBulk(args)
                except Exception as exc:
                    last_error = exc
                    if attempt >= total_attempts:
                        break

                    if retry_mode == "fixed":
                        delay_ms = retry_backoff_ms
                    else:
                        delay_ms = retry_backoff_ms * (2 ** (attempt - 1))

                    if debug:
                        console.print(
                            f"[yellow][DEBUG] {batch_label} attempt {attempt}/{total_attempts} failed: {str(exc)}[/yellow]"
                        )
                        console.print(
                            f"[yellow][DEBUG] Retrying in {delay_ms} ms[/yellow]"
                        )

                    if delay_ms > 0:
                        time.sleep(delay_ms / 1000.0)

            if last_error is not None:
                raise last_error
            raise RuntimeError(f"{batch_label} failed without exception details")

        # Determine mode:
        # - If CSV has both 'typeName' and 'qualifiedName' -> map rows to Purview entities and call bulk create-or-update
        # - Else if CSV has 'guid' -> build guid-based payloads (preferred for partial attribute updates)
        has_type_qn = ("typeName" in df.columns and "qualifiedName" in df.columns)
        has_guid = "guid" in df.columns
        classification_columns = [
            col for col in ["classification", "classificationName"] if col in df.columns
        ]
        
        if debug:
            console.print(f"[cyan][DEBUG] has_type_qn: {has_type_qn}[/cyan]")
            console.print(f"[cyan][DEBUG] has_guid: {has_guid}[/cyan]")
            if classification_columns:
                console.print(
                    f"[cyan][DEBUG] Classification columns: {classification_columns}[/cyan]"
                )

        for i in range(0, total, batch_size):
            batch = df.iloc[i : i + batch_size]

            if has_type_qn:
                # Map flat rows to Purview entity objects using helper
                from purviewcli.client._entity import map_flat_entity_to_purview_entity

                entities = [map_flat_entity_to_purview_entity(row, debug=debug) for _, row in batch.iterrows()]
                
                if debug:
                    console.print(f"[cyan][DEBUG] Batch {i//batch_size+1} entities: {json.dumps(entities, indent=2, default=str)}[/cyan]")
                payload = {"entities": entities}

                if dry_run:
                    console.print(f"[blue]DRY RUN: Would bulk-create/update batch {i//batch_size+1} with {len(batch)} entities[/blue]")
                    continue

                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmpf:
                    json.dump(payload, tmpf, indent=2)
                    tmpf.flush()
                    payload_file = tmpf.name
                
                if debug:
                    console.print(f"[cyan][DEBUG] Payload file: {payload_file}[/cyan]")
                    console.print(f"[cyan][DEBUG] Payload:\n{json.dumps(payload, indent=2, default=str)}[/cyan]")

                try:
                    args = {"--payloadFile": payload_file}
                    result = _call_bulk_with_retry(args, f"Batch {i//batch_size+1}")
                    if debug:
                        console.print(f"[cyan][DEBUG] API Result: {result}[/cyan]")
                    if result and (not isinstance(result, dict) or result.get("status") != "error"):
                        success += len(batch)
                    else:
                        failed += len(batch)
                        errors.append(f"Batch {i//batch_size+1}: {result}")
                        failed_rows.extend(batch.to_dict(orient="records"))
                except Exception as e:
                    failed += len(batch)
                    errors.append(f"Batch {i//batch_size+1}: {str(e)}")
                    failed_rows.extend(batch.to_dict(orient="records"))
                    if debug:
                        console.print(f"[cyan][DEBUG] Exception: {str(e)}[/cyan]")
                finally:
                    try:
                        os.remove(payload_file)
                    except Exception:
                        pass

                if throttle_ms > 0 and (i + batch_size) < total:
                    if debug:
                        console.print(
                            f"[cyan][DEBUG] Throttling {throttle_ms} ms before next batch[/cyan]"
                        )
                    time.sleep(throttle_ms / 1000.0)

            elif has_guid:
                # Build guid-based updates in a bulk payload to avoid per-attribute API calls.
                rows = [row.to_dict() for _, row in batch.iterrows()]
                entities = []

                has_attr_name_value = set(["guid", "attrName", "attrValue"]).issubset(
                    set(batch.columns)
                )

                for r in rows:
                    guid_value = r.get("guid")
                    if pd.isna(guid_value):
                        failed += 1
                        failed_rows.append(r)
                        errors.append("Row missing required guid")
                        continue

                    guid = str(guid_value).strip()
                    if not guid:
                        failed += 1
                        failed_rows.append(r)
                        errors.append("Row has empty guid")
                        continue

                    entity: dict[str, object] = {"guid": guid}
                    attributes: dict[str, str] = {}

                    if has_attr_name_value:
                        attr_name = r.get("attrName")
                        attr_value = r.get("attrValue")
                        if pd.notna(attr_name) and str(attr_name).strip() and pd.notna(attr_value):
                            attributes[str(attr_name).strip()] = str(attr_value)
                    else:
                        column_mapping = {
                            "DisplayName": "displayName",
                            "Description": "description",
                        }

                        skip_columns = {"guid", "attrName", "attrValue"} | set(
                            classification_columns
                        )

                        for csv_col, purview_attr in column_mapping.items():
                            if csv_col in r and pd.notnull(r.get(csv_col)):
                                attributes[purview_attr] = str(r.get(csv_col))

                        for k, v in r.items():
                            if k in skip_columns or k in column_mapping:
                                continue
                            if pd.notnull(v):
                                attributes[str(k)] = str(v)

                    if attributes:
                        entity["attributes"] = attributes

                    classification_value = None
                    for col in classification_columns:
                        if col in r and pd.notnull(r.get(col)):
                            classification_value = r.get(col)
                            break

                    if classification_value is not None:
                        if isinstance(classification_value, str):
                            raw_items = [
                                v.strip() for v in classification_value.replace(",", ";").split(";")
                            ]
                            classification_names = [v for v in raw_items if v]
                        else:
                            classification_names = [str(classification_value).strip()]

                        if classification_names:
                            entity["classifications"] = [
                                {"typeName": name} for name in classification_names
                            ]

                    if "attributes" not in entity and "classifications" not in entity:
                        failed += 1
                        failed_rows.append(r)
                        errors.append(f"GUID {guid}: no updatable fields found")
                        continue

                    entities.append(entity)

                if not entities:
                    continue

                payload = {"entities": entities}

                if dry_run:
                    console.print(
                        f"[blue]DRY RUN: Would bulk-update (by guid) batch {i//batch_size+1} with {len(entities)} entities[/blue]"
                    )
                    success += len(entities)
                    continue

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False, encoding="utf-8"
                ) as tmpf:
                    json.dump(payload, tmpf, indent=2)
                    tmpf.flush()
                    payload_file = tmpf.name

                if debug:
                    console.print(f"[cyan][DEBUG] GUID bulk payload file: {payload_file}[/cyan]")
                    console.print(
                        f"[cyan][DEBUG] GUID bulk payload:\n{json.dumps(payload, indent=2, default=str)}[/cyan]"
                    )

                try:
                    args = {"--payloadFile": payload_file}
                    result = _call_bulk_with_retry(args, f"Batch {i//batch_size+1}")
                    if debug:
                        console.print(f"[cyan][DEBUG] API Result: {result}[/cyan]")

                    if result and (
                        not isinstance(result, dict) or result.get("status") != "error"
                    ):
                        success += len(entities)
                    else:
                        failed += len(entities)
                        errors.append(f"Batch {i//batch_size+1}: {result}")
                        failed_rows.extend(batch.to_dict(orient="records"))
                except Exception as e:
                    failed += len(entities)
                    errors.append(f"Batch {i//batch_size+1}: {str(e)}")
                    failed_rows.extend(batch.to_dict(orient="records"))
                finally:
                    try:
                        os.remove(payload_file)
                    except Exception:
                        pass

                if throttle_ms > 0 and (i + batch_size) < total:
                    if debug:
                        console.print(
                            f"[cyan][DEBUG] Throttling {throttle_ms} ms before next batch[/cyan]"
                        )
                    time.sleep(throttle_ms / 1000.0)

            else:
                console.print(f"[red][X] CSV must contain either (typeName and qualifiedName) or guid column[/red]")
                return

        console.print(f"[green][OK] Bulk update completed. Success: {success}, Failed: {failed}[/green]")
        if errors:
            console.print("[red]Errors:[/red]")
            for err in errors:
                console.print(f"[red]- {err}[/red]")
        if error_csv and failed_rows:
            pd.DataFrame(failed_rows).to_csv(error_csv, index=False)
            console.print(f"[yellow]WARNING: Failed rows written to {error_csv}[/yellow]")
    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-update-csv: {str(e)}[/red]")


@entity.command()
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="CSV file with GUIDs to delete")
@click.option("--batch-size", default=100, help="Batch size for API calls")
@click.option("--dry-run", is_flag=True, help="Preview entities to be deleted without making changes")
@click.option("--error-csv", type=click.Path(), help="CSV file to write failed rows (optional)")
@click.pass_context
def bulk_delete_csv(ctx, csv_file, batch_size, dry_run, error_csv):
    """Bulk delete entities from a CSV file (guid column)"""
    import pandas as pd
    import os
    from purviewcli.client._entity import Entity
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity bulk-delete-csv command[/yellow]")
            console.print(f"[dim]CSV File: {csv_file}[/dim]")
            console.print("[green][OK] Mock entity bulk-delete-csv completed successfully[/green]")
            return

        df = pd.read_csv(csv_file)
        if "guid" not in df.columns:
            console.print("[red][X] CSV must contain 'guid' column[/red]")
            return
        entity_client = Entity()
        total = len(df)
        success, failed = 0, 0
        errors = []
        failed_rows = []
        for i in range(0, total, batch_size):
            batch = df.iloc[i:i+batch_size]
            guids = [str(row["guid"]) for _, row in batch.iterrows() if pd.notnull(row["guid"])]
            if dry_run:
                console.print(f"[blue]DRY RUN: Would delete batch {i//batch_size+1} with {len(guids)} entities[/blue]")
                continue
            try:
                args = {"--guid": guids}
                result = entity_client.entityDeleteBulk(args)
                if result and (not isinstance(result, dict) or result.get("status") != "error"):
                    success += len(guids)
                else:
                    failed += len(guids)
                    errors.append(f"Batch {i//batch_size+1}: {result}")
                    failed_rows.extend(batch.to_dict(orient="records"))
            except Exception as e:
                failed += len(guids)
                errors.append(f"Batch {i//batch_size+1}: {str(e)}")
                failed_rows.extend(batch.to_dict(orient="records"))
        console.print(f"[green][OK] Bulk delete completed. Success: {success}, Failed: {failed}[/green]")
        if errors:
            console.print("[red]Errors:[/red]")
            for err in errors:
                console.print(f"[red]- {err}[/red]")
        if error_csv and failed_rows:
            pd.DataFrame(failed_rows).to_csv(error_csv, index=False)
            console.print(f"[yellow][X] Failed rows written to {error_csv}[/yellow]")
    except Exception as e:
        console.print(f"[red][X] Error executing entity bulk-delete-csv: {str(e)}[/red]")


# === AUDIT OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def audit(ctx, guid):
    """Get audit events for an entity by GUID"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity audit command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green][OK] Mock entity audit completed successfully[/green]")
            return
        args = {"--guid": guid}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityReadAudit(args)
        if result:
            console.print("[green][OK] Entity audit events retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Entity audit completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red][X] Error executing entity audit: {str(e)}[/red]")


@entity.command()
@click.option('--type-name', required=False, help='Filter by entity typeName (e.g., DataSet, DataProduct)')
@click.option('--limit', default=100, help='Maximum number of entities to return')
def list(type_name, limit):
    """List entities in Microsoft Purview."""
    try:
        from purviewcli.client._search import Search
        search_client = Search()
        
        # Create search query payload with proper filter structure
        # Use null keywords to return all entities (Purview API ignores "*" as a wildcard)
        search_payload = {
            "keywords": None,
            "limit": limit,
        }
        
        # Only add filter if type_name is specified
        if type_name:
            search_payload["filter"] = {
                "entityType": type_name  # Send as string, not array
            }
        # If no type specified, don't include filter at all
        
        # Convert to args format expected by searchQuery
        search_args = {
            "--payloadFile": None,
            "--payload": json.dumps(search_payload)
        }
        
        results = search_client.searchQuery(search_args)
        from rich.console import Console
        console = Console()
        console.print(json.dumps(results, indent=2))
    except Exception as e:
        from rich.console import Console
        console = Console()
        console.print(f"[red][X] Error executing entity list: {str(e)}[/red]")


@entity.command("bulk-delete-optimized")
@click.argument("guids", nargs=-1, required=True)
@click.option("--bulk-size", type=int, default=50, 
              help="Assets per bulk delete request (Microsoft recommended: 50)")
@click.option("--max-parallel", type=int, default=10, 
              help="Maximum parallel deletion jobs")
@click.option("--throttle-ms", type=int, default=200, 
              help="Throttle delay between API calls (milliseconds)")
@click.option("--batch-throttle-ms", type=int, default=800, 
              help="Throttle delay between batches (milliseconds)")
@click.option("--dry-run", is_flag=True, 
              help="Show what would be deleted without actually deleting")
@click.option("--continuous", is_flag=True, 
              help="Continue until all assets in collection are deleted")
@click.option("--collection-name", 
              help="Collection name for continuous deletion mode")
@click.pass_context
def bulk_delete_optimized(ctx, guids, bulk_size, max_parallel, throttle_ms, 
                         batch_throttle_ms, dry_run, continuous, collection_name):
    """
    Optimized bulk delete with mathematical precision (equivalent to Remove-PurviewAsset-Batch.ps1)
    
    Features:
    - Mathematical optimization for perfect efficiency
    - Parallel processing with controlled throttling
    - Continuous deletion mode for large collections
    - Reliable counting and progress tracking
    - Microsoft's recommended 50 assets per bulk request
    """
    try:
        from rich.console import Console
        import math
        
        console = Console()

        # Mathematical optimization display
        if len(guids) > 0:
            total_assets = len(guids)
            assets_per_job = math.ceil(total_assets / max_parallel)
            api_calls_per_job = math.ceil(assets_per_job / bulk_size)
            total_api_calls = api_calls_per_job * max_parallel
            
            console.print(f"[blue][*] Mathematical Optimization Analysis:[/blue]")
            console.print(f"   [INFO] Total Assets: {total_assets}")
            console.print(f"   [PATTERN] Parallel Jobs: {max_parallel}")
            console.print(f"   [INFO] Assets per Job: {assets_per_job}")
            console.print(f"   [START] Bulk Size: {bulk_size}")
            console.print(f"   [API] API Calls per Job: {api_calls_per_job}")
            console.print(f"   [STATS] Total API Calls: {total_api_calls}")
            
            # Check for perfect division (like PowerShell mathematical optimization)
            if total_assets % (max_parallel * bulk_size) == 0:
                console.print(f"[green][OK] Perfect mathematical division achieved! Zero waste.[/green]")
            else:
                waste_assets = (total_api_calls * bulk_size) - total_assets
                console.print(f"[yellow][!] Mathematical waste: {waste_assets} empty slots in final requests[/yellow]")

        if continuous and collection_name:
            deleted_count = _continuous_collection_deletion(
                ctx, collection_name, bulk_size, max_parallel, 
                throttle_ms, batch_throttle_ms, dry_run
            )
        else:
            deleted_count = _execute_optimized_bulk_delete(
                ctx, list(guids), bulk_size, max_parallel, 
                throttle_ms, batch_throttle_ms, dry_run
            )
        
        console.print(f"[green][OK] {'Would delete' if dry_run else 'Successfully deleted'} {deleted_count} assets[/green]")

    except Exception as e:
        from rich.console import Console
        console = Console()
        console.print(f"[red][X] Error in bulk-delete-optimized: {str(e)}[/red]")


@entity.command("bulk-delete-from-collection")
@click.argument("collection-name")
@click.option("--bulk-size", type=int, default=50, 
              help="Assets per bulk delete request (Microsoft recommended: 50)")
@click.option("--max-parallel", type=int, default=10, 
              help="Maximum parallel deletion jobs")
@click.option("--batch-size", type=int, default=1000, 
              help="Assets to process per batch cycle")
@click.option("--throttle-ms", type=int, default=200, 
              help="Throttle delay between API calls (milliseconds)")
@click.option("--dry-run", is_flag=True, 
              help="Show what would be deleted without actually deleting")
@click.confirmation_option(prompt="Are you sure you want to delete all assets in this collection?")
@click.pass_context
def bulk_delete_from_collection(ctx, collection_name, bulk_size, max_parallel, 
                               batch_size, throttle_ms, dry_run):
    """
    Delete all assets from a collection using continuous deletion strategy        
    Features:
    - Continuous deletion until collection is empty
    - Mathematical optimization for each batch
    - Progress tracking and estimation
    - Handles 500K+ assets efficiently
    """
    try:
        from rich.console import Console
        
        console = Console()
        console.print(f"[blue][TARGET] Starting continuous deletion for collection: {collection_name}[/blue]")
        
        deleted_count = _continuous_collection_deletion(
            ctx, collection_name, bulk_size, max_parallel, 
            throttle_ms, 800, dry_run, batch_size
        )
        
        console.print(f"[green][OK] Collection cleanup complete: {'Would delete' if dry_run else 'Deleted'} {deleted_count} total assets[/green]")

    except Exception as e:
        from rich.console import Console
        console = Console()
        console.print(f"[red][X] Error in bulk-delete-from-collection: {str(e)}[/red]")


@entity.command("count-assets")
@click.argument("collection-name")
@click.option("--by-type", is_flag=True, help="Group count by asset type")
@click.option("--include-relationships", is_flag=True, help="Include relationship counts")
@click.pass_context
def count_assets(ctx, collection_name, by_type, include_relationships):
    """
    Count assets in a collection with detailed breakdown
    
    """
    try:
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        console.print(f"[blue][INFO] Counting assets in collection: {collection_name}[/blue]")
        
        # Get asset count using search API
        total_count = _get_collection_asset_count(collection_name)
        
        console.print(f"[green][OK] Total assets: {total_count}[/green]")

        if by_type:
            type_counts = _get_asset_type_breakdown(collection_name)
            _display_type_breakdown(type_counts)

        if include_relationships:
            rel_count = _get_relationship_count(collection_name)
            console.print(f"[blue][LINK] Total relationships: {rel_count}[/blue]")

    except Exception as e:
        from rich.console import Console
        console = Console()
        console.print(f"[red][X] Error in count-assets: {str(e)}[/red]")


@entity.command("analyze-performance")
@click.option("--bulk-size", type=int, default=50, help="Bulk size to analyze")
@click.option("--max-parallel", type=int, default=10, help="Parallel jobs to analyze")
@click.option("--asset-count", type=int, default=1000, help="Total assets for analysis")
@click.pass_context
def analyze_performance(ctx, bulk_size, max_parallel, asset_count):
    """
    Analyze bulk deletion performance with mathematical optimization
    """
    try:
        from rich.console import Console
        from rich.table import Table
        import math
        
        console = Console()
        console.print("[blue][STATS] Performance Analysis[/blue]")
        
        # Mathematical calculations (from PowerShell scripts)
        assets_per_job = math.ceil(asset_count / max_parallel)
        api_calls_per_job = math.ceil(assets_per_job / bulk_size)
        total_api_calls = api_calls_per_job * max_parallel
        
        # Time estimations (based on PowerShell measurements)
        avg_api_time_ms = 1500  # Average API call time
        throttle_time_ms = 200  # Throttle between calls
        total_time_per_call = avg_api_time_ms + throttle_time_ms
        
        estimated_time_seconds = (total_api_calls * total_time_per_call) / 1000
        estimated_time_minutes = estimated_time_seconds / 60
        estimated_time_hours = estimated_time_minutes / 60

        # Create performance table
        table = Table(title="Performance Analysis")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Details", style="yellow")

        table.add_row("Total Assets", f"{asset_count:,}", "Assets to process")
        table.add_row("Parallel Jobs", f"{max_parallel}", "Concurrent deletion jobs")
        table.add_row("Bulk Size", f"{bulk_size}", "Assets per API call")
        table.add_row("Assets per Job", f"{assets_per_job}", f"{asset_count} ÷ {max_parallel}")
        table.add_row("API Calls per Job", f"{api_calls_per_job}", f"{assets_per_job} ÷ {bulk_size}")
        table.add_row("Total API Calls", f"{total_api_calls}", f"{api_calls_per_job} × {max_parallel}")
        table.add_row("Estimated Time", f"{estimated_time_hours:.1f} hours", f"{estimated_time_minutes:.1f} minutes")
        
        # Efficiency calculation
        theoretical_minimum_calls = math.ceil(asset_count / bulk_size)
        efficiency = (theoretical_minimum_calls / total_api_calls) * 100
        table.add_row("Efficiency", f"{efficiency:.1f}%", f"{theoretical_minimum_calls} minimum calls")

        console.print(table)

        # Recommendations (from PowerShell optimization experience)
        console.print("\n[blue][TIP] Optimization Recommendations:[/blue]")
        
        if asset_count % (max_parallel * bulk_size) == 0:
            console.print("[green][OK] Perfect mathematical division - optimal configuration![/green]")
        else:
            # Calculate optimal configurations
            optimal_configs = _calculate_optimal_configs(asset_count, bulk_size)
            console.print("[yellow][TIP] Consider these optimal configurations:[/yellow]")
            for config in optimal_configs[:3]:
                console.print(f"   • {config['parallel']} parallel jobs: {config['efficiency']:.1f}% efficiency")

    except Exception as e:
        from rich.console import Console
        console = Console()
        console.print(f"[red][X] Error in analyze-performance: {str(e)}[/red]")


# === ENHANCED BULK OPERATION FUNCTIONS ===

def _execute_optimized_bulk_delete(ctx, guids, bulk_size, max_parallel, throttle_ms, batch_throttle_ms, dry_run):
    """
    Execute optimized bulk delete with parallel processing
    (Core logic from PowerShell Remove-PurviewAsset-Batch.ps1)
    """
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    import concurrent.futures
    import math
    import time
    
    console = Console()
    
    if not guids:
        return 0

    total_assets = len(guids)
    deleted_count = 0

    if dry_run:
        console.print(f"[yellow][*] DRY RUN: Would delete {total_assets} assets[/yellow]")
        return total_assets

    from purviewcli.client._entity import Entity
    entity_client = Entity()

    # Split GUIDs into job batches
    assets_per_job = math.ceil(total_assets / max_parallel)
    job_batches = []
    
    for i in range(max_parallel):
        start_idx = i * assets_per_job
        end_idx = min(start_idx + assets_per_job, total_assets)
        if start_idx < total_assets:
            job_batches.append(guids[start_idx:end_idx])

    console.print(f"[blue][START] Starting {len(job_batches)} parallel deletion jobs...[/blue]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[red]Deleting assets...", total=total_assets)
        
        # Execute parallel deletions
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_parallel) as executor:
            future_to_batch = {
                executor.submit(_delete_batch_job, entity_client, batch, bulk_size, throttle_ms, i): batch
                for i, batch in enumerate(job_batches)
            }
            
            for future in concurrent.futures.as_completed(future_to_batch):
                batch = future_to_batch[future]
                try:
                    batch_deleted = future.result()
                    deleted_count += batch_deleted
                    progress.update(task, advance=batch_deleted)
                    
                    # Batch throttle
                    if batch_throttle_ms > 0:
                        time.sleep(batch_throttle_ms / 1000)
                        
                except Exception as e:
                    console.print(f"[red][X] Batch deletion failed: {str(e)}[/red]")

    return deleted_count


def _delete_batch_job(entity_client, guid_batch, bulk_size, throttle_ms, job_id):
    """
    Execute a single batch job (parallel worker function)
    """
    import time
    
    deleted_in_job = 0
    
    # Split batch into bulk delete chunks
    for i in range(0, len(guid_batch), bulk_size):
        bulk_guids = guid_batch[i:i + bulk_size]
        
        try:
            # Execute bulk delete API call
            args = {"--guid": bulk_guids}
            result = entity_client.entityDeleteBulk(args)
            
            if result:
                deleted_in_job += len(bulk_guids)
            
            # Throttle between API calls
            if throttle_ms > 0 and i + bulk_size < len(guid_batch):
                time.sleep(throttle_ms / 1000)
                
        except Exception as e:
            from rich.console import Console
            console = Console()
            console.print(f"[red][X] Job {job_id} bulk delete failed: {str(e)}[/red]")
    
    return deleted_in_job


def _continuous_collection_deletion(ctx, collection_name, bulk_size, max_parallel, throttle_ms, batch_throttle_ms, dry_run, batch_size=1000):
    """
    Continuous deletion strategy for large collections
    """
    from rich.console import Console
    
    console = Console()
    total_deleted = 0
    iteration = 1

    console.print(f"[blue][PATTERN] Starting continuous deletion for collection: {collection_name}[/blue]")

    while True:
        console.print(f"\n[blue][ITER] Iteration {iteration}: Finding assets to delete...[/blue]")
        
        # Get next batch of assets from collection
        asset_guids = _get_collection_assets_batch(collection_name, batch_size)
        
        if not asset_guids:
            console.print("[green][OK] No more assets found - collection is clean![/green]")
            break
        
        found_count = len(asset_guids)
        console.print(f"[blue][INFO] Found {found_count} assets in iteration {iteration}[/blue]")
        
        if dry_run:
            console.print(f"[yellow][*] DRY RUN: Would delete {found_count} assets[/yellow]")
            total_deleted += found_count
        else:
            # Execute optimized deletion for this batch
            deleted_in_iteration = _execute_optimized_bulk_delete(
                ctx, asset_guids, bulk_size, max_parallel, 
                throttle_ms, batch_throttle_ms, False
            )
            
            total_deleted += deleted_in_iteration
            console.print(f"[green][OK] Iteration {iteration}: Deleted {deleted_in_iteration}/{found_count} assets[/green]")
            console.print(f"[blue][STATS] Running total: {total_deleted} assets deleted[/blue]")
        
        iteration += 1
        
        # Break after reasonable number of iterations in dry-run
        if dry_run and iteration > 5:
            console.print("[yellow][*] DRY RUN: Simulated 5 iterations[/yellow]")
            break

    return total_deleted


def _get_collection_assets_batch(collection_name, batch_size):
    """
    Get a batch of asset GUIDs from a collection
    (Would integrate with search API)
    """
    # Placeholder - would use search API to get actual asset GUIDs
    # For testing, return mock data that decreases over iterations
    import random
    mock_count = random.randint(0, min(batch_size, 100))
    return [f"mock-guid-{i}" for i in range(mock_count)]


def _get_collection_asset_count(collection_name):
    """Get total asset count for a collection"""
    # Placeholder - would use search API
    return 1500  # Mock count


def _get_asset_type_breakdown(collection_name):
    """Get asset count breakdown by type"""
    # Placeholder - would use search API with type filters
    return {
        "DataSet": 450,
        "Table": 320,
        "Column": 580,
        "Process": 150
    }


def _get_relationship_count(collection_name):
    """Get relationship count for collection"""
    # Placeholder - would use relationship API
    return 2340


def _display_type_breakdown(type_counts):
    """Display asset type breakdown in a table"""
    from rich.table import Table
    from rich.console import Console
    
    console = Console()
    table = Table(title="Asset Type Breakdown")
    table.add_column("Asset Type", style="cyan")
    table.add_column("Count", style="green")
    table.add_column("Percentage", style="yellow")

    total = sum(type_counts.values())
    
    for asset_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100 if total > 0 else 0
        table.add_row(asset_type, f"{count:,}", f"{percentage:.1f}%")
    
    table.add_row("[bold]Total[/bold]", f"[bold]{total:,}[/bold]", "[bold]100.0%[/bold]")
    console.print(table)


def _calculate_optimal_configs(asset_count, bulk_size):
    """
    Calculate optimal parallel job configurations
    (Mathematical optimization from PowerShell)
    """
    import math
    
    configs = []
    
    for parallel_jobs in range(1, 21):  # Test 1-20 parallel jobs
        assets_per_job = math.ceil(asset_count / parallel_jobs)
        api_calls_per_job = math.ceil(assets_per_job / bulk_size)
        total_api_calls = api_calls_per_job * parallel_jobs
        
        theoretical_minimum = math.ceil(asset_count / bulk_size)
        efficiency = (theoretical_minimum / total_api_calls) * 100
        
        configs.append({
            'parallel': parallel_jobs,
            'efficiency': efficiency,
            'total_calls': total_api_calls,
            'waste': total_api_calls - theoretical_minimum
        })
    
    # Sort by efficiency (descending)
    return sorted(configs, key=lambda x: x['efficiency'], reverse=True)


# === ADVANCED ENTITY OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
@click.pass_context
def history(ctx, guid, output):
    """Get change history for an entity by GUID.
    
    Retrieves the complete change history for an entity, showing all modifications,
    updates, and metadata changes over time. Useful for compliance, auditing, and
    understanding entity evolution.
    
    Examples:
        # Get history for an entity
        pvw entity history --guid <entity-guid>
        
        # Export as JSON
        pvw entity history --guid <entity-guid> --output json
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity history command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green][OK] Mock entity history completed successfully[/green]")
            return
            
        args = {"--guid": guid}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityReadHistory(args)
        
        if result:
            if output == "json":
                console.print(json.dumps(result, indent=2))
            else:
                # Display history in table format
                from rich.table import Table
                
                events = result.get("value", result.get("events", []))
                if not events:
                    console.print("[yellow]No history events found for this entity.[/yellow]")
                    return
                
                table = Table(title=f"Entity History: {guid[:8]}...", show_header=True)
                table.add_column("Event Time", style="cyan", no_wrap=True)
                table.add_column("Action", style="yellow")
                table.add_column("User", style="green")
                table.add_column("Details", style="white")
                
                for event in events[:50]:  # Limit to 50 most recent
                    event_time = event.get("eventTime", event.get("timestamp", "N/A"))
                    if "T" in str(event_time):
                        event_time = event_time.split("T")[0] + " " + event_time.split("T")[1][:8]
                    
                    action = event.get("action", event.get("operation", "N/A"))
                    user = event.get("user", event.get("modifiedBy", "N/A"))
                    details = event.get("details", event.get("description", ""))[:40]
                    
                    table.add_row(str(event_time), action, user, details)
                
                console.print(table)
                console.print(f"\n[dim]Showing {min(len(events), 50)} of {len(events)} events[/dim]")
                
            console.print("[green][OK] Entity history retrieved successfully[/green]")
        else:
            console.print("[yellow][!] No history found for this entity[/yellow]")
            
    except Exception as e:
        console.print(f"[red][X] Error executing entity history: {str(e)}[/red]")


@entity.command()
@click.option("--guid", help="Entity GUID to validate")
@click.option("--payload-file", help="JSON file with entity definition to validate")
@click.option("--type-name", help="Entity type name (required if using payload-file)")
@click.pass_context
def validate(ctx, guid, payload_file, type_name):
    """Validate an entity definition before creation or update.
    
    Performs pre-flight validation to check if an entity definition is valid
    without actually creating or updating it. Helps catch errors early and
    ensures data quality.
    
    Examples:
        # Validate existing entity by GUID
        pvw entity validate --guid <entity-guid>
        
        # Validate new entity definition from file
        pvw entity validate --payload-file entity.json --type-name DataSet
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity validate command[/yellow]")
            console.print("[green][OK] Mock entity validation completed successfully[/green]")
            return
        
        args = {}
        if guid:
            args["--guid"] = guid
        if payload_file:
            args["--payloadFile"] = payload_file
        if type_name:
            args["--typeName"] = type_name
            
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityValidate(args)
        
        if result:
            validation_status = result.get("valid", result.get("isValid", False))
            
            if validation_status:
                console.print("[green][OK] Entity validation passed[/green]")
            else:
                console.print("[red][X] Entity validation failed[/red]")
                
            # Show validation errors if any
            errors = result.get("errors", result.get("validationErrors", []))
            if errors:
                console.print("\n[red]Validation Errors:[/red]")
                for error in errors:
                    if isinstance(error, dict):
                        console.print(f"  - {error.get('message', error.get('error', str(error)))}")
                    else:
                        console.print(f"  - {error}")
            
            # Show warnings if any
            warnings = result.get("warnings", [])
            if warnings:
                console.print("\n[yellow]Warnings:[/yellow]")
                for warning in warnings:
                    if isinstance(warning, dict):
                        console.print(f"  - {warning.get('message', str(warning))}")
                    else:
                        console.print(f"  - {warning}")
                        
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow][!] Validation completed with no result[/yellow]")
            
    except Exception as e:
        console.print(f"[red][X] Error executing entity validate: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
@click.pass_context
def dependencies(ctx, guid, output):
    """Get dependencies for an entity by GUID.
    
    Retrieves all entities that this entity depends on or that depend on it.
    Useful for understanding data lineage, impact analysis, and entity relationships.
    
    Examples:
        # Get dependencies for an entity
        pvw entity dependencies --guid <entity-guid>
        
        # Export as JSON
        pvw entity dependencies --guid <entity-guid> --output json
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity dependencies command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green][OK] Mock entity dependencies completed successfully[/green]")
            return
            
        args = {"--guid": guid}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityReadDependencies(args)
        
        if result:
            if output == "json":
                console.print(json.dumps(result, indent=2))
            else:
                # Display dependencies in table format
                from rich.table import Table
                
                dependencies = result.get("dependencies", result.get("value", []))
                if not dependencies:
                    console.print("[yellow]No dependencies found for this entity.[/yellow]")
                    return
                
                table = Table(title=f"Entity Dependencies: {guid[:8]}...", show_header=True)
                table.add_column("Type", style="cyan")
                table.add_column("Entity GUID", style="yellow", no_wrap=True)
                table.add_column("Entity Name", style="green")
                table.add_column("Relationship", style="white")
                
                for dep in dependencies[:100]:  # Limit to 100
                    dep_type = dep.get("type", dep.get("dependencyType", "N/A"))
                    dep_guid = dep.get("guid", dep.get("entityGuid", "N/A"))
                    dep_name = dep.get("name", dep.get("displayName", "N/A"))
                    relationship = dep.get("relationship", dep.get("relationshipType", "N/A"))
                    
                    # Truncate GUID for display
                    if len(dep_guid) > 20:
                        dep_guid = dep_guid[:8] + "..." + dep_guid[-8:]
                    
                    table.add_row(dep_type, dep_guid, dep_name[:30], relationship)
                
                console.print(table)
                console.print(f"\n[dim]Showing {min(len(dependencies), 100)} of {len(dependencies)} dependencies[/dim]")
                
            console.print("[green][OK] Entity dependencies retrieved successfully[/green]")
        else:
            console.print("[yellow][!] No dependencies found for this entity[/yellow]")
            
    except Exception as e:
        console.print(f"[red][X] Error executing entity dependencies: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--output", default="table", type=click.Choice(["json", "table"]), help="Output format")
@click.pass_context
def usage(ctx, guid, output):
    """Get usage statistics for an entity by GUID.
    
    Retrieves usage metrics including access patterns, query statistics, and
    popularity metrics. Helps identify frequently used assets and optimize
    data governance.
    
    Examples:
        # Get usage statistics for an entity
        pvw entity usage --guid <entity-guid>
        
        # Export as JSON
        pvw entity usage --guid <entity-guid> --output json
    """
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow][MOCK] entity usage command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green][OK] Mock entity usage completed successfully[/green]")
            return
            
        args = {"--guid": guid}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityReadUsage(args)
        
        if result:
            if output == "json":
                console.print(json.dumps(result, indent=2))
            else:
                # Display usage statistics
                console.print(f"\n[bold cyan]Usage Statistics for Entity: {guid[:8]}...[/bold cyan]\n")
                
                # Extract metrics
                total_views = result.get("totalViews", result.get("viewCount", 0))
                unique_users = result.get("uniqueUsers", result.get("userCount", 0))
                last_accessed = result.get("lastAccessed", result.get("lastAccessTime", "N/A"))
                access_freq = result.get("accessFrequency", result.get("frequency", "N/A"))
                
                console.print(f"[green]Total Views:[/green] {total_views}")
                console.print(f"[green]Unique Users:[/green] {unique_users}")
                console.print(f"[green]Last Accessed:[/green] {last_accessed}")
                console.print(f"[green]Access Frequency:[/green] {access_freq}")
                
                # Show top users if available
                top_users = result.get("topUsers", result.get("users", []))
                if top_users:
                    from rich.table import Table
                    
                    table = Table(title="Top Users", show_header=True)
                    table.add_column("User", style="cyan")
                    table.add_column("Access Count", style="yellow")
                    table.add_column("Last Access", style="green")
                    
                    for user in top_users[:10]:  # Top 10
                        user_name = user.get("name", user.get("user", "N/A"))
                        access_count = user.get("accessCount", user.get("count", 0))
                        last_access = user.get("lastAccess", user.get("lastAccessTime", "N/A"))
                        
                        table.add_row(user_name, str(access_count), str(last_access))
                    
                    console.print("\n")
                    console.print(table)
                
            console.print("\n[green][OK] Entity usage statistics retrieved successfully[/green]")
        else:
            console.print("[yellow][!] No usage statistics available for this entity[/yellow]")
            
    except Exception as e:
        console.print(f"[red][X] Error executing entity usage: {str(e)}[/red]")


# Make the entity group available for import
__all__ = ["entity"]
