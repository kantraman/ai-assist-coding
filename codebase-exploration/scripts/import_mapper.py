#!/usr/bin/env python3
"""
Import/Dependency Mapper for JavaScript/TypeScript - Execute in container
Usage: python3 import_mapper.py /project/root [--ext .js] [--output deps.json]
"""
import os, re, json, sys, argparse
from collections import defaultdict

# Import regex patterns
IMPORT_RE = re.compile(
    r'(?:import\s+(?:(?:\*\s+as\s+(\w+))|(?:(?:\{([^}]+)\})|(\w+))?\s+from\s+)?'
    r'[\'"]([^\'"]+)[\'"])'
)
REQUIRE_RE = re.compile(r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)')
EXPORT_RE = re.compile(
    r'export\s+(?:default\s+)?(?:function|class|const|let|var)?\s*(\w+)'
)
MODULE_EXPORTS_RE = re.compile(r'module\.exports\s*=\s*(\w+)')

def resolve_import(import_path, current_file, root):
    """Resolve relative import to absolute path"""
    if import_path.startswith('.'):
        base = os.path.dirname(current_file)
        return os.path.normpath(os.path.join(base, import_path)) + ('.js' if not import_path.endswith('.js') else '')
    return import_path  # External module

def extract_imports_exports(root, ext=".js"):
    """Extract all imports and exports from project"""
    files = {}
    
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(ext):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                    
                    imports = []
                    exports = []
                    
                    # ES6 imports
                    for m in IMPORT_RE.finditer(content):
                        groups = m.groups()
                        named = groups[1].split(',') if groups[1] else []
                        default = groups[2]
                        source = groups[3]
                        imports.append({
                            "source": source,
                            "default": default.strip() if default else None,
                            "named": [n.strip() for n in named if n.strip()],
                            "resolved": resolve_import(source, path, root)
                        })
                    
                    # CommonJS requires
                    for m in REQUIRE_RE.finditer(content):
                        imports.append({
                            "source": m.group(1),
                            "default": None,
                            "named": [],
                            "resolved": resolve_import(m.group(1), path, root)
                        })
                    
                    # ES6 exports
                    for m in EXPORT_RE.finditer(content):
                        exports.append(m.group(1))
                    
                    # CommonJS exports
                    for m in MODULE_EXPORTS_RE.finditer(content):
                        exports.append(m.group(1))
                    
                    files[path] = {
                        "imports": imports,
                        "exports": exports
                    }
                except Exception as e:
                    files[path] = {"imports": [], "exports": [], "error": str(e)}
    
    return files

def build_dependency_graph(files):
    """Build file-to-file dependency graph"""
    graph = defaultdict(set)
    reverse_graph = defaultdict(set)
    external_deps = set()
    
    file_map = {f: f for f in files}
    
    for file, data in files.items():
        for imp in data["imports"]:
            resolved = imp["resolved"]
            if resolved in file_map:
                graph[file].add(resolved)
                reverse_graph[resolved].add(file)
            elif not resolved.startswith('.') and not resolved.startswith('/'):
                external_deps.add(resolved)
    
    return {
        "dependencies": {k: sorted(list(v)) for k, v in graph.items()},
        "dependents": {k: sorted(list(v)) for k, v in reverse_graph.items()},
        "external": sorted(external_deps)
    }

def find_unused_exports(files):
    """Find exports that are never imported"""
    all_exports = {}
    for file, data in files.items():
        for exp in data["exports"]:
            all_exports.setdefault(exp, []).append(file)
    
    all_imports = set()
    for file, data in files.items():
        for imp in data["imports"]:
            all_imports.update(imp["named"])
            if imp["default"]:
                all_imports.add(imp["default"])
    
    unused = {}
    for exp, files_list in all_exports.items():
        if exp not in all_imports:
            unused[exp] = files_list
    
    return unused

def find_circular_deps(graph):
    """Find circular dependencies in file graph"""
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor, path.copy())
            elif neighbor in rec_stack:
                idx = path.index(neighbor)
                cycle = path[idx:] + [neighbor]
                if cycle not in cycles:
                    cycles.append(cycle)
        
        rec_stack.remove(node)
    
    for node in graph:
        if node not in visited:
            dfs(node, [])
    
    return cycles

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Map JS/TS imports and dependencies")
    parser.add_argument("root", help="Project root directory")
    parser.add_argument("--ext", default=".js", help="File extension")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--unused", action="store_true", help="Find unused exports")
    parser.add_argument("--circular", action="store_true", help="Find circular deps")
    
    args = parser.parse_args()
    
    files = extract_imports_exports(args.root, args.ext)
    graph = build_dependency_graph(files)
    
    result = {
        "files": files,
        "dependency_graph": graph
    }
    
    if args.unused:
        result["unused_exports"] = find_unused_exports(files)
    
    if args.circular:
        result["circular_dependencies"] = find_circular_deps(graph["dependencies"])
    
    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)