---
name: codebase-exploration
description: >-
  Search codebase, identify patterns, generate call graphs, map imports/dependencies,
  and generate codebase maps using fast local Python scripts. Use this skill whenever
  the user asks to explore, search, map, or analyze a codebase, find regex patterns,
  trace function calls or dependencies, find unused exports, or inspect project structure.
---

# Codebase Exploration

This skill provides fast codebase exploration using Python scripts that run locally. It avoids token-heavy grep/glob operations by offloading search/analysis to fast local scripts.

## Route the task

Read only what the task needs. All paths are relative to this skill.

| If the task involves… | Run / Script |
|---|---|
| **Regex pattern search** across codebase with context lines | `scripts/find_patterns.py` |
| **Function call graph & cycle detection** for JS/TS projects | `scripts/call_graph.py` |
| **Import & dependency mapping**, unused exports & circular deps | `scripts/import_mapper.py` |
| **Full codebase map generation**, file categorization & summaries | `scripts/codebase_mapper.py` |

## Available Scripts

All paths are relative to this skill. Scripts are located in `scripts/` and run locally:

### 1. find_patterns.py - Regex Pattern Search
Fast regex search across codebase with context lines.

```bash
python scripts/find_patterns.py <project-path> --pattern "async function" --ext .js --context 2
```

Options:
- `--pattern`: Regex pattern to search
- `--ext`: File extension filter (default: `.js`)
- `--context`: Context lines around matches (default: `0`)
- `--mode`: `pattern` | `calls` | `imports` | `todos` (default: `pattern`)
- `--output`: Output JSON file

### 2. call_graph.py - Function Call Graph
Builds call graphs for JavaScript/TypeScript projects.

```bash
python scripts/call_graph.py <project-path> --ext .js --output graph.json --cycles --entries
```

Options:
- `--cycles`: Detect circular dependencies
- `--entries`: Find entry points (never-called functions)
- `--output`: Output JSON file

### 3. import_mapper.py - Import/Dependency Mapper
Maps ES6/CommonJS imports and exports, finds unused exports and circular dependencies.

```bash
python scripts/import_mapper.py <project-path> --ext .js --output deps.json --unused --circular
```

Options:
- `--unused`: Find unused exports
- `--circular`: Find circular dependencies
- `--output`: Output JSON file

### 4. codebase_mapper.py - Codebase Map Generator
Generates a structured markdown map of the entire project for LLM consumption. Categorizes files by type (controller, model, route, etc.), extracts exports/imports, and generates summaries. Filters out noise (`node_modules`, build artifacts, lock files, binaries).

```bash
python scripts/codebase_mapper.py <project-path>
```

Features:
- **File categorization**: Detects controllers, models, routes, validators, helpers, configs, migrations, services, middleware, utilities
- **Export extraction**: Parses `module.exports`, `export`, and CommonJS exports
- **Import extraction**: Collects local dependencies (filters out common npm packages)
- **Summary generation**: Extracts JSDoc comments, function names, or first meaningful line
- **Smart ignoring**: Skips `node_modules`, `.git`, `dist`, `build`, lock files, binaries, images, fonts, and hidden files

**CLI Modes** (pass `--mode`):
- `--mode map` (default): Full `CODEBASE_MAP.md` with summaries
- `--mode compact [--depth 2]`: Compact directory tree with file/line counts
- `--mode fingerprint --file <file>`: One-line JSON summary of a single file
- `--mode functions --file <file>`: Extract function signatures from one file (prints JSON)
- `--mode dependents --file <file>`: Find files that import a given file (prints JSON)
- `--mode search --pattern "pattern" [--ext .js] [--context 2]`: Search regex with context (prints JSON)

Output:
- `CODEBASE_MAP.md` written to project root (for `--mode map`)
- JSON to stdout for other modes (pipe to file with `> output.json`)
- JSON data returned programmatically via `CodebaseMapper.map_codebase()` and methods

## Usage Patterns

### Find all async functions
```bash
python scripts/find_patterns.py . --pattern "async\s+function" --ext .js --context 3
```

### Find TODO/FIXME comments
```bash
python scripts/find_patterns.py . --mode todos --ext .js
```

### Map all imports in project
```bash
python scripts/import_mapper.py . --ext .js --output imports.json
```

### Generate call graph and find cycles
```bash
python scripts/call_graph.py . --cycles --entries
```

### Generate full codebase map (markdown)
```bash
python scripts/codebase_mapper.py . --mode map
```

### Compact tree view (token-efficient overview)
```bash
python scripts/codebase_mapper.py . --mode compact --depth 2
```

### Extract function signatures from a file
```bash
python scripts/codebase_mapper.py . --mode functions --file src/controllers/userController.js
```

### Find files that import a given module
```bash
python scripts/codebase_mapper.py . --mode dependents --file src/models/User.js
```

### Search codebase with structured output
```bash
python scripts/codebase_mapper.py . --mode search --pattern "async.*function" --ext .js --context 2
```

### Get one-line fingerprint of a file
```bash
python scripts/codebase_mapper.py . --mode fingerprint --file src/config/db.js
```

## Output Format

All scripts output JSON. Common structure:
```json
{
  "matches": [
    {"file": "path/file.js", "line": 42, "match": "async function foo()", "context": ["line 41", "line 43"]}
  ]
}
```

## Benefits

1. **Token efficient**: Python does heavy lifting, returns only results
2. **Fast**: Native filesystem + regex vs LLM token processing
3. **Structured output**: JSON for programmatic use
4. **No container needed**: Runs locally with any project path

## Bundled resources

- `scripts/find_patterns.py`: Fast regex search across codebase with context lines. Run: `python scripts/find_patterns.py <project-root> --pattern "async function" --ext .js --context 2`.
- `scripts/call_graph.py`: Builds call graphs for JavaScript/TypeScript projects, detects circular dependencies and entry points. Run: `python scripts/call_graph.py <project-root> --ext .js --output graph.json --cycles --entries`.
- `scripts/import_mapper.py`: Maps ES6/CommonJS imports and exports, finds unused exports and circular dependencies. Run: `python scripts/import_mapper.py <project-root> --ext .js --output deps.json --unused --circular`.
- `scripts/codebase_mapper.py`: Generates a structured markdown map of the entire project for LLM consumption, categorizes files, extracts exports/imports. Run: `python scripts/codebase_mapper.py <project-root>`.