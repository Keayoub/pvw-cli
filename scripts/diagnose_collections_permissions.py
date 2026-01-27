#!/usr/bin/env python3
"""
Collections API Permissions Diagnostic Tool

This script helps diagnose permission issues when running 'pvw collections create'.
It checks:
1. Azure authentication configuration
2. Azure RBAC roles on Purview account
3. Purview account-level permissions
4. Network connectivity to Purview endpoints
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Tuple, Optional

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}► {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}═══════════════════════════════════════════════════════════{Colors.END}\n")

def print_check(status: bool, message: str, details: str = ""):
    """Print a check result with status"""
    icon = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"{icon} {message}")
    if details:
        print(f"  {Colors.YELLOW}→{Colors.END} {details}")

def run_command(cmd: List[str], silent: bool = False) -> Tuple[bool, str, str]:
    """Run a shell command and return (success, stdout, stderr)"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_azure_cli() -> bool:
    """Check if Azure CLI is installed"""
    success, stdout, stderr = run_command(["az", "--version"])
    if success:
        print_check(True, "Azure CLI installed")
        version_line = stdout.split('\n')[0] if stdout else "Unknown version"
        print(f"  {Colors.YELLOW}→{Colors.END} {version_line}")
        return True
    else:
        print_check(False, "Azure CLI not found", "Install from https://docs.microsoft.com/cli/azure/install-azure-cli")
        return False

def check_azure_login() -> bool:
    """Check if user is logged in to Azure"""
    success, stdout, stderr = run_command(["az", "account", "show"])
    if success:
        try:
            account = json.loads(stdout)
            print_check(True, f"Logged in as: {account.get('user', {}).get('name', 'Unknown')}")
            print(f"  {Colors.YELLOW}→{Colors.END} Subscription: {account.get('name', 'Unknown')}")
            return True
        except json.JSONDecodeError:
            print_check(False, "Failed to parse account info")
            return False
    else:
        print_check(False, "Not logged in to Azure", "Run: az login")
        return False

def check_service_principal_env() -> Tuple[bool, Dict[str, str]]:
    """Check if Service Principal environment variables are set"""
    required_vars = ["AZURE_CLIENT_ID", "AZURE_TENANT_ID", "AZURE_CLIENT_SECRET"]
    env_vars = {}
    all_set = True
    
    for var in required_vars:
        if var in os.environ:
            if var == "AZURE_CLIENT_SECRET":
                env_vars[var] = "***HIDDEN***"
                print_check(True, f"{var} is set")
            else:
                env_vars[var] = os.environ[var]
                print_check(True, f"{var} is set", os.environ[var])
        else:
            print_check(False, f"{var} not set")
            all_set = False
    
    return all_set, env_vars

def check_purview_env() -> Tuple[bool, Optional[str]]:
    """Check if Purview environment variables are set"""
    account_name = os.environ.get("PURVIEW_ACCOUNT_NAME")
    if account_name:
        # Check format
        if "." in account_name or "://" in account_name:
            print_check(False, f"PURVIEW_ACCOUNT_NAME has wrong format: {account_name}", 
                       "Should be just the account name, not a full URL")
            return False, account_name
        print_check(True, f"PURVIEW_ACCOUNT_NAME is set", account_name)
        return True, account_name
    else:
        print_check(False, "PURVIEW_ACCOUNT_NAME not set")
        return False, None

def get_service_principal_object_id(client_id: str) -> Optional[str]:
    """Get the Object ID of a service principal"""
    success, stdout, stderr = run_command(["az", "ad", "sp", "show", "--id", client_id, "--query", "id", "-o", "tsv"])
    if success and stdout:
        return stdout
    return None

def check_purview_account_exists(account_name: str) -> Tuple[bool, Optional[Dict]]:
    """Check if Purview account exists"""
    # First get subscription and resource group from current context
    success, sub_id, _ = run_command(["az", "account", "show", "--query", "id", "-o", "tsv"])
    if not success:
        print_check(False, "Could not get current subscription")
        return False, None
    
    # List Purview accounts to find the one with matching name
    success, stdout, stderr = run_command(["az", "purview", "account", "list", "--query", 
                                          f"[?name=='{account_name}']", "-o", "json"])
    if success and stdout:
        try:
            accounts = json.loads(stdout)
            if accounts:
                account = accounts[0]
                print_check(True, f"Purview account '{account_name}' found")
                print(f"  {Colors.YELLOW}→{Colors.END} Resource ID: {account.get('id', 'Unknown')}")
                return True, account
            else:
                print_check(False, f"Purview account '{account_name}' not found")
                return False, None
        except json.JSONDecodeError:
            print_check(False, "Failed to parse account list")
            return False, None
    else:
        print_check(False, "Failed to query Purview accounts", stderr)
        return False, None

def check_azure_rbac_roles(sp_object_id: str, account_resource_id: str) -> bool:
    """Check if service principal has required Azure RBAC roles"""
    success, stdout, stderr = run_command([
        "az", "role", "assignment", "list",
        "--assignee-object-id", sp_object_id,
        "--scope", account_resource_id,
        "--output", "json"
    ])
    
    if success and stdout:
        try:
            assignments = json.loads(stdout)
            if not assignments:
                print_check(False, "No Azure RBAC role assignments found on Purview account")
                print(f"  {Colors.YELLOW}→{Colors.END} Service Principal needs: Contributor or Owner role")
                return False
            
            required_roles = ["Owner", "Contributor", "Data Admin"]
            has_required_role = False
            
            for assignment in assignments:
                role_name = assignment.get('roleDefinitionName', 'Unknown')
                print_check(role_name in required_roles, f"Azure RBAC Role: {role_name}")
                if role_name in required_roles:
                    has_required_role = True
            
            return has_required_role
        except json.JSONDecodeError:
            print_check(False, "Failed to parse role assignments")
            return False
    else:
        print_check(False, "Failed to query role assignments", stderr)
        return False

def check_purview_permissions(account_name: str) -> bool:
    """Check if user/SP has Purview-level permissions"""
    # Try to list collections to test basic permissions
    success, stdout, stderr = run_command(["pvw", "collections", "list"])
    
    if success:
        print_check(True, "Can list collections (Purview permissions OK)")
        return True
    else:
        if "403" in stderr or "Forbidden" in stderr:
            print_check(False, "Access denied when listing collections", 
                       "Service Principal may lack Purview Data Source Administrator role")
        else:
            print_check(False, "Failed to list collections", stderr[:100])
        return False

def check_network_connectivity() -> bool:
    """Check network connectivity to Purview endpoints"""
    import socket
    
    endpoints = [
        ("management.azure.com", 443),
        ("graph.microsoft.com", 443),
    ]
    
    all_connected = True
    for host, port in endpoints:
        try:
            socket.create_connection((host, port), timeout=5)
            print_check(True, f"Can reach {host}:{port}")
        except (socket.timeout, socket.error) as e:
            print_check(False, f"Cannot reach {host}:{port}", str(e))
            all_connected = False
    
    return all_connected

def show_recommendations(checks: Dict[str, bool]):
    """Show recommendations based on failed checks"""
    print_section("Recommendations")
    
    issues = []
    
    if not checks.get("azure_cli"):
        issues.append("1. Install Azure CLI: https://docs.microsoft.com/cli/azure/install-azure-cli")
    
    if not checks.get("azure_login"):
        issues.append("2. Login to Azure: az login")
    
    if checks.get("service_principal") and not checks.get("azure_login"):
        issues.append("3. Use Service Principal for authentication:")
        issues.append("   export AZURE_CLIENT_ID=<your-client-id>")
        issues.append("   export AZURE_TENANT_ID=<your-tenant-id>")
        issues.append("   export AZURE_CLIENT_SECRET=<your-client-secret>")
    
    if not checks.get("purview_env"):
        issues.append("4. Set Purview account: export PURVIEW_ACCOUNT_NAME=<your-account-name>")
    
    if not checks.get("azure_rbac"):
        issues.append("5. Assign Azure RBAC role (Contributor) to Service Principal on Purview account")
        issues.append("   az role assignment create --role 'Contributor' \\")
        issues.append("     --assignee <sp-object-id> --scope <purview-resource-id>")
    
    if not checks.get("purview_perms"):
        issues.append("6. Assign Purview role via Azure Portal:")
        issues.append("   a. Go to Purview Account > Access Control (IAM)")
        issues.append("   b. Add role assignment > Purview Data Source Administrator")
        issues.append("   c. Select your Service Principal")
    
    if issues:
        for issue in issues:
            print(issue)
    else:
        print(f"{Colors.GREEN}All checks passed! You should be able to create collections.{Colors.END}")
    
    print("\n" + "="*60)
    print("If you still have issues after addressing the above:")
    print(f"  {Colors.BLUE}1. Wait 5-10 minutes for permissions to propagate{Colors.END}")
    print(f"  {Colors.BLUE}2. Try: az logout && az login (refresh authentication){Colors.END}")
    print(f"  {Colors.BLUE}3. Enable debug: export LOGLEVEL=DEBUG{Colors.END}")
    print(f"  {Colors.BLUE}4. Check: doc/COLLECTIONS_PERMISSIONS.md{Colors.END}")

def main():
    """Run all diagnostics"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}PVW Collections Permissions Diagnostic Tool{Colors.END}\n")
    
    checks = {
        "azure_cli": False,
        "azure_login": False,
        "service_principal": False,
        "purview_env": False,
        "purview_account_exists": False,
        "azure_rbac": False,
        "purview_perms": False,
        "network": False,
    }
    
    # Section 1: Azure CLI
    print_section("1. Azure CLI & Authentication")
    if not check_azure_cli():
        print("\nCannot proceed without Azure CLI. Please install it first.")
        sys.exit(1)
    
    # Check both Azure CLI login and Service Principal
    has_azure_login = check_azure_login()
    has_sp_env = check_service_principal_env()[0]
    
    if not has_azure_login and not has_sp_env:
        print(f"\n{Colors.RED}No authentication method configured!{Colors.END}")
        print("Please either: az login OR set AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET")
        sys.exit(1)
    
    checks["azure_login"] = has_azure_login or has_sp_env
    
    # Section 2: Purview Configuration
    print_section("2. Purview Configuration")
    purview_env_ok, account_name = check_purview_env()
    checks["purview_env"] = purview_env_ok
    
    if not purview_env_ok or not account_name:
        print(f"\n{Colors.YELLOW}Skipping remaining checks - PURVIEW_ACCOUNT_NAME not set{Colors.END}")
        show_recommendations(checks)
        sys.exit(1)
    
    # Section 3: Purview Account Existence
    print_section("3. Purview Account Verification")
    account_exists, account_info = check_purview_account_exists(account_name)
    checks["purview_account_exists"] = account_exists
    
    if not account_exists:
        print(f"\n{Colors.YELLOW}Skipping remaining checks - Account not found{Colors.END}")
        show_recommendations(checks)
        sys.exit(1)
    
    # Section 4: Azure RBAC Roles
    print_section("4. Azure RBAC Roles")
    sp_object_id = None
    if has_sp_env:
        env_vars = os.environ
        sp_object_id = get_service_principal_object_id(env_vars.get("AZURE_CLIENT_ID", ""))
        if sp_object_id:
            print(f"Service Principal Object ID: {sp_object_id}")
    
    if sp_object_id and account_info:
        rbac_ok = check_azure_rbac_roles(sp_object_id, account_info.get("id", ""))
        checks["azure_rbac"] = rbac_ok
    
    # Section 5: Purview Permissions
    print_section("5. Purview Account Permissions")
    purview_perms_ok = check_purview_permissions(account_name)
    checks["purview_perms"] = purview_perms_ok
    
    # Section 6: Network Connectivity
    print_section("6. Network Connectivity")
    network_ok = check_network_connectivity()
    checks["network"] = network_ok
    
    # Section 7: Recommendations
    show_recommendations(checks)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {e}{Colors.END}")
        sys.exit(1)
