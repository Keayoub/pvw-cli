#!/usr/bin/env python
"""
Create Business Metadata Groups - Python Example
This script demonstrates how to create business metadata programmatically
"""

import json
import subprocess
import sys
import time
from pathlib import Path

# ANSI color codes for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
GRAY = '\033[90m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{CYAN}{'='*50}{RESET}")
    print(f"{CYAN}{text}{RESET}")
    print(f"{CYAN}{'='*50}{RESET}\n")

def print_success(text):
    print(f"{GREEN}[SUCCESS]{RESET} {text}")

def print_error(text):
    print(f"{RED}[FAILED]{RESET} {text}")

def print_info(text):
    print(f"{YELLOW}[INFO]{RESET} {text}")

def create_metadata_group(template_file, group_name, scope, description):
    """Create a business metadata group from a template file"""
    print_info(f"Creating: {group_name}")
    print(f"{GRAY}       File: {template_file}{RESET}")
    print(f"{GRAY}       Scope: {scope}{RESET}")
    print(f"{GRAY}       Description: {description}{RESET}")
    
    try:
        # Validate with dry-run
        print(f"{GRAY}       Validating JSON...{RESET}")
        result = subprocess.run(
            ['py', '-m', 'purviewcli', 'types', 'create-business-metadata-def',
             '--payload-file', template_file, '--dry-run', '--validate'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print_error(f"Validation failed for {group_name}")
            print(f"{GRAY}{result.stderr}{RESET}")
            return False
        
        # Create the metadata
        result = subprocess.run(
            ['py', '-m', 'purviewcli', 'types', 'create-business-metadata-def',
             '--payload-file', template_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_success(f"Created: {group_name}")
            return True
        else:
            print_error(f"Failed to create: {group_name}")
            print(f"{GRAY}{result.stderr}{RESET}")
            return False
            
    except Exception as e:
        print_error(f"Exception creating {group_name}: {e}")
        return False

def verify_groups():
    """Verify created groups"""
    print_info("Verifying created groups...")
    print()
    
    try:
        result = subprocess.run(
            ['py', '-m', 'purviewcli', 'types', 'list-business-metadata-groups'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except Exception as e:
        print_error(f"Failed to verify groups: {e}")

def main():
    print_header("Business Metadata Creation Script")
    
    # Define templates to create
    templates = [
        {
            'name': 'Governance',
            'file': 'templates/business_metadata_governance.json',
            'scope': 'Business Concept',
            'description': 'Governance metadata for terms and domains'
        },
        {
            'name': 'DataQuality',
            'file': 'templates/business_metadata_quality.json',
            'scope': 'Data Asset',
            'description': 'Quality metrics for tables and files'
        },
        {
            'name': 'Privacy',
            'file': 'templates/business_metadata_privacy.json',
            'scope': 'Business Concept',
            'description': 'Privacy classification for terms'
        },
        {
            'name': 'Documentation',
            'file': 'templates/business_metadata_universal.json',
            'scope': 'Universal',
            'description': 'Documentation links for all entities'
        }
    ]
    
    # Display what will be created
    print(f"{YELLOW}The following Business Metadata groups will be created:{RESET}\n")
    for template in templates:
        print(f"  [*] {template['name']}")
        print(f"{GRAY}      File: {template['file']}{RESET}")
        print(f"{GRAY}      Scope: {template['scope']}{RESET}")
        print(f"{GRAY}      Description: {template['description']}{RESET}")
        print()
    
    # Ask for confirmation
    response = input("Do you want to proceed? (Y/N): ")
    if response.upper() != 'Y':
        print(f"{RED}Cancelled.{RESET}")
        sys.exit(0)
    
    print_header("Creating Metadata Groups")
    
    # Create each metadata group
    success_count = 0
    error_count = 0
    
    for template in templates:
        success = create_metadata_group(
            template['file'],
            template['name'],
            template['scope'],
            template['description']
        )
        
        if success:
            success_count += 1
        else:
            error_count += 1
        
        # Small delay to avoid rate limiting
        time.sleep(1)
        print()
    
    # Summary
    print_header("Summary")
    print(f"{GREEN}SUCCESS: {success_count} groups created{RESET}")
    if error_count > 0:
        print(f"{RED}FAILED: {error_count} groups failed{RESET}")
    else:
        print(f"{GRAY}FAILED: {error_count} groups failed{RESET}")
    print()
    
    # Verify creation
    verify_groups()
    
    # Next steps
    print_header("Next Steps")
    print(f"{YELLOW}1. View all attributes:{RESET}")
    print(f"{GRAY}   py -m purviewcli types list-business-attributes{RESET}\n")
    print(f"{YELLOW}2. View specific group details:{RESET}")
    print(f"{GRAY}   py -m purviewcli types read-business-metadata-def --name Governance{RESET}\n")
    print(f"{YELLOW}3. Apply metadata to entities:{RESET}")
    print(f"{GRAY}   Use Purview UI or entity update commands{RESET}\n")

if __name__ == '__main__':
    main()
