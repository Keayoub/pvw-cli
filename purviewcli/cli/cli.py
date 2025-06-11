"""
Purview CLI (pvw) - Production Version
======================================

A comprehensive, automation-friendly command-line interface for Microsoft Purview.
"""

import json
import sys
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich.console import Console

console = Console()


@click.group()
@click.option("--profile", help="Configuration profile to use")
@click.option("--account-name", help="Override Purview account name")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--mock", is_flag=True, help="Mock mode - simulate commands without real API calls")
@click.pass_context
def main(ctx, profile, account_name, debug, mock):
    """Purview CLI with profile management and automation"""
    ctx.ensure_object(dict)

    if debug:
        console.print("[cyan]Debug mode enabled[/cyan]")
    if mock:
        console.print("[yellow]Mock mode enabled - commands will be simulated[/yellow]")

    # Store basic config
    ctx.obj["account_name"] = account_name
    ctx.obj["profile"] = profile
    ctx.obj["debug"] = debug
    ctx.obj["mock"] = mock


# ============================================================================
# COMMAND GENERATION
# ============================================================================


def create_endpoint_command(client_module_name, client_class_name, method_name, command_name):
    """Create a Click command from a client endpoint method"""

    @click.pass_context
    def command_func(ctx, **kwargs):
        """Dynamic command function"""
        try:
            # Check if mock mode is enabled
            if ctx.obj.get("mock"):
                console.print(f"[yellow]🎭 Mock: {command_name} command[/yellow]")
                console.print(
                    f"[dim]Module: {client_module_name}, Class: {client_class_name}, Method: {method_name}[/dim]"
                )
                if kwargs:
                    console.print(f"[dim]Parameters: {kwargs}[/dim]")
                console.print(f"[green]✓ Mock {command_name} completed successfully[/green]")
                return

            # Real mode execution - Make actual API calls
            if ctx.obj.get("debug"):
                console.print(f"[cyan]🔄 Executing {command_name}...[/cyan]")

            # Convert Click kwargs to client args format
            method_args = {}

            # For glossary methods, always provide required parameters with defaults
            if "glossary" in method_name.lower():
                method_args["--glossaryGuid"] = kwargs.get("glossary_guid")
                method_args["--limit"] = kwargs.get("limit", 1000)  # Default limit
                method_args["--offset"] = kwargs.get("offset", 0)  # Default offset
                method_args["--sort"] = kwargs.get("sort", "ASC")  # Default sort
                method_args["--ignoreTermsAndCategories"] = kwargs.get(
                    "ignore_terms_and_categories", False
                )

                # Handle specific parameter requirements for different glossary methods
                if any(word in method_name.lower() for word in ["category", "term"]):
                    if "categoryGuid" in method_name or "termGuid" in method_name:
                        method_args["--categoryGuid"] = kwargs.get("category_guid")
                        method_args["--termGuid"] = (
                            [kwargs.get("term_guid")] if kwargs.get("term_guid") else None
                        )
                        method_args["--includeTermHierarchy"] = kwargs.get(
                            "include_term_hierarchy", False
                        )

                if any(word in method_name.lower() for word in ["create", "put", "update"]):
                    method_args["--payloadFile"] = kwargs.get("payload_file")

            else:
                # For other methods, convert parameters as provided
                for key, value in kwargs.items():
                    if value is not None:
                        # Convert kebab-case to the format expected by client
                        if key == "payload_file":
                            method_args["--payloadFile"] = value
                        else:
                            # Convert other kebab-case to camelCase if needed
                            if "_" in key:
                                parts = key.split("_")
                                camel_key = parts[0] + "".join(
                                    word.capitalize() for word in parts[1:]
                                )
                                method_args[f"--{camel_key}"] = value
                            else:
                                method_args[f"--{key}"] = value

            # Import and execute the actual client method
            try:
                module = __import__(
                    f"purviewcli.client.{client_module_name}", fromlist=[client_class_name]
                )
                client_class = getattr(module, client_class_name)
                client_instance = client_class()

                if ctx.obj.get("debug"):
                    console.print(f"[cyan]Calling {method_name} with args: {method_args}[/cyan]")

                # Execute the actual method
                result = getattr(client_instance, method_name)(method_args)

                # Handle the result
                if result:
                    if isinstance(result, dict):
                        if result.get("status") == "success":
                            console.print(f"[green]✓ {command_name} completed successfully[/green]")
                            # Display result data if available
                            if "data" in result and result["data"]:
                                console.print(json.dumps(result["data"], indent=2))
                            elif "message" in result:
                                console.print(result["message"])
                        else:
                            console.print(
                                f"[yellow]⚠ {command_name}: {result.get('message', 'Unknown status')}[/yellow]"
                            )
                    elif isinstance(result, list):
                        console.print(f"[green]✓ {command_name} completed successfully[/green]")
                        console.print(json.dumps(result, indent=2))
                    else:
                        console.print(f"[green]✓ {command_name} completed successfully[/green]")
                        console.print(str(result))
                else:
                    console.print(f"[yellow]⚠ {command_name} completed with no result[/yellow]")

            except ImportError as e:
                console.print(f"[red]✗ Failed to import {client_class_name}: {str(e)}[/red]")
                console.print(
                    f"[yellow]💡 Try using --mock flag for testing CLI structure[/yellow]"
                )
            except Exception as e:
                console.print(f"[red]✗ Error executing {command_name}: {str(e)}[/red]")
                if ctx.obj.get("debug"):
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")

        except Exception as e:
            console.print(f"[red]✗ Unexpected error in {command_name}: {str(e)}[/red]")
            if ctx.obj.get("debug"):
                console.print(f"[dim]{traceback.format_exc()}[/dim]")

    return command_func


# ============================================================================
# COMMAND GROUPS WITH KNOWN COMMANDS
# ============================================================================
@main.group()
@click.pass_context
def entity(ctx):
    """Entity management operations"""
    pass


# Add other groups with their actual method mappings
groups_with_methods = [
    (
        "account",
        "_account",
        "Account",
        {
            "get-access-keys": "accountGetAccessKeys",
            "get-account": "accountGetAccount",
            "regenerate-access-keys": "accountRegenerateAccessKeys",
            "update-account": "accountUpdateAccount",
        },
    ),
    (
        "collections",
        "_collections",
        "Collections",
        {
            "create": "collectionsCreateCollection",
            "create-or-update": "collectionsCreateOrUpdateCollection",
            "delete": "collectionsDeleteCollection",
            "export-csv": "collectionsExportToCSV",
            "get": "collectionsGetCollection",
            "get-child-names": "collectionsGetChildCollectionNames",
            "get-path": "collectionsGetCollectionPath",
            "import": "collectionsImportFromCSV",
            "list": "collectionsGetCollections",
            "update": "collectionsUpdateCollection",
        },
    ),
    (
        "glossary",
        "_glossary",
        "Glossary",
        {
            "create": "glossaryCreate",
            "create-categories": "glossaryCreateCategories",
            "create-category": "glossaryCreateCategory",
            "create-term": "glossaryCreateTerm",
            "create-terms": "glossaryCreateTerms",
            "delete": "glossaryDeleteCategory",
            "delete-category": "glossaryDeleteCategory",
            "delete-term": "glossaryDeleteTerm",
            "export-csv": "glossaryExportToCSV",
            "import-terms-csv": "glossaryImportTermsFromCSV",
            "list": "glossaryRead",
            "put-category": "glossaryPutCategory",
            "put-category-partial": "glossaryPutCategoryPartial",
            "put-term": "glossaryPutTerm",
            "put-term-partial": "glossaryPutTermPartial",
            "read": "glossaryRead",
            "read-category": "glossaryReadCategory",
            "read-category-related": "glossaryReadCategoryRelated",
            "read-category-terms": "glossaryReadCategoryTerms",
            "read-term": "glossaryReadTerm",
            "update": "glossaryPutCategory",
        },
    ),
    (
        "insight",
        "_insight",
        "Insight",
        {
            "asset-distribution": "insightAssetDistribution",
            "files-aggregation": "insightFilesAggregation",
            "files-without-resource-set": "insightFilesWithoutResourceSet",
            "scan-status-summary": "insightScanStatusSummary",
            "scan-status-summary-by-ts": "insightScanStatusSummaryByTs",
            "tags": "insightTags",
            "tags-time-series": "insightTagsTimeSeries",
        },
    ),
    (
        "lineage",
        "_lineage",
        "Lineage",
        {
            "analyze": "lineageAnalyze",
            "analyze-column": "lineageAnalyzeColumn",
            "analyze-dataflow": "lineageAnalyzeDataflow",
            "bulk-create": "lineageBulkCreate",
            "bulk-update": "lineageBulkUpdate",
            "create-relationship": "lineageCreateRelationship",
            "csv-process": "lineageCSVProcess",
            "csv-sample": "lineageCSVSample",
            "csv-templates": "lineageCSVTemplates",
            "csv-validate": "lineageCSVValidate",
            "delete-relationship": "lineageDeleteRelationship",
            "get-metrics": "lineageGetMetrics",
            "impact": "lineageImpact",
            "read": "lineageRead",
            "read-downstream": "lineageReadDownstream",
            "read-impact-analysis": "lineageReadImpactAnalysis",
            "read-next": "lineageReadNext",
            "read-next-page": "lineageReadNextPage",
            "read-unique-attribute": "lineageReadUniqueAttribute",
            "read-upstream": "lineageReadUpstream",
            "update-relationship": "lineageUpdateRelationship",
        },
    ),
    (
        "management",
        "_management",
        "Management",
        {
            "add-root-collection-admin": "managementAddRootCollectionAdmin",
            "check-name-availability": "managementCheckNameAvailability",
            "create-account": "managementCreateAccount",
            "default-account": "managementDefaultAccount",
            "delete-account": "managementDeleteAccount",
            "delete-private-endpoint": "managementDeletePrivateEndpoint",
            "list-keys": "managementListKeys",
            "list-operations": "managementListOperations",
            "list-private-link-resources": "managementListPrivateLinkResources",
            "put-private-endpoint": "managementPutPrivateEndpoint",
            "read-account": "managementReadAccount",
            "read-accounts": "managementReadAccounts",
            "read-private-endpoint": "managementReadPrivateEndpoint",
            "read-private-endpoints": "managementReadPrivateEndpoints",
            "remove-default-account": "managementRemoveDefaultAccount",
            "set-default-account": "managementSetDefaultAccount",
            "update-account": "managementUpdateAccount",
        },
    ),
    (
        "policystore",
        "_policystore",
        "PolicyStore",
        {
            "delete-data-policy": "policystoreDeleteDataPolicy",
            "delete-data-policy-scope": "policystoreDeleteDataPolicyScope",
            "put-data-policy": "policystorePutDataPolicy",
            "put-data-policy-scope": "policystorePutDataPolicyScope",
            "put-metadata-policy": "policystorePutMetadataPolicy",
            "read-data-policies": "policystoreReadDataPolicies",
            "read-data-policy-scopes": "policystoreReadDataPolicyScopes",
            "read-metadata-policies": "policystoreReadMetadataPolicies",
            "read-metadata-policy": "policystoreReadMetadataPolicy",
            "read-metadata-roles": "policystoreReadMetadataRoles",
        },
    ),
    (
        "relationship",
        "_relationship",
        "Relationship",
        {
            "create": "relationshipCreate",
            "delete": "relationshipDelete",
            "put": "relationshipPut",
            "read": "relationshipRead",
        },
    ),
    (
        "scan",
        "_scan",
        "Scan",
        {
            "cancel-scan": "scanCancelScan",
            "delete-classification-rule": "scanDeleteClassificationRule",
            "delete-credential": "scanDeleteCredential",
            "delete-data-source": "scanDeleteDataSource",
            "delete-key-vault": "scanDeleteKeyVault",
            "delete-scan": "scanDeleteScan",
            "delete-scan-ruleset": "scanDeleteScanRuleset",
            "delete-trigger": "scanDeleteTrigger",
            "put-classification-rule": "scanPutClassificationRule",
            "put-credential": "scanPutCredential",
            "put-data-source": "scanPutDataSource",
            "put-filter": "scanPutFilter",
            "put-key-vault": "scanPutKeyVault",
            "put-scan": "scanPutScan",
            "put-scan-ruleset": "scanPutScanRuleset",
            "put-trigger": "scanPutTrigger",
            "read-classification-rule": "scanReadClassificationRule",
            "read-classification-rule-versions": "scanReadClassificationRuleVersions",
            "read-classification-rules": "scanReadClassificationRules",
            "read-credential": "scanReadCredential",
            "read-data-source": "scanReadDataSource",
            "read-data-sources": "scanReadDataSources",
            "read-filters": "scanReadFilters",
            "read-key-vault": "scanReadKeyVault",
            "read-key-vaults": "scanReadKeyVaults",
            "read-scan": "scanReadScan",
            "read-scan-history": "scanReadScanHistory",
            "read-scan-ruleset": "scanReadScanRuleset",
            "read-scan-rulesets": "scanReadScanRulesets",
            "read-scans": "scanReadScans",
            "read-system-scan-ruleset": "scanReadSystemScanRuleset",
            "read-system-scan-ruleset-latest": "scanReadSystemScanRulesetLatest",
            "read-system-scan-ruleset-version": "scanReadSystemScanRulesetVersion",
            "read-system-scan-ruleset-versions": "scanReadSystemScanRulesetVersions",
            "read-system-scan-rulesets": "scanReadSystemScanRulesets",
            "read-trigger": "scanReadTrigger",
            "run-scan": "scanRunScan",
            "tag-classification-version": "scanTagClassificationVersion",
        },
    ),
    (
        "search",
        "_search",
        "Search",
        {
            "autocomplete": "searchAutoComplete",
            "browse": "searchBrowse",
            "query": "searchQuery",
            "suggest": "searchSuggest",
        },
    ),
    (
        "share",
        "_share",
        "Share",
        {
            "activate-email": "shareActivateEmail",
            "create-asset": "shareCreateAsset",
            "create-asset-mapping": "shareCreateAssetMapping",
            "create-received-share": "shareCreateReceivedShare",
            "create-sent-invitation": "shareCreateSentInvitation",
            "create-sent-share": "shareCreateSentShare",
            "delete-asset": "shareDeleteAsset",
            "delete-asset-mapping": "shareDeleteAssetMapping",
            "delete-received-share": "shareDeleteReceivedShare",
            "delete-sent-invitation": "shareDeleteSentInvitation",
            "delete-sent-share": "shareDeleteSentShare",
            "get-accepted-share": "shareGetAcceptedShare",
            "get-asset": "shareGetAsset",
            "get-asset-mapping": "shareGetAssetMapping",
            "get-received-invitation": "shareGetReceivedInvitation",
            "get-received-share": "shareGetReceivedShare",
            "get-sent-invitation": "shareGetSentInvitation",
            "get-sent-share": "shareGetSentShare",
            "list-accepted-shares": "shareListAcceptedShares",
            "list-asset-mappings": "shareListAssetMappings",
            "list-assets": "shareListAssets",
            "list-received-assets": "shareListReceivedAssets",
            "list-received-invitations": "shareListReceivedInvitations",
            "list-received-shares": "shareListReceivedShares",
            "list-sent-invitations": "shareListSentInvitations",
            "list-sent-shares": "shareListSentShares",
            "register-email": "shareRegisterEmail",
            "reject-received-invitation": "shareRejectReceivedInvitation",
            "reinstate-accepted-share": "shareReinstateAcceptedShare",
            "revoke-accepted-share": "shareRevokeAcceptedShare",
            "update-expiration-accepted-share": "shareUpdateExpirationAcceptedShare",
        },
    ),
    (
        "types",
        "_types",
        "Types",
        {
            "create-type-defs": "typesCreateTypeDefs",
            "delete-type-def": "typesDeleteTypeDef",
            "delete-type-defs": "typesDeleteTypeDefs",
            "put-type-defs": "typesPutTypeDefs",
            "read-business-metadata-def": "typesReadBusinessMetadataDef",
            "read-classification-def": "typesReadClassificationDef",
            "read-entity-def": "typesReadEntityDef",
            "read-enum-def": "typesReadEnumDef",
            "read-relationship-def": "typesReadRelationshipDef",
            "read-statistics": "typesReadStatistics",
            "read-struct-def": "typesReadStructDef",
            "read-term-template-def": "typesReadTermTemplateDef",
            "read-type-def": "typesReadTypeDef",
            "read-type-defs": "typesReadTypeDefs",
            "read-type-defs-headers": "typesReadTypeDefsHeaders",
        },
    ),
]

# Entity commands (from our previous analysis)
entity_commands = [
    "add-classification",
    "add-classifications",
    "add-labels",
    "add-or-update-business-metadata",
    "bulk-update-business-metadata",
    "create",
    "delete",
    "delete-business-metadata",
    "delete-by-unique-attribute",
    "delete-bulk",
    "delete-classification",
    "export-business-metadata",
    "export-to-csv",
    "get-business-metadata-statistics",
    "get-business-metadata-status",
    "import-business-metadata",
    "import-from-csv",
    "partial-update-by-unique-attribute",
    "purge-deleted",
    "read",
    "read-bulk",
    "read-classification",
    "read-classifications",
    "read-header",
    "read-sample",
    "read-unique-attribute",
    "remove-labels",
    "search-business-metadata",
    "set-labels",
    "update",
    "update-classification",
    "update-classifications",
    "validate-business-metadata",
]

for cmd_name in entity_commands:
    method_name = f'entity{cmd_name.replace("-", "")}'
    command_func = create_endpoint_command("_entity", "Entity", method_name, cmd_name)

    # Add appropriate options
    if any(word in cmd_name for word in ["read", "get", "delete"]):
        command_func = click.option("--guid", help="Entity GUID")(command_func)
    if any(word in cmd_name for word in ["create", "update"]):
        command_func = click.option("--payload-file", help="JSON payload file")(command_func)
    if "read" in cmd_name:
        command_func = click.option(
            "--output", type=click.Choice(["json", "table"]), default="json", help="Output format"
        )(command_func)

    entity.command(name=cmd_name, help=f'{cmd_name.replace("-", " ").title()} operation')(
        command_func
    )

for group_name, module_name, class_name, method_mapping in groups_with_methods:
    # Create the group
    group = click.Group(name=group_name, help=f"{group_name.title()} operations")
    main.add_command(group)

    # Add commands using the correct method names
    for cmd_name, method_name in method_mapping.items():
        command_func = create_endpoint_command(module_name, class_name, method_name, cmd_name)

        # Add specific options based on group and command
        if group_name == "glossary":
            if cmd_name in ["read", "list"]:
                command_func = click.option(
                    "--glossary-guid", help="Glossary GUID (optional for specific glossary)"
                )(command_func)
                command_func = click.option(
                    "--limit", type=int, default=1000, help="Limit results"
                )(command_func)
                command_func = click.option(
                    "--offset", type=int, default=0, help="Offset for pagination"
                )(command_func)
                command_func = click.option("--sort", default="ASC", help="Sort order")(
                    command_func
                )
                command_func = click.option(
                    "--ignore-terms-and-categories",
                    is_flag=True,
                    help="Ignore terms and categories",
                )(command_func)
            elif cmd_name in [
                "create",
                "update",
                "put-category",
                "put-term",
                "create-category",
                "create-term",
            ]:
                command_func = click.option("--payload-file", help="JSON payload file")(
                    command_func
                )
                if "term" in cmd_name:
                    command_func = click.option(
                        "--include-term-hierarchy", is_flag=True, help="Include term hierarchy"
                    )(command_func)
            elif cmd_name in ["delete", "delete-category"]:
                command_func = click.option("--category-guid", help="Category GUID to delete")(
                    command_func
                )
            elif cmd_name in ["delete-term", "read-term", "put-term"]:
                command_func = click.option("--term-guid", help="Term GUID")(command_func)
                command_func = click.option(
                    "--include-term-hierarchy", is_flag=True, help="Include term hierarchy"
                )(command_func)
            elif cmd_name in ["read-category", "put-category-partial"]:
                command_func = click.option("--category-guid", help="Category GUID")(command_func)
                command_func = click.option(
                    "--include-term-hierarchy", is_flag=True, help="Include term hierarchy"
                )(command_func)

        elif group_name == "collections":
            # Collections commands all require --collectionName parameter
            if cmd_name in [
                "delete",
                "get",
                "create",
                "create-or-update",
                "get",
                "get-child-names",
                "update",
            ]:
                command_func = click.option(
                    "--collection-name",
                    required=True,
                    help="Collection name (required for this command)",
                )(command_func)

            if cmd_name in ["create", "create-or-update", "update"]:
                # Specific options for collection commands
                command_func = click.option("--payload-file", help="JSON payload file")(
                    command_func
                )
                command_func = click.option("--friendly-name", help="Friendly name for collection")(
                    command_func
                )
                command_func = click.option("--description", help="Description for collection")(
                    command_func
                )
                command_func = click.option("--parent-collection", help="Parent collection name")(
                    command_func
                )
            elif cmd_name == "import":
                command_func = click.option(
                    "--filename", required=True, help="CSV file path for import"
                )(command_func)
                command_func = click.option(
                    "--batchsize", default=10, help="Batch size for processing"
                )(command_func)
            elif cmd_name == "export-csv":
                command_func = click.option(
                    "--output-file", help="Output file path for CSV export"
                )(command_func)
                command_func = click.option(
                    "--include-hierarchy",
                    is_flag=True,
                    default=True,
                    help="Include hierarchy information",
                )(command_func)
                command_func = click.option(
                    "--include-metadata", is_flag=True, default=True, help="Include system metadata"
                )(command_func)

        else:
            # Generic options for other groups
            if cmd_name in ["read", "delete"]:
                command_func = click.option("--guid", help=f"{group_name.title()} GUID")(
                    command_func
                )
            elif cmd_name in ["create", "update"]:
                command_func = click.option("--payload-file", help="JSON payload file")(
                    command_func
                )
            elif cmd_name == "list":
                command_func = click.option("--limit", help="Limit results")(command_func)
                command_func = click.option("--offset", help="Offset for pagination")(command_func)

        group.command(name=cmd_name, help=f"{cmd_name.title()} {group_name}")(command_func)


# Add custom options for entity import and export commands
entity_group = main.get_command(None, "entity")
if entity_group:
    entity_import_cmd = entity_group.get_command(None, "import-csv")
    if entity_import_cmd:
        entity_import_cmd = click.option(
            "--csvfile", required=True, help="CSV file path for import"
        )(entity_import_cmd)
        entity_import_cmd = click.option(
            "--batchsize", default=10, help="Batch size for processing"
        )(entity_import_cmd)

    entity_export_cmd = entity_group.get_command(None, "export-csv")
    if entity_export_cmd:
        entity_export_cmd = click.option("--outputfile", help="Output CSV file path")(
            entity_export_cmd
        )
        entity_export_cmd = click.option("--entitytype", help="Filter by entity type")(
            entity_export_cmd
        )
        entity_export_cmd = click.option("--collection", help="Filter by collection")(
            entity_export_cmd
        )
        entity_export_cmd = click.option("--searchquery", help="Search query filter")(
            entity_export_cmd
        )
        entity_export_cmd = click.option(
            "--include-metadata", is_flag=True, default=True, help="Include system metadata"
        )(entity_export_cmd)
        entity_export_cmd = click.option(
            "--include-attributes", is_flag=True, default=True, help="Include all attributes"
        )(entity_export_cmd)

# Add custom options for glossary import and export commands
glossary_group = main.get_command(None, "glossary")
if glossary_group:
    glossary_import_cmd = glossary_group.get_command(None, "import-terms-csv")
    if glossary_import_cmd:
        glossary_import_cmd = click.option(
            "--csvfile", required=True, help="CSV file path for import"
        )(glossary_import_cmd)
        glossary_import_cmd = click.option(
            "--glossary-guid", required=True, help="Target glossary GUID"
        )(glossary_import_cmd)
        glossary_import_cmd = click.option(
            "--batchsize", default=10, help="Batch size for processing"
        )(glossary_import_cmd)

    glossary_export_cmd = glossary_group.get_command(None, "export-csv")
    if glossary_export_cmd:
        glossary_export_cmd = click.option("--outputfile", help="Output CSV file path")(
            glossary_export_cmd
        )
        glossary_export_cmd = click.option(
            "--export-type",
            type=click.Choice(["both", "glossaries", "terms"]),
            default="both",
            help="Type of data to export",
        )(glossary_export_cmd)
        glossary_export_cmd = click.option(
            "--glossary-guid", help="Specific glossary GUID to export"
        )(glossary_export_cmd)
        glossary_export_cmd = click.option(
            "--include-metadata", is_flag=True, default=True, help="Include system metadata"
        )(glossary_export_cmd)

if __name__ == "__main__":
    main()
