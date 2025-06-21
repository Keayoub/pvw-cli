# Quick Reference: List Glossary Terms

## Primary Command (Recommended)
```
pvw glossary list-terms --glossary-guid <GLOSSARY_GUID>
```

## Alternative Commands
- **read-terms**: Same as list-terms
- **read-terms-headers**: Lightweight version (headers only)
- **read-category-terms**: Terms in a specific category
- **read-term**: Single term details

## Common Options
- `--limit 50` - Limit results 
- `--offset 25` - Pagination
- `--include-term-hierarchy` - Include relationships
- `--ext-info` - Extended information

## Examples
```
# List all terms in a glossary
pvw glossary list-terms --glossary-guid "12345678-1234-1234-1234-123456789012"

# Get first 50 terms with hierarchy
pvw glossary list-terms --glossary-guid "12345678-1234-1234-1234-123456789012" --limit 50 --include-term-hierarchy

# Quick headers-only view
pvw glossary read-terms-headers --glossary-guid "12345678-1234-1234-1234-123456789012"
```

For detailed guide see: `doc/commands/glossary/list-terms-guide.md`
