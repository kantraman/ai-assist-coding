#!/usr/bin/env python3
"""Maintainability metrics for Python files (stdlib only).

Usage: complexity_check.py <path>
Flags functions that are long, deeply nested, branch-heavy, or take many parameters.
Also flags oversized files in any language (line count only).
"""
import ast, os, sys

MAX_FUNC_LINES, MAX_COMPLEXITY, MAX_NESTING, MAX_PARAMS, MAX_FILE_LINES = 50, 10, 4, 5, 500
SKIP = {".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build"}
BRANCH = (ast.If, ast.For, ast.While, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.AsyncWith,
          ast.IfExp, ast.comprehension, ast.Assert)


def complexity(fn):
    c = 1
    for n in ast.walk(fn):
        if isinstance(n, BRANCH):
            c += 1
        elif isinstance(n, ast.BoolOp):
            c += len(n.values) - 1
    return c


def depth(node, d=0):
    nest = (ast.If, ast.For, ast.While, ast.AsyncFor, ast.Try, ast.With, ast.AsyncWith)
    best = d
    for ch in ast.iter_child_nodes(node):
        best = max(best, depth(ch, d + 1) if isinstance(ch, nest) else depth(ch, d))
    return best


def check_py(path):
    issues = []
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except (SyntaxError, UnicodeDecodeError) as e:
        return [f"{path}: cannot parse ({e})"]
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            length = (n.end_lineno or n.lineno) - n.lineno + 1
            params = len(n.args.args) + len(n.args.kwonlyargs)
            cx, nd = complexity(n), depth(n)
            where = f"{path}:{n.lineno} {n.name}()"
            if length > MAX_FUNC_LINES: issues.append(f"{where} is {length} lines (>{MAX_FUNC_LINES})")
            if cx > MAX_COMPLEXITY:     issues.append(f"{where} complexity ~{cx} (>{MAX_COMPLEXITY})")
            if nd > MAX_NESTING:        issues.append(f"{where} nesting depth {nd} (>{MAX_NESTING})")
            if params > MAX_PARAMS:     issues.append(f"{where} has {params} parameters (>{MAX_PARAMS})")
            if not ast.get_docstring(n) and not n.name.startswith("_") and length > 15:
                issues.append(f"{where} public, {length} lines, no docstring")
    return issues


def main(root):
    issues, files = [], []
    for d, dirs, fs in os.walk(root) if os.path.isdir(root) else [(os.path.dirname(root), [], [os.path.basename(root)])]:
        dirs[:] = [x for x in dirs if x not in SKIP]
        files += [os.path.join(d, f) for f in fs]
    for p in files:
        ext = os.path.splitext(p)[1]
        if ext == ".py":
            issues += check_py(p)
        if ext in {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".go", ".rs", ".c", ".cpp", ".cs", ".rb", ".php"}:
            try:
                n = sum(1 for _ in open(p, encoding="utf-8", errors="ignore"))
                if n > MAX_FILE_LINES:
                    issues.append(f"{p} is {n} lines (>{MAX_FILE_LINES}); consider splitting")
            except OSError:
                pass
    print("\n".join(issues) if issues else "No maintainability issues flagged by thresholds.")
    print(f"\n{len(issues)} maintainability finding(s). Thresholds are smells, not laws; use judgment.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
