# Purview CLI Command Reference

Complete reference for all Purview CLI commands.

## Command Groups

### [entity](./entity/main.md)
Commands for managing entity operations (12 actions)

### [types](./types/main.md)
Commands for managing types operations (1 actions)


## Quick Reference

| Command | Description | Actions |
|---------|-------------|---------|
| [`entity`](./entity/main.md) | Manage entity operations | addLabels, addLabelsByUniqueAttribute, addOrUpdateBusinessAttribute, ... (12 total) |
| [`types`](./types/main.md) | Manage types operations | readBusinessMetadataDef |

## Usage Examples

```bash
# Get help for any command
pvw <command> --help

# Get help for specific action
pvw <command> <action> --help

# Common operations
pvw entity list
pvw glossary read
pvw lineage get --guid <entity-guid>
```

## Documentation Sections

- **Command Reference**: Individual command documentation
- **[API Documentation](../api/index.html)**: Auto-generated API docs
- **[User Guides](../guides/README.md)**: Step-by-step guides
- **[Examples](../examples/README.md)**: Code examples

---

*Generated automatically from Purview CLI source code*
