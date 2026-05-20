# Contributing to pvw-cli

Thank you for contributing.

## Development Workflow

1. Fork the repository on GitHub.
2. Create a feature branch from main.
3. Implement and test your change.
4. Open a pull request against main.

Recommended branch naming:
- feature/<short-description>
- fix/<short-description>
- docs/<short-description>
- chore/<short-description>

## Pull Request Guidelines

1. Keep pull requests focused and reasonably small.
2. Include a clear description of the problem and solution.
3. Link related issues when applicable.
4. Add or update tests when behavior changes.
5. Update documentation for user-visible changes.
6. Ensure CI checks pass before requesting review.

## Coding Standards

1. Follow existing project structure and naming patterns.
2. Preserve separation between CLI commands and client/service logic.
3. Avoid unrelated refactors in functional change PRs.
4. Keep code comments concise and meaningful.
5. Prefer explicit, actionable error handling.

For Python changes:
- Support Python versions defined in pyproject metadata.
- Run formatting/linting/test commands used by the project.

## Commit Quality Requirements

1. Keep commits clean, scoped, and reviewable.
2. Use descriptive commit messages that explain intent.
3. Avoid committing generated artifacts unless required.
4. Do not mix unrelated changes in the same commit.
5. Document rationale in commit messages when behavior or API contracts change.

## Licensing of Contributions

By submitting code, documentation, or any other contribution to this repository,
you agree that your contribution is provided under the Apache License 2.0 and
may be redistributed under the repository license.

If you do not have the right to license your contribution under Apache-2.0,
please do not submit it.

## Security

Do not disclose vulnerabilities in public issues. Follow SECURITY.md for private reporting instructions.
