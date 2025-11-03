"""
Batch apply docstrings to any Purview CLI client module
Generic version that works with all client modules in purviewcli/client/

Usage:
    python scripts/apply_client_docstrings.py _entity.py
    python scripts/apply_client_docstrings.py _glossary.py
    python scripts/apply_client_docstrings.py all  # Process all modules with templates
"""

import re
import sys
from pathlib import Path


def apply_docstrings_to_module(module_name):
    """Apply generated docstrings to a specific client module"""
    
    # Normalize module name (add .py if not present)
    if not module_name.endswith('.py'):
        module_name = f"{module_name}.py"
    
    # Paths
    source_file = Path(f"purviewcli/client/{module_name}")
    template_file = Path(f"doc/boilerplate/generated_docstrings/{module_name}.docstrings.txt")
    
    # Validate files exist
    if not source_file.exists():
        print(f"[X] Source file not found: {source_file}")
        return 0
    
    if not template_file.exists():
        print(f"[X] Template file not found: {template_file}")
        print(f"    Generate it first: python scripts/generate_docstrings.py {module_name}")
        return 0
    
    print(f"\nProcessing: {module_name}")
    print("=" * 60)
    
    # Read the source file
    with open(source_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Read the generated docstrings
    with open(template_file, 'r', encoding='utf-8') as f:
        templates_content = f.read()
    
    # Split into individual method docstrings
    method_sections = templates_content.split("=" * 80)
    
    methods_updated = 0
    methods_skipped = 0
    methods_not_found = 0
    
    for section in method_sections:
        if not section.strip() or "##" not in section:
            continue
        
        # Extract method name - handle different class naming patterns
        match = re.search(r'## (\w+)\.(\w+)', section)
        if not match:
            continue
        
        class_name = match.group(1)
        method_name = match.group(2)
        
        # Extract the docstring (between the triple quotes)
        docstring_match = re.search(r'"""(.+?)"""', section, re.DOTALL)
        if not docstring_match:
            methods_skipped += 1
            continue
        
        docstring = docstring_match.group(1)
        
        # Customize docstring for the specific module
        docstring = customize_docstring(module_name, method_name, docstring)
        
        # Skip if customization returned None (method already documented)
        if docstring is None:
            methods_skipped += 1
            continue
        
        # Try multiple patterns to find the method
        patterns = [
            # Pattern 1: Standard decorator pattern with docstring
            rf'(@decorator\s+def {method_name}\(self, args\):\s+)""".*?"""',
            # Pattern 2: Decorator with multi-line docstring (non-greedy)
            rf'(@decorator\s+def {method_name}\(self, args\):\s+""")(.*?)(""")',
            # Pattern 3: Regular method
            rf'(def {method_name}\(self, args\):\s+)"""[^"]*"""',
            # Pattern 4: Method with short docstring
            rf'(def {method_name}\(self, args\):\s+)"""[^\n]+"""',
        ]
        
        updated = False
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, content, re.DOTALL)
            if match:
                # For pattern 2 (multi-line capture), we need special handling
                if i == 1:
                    # Replace the middle group (docstring content)
                    replacement = match.group(1) + docstring + match.group(3)
                else:
                    replacement = rf'\1"""{docstring}"""'
                
                content = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
                methods_updated += 1
                print(f"[OK] Updated {method_name}")
                updated = True
                break
        
        if not updated:
            methods_not_found += 1
            print(f"[X] Could not find pattern for {method_name}")
    
    # Write back to file
    with open(source_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "=" * 60)
    print(f"Results for {module_name}:")
    print(f"  [OK] Updated:   {methods_updated}")
    print(f"  [SKIP] Skipped: {methods_skipped}")
    print(f"  [X] Not found:  {methods_not_found}")
    
    return methods_updated


def customize_docstring(module_name, method_name, docstring):
    """
    Customize generic docstring based on module and method context
    Returns None to skip methods that are already documented
    """
    
    # Module-specific customizations
    module_customizations = {
        '_unified_catalog.py': customize_uc_docstring,
        '_entity.py': customize_entity_docstring,
        '_glossary.py': customize_glossary_docstring,
        '_collections.py': customize_collections_docstring,
        '_lineage.py': customize_lineage_docstring,
        '_search.py': customize_search_docstring,
        '_scan.py': customize_scan_docstring,
        '_types.py': customize_types_docstring,
        '_workflow.py': customize_workflow_docstring,
        '_relationship.py': customize_relationship_docstring,
        '_policystore.py': customize_policystore_docstring,
        '_management.py': customize_management_docstring,
        '_account.py': customize_account_docstring,
        '_domain.py': customize_domain_docstring,
        '_health.py': customize_health_docstring,
        '_insight.py': customize_insight_docstring,
        '_share.py': customize_share_docstring,
    }
    
    # Get module-specific customization function
    customizer = module_customizations.get(module_name, customize_generic_docstring)
    
    # Apply customization
    return customizer(method_name, docstring)


def customize_uc_docstring(method_name, docstring):
    """Customize for Unified Catalog module"""
    # Skip already documented UC methods
    skip_methods = [
        'get_governance_domains', 'get_governance_domain_by_id',
        'create_governance_domain', 'update_governance_domain',
        'delete_governance_domain', 'add_custom_metadata',
        'update_custom_metadata'
    ]
    if method_name in skip_methods:
        return None
    
    # UC-specific resource types
    resource_mapping = {
        'get_data_products': 'data product',
        'get_data_product_by_id': 'data product',
        'create_data_product': 'data product',
        'update_data_product': 'data product',
        'delete_data_product': 'data product',
        'get_terms': 'Unified Catalog term',
        'get_term_by_id': 'Unified Catalog term',
        'create_term': 'Unified Catalog term',
        'update_term': 'Unified Catalog term',
        'delete_term': 'Unified Catalog term',
        'query_terms': 'Unified Catalog term',
        'get_objectives': 'objective',
        'get_objective_by_id': 'objective',
        'create_objective': 'objective',
        'update_objective': 'objective',
        'delete_objective': 'objective',
        'query_objectives': 'objective',
    }
    
    resource_type = resource_mapping.get(method_name, 'resource')
    docstring = replace_generic_terms(docstring, resource_type, 'Unified Catalog')
    return docstring


def customize_entity_docstring(method_name, docstring):
    """Customize for Entity module"""
    docstring = replace_generic_terms(docstring, 'entity', 'Data Map')
    docstring = docstring.replace('Microsoft Purview.', 'Microsoft Purview Data Map.')
    return docstring


def customize_glossary_docstring(method_name, docstring):
    """Customize for Glossary module"""
    if 'category' in method_name.lower() or 'categories' in method_name.lower():
        resource_type = 'glossary category'
    elif 'term' in method_name.lower():
        resource_type = 'glossary term'
    else:
        resource_type = 'glossary'
    
    docstring = replace_generic_terms(docstring, resource_type, 'Data Map Glossary')
    return docstring


def customize_collections_docstring(method_name, docstring):
    """Customize for Collections module"""
    docstring = replace_generic_terms(docstring, 'collection', 'Collections')
    docstring = docstring.replace(
        'Microsoft Purview.',
        'Microsoft Purview Collections. Collections organize assets into logical groups.'
    )
    return docstring


def customize_lineage_docstring(method_name, docstring):
    """Customize for Lineage module"""
    docstring = replace_generic_terms(docstring, 'lineage information', 'Data Lineage')
    docstring = docstring.replace(
        'Microsoft Purview.',
        'Microsoft Purview Data Lineage. Tracks data flow and transformations.'
    )
    return docstring


def customize_search_docstring(method_name, docstring):
    """Customize for Search module"""
    docstring = replace_generic_terms(docstring, 'search result', 'Search')
    docstring = docstring.replace(
        'Microsoft Purview.',
        'Microsoft Purview Search. Discover data assets across the catalog.'
    )
    return docstring


def customize_scan_docstring(method_name, docstring):
    """Customize for Scan module"""
    if 'scan' in method_name.lower():
        resource_type = 'scan'
    elif 'datasource' in method_name.lower() or 'data_source' in method_name.lower():
        resource_type = 'data source'
    else:
        resource_type = 'scan resource'
    
    docstring = replace_generic_terms(docstring, resource_type, 'Scanning')
    return docstring


def customize_types_docstring(method_name, docstring):
    """Customize for Types module"""
    docstring = replace_generic_terms(docstring, 'type definition', 'Type System')
    docstring = docstring.replace(
        'Microsoft Purview.',
        'Microsoft Purview Type System. Define custom entity and relationship types.'
    )
    return docstring


def customize_workflow_docstring(method_name, docstring):
    """Customize for Workflow module"""
    docstring = replace_generic_terms(docstring, 'workflow', 'Workflows')
    docstring = docstring.replace(
        'Microsoft Purview.',
        'Microsoft Purview Workflows. Automate governance tasks.'
    )
    return docstring


def customize_relationship_docstring(method_name, docstring):
    """Customize for Relationship module"""
    docstring = replace_generic_terms(docstring, 'relationship', 'Relationships')
    docstring = docstring.replace(
        'Microsoft Purview.',
        'Microsoft Purview Relationships. Define connections between entities.'
    )
    return docstring


def customize_policystore_docstring(method_name, docstring):
    """Customize for Policy Store module"""
    docstring = replace_generic_terms(docstring, 'policy', 'Policy Store')
    docstring = docstring.replace(
        'Microsoft Purview.',
        'Microsoft Purview Policy Store. Manage access and data policies.'
    )
    return docstring


def customize_management_docstring(method_name, docstring):
    """Customize for Management module"""
    docstring = replace_generic_terms(docstring, 'management resource', 'Management')
    return docstring


def customize_account_docstring(method_name, docstring):
    """Customize for Account module"""
    docstring = replace_generic_terms(docstring, 'account resource', 'Account Management')
    return docstring


def customize_domain_docstring(method_name, docstring):
    """Customize for Domain module"""
    docstring = replace_generic_terms(docstring, 'domain', 'Domains')
    return docstring


def customize_health_docstring(method_name, docstring):
    """Customize for Health module"""
    docstring = replace_generic_terms(docstring, 'health metric', 'Health Monitoring')
    return docstring


def customize_insight_docstring(method_name, docstring):
    """Customize for Insight module"""
    docstring = replace_generic_terms(docstring, 'insight', 'Insights')
    return docstring


def customize_share_docstring(method_name, docstring):
    """Customize for Share module"""
    docstring = replace_generic_terms(docstring, 'share', 'Data Sharing')
    return docstring


def customize_generic_docstring(method_name, docstring):
    """Generic customization for modules without specific rules"""
    docstring = replace_generic_terms(docstring, 'resource', 'Purview')
    return docstring


def replace_generic_terms(docstring, resource_type, area_name):
    """Replace generic placeholder terms with specific resource names"""
    
    # Replace generic resource references
    replacements = [
        ('resource information', f'{resource_type} information'),
        ('resource metadata', f'{resource_type} metadata'),
        ('resource definition', f'{resource_type} definition'),
        ('resource details', f'{resource_type} details'),
        ('created resource', f'created {resource_type}'),
        ('updated resource', f'updated {resource_type}'),
        ('specified resource', f'specified {resource_type}'),
        ('new resource', f'new {resource_type}'),
        ('existing resource', f'existing {resource_type}'),
        ('Create a new resource', f'Create a new {resource_type}'),
        ('Update an existing resource', f'Update an existing {resource_type}'),
        ('Retrieve resource', f'Retrieve {resource_type}'),
        ('Delete a resource', f'Delete a {resource_type}'),
        ('Search for resources', f'Search for {resource_type}s'),
        ('List all resources', f'List all {resource_type}s'),
        ('Get resource by', f'Get {resource_type} by'),
    ]
    
    for old, new in replacements:
        docstring = docstring.replace(old, new)
    
    # Update generic Purview references
    docstring = docstring.replace(
        'Creates a new resource in Microsoft Purview.',
        f'Creates a new {resource_type} in Microsoft Purview {area_name}.'
    )
    docstring = docstring.replace(
        'Retrieves detailed information about the specified resource.',
        f'Retrieves detailed information about the specified {resource_type} from {area_name}.'
    )
    docstring = docstring.replace(
        'Updates an existing resource with new values.',
        f'Updates an existing {resource_type} in {area_name} with new values.'
    )
    docstring = docstring.replace(
        'Permanently deletes the specified resource.',
        f'Permanently deletes the specified {resource_type} from {area_name}.'
    )
    
    # Update client references to match actual class names
    docstring = docstring.replace('client = Client()', f'client = {get_client_class_name(area_name)}()')
    docstring = docstring.replace('Client()', f'{get_client_class_name(area_name)}()')
    
    return docstring


def get_client_class_name(area_name):
    """Get the proper client class name based on area"""
    mapping = {
        'Unified Catalog': 'UnifiedCatalogClient',
        'Data Map': 'Entity',
        'Data Map Glossary': 'Glossary',
        'Collections': 'Collections',
        'Data Lineage': 'Lineage',
        'Search': 'Search',
        'Scanning': 'Scan',
        'Type System': 'Types',
        'Workflows': 'Workflow',
        'Relationships': 'Relationship',
        'Policy Store': 'PolicyStore',
        'Management': 'Management',
        'Account Management': 'Account',
        'Domains': 'Domain',
        'Health Monitoring': 'Health',
        'Insights': 'Insight',
        'Data Sharing': 'Share',
    }
    return mapping.get(area_name, 'PurviewClient')


def process_all_modules():
    """Process all modules that have template files"""
    templates_dir = Path("doc/boilerplate/generated_docstrings")
    
    if not templates_dir.exists():
        print(f"[X] Templates directory not found: {templates_dir}")
        print("    Generate templates first: python scripts/generate_docstrings.py")
        return
    
    # Find all template files
    template_files = list(templates_dir.glob("*.docstrings.txt"))
    
    if not template_files:
        print("[X] No template files found in doc/boilerplate/generated_docstrings/")
        return
    
    print(f"\nFound {len(template_files)} template files")
    print("=" * 60)
    
    total_updated = 0
    modules_processed = 0
    
    for template_file in sorted(template_files):
        # Extract module name from template filename
        module_name = template_file.name.replace('.docstrings.txt', '')
        
        updated = apply_docstrings_to_module(module_name)
        if updated > 0:
            total_updated += updated
            modules_processed += 1
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Modules processed: {modules_processed}")
    print(f"  Total methods updated: {total_updated}")
    print("\nRun: python scripts/document_client_apis.py")
    print("to verify the updated coverage.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/apply_client_docstrings.py <module_name>")
        print("  python scripts/apply_client_docstrings.py _entity.py")
        print("  python scripts/apply_client_docstrings.py all")
        sys.exit(1)
    
    module_arg = sys.argv[1]
    
    if module_arg.lower() == 'all':
        process_all_modules()
    else:
        updated = apply_docstrings_to_module(module_arg)
        if updated > 0:
            print("\n" + "=" * 60)
            print("Complete! Run: python scripts/document_client_apis.py")
            print("to verify the updated coverage.")
