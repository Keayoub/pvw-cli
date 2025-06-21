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

---

## Additional Recommendations

- **Code Quality:**  
    - Follow PEP 8 and project-specific style guides.
    - Use type hints where appropriate.
    - Run static analysis and linters before committing.

- **Collaboration:**  
    - Write clear, concise commit messages.
    - Document significant architectural or design changes.

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