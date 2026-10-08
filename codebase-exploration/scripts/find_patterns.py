#!/usr/bin/env python3
"""
Codebase Pattern Finder - Execute in container for fast token-efficient analysis
Usage: python3 find_patterns.py /project/root "pattern" [--ext .js]
"""
import os, re, json, sys, argparse
from collections import defaultdict

def find_patterns(root, pattern, ext=".js", context=0):
    results = defaultdict(list)
    regex = re.compile(pattern)
    
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(ext):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                        lines = fp.readlines()
                    for i, line in enumerate(lines):
                        if regex.search(line):
                            start = max(0, i - context)
                            end = min(len(lines), i + context + 1)
                            ctx = [f"{j+1}: {lines[j].rstrip()}" for j in range(start, end)]
                            results[path].append({
                                "line": i + 1,
                                "match": line.strip(),
                                "context": ctx
                            })
                except Exception as e:
                    results[path].append({"error": str(e)})
    return results

def find_function_calls(root, ext=".js"):
    """Find all function calls in JS files"""
    call_re = re.compile(r'(\w+)\s*\(')
    results = defaultdict(list)
    
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(ext):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                    for match in call_re.finditer(content):
                        results[path].append(match.group(1))
                except: pass
    return {k: list(set(v)) for k, v in results.items()}

def find_imports_exports(root, ext=".js"):
    """Map imports and exports across files"""
    import_re = re.compile(r'(?:require|import)\s*\(?\s*[\'"]([^\'"]+)[\'"]')
    export_re = re.compile(r'exports?\.(\w+)\s*=')
    
    imports = defaultdict(set)
    exports = defaultdict(set)
    
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(ext):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                    for m in import_re.finditer(content):
                        imports[path].add(m.group(1))
                    for m in export_re.finditer(content):
                        exports[path].add(m.group(1))
                except: pass
    
    return {
        "imports": {k: list(v) for k, v in imports.items()},
        "exports": {k: list(v) for k, v in exports.items()}
    }

def find_todos_fixmes(root, ext=".js"):
    """Find TODO, FIXME, HACK comments"""
    todo_re = re.compile(r'(TODO|FIXME|HACK|NOTE|XXX)[:]\s*(.+)')
    results = defaultdict(list)
    
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith(ext):
                path = os.path.join(dirpath, f)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                        for i, line in enumerate(fp, 1):
                            m = todo_re.search(line)
                            if m:
                                results[path].append({
                                    "line": i,
                                    "type": m.group(1),
                                    "text": m.group(2).strip()
                                })
                except: pass
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Codebase pattern finder")
    parser.add_argument("root", help="Project root directory")
    parser.add_argument("pattern", nargs="?", help="Regex pattern to search")
    parser.add_argument("--ext", default=".js", help="File extension filter")
    parser.add_argument("--context", type=int, default=0, help="Context lines")
    parser.add_argument("--mode", choices=["pattern", "calls", "imports", "todos"], 
                        default="pattern", help="Analysis mode")
    parser.add_argument("--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    if args.mode == "pattern":
        if not args.pattern:
            parser.error("Pattern required for pattern mode")
        result = find_patterns(args.root, args.pattern, args.ext, args.context)
    elif args.mode == "calls":
        result = find_function_calls(args.root, args.ext)
    elif args.mode == "imports":
        result = find_imports_exports(args.root, args.ext)
    elif args.mode == "todos":
        result = find_todos_fixmes(args.root, args.ext)
    
    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)