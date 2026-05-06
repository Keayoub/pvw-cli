# Security Policy

## Supported Versions

| Version | Status | Support Until |
|---------|--------|----------------|
| 1.11.x  | Active | Ongoing |
| 1.10.x  | Security fixes only | 2026-06-30 |
| < 1.10  | Unsupported | N/A |

We recommend always using the latest version to ensure you have the most recent security updates and features.

## Reporting Security Vulnerabilities

**Please do NOT open a public GitHub issue for security vulnerabilities.**

If you discover a security vulnerability in the Purview CLI, please report it responsibly by emailing **security@purviewcli.dev** with:

1. **Title**: Brief description of the vulnerability
2. **Description**: Detailed explanation of the issue
3. **Impact**: Potential impact and severity (critical, high, medium, low)
4. **Steps to Reproduce**: Clear steps or proof-of-concept code
5. **Affected Versions**: Which versions are impacted
6. **Suggested Fix**: Any proposed solution (if available)

### Response Timeline

- **Initial acknowledgment**: Within 24 hours
- **Investigation**: Within 48-72 hours
- **Update**: Regular progress updates every 7 days
- **Resolution**: Target of 30 days for security patches

## Security Best Practices

When using the Purview CLI, follow these recommendations:

### Authentication & Credentials

- ✅ Use **Azure Managed Identities** when running in Azure environments
- ✅ Use **Service Principals** with minimal required permissions
- ✅ Store credentials in **Azure Key Vault**, never in code or configuration files
- ✅ Use **short-lived tokens** where possible
- ✅ Rotate credentials regularly (at least quarterly)
- ❌ Never commit credentials, API keys, or secrets to version control
- ❌ Never use personal credentials in production environments

### Data Protection

- ✅ Use **TLS 1.2+** for all API connections (enforced by default)
- ✅ Validate SSL certificates in production (default behavior)
- ✅ Encrypt sensitive data in transit and at rest
- ✅ Restrict access to Purview catalogs using Azure RBAC
- ✅ Enable audit logging for sensitive operations
- ❌ Don't disable certificate validation for debugging in production

### Access Control

- ✅ Apply **principle of least privilege** - grant only necessary permissions
- ✅ Use **Azure RBAC roles** to control who can run CLI commands
- ✅ Audit who has access to the CLI and Purview resources
- ✅ Regularly review and revoke unnecessary permissions
- ✅ Use **service principals** instead of user credentials for automation
- ❌ Don't use overly broad roles (e.g., Owner, Contributor) for routine operations

### Network Security

- ✅ Use **private endpoints** when accessing Purview from Azure networks
- ✅ Restrict outbound traffic using **network security groups** or firewalls
- ✅ Use **VPN or private networks** for remote CLI access
- ✅ Monitor network activity for suspicious patterns
- ❌ Don't expose Purview API endpoints to the public internet

### Code & Scripting

- ✅ Validate all user input before using in commands
- ✅ Use environment variables or secure vaults for sensitive configuration
- ✅ Review scripts for hardcoded credentials before committing
- ✅ Use pre-commit hooks to prevent credential commits
- ✅ Keep dependencies up-to-date with security patches
- ❌ Don't concatenate user input directly into shell commands

### Monitoring & Auditing

- ✅ Enable **Azure Monitor** and **Application Insights** for production deployments
- ✅ Monitor authentication failures and permission errors
- ✅ Review audit logs regularly for suspicious activity
- ✅ Set up alerts for critical operations
- ✅ Log all bulk operations for audit trails
- ❌ Don't ignore security warnings or audit alerts

## Dependencies & Vulnerabilities

This project uses several third-party dependencies. We:

- Monitor dependencies for known vulnerabilities using GitHub Dependabot
- Apply security patches promptly
- Regularly update dependencies to latest secure versions
- Review all dependencies for compliance with security policies

### Vulnerability Reporting for Dependencies

If you find a vulnerability in a dependency:

1. Check if there's already a [GitHub security advisory](https://github.com/Keayoub/pvw-cli/security/advisories)
2. Report to the dependency maintainer directly if applicable
3. Email security@purviewcli.dev with details

## Security Standards

This project aims to follow:

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) security guidelines
- [Microsoft Security Development Lifecycle (SDL)](https://www.microsoft.com/en-us/securityengineering/sdl/) practices
- [Azure security best practices](https://learn.microsoft.com/en-us/azure/security/fundamentals/security-best-practices-and-patterns)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/) most dangerous software weaknesses

## Secure Development

### For Contributors

When contributing to pvw-cli:

- ✅ Review [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines
- ✅ Follow secure coding practices
- ✅ Use credential scanning tools before committing
- ✅ Test security scenarios (invalid input, missing permissions, etc.)
- ✅ Document any security considerations for new features
- ❌ Don't commit any credentials, keys, or secrets

### Pre-commit Security

We recommend installing security tools:

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks (detects secrets, validates code, etc.)
pre-commit install

# Manually run checks
pre-commit run --all-files
```

## Security Disclosure

We follow a **coordinated disclosure** approach:

1. **Reporter**: Privately discloses vulnerability
2. **Team**: Investigates and develops fix
3. **Patch**: Security patch is created and tested
4. **Release**: Patch is released in a security update
5. **Disclosure**: Vulnerability is publicly disclosed after patch is available

Users are notified via:
- GitHub security advisories
- Release notes
- Email to registered users (if applicable)

## Questions?

For general security questions, email **security@purviewcli.dev**

For other inquiries, see [README.md](README.md) for contact information.

---

**Last Updated**: May 6, 2026  
**Version**: 1.0
