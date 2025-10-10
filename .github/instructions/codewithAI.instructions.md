# Copilot Instructions for Purview_cli Project
## General Principles

- **Adhere to Clean Architecture:**  
    - Separate concerns: keep business logic, data access, and presentation layers distinct.
    - Use dependency injection to promote testability and flexibility.
    - Avoid tight coupling between modules and layers.

- **Respect Project Structure:**  
    - Place CLI commands and documentation classes in the `cli/` directory.
    - The main entry point should be in `cli.py`.
    - Place core business logic in the `purviewcli/client/` directory.
    - Place integrations (e.g., Azure, Purview SDK) in the `integrations/` directory.
    - Place utilities and helpers in the `utils/` directory.
    - Place tests in the `tests/` directory.
    - Mirror the source structure in the `tests/` directory for better test organization.

- **Naming Conventions:**  
    - Use descriptive, consistent names for files, classes, and functions.
    - Use `snake_case` for files and functions, `PascalCase` for classes.

- **Error Handling:**  
    - Always handle exceptions gracefully.
    - Provide meaningful, actionable error messages.
    - Avoid exposing sensitive information in errors.

- **Documentation:**  
    - Add docstrings to all public functions, classes, and modules.
    - Use comments to clarify complex logic or design decisions.

---

## Design Guidelines

- **CLI Design:**  
    - Use `clink` for command-line interfaces.
    - Place CLI commands and documentation classes in the `cli/` directory.
    - The main entry point should be in `cli.py`.
    - Each CLI command should delegate to a service in the `purviewcli/client/` layer.
    - Ensure CLI commands are discoverable and provide helpful usage messages.

- **Integration with Microsoft Purview:**  
    - Use official SDKs and REST APIs.
    - Encapsulate all Azure-specific logic in the `integrations/` directory.
    - Isolate external dependencies to simplify testing and maintenance.
    - When handling Azure-related requests, always use Azure tools and follow Azure code generation and deployment best practices.

- **Testing:**  
    - Write unit tests for all core logic.
    - Use mocks or fakes for external services and integrations.
    - Place all tests in the `tests/` directory, mirroring the source structure.

- **Extensibility & Configuration:**  
    - Design modules to be easily extendable.
    - Avoid hardcoding values; use configuration files or environment variables.
    - Document extension points and configuration options.

---

## What to Avoid

- Do not mix CLI, business logic, and integrations in a single file.
- Do not use global variables for state management.
- Do not bypass the architecture layers.
- Do not duplicate code; prefer reusable utilities and helpers.
- Do not commit secrets or sensitive information.
- **Do not use Unicode emoji or special characters in CLI output** - see Windows Console Compatibility section below.
- Do not use `git checkout` on files with uncommitted work - always commit or stash first.

---

## Windows Console Compatibility

### Critical: Avoid Unicode Emoji in CLI Output

**Problem:** Windows Command Prompt (CMD) and PowerShell use CP-1252 encoding by default, which does not support Unicode emoji characters (U+2705, U+274C, U+1F4CA, etc.).

**Symptoms:**
- `UnicodeEncodeError: 'charmap' codec can't encode character`
- CLI crashes when printing output with emoji
- Users cannot run commands that output emoji

**Solution:**
- Use ASCII-safe alternatives for visual indicators:
  - SUCCESS/OK instead of ✅
  - FAILED/ERROR instead of ❌
  - WARNING instead of ⚠️
  - INFO instead of 🔍
  - [*] for bullet points instead of •
  - [OK], [X], [!] for status indicators

**Example:**
```python
# BAD - Will fail on Windows
console.print("✅ Success: Term created")
console.print("❌ Failed: Term not found")

# GOOD - Works on all platforms
console.print("[green]SUCCESS:[/green] Term created")
console.print("[red]FAILED:[/red] Term not found")
```

---

## Common Failure Causes and Prevention

### 1. Uncommitted Work Loss
**Cause:** Using `git checkout` on files with uncommitted changes
**Prevention:** Always commit or use `git stash` before running checkout commands
**Recovery:** Use conversation history and helper scripts to recreate lost work

### 2. File Corruption from Shell Operations
**Cause:** Using shell one-liners or regex replacements that recursively modify content
**Prevention:** 
- Use proper Python scripts with file I/O for bulk replacements
- Test on a single file first
- Commit before running bulk operations
**Example of dangerous operation:**
```powershell
# BAD - Can cause recursive replacements
(Get-Content file.py) -replace '✓','[OK]' -replace '✗','[X]' | Set-Content file.py
```

### 3. Missing Module Imports
**Cause:** Using libraries without importing them (e.g., `time.sleep()` without `import time`)
**Prevention:** Always verify imports at the top of files
**Common missing imports:**
- `import time` - for sleep() and timing
- `import csv` - for CSV operations
- `import json` - for JSON operations
- `from rich.syntax import Syntax` - for colored JSON output

### 4. PowerShell JSON Parsing Errors
**Cause:** Trying to parse Rich-formatted output with `ConvertFrom-Json`
**Prevention:** Use `--output json` parameter for plain JSON output
**Solution:**
```powershell
# BAD - Rich formatted output cannot be parsed
$terms = py -m purviewcli uc term list --domain-id $id | ConvertFrom-Json

# GOOD - Plain JSON output
$terms = py -m purviewcli uc term list --domain-id $id --output json | ConvertFrom-Json
```

### 5. Invalid Owner IDs
**Cause:** Using email addresses instead of Entra Object IDs (GUIDs)
**Prevention:** Use Entra Object IDs (GUIDs) for owner_id parameters
**Example:**
```bash
# BAD - Email address will fail
pvw uc term create --owner-id user@company.com

# GOOD - Entra Object ID (GUID)
pvw uc term create --owner-id 0360aff3-add5-4b7c-b172-52add69b0199
```

### 6. Rate Limiting and API Throttling
**Cause:** Making too many API requests too quickly
**Prevention:** 
- Use bulk operations (import-csv, update-csv) which have built-in rate limiting
- Add delays between requests in custom scripts (200ms recommended)
- Monitor for 429 (Too Many Requests) errors

### 7. Dry-Run Mode Confusion
**Cause:** Users forget to remove `--dry-run` flag for actual execution
**Prevention:**
- Always show clear dry-run indicators in output
- Provide examples with and without dry-run flag
- Document the difference in help text

---

## Additional Recommendations

- **Code Quality:**  
    - Follow PEP 8 and project-specific style guides.
    - Use type hints where appropriate.
    - Run static analysis and linters before committing.
    - **Test on Windows console** to verify no Unicode errors.

- **Collaboration:**  
    - Write clear, concise commit messages.
    - Document significant architectural or design changes.
    - **Commit frequently** to avoid data loss from accidents.

---

## Copilot-Specific Guidance

- When generating code for Azure or Microsoft Purview:
    - Use Azure tools and follow Azure code generation, deployment, and Azure Functions best practices.
    - Encapsulate Azure-specific logic in the `plugins/` directory.
    - Use mocks for Azure integrations in tests.
- Always respect the project directory structure and separation of concerns.
- Ensure all code is well-documented and tested.
- Adhere strictly to error handling and security guidelines.

---

**By following these instructions, Copilot will help maintain a clean, scalable, and maintainable codebase.**