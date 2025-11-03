"""
Script to analyze and document Purview CLI client APIs for MCP/LLM integration.

This script:
1. Scans all client modules in purviewcli/client/
2. Identifies public methods that need documentation
3. Generates documentation templates
4. Creates tracking report for documentation progress
"""

import os
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
import json


@dataclass
class MethodInfo:
    """Information about a client method"""
    name: str
    module: str
    class_name: str
    line_number: int
    signature: str
    current_docstring: str = ""
    has_comprehensive_docs: bool = False
    missing_sections: List[str] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)
    is_async: bool = False
    is_public: bool = True


@dataclass
class ModuleInfo:
    """Information about a client module"""
    name: str
    file_path: str
    classes: List[str] = field(default_factory=list)
    methods: List[MethodInfo] = field(default_factory=list)
    has_module_docstring: bool = False
    module_docstring: str = ""


class ClientAPIAnalyzer:
    """Analyzes Purview CLI client modules for documentation completeness"""
    
    def __init__(self, client_dir: str = "purviewcli/client"):
        self.client_dir = Path(client_dir)
        self.modules: Dict[str, ModuleInfo] = {}
        
    def analyze_all_modules(self) -> Dict[str, ModuleInfo]:
        """Analyze all client modules"""
        # Client modules to analyze
        client_files = [
            "_entity.py",
            "_glossary.py",
            "_collections.py",
            "_domain.py",
            "_lineage.py",
            "_scan.py",
            "_search.py",
            "_types.py",
            "_unified_catalog.py",
            "_workflow.py",
            "_relationship.py",
            "_policystore.py",
            "_management.py",
            "_account.py",
            "_health.py",
            "_insight.py",
            "_share.py",
            "api_client.py",
            "data_quality.py",
            "scanning_operations.py",
        ]
        
        for file_name in client_files:
            file_path = self.client_dir / file_name
            if file_path.exists():
                try:
                    module_info = self.analyze_module(str(file_path), file_name)
                    self.modules[file_name] = module_info
                    print(f"[OK] Analyzed {file_name}: {len(module_info.methods)} methods")
                except Exception as e:
                    print(f"[ERROR] Error analyzing {file_name}: {e}")
        
        return self.modules
    
    def analyze_module(self, file_path: str, module_name: str) -> ModuleInfo:
        """Analyze a single module"""
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        
        tree = ast.parse(source)
        module_info = ModuleInfo(
            name=module_name,
            file_path=file_path
        )
        
        # Get module docstring
        module_docstring = ast.get_docstring(tree)
        if module_docstring:
            module_info.has_module_docstring = True
            module_info.module_docstring = module_docstring
        
        # Find all classes and methods
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                module_info.classes.append(node.name)
                
                # Analyze methods in the class
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_info = self.analyze_method(item, module_name, node.name)
                        if method_info.is_public:
                            module_info.methods.append(method_info)
        
        return module_info
    
    def analyze_method(
        self, 
        node: ast.FunctionDef, 
        module_name: str, 
        class_name: str
    ) -> MethodInfo:
        """Analyze a single method"""
        method_info = MethodInfo(
            name=node.name,
            module=module_name,
            class_name=class_name,
            line_number=node.lineno,
            signature=self._get_signature(node),
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_public=not node.name.startswith('_')
        )
        
        # Get docstring
        docstring = ast.get_docstring(node)
        if docstring:
            method_info.current_docstring = docstring
            method_info.has_comprehensive_docs = self._check_comprehensive_docs(docstring)
            method_info.missing_sections = self._find_missing_sections(docstring)
        else:
            method_info.current_docstring = ""
            method_info.has_comprehensive_docs = False
            method_info.missing_sections = ["All sections missing"]
        
        # Get parameters
        for arg in node.args.args:
            if arg.arg != 'self':
                method_info.parameters.append(arg.arg)
        
        return method_info
    
    def _get_signature(self, node: ast.FunctionDef) -> str:
        """Get method signature as string"""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)
        
        # Add return type
        return_type = ""
        if node.returns:
            return_type = f" -> {ast.unparse(node.returns)}"
        
        async_prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
        return f"{async_prefix}def {node.name}({', '.join(args)}){return_type}"
    
    def _check_comprehensive_docs(self, docstring: str) -> bool:
        """Check if docstring has comprehensive documentation"""
        required_sections = ["Args:", "Returns:", "Example:"]
        has_all_sections = all(section in docstring for section in required_sections)
        has_sufficient_length = len(docstring) > 200  # Basic heuristic
        return has_all_sections and has_sufficient_length
    
    def _find_missing_sections(self, docstring: str) -> List[str]:
        """Find missing documentation sections"""
        sections = {
            "Args:": "Parameter documentation",
            "Returns:": "Return value documentation",
            "Raises:": "Exception documentation",
            "Example:": "Usage examples",
            "Use Cases:": "Use case documentation"
        }
        
        missing = []
        for section, description in sections.items():
            if section not in docstring:
                missing.append(description)
        
        return missing
    
    def generate_report(self, output_file: str = "doc/api-documentation-status.md"):
        """Generate documentation status report"""
        total_modules = len(self.modules)
        total_methods = sum(len(m.methods) for m in self.modules.values())
        documented_methods = sum(
            1 for m in self.modules.values() 
            for method in m.methods 
            if method.has_comprehensive_docs
        )
        
        coverage_pct = (documented_methods / total_methods * 100) if total_methods > 0 else 0
        
        report_lines = [
            "# Purview CLI API Documentation Status",
            "",
            f"**Generated:** {Path(output_file).absolute()}",
            "",
            "## Summary",
            "",
            f"- **Total Modules:** {total_modules}",
            f"- **Total Public Methods:** {total_methods}",
            f"- **Comprehensively Documented:** {documented_methods}",
            f"- **Documentation Coverage:** {coverage_pct:.1f}%",
            "",
            "## Documentation Progress",
            ""
        ]
        
        # Sort modules by documentation completion
        sorted_modules = sorted(
            self.modules.items(),
            key=lambda x: sum(1 for m in x[1].methods if m.has_comprehensive_docs) / len(x[1].methods) if x[1].methods else 0,
            reverse=True
        )
        
        for module_name, module_info in sorted_modules:
            if not module_info.methods:
                continue
                
            documented = sum(1 for m in module_info.methods if m.has_comprehensive_docs)
            total = len(module_info.methods)
            pct = (documented / total * 100) if total > 0 else 0
            
            status_emoji = "✅" if pct == 100 else "🔄" if pct > 0 else "❌"
            
            report_lines.extend([
                f"### {status_emoji} {module_name}",
                "",
                f"- **Progress:** {documented}/{total} methods ({pct:.0f}%)",
                f"- **Classes:** {', '.join(module_info.classes)}",
                f"- **Module Docstring:** {'[YES]' if module_info.has_module_docstring else '[NO]'}",
                ""
            ])
            
            # List undocumented methods
            undocumented = [m for m in module_info.methods if not m.has_comprehensive_docs]
            if undocumented:
                report_lines.append("**Methods Needing Documentation:**")
                report_lines.append("")
                for method in undocumented[:10]:  # Show first 10
                    missing = ", ".join(method.missing_sections)
                    report_lines.append(
                        f"- `{method.name}` (line {method.line_number}) - Missing: {missing}"
                    )
                if len(undocumented) > 10:
                    report_lines.append(f"- ... and {len(undocumented) - 10} more")
                report_lines.append("")
        
        # Priority recommendations
        report_lines.extend([
            "## Documentation Priorities",
            "",
            "### High Priority (Core MCP Operations)",
            "",
            "These modules are most likely to be used by LLMs via MCP:",
            ""
        ])
        
        high_priority = [
            "_entity.py",
            "_glossary.py", 
            "_collections.py",
            "_lineage.py",
            "_search.py",
            "_unified_catalog.py",
            "api_client.py"
        ]
        
        for module_name in high_priority:
            if module_name in self.modules:
                module_info = self.modules[module_name]
                documented = sum(1 for m in module_info.methods if m.has_comprehensive_docs)
                total = len(module_info.methods)
                pct = (documented / total * 100) if total > 0 else 0
                status = "✅ Complete" if pct == 100 else f"🔄 {pct:.0f}% complete"
                report_lines.append(f"- **{module_name}:** {status} ({documented}/{total} methods)")
        
        report_lines.extend([
            "",
            "### Medium Priority (Supporting Operations)",
            "",
            "These modules provide important supporting functionality:",
            ""
        ])
        
        medium_priority = [
            "_scan.py",
            "_types.py",
            "_relationship.py",
            "_workflow.py",
            "data_quality.py"
        ]
        
        for module_name in medium_priority:
            if module_name in self.modules:
                module_info = self.modules[module_name]
                documented = sum(1 for m in module_info.methods if m.has_comprehensive_docs)
                total = len(module_info.methods)
                pct = (documented / total * 100) if total > 0 else 0
                status = "✅ Complete" if pct == 100 else f"🔄 {pct:.0f}% complete"
                report_lines.append(f"- **{module_name}:** {status} ({documented}/{total} methods)")
        
        report_lines.extend([
            "",
            "## Next Steps",
            "",
            "1. **Document High Priority modules** (if not 100%)",
            "2. **Review and enhance** existing documentation",
            "3. **Add runnable examples** to all methods",
            "4. **Document use cases** for business context",
            "5. **Generate API reference** from docstrings",
            "",
            "## Documentation Guide",
            "",
            "Follow the comprehensive guide: [`doc/guides/api-documentation-guide.md`](guides/api-documentation-guide.md)",
            "",
            "## Tools",
            "",
            "- **Analyze:** `python scripts/document_client_apis.py analyze`",
            "- **Generate Report:** `python scripts/document_client_apis.py report`",
            "- **Create Templates:** `python scripts/document_client_apis.py template <module>`",
            ""
        ])
        
        # Write report
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"\n[OK] Report generated: {output_path}")
        print(f"     Coverage: {coverage_pct:.1f}% ({documented_methods}/{total_methods} methods)")
        
        return str(output_path)
    
    def generate_json_report(self, output_file: str = "doc/api-documentation-status.json"):
        """Generate JSON report for programmatic use"""
        data = {
            "summary": {
                "total_modules": len(self.modules),
                "total_methods": sum(len(m.methods) for m in self.modules.values()),
                "documented_methods": sum(
                    1 for m in self.modules.values() 
                    for method in m.methods 
                    if method.has_comprehensive_docs
                )
            },
            "modules": {}
        }
        
        for module_name, module_info in self.modules.items():
            data["modules"][module_name] = {
                "file_path": module_info.file_path,
                "classes": module_info.classes,
                "has_module_docstring": module_info.has_module_docstring,
                "methods": [
                    {
                        "name": m.name,
                        "line": m.line_number,
                        "signature": m.signature,
                        "has_docs": m.has_comprehensive_docs,
                        "missing": m.missing_sections,
                        "is_async": m.is_async
                    }
                    for m in module_info.methods
                ]
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"[OK] JSON report generated: {output_file}")


def main():
    """Main entry point"""
    import sys
    
    analyzer = ClientAPIAnalyzer()
    
    print("Analyzing Purview CLI client modules...")
    print("=" * 60)
    
    analyzer.analyze_all_modules()
    
    print("\nGenerating reports...")
    print("=" * 60)
    
    # Generate markdown report
    md_report = analyzer.generate_report()
    
    # Generate JSON report
    analyzer.generate_json_report()
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print(f"\nView report: {md_report}")
    print("\nNext steps:")
    print("1. Review high-priority modules")
    print("2. Follow doc/guides/api-documentation-guide.md")
    print("3. Document methods with comprehensive docstrings")


if __name__ == "__main__":
    main()
