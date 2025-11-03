"""
Fix incorrect client class names in docstrings
Replaces patterns like EntityEntity() with Entity(), GlossaryGlossary() with Glossary(), etc.
"""

import re
from pathlib import Path


def fix_client_names_in_file(file_path):
    """Fix client class names in a single file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Mapping of wrong patterns to correct ones
    fixes = [
        (r'EntityEntity\(\)', 'Entity()'),
        (r'GlossaryGlossary\(\)', 'Glossary()'),
        (r'SearchSearch\(\)', 'Search()'),
        (r'LineageLineage\(\)', 'Lineage()'),
        (r'CollectionsCollections\(\)', 'Collections()'),
        (r'TypesTypes\(\)', 'Types()'),
        (r'ScanScan\(\)', 'Scan()'),
        (r'WorkflowWorkflow\(\)', 'Workflow()'),
        (r'RelationshipRelationship\(\)', 'Relationship()'),
        (r'PolicystorePolicystore\(\)', 'Policystore()'),
        (r'ManagementManagement\(\)', 'Management()'),
        (r'AccountAccount\(\)', 'Account()'),
        (r'InsightInsight\(\)', 'Insight()'),
        (r'ShareShare\(\)', 'Share()'),
        (r'DomainDomain\(\)', 'Domain()'),
        (r'HealthHealth\(\)', 'Health()'),
    ]
    
    changes_made = 0
    for wrong_pattern, correct_name in fixes:
        matches = len(re.findall(wrong_pattern, content))
        if matches > 0:
            content = re.sub(wrong_pattern, correct_name, content)
            changes_made += matches
            print(f"  Fixed {matches} occurrences: {wrong_pattern} -> {correct_name}")
    
    if changes_made > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes_made
    
    return 0


def fix_all_client_modules():
    """Fix client names in all client modules"""
    client_dir = Path("purviewcli/client")
    
    modules_to_fix = [
        "_entity.py",
        "_glossary.py",
        "_search.py",
        "_lineage.py",
        "_collections.py",
        "_types.py",
        "_scan.py",
        "_workflow.py",
        "_relationship.py",
        "_policystore.py",
        "_management.py",
        "_account.py",
        "_insight.py",
        "_share.py",
        "_domain.py",
        "_health.py",
    ]
    
    total_fixes = 0
    modules_fixed = 0
    
    print("Fixing client class names in docstrings...")
    print("=" * 60)
    
    for module_name in modules_to_fix:
        file_path = client_dir / module_name
        if file_path.exists():
            print(f"\nProcessing {module_name}:")
            fixes = fix_client_names_in_file(file_path)
            if fixes > 0:
                total_fixes += fixes
                modules_fixed += 1
                print(f"  [OK] Fixed {fixes} client names")
            else:
                print(f"  [SKIP] No issues found")
        else:
            print(f"\n[X] File not found: {file_path}")
    
    print("\n" + "=" * 60)
    print(f"SUMMARY:")
    print(f"  Modules processed: {modules_fixed}")
    print(f"  Total fixes: {total_fixes}")
    print("\nRun: python scripts/document_client_apis.py")
    print("to verify the changes.")


if __name__ == "__main__":
    fix_all_client_modules()
