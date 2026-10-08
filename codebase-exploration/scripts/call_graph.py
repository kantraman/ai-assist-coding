#!/usr/bin/env python3
"""
Call Graph Generator for JavaScript/TypeScript - Execute in container
Usage: python3 call_graph.py /project/root [--ext .js] [--output graph.json]
"""
import os, re, json, sys, argparse
from collections import defaultdict

# Simple regex-based call extraction for JS (no full parser needed)
FUNC_DEF_RE = re.compile(r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))')
CALL_RE = re.compile(r'(?:^|\s|[({;,])\s*(\w+)\s*\(')

def extract_functions(content):
    """Extract function names from JS content"""
    functions = set()
    for match in FUNC_DEF_RE.finditer(content):
        name = match.group(1) or match.group(2)
        if name and not name.startswith('_'):
            functions.add(name)
    return functions

def extract_calls(content, defined_funcs):
    """Extract function calls that match defined functions"""
    calls = defaultdict(set)
    lines = content.split('\n')
    current_func = None
    
    for i, line in enumerate(lines):
        # Track current function
        func_match = FUNC_DEF_RE.search(line)
        if func_match:
            current_func = func_match.group(1) or func_match.group(2)
        
        # Find calls
        for call_match in CALL_RE.finditer(line):
            called = call_match.group(1)
            if called in defined_funcs and current_func and called != current_func:
                calls[current_func].add(called)
    
    return calls

def build_call_graph(root, ext=".js"):
    """Build call graph across all JS files in project"""
    all_functions = set()
    file_functions = {}
    file_contents = {}
    
    # First pass: collect all function definitions
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(ext):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                    file_contents[path] = content
                    funcs = extract_functions(content)
                    file_functions[path] = funcs
                    all_functions.update(funcs)
                except:
                    pass
    
    # Second pass: extract calls
    graph = defaultdict(set)
    for path, content in file_contents.items():
        calls = extract_calls(content, all_functions)
        for caller, callees in calls.items():
            graph[caller].update(callees)
    
    # Convert to serializable format
    return {k: sorted(list(v)) for k, v in sorted(graph.items())}

def find_circular_deps(graph):
    """Detect circular dependencies in call graph"""
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
                # Found cycle
                idx = path.index(neighbor)
                cycle = path[idx:] + [neighbor]
                if cycle not in cycles:
                    cycles.append(cycle)
        
        rec_stack.remove(node)
    
    for node in graph:
        if node not in visited:
            dfs(node, [])
    
    return cycles

def find_entry_points(graph):
    """Find functions that are never called (potential entry points)"""
    all_called = set()
    for callees in graph.values():
        all_called.update(callees)
    
    all_funcs = set(graph.keys())
    return sorted(all_funcs - all_called)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate call graph for JS/TS project")
    parser.add_argument("root", help="Project root directory")
    parser.add_argument("--ext", default=".js", help="File extension")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--cycles", action="store_true", help="Detect circular dependencies")
    parser.add_argument("--entries", action="store_true", help="Find entry points")
    
    args = parser.parse_args()
    
    graph = build_call_graph(args.root, args.ext)
    
    result = {"call_graph": graph}
    
    if args.cycles:
        result["circular_dependencies"] = find_circular_deps(graph)
    
    if args.entries:
        result["entry_points"] = find_entry_points(graph)
    
    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)