# Glossary Commands

Build and manage your business vocabulary with glossary terms, categories, and hierarchies in Microsoft Purview.

!!! tip "Quick Start"
    Manage glossaries, categories, terms, imports, exports, and assigned entity relationships for business metadata governance.

## What You Can Do

- Create and organize glossary terms and categories
- Build hierarchical term structures
- Import and export term sets from CSV
- Assign terms to entities
- Manage term relationships and synonyms

## Quick Examples

=== "List all terms"
    ```bash
    pvw glossary readterms
    ```

=== "Create a term"
    ```bash
    pvw glossary createterm --help
    ```

=== "Import terms from CSV"
    ```bash
    pvw glossary createtermsimport --help
    ```

=== "Create category"
    ```bash
    pvw glossary createcategory --help
    ```

## Available Actions

### Read Operations

| Command | Purpose |
| --- | --- |
| `read` | Retrieve glossary metadata |
| `readdetailed` | Get detailed glossary information |
| `readterms` | List all terms |
| `readtermsheaders` | Get term headers |
| `readterm` | Get specific term |
| `readcategories` | List categories |
| `readcategoriesheaders` | Get category headers |
| `readcategory` | Get specific category |
| `readcategoryterms` | Get terms in category |

### Create Operations

| Command | Purpose |
| --- | --- |
| `create` | Create glossary |
| `createterm` | Create single term |
| `createterms` | Create multiple terms |
| `createcategory` | Create category |
| `createcategories` | Create multiple categories |
| `createtermsimport` | Import terms from file |

### Update Operations

| Command | Purpose |
| --- | --- |
| `put` | Update glossary |
| `putterm` | Update term |
| `puttermpartial` | Partially update term |
| `putcategory` | Update category |
| `putcategorypartial` | Partially update category |
| `putpartial` | Partially update glossary |

### Delete Operations

| Command | Purpose |
| --- | --- |
| `delete` | Delete glossary |
| `deleteterm` | Delete term |
| `deletecategory` | Delete category |

### Entity Assignment

| Command | Purpose |
| --- | --- |
| `createtermsassignedentities` | Assign term to entities |
| `puttermsassignedentities` | Update term assignments |
| `readtermsassignedentities` | List assigned entities |
| `deletetermsassignedentities` | Remove term assignment |

### Export & Import

| Command | Purpose |
| --- | --- |
| `createtermsexport` | Export terms to file |
| `readtermsimport` | Get import status |
| `createtermsimport` | Start import job |

### Relationships

| Command | Purpose |
| --- | --- |
| `readcategoryrelated` | Get related categories |
| `readtermsrelated` | Get related terms |

## Common Workflows

### Build a Business Glossary

```bash
# 1. Create glossary
pvw glossary create --help

# 2. Create categories
pvw glossary createcategories --help

# 3. Add terms
pvw glossary createterms --help

# 4. Assign to entities
pvw glossary createtermsassignedentities --help
```

### Bulk Import Terms

```bash
# Create CSV template
pvw glossary createtermsexport --help

# Import from CSV
pvw glossary createtermsimport --help
```

### Manage Term Hierarchy

Terms and categories support hierarchical organization for complex business vocabularies.

## Related Topics

- [Create Tasks](../task-create.md)
- [Update Tasks](../task-update.md)
- [Delete Tasks](../task-delete.md)
- [Import Tasks](../task-import.md)
- [Entity commands](../entity/main.md)
- [Search commands](../search/main.md)
