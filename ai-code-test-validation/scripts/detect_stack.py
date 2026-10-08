#!/usr/bin/env python3
"""Detect languages, test frameworks, and likely test commands for a project.

Usage: python detect_stack.py [project_root]
Prints a JSON report. Heuristic only: always confirm by reading the repo.
"""
import json
import os
import sys

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "__pycache__", "target",
             "build", "dist", ".tox", ".idea", ".gradle", "bin", "obj", ".next"}
EXT_LANG = {".py": "python", ".js": "javascript", ".jsx": "javascript",
            ".ts": "typescript", ".tsx": "typescript", ".java": "java",
            ".kt": "kotlin", ".cs": "csharp", ".fs": "fsharp", ".go": "go",
            ".rs": "rust", ".rb": "ruby", ".php": "php", ".swift": "swift",
            ".scala": "scala", ".c": "c", ".cpp": "cpp"}
TEST_HINTS = ("test", "tests", "spec", "__tests__", "specs")


def read(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def walk(root, max_files=20000):
    n = 0
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            n += 1
            if n > max_files:
                return
            yield dp, fn


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    langs, manifests, test_files, test_dirs = {}, [], [], set()
    for dp, fn in walk(root):
        rel = os.path.relpath(os.path.join(dp, fn), root)
        ext = os.path.splitext(fn)[1].lower()
        if ext in EXT_LANG:
            langs[EXT_LANG[ext]] = langs.get(EXT_LANG[ext], 0) + 1
        low = fn.lower()
        if ext in EXT_LANG and (low.startswith("test_") or ".test." in low or ".spec." in low
                                or low.endswith(("_test.py", "_test.go", "tests.cs", "test.java",
                                                 "tests.java", "test.kt", "_test.rs"))):
            test_files.append(rel)
        parts = rel.lower().split(os.sep)
        for p in parts[:-1]:
            if p in TEST_HINTS:
                test_dirs.add(os.sep.join(rel.split(os.sep)[:parts.index(p) + 1]))
        if fn in ("package.json", "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt",
                  "pytest.ini", "tox.ini", "pom.xml", "build.gradle", "build.gradle.kts",
                  "go.mod", "Cargo.toml", "Gemfile", "composer.json", "Makefile") \
                or fn.endswith((".csproj", ".sln", ".fsproj")):
            manifests.append(rel)

    frameworks, commands, mutation = set(), [], []
    txt = {m: read(os.path.join(root, m)) for m in manifests}
    blob = "\n".join(txt.values()).lower()

    if "python" in langs:
        if "pytest" in blob or any(f.endswith("conftest.py") for f in test_files) or "pytest.ini" in manifests:
            frameworks.add("pytest"); commands.append("pytest -q")
        else:
            frameworks.add("unittest"); commands.append("python -m unittest discover")
        mutation.append("mutmut / cosmic-ray")
    js_pkgs = [m for m in manifests if m.endswith("package.json")]
    if js_pkgs:
        for name in ("vitest", "jest", "mocha", "playwright", "cypress", "ava"):
            if name in blob:
                frameworks.add(name)
        commands.append("npm test")
        mutation.append("stryker")
    if any(m.endswith(("pom.xml",)) for m in manifests):
        frameworks.add("junit" if "junit" in blob else "maven-tests"); commands.append("mvn -q test")
        mutation.append("PIT")
    if any("build.gradle" in m for m in manifests):
        commands.append("./gradlew test"); mutation.append("PIT")
    if any(m.endswith((".csproj", ".sln", ".fsproj")) for m in manifests):
        for name in ("xunit", "nunit", "mstest"):
            if name in blob:
                frameworks.add(name)
        commands.append("dotnet test"); mutation.append("Stryker.NET")
    if "go.mod" in manifests or any(m.endswith("go.mod") for m in manifests):
        frameworks.add("go test"); commands.append("go test -race -cover ./...")
        mutation.append("go-mutesting / gremlins")
    if any(m.endswith("Cargo.toml") for m in manifests):
        frameworks.add("cargo test"); commands.append("cargo test")
        mutation.append("cargo-mutants")
    if "Makefile" in manifests and "test:" in txt.get("Makefile", ""):
        commands.append("make test")

    report = {
        "root": root,
        "languages_by_file_count": dict(sorted(langs.items(), key=lambda kv: -kv[1])),
        "manifests": sorted(manifests),
        "test_frameworks": sorted(frameworks),
        "likely_test_commands": commands,
        "existing_test_dirs": sorted(test_dirs),
        "existing_test_file_count": len(test_files),
        "sample_test_files": test_files[:5],
        "mutation_tools_to_consider": sorted(set(mutation)),
        "note": "Heuristic detection. Confirm by reading manifests and 2-3 existing tests.",
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
