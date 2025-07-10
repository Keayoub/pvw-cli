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
from rich.console import Console

console = Console()


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
@click.pass_context
def read(ctx, guid, ignore_relationships, min_ext_info):
    """Read entity information by GUID"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity read command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(f"[dim]Ignore Relationships: {ignore_relationships}[/dim]")
            console.print(f"[dim]Min Ext Info: {min_ext_info}[/dim]")
            console.print("[green]✓ Mock entity read completed successfully[/green]")
            return

        args = {
            "--guid": guid,
            "--ignoreRelationships": ignore_relationships,
            "--minExtInfo": min_ext_info,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityRead(args)

        if result:
            console.print("[green]✓ Entity read completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity read completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity read: {str(e)}[/red]")


@entity.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing entity data",
)
@click.pass_context
def create(ctx, payload_file):
    """Create a new entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity create command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity create completed successfully[/green]")
            return

        args = {"--payloadFile": payload_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityCreate(args)

        if result:
            console.print("[green]✓ Entity create completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity create completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity create: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def delete(ctx, guid):
    """Delete an entity by GUID"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity delete command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green]✓ Mock entity delete completed successfully[/green]")
            return

        args = {"--guid": guid}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityDelete(args)

        if result:
            console.print("[green]✓ Entity delete completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity delete completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity delete: {str(e)}[/red]")


@entity.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing bulk entity data",
)
@click.pass_context
def bulk_create(ctx, payload_file):
    """Create multiple entities in bulk"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity bulk-create command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity bulk-create completed successfully[/green]")
            return

        args = {"--payloadFile": payload_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityBulkCreateOrUpdate(args)

        if result:
            console.print("[green]✓ Entity bulk-create completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity bulk-create completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-create: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity bulk-read command[/yellow]")
            console.print(f"[dim]GUIDs: {', '.join(guid)}[/dim]")
            console.print("[green]✓ Mock entity bulk-read completed successfully[/green]")
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
            console.print("[green]✓ Entity bulk-read completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity bulk-read completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-read: {str(e)}[/red]")


@entity.command()
@click.option(
    "--guid", required=True, multiple=True, help="Entity GUIDs to delete (can specify multiple)"
)
@click.pass_context
def bulk_delete(ctx, guid):
    """Delete multiple entities by their GUIDs"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity bulk-delete command[/yellow]")
            console.print(f"[dim]GUIDs: {', '.join(guid)}[/dim]")
            console.print("[green]✓ Mock entity bulk-delete completed successfully[/green]")
            return

        args = {"--guid": list(guid)}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityDeleteBulk(args)

        if result:
            console.print("[green]✓ Entity bulk-delete completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity bulk-delete completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-delete: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity read-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print("[green]✓ Mock entity read-by-attribute completed successfully[/green]")
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
            console.print("[green]✓ Entity read-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity read-by-attribute completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity read-by-attribute: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity bulk-read-by-attribute command[/yellow]")
            console.print(
                f"[dim]Type: {type_name}, Qualified Names: {', '.join(qualified_name)}[/dim]"
            )
            console.print(
                "[green]✓ Mock entity bulk-read-by-attribute completed successfully[/green]"
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
            console.print("[green]✓ Entity bulk-read-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity bulk-read-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-read-by-attribute: {str(e)}[/red]")


@entity.command()
@click.option("--type-name", required=True, help="The name of the entity type")
@click.option("--qualified-name", required=True, help="The qualified name of the entity")
@click.pass_context
def delete_by_attribute(ctx, type_name, qualified_name):
    """Delete entity by unique attributes"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity delete-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print("[green]✓ Mock entity delete-by-attribute completed successfully[/green]")
            return

        args = {
            "--typeName": type_name,
            "--qualifiedName": qualified_name,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityDeleteUniqueAttribute(args)

        if result:
            console.print("[green]✓ Entity delete-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity delete-by-attribute completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity delete-by-attribute: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity update-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print("[green]✓ Mock entity update-by-attribute completed successfully[/green]")
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
            console.print("[green]✓ Entity update-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity update-by-attribute completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity update-by-attribute: {str(e)}[/red]")


# === HEADER OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def read_header(ctx, guid):
    """Read entity header information by GUID"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity read-header command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green]✓ Mock entity read-header completed successfully[/green]")
            return

        args = {"--guid": [guid]}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadHeader(args)

        if result:
            console.print("[green]✓ Entity read-header completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity read-header completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity read-header: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--attr-name", required=True, help="The name of the attribute to update")
@click.option("--attr-value", required=True, help="The new value for the attribute")
@click.pass_context
def update_attribute(ctx, guid, attr_name, attr_value):
    """Update a specific attribute of an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity update-attribute command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Attribute: {attr_name}, Value: {attr_value}[/dim]")
            console.print("[green]✓ Mock entity update-attribute completed successfully[/green]")
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
            console.print("[green]✓ Entity update-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity update-attribute completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity update-attribute: {str(e)}[/red]")


# === CLASSIFICATION OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--classification-name", required=True, help="The name of the classification")
@click.pass_context
def read_classification(ctx, guid, classification_name):
    """Read specific classification for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity read-classification command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Classification: {classification_name}[/dim]")
            console.print("[green]✓ Mock entity read-classification completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--classificationName": classification_name,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadClassification(args)

        if result:
            console.print("[green]✓ Entity read-classification completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity read-classification completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity read-classification: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def read_classifications(ctx, guid):
    """Read all classifications for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity read-classifications command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(
                "[green]✓ Mock entity read-classifications completed successfully[/green]"
            )
            return

        args = {"--guid": [guid]}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadClassifications(args)

        if result:
            console.print("[green]✓ Entity read-classifications completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity read-classifications completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity read-classifications: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity add-classifications command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity add-classifications completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddClassifications(args)

        if result:
            console.print("[green]✓ Entity add-classifications completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity add-classifications completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity add-classifications: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity update-classifications command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print(
                "[green]✓ Mock entity update-classifications completed successfully[/green]"
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
            console.print("[green]✓ Entity update-classifications completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity update-classifications completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity update-classifications: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity remove-classification command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Classification: {classification_name}[/dim]")
            console.print(
                "[green]✓ Mock entity remove-classification completed successfully[/green]"
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
            console.print("[green]✓ Entity remove-classification completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity remove-classification completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity remove-classification: {str(e)}[/red]")


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
                "[yellow]🎭 Mock: entity add-classifications-by-attribute command[/yellow]"
            )
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print(
                "[green]✓ Mock entity add-classifications-by-attribute completed successfully[/green]"
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
                "[green]✓ Entity add-classifications-by-attribute completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity add-classifications-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red]✗ Error executing entity add-classifications-by-attribute: {str(e)}[/red]"
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
                "[yellow]🎭 Mock: entity update-classifications-by-attribute command[/yellow]"
            )
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print(
                "[green]✓ Mock entity update-classifications-by-attribute completed successfully[/green]"
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
                "[green]✓ Entity update-classifications-by-attribute completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity update-classifications-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red]✗ Error executing entity update-classifications-by-attribute: {str(e)}[/red]"
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
                "[yellow]🎭 Mock: entity remove-classification-by-attribute command[/yellow]"
            )
            console.print(
                f"[dim]Type: {type_name}, Qualified Name: {qualified_name}, Classification: {classification_name}[/dim]"
            )
            console.print(
                "[green]✓ Mock entity remove-classification-by-attribute completed successfully[/green]"
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
                "[green]✓ Entity remove-classification-by-attribute completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity remove-classification-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red]✗ Error executing entity remove-classification-by-attribute: {str(e)}[/red]"
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
            console.print("[yellow]🎭 Mock: entity bulk-add-classification command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print(
                "[green]✓ Mock entity bulk-add-classification completed successfully[/green]"
            )
            return

        args = {"--payloadFile": payload_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddClassification(args)

        if result:
            console.print("[green]✓ Entity bulk-add-classification completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity bulk-add-classification completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-add-classification: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity bulk-set-classifications command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print(
                "[green]✓ Mock entity bulk-set-classifications completed successfully[/green]"
            )
            return

        args = {"--payloadFile": payload_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityBulkSetClassifications(args)

        if result:
            console.print("[green]✓ Entity bulk-set-classifications completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity bulk-set-classifications completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-set-classifications: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity add-labels command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity add-labels completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddLabels(args)

        if result:
            console.print("[green]✓ Entity add-labels completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity add-labels completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity add-labels: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity set-labels command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity set-labels completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entitySetLabels(args)

        if result:
            console.print("[green]✓ Entity set-labels completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity set-labels completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity set-labels: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity remove-labels command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity remove-labels completed successfully[/green]")
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityRemoveLabels(args)

        if result:
            console.print("[green]✓ Entity remove-labels completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity remove-labels completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity remove-labels: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity add-labels-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print(
                "[green]✓ Mock entity add-labels-by-attribute completed successfully[/green]"
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
            console.print("[green]✓ Entity add-labels-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity add-labels-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity add-labels-by-attribute: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity set-labels-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}[/dim]")
            console.print(
                "[green]✓ Mock entity set-labels-by-attribute completed successfully[/green]"
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
            console.print("[green]✓ Entity set-labels-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity set-labels-by-attribute completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity set-labels-by-attribute: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity bulk-remove-labels command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity bulk-remove-labels completed successfully[/green]")
            return
        args = {"--payloadFile": payload_file}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityBulkRemoveLabels(args)
        if result:
            console.print("[green]✓ Entity bulk-remove-labels completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity bulk-remove-labels completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-remove-labels: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity bulk-remove-labels-by-attribute command[/yellow]")
            console.print(f"[dim]Type: {type_name}, Qualified Name: {qualified_name}, Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity bulk-remove-labels-by-attribute completed successfully[/green]")
            return
        args = {"--typeName": type_name, "--qualifiedName": qualified_name, "--payloadFile": payload_file}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityBulkRemoveLabelsByUniqueAttribute(args)
        if result:
            console.print("[green]✓ Entity bulk-remove-labels-by-attribute completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity bulk-remove-labels-by-attribute completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-remove-labels-by-attribute: {str(e)}[/red]")


# === BUSINESS METADATA OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing business metadata",
)
@click.option(
    "--is-overwrite", is_flag=True, help="Whether to overwrite existing business metadata"
)
@click.pass_context
def add_business_metadata(ctx, guid, payload_file, is_overwrite):
    """Add or update business metadata to an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity add-business-metadata command[/yellow]")
            console.print(f"[dim]GUID: {guid}, Overwrite: {is_overwrite}[/dim]")
            console.print(
                "[green]✓ Mock entity add-business-metadata completed successfully[/green]"
            )
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
            "--isOverwrite": is_overwrite,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddOrUpdateBusinessMetadata(args)

        if result:
            console.print("[green]✓ Entity add-business-metadata completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity add-business-metadata completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity add-business-metadata: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--bm-name", required=True, help="The business metadata name")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing business metadata attributes",
)
@click.pass_context
def add_business_metadata_attributes(ctx, guid, bm_name, payload_file):
    """Add or update business metadata attributes"""
    try:
        if ctx.obj.get("mock"):
            console.print(
                "[yellow]🎭 Mock: entity add-business-metadata-attributes command[/yellow]"
            )
            console.print(f"[dim]GUID: {guid}, BM Name: {bm_name}[/dim]")
            console.print(
                "[green]✓ Mock entity add-business-metadata-attributes completed successfully[/green]"
            )
            return

        args = {
            "--guid": [guid],
            "--bmName": bm_name,
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityAddOrUpdateBusinessMetadataAttributes(args)

        if result:
            console.print(
                "[green]✓ Entity add-business-metadata-attributes completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity add-business-metadata-attributes completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red]✗ Error executing entity add-business-metadata-attributes: {str(e)}[/red]"
        )


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document specifying business metadata to remove",
)
@click.pass_context
def remove_business_metadata(ctx, guid, payload_file):
    """Remove business metadata from an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity remove-business-metadata command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print(
                "[green]✓ Mock entity remove-business-metadata completed successfully[/green]"
            )
            return

        args = {
            "--guid": [guid],
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityRemoveBusinessMetadata(args)

        if result:
            console.print("[green]✓ Entity remove-business-metadata completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity remove-business-metadata completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity remove-business-metadata: {str(e)}[/red]")


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.option("--bm-name", required=True, help="The business metadata name")
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document specifying attributes to remove",
)
@click.pass_context
def remove_business_metadata_attributes(ctx, guid, bm_name, payload_file):
    """Remove business metadata attributes"""
    try:
        if ctx.obj.get("mock"):
            console.print(
                "[yellow]🎭 Mock: entity remove-business-metadata-attributes command[/yellow]"
            )
            console.print(f"[dim]GUID: {guid}, BM Name: {bm_name}[/dim]")
            console.print(
                "[green]✓ Mock entity remove-business-metadata-attributes completed successfully[/green]"
            )
            return

        args = {
            "--guid": [guid],
            "--bmName": bm_name,
            "--payloadFile": payload_file,
        }

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityRemoveBusinessMetadataAttributes(args)

        if result:
            console.print(
                "[green]✓ Entity remove-business-metadata-attributes completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity remove-business-metadata-attributes completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red]✗ Error executing entity remove-business-metadata-attributes: {str(e)}[/red]"
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
            console.print("[yellow]🎭 Mock: entity import-business-metadata command[/yellow]")
            console.print(f"[dim]BM File: {bm_file}[/dim]")
            console.print(
                "[green]✓ Mock entity import-business-metadata completed successfully[/green]"
            )
            return

        args = {"--bmFile": bm_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityImportBusinessMetadata(args)

        if result:
            console.print("[green]✓ Entity import-business-metadata completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity import-business-metadata completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]✗ Error executing entity import-business-metadata: {str(e)}[/red]")


@entity.command()
@click.pass_context
def get_business_metadata_template(ctx):
    """Get sample template for business metadata"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity get-business-metadata-template command[/yellow]")
            console.print(
                "[green]✓ Mock entity get-business-metadata-template completed successfully[/green]"
            )
            return

        args = {}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityGetBusinessMetadataTemplate(args)

        if result:
            console.print(
                "[green]✓ Entity get-business-metadata-template completed successfully[/green]"
            )
            console.print(json.dumps(result, indent=2))
        else:
            console.print(
                "[yellow]⚠ Entity get-business-metadata-template completed with no result[/yellow]"
            )

    except Exception as e:
        console.print(
            f"[red]✗ Error executing entity get-business-metadata-template: {str(e)}[/red]"
        )


# === COLLECTION OPERATIONS ===


@entity.command()
@click.option(
    "--payload-file",
    required=True,
    type=click.Path(exists=True),
    help="File path to a valid JSON document containing entities to move and target collection",
)
@click.pass_context
def move_to_collection(ctx, payload_file):
    """Move entities to a target collection"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity move-to-collection command[/yellow]")
            console.print(f"[dim]Payload File: {payload_file}[/dim]")
            console.print("[green]✓ Mock entity move-to-collection completed successfully[/green]")
            return

        args = {"--payloadFile": payload_file}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityMoveEntitiesToCollection(args)

        if result:
            console.print("[green]✓ Entity move-to-collection completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity move-to-collection completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity move-to-collection: {str(e)}[/red]")


# === SAMPLE OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def read_sample(ctx, guid):
    """Get sample data for an entity"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity read-sample command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green]✓ Mock entity read-sample completed successfully[/green]")
            return

        args = {"--guid": [guid]}

        from purviewcli.client._entity import Entity

        entity_client = Entity()
        result = entity_client.entityReadSample(args)

        if result:
            console.print("[green]✓ Entity read-sample completed successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity read-sample completed with no result[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ Error executing entity read-sample: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity bulk-classify-csv command[/yellow]")
            console.print(f"[dim]CSV File: {csv_file}[/dim]")
            console.print("[green]✓ Mock entity bulk-classify-csv completed successfully[/green]")
            return

        df = pd.read_csv(csv_file)
        if "guid" not in df.columns or "classificationName" not in df.columns:
            console.print("[red]✗ CSV must contain 'guid' and 'classificationName' columns[/red]")
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
        console.print(f"[green]✓ Bulk classification completed. Success: {success}, Failed: {failed}[/green]")
        if errors:
            console.print("[red]Errors:[/red]")
            for err in errors:
                console.print(f"[red]- {err}[/red]")
    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-classify-csv: {str(e)}[/red]")


# === BULK ENTITY CSV OPERATIONS ===

@entity.command()
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="CSV file with entity attributes (typeName, qualifiedName, ...)")
@click.option("--batch-size", default=100, help="Batch size for API calls")
@click.option("--dry-run", is_flag=True, help="Preview entities to be created without making changes")
@click.option("--error-csv", type=click.Path(), help="CSV file to write failed rows (optional)")
@click.pass_context
def bulk_create_csv(ctx, csv_file, batch_size, dry_run, error_csv):
    """Bulk create entities from a CSV file (typeName, qualifiedName, ... columns)"""
    import pandas as pd
    import tempfile
    import os
    from purviewcli.client._entity import Entity
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity bulk-create-csv command[/yellow]")
            console.print(f"[dim]CSV File: {csv_file}[/dim]")
            console.print("[green]✓ Mock entity bulk-create-csv completed successfully[/green]")
            return

        df = pd.read_csv(csv_file)
        if "typeName" not in df.columns or "qualifiedName" not in df.columns:
            console.print("[red]✗ CSV must contain at least 'typeName' and 'qualifiedName' columns[/red]")
            return
        entity_client = Entity()
        total = len(df)
        success, failed = 0, 0
        errors = []
        failed_rows = []
        for i in range(0, total, batch_size):
            batch = df.iloc[i:i+batch_size]
            # Map each row to the correct Purview entity format
            from purviewcli.client._entity import map_flat_entity_to_purview_entity
            entities = [map_flat_entity_to_purview_entity(row) for _, row in batch.iterrows()]
            payload = {"entities": entities}
            if dry_run:
                console.print(f"[blue]DRY RUN: Would create batch {i//batch_size+1} with {len(batch)} entities[/blue]")
                continue
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmpf:
                import json
                json.dump(payload, tmpf, indent=2)
                tmpf.flush()
                payload_file = tmpf.name
            try:
                args = {"--payloadFile": payload_file}
                result = entity_client.entityCreateBulk(args)
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
            finally:
                os.remove(payload_file)
        console.print(f"[green]SUCCESS: Bulk create completed. Success: {success}, Failed: {failed}[/green]")
        if errors:
            console.print("[red]Errors:[/red]")
            for err in errors:
                console.print(f"[red]- {err}[/red]")
        if error_csv and failed_rows:
            pd.DataFrame(failed_rows).to_csv(error_csv, index=False)
            console.print(f"[yellow]WARNING: Failed rows written to {error_csv}[/yellow]")
    except Exception as e:
        console.print(f"[red]ERROR: Error executing entity bulk-create-csv: {str(e)}[/red]")


@entity.command()
@click.option("--csv-file", required=True, type=click.Path(exists=True), help="CSV file with GUID and attributes to update")
@click.option("--batch-size", default=100, help="Batch size for API calls")
@click.option("--dry-run", is_flag=True, help="Preview entities to be updated without making changes")
@click.option("--error-csv", type=click.Path(), help="CSV file to write failed rows (optional)")
@click.pass_context
def bulk_update_csv(ctx, csv_file, batch_size, dry_run, error_csv):
    """Bulk update entities from a CSV file (guid, attributes...)"""
    import pandas as pd
    import tempfile
    import os
    import json
    from purviewcli.client._entity import Entity
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity bulk-update-csv command[/yellow]")
            console.print(f"[dim]CSV File: {csv_file}[/dim]")
            console.print("[green]✓ Mock entity bulk-update-csv completed successfully[/green]")
            return

        df = pd.read_csv(csv_file)
        if "guid" not in df.columns:
            console.print("[red]✗ CSV must contain 'guid' column[/red]")
            return
        entity_client = Entity()
        total = len(df)
        success, failed = 0, 0
        errors = []
        failed_rows = []
        for i in range(0, total, batch_size):
            batch = df.iloc[i:i+batch_size]
            payload = {
                "entities": [
                    {col: row[col] for col in batch.columns if pd.notnull(row[col])}
                    for _, row in batch.iterrows()
                ]
            }
            if dry_run:
                console.print(f"[blue]DRY RUN: Would update batch {i//batch_size+1} with {len(batch)} entities[/blue]")
                continue
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmpf:
                json.dump(payload, tmpf, indent=2)
                tmpf.flush()
                payload_file = tmpf.name
            try:
                args = {"--payloadFile": payload_file}
                result = entity_client.entityBulkUpdate(args)
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
            finally:
                os.remove(payload_file)
        console.print(f"[green]✓ Bulk update completed. Success: {success}, Failed: {failed}[/green]")
        if errors:
            console.print("[red]Errors:[/red]")
            for err in errors:
                console.print(f"[red]- {err}[/red]")
        if error_csv and failed_rows:
            pd.DataFrame(failed_rows).to_csv(error_csv, index=False)
            console.print(f"[yellow]✗ Failed rows written to {error_csv}[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-update-csv: {str(e)}[/red]")


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
            console.print("[yellow]🎭 Mock: entity bulk-delete-csv command[/yellow]")
            console.print(f"[dim]CSV File: {csv_file}[/dim]")
            console.print("[green]✓ Mock entity bulk-delete-csv completed successfully[/green]")
            return

        df = pd.read_csv(csv_file)
        if "guid" not in df.columns:
            console.print("[red]✗ CSV must contain 'guid' column[/red]")
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
                result = entity_client.entityBulkDelete(args)
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
        console.print(f"[green]✓ Bulk delete completed. Success: {success}, Failed: {failed}[/green]")
        if errors:
            console.print("[red]Errors:[/red]")
            for err in errors:
                console.print(f"[red]- {err}[/red]")
        if error_csv and failed_rows:
            pd.DataFrame(failed_rows).to_csv(error_csv, index=False)
            console.print(f"[yellow]✗ Failed rows written to {error_csv}[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing entity bulk-delete-csv: {str(e)}[/red]")


# === AUDIT OPERATIONS ===


@entity.command()
@click.option("--guid", required=True, help="The globally unique identifier of the entity")
@click.pass_context
def audit(ctx, guid):
    """Get audit events for an entity by GUID"""
    try:
        if ctx.obj.get("mock"):
            console.print("[yellow]🎭 Mock: entity audit command[/yellow]")
            console.print(f"[dim]GUID: {guid}[/dim]")
            console.print("[green]✓ Mock entity audit completed successfully[/green]")
            return
        args = {"--guid": guid}
        from purviewcli.client._entity import Entity
        entity_client = Entity()
        result = entity_client.entityReadAudit(args)
        if result:
            console.print("[green]✓ Entity audit events retrieved successfully[/green]")
            console.print(json.dumps(result, indent=2))
        else:
            console.print("[yellow]⚠ Entity audit completed with no result[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error executing entity audit: {str(e)}[/red]")


@entity.command()
@click.option('--type-name', required=False, help='Filter by entity typeName (e.g., DataSet, DataProduct)')
@click.option('--limit', default=100, help='Maximum number of entities to return')
def list(type_name, limit):
    """List entities in Microsoft Purview."""
    try:
        from purviewcli.client._search import Search
        search_client = Search()
        
        # Create search query payload with proper filter structure
        search_payload = {
            "keywords": "*",
            "limit": limit,
        }
        
        # Only add filter if type_name is specified
        if type_name:
            search_payload["filter"] = {
                "entityType": [type_name]
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
        console.print(f"[red]✗ Error executing entity list: {str(e)}[/red]")


# Make the entity group available for import
__all__ = ["entity"]
