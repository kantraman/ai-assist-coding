#!/usr/bin/env python3
"""Reconnaissance for a code repository's testing setup.

Detects languages, build manifests, existing test frameworks and test types,
CI configuration, coverage config, and source files that appear to have no
corresponding test. Heuristic by design: use the output as a starting point,
then read the code.

Usage:
    python analyze_repo.py <repo-root> [--format json|markdown] [--max-untested 40]

Stdlib only.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

IGNORE_DIRS = {
    ".git", "node_modules", "venv", ".venv", "env", "__pycache__", "dist", "build",
    "target", "out", ".tox", ".mypy_cache", ".pytest_cache", ".idea", ".vscode",
    "vendor", "coverage", ".next", ".nuxt", ".gradle", "bin", "obj", ".terraform",
    "site-packages", ".cache", "htmlcov", "test-results", "test-report",
}

LANG_BY_EXT = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
    ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript", ".java": "Java",
    ".kt": "Kotlin", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
    ".cs": "C#", ".swift": "Swift", ".c": "C", ".h": "C", ".cpp": "C++", ".cc": "C++",
    ".hpp": "C++", ".scala": "Scala", ".dart": "Dart", ".vue": "Vue", ".svelte": "Svelte",
}

MANIFESTS = {
    "package.json": "Node/JS", "pyproject.toml": "Python", "setup.py": "Python",
    "setup.cfg": "Python", "requirements.txt": "Python", "Pipfile": "Python",
    "pom.xml": "Maven/Java", "build.gradle": "Gradle", "build.gradle.kts": "Gradle",
    "go.mod": "Go", "Cargo.toml": "Rust", "Gemfile": "Ruby", "composer.json": "PHP",
    "Package.swift": "Swift", "pubspec.yaml": "Dart", "mix.exs": "Elixir",
    "Makefile": "Make", "Dockerfile": "Docker", "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose", "tox.ini": "tox", "noxfile.py": "nox",
}

# keyword (matched against dependency names / file content) -> (framework, test type hint)
FRAMEWORK_SIGNATURES = {
    "jest": ("Jest", "unit/integration"), "vitest": ("Vitest", "unit/integration"),
    "mocha": ("Mocha", "unit/integration"), "jasmine": ("Jasmine", "unit"),
    "ava": ("AVA", "unit"), "@playwright/test": ("Playwright", "e2e"),
    "playwright": ("Playwright", "e2e"), "cypress": ("Cypress", "e2e"),
    "puppeteer": ("Puppeteer", "e2e"), "selenium-webdriver": ("Selenium", "e2e"),
    "selenium": ("Selenium", "e2e"), "@testing-library/react": ("Testing Library", "component"),
    "@testing-library/vue": ("Testing Library", "component"),
    "@testing-library/dom": ("Testing Library", "component"),
    "supertest": ("Supertest", "api/integration"), "nock": ("nock", "mocking"),
    "msw": ("MSW", "mocking"), "sinon": ("Sinon", "mocking"),
    "storybook": ("Storybook", "component"), "k6": ("k6", "performance"),
    "pytest": ("pytest", "unit/integration"), "hypothesis": ("Hypothesis", "property-based"),
    "pytest-cov": ("pytest-cov", "coverage"), "coverage": ("coverage.py", "coverage"),
    "pytest-django": ("pytest-django", "integration"), "responses": ("responses", "mocking"),
    "requests-mock": ("requests-mock", "mocking"), "factory-boy": ("factory_boy", "fixtures"),
    "locust": ("Locust", "performance"), "behave": ("Behave", "bdd"),
    "robotframework": ("Robot Framework", "e2e/acceptance"), "tox": ("tox", "runner"),
    "mutmut": ("mutmut", "mutation"), "cosmic-ray": ("Cosmic Ray", "mutation"),
    "@stryker-mutator": ("Stryker", "mutation"), "junit": ("JUnit", "unit"),
    "testng": ("TestNG", "unit"), "mockito": ("Mockito", "mocking"),
    "testcontainers": ("Testcontainers", "integration"), "rest-assured": ("REST Assured", "api"),
    "cucumber": ("Cucumber", "bdd"), "jacoco": ("JaCoCo", "coverage"),
    "pitest": ("PIT", "mutation"), "pact": ("Pact", "contract"),
    "rspec": ("RSpec", "unit/integration"), "minitest": ("Minitest", "unit"),
    "capybara": ("Capybara", "e2e"), "phpunit": ("PHPUnit", "unit/integration"),
    "pest": ("Pest", "unit"), "nunit": ("NUnit", "unit"), "xunit": ("xUnit", "unit"),
    "testify": ("testify", "unit"), "ginkgo": ("Ginkgo", "bdd"), "gomock": ("gomock", "mocking"),
    "tarpaulin": ("tarpaulin", "coverage"), "proptest": ("proptest", "property-based"),
    "nyc": ("nyc/istanbul", "coverage"), "c8": ("c8", "coverage"), "istanbul": ("istanbul", "coverage"),
    "newman": ("Newman/Postman", "api"), "schemathesis": ("Schemathesis", "api fuzz"),
    "detox": ("Detox", "mobile e2e"), "appium": ("Appium", "mobile e2e"),
}

TEST_FILE_PATTERNS = [
    re.compile(r"(^|/)test_[^/]+\.py$"), re.compile(r"_test\.py$"),
    re.compile(r"\.(test|spec)\.[cm]?[jt]sx?$"), re.compile(r"_test\.go$"),
    re.compile(r"(Test|Tests|IT|Spec)\.java$"), re.compile(r"(^|/)Test[A-Z][^/]*\.java$"),
    re.compile(r"(Test|Tests|Spec)\.kt$"), re.compile(r"_spec\.rb$"), re.compile(r"_test\.rb$"),
    re.compile(r"Test\.php$"), re.compile(r"(Tests?|Spec)\.cs$"), re.compile(r"Tests?\.swift$"),
    re.compile(r"_test\.rs$"), re.compile(r"_test\.dart$"),
]
TEST_DIR_NAMES = {"test", "tests", "__tests__", "spec", "specs", "e2e", "integration",
                  "unit", "cypress", "playwright", "features", "acceptance", "functional"}

TYPE_BY_DIR = {
    "unit": "unit", "integration": "integration", "e2e": "e2e", "end2end": "e2e",
    "end-to-end": "e2e", "acceptance": "e2e", "functional": "integration",
    "smoke": "smoke", "regression": "regression", "contract": "contract",
    "perf": "performance", "performance": "performance", "load": "performance",
    "cypress": "e2e", "playwright": "e2e", "features": "bdd", "api": "api",
    "component": "component", "security": "security", "snapshots": "snapshot",
    "__snapshots__": "snapshot",
}

CI_FILES = [
    (".github/workflows", "GitHub Actions"), (".gitlab-ci.yml", "GitLab CI"),
    ("Jenkinsfile", "Jenkins"), (".circleci/config.yml", "CircleCI"),
    ("azure-pipelines.yml", "Azure Pipelines"), ("bitbucket-pipelines.yml", "Bitbucket Pipelines"),
    (".travis.yml", "Travis CI"), ("buildkite.yml", "Buildkite"), (".drone.yml", "Drone"),
]
COVERAGE_FILES = [".coveragerc", "coverage.xml", ".nycrc", ".nycrc.json", "codecov.yml",
                  ".codecov.yml", "jest.config.js", "jest.config.ts", "vitest.config.ts",
                  "vitest.config.js", "jacoco.xml", ".c8rc.json"]


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.endswith(".egg-info")]
        for f in filenames:
            full = os.path.join(dirpath, f)
            yield os.path.relpath(full, root).replace(os.sep, "/")


def is_test_file(rel):
    if any(p.search(rel) for p in TEST_FILE_PATTERNS):
        return True
    parts = rel.split("/")[:-1]
    ext = os.path.splitext(rel)[1]
    return ext in LANG_BY_EXT and any(p.lower() in TEST_DIR_NAMES for p in parts)


def classify_test_type(rel):
    for part in rel.lower().split("/")[:-1]:
        if part in TYPE_BY_DIR:
            return TYPE_BY_DIR[part]
    name = rel.lower().rsplit("/", 1)[-1]
    for key in ("e2e", "integration", "smoke", "regression", "contract", "perf", "load"):
        if key in name:
            return TYPE_BY_DIR.get(key, key)
    return "unit"  # default bucket; a test with no hint is most often a unit test


def read(path, limit=200_000):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read(limit)
    except OSError:
        return ""


def detect_frameworks(root, rels):
    """Return {framework: {"type": hint, "evidence": set()}}."""
    found = defaultdict(lambda: {"type": "", "evidence": set()})

    def add(key, source):
        low = key.lower()
        for sig, (name, kind) in FRAMEWORK_SIGNATURES.items():
            if low == sig or low.startswith(sig + "-") and sig in ("@stryker-mutator",) or \
                    (sig.startswith("@") and low.startswith(sig)):
                found[name]["type"] = kind
                found[name]["evidence"].add(source)

    for rel in rels:
        base = rel.rsplit("/", 1)[-1]
        full = os.path.join(root, rel)
        if base == "package.json":
            try:
                data = json.loads(read(full))
            except ValueError:
                continue
            deps = {}
            for k in ("dependencies", "devDependencies", "peerDependencies"):
                deps.update(data.get(k) or {})
            for d in deps:
                add(d, rel)
            scripts = data.get("scripts") or {}
            for name, cmd in scripts.items():
                for sig in ("jest", "vitest", "mocha", "playwright", "cypress", "nyc", "c8", "k6"):
                    if re.search(r"\b" + sig + r"\b", cmd):
                        add(sig, f"{rel} script '{name}'")
        elif base in ("requirements.txt", "requirements-dev.txt", "requirements-test.txt",
                      "pyproject.toml", "setup.py", "setup.cfg", "Pipfile", "tox.ini", "noxfile.py") \
                or (base.endswith(".txt") and "requirements" in rel):
            text = read(full).lower()
            for sig in ("pytest", "hypothesis", "pytest-cov", "pytest-django", "responses",
                        "requests-mock", "factory-boy", "factory_boy", "locust", "behave", "robotframework",
                        "tox", "mutmut", "cosmic-ray", "selenium", "playwright", "coverage"):
                if re.search(r"(?<![\w-])" + re.escape(sig) + r"(?![\w])", text):
                    add(sig.replace("_", "-"), rel)
            if re.search(r"\bunittest\b", text):
                found["unittest"]["type"] = "unit"
                found["unittest"]["evidence"].add(rel)
        elif base in ("pom.xml", "build.gradle", "build.gradle.kts"):
            text = read(full).lower()
            for sig in ("junit", "testng", "mockito", "testcontainers", "rest-assured", "cucumber",
                        "jacoco", "pitest", "selenium", "playwright", "pact"):
                if sig in text:
                    add(sig, rel)
        elif base == "Gemfile":
            text = read(full).lower()
            for sig in ("rspec", "minitest", "capybara", "cucumber", "selenium"):
                if sig in text:
                    add(sig, rel)
        elif base == "composer.json":
            text = read(full).lower()
            for sig in ("phpunit", "pest", "mockery", "behat"):
                if sig in text:
                    add(sig, rel)
        elif base == "go.mod":
            text = read(full).lower()
            for sig in ("testify", "ginkgo", "gomock", "testcontainers"):
                if sig in text:
                    add(sig, rel)
        elif base == "Cargo.toml":
            text = read(full).lower()
            for sig in ("proptest", "tarpaulin"):
                if sig in text:
                    add(sig, rel)
        elif base.endswith(".csproj"):
            text = read(full).lower()
            for sig in ("xunit", "nunit", "mstest", "specflow", "coverlet", "playwright", "selenium"):
                if sig in text:
                    add(sig, rel)
    # Language-native runners that need no dependency
    if any(r.endswith("_test.go") for r in rels):
        found["go test"]["type"] = "unit"
        found["go test"]["evidence"].add("*_test.go files")
    if any(r.endswith("_test.rs") or "/tests/" in r and r.endswith(".rs") for r in rels):
        found["cargo test"]["type"] = "unit/integration"
        found["cargo test"]["evidence"].add("Rust test files")
    return {k: {"type": v["type"], "evidence": sorted(v["evidence"])} for k, v in found.items()}


def stem_variants(rel):
    """Names a test for this source file might carry."""
    base = os.path.splitext(rel.rsplit("/", 1)[-1])[0]
    return {base.lower(), base.lower().replace("_", ""), base.lower().replace("-", "")}


def test_stems(test_rels):
    stems = set()
    for rel in test_rels:
        base = os.path.splitext(rel.rsplit("/", 1)[-1])[0].lower()
        base = re.sub(r"\.(test|spec)$", "", base)
        base = re.sub(r"^test_", "", base)
        base = re.sub(r"(_test|_spec|tests?|spec|it)$", "", base) if not base.startswith("test") else base
        stems.add(base)
        stems.add(base.replace("_", "").replace("-", ""))
    return stems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--format", choices=["json", "markdown"], default="markdown")
    ap.add_argument("--max-untested", type=int, default=40)
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.exit(f"Not a directory: {root}")

    rels = sorted(walk(root))
    lang_counter, lang_loc = Counter(), Counter()
    src_files, test_files = [], []
    for rel in rels:
        ext = os.path.splitext(rel)[1].lower()
        if ext not in LANG_BY_EXT:
            continue
        lang = LANG_BY_EXT[ext]
        if is_test_file(rel):
            test_files.append(rel)
            continue
        src_files.append(rel)
        lang_counter[lang] += 1
        text = read(os.path.join(root, rel), 400_000)
        lang_loc[lang] += text.count("\n") + 1

    manifests = sorted({r for r in rels if r.rsplit("/", 1)[-1] in MANIFESTS or r.endswith(".csproj") or r.endswith(".sln")})
    frameworks = detect_frameworks(root, rels)

    ci = []
    for path, name in CI_FILES:
        full = os.path.join(root, path)
        if os.path.exists(full):
            ci.append({"system": name, "path": path})
    ci_runs_tests = None
    for entry in ci:
        full = os.path.join(root, entry["path"])
        text = ""
        if os.path.isdir(full):
            for f in os.listdir(full):
                text += read(os.path.join(full, f))
        else:
            text = read(full)
        if re.search(r"\b(test|pytest|jest|vitest|mvn|gradle|go test|cargo test|rspec|phpunit|dotnet test)\b", text):
            ci_runs_tests = True
    if ci and ci_runs_tests is None:
        ci_runs_tests = False

    coverage_cfg = [f for f in COVERAGE_FILES if f in {r.rsplit("/", 1)[-1] for r in rels}]

    type_counter = Counter(classify_test_type(t) for t in test_files)

    stems = test_stems(test_files)
    skip_names = {"__init__", "index", "conftest", "setup", "main", "app", "config", "settings",
                  "types", "constants", "manage", "wsgi", "asgi", "mod", "lib"}
    untested = []
    for rel in src_files:
        base = os.path.splitext(rel.rsplit("/", 1)[-1])[0]
        if base.lower() in skip_names or base.endswith(".d") or base.endswith(".config"):
            continue
        if rel.endswith((".h", ".hpp")):
            continue
        if not (stem_variants(rel) & stems):
            try:
                size = os.path.getsize(os.path.join(root, rel))
            except OSError:
                size = 0
            untested.append((rel, size))
    untested.sort(key=lambda x: -x[1])  # bigger files first: more likely to matter

    # Weak signals in existing tests
    skipped_markers = 0
    no_assert_files = []
    assert_re = re.compile(r"\b(assert|expect|should|verify|Assert\.|assertEquals?|require\.|t\.(Error|Fatal)|XCTAssert)")
    for rel in test_files[:2000]:
        text = read(os.path.join(root, rel), 300_000)
        skipped_markers += len(re.findall(
            r"(@pytest\.mark\.skip|@unittest\.skip|\bxit\(|\bit\.skip|\btest\.skip|\bxdescribe|@Disabled|@Ignore|t\.Skip\(|pending\()", text))
        if text and not assert_re.search(text):
            no_assert_files.append(rel)

    result = {
        "root": root,
        "languages": [{"language": l, "files": lang_counter[l], "approx_loc": lang_loc[l]}
                      for l, _ in lang_counter.most_common()],
        "manifests": manifests[:40],
        "source_files": len(src_files),
        "test_files": len(test_files),
        "test_to_source_ratio": round(len(test_files) / len(src_files), 2) if src_files else None,
        "test_types_detected": dict(type_counter),
        "frameworks": frameworks,
        "ci": ci,
        "ci_runs_tests": ci_runs_tests,
        "coverage_config": coverage_cfg,
        "skipped_test_markers": skipped_markers,
        "test_files_without_assertions": no_assert_files[:25],
        "likely_untested_sources": [{"file": f, "bytes": s} for f, s in untested[:args.max_untested]],
        "likely_untested_total": len(untested),
        "has_docker_compose": any(r.startswith("docker-compose") or r.endswith("/docker-compose.yml") for r in rels),
        "notes": [
            "Heuristic output: 'untested' means no test file with a matching name was found, "
            "not that the code has no coverage.",
        ],
    }

    if args.format == "json":
        print(json.dumps(result, indent=2))
        return

    out = [f"# Repository test recon: `{os.path.basename(root)}`", ""]
    out.append("## Stack")
    if result["languages"]:
        for l in result["languages"][:8]:
            out.append(f"- {l['language']}: {l['files']} files, ~{l['approx_loc']:,} lines")
    else:
        out.append("- No recognised source files found")
    if manifests:
        out.append(f"- Manifests: {', '.join(manifests[:12])}")
    out.append("")
    out.append("## Current testing state")
    out.append(f"- Source files: {result['source_files']} | Test files: {result['test_files']} "
               f"| Ratio: {result['test_to_source_ratio']}")
    if type_counter:
        out.append("- Test types (by location/name): " + ", ".join(f"{k}={v}" for k, v in type_counter.most_common()))
    else:
        out.append("- **No tests detected**")
    if frameworks:
        out.append("- Frameworks/tools detected:")
        for name, info in sorted(frameworks.items()):
            out.append(f"  - {name} ({info['type']}) — {', '.join(info['evidence'][:2])}")
    else:
        out.append("- No test frameworks detected")
    out.append(f"- CI: {', '.join(c['system'] for c in ci) if ci else 'none detected'}"
               + (f" (runs tests: {ci_runs_tests})" if ci else ""))
    out.append(f"- Coverage config: {', '.join(coverage_cfg) if coverage_cfg else 'none detected'}")
    out.append(f"- Skipped/disabled test markers: {skipped_markers}")
    if no_assert_files:
        out.append(f"- Test files with no assertion-like calls ({len(no_assert_files)}): "
                   + ", ".join(no_assert_files[:8]) + (" …" if len(no_assert_files) > 8 else ""))
    out.append("")
    out.append(f"## Source files with no obviously matching test ({result['likely_untested_total']} total; largest first)")
    for f, s in untested[:args.max_untested]:
        out.append(f"- `{f}` ({s:,} bytes)")
    if not untested:
        out.append("- none")
    out.append("")
    out.append("_Heuristic only — matching is by file name. Confirm by reading code and measuring coverage._")
    print("\n".join(out))


if __name__ == "__main__":
    main()
