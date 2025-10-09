# Update Term Examples for Notebook

## Summary

You can update existing terms using `pvw uc term update` with the following options:

### Replace Options (overwrites existing values):
- `--acronym`: Replace all acronyms
- `--owner-id`: Replace all owners
- `--resource-name` + `--resource-url`: Replace all resources
- `--name`, `--description`, `--status`, `--domain-id`: Update these properties

### Add Options (preserves existing and adds new):
- `--add-acronym`: Add to existing acronyms
- `--add-owner-id`: Add to existing owners

## Examples

### Example 1: Add an acronym to existing ones
```bash
pvw uc term update \
    --term-id YOUR_TERM_ID \
    --add-acronym "SQL" \
    --add-acronym "DBMS"
```

### Example 2: Replace all acronyms
```bash
pvw uc term update \
    --term-id YOUR_TERM_ID \
    --acronym "NewAcronym1" \
    --acronym "NewAcronym2"
```

### Example 3: Change status
```bash
pvw uc term update \
    --term-id YOUR_TERM_ID \
    --status Published
```

### Example 4: Add owner
```bash
pvw uc term update \
    --term-id YOUR_TERM_ID \
    --add-owner-id "user@company.com"
```

### Example 5: Update multiple properties
```bash
pvw uc term update \
    --term-id YOUR_TERM_ID \
    --name "Updated Term Name" \
    --description "Updated description" \
    --status Published \
    --add-acronym "NewAcronym"
```
