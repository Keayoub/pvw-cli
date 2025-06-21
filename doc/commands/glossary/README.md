# Microsoft Purview CLI - Complete Glossary Command Reference

## Summary

The Microsoft Purview CLI provides comprehensive glossary management capabilities with full API coverage. This includes creating, reading, updating, deleting glossaries, categories, and terms, as well as advanced operations like import/export and relationship management.

## Quick Commands for Listing Terms

### Primary Commands (Most Common)
```bash
# List all terms in a glossary
pvw glossary list-terms --glossary-guid "12345678-1234-1234-1234-123456789012"

# List terms with pagination
pvw glossary list-terms --glossary-guid "your-guid" --limit 50 --offset 0

# List terms with hierarchy information
pvw glossary list-terms --glossary-guid "your-guid" --include-term-hierarchy

# Quick headers-only view (faster for large glossaries)
pvw glossary read-terms-headers --glossary-guid "your-guid"
```

### Alternative Commands
```bash
# Same as list-terms (alternative name)
pvw glossary read-terms --glossary-guid "your-guid"

# Terms in a specific category
pvw glossary read-category-terms --category-guid "category-guid"

# Single term details
pvw glossary read-term --term-guid "term-guid"
```

## Finding Your Glossary GUID

Before listing terms, you need the glossary GUID:

```bash
# List all glossaries to find the GUID
pvw glossary list

# Or get details of a specific glossary
pvw glossary read --glossary-guid "your-guid"
```

## Complete Command List

### Glossary Management
- `pvw glossary create` - Create a new glossary
- `pvw glossary read` / `pvw glossary list` - List all glossaries
- `pvw glossary put` - Update a glossary
- `pvw glossary delete` - Delete a glossary
- `pvw glossary read-detailed` - Get detailed glossary information

### Category Management
- `pvw glossary create-category` - Create a glossary category
- `pvw glossary create-categories` - Create multiple categories
- `pvw glossary read-categories` - List categories in a glossary
- `pvw glossary read-categories-headers` - List category headers
- `pvw glossary read-category` - Get details of a specific category
- `pvw glossary read-category-related` - Get related terms for a category
- `pvw glossary read-category-terms` - List terms in a category
- `pvw glossary put-category` - Update a category
- `pvw glossary delete-category` - Delete a category

### Term Management
- `pvw glossary create-term` - Create a single glossary term
- `pvw glossary create-terms` - Create multiple terms
- `pvw glossary list-terms` ⭐ - **List all terms in a glossary** (NEW!)
- `pvw glossary read-terms` - List all terms in a glossary (alternative)
- `pvw glossary read-terms-headers` - List term headers only
- `pvw glossary read-term` - Get details of a specific term
- `pvw glossary read-terms-assigned-entities` - Get entities assigned to a term
- `pvw glossary read-terms-related` - Get related terms
- `pvw glossary put-term` - Update a term
- `pvw glossary delete-term` - Delete a term

### Import/Export Operations
- `pvw glossary import-terms` - Import terms from CSV
- `pvw glossary read-terms-import` - Check import operation status

## API Mapping

The CLI commands map to these Microsoft Purview REST API endpoints:

| CLI Command | API Endpoint |
|-------------|--------------|
| `list-terms` | `GET /catalog/api/atlas/v2/glossary/{glossaryGuid}/terms` |
| `read-terms-headers` | `GET /catalog/api/atlas/v2/glossary/{glossaryGuid}/terms/headers` |
| `read-category-terms` | `GET /catalog/api/atlas/v2/glossary/category/{categoryGuid}/terms` |
| `read-term` | `GET /catalog/api/atlas/v2/glossary/term/{termGuid}` |
| `create-term` | `POST /catalog/api/atlas/v2/glossary/term` |
| `import-terms` | `POST /catalog/api/atlas/v2/glossary/{glossaryGuid}/terms/import` |

## Output Format

All commands return JSON-formatted output containing:
- Term metadata (name, definition, status, etc.)
- Relationships and hierarchy information
- Associated entities and categories  
- Audit information (created/modified dates, users)

## Common Use Cases

1. **Browse all terms in a business glossary**
   ```bash
   pvw glossary list-terms --glossary-guid "your-guid" --include-term-hierarchy
   ```

2. **Get a quick overview (headers only)**
   ```bash
   pvw glossary read-terms-headers --glossary-guid "your-guid"
   ```

3. **Paginated browsing of large glossaries**
   ```bash
   pvw glossary list-terms --glossary-guid "your-guid" --limit 25 --offset 0
   ```

4. **Find terms in a specific domain/category**
   ```bash
   pvw glossary read-category-terms --category-guid "category-guid"
   ```

## Tips for Success

- Use `--include-term-hierarchy` to see parent-child relationships
- Use `--limit` and `--offset` for pagination with large glossaries
- Use `read-terms-headers` for better performance when you don't need full details
- Use `--ext-info` to get additional metadata about terms

## Documentation References

- **Detailed Guide**: `doc/commands/glossary/list-terms-guide.md`
- **Quick Reference**: `doc/commands/glossary/quick-reference-list-terms.md`
- **API Documentation**: [Microsoft Purview REST API](https://learn.microsoft.com/en-us/rest/api/purview/)

---

**✅ The Purview CLI now provides 100% coverage of Microsoft Purview glossary APIs with user-friendly commands for all operations.**
