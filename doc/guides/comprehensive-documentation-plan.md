# Comprehensive API Documentation Plan for Purview MCP Server

## Current Situation

You have a rich Purview CLI with **20 client modules** and **624 public methods**, but only **1.8% (11 methods)** have comprehensive documentation suitable for LLM/MCP integration.

### Your Client Architecture

```
purviewcli/client/
├── Core API Clients (High Priority for MCP)
│   ├── _entity.py           (51 methods) - Entity CRUD, bulk ops, classifications
│   ├── _glossary.py         (48 methods) - Terms, categories, assignments
│   ├── _collections.py      (27 methods) - Collection management, permissions
│   ├── _lineage.py          (23 methods) - Data lineage, upstream/downstream
│   ├── _search.py           (22 methods) - Entity search, filtering
│   ├── _unified_catalog.py  (60 methods) - UC domains, terms, scopes
│   └── api_client.py        (29 methods) - High-level async wrapper (11/29 documented)
│
├── Supporting Clients (Medium Priority)
│   ├── _scan.py             (39 methods) - Data source scanning
│   ├── _types.py            (42 methods) - Type definitions
│   ├── _relationship.py     (20 methods) - Entity relationships
│   ├── _workflow.py         (43 methods) - Workflow management
│   ├── data_quality.py      (6 methods) - Quality validation
│   └── scanning_operations.py (14 methods) - Scan operations
│
└── Administrative Clients (Lower Priority)
    ├── _account.py          (29 methods) - Account management
    ├── _management.py       (33 methods) - Admin operations
    ├── _policystore.py      (45 methods) - Policy management
    ├── _insight.py          (49 methods) - Analytics/insights
    ├── _health.py           (6 methods) - Health checks
    ├── _share.py            (31 methods) - Data sharing
    └── _domain.py           (7 methods) - Domain management
```

### Current MCP Server Coverage

Your `mcp/server/server.py` currently exposes **only 18 tools** from `api_client.py`:

**Currently Exposed:**
- Entity operations: get, create, update, delete, search (5 tools)
- Glossary: terms, create term, assign (3 tools)
- Collections: list, get (2 tools)
- Lineage: get, create (2 tools)
- CSV operations: import/export entities, terms (4 tools)
- Account: get info, list collections (2 tools)

**Not Exposed** (but available in specialized clients):
- Advanced entity operations (bulk, classifications, business metadata)
- Advanced glossary (categories, hierarchies, workflows)
- Scanning operations (data sources, scan rules)
- Type management (custom types, attributes)
- Relationships (advanced linking)
- Workflows (approval processes)
- Policy management (access policies)
- Data quality validation
- **60 Unified Catalog operations** (domains, terms, scopes, etc.)

## Recommended Approach

### Phase 1: Document High-Priority Clients (MCP-Ready)

Focus on the modules most likely to be used by LLMs via MCP:

#### Priority 1A: Core Operations (Already Partially Done)
- ✅ `api_client.py` - Continue documenting remaining 18 methods
- ⏭️ `_entity.py` - 51 methods for entity management
- ⏭️ `_glossary.py` - 48 methods for glossary operations

#### Priority 1B: Discovery & Governance
- ⏭️ `_search.py` - 22 methods for entity search
- ⏭️ `_collections.py` - 27 methods for collection management
- ⏭️ `_lineage.py` - 23 methods for lineage tracking

#### Priority 1C: Unified Catalog (Your Unique Feature)
- ⏭️ `_unified_catalog.py` - **60 methods** for UC domains, terms, scopes

**Estimated Effort:** ~171 methods × 15 minutes = **43 hours**

### Phase 2: Expand MCP Server with Specialized Tools

Once documentation is complete, expose specialized client methods as MCP tools:

#### Example: Advanced Entity Operations
```python
# In server.py - Add tools for bulk operations
Tool(
    name="entity_bulk_create",
    description="Create multiple entities in a single batch operation",
    inputSchema={...}
),
Tool(
    name="entity_add_classification", 
    description="Add classification tags to an entity (PII, Confidential, etc.)",
    inputSchema={...}
),
Tool(
    name="entity_set_business_metadata",
    description="Set custom business metadata attributes on an entity",
    inputSchema={...}
)
```

#### Example: Unified Catalog Operations
```python
# Expose UC domain operations
Tool(
    name="uc_create_domain",
    description="Create a new governance domain in Unified Catalog",
    inputSchema={...}
),
Tool(
    name="uc_list_terms_by_domain",
    description="Get all terms within a specific UC domain",
    inputSchema={...}
),
Tool(
    name="uc_assign_scope_to_term",
    description="Define business metadata scope for UC term",
    inputSchema={...}
)
```

### Phase 3: Document Supporting Clients

Once core operations are documented and working well in MCP:

- `_scan.py` - Scanning operations
- `_types.py` - Type management
- `_relationship.py` - Relationship operations
- `data_quality.py` - Quality validation

**Estimated Effort:** ~125 methods × 10 minutes = **21 hours**

### Phase 4: Administrative Clients (Optional)

Document administrative modules if needed for LLM use:

- `_account.py`, `_management.py`, `_policystore.py`, etc.

**Estimated Effort:** ~195 methods × 10 minutes = **33 hours**

## Tools & Workflow

### 1. Analysis Tool (✅ Complete)

```bash
# Analyze all client modules
python scripts/document_client_apis.py

# Generates:
# - doc/api-documentation-status.md (progress report)
# - doc/api-documentation-status.json (programmatic data)
```

### 2. Documentation Guide (✅ Complete)

Comprehensive guide with examples and best practices:
```
doc/guides/api-documentation-guide.md
```

### 3. Incremental Documentation Workflow

**For each client module:**

1. **Analyze current state**
   ```bash
   python scripts/document_client_apis.py
   # Check doc/api-documentation-status.md for module progress
   ```

2. **Document methods following the guide**
   - Open the client file (e.g., `purviewcli/client/_entity.py`)
   - For each public method, add comprehensive docstring:
     - Description
     - Args (with types, constraints, examples)
     - Returns (with structure details)
     - Raises (all possible exceptions)
     - Example (runnable code)
     - Use Cases (business context)

3. **Test examples**
   ```bash
   # Verify examples work
   python -m doctest purviewcli/client/_entity.py -v
   ```

4. **Re-run analysis**
   ```bash
   python scripts/document_client_apis.py
   # Verify improved coverage percentage
   ```

5. **Commit progress**
   ```bash
   git add purviewcli/client/_entity.py
   git commit -m "docs: Document _entity.py methods (20/51 complete)"
   ```

### 4. Parallel Strategy (Recommended)

Given the scale (624 methods), consider parallel documentation:

**Option A: AI-Assisted Documentation**
- Use GitHub Copilot to generate initial docstrings
- Review and refine for accuracy
- Add realistic examples from actual API usage

**Option B: Template-Based Approach**
- Create docstring templates for common patterns (CRUD, list, search)
- Fill in method-specific details
- Faster for similar methods

**Option C: Incremental + Selective**
- **Week 1:** Document api_client.py remaining methods (18 left)
- **Week 2:** Document _entity.py core methods (15 most-used)
- **Week 3:** Document _glossary.py core methods (12 most-used)
- **Week 4:** Document _unified_catalog.py (20 most-used)
- Continue incrementally based on MCP usage patterns

## MCP Server Enhancement Plan

### Current Server Architecture

```python
# mcp/server/server.py
class PurviewMCPServer:
    def __init__(self):
        self.client: Optional[PurviewClient] = None  # Only uses api_client.py
    
    async def list_tools(self):
        # Returns 18 tools from api_client.py methods
        return [Tool(...), Tool(...), ...]
    
    async def _execute_tool(self, tool_name, arguments):
        # Routes to self.client.method_name(...)
        # Limited to api_client.py methods only
```

### Enhanced Architecture (Proposal)

```python
# mcp/server/server.py - Enhanced version
class PurviewMCPServer:
    def __init__(self):
        self.api_client: Optional[PurviewClient] = None
        
        # Add specialized clients
        self.entity_client: Optional[Entity] = None
        self.glossary_client: Optional[Glossary] = None
        self.uc_client: Optional[UnifiedCatalogClient] = None
        self.lineage_client: Optional[Lineage] = None
        # ... more as needed
    
    async def _ensure_clients(self):
        """Initialize all specialized clients"""
        if not self.api_client:
            config = PurviewConfig(...)
            self.api_client = PurviewClient(config)
            
            # Initialize specialized clients
            from purviewcli.client._entity import Entity
            from purviewcli.client._glossary import Glossary
            from purviewcli.client._unified_catalog import UnifiedCatalogClient
            
            self.entity_client = Entity()
            self.glossary_client = Glossary()
            self.uc_client = UnifiedCatalogClient()
            # ... more as needed
    
    async def list_tools(self):
        """Expose 100+ tools from specialized clients"""
        tools = []
        
        # Core entity operations (from api_client)
        tools.extend(self._get_api_client_tools())
        
        # Advanced entity operations (from _entity)
        tools.extend(self._get_entity_client_tools())
        
        # Glossary operations (from _glossary)
        tools.extend(self._get_glossary_client_tools())
        
        # Unified Catalog operations (from _unified_catalog)
        tools.extend(self._get_uc_client_tools())
        
        # ... more categories
        
        return tools
    
    def _get_entity_client_tools(self):
        """Entity-specific tools"""
        return [
            Tool(
                name="entity_bulk_create",
                description="Create multiple entities in batch",
                inputSchema={...}
            ),
            Tool(
                name="entity_add_classification",
                description="Add classification tag to entity",
                inputSchema={...}
            ),
            # ... 50 more entity operations
        ]
    
    def _get_uc_client_tools(self):
        """Unified Catalog tools"""
        return [
            Tool(
                name="uc_create_domain",
                description="Create UC governance domain",
                inputSchema={...}
            ),
            Tool(
                name="uc_list_terms",
                description="List all UC terms",
                inputSchema={...}
            ),
            # ... 60 UC operations
        ]
    
    async def _execute_tool(self, tool_name, arguments):
        """Route to appropriate specialized client"""
        # Entity operations
        if tool_name.startswith("entity_"):
            method_name = tool_name.replace("entity_", "entity")
            return await getattr(self.entity_client, method_name)(arguments)
        
        # Glossary operations
        elif tool_name.startswith("glossary_"):
            method_name = tool_name.replace("glossary_", "glossary")
            return await getattr(self.glossary_client, method_name)(arguments)
        
        # UC operations
        elif tool_name.startswith("uc_"):
            method_name = tool_name.replace("uc_", "")
            return await getattr(self.uc_client, method_name)(arguments)
        
        # ... more routing
```

## Success Metrics

### Documentation Metrics
- **Target Coverage:** 80%+ for high-priority modules
- **Quality Indicators:**
  - All methods have Args, Returns, Example sections
  - Examples are runnable and realistic
  - Use cases explain business context
  - Error conditions documented

### MCP Integration Metrics
- **Tool Count:** Expand from 18 to 100+ tools
- **Usage Patterns:** Track which tools LLMs use most via logs
- **Success Rate:** % of tool calls that succeed vs. fail
- **Response Quality:** LLM's ability to chain operations correctly

## Quick Start: Document First Module

### Step 1: Start with api_client.py (Already 38% done)

Document the remaining 18 methods:

```bash
# Open the file
code purviewcli/client/api_client.py

# Focus on these methods (from status report):
# - batch_create_entities (line 278)
# - batch_update_entities (line 304)
# - import_entities_from_csv (line 331)
# - export_entities_to_csv (line 343)
# - get_asset_distribution (line 519)
# ... and 13 more
```

### Step 2: Apply Documentation Pattern

For each method, add comprehensive docstring:

```python
async def batch_create_entities(
    self, 
    entities: List[Dict[str, Any]],
    progress_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Create multiple entities in a single batch operation.
    
    Efficiently creates many entities at once with rate limiting and error handling.
    Use this instead of multiple create_entity calls for bulk imports.
    
    Args:
        entities: List of entity definition dictionaries. Each must contain:
                 - typeName (str): Entity type (e.g., "DataSet", "azure_sql_table")
                 - attributes (dict): Entity attributes including qualifiedName
                 Maximum: 1000 entities per batch
                 
        progress_callback: Optional callback function for progress tracking.
                          Called with (completed, total, current_entity) after each entity.
                          Example: lambda done, total, entity: print(f"{done}/{total}")
                          
    Returns:
        Dictionary with batch operation results:
            {
                "created": int,           # Successfully created count
                "failed": int,            # Failed creation count
                "entities": [             # Created entity details
                    {
                        "guid": str,      # New entity GUID
                        "typeName": str,  # Entity type
                        "qualifiedName": str  # Entity qualified name
                    }
                ],
                "errors": [               # Errors for failed entities
                    {
                        "entity": dict,   # Original entity definition
                        "error": str      # Error message
                    }
                ]
            }
            
    Raises:
        ValueError: When entities list is empty or exceeds 1000 items
        AuthenticationError: When Azure credentials are invalid
        HTTPError: When Purview API returns 4xx/5xx errors
        
    Example:
        # Create multiple datasets
        entities = [
            {
                "typeName": "DataSet",
                "attributes": {
                    "qualifiedName": "sales_2023@example",
                    "name": "Sales 2023",
                    "owner": "data-team@example.com"
                }
            },
            {
                "typeName": "DataSet",
                "attributes": {
                    "qualifiedName": "customers@example",
                    "name": "Customer Master",
                    "owner": "data-team@example.com"
                }
            }
        ]
        
        # With progress callback
        def show_progress(done, total, entity):
            print(f"Created {done}/{total}: {entity['attributes']['name']}")
        
        result = await client.batch_create_entities(
            entities,
            progress_callback=show_progress
        )
        
        print(f"Success: {result['created']}, Failed: {result['failed']}")
        
        # Handle errors
        for error in result.get('errors', []):
            print(f"Failed entity: {error['entity']['attributes']['qualifiedName']}")
            print(f"Error: {error['error']}")
            
    Use Cases:
        - Data Migration: Import existing catalog from other systems
        - Bulk Onboarding: Register many data sources at once
        - Testing: Create test datasets for development/QA
        - Automation: Populate catalog from infrastructure-as-code
    """
    # Implementation...
```

### Step 3: Verify and Commit

```bash
# Re-run analysis
python scripts/document_client_apis.py

# Should show improved coverage for api_client.py
# Example: "Progress: 19/29 methods (66%)"

# Commit progress
git add purviewcli/client/api_client.py
git commit -m "docs: Document batch operations in api_client.py"
```

## Timeline Estimate

### Aggressive Schedule (Full-Time Documentation)
- **Week 1:** api_client.py (remaining 18 methods) + _entity.py (51 methods)
- **Week 2:** _glossary.py (48 methods) + _collections.py (27 methods)
- **Week 3:** _unified_catalog.py (60 methods)
- **Week 4:** _lineage.py (23 methods) + _search.py (22 methods)
- **Week 5:** Enhance MCP server with new tools
- **Week 6:** Testing and refinement

### Incremental Schedule (Part-Time, 2-3 hours/day)
- **Month 1:** High-priority clients (api_client, _entity, _glossary)
- **Month 2:** Discovery clients (_search, _collections, _lineage)
- **Month 3:** Unified Catalog (_unified_catalog)
- **Month 4:** MCP server enhancement and testing

### Pragmatic Schedule (Focus on MCP Usage)
- **Week 1:** Document top 20 most-used methods across all clients
- **Week 2:** Expose as MCP tools, test with LLM
- **Week 3:** Based on usage patterns, document next 20 methods
- **Week 4:** Iterate - document what LLMs actually use

## Next Steps

### Immediate Actions (Today)

1. ✅ **Analysis Complete** - You now know the scope (624 methods, 1.8% done)
2. ✅ **Documentation Guide Created** - `doc/guides/api-documentation-guide.md`
3. ✅ **Tracking System Ready** - `scripts/document_client_apis.py`

### Tomorrow

4. **Choose Your Approach:**
   - Option A: Complete api_client.py (finish remaining 18 methods)
   - Option B: Start with most-used methods across clients
   - Option C: Focus on Unified Catalog (your unique feature)

5. **Document First 5 Methods** - Following the guide, add comprehensive docstrings

6. **Re-run Analysis** - See progress improve

### This Week

7. **Complete One High-Priority Client** - e.g., api_client.py or _entity.py
8. **Test with MCP** - Verify documented methods work well with LLM
9. **Refine Process** - Adjust based on what works best

### This Month

10. **Document High-Priority Clients** - Entity, Glossary, UC
11. **Enhance MCP Server** - Expose specialized client methods as tools
12. **Measure LLM Usage** - Track which operations LLMs use most

## Questions to Consider

1. **Which operations do YOU use most?** - Prioritize documenting those first
2. **What's your unique value?** - UC operations? Focus there
3. **Time availability?** - Aggressive vs. incremental schedule
4. **AI assistance?** - Use Copilot to speed up initial docstring generation
5. **MCP expansion?** - When to add specialized client tools to server?

## Conclusion

You have a **powerful, comprehensive Purview CLI** with 624 methods across 20 specialized clients. Currently, only the high-level `api_client.py` wrapper is exposed to LLMs via MCP, and even that is only 38% documented.

**The opportunity is huge**: With proper documentation and MCP expansion, you could expose 100+ specialized Purview operations to LLMs, enabling sophisticated data governance workflows through natural language.

**Start small, iterate fast**: Document the most-used operations first, test with LLMs, and let actual usage patterns guide further documentation priorities.

---

**Ready to start? Pick a module and let's document it together!** 🚀
