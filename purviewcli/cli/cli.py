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
@click.option('--profile', help='Configuration profile to use')
@click.option('--account-name', help='Override Purview account name')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--mock', is_flag=True, help='Mock mode - simulate commands without real API calls')
@click.pass_context
def main(ctx, profile, account_name, debug, mock):
    """Purview CLI with profile management and automation"""
    ctx.ensure_object(dict)
    
    if debug:
        console.print("[cyan]Debug mode enabled[/cyan]")
    if mock:
        console.print("[yellow]Mock mode enabled - commands will be simulated[/yellow]")
    
    # Store basic config
    ctx.obj['account_name'] = account_name
    ctx.obj['profile'] = profile
    ctx.obj['debug'] = debug
    ctx.obj['mock'] = mock

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
            if ctx.obj.get('mock'):
                console.print(f"[yellow]🎭 Mock: {command_name} command[/yellow]")
                console.print(f"[dim]Module: {client_module_name}, Class: {client_class_name}, Method: {method_name}[/dim]")
                if kwargs:
                    console.print(f"[dim]Parameters: {kwargs}[/dim]")
                console.print(f"[green]✓ Mock {command_name} completed successfully[/green]")
                return
            
            # Real mode execution - Make actual API calls
            if ctx.obj.get('debug'):
                console.print(f"[cyan]🔄 Executing {command_name}...[/cyan]")
            
            # Convert Click kwargs to client args format
            method_args = {}
            
            # For glossary methods, always provide required parameters with defaults
            if 'glossary' in method_name.lower():
                method_args['--glossaryGuid'] = kwargs.get('glossary_guid')
                method_args['--limit'] = kwargs.get('limit', 1000)  # Default limit
                method_args['--offset'] = kwargs.get('offset', 0)   # Default offset
                method_args['--sort'] = kwargs.get('sort', 'ASC')   # Default sort
                method_args['--ignoreTermsAndCategories'] = kwargs.get('ignore_terms_and_categories', False)
                
                # Handle specific parameter requirements for different glossary methods
                if any(word in method_name.lower() for word in ['category', 'term']):
                    if 'categoryGuid' in method_name or 'termGuid' in method_name:
                        method_args['--categoryGuid'] = kwargs.get('category_guid')
                        method_args['--termGuid'] = [kwargs.get('term_guid')] if kwargs.get('term_guid') else None
                        method_args['--includeTermHierarchy'] = kwargs.get('include_term_hierarchy', False)
                
                if any(word in method_name.lower() for word in ['create', 'put', 'update']):
                    method_args['--payloadFile'] = kwargs.get('payload_file')
            else:
                # For other methods, convert parameters as provided
                for key, value in kwargs.items():
                    if value is not None:
                        # Convert kebab-case to the format expected by client
                        if key == 'payload_file':
                            method_args['--payloadFile'] = value
                        else:
                            # Convert other kebab-case to camelCase if needed
                            if '_' in key:
                                parts = key.split('_')
                                camel_key = parts[0] + ''.join(word.capitalize() for word in parts[1:])
                                method_args[f'--{camel_key}'] = value
                            else:
                                method_args[f'--{key}'] = value
            
            # Import and execute the actual client method
            try:
                module = __import__(f'purviewcli.client.{client_module_name}', fromlist=[client_class_name])
                client_class = getattr(module, client_class_name)
                client_instance = client_class()
                
                if ctx.obj.get('debug'):
                    console.print(f"[cyan]Calling {method_name} with args: {method_args}[/cyan]")
                
                # Execute the actual method
                result = getattr(client_instance, method_name)(method_args)
                
                # Handle the result
                if result:
                    if isinstance(result, dict):
                        if result.get('status') == 'success':
                            console.print(f"[green]✓ {command_name} completed successfully[/green]")
                            # Display result data if available
                            if 'data' in result and result['data']:
                                console.print(json.dumps(result['data'], indent=2))
                            elif 'message' in result:
                                console.print(result['message'])
                        else:
                            console.print(f"[yellow]⚠ {command_name}: {result.get('message', 'Unknown status')}[/yellow]")
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
                console.print(f"[yellow]💡 Try using --mock flag for testing CLI structure[/yellow]")
            except Exception as e:
                console.print(f"[red]✗ Error executing {command_name}: {str(e)}[/red]")
                if ctx.obj.get('debug'):
                    console.print(f"[dim]{traceback.format_exc()}[/dim]")
        
        except Exception as e:
            console.print(f"[red]✗ Unexpected error in {command_name}: {str(e)}[/red]")
            if ctx.obj.get('debug'):
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

# Entity commands (from our previous analysis)
entity_commands = [
    'create', 'read', 'update', 'delete', 'read-bulk', 'delete-bulk',
    'add-labels', 'remove-labels', 'set-labels', 'add-classifications',
    'update-classifications', 'delete-classification', 'read-header',
    'read-sample', 'import-business-metadata', 'delete-business-metadata',
    'add-or-update-business-metadata', 'purge-deleted', 'read-unique-attribute',
    'partial-update-by-unique-attribute', 'delete-by-unique-attribute',
    'add-classification', 'update-classification', 'read-classification',
    'read-classifications'
]

for cmd_name in entity_commands:
    method_name = f'entity{cmd_name.replace("-", "")}'
    command_func = create_endpoint_command('_entity', 'Entity', method_name, cmd_name)
    
    # Add appropriate options
    if any(word in cmd_name for word in ['read', 'get', 'delete']):
        command_func = click.option('--guid', help='Entity GUID')(command_func)
    if any(word in cmd_name for word in ['create', 'update']):
        command_func = click.option('--payload-file', help='JSON payload file')(command_func)
    if 'read' in cmd_name:
        command_func = click.option('--output', type=click.Choice(['json', 'table']), default='json', help='Output format')(command_func)
    
    entity.command(name=cmd_name, help=f'{cmd_name.replace("-", " ").title()} operation')(command_func)

# Add other groups with their actual method mappings
groups_with_methods = [
    ('account', '_account', 'Account', {
        'get-account': 'accountGetAccount',
        'update-account': 'accountUpdateAccount',
        'get-collections': 'accountGetCollections',
        'get-collection': 'accountGetCollection',
        'get-collection-path': 'accountGetCollectionPath',
        'get-child-collection-names': 'accountGetChildCollectionNames',
        'delete-collection': 'accountDeleteCollection',
        'put-collection': 'accountPutCollection',
        'get-access-keys': 'accountGetAccessKeys',
        'regenerate-access-keys': 'accountRegenerateAccessKeys',
        'get-resource-set-rules': 'accountGetResourceSetRules',
        'delete-resource-set-rule': 'accountDeleteResourceSetRule',
        'get-resource-set-rule': 'accountGetResourceSetRule',
        'put-resource-set-rule': 'accountPutResourceSetRule'
    }),
    ('glossary', '_glossary', 'Glossary', {
        'create': 'glossaryCreate',
        'read': 'glossaryRead',
        'update': 'glossaryPutCategory', 
        'delete': 'glossaryDeleteCategory',
        'list': 'glossaryRead',
        'create-categories': 'glossaryCreateCategories',
        'create-category': 'glossaryCreateCategory',
        'delete-category': 'glossaryDeleteCategory',
        'read-category': 'glossaryReadCategory',
        'put-category': 'glossaryPutCategory',
        'put-category-partial': 'glossaryPutCategoryPartial',
        'read-category-related': 'glossaryReadCategoryRelated',
        'read-category-terms': 'glossaryReadCategoryTerms',
        'create-term': 'glossaryCreateTerm',
        'delete-term': 'glossaryDeleteTerm',
        'read-term': 'glossaryReadTerm',
        'put-term': 'glossaryPutTerm',
        'put-term-partial': 'glossaryPutTermPartial',
        'create-terms': 'glossaryCreateTerms'
    }),    ('lineage', '_lineage', 'Lineage', {
        'read': 'lineageRead',
        'read-next': 'lineageReadNext',
        'analyze': 'lineageAnalyze',
        'impact': 'lineageImpact',
        'csv-process': 'lineageCSVProcess',
        'csv-validate': 'lineageCSVValidate',
        'csv-sample': 'lineageCSVSample',
        'csv-templates': 'lineageCSVTemplates'
    }),
    ('management', '_management', 'Management', {
        'list-operations': 'managementListOperations',
        'check-name-availability': 'managementCheckNameAvailability',
        'read-accounts': 'managementReadAccounts',
        'read-account': 'managementReadAccount',
        'create-account': 'managementCreateAccount',
        'delete-account': 'managementDeleteAccount',
        'list-keys': 'managementListKeys',
        'update-account': 'managementUpdateAccount',
        'default-account': 'managementDefaultAccount',
        'set-default-account': 'managementSetDefaultAccount',
        'remove-default-account': 'managementRemoveDefaultAccount',
        'list-private-link-resources': 'managementListPrivateLinkResources',
        'put-private-endpoint': 'managementPutPrivateEndpoint',
        'delete-private-endpoint': 'managementDeletePrivateEndpoint',
        'read-private-endpoint': 'managementReadPrivateEndpoint',
        'read-private-endpoints': 'managementReadPrivateEndpoints',
        'add-root-collection-admin': 'managementAddRootCollectionAdmin'
    }),    ('types', '_types', 'Types', {
        'read-term-template-def': 'typesReadTermTemplateDef',
        'read-classification-def': 'typesReadClassificationDef',
        'read-entity-def': 'typesReadEntityDef',
        'read-enum-def': 'typesReadEnumDef',
        'read-relationship-def': 'typesReadRelationshipDef',
        'read-struct-def': 'typesReadStructDef',
        'read-type-def': 'typesReadTypeDef',
        'read-business-metadata-def': 'typesReadBusinessMetadataDef',
        'read-type-defs': 'typesReadTypeDefs',
        'read-type-defs-headers': 'typesReadTypeDefsHeaders',
        'delete-type-def': 'typesDeleteTypeDef',
        'delete-type-defs': 'typesDeleteTypeDefs',
        'create-type-defs': 'typesCreateTypeDefs',
        'put-type-defs': 'typesPutTypeDefs',
        'read-statistics': 'typesReadStatistics'    }),
    ('lineage', '_lineage', 'Lineage', {
        'read': 'lineageRead',
        'read-next': 'lineageReadNext',
        'analyze': 'lineageAnalyze',
        'impact': 'lineageImpact',
        'csv-process': 'lineageCSVProcess',
        'csv-validate': 'lineageCSVValidate',
        'csv-sample': 'lineageCSVSample',
        'csv-templates': 'lineageCSVTemplates'
    }),
    ('relationship', '_relationship', 'Relationship', {
        'create': 'relationshipCreate',
        'put': 'relationshipPut',
        'delete': 'relationshipDelete',
        'read': 'relationshipRead'
    }),
    ('policystore', '_policystore', 'PolicyStore', {
        'read-metadata-roles': 'policystoreReadMetadataRoles',
        'read-metadata-policy': 'policystoreReadMetadataPolicy',
        'read-metadata-policies': 'policystoreReadMetadataPolicies',
        'put-metadata-policy': 'policystorePutMetadataPolicy',
        'read-data-policies': 'policystoreReadDataPolicies',
        'put-data-policy': 'policystorePutDataPolicy',
        'read-data-policy-scopes': 'policystoreReadDataPolicyScopes',
        'put-data-policy-scope': 'policystorePutDataPolicyScope',
        'delete-data-policy-scope': 'policystoreDeleteDataPolicyScope',
        'delete-data-policy': 'policystoreDeleteDataPolicy'
    }),
    ('scan', '_scan', 'Scan', {
        'read-classification-rule': 'scanReadClassificationRule',
        'read-classification-rules': 'scanReadClassificationRules',
        'read-classification-rule-versions': 'scanReadClassificationRuleVersions',
        'read-data-source': 'scanReadDataSource',
        'read-data-sources': 'scanReadDataSources',
        'read-filters': 'scanReadFilters',
        'read-key-vault': 'scanReadKeyVault',
        'read-key-vaults': 'scanReadKeyVaults',
        'read-scan-history': 'scanReadScanHistory',
        'read-scan-ruleset': 'scanReadScanRuleset',
        'read-scan-rulesets': 'scanReadScanRulesets',
        'read-scan': 'scanReadScan',
        'read-scans': 'scanReadScans',
        'read-system-scan-ruleset': 'scanReadSystemScanRuleset',
        'read-system-scan-ruleset-version': 'scanReadSystemScanRulesetVersion',
        'read-system-scan-ruleset-latest': 'scanReadSystemScanRulesetLatest',
        'read-system-scan-rulesets': 'scanReadSystemScanRulesets',
        'read-system-scan-ruleset-versions': 'scanReadSystemScanRulesetVersions',
        'read-trigger': 'scanReadTrigger',
        'delete-classification-rule': 'scanDeleteClassificationRule',
        'delete-data-source': 'scanDeleteDataSource',
        'delete-key-vault': 'scanDeleteKeyVault',
        'delete-scan-ruleset': 'scanDeleteScanRuleset',
        'delete-scan': 'scanDeleteScan',
        'delete-trigger': 'scanDeleteTrigger',
        'put-classification-rule': 'scanPutClassificationRule',
        'put-data-source': 'scanPutDataSource',
        'put-filter': 'scanPutFilter',
        'put-key-vault': 'scanPutKeyVault',
        'run-scan': 'scanRunScan',
        'cancel-scan': 'scanCancelScan',
        'put-scan-ruleset': 'scanPutScanRuleset',
        'put-scan': 'scanPutScan',
        'put-trigger': 'scanPutTrigger',
        'tag-classification-version': 'scanTagClassificationVersion',
        'read-credential': 'scanReadCredential',
        'put-credential': 'scanPutCredential',
        'delete-credential': 'scanDeleteCredential'
    }),
    ('search', '_search', 'Search', {
        'query': 'searchQuery',
        'autocomplete': 'searchAutoComplete',
        'suggest': 'searchSuggest',
        'browse': 'searchBrowse'
    }),
    ('share', '_share', 'Share', {
        'list-accepted-shares': 'shareListAcceptedShares',
        'get-accepted-share': 'shareGetAcceptedShare',
        'reinstate-accepted-share': 'shareReinstateAcceptedShare',
        'revoke-accepted-share': 'shareRevokeAcceptedShare',
        'update-expiration-accepted-share': 'shareUpdateExpirationAcceptedShare',
        'list-asset-mappings': 'shareListAssetMappings',
        'create-asset-mapping': 'shareCreateAssetMapping',
        'delete-asset-mapping': 'shareDeleteAssetMapping',
        'get-asset-mapping': 'shareGetAssetMapping',
        'list-assets': 'shareListAssets',
        'create-asset': 'shareCreateAsset',
        'delete-asset': 'shareDeleteAsset',
        'get-asset': 'shareGetAsset',
        'activate-email': 'shareActivateEmail',
        'register-email': 'shareRegisterEmail',
        'list-received-assets': 'shareListReceivedAssets',
        'list-received-invitations': 'shareListReceivedInvitations',
        'get-received-invitation': 'shareGetReceivedInvitation',
        'reject-received-invitation': 'shareRejectReceivedInvitation',
        'list-received-shares': 'shareListReceivedShares',
        'create-received-share': 'shareCreateReceivedShare',
        'delete-received-share': 'shareDeleteReceivedShare',
        'get-received-share': 'shareGetReceivedShare',
        'list-sent-invitations': 'shareListSentInvitations',
        'create-sent-invitation': 'shareCreateSentInvitation',
        'delete-sent-invitation': 'shareDeleteSentInvitation',
        'get-sent-invitation': 'shareGetSentInvitation',
        'list-sent-shares': 'shareListSentShares',
        'create-sent-share': 'shareCreateSentShare',
        'delete-sent-share': 'shareDeleteSentShare',
        'get-sent-share': 'shareGetSentShare'
    }),
    ('insight', '_insight', 'Insight', {
        'asset-distribution': 'insightAssetDistribution',
        'files-without-resource-set': 'insightFilesWithoutResourceSet',
        'files-aggregation': 'insightFilesAggregation',
        'tags': 'insightTags',
        'tags-time-series': 'insightTagsTimeSeries',
        'scan-status-summary': 'insightScanStatusSummary',
        'scan-status-summary-by-ts': 'insightScanStatusSummaryByTs'
    })
]

for group_name, module_name, class_name, method_mapping in groups_with_methods:
    # Create the group
    group = click.Group(name=group_name, help=f'{group_name.title()} operations')
    main.add_command(group)
    
    # Add commands using the correct method names
    for cmd_name, method_name in method_mapping.items():
        command_func = create_endpoint_command(module_name, class_name, method_name, cmd_name)
        
        # Add specific options based on group and command
        if group_name == 'glossary':
            if cmd_name in ['read', 'list']:
                command_func = click.option('--glossary-guid', help='Glossary GUID (optional for specific glossary)')(command_func)
                command_func = click.option('--limit', type=int, default=1000, help='Limit results')(command_func)
                command_func = click.option('--offset', type=int, default=0, help='Offset for pagination')(command_func)
                command_func = click.option('--sort', default='ASC', help='Sort order')(command_func)
                command_func = click.option('--ignore-terms-and-categories', is_flag=True, help='Ignore terms and categories')(command_func)
            elif cmd_name in ['create', 'update', 'put-category', 'put-term', 'create-category', 'create-term']:
                command_func = click.option('--payload-file', help='JSON payload file')(command_func)
                if 'term' in cmd_name:
                    command_func = click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy')(command_func)
            elif cmd_name in ['delete', 'delete-category']:
                command_func = click.option('--category-guid', help='Category GUID to delete')(command_func)
            elif cmd_name in ['delete-term', 'read-term', 'put-term']:
                command_func = click.option('--term-guid', help='Term GUID')(command_func)
                command_func = click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy')(command_func)
            elif cmd_name in ['read-category', 'put-category-partial']:
                command_func = click.option('--category-guid', help='Category GUID')(command_func)
                command_func = click.option('--include-term-hierarchy', is_flag=True, help='Include term hierarchy')(command_func)
        else:
            # Generic options for other groups
            if cmd_name in ['read', 'delete']:
                command_func = click.option('--guid', help=f'{group_name.title()} GUID')(command_func)
            elif cmd_name in ['create', 'update']:
                command_func = click.option('--payload-file', help='JSON payload file')(command_func)
            elif cmd_name == 'list':
                command_func = click.option('--limit', help='Limit results')(command_func)
                command_func = click.option('--offset', help='Offset for pagination')(command_func)
        
        group.command(name=cmd_name, help=f'{cmd_name.title()} {group_name}')(command_func)

if __name__ == '__main__':
    main()
