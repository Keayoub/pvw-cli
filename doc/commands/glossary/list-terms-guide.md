# How to List Glossary Terms with Microsoft Purview CLI

This guide explains the various ways to list and retrieve glossary terms using the Microsoft Purview CLI.

## Overview

The Purview CLI provides several commands to list glossary terms with different levels of detail and filtering options. This flexibility allows you to get exactly the information you need.

## Commands for Listing Terms

### 1. List All Terms in a Glossary (Recommended)

**Command:**
```cmd
pvw glossary list-terms --glossary-guid <GLOSSARY_GUID>
```

**Alternative (same functionality):**
```cmd
pvw glossary read-terms --glossary-guid <GLOSSARY_GUID>
```

**Parameters:**
- `--glossary-guid` (required): The GUID of the glossary containing the terms
- `--limit` (optional): Number of results to return (default: 1000)
- `--offset` (optional): Pagination offset for large result sets (default: 0)
- `--sort` (optional): Sort order - ASC or DESC (default: ASC)
- `--ext-info` (optional): Include extended information (flag)
- `--include-term-hierarchy` (optional): Include term hierarchy relationships (flag)

**Examples:**
```cmd
# Basic usage - list all terms in a glossary
pvw glossary list-terms --glossary-guid "12345678-1234-1234-1234-123456789012"

# With pagination - get first 50 terms
pvw glossary list-terms --glossary-guid "12345678-1234-1234-1234-123456789012" --limit 50

# Include extended info and hierarchy
pvw glossary list-terms --glossary-guid "12345678-1234-1234-1234-123456789012" --ext-info --include-term-hierarchy

# Get next page of results
pvw glossary list-terms --glossary-guid "12345678-1234-1234-1234-123456789012" --limit 50 --offset 50
```

### 2. List Term Headers Only (Lightweight)

For better performance when you only need basic term information:

**Command:**
```cmd
pvw glossary read-terms-headers --glossary-guid <GLOSSARY_GUID>
```

**Parameters:**
- `--glossary-guid` (required): The GUID of the glossary
- `--limit`, `--offset`, `--sort`: Same pagination options as above

**Example:**
```cmd
pvw glossary read-terms-headers --glossary-guid "12345678-1234-1234-1234-123456789012" --limit 100
```

### 3. List Terms in a Specific Category

**Command:**
```cmd
pvw glossary read-category-terms --category-guid <CATEGORY_GUID>
```

**Parameters:**
- `--category-guid` (required): The GUID of the category
- `--limit`, `--offset`, `--sort`: Pagination options

**Example:**
```cmd
pvw glossary read-category-terms --category-guid "87654321-4321-4321-4321-210987654321"
```

### 4. Get Details of a Specific Term

**Command:**
```cmd
pvw glossary read-term --term-guid <TERM_GUID>
```

**Parameters:**
- `--term-guid` (required): The GUID of the specific term
- `--include-term-hierarchy` (optional): Include hierarchy relationships

**Example:**
```cmd
pvw glossary read-term --term-guid "abcdef12-3456-7890-abcd-ef1234567890" --include-term-hierarchy
```

## Finding Glossary GUIDs

Before you can list terms, you need to know the glossary GUID. Use these commands:

**List all glossaries:**
```cmd
pvw glossary list
```

**Get detailed glossary information:**
```cmd
pvw glossary read --glossary-guid <GLOSSARY_GUID>
```

## Output Format

All commands return JSON-formatted output containing:
- Term details (name, definition, status, etc.)
- Relationships and hierarchy information (if requested)
- Associated entities and categories
- Metadata and audit information

## Common Use Cases

### 1. Browse All Terms in a Business Glossary
```cmd
pvw glossary list-terms --glossary-guid "your-glossary-guid" --include-term-hierarchy
```

### 2. Quick Overview of Terms (Headers Only)
```cmd
pvw glossary read-terms-headers --glossary-guid "your-glossary-guid"
```

### 3. Paginated Browsing of Large Glossaries
```cmd
# First page
pvw glossary list-terms --glossary-guid "your-glossary-guid" --limit 25

# Second page
pvw glossary list-terms --glossary-guid "your-glossary-guid" --limit 25 --offset 25
```

### 4. Terms in a Specific Domain/Category
```cmd
pvw glossary read-category-terms --category-guid "your-category-guid"
```

## Tips

1. **Performance**: Use `read-terms-headers` for faster responses when you don't need full term details
2. **Pagination**: Use `--limit` and `--offset` for large glossaries to avoid overwhelming output
3. **Hierarchy**: Add `--include-term-hierarchy` to see term relationships and parent-child structures
4. **Extended Info**: Use `--ext-info` to get additional metadata about each term

## API Mapping

These CLI commands map to the following Microsoft Purview REST API endpoints:
- `list-terms` → `GET /catalog/api/atlas/v2/glossary/{glossaryGuid}/terms`
- `read-terms-headers` → `GET /catalog/api/atlas/v2/glossary/{glossaryGuid}/terms/headers`
- `read-category-terms` → `GET /catalog/api/atlas/v2/glossary/category/{categoryGuid}/terms`
- `read-term` → `GET /catalog/api/atlas/v2/glossary/term/{termGuid}`
