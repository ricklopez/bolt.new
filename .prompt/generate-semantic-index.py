#!/usr/bin/env python3
"""
Semantic Index Generator for DotPrompt Workspace

Loads all IR files and generates:
- Summaries and file index
- Domain clusters
- Dependency cycles
- System architecture map
- Priority groups
- Migration grouping
- Database schema candidates

Output: .prompt/semantic-index.md
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict


class SemanticIndexGenerator:
    """Generates semantic index from IR files and dependency graph"""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.prompt_path = self.root_path / ".prompt"
        self.ir_path = self.prompt_path / "ir"
        self.dep_graph_path = self.prompt_path / "dependency-graph.json"

        # Data structures
        self.ir_files = {}
        self.dependency_graph = None
        self.domain_clusters = defaultdict(list)
        self.priority_groups = defaultdict(list)
        self.database_schemas = []
        self.dependency_cycles = []
        self.architecture_map = {
            "backend": defaultdict(list),
            "frontend": defaultdict(list),
            "shared": defaultdict(list),
            "database": []
        }

    def load_dependency_graph(self):
        """Load the dependency graph JSON"""
        if not self.dep_graph_path.exists():
            print(f"⚠️  Dependency graph not found at {self.dep_graph_path}")
            print("   Run: python3 .prompt/build_dependency_graph.py")
            return False

        with open(self.dep_graph_path, 'r', encoding='utf-8') as f:
            self.dependency_graph = json.load(f)

        print(f"✅ Loaded dependency graph: {len(self.dependency_graph['files'])} files")
        return True

    def load_ir_files(self):
        """Load all IR markdown files"""
        if not self.ir_path.exists():
            print(f"⚠️  IR directory not found: {self.ir_path}")
            print("   No IR files to process yet.")
            return 0

        count = 0
        for ir_file in self.ir_path.rglob("*.md"):
            relative_path = str(ir_file.relative_to(self.ir_path))

            try:
                with open(ir_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.ir_files[relative_path] = self.parse_ir_file(content, relative_path)
                    count += 1
            except Exception as e:
                print(f"⚠️  Error loading {relative_path}: {e}")

        print(f"✅ Loaded {count} IR files")
        return count

    def parse_ir_file(self, content: str, path: str) -> Dict:
        """Parse an IR file into structured data"""
        ir_data = {
            "path": path,
            "source_file": "",
            "purpose": "",
            "domain_role": "",
            "tags": [],
            "classes": [],
            "functions": [],
            "interfaces": [],
            "dependencies": [],
            "migration_target": {},
            "database_tables": [],
            "priority": "normal"
        }

        # Extract source file path
        file_match = re.search(r'^File:\s*(.+)$', content, re.MULTILINE)
        if file_match:
            ir_data["source_file"] = file_match.group(1).strip()

        # Extract sections
        ir_data["purpose"] = self.extract_section(content, r'##\s*1\.\s*Purpose')
        ir_data["domain_role"] = self.extract_section(content, r'##\s*2\.\s*Domain Role')

        # Extract tags (section 14)
        tags_section = self.extract_section(content, r'##\s*14\.\s*Tags')
        if tags_section:
            tag_pattern = r'[-*]\s*`([^`]+)`'
            ir_data["tags"] = re.findall(tag_pattern, tags_section)

        # Extract classes from section 3
        classes_section = self.extract_section(content, r'##\s*3\.\s*Public API')
        if classes_section:
            class_pattern = r'class\s+(\w+)'
            ir_data["classes"] = re.findall(class_pattern, classes_section)

        # Extract dependencies from section 13
        deps_section = self.extract_section(content, r'##\s*13\.\s*Dependencies')
        if deps_section:
            # Extract dependsOn list
            depends_match = re.search(r'###\s*dependsOn\s*\n(.*?)(?=###|##|$)', deps_section, re.DOTALL)
            if depends_match:
                dep_lines = depends_match.group(1)
                dep_pattern = r'[-*]\s*(.+?)(?:\n|$)'
                ir_data["dependencies"] = [d.strip() for d in re.findall(dep_pattern, dep_lines)]

        # Extract migration target from section 11
        migration_section = self.extract_section(content, r'##\s*11\.\s*Migration Mapping')
        if migration_section:
            ir_data["migration_target"] = self.parse_migration_mapping(migration_section)

        # Extract database info from section 7
        db_section = self.extract_section(content, r'##\s*7\.\s*Database Interaction')
        if db_section:
            ir_data["database_tables"] = self.extract_database_tables(db_section)

        # Determine priority from tags
        if 'migration-critical' in ir_data["tags"]:
            ir_data["priority"] = "critical"
        elif 'domain-model' in ir_data["tags"] or 'business-logic' in ir_data["tags"]:
            ir_data["priority"] = "high"

        return ir_data

    def extract_section(self, content: str, section_header: str) -> str:
        """Extract content between section headers"""
        pattern = f'{section_header}(.*?)(?=##|$)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def parse_migration_mapping(self, section: str) -> Dict:
        """Parse migration mapping section"""
        mapping = {
            "backend": [],
            "frontend": [],
            "database": [],
            "shared": []
        }

        # Extract subsections
        for category in ["backend", "frontend", "database", "shared"]:
            pattern = f'###\s*{category.title()}[:\s]+(.*?)(?=###|##|$)'
            match = re.search(pattern, section, re.DOTALL | re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Extract bullet points
                items = re.findall(r'[-*]\s*(.+?)(?:\n|$)', content)
                mapping[category] = [item.strip() for item in items]

        return mapping

    def extract_database_tables(self, section: str) -> List[str]:
        """Extract table names from database section"""
        tables = []

        # Look for table mentions
        patterns = [
            r'table[s]?:\s*([^\n]+)',
            r'affected table[s]?:\s*([^\n]+)',
            r'`(\w+)`\s+table',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, section, re.IGNORECASE)
            for match in matches:
                # Split by commas or 'and'
                table_names = re.split(r'[,&]|\band\b', match)
                tables.extend([t.strip().strip('`"\'') for t in table_names if t.strip()])

        return list(set(tables))

    def analyze_domain_clusters(self):
        """Group files by domain using tags"""
        print("\n🔍 Analyzing domain clusters...")

        # Cluster by tags
        for ir_path, ir_data in self.ir_files.items():
            for tag in ir_data["tags"]:
                self.domain_clusters[tag].append(ir_data["source_file"] or ir_path)

        # If no IR files, cluster by directory structure from dependency graph
        if not self.ir_files and self.dependency_graph:
            for file_path in self.dependency_graph["files"].keys():
                parts = Path(file_path).parts
                if len(parts) > 1:
                    domain = parts[0] if parts[0] != 'app' else (parts[1] if len(parts) > 1 else parts[0])
                    self.domain_clusters[domain].append(file_path)

        print(f"   Found {len(self.domain_clusters)} domain clusters")

    def detect_dependency_cycles(self):
        """Detect circular dependencies"""
        print("\n🔍 Detecting dependency cycles...")

        if not self.dependency_graph:
            return

        files = self.dependency_graph["files"]

        def find_cycles(node: str, visited: Set[str], rec_stack: Set[str], path: List[str]) -> List[List[str]]:
            """DFS to find cycles"""
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            cycles = []

            if node in files:
                for dep in files[node].get("dependencies", []):
                    if dep not in visited:
                        cycles.extend(find_cycles(dep, visited, rec_stack, path[:]))
                    elif dep in rec_stack:
                        # Found a cycle
                        cycle_start = path.index(dep)
                        cycle = path[cycle_start:] + [dep]
                        cycles.append(cycle)

            rec_stack.remove(node)
            return cycles

        visited = set()
        all_cycles = []

        for file_path in files.keys():
            if file_path not in visited:
                cycles = find_cycles(file_path, visited, set(), [])
                all_cycles.extend(cycles)

        # Deduplicate cycles
        unique_cycles = []
        seen = set()
        for cycle in all_cycles:
            cycle_key = tuple(sorted(cycle))
            if cycle_key not in seen:
                seen.add(cycle_key)
                unique_cycles.append(cycle)

        self.dependency_cycles = unique_cycles[:20]  # Limit to top 20
        print(f"   Found {len(unique_cycles)} dependency cycles")

    def map_architecture(self):
        """Map system architecture from IR files and dependency graph"""
        print("\n🔍 Mapping system architecture...")

        # From IR files
        for ir_path, ir_data in self.ir_files.items():
            source = ir_data["source_file"] or ir_path
            migration = ir_data["migration_target"]

            if migration.get("backend"):
                for item in migration["backend"]:
                    self.architecture_map["backend"]["services"].append({"file": source, "target": item})

            if migration.get("frontend"):
                for item in migration["frontend"]:
                    self.architecture_map["frontend"]["components"].append({"file": source, "target": item})

            if migration.get("shared"):
                for item in migration["shared"]:
                    self.architecture_map["shared"]["utilities"].append({"file": source, "target": item})

            if ir_data["database_tables"]:
                for table in ir_data["database_tables"]:
                    self.database_schemas.append({"file": source, "table": table})

        # From dependency graph - classify by directory
        if self.dependency_graph:
            for file_path, file_data in self.dependency_graph["files"].items():
                if file_path.startswith("app/lib/.server"):
                    self.architecture_map["backend"]["server-side"].append(file_path)
                elif file_path.startswith("app/components"):
                    self.architecture_map["frontend"]["ui-components"].append(file_path)
                elif file_path.startswith("app/lib/stores"):
                    self.architecture_map["shared"]["state-management"].append(file_path)
                elif file_path.startswith("app/routes"):
                    if ".server" in file_path or "api." in file_path:
                        self.architecture_map["backend"]["api-routes"].append(file_path)
                    else:
                        self.architecture_map["frontend"]["pages"].append(file_path)

        print(f"   Mapped architecture across backend/frontend/shared")

    def compute_priority_groups(self):
        """Compute priority groups for migration"""
        print("\n🔍 Computing priority groups...")

        # From IR files
        for ir_path, ir_data in self.ir_files.items():
            priority = ir_data["priority"]
            source = ir_data["source_file"] or ir_path
            self.priority_groups[priority].append({
                "file": source,
                "tags": ir_data["tags"],
                "reason": self.get_priority_reason(ir_data)
            })

        # If no IR files, prioritize by connection count
        if not self.ir_files and self.dependency_graph:
            for file_path, file_data in self.dependency_graph["files"].items():
                dep_count = len(file_data.get("dependencies", []))
                dependent_count = len(file_data.get("dependents", []))
                total_connections = dep_count + dependent_count

                if total_connections > 10:
                    priority = "critical"
                elif total_connections > 5:
                    priority = "high"
                elif total_connections > 2:
                    priority = "medium"
                else:
                    priority = "low"

                self.priority_groups[priority].append({
                    "file": file_path,
                    "connections": total_connections,
                    "reason": f"{dep_count} deps, {dependent_count} dependents"
                })

        print(f"   Computed priority groups: {dict((k, len(v)) for k, v in self.priority_groups.items())}")

    def get_priority_reason(self, ir_data: Dict) -> str:
        """Get reason for priority assignment"""
        reasons = []

        if 'migration-critical' in ir_data["tags"]:
            reasons.append("migration-critical")
        if 'domain-model' in ir_data["tags"]:
            reasons.append("core domain model")
        if 'business-logic' in ir_data["tags"]:
            reasons.append("business logic")
        if len(ir_data["dependencies"]) > 5:
            reasons.append(f"high coupling ({len(ir_data['dependencies'])} deps)")

        return ", ".join(reasons) if reasons else "normal priority"

    def generate_markdown(self) -> str:
        """Generate the semantic index markdown"""
        md = []

        # Header
        md.append("# Semantic Index - bolt.new Repository")
        md.append("")
        md.append(f"**Generated:** {self.get_timestamp()}")
        md.append("")

        if self.dependency_graph:
            md.append(f"**Total Files:** {self.dependency_graph['metadata']['total_files']}")
        md.append(f"**IR Files Analyzed:** {len(self.ir_files)}")
        md.append("")
        md.append("---")
        md.append("")

        # 1. File Index
        md.append("## 1. File Index")
        md.append("")

        if self.ir_files:
            md.append("### IR Files")
            md.append("")
            for ir_path, ir_data in sorted(self.ir_files.items()):
                source = ir_data["source_file"]
                purpose = ir_data["purpose"][:100].replace('\n', ' ') if ir_data["purpose"] else "No description"
                md.append(f"**{source}**")
                md.append(f"- IR: `{ir_path}`")
                md.append(f"- Purpose: {purpose}...")
                md.append(f"- Tags: {', '.join(ir_data['tags'])}")
                md.append(f"- Priority: {ir_data['priority']}")
                md.append("")
        else:
            md.append("*No IR files found. Generate IR files using the template at `.prompt/prompt-file-template.md`*")
            md.append("")

            # Show top files from dependency graph
            if self.dependency_graph:
                md.append("### Repository Files (from dependency graph)")
                md.append("")

                # Group by directory
                by_dir = defaultdict(list)
                for file_path in sorted(self.dependency_graph["files"].keys()):
                    dir_name = str(Path(file_path).parent) or "root"
                    by_dir[dir_name].append(file_path)

                for dir_name in sorted(by_dir.keys())[:10]:  # Top 10 directories
                    md.append(f"**{dir_name}/**")
                    for file in by_dir[dir_name][:5]:  # Top 5 files per dir
                        file_data = self.dependency_graph["files"][file]
                        exports = ", ".join(file_data.get("exports", [])[:3])
                        md.append(f"- `{Path(file).name}` - Exports: {exports or 'none'}")
                    md.append("")

        md.append("---")
        md.append("")

        # 2. Domain Clusters
        md.append("## 2. Domain Clusters")
        md.append("")

        if self.domain_clusters:
            for domain in sorted(self.domain_clusters.keys(), key=lambda x: len(self.domain_clusters[x]), reverse=True)[:15]:
                files = self.domain_clusters[domain]
                md.append(f"### {domain}")
                md.append(f"*{len(files)} files*")
                md.append("")
                for f in files[:10]:  # Top 10 per cluster
                    md.append(f"- `{f}`")
                if len(files) > 10:
                    md.append(f"- *...and {len(files) - 10} more*")
                md.append("")
        else:
            md.append("*No domain clusters identified yet*")
            md.append("")

        md.append("---")
        md.append("")

        # 3. Dependency Cycles
        md.append("## 3. Dependency Cycles")
        md.append("")

        if self.dependency_cycles:
            md.append(f"**Found {len(self.dependency_cycles)} circular dependencies**")
            md.append("")
            md.append("⚠️ These should be resolved during migration:")
            md.append("")

            for i, cycle in enumerate(self.dependency_cycles[:10], 1):
                md.append(f"**Cycle {i}:**")
                for j, file in enumerate(cycle):
                    arrow = " → " if j < len(cycle) - 1 else ""
                    md.append(f"- `{file}`{arrow}")
                md.append("")
        else:
            md.append("✅ No circular dependencies detected")
            md.append("")

        md.append("---")
        md.append("")

        # 4. System Architecture Map
        md.append("## 4. System Architecture Map")
        md.append("")

        md.append("### Backend")
        for category, items in self.architecture_map["backend"].items():
            if items:
                md.append(f"**{category}** ({len(items)} files)")
                for item in items[:5]:
                    if isinstance(item, dict):
                        md.append(f"- {item['file']} → {item['target']}")
                    else:
                        md.append(f"- `{item}`")
                if len(items) > 5:
                    md.append(f"- *...and {len(items) - 5} more*")
                md.append("")

        md.append("### Frontend")
        for category, items in self.architecture_map["frontend"].items():
            if items:
                md.append(f"**{category}** ({len(items)} files)")
                for item in items[:5]:
                    if isinstance(item, dict):
                        md.append(f"- {item['file']} → {item['target']}")
                    else:
                        md.append(f"- `{item}`")
                if len(items) > 5:
                    md.append(f"- *...and {len(items) - 5} more*")
                md.append("")

        md.append("### Shared")
        for category, items in self.architecture_map["shared"].items():
            if items:
                md.append(f"**{category}** ({len(items)} files)")
                for item in items[:5]:
                    if isinstance(item, dict):
                        md.append(f"- {item['file']} → {item['target']}")
                    else:
                        md.append(f"- `{item}`")
                if len(items) > 5:
                    md.append(f"- *...and {len(items) - 5} more*")
                md.append("")

        md.append("---")
        md.append("")

        # 5. Priority Groups
        md.append("## 5. Migration Priority Groups")
        md.append("")

        priority_order = ["critical", "high", "medium", "normal", "low"]

        for priority in priority_order:
            if priority in self.priority_groups:
                items = self.priority_groups[priority]
                md.append(f"### {priority.upper()} Priority")
                md.append(f"*{len(items)} files*")
                md.append("")

                for item in items[:10]:
                    md.append(f"**`{item['file']}`**")
                    if 'reason' in item:
                        md.append(f"- Reason: {item['reason']}")
                    if 'tags' in item and item['tags']:
                        md.append(f"- Tags: {', '.join(item['tags'])}")
                    if 'connections' in item:
                        md.append(f"- Connections: {item['connections']}")
                    md.append("")

                if len(items) > 10:
                    md.append(f"*...and {len(items) - 10} more*")
                    md.append("")

        md.append("---")
        md.append("")

        # 6. Migration Grouping
        md.append("## 6. Migration Grouping Recommendations")
        md.append("")

        md.append("### Phase 1: Foundation (Critical)")
        md.append("Migrate these first - highest priority and most dependencies")
        md.append("")
        for item in self.priority_groups.get("critical", [])[:5]:
            md.append(f"- `{item['file']}`")
        md.append("")

        md.append("### Phase 2: Core Business Logic (High)")
        md.append("Domain models and business logic")
        md.append("")
        for item in self.priority_groups.get("high", [])[:5]:
            md.append(f"- `{item['file']}`")
        md.append("")

        md.append("### Phase 3: Application Layer (Medium)")
        md.append("UI components, controllers, services")
        md.append("")
        for item in self.priority_groups.get("medium", [])[:5]:
            md.append(f"- `{item['file']}`")
        md.append("")

        md.append("### Phase 4: Supporting Features (Low)")
        md.append("Utilities, helpers, minor features")
        md.append("")
        for item in self.priority_groups.get("low", [])[:5]:
            md.append(f"- `{item['file']}`")
        md.append("")

        md.append("---")
        md.append("")

        # 7. Database Schema Candidates
        md.append("## 7. Database Schema Candidates")
        md.append("")

        if self.database_schemas:
            unique_tables = defaultdict(list)
            for schema in self.database_schemas:
                unique_tables[schema['table']].append(schema['file'])

            md.append(f"**{len(unique_tables)} unique tables identified**")
            md.append("")

            for table, files in sorted(unique_tables.items()):
                md.append(f"### `{table}`")
                md.append(f"Used by: {', '.join(files)}")
                md.append("")
        else:
            md.append("*No database tables identified yet*")
            md.append("")

            # Check for potential data models from dependency graph
            if self.dependency_graph:
                md.append("### Potential Data Models (from code analysis)")
                md.append("")

                for file_path, file_data in self.dependency_graph["files"].items():
                    if file_data.get("interfaces") or file_data.get("classes"):
                        if "model" in file_path.lower() or "types" in file_path.lower() or "schema" in file_path.lower():
                            interfaces = [i if isinstance(i, str) else i.get("name") for i in file_data.get("interfaces", [])]
                            classes = [c if isinstance(c, str) else c.get("name") for c in file_data.get("classes", [])]
                            all_types = interfaces + classes

                            if all_types:
                                md.append(f"**`{file_path}`**")
                                md.append(f"- Types: {', '.join(all_types[:5])}")
                                md.append("")

        md.append("---")
        md.append("")

        # 8. Summary Statistics
        md.append("## 8. Summary Statistics")
        md.append("")

        if self.dependency_graph:
            total_imports = sum(len(f.get("imports", [])) for f in self.dependency_graph["files"].values())
            total_exports = sum(len(f.get("exports", [])) for f in self.dependency_graph["files"].values())
            total_classes = sum(len(f.get("classes", [])) for f in self.dependency_graph["files"].values())
            total_functions = sum(len(f.get("functions", [])) for f in self.dependency_graph["files"].values())

            md.append(f"- **Total Files:** {self.dependency_graph['metadata']['total_files']}")
            md.append(f"- **Total Imports:** {total_imports}")
            md.append(f"- **Total Exports:** {total_exports}")
            md.append(f"- **Total Classes:** {total_classes}")
            md.append(f"- **Total Functions:** {total_functions}")
            md.append(f"- **Circular Dependencies:** {len(self.dependency_cycles)}")
            md.append(f"- **Domain Clusters:** {len(self.domain_clusters)}")
            md.append(f"- **Database Tables:** {len(set(s['table'] for s in self.database_schemas))}")

        md.append("")
        md.append("---")
        md.append("")
        md.append("*Generated by DotPrompt Semantic Index Generator*")

        return "\n".join(md)

    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def generate(self, output_path: str):
        """Main generation workflow"""
        print("=" * 60)
        print("  Semantic Index Generator")
        print("=" * 60)

        # Load data
        has_graph = self.load_dependency_graph()
        ir_count = self.load_ir_files()

        if not has_graph:
            print("\n❌ Cannot proceed without dependency graph")
            print("   Run: python3 .prompt/build_dependency_graph.py")
            return False

        # Analyze
        self.analyze_domain_clusters()
        self.detect_dependency_cycles()
        self.map_architecture()
        self.compute_priority_groups()

        # Generate markdown
        print("\n📝 Generating semantic index...")
        markdown = self.generate_markdown()

        # Write output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"\n✅ Semantic index written to: {output_path}")
        print(f"   Size: {len(markdown)} characters")

        return True


def main():
    """Main entry point"""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    generator = SemanticIndexGenerator(str(repo_root))
    output_path = script_dir / "semantic-index.md"

    success = generator.generate(str(output_path))

    if success:
        print("\n" + "=" * 60)
        print("  Semantic Index Generated Successfully!")
        print("=" * 60)
    else:
        print("\n❌ Failed to generate semantic index")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
