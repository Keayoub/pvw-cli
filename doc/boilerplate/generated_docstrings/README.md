# Docstring Application Guide

## Generated Templates

The `generate_docstrings.py` script has created comprehensive docstring templates for your client modules. These templates are ready to be copied into your source files.

## Generated Files

Located in: `doc/boilerplate/generated_docstrings/`

- **_entity.py.docstrings.txt** - 51 methods
- **_glossary.py.docstrings.txt** - 48 methods
- **_collections.py.docstrings.txt** - 27 methods
- **_unified_catalog.py.docstrings.txt** - 60 methods
- **_lineage.py.docstrings.txt** - 23 methods
- **_search.py.docstrings.txt** - 22 methods

**Total:** 231 method docstrings ready to use!

## How to Use the Templates

### Option 1: Manual Copy-Paste (Recommended for Review)

1. **Open the generated docstring file**
   ```powershell
   code doc/boilerplate/generated_docstrings/_entity.py.docstrings.txt
   ```

2. **Open your source file**
   ```powershell
   code purviewcli/client/_entity.py
   ```

3. **For each method:**
   - Find the method in the docstring file (e.g., `## Entity.entityCreate`)
   - Copy the generated docstring
   - Paste it right after the method definition in your source file
   - **Review and customize** - The templates are a starting point!

### Option 2: Semi-Automated with VS Code Multi-Cursor

1. Open both files side-by-side in VS Code
2. Use multi-cursor editing (Alt+Click) to select method signatures
3. Paste docstrings in batch
4. Review and refine

### Option 3: Automated Script (Use with Caution)

We can create a script to automatically insert docstrings, but **manual review is still recommended** to ensure accuracy.

## Customization Checklist

After pasting a generated docstring, review and update:

### ✅ Description Section
- [ ] Verify the description matches what the method actually does
- [ ] Add specific details about Microsoft Purview behavior
- [ ] Include any important caveats or limitations

### ✅ Args Section
- [ ] Replace `[TODO: ...]` placeholders with actual parameter details
- [ ] Verify parameter types match the actual code
- [ ] Add valid value ranges or enum options
- [ ] Specify which parameters are required vs optional
- [ ] Add examples for complex parameter structures

### ✅ Returns Section
- [ ] Verify the return structure matches actual API response
- [ ] Add or remove fields based on actual data
- [ ] Document conditional fields (only present in certain cases)
- [ ] Add examples of actual return values

### ✅ Raises Section
- [ ] Add method-specific exceptions
- [ ] Document business rule violations
- [ ] Include rate limit details if applicable

### ✅ Example Section
- [ ] Test the example code - make sure it runs!
- [ ] Use realistic values (real GUIDs, actual resource names)
- [ ] Add error handling examples
- [ ] Show common parameter combinations

### ✅ Use Cases Section
- [ ] Add domain-specific use cases
- [ ] Reference related methods (e.g., "Use entityCreate before entityUpdate")
- [ ] Explain when to use this method vs alternatives

## Example: Before and After

### Before (No Docstring)
```python
@decorator
def entityCreate(self, args):
    """Create a new entity (Official API: Create Entity)"""
    self.method = "POST"
    self.endpoint = ENDPOINTS["entity"]["create"]
    self.params = get_api_version_params("datamap")
    self.payload = get_json(args, "--payloadFile")
```

### After (With Generated Template)
```python
@decorator
def entityCreate(self, args):
    """
    Create a new entity in Microsoft Purview Data Map.
    
    Creates a new entity (asset, table, data source, etc.) with the specified
    type and attributes. Entities represent data assets in your organization's
    data landscape.
    
    Official API: https://learn.microsoft.com/rest/api/purview/datamapdataplane/entity/create
    
    Args:
        args: Dictionary containing operation arguments:
              - '--payloadFile' (str): Path to JSON file with entity definition
              
              Entity payload structure:
              {
                  "typeName": str,      # Required: e.g., "DataSet", "azure_sql_table"
                  "attributes": {       # Required: Type-specific attributes
                      "qualifiedName": str,  # Required: Unique identifier
                      "name": str,           # Required: Display name
                      "description": str,    # Optional: Entity description
                      "owner": str           # Optional: Owner email/ID
                  },
                  "classifications": [  # Optional: Classification tags
                      {
                          "typeName": str  # e.g., "PII", "Confidential"
                      }
                  ]
              }
    
    Returns:
        Dictionary containing created entity:
            {
                'guid': str,              # Unique entity identifier (UUID)
                'typeName': str,          # Entity type
                'attributes': {           # Entity attributes
                    'qualifiedName': str,
                    'name': str,
                    ...
                },
                'status': str,            # 'ACTIVE' or 'DRAFT'
                'createTime': int,        # Creation timestamp (Unix)
                'createdBy': str          # Creator username
            }
    
    Raises:
        ValueError: When required parameters are missing:
            - payloadFile not provided
            - Entity missing required fields (typeName, qualifiedName, name)
            
        AuthenticationError: When Azure credentials invalid or expired
        
        HTTPError: When Purview API returns error:
            - 400: Invalid entity structure or type not found
            - 401: Authentication failed
            - 403: Insufficient permissions (requires Data Curator role)
            - 409: Entity with qualifiedName already exists
            - 429: Rate limit exceeded (max 100 creates/minute)
            - 500: Purview internal error
    
    Example:
        # Create a simple dataset entity
        entity_data = {
            "typeName": "DataSet",
            "attributes": {
                "qualifiedName": "sales_2023@myorg",
                "name": "Sales Data 2023",
                "description": "Annual sales records",
                "owner": "data-team@myorg.com"
            }
        }
        
        # Save to file
        with open('entity.json', 'w') as f:
            json.dump(entity_data, f)
        
        # Create entity
        client = Entity()
        args = {'--payloadFile': 'entity.json'}
        result = client.entityCreate(args)
        
        print(f"Created entity: {result['guid']}")
        print(f"Qualified name: {result['attributes']['qualifiedName']}")
        
        # Create with classifications
        entity_with_class = {
            "typeName": "azure_sql_table",
            "attributes": {
                "qualifiedName": "mssql://server.database.windows.net/db/schema/customers",
                "name": "Customers Table"
            },
            "classifications": [
                {"typeName": "PII"},
                {"typeName": "GDPR"}
            ]
        }
        
    Use Cases:
        - Data Onboarding: Register new data sources when they're added
        - Metadata Management: Document undocumented datasets
        - Automation: Auto-discover and register assets via scripts
        - Testing: Create test entities for development
        - Migration: Import catalog metadata from other systems
        
    See Also:
        - entityUpdate: Modify existing entity
        - entityBulkCreateOrUpdate: Create multiple entities efficiently
        - entityReadByUniqueAttribute: Retrieve by qualifiedName
    """
    self.method = "POST"
    self.endpoint = ENDPOINTS["entity"]["create"]
    self.params = get_api_version_params("datamap")
    self.payload = get_json(args, "--payloadFile")
```

## Quick Start: Document Your First Method

Let's document one method together:

1. **Choose a method** - Start with one you use frequently
   ```powershell
   # Example: entityRead
   code purviewcli/client/_entity.py:80
   ```

2. **Get the generated template**
   ```powershell
   # Open the docstring file
   code doc/boilerplate/generated_docstrings/_entity.py.docstrings.txt
   # Search for: ## Entity.entityRead
   ```

3. **Copy and customize**
   - Copy the entire docstring (from `"""` to `"""`)
   - Paste after the method definition
   - Update the description with actual behavior
   - Fill in the `[TODO]` placeholders
   - Test the example code

4. **Verify**
   ```bash
   # Run your analysis tool
   python scripts/document_client_apis.py
   
   # Should show improved coverage for _entity.py
   ```

5. **Commit**
   ```bash
   git add purviewcli/client/_entity.py
   git commit -m "docs: Add comprehensive docstring for entityRead method"
   ```

## Batch Documentation Strategy

### Week 1: Core Entity Operations (Focus on Most-Used)
Document these 10 methods first:
- entityCreate
- entityRead
- entityUpdate
- entityDelete
- entityReadByUniqueAttribute
- entityBulkCreateOrUpdate
- entityAddClassification
- entitySearch (if in _entity.py)
- entityUpdateAttribute
- entityReadHeader

### Week 2: Glossary Operations
Document these 12 methods:
- glossaryCreate
- glossaryRead
- glossaryUpdate
- glossaryDelete
- glossaryCreateTerm
- glossaryReadTerm
- glossaryUpdateTerm
- glossaryDeleteTerm
- glossaryAssignTermToEntity
- glossaryRemoveTermFromEntity
- glossaryCreateCategory
- glossaryReadCategories

### Week 3: Unified Catalog (Your Differentiator)
Document key UC methods:
- get_governance_domains
- create_governance_domain
- get_uc_terms
- create_uc_term
- assign_scope_to_term
- list_assets_by_domain
- (Continue with most important UC operations)

## Tips for Efficient Documentation

1. **Use AI Assistance**
   - Copy the template
   - Ask GitHub Copilot: "Review this docstring and make it more specific based on the actual method implementation"
   - Copilot will see your code and suggest improvements

2. **Reuse Patterns**
   - Document one CRUD operation thoroughly
   - Use it as a template for similar operations
   - Adjust details but keep the structure

3. **Test Examples**
   - Always run your example code
   - Use actual data from your Purview instance
   - Include error handling

4. **Document as You Code**
   - When writing new methods, add docstrings immediately
   - When fixing bugs, improve docstrings
   - When someone asks "how do I...?", add that to use cases

## Measuring Progress

Run this to see your progress:
```bash
python scripts/document_client_apis.py
```

Check the report:
```bash
code doc/api-documentation-status.md
```

Current status:
- **Starting point:** 1.8% (11/624 methods)
- **With templates:** 231 templates ready
- **Target:** 80%+ for high-priority modules

## Next Steps

1. ✅ **Templates Generated** - 231 docstrings ready
2. 📝 **Choose First Module** - Recommend: `_entity.py` or `api_client.py`
3. ⚡ **Document 5 Methods** - Start small, build momentum
4. 🔄 **Test & Refine** - Run examples, improve clarity
5. 📊 **Track Progress** - Re-run analysis after each batch
6. 🚀 **Expand MCP Server** - Expose documented methods as tools

## Questions?

- **Which module should I start with?** → Start with api_client.py (already 38% done)
- **How long does each method take?** → 10-20 minutes with template
- **Can I skip some sections?** → Args, Returns, Example are essential; others are nice-to-have
- **What if I'm not sure about details?** → Add `[TODO]` markers and come back later

---

**Ready to start? Let me know which module you'd like to document first!**
