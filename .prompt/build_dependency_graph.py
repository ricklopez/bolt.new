#!/usr/bin/env python3
"""
Dependency Graph Builder for bolt.new repository

Scans all source files and extracts:
- imports
- exports
- class references
- identifier references
- inheritance
- relationships

Outputs to: .prompt/dependency-graph.json
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from collections import defaultdict


class DependencyGraphBuilder:
    """Builds a dependency graph from source code files"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.graph = {
            "metadata": {
                "repository": "bolt.new",
                "timestamp": None,
                "total_files": 0,
                "file_types": {}
            },
            "files": {}
        }

        # Track statistics
        self.stats = defaultdict(int)

        # File extensions to process
        self.extensions = {
            '.ts', '.tsx', '.js', '.jsx',  # TypeScript/JavaScript
            '.py',                           # Python
            '.cs',                           # C#
            '.go',                           # Go
            '.sql',                          # SQL
            '.yaml', '.yml',                 # YAML
            '.html', '.htm',                 # HTML
            '.json',                         # JSON
            '.css', '.scss',                 # CSS/SCSS
            '.md',                           # Markdown
            '.toml',                         # TOML
            '.sh',                           # Shell
        }

        # Directories to skip
        self.skip_dirs = {
            'node_modules', '.git', 'dist', 'build', '.cache',
            '__pycache__', '.next', '.vite', 'coverage'
        }

    def build(self):
        """Build the complete dependency graph"""
        print("🔍 Scanning repository...")

        # Scan all files
        for file_path in self.root_path.rglob('*'):
            if not file_path.is_file():
                continue

            # Skip ignored directories
            if any(skip in file_path.parts for skip in self.skip_dirs):
                continue

            # Check if extension is supported
            if file_path.suffix not in self.extensions:
                continue

            relative_path = str(file_path.relative_to(self.root_path))

            try:
                self.process_file(file_path, relative_path)
            except Exception as e:
                print(f"⚠️  Error processing {relative_path}: {e}")

        # Update metadata
        import datetime
        self.graph["metadata"]["timestamp"] = datetime.datetime.now().isoformat()
        self.graph["metadata"]["total_files"] = len(self.graph["files"])
        self.graph["metadata"]["file_types"] = dict(self.stats)

        print(f"\n✅ Processed {len(self.graph['files'])} files")
        print(f"📊 File types: {dict(self.stats)}")

    def process_file(self, file_path: Path, relative_path: str):
        """Process a single file and extract dependencies"""
        ext = file_path.suffix
        self.stats[ext] += 1

        # Initialize file entry
        file_entry = {
            "path": relative_path,
            "type": ext[1:],  # Remove leading dot
            "imports": [],
            "exports": [],
            "classes": [],
            "functions": [],
            "interfaces": [],
            "types": [],
            "dependencies": [],
            "dependents": [],
            "identifiers": [],
            "inheritance": []
        }

        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Binary file, skip
            return

        # Process based on file type
        if ext in {'.ts', '.tsx', '.js', '.jsx'}:
            self.process_typescript(content, file_entry)
        elif ext == '.py':
            self.process_python(content, file_entry)
        elif ext == '.cs':
            self.process_csharp(content, file_entry)
        elif ext == '.go':
            self.process_go(content, file_entry)
        elif ext == '.sql':
            self.process_sql(content, file_entry)
        elif ext in {'.yaml', '.yml'}:
            self.process_yaml(content, file_entry)
        elif ext in {'.html', '.htm'}:
            self.process_html(content, file_entry)
        elif ext in {'.css', '.scss'}:
            self.process_css(content, file_entry)

        self.graph["files"][relative_path] = file_entry

    def process_typescript(self, content: str, file_entry: Dict):
        """Process TypeScript/JavaScript files"""

        # Extract imports
        # import { foo } from './bar'
        # import foo from './bar'
        # import * as foo from './bar'
        # import './bar'
        import_patterns = [
            r"import\s+(?:type\s+)?{([^}]+)}\s+from\s+['\"]([^'\"]+)['\"]",
            r"import\s+(?:type\s+)?(\w+)\s+from\s+['\"]([^'\"]+)['\"]",
            r"import\s+\*\s+as\s+(\w+)\s+from\s+['\"]([^'\"]+)['\"]",
            r"import\s+['\"]([^'\"]+)['\"]",
        ]

        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                groups = match.groups()
                if len(groups) == 2:
                    imported, source = groups
                    file_entry["imports"].append({
                        "source": source,
                        "imported": imported.strip() if imported else "*"
                    })
                    if not source.startswith('.') and not source.startswith('@'):
                        continue
                    file_entry["dependencies"].append(source)
                elif len(groups) == 1:
                    source = groups[0]
                    file_entry["imports"].append({
                        "source": source,
                        "imported": "*"
                    })
                    if not source.startswith('.') and not source.startswith('@'):
                        continue
                    file_entry["dependencies"].append(source)

        # Extract exports
        # export { foo }
        # export const foo = ...
        # export function foo() {}
        # export class Foo {}
        # export interface Foo {}
        # export type Foo = ...
        # export default ...
        export_patterns = [
            r"export\s+{([^}]+)}",
            r"export\s+const\s+(\w+)",
            r"export\s+let\s+(\w+)",
            r"export\s+var\s+(\w+)",
            r"export\s+function\s+(\w+)",
            r"export\s+class\s+(\w+)",
            r"export\s+interface\s+(\w+)",
            r"export\s+type\s+(\w+)",
            r"export\s+default\s+(?:class\s+)?(\w+)?",
        ]

        for pattern in export_patterns:
            for match in re.finditer(pattern, content):
                exported = match.group(1)
                if exported:
                    # Handle multiple exports in braces
                    if '{' in pattern:
                        exports = [e.strip() for e in exported.split(',')]
                        file_entry["exports"].extend(exports)
                    else:
                        file_entry["exports"].append(exported.strip())

        # Extract classes
        class_pattern = r"class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?"
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            extends = match.group(2)
            implements = match.group(3)

            class_info = {"name": class_name}
            if extends:
                class_info["extends"] = extends
                file_entry["inheritance"].append({
                    "class": class_name,
                    "extends": extends
                })
            if implements:
                class_info["implements"] = [i.strip() for i in implements.split(',')]

            file_entry["classes"].append(class_info)
            file_entry["identifiers"].append(class_name)

        # Extract functions
        function_patterns = [
            r"function\s+(\w+)\s*\(",
            r"const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[\w]+)\s*=>",
            r"let\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[\w]+)\s*=>",
        ]

        for pattern in function_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                if func_name and not func_name.startswith('_'):
                    file_entry["functions"].append(func_name)
                    file_entry["identifiers"].append(func_name)

        # Extract interfaces
        interface_pattern = r"interface\s+(\w+)(?:\s+extends\s+([\w,\s]+))?"
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            extends = match.group(2)

            interface_info = {"name": interface_name}
            if extends:
                interface_info["extends"] = [e.strip() for e in extends.split(',')]
                for ext in interface_info["extends"]:
                    file_entry["inheritance"].append({
                        "interface": interface_name,
                        "extends": ext
                    })

            file_entry["interfaces"].append(interface_info)
            file_entry["identifiers"].append(interface_name)

        # Extract type aliases
        type_pattern = r"type\s+(\w+)\s*="
        for match in re.finditer(type_pattern, content):
            type_name = match.group(1)
            file_entry["types"].append(type_name)
            file_entry["identifiers"].append(type_name)

        # Deduplicate
        file_entry["dependencies"] = list(set(file_entry["dependencies"]))
        file_entry["exports"] = list(set(file_entry["exports"]))
        file_entry["identifiers"] = list(set(file_entry["identifiers"]))

    def process_python(self, content: str, file_entry: Dict):
        """Process Python files using AST"""
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        # Extract imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    file_entry["imports"].append({
                        "source": alias.name,
                        "imported": alias.asname or alias.name
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    file_entry["imports"].append({
                        "source": module,
                        "imported": alias.name
                    })
                    if module.startswith('.'):
                        file_entry["dependencies"].append(module)

            # Extract classes
            elif isinstance(node, ast.ClassDef):
                class_info = {"name": node.name}
                if node.bases:
                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                            file_entry["inheritance"].append({
                                "class": node.name,
                                "extends": base.id
                            })
                    if bases:
                        class_info["extends"] = bases
                file_entry["classes"].append(class_info)
                file_entry["identifiers"].append(node.name)

            # Extract functions
            elif isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    file_entry["functions"].append(node.name)
                    file_entry["identifiers"].append(node.name)

        # Deduplicate
        file_entry["dependencies"] = list(set(file_entry["dependencies"]))
        file_entry["identifiers"] = list(set(file_entry["identifiers"]))

    def process_csharp(self, content: str, file_entry: Dict):
        """Process C# files"""

        # Extract using statements
        using_pattern = r"using\s+(?:static\s+)?([^;]+);"
        for match in re.finditer(using_pattern, content):
            namespace = match.group(1).strip()
            file_entry["imports"].append({
                "source": namespace,
                "imported": "*"
            })

        # Extract classes
        class_pattern = r"(?:public|private|protected|internal)?\s*(?:abstract|sealed)?\s*class\s+(\w+)(?:\s*:\s*([\w,\s]+))?"
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            inheritance = match.group(2)

            class_info = {"name": class_name}
            if inheritance:
                bases = [b.strip() for b in inheritance.split(',')]
                class_info["extends"] = bases
                for base in bases:
                    file_entry["inheritance"].append({
                        "class": class_name,
                        "extends": base
                    })

            file_entry["classes"].append(class_info)
            file_entry["identifiers"].append(class_name)

        # Extract interfaces
        interface_pattern = r"(?:public|private|protected|internal)?\s*interface\s+(\w+)(?:\s*:\s*([\w,\s]+))?"
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            inheritance = match.group(2)

            interface_info = {"name": interface_name}
            if inheritance:
                bases = [b.strip() for b in inheritance.split(',')]
                interface_info["extends"] = bases

            file_entry["interfaces"].append(interface_info)
            file_entry["identifiers"].append(interface_name)

    def process_go(self, content: str, file_entry: Dict):
        """Process Go files"""

        # Extract imports
        # Single import: import "fmt"
        # Multi import: import ( "fmt" "os" )
        single_import = r'import\s+"([^"]+)"'
        multi_import = r'import\s*\(\s*([^)]+)\s*\)'

        for match in re.finditer(single_import, content):
            file_entry["imports"].append({
                "source": match.group(1),
                "imported": "*"
            })

        for match in re.finditer(multi_import, content):
            imports = match.group(1)
            for line in imports.split('\n'):
                import_match = re.search(r'"([^"]+)"', line)
                if import_match:
                    file_entry["imports"].append({
                        "source": import_match.group(1),
                        "imported": "*"
                    })

        # Extract structs
        struct_pattern = r'type\s+(\w+)\s+struct\s*{'
        for match in re.finditer(struct_pattern, content):
            struct_name = match.group(1)
            file_entry["classes"].append({"name": struct_name})
            file_entry["identifiers"].append(struct_name)

        # Extract interfaces
        interface_pattern = r'type\s+(\w+)\s+interface\s*{'
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            file_entry["interfaces"].append({"name": interface_name})
            file_entry["identifiers"].append(interface_name)

        # Extract functions
        func_pattern = r'func\s+(?:\([^)]+\)\s+)?(\w+)\s*\('
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            file_entry["functions"].append(func_name)
            file_entry["identifiers"].append(func_name)

    def process_sql(self, content: str, file_entry: Dict):
        """Process SQL files"""

        # Extract table references
        create_table = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)'
        for match in re.finditer(create_table, content, re.IGNORECASE):
            table_name = match.group(1).strip('`"\'')
            file_entry["identifiers"].append(table_name)

        # Extract view references
        create_view = r'CREATE\s+VIEW\s+([^\s(]+)'
        for match in re.finditer(create_view, content, re.IGNORECASE):
            view_name = match.group(1).strip('`"\'')
            file_entry["identifiers"].append(view_name)

    def process_yaml(self, content: str, file_entry: Dict):
        """Process YAML files"""
        # YAML is configuration - extract key references
        try:
            import yaml
            data = yaml.safe_load(content)
            if isinstance(data, dict):
                file_entry["identifiers"] = list(data.keys())
        except:
            # Fallback to simple key extraction
            key_pattern = r'^(\w+):'
            for match in re.finditer(key_pattern, content, re.MULTILINE):
                file_entry["identifiers"].append(match.group(1))

    def process_html(self, content: str, file_entry: Dict):
        """Process HTML files"""

        # Extract script src
        script_pattern = r'<script[^>]+src=["\']([^"\']+)["\']'
        for match in re.finditer(script_pattern, content):
            src = match.group(1)
            file_entry["dependencies"].append(src)

        # Extract link href (CSS)
        link_pattern = r'<link[^>]+href=["\']([^"\']+)["\']'
        for match in re.finditer(link_pattern, content):
            href = match.group(1)
            if href.endswith('.css') or href.endswith('.scss'):
                file_entry["dependencies"].append(href)

    def process_css(self, content: str, file_entry: Dict):
        """Process CSS/SCSS files"""

        # Extract @import statements
        import_pattern = r'@import\s+["\']([^"\']+)["\']'
        for match in re.finditer(import_pattern, content):
            imported = match.group(1)
            file_entry["imports"].append({
                "source": imported,
                "imported": "*"
            })
            file_entry["dependencies"].append(imported)

        # Extract class names
        class_pattern = r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)\s*{'
        for match in re.finditer(class_pattern, content):
            class_name = match.group(1)
            file_entry["identifiers"].append(class_name)

        # Deduplicate
        file_entry["identifiers"] = list(set(file_entry["identifiers"]))

    def resolve_dependencies(self):
        """Resolve dependencies and build reverse dependency graph"""
        print("\n🔗 Resolving dependencies...")

        # Build a map of possible file paths
        file_paths = set(self.graph["files"].keys())

        for file_path, file_entry in self.graph["files"].items():
            resolved_deps = []

            for dep in file_entry["dependencies"]:
                # Try to resolve relative imports
                if dep.startswith('.'):
                    base_dir = str(Path(file_path).parent)

                    # Possible extensions
                    possible_exts = ['', '.ts', '.tsx', '.js', '.jsx', '.py', '.css', '.scss']

                    # Resolve path
                    if base_dir:
                        resolved = str(Path(base_dir) / dep)
                    else:
                        resolved = dep[2:] if dep.startswith('./') else dep[3:]

                    # Try different extensions
                    for ext in possible_exts:
                        test_path = resolved + ext
                        if test_path in file_paths:
                            resolved_deps.append(test_path)
                            # Add to dependents
                            if test_path in self.graph["files"]:
                                if file_path not in self.graph["files"][test_path]["dependents"]:
                                    self.graph["files"][test_path]["dependents"].append(file_path)
                            break

                        # Try index files
                        index_path = str(Path(resolved) / ('index' + ext))
                        if index_path in file_paths:
                            resolved_deps.append(index_path)
                            if index_path in self.graph["files"]:
                                if file_path not in self.graph["files"][index_path]["dependents"]:
                                    self.graph["files"][index_path]["dependents"].append(file_path)
                            break

            file_entry["dependencies"] = resolved_deps

    def save(self, output_path: str):
        """Save the dependency graph to JSON"""
        print(f"\n💾 Writing dependency graph to {output_path}...")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.graph, f, indent=2)

        # Print statistics
        total_imports = sum(len(f["imports"]) for f in self.graph["files"].values())
        total_exports = sum(len(f["exports"]) for f in self.graph["files"].values())
        total_classes = sum(len(f["classes"]) for f in self.graph["files"].values())
        total_functions = sum(len(f["functions"]) for f in self.graph["files"].values())
        total_interfaces = sum(len(f["interfaces"]) for f in self.graph["files"].values())

        print(f"\n📊 Statistics:")
        print(f"   Total files: {self.graph['metadata']['total_files']}")
        print(f"   Total imports: {total_imports}")
        print(f"   Total exports: {total_exports}")
        print(f"   Total classes: {total_classes}")
        print(f"   Total functions: {total_functions}")
        print(f"   Total interfaces: {total_interfaces}")
        print(f"\n✅ Dependency graph successfully generated!")


def main():
    """Main entry point"""
    print("=" * 60)
    print("  Dependency Graph Builder for bolt.new")
    print("=" * 60)

    # Determine repository root (parent of .prompt directory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    print(f"\n📁 Repository root: {repo_root}")

    # Build dependency graph
    builder = DependencyGraphBuilder(str(repo_root))
    builder.build()
    builder.resolve_dependencies()

    # Save to output
    output_path = script_dir / "dependency-graph.json"
    builder.save(str(output_path))


if __name__ == "__main__":
    main()
