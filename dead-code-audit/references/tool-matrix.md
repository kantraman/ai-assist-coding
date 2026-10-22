# Language tools and dynamic-use traps

Use dedicated tools when installed; they understand language semantics better than grep.
Install only with the user's OK. If a tool is unavailable, `scripts/scan.py` plus manual
verification (SKILL.md step 4) still works.

## Contents
- Python
- JavaScript / TypeScript
- Go
- Java / Kotlin
- Rust
- C# / .NET
- Ruby
- PHP
- Unused third-party dependencies (all ecosystems)
- Dependency graph and cycles

## Python
- `vulture <path> --min-confidence 60`: unused functions/classes/variables/imports. Add a whitelist for framework hooks.
- `ruff check --select F401,F841,ERA001`: unused imports, unused local variables, commented-out code.
- `pydeps`/`import-linter`/`pyan3`: import graph and call graph.
- Traps: `getattr`/`importlib.import_module`, entry points in `pyproject.toml`/`setup.cfg`, Django (`models.py`, `admin.py`, signals, management commands, `urls.py` string refs, `INSTALLED_APPS`), Flask/FastAPI route decorators, Celery tasks, pytest fixtures/`conftest.py`, `__all__`, pickled class paths, Alembic migrations.

## JavaScript / TypeScript
- `npx knip`: unused files, exports, types, dependencies, devDependencies (best single tool; reads package.json, tsconfig, framework configs).
- `npx ts-prune` / `npx unimported`: unused exports / unreferenced files. `depcheck`: unused packages.
- `npx madge --circular --extensions ts,tsx,js src`: cycles; `madge --image graph.svg src` for the graph.
- ESLint `no-unused-vars`, `no-unreachable`, `import/no-unused-modules`.
- Traps: Next.js/Nuxt/SvelteKit file-based routing, barrel files (`index.ts` re-exports), dynamic `import()`, `require(variable)`, webpack aliases, Storybook stories, jest/vite config globs, `package.json` `exports`/`bin`, CSS-in-string class names, React components referenced only in JSX strings or lazy maps.

## Go
- `deadcode ./...` (golang.org/x/tools/cmd/deadcode): reachability from `main`. `staticcheck` (U1000 unused). `go mod tidy -diff` for modules.
- Traps: `init()` functions, interface satisfaction (methods with no direct callers), `//go:linkname`, build tags, reflection/`encoding/json` field use, cgo exports.

## Java / Kotlin
- IntelliJ "Unused declaration" inspection, `ArchUnit`, Gradle `dependency-analysis-plugin`, `mvn dependency:analyze`.
- Traps: Spring/Jakarta annotations (`@Component`, `@Bean`, `@Scheduled`), reflection, serialization, `META-INF/services`, XML configs, public library API.

## Rust
- Compiler `dead_code` and `unused` lints (they already cover private items); `cargo +nightly udeps` or `cargo machete` for dependencies.
- Traps: `pub` items in libraries, `#[cfg(...)]` features, macros, `#[no_mangle]`.

## C# / .NET
- Roslyn analyzers IDE0051/IDE0052/CS8019, ReSharper "unused", `dotnet list package` plus `dotnet-outdated`.
- Traps: DI registration, reflection, Razor/XAML bindings, attributes, serialization.

## Ruby
- `debride` (unused methods), `rubocop --only Lint/UselessAssignment,Lint/UnusedMethodArgument`, `bundle clean`/`bundler-audit`; `traceroute` for unreferenced Rails routes/actions.
- Traps: `send`/`public_send`, `method_missing`, Rails autoload conventions, callbacks, views referencing helpers.

## PHP
- `phpstan` (level 4+ reports unused private members), `composer-unused`, `shipmonk/dead-code-detector`.
- Traps: autoloading by PSR-4 namespace, service containers, Blade/Twig templates, annotations.

## Unused third-party dependencies (all ecosystems)
1. List declared deps (`package.json`, `requirements*.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, `composer.json`).
2. Map package name to import name (they often differ: `pyyaml` to `yaml`, `Pillow` to `PIL`, `@types/x` goes with `x`).
3. Search for imports, plus usage in config/CLI/build scripts (`eslint-plugin-*`, `babel-preset-*`, `pytest-*` plugins, CLI tools invoked from scripts or CI).
4. Distinguish runtime vs dev deps. Flag also *undeclared* imports (used but missing from the manifest).
5. Peer/transitive requirements and plugins loaded by convention are Low confidence.

## Dependency graph and cycles
- Direct dependents of X: files that import X. Transitive: repeat until fixed point.
- "Hot spots": modules with many dependents are risky to change; modules with zero dependents that are not roots are the orphan candidates.
- Report cycles separately. They are not dead code, but they often explain why something couldn't be removed cleanly.
