# Agent Skills Library

A curated, battle-tested collection of modular **skills, runbooks, and executable toolkits** designed for agentic AI coding assistants—including **Google Antigravity (AGY)**, **Gemini CLI**, **Claude Code**, and coding agents implementing the `.agents/skills` customization protocol.

Each skill acts as a specialized playbook that equips the AI agent with domain expertise, proven engineering workflows, decision trees, and local automation scripts—without needing external containers or heavyweight dependencies.

---

## Table of Contents

- [Overview](#overview)
- [How Skills Work](#how-skills-work)
- [Installation & Setup](#installation--setup)
- [Skills Catalog](#skills-catalog)
  - [1. Planning, Architecture & Fullstack Systems](#1-planning-architecture--fullstack-systems)
  - [2. Software Implementation & Engineering](#2-software-implementation--engineering)
  - [3. Disciplined Reasoning & Research](#3-disciplined-reasoning--research)
  - [4. Database & Data Modeling](#4-database--data-modeling)
  - [5. Code Quality, Refactoring & Codebase Health](#5-code-quality-refactoring--codebase-health)
  - [6. Testing & Quality Assurance](#6-testing--quality-assurance)
  - [7. Codebase Exploration & Security Analysis](#7-codebase-exploration--security-analysis)
  - [8. Debugging & Root Cause Analysis](#8-debugging--root-cause-analysis)
  - [9. UI/UX & Creative Frontend Engineering](#9-uiux--creative-frontend-engineering)
  - [10. Algorithms & Problem Solving](#10-algorithms--problem-solving)
  - [11. Domain Integrations & Compliance](#11-domain-integrations--compliance)
  - [12. Documentation & Technical Handover](#12-documentation--technical-handover)
  - [13. Agent Meta-Skills & Evolution](#13-agent-meta-skills--evolution)
  - [14. Cost & Token Optimization](#14-cost--token-optimization)
- [Skill Structure Specification](#skill-structure-specification)
- [Adding New Skills](#adding-new-skills)
- [License](#license)

---

## Overview

Modern AI coding agents excel when guided by clear protocols and targeted domain knowledge rather than generic prompts. This repository packages production-grade software engineering practices into modular directories:

- **Token Efficient**: Uses progressive disclosure—agents load only the frontmatter index initially, reading detailed instructions and reference manuals only when relevant.
- **Runnable Local Tools**: Ships with fast, zero-dependency Python utilities for tasks like dependency analysis, AST pattern matching, WCAG contrast verification, Mermaid syntax linting, Postman collection generation, hardcoded color extraction, dead code scanning, repo reconnaissance, and mutation testing.
- **Portable & Isolated**: All script and asset paths are self-contained and relative to each skill directory.

---

## How Skills Work

Skills leverage **Progressive Disclosure** to maintain a lean context window:

1. **Discovery**: On startup, the agent indexes the `name` and `description` frontmatter from every `SKILL.md`.
2. **Triggering**: When user requests match the skill's triggers or domain (e.g., "draw architecture diagram", "desktop-like React app", "break out of debugging loop", "audit dead code", "audit accessibility"), the agent activates the skill.
3. **Execution**: The agent loads `SKILL.md`, executes local scripts from `scripts/`, or consults deep-dive documentation in `references/` on-demand.

---

## Installation & Setup

### Option 1: Workspace Installation (Project-Specific)

Place the skills folder into the `.agents/skills/` directory at the root of your project:

```bash
# Clone directly into your repository's .agents folder
git clone https://github.com/your-username/agent-skills.git .agents/skills
```

Your project directory tree:
```text
my-project/
├── .agents/
│   └── skills/
│       ├── architecture-diagrams/
│       ├── codebase-exploration/
│       ├── db-schema-designer/
│       ├── desktop-app-ux/
│       ├── frontend-ux-craft/
│       ├── fullstack-dev/
│       ├── refactor-and-redesign/
│       ├── secure-code-forge/
│       ├── software-documentation/
│       ├── test-suite-architect/
│       ├── web-graphics-studio/
│       ├── widen-the-lens/
│       └── ...
├── src/
└── package.json
```

Any agent operating in `my-project` will automatically discover and load these skills.

### Option 2: Global Installation (Machine-Wide)

To make these skills available across all workspaces on your machine, copy or clone them into your global agent configuration directory:

```bash
# For Antigravity / Gemini CLI:
git clone https://github.com/your-username/agent-skills.git ~/.gemini/config/skills

# Or under user home:
git clone https://github.com/your-username/agent-skills.git ~/.agents/skills
```

---

## Skills Catalog

| Skill | Category | Purpose | Key Tools / Resources |
|---|---|---|---|
| [`adversial-review`](#adversial-review) | Quality & Review | Strict Principal Engineer & Security Architect code review | Correctness, complexity, security vectors |
| [`ai-code-test-validation`](#ai-code-test-validation) | Testing | Requirement-driven unit/regression tests with mutation verification | Stack detector, AST mutation runner (`scripts/`) |
| [`architecture-diagrams`](#architecture-diagrams) | Architecture | Diagrams systems using Mermaid across C4 (L1-L3) and UML (sequence, state, class, ER) | `scripts/lint_mermaid.py`, C4/UML templates |
| [`autonomous-planner`](#autonomous-planner) | Planning | Turns vague briefs into approved Markdown execution plans (`PLAN.md`) before coding | Step-by-step interview, plan templates |
| [`code-implementation`](#code-implementation) | Implementation | Modular, iterative implementation from specs calibrated to complexity & robustness targets | Complexity matrix, module breakdown protocol |
| [`code-quality`](#code-quality) | Quality & Review | Writing and refactoring clean, maintainable, and sensibly performant code | `references/maintainability.md`, `references/performance.md` |
| [`codebase-exploration`](#codebase-exploration) | Exploration | High-speed regex pattern search, import/dependency mapping, call graphs | `find_patterns.py`, `call_graph.py`, `import_mapper.py` |
| [`coding-expert`](#coding-expert) | Implementation | Pragmatic, low-overhead code generation tuned for cost/context efficiency | Architecture preservation rules |
| [`commit-message-crafter`](#commit-message-crafter) | Implementation | Git commit messages crafted from real diff analysis, change splitting, and repo style matching | `scripts/analyze_changes.py`, `conventions.md` |
| [`db-schema-designer`](#db-schema-designer) | Database | Designs SQL and NoSQL schemas optimized for access patterns, integrity, and indexes | SQL & NoSQL modeling guides |
| [`dead-code-audit`](#dead-code-audit) | Quality & Review | Identifies unreachable files, dead exports, stale flags, and unused packages with confidence tiers | `scripts/scan.py`, `references/tool-matrix.md` |
| [`desktop-app-ux`](#desktop-app-ux) | Frontend UX | Desktop-like native feel for React (VS Code/Linear/Figma style, hotkeys, palettes) | `references/react-patterns.md`, pane layouts |
| [`domain-ux-design`](#domain-ux-design) | Frontend UX | Business-domain-driven UX, visible business logic, and one memorable signature element | `references/patterns.md`, `references/anti-patterns.md` |
| [`dsa-expert`](#dsa-expert) | Algorithms | Algorithm selection, Big-O analysis, LeetCode/DSA problem solving | Decision matrix, patterns catalog |
| [`engineering-mindset`](#engineering-mindset) | Reasoning | Disciplined software-reasoning pipeline (First-Principles, Systems, Premortem, TDD, YAGNI) | `references/lenses.md`, `references/templates.md` |
| [`frontend-ux-craft`](#frontend-ux-craft) | Frontend UX | Senior UI/UX engineering, WCAG 2.2 AA accessibility, design tokens, security | `tokens.css`, `audit_project.py`, `contrast.py` |
| [`fullstack-dev`](#fullstack-dev) | Fullstack | End-to-end applications via fractal architecture, genetic algorithm tuning, and knowledge graphs | `scaffold_module.py`, `ga_tuner.py`, `kg_build.py` |
| [`grounded-reasoning`](#grounded-reasoning) | Reasoning | Rigorous anti-hallucination workflow: Focus, Elaborate, Substantiate, Decide with Knowledge Graph | `scripts/kg_tool.py`, `evidence-standards.md` |
| [`nist-rmf-ai`](#nist-rmf-ai) | Compliance | NIST AI Risk Management Framework (Govern, Map, Measure, Manage) compliance | 7 AI trustworthiness pillars |
| [`payment-integration`](#payment-integration) | Integrations | Payment gateways (Stripe, Razorpay, PayPal, UPI) with safe webhook verification | Plan template, security checklist |
| [`refactor-and-redesign`](#refactor-and-redesign) | Refactoring | Large-scale code refactors and UI redesigns in small verified batches | `find_hardcoded_colors.py`, `contrast.py`, `PLAN.md` |
| [`researcher`](#researcher) | Research | Deep web-based research, source hierarchy verification, full-page inspection, and synthesis | Strategic querying, cross-checking protocols |
| [`secure-code-forge`](#secure-code-forge) | Implementation | Secure-by-construction code synthesis with intent contracts, STRIDE threat models, and self-review | `complexity_check.py`, `pattern_scan.py`, checklists |
| [`security-analysis`](#security-analysis) | Security | OWASP vulnerability detection, threat modeling, and input validation | Security checklists and reporting templates |
| [`skill-evolver`](#skill-evolver) | Meta-Skills | Evaluates, audits, benchmarks, mutates, and evolves agent skills without in-place edits | `scripts/audit_skill.py`, capability diffs, rubrics |
| [`skill-orchestrator`](#skill-orchestrator) | Meta-Skills | Decides HOW to accomplish tasks; searches, selects, composes, or builds skills on a least-power ladder | `selection-rubric.md`, `mcp-server-template.md` |
| [`software-documentation`](#software-documentation) | Documentation | Produces audience-specific docs (Dev, Client, PM, QA) and Postman collections | `scripts/build_postman_collection.py`, templates |
| [`specification-planning`](#specification-planning) | Planning | Systemic architectural discovery and interface mapping before refactors | Interface discovery protocol |
| [`test-suite-architect`](#test-suite-architect) | Testing | Repository-wide test suite design, gap analysis, flaky test repairs, and execution reporting | `scripts/analyze_repo.py`, `generate_report.py` |
| [`token-optimiser`](#token-optimiser) | Optimization | Anti-burst request pacing and context compaction for free-tier models | Throttling rules, context strategies |
| [`web-graphics-studio`](#web-graphics-studio) | Graphics | Creative animations, interactive visuals, Canvas 2D/WebGL, and high-impact pages | `starter.html`, GSAP/SVG/Canvas recipes |
| [`widen-the-lens`](#widen-the-lens) | Debugging | Unstick-and-widen protocol to break debugging loops and surface root causes | `scripts/ledger.py`, hypothesis matrix |

---

### 1. Planning, Architecture & Fullstack Systems

#### `autonomous-planner`
- **When to use**: When starting any non-trivial feature, complex bug fix, or greenfield project where coding without a plan is risky.
- **Workflow**: Clarifies underspecified requirements, conducts targeted web research, coordinates with other skills, and outputs a clear, step-by-step `PLAN.md` with verification criteria.
- **Example triggers**: `"plan this feature"`, `"create a spec"`, `"how should we build this"`, `"write a design doc"`.
- **Bundled Resources**:
  - `references/clarifying-questions.md`: Structured interview guide for underspecified requests.
  - `references/plan-template.md`: Battle-tested template for execution plans with rollback gates.

#### `specification-planning`
- **When to use**: When initiating complex refactors, structural migrations, or component redesigns.
- **Workflow**: Enforces a strict pause before touching code: maps existing dependencies, defines explicit interfaces and data types, and traces side effects.
- **Key Focus**: Contract-driven interface mapping, component decoupling, and dependency boundary verification.

#### `architecture-diagrams`
- **When to use**: Whenever you need to visualize, diagram, document, or explain a software system, service topology, microservices layout, API communication flow, or data lifecycle.
- **Notation & Standards**:
  - **C4 Model**: Level 1 (System Context), Level 2 (Container), and Level 3 (Component) rendered using universally compatible Mermaid `flowchart` syntax.
  - **UML Diagrams**: Sequence diagrams (`sequenceDiagram`), state machines (`stateDiagram-v2`), class structures (`classDiagram`), and database relationships (`erDiagram`).
  - **Portability**: Uses strict, render-safe Mermaid syntax that compiles reliably on GitHub, GitLab, Notion, Confluence, and MkDocs without requiring fragile beta features.
- **Bundled Resources**:
  - `scripts/lint_mermaid.py`: Validates Mermaid diagrams for syntax errors, unescaped characters, and renderer-breaking constructs.
  - `references/c4-in-mermaid.md`: Copy-ready C4 diagram templates with subgraphs and styling.
  - `references/uml-in-mermaid.md`: Production templates for sequence, state, class, and ER diagrams.
  - `references/mermaid-pitfalls.md`: Comprehensive list of Mermaid parser quirks and fixes.
  - `assets/architecture-doc-template.md`: Architectural documentation template.

#### `fullstack-dev`
- **When to use**: Building, extending, scaling, or reviewing complete full-stack applications across web frameworks (Next.js, FastAPI, Django, NestJS, Spring Boot, Rails, Go, Express) and databases.
- **Key Pillars**:
  - **Fractal Architecture**: Enforces a self-similar repeating shape (Contract, Core, Adapters, Proof) at every scale so code remains modular and predictable (`references/fractal-architecture.md`).
  - **Genetic Optimization (GA)**: Searches combinatorial tuning spaces (index sets, cache pool sizing, chunking, query variants) against measurable fitness functions (`scripts/ga_tuner.py`, `references/genetic-optimization.md`).
  - **Knowledge Graph + Ontology**: Maps relationships between requirements, modules, entities, endpoints, and test gates for automated impact analysis and drift detection (`scripts/kg_build.py`, `references/knowledge-graph-ontology.md`).
- **Bundled Resources**:
  - `scripts/scaffold_module.py`: Generates standardized modular architecture folders with manifests, contracts, adapters, and tests.
  - `scripts/design_tokens.py`: Generates modular-scale design tokens with OKLCH theme palettes.
  - `scripts/ga_tuner.py`: Genetic algorithm parameter optimizer for system bottlenecks.
  - `scripts/kg_build.py`: Knowledge graph builder and validation engine.
  - `references/stack-profiles.md`: Curated conventions, idioms, and defaults for modern tech stacks.
  - `references/api-design.md`: REST, GraphQL, cursor pagination, and error contract standards.
  - `references/db-schema-design.md`: Expand/contract migrations, constraint modeling, and index derivation.
  - `references/quality-gates.md`: Non-negotiable release criteria for performance, security, and test coverage.

---

### 2. Software Implementation & Engineering

#### `code-implementation`
- **When to use**: Implementing code from software requirements, specifications, user stories, or design docs, one module at a time.
- **Workflow**:
  - **Intake & Clarification**: Restates objectives in 3-6 lines and surfaces ambiguities before touching code.
  - **Upfront Calibration**: Explicitly queries complexity targets (Prototype vs. Standard vs. Production-grade) and robustness levels (Happy path vs. Validated inputs vs. Defensive).
  - **Modular Construction**: Proposes build order dependencies-first, implementing the simplest correct code with proportionate tests before asking for feedback.
  - **Evidence Gate**: Never claims code works without running it in a sandbox or execution environment.

#### `secure-code-forge`
- **When to use**: Writing production-grade code that is secure, maintainable, and performant by construction, or auditing and hardening existing code.
- **The Loop**: **Intent → Design → Generate → Review → Fix → Deliver**.
- **Core Principles**:
  - **Intent Contract**: Captures numbered requirements (R1, R2...), trust boundaries, and performance budgets before coding (`assets/intent-contract.md`).
  - **Secure by Construction**: Input validation allowlists, parameterization, constant-time secret comparison, and boundary bounding (timeouts, payload caps).
  - **Autonomous Self-Review**: Claude reviews its generated output as a skeptical outsider against maintainability, performance, and security checklists before delivery.
- **Bundled Resources**:
  - `scripts/complexity_check.py`: Calculates cyclomatic complexity and nesting depth to enforce maintainability gates.
  - `scripts/pattern_scan.py`: AST and regex scanner detecting dangerous patterns (eval, raw queries, unquoted shell args).
  - `scripts/static_checks.sh`: Local static analysis orchestrator.
  - `references/security-checklist.md`, `references/maintainability-checklist.md`, `references/performance-checklist.md`: Deep inspection rubrics.

#### `coding-expert`
- **When to use**: Optimized for smaller models or constrained token budgets where fast, pragmatic, and surgical code generation is needed.
- **Focus**: Produces surgical, working code with minimal diffs, avoiding unnecessary dependencies, verbose explanations, or stylistic churn.

#### `commit-message-crafter`
- **When to use**: Writing clear, accurate git commit messages by analyzing real diffs, splitting mixed commits, or generating PR titles and squash messages.
- **Workflow**:
  - **Diff Analysis**: Inspects staged changes, working trees, or commit ranges using `scripts/analyze_changes.py`.
  - **Behavior & Intent Extraction**: Identifies what behavior changed and why (extracting ticket IDs from branch names, comments, and test names).
  - **Commit Splitting**: Recommends splitting commits when the analyzer flags mixed concerns (refactors mixed with features or dependency updates).
  - **Convention Matching**: Aligns with repository conventions (Conventional Commits, ticket prefixes, imperative mood).
- **Bundled Resources**:
  - `scripts/analyze_changes.py`: Zero-dependency script analyzing git diffs, file modifications, commit style history, and risk warnings.
  - `references/conventions.md`: Comprehensive guide to Conventional Commits, scopes, and breaking change footers.

---

### 3. Disciplined Reasoning & Research

#### `engineering-mindset`
- **When to use**: System design, architecture trade-offs, code reviews, refactoring plans, or debugging when a robust, multi-perspective evaluation is required.
- **Reasoning Lenses**:
  - **First-Principles & Systems Thinking**: Decomposing to fundamental limits, trust boundaries, feedback loops, and data flows.
  - **Tree-of-Thought & Trade-Off Matrices**: Generating 2-4 distinct solutions and scoring them against weighted constraints.
  - **Premortem & Second-Order Effects**: Assuming production failure to surface risks, and tracing impact at 1 week, 6 months, and 2 years.
  - **YAGNI & TDD**: Pruning speculative code and driving implementation through failure-mode and boundary tests.
- **Bundled Resources**:
  - `references/lenses.md`: Comprehensive prompts, failure modes, and guidance for each reasoning lens.
  - `references/templates.md`: Ready-made markdown templates for trade-off matrices, premortems, and architectural decision records.

#### `grounded-reasoning`
- **When to use**: High-stakes research questions, fact-checking, due diligence, technical comparisons, or decision-making where hallucination must be strictly eliminated.
- **Protocol**: **Focus → Elaborate → Substantiate → Decide**.
- **Core Principles**:
  - **Status-Tagged Claims**: Every material claim is labeled as *verified*, *established*, *inferred*, *assumed*, or *unknown*.
  - **Atomic Decomposition**: Breaks complex claims into individually checkable pieces.
  - **Triangulation**: Corroborates critical facts with at least two independent primary or reputable secondary sources.
  - **Knowledge Graph Structure**: Retains verified entities and relationships in an inspectable structure.
- **Bundled Resources**:
  - `scripts/kg_tool.py`: CLI knowledge graph utility supporting entity extraction, relationship querying, and format exports.
  - `references/evidence-standards.md`: Epistemic tiers, source reliability hierarchy, and confidence evaluation guidelines.
  - `references/decision-protocol.md`: Decision-making algorithms that inherit confidence from the weakest critical claim.

#### `researcher`
- **When to use**: Deep web research, investigating tools, libraries, companies, market developments, or verifying contested technical claims.
- **Workflow**:
  - **Strategic Querying**: Deconstructs questions into independent sub-queries; executes tiered searches (Quick vs. Standard vs. Deep).
  - **Source Hierarchy**: Prioritizes primary sources (official docs, regulator filings, repos) over secondary commentary and SEO listicles.
  - **Full-Page Verification**: Fetches and reads full web pages rather than relying on search snippets.
  - **Disagreement Mapping**: Explicitly highlights conflicting findings rather than picking winners arbitrarily.

---

### 4. Database & Data Modeling

#### `db-schema-designer`
- **When to use**: Designing schemas for relational databases (PostgreSQL, MySQL, SQLite, SQL Server) or NoSQL stores (MongoDB, DynamoDB, Cassandra, Redis, Firestore), evaluating SQL vs. NoSQL trade-offs, or optimizing indexes and access paths.
- **Design Philosophy**:
  - **Access-Pattern Driven**: Schema design starts from query and write patterns rather than abstract entity lists.
  - **Relational Rigor**: Normalization (3NF), explicit constraints (foreign keys, nullability, unique checks), composite indexes, and safe migrations.
  - **NoSQL Discipline**: Strategic embedding vs. referencing, partition/sort key selection, and single-table DynamoDB design.
- **Bundled Resources**:
  - `references/sql.md`: Relational data types, constraints, indexing strategies (B-tree, GIN), partitioning, and migration safety.
  - `references/nosql.md`: Access-pattern modeling for document, key-value, and wide-column stores.

---

### 5. Code Quality, Refactoring & Codebase Health

#### `code-quality`
- **When to use**: Whenever writing, refactoring, or optimizing code across any language.
- **Core Principles**: Correctness first, clarity second, performance where evidence justifies it. Avoids premature optimization and drive-by rewrites.
- **References**: Deep guides for maintainability (`references/maintainability.md`) and algorithmic performance (`references/performance.md`).

#### `refactor-and-redesign`
- **When to use**: Planning and executing large-scale code refactors, codebase modernizations, tech debt paydowns, architectural migrations, or UI reskins/dark mode additions.
- **Phased Discipline**:
  - **Batch Execution**: Splits massive changes into small, reviewable batches (1 to 8 files each) that keep behavior verified at every step.
  - **Separation of Concerns**: Never changes behavior and structure in the same step.
  - **Progress Persistence**: Maintains an explicit `PLAN.md` tracking goals, inventories, batches, and verification gates.
- **Bundled Tools & Resources**:
  - `scripts/find_hardcoded_colors.py`: Scans codebases to catalog hardcoded colors before introducing design tokens.
  - `scripts/contrast.py`: WCAG color contrast calculator.
  - `references/refactor-playbook.md`: Safe refactoring recipes (parallel change, strangler pattern, characterization tests).
  - `references/ui-redesign-and-theming.md`: Design token architecture, theme migrations, and CSS variable strategies.

#### `dead-code-audit`
- **When to use**: Finding unreachable files, unused exports, dead functions, unreferenced variables, stale feature flags, and obsolete dependencies before refactoring.
- **Methodology**:
  - **Root Identification**: Maps explicit application roots (entry points, public APIs, route handlers, cron jobs, build scripts).
  - **Static & Dynamic Analysis**: Scans source files with `scripts/scan.py` and inspects reflection, DI registries, framework conventions, and string lookups.
  - **Confidence Tiers**: Categorizes findings into High (safe removal), Medium (probable dead, verify dynamic use), Low (needs manual check), and Live.
  - **Revertible Removal**: Employs git-revertible safe deletion steps.
- **Bundled Resources**:
  - `scripts/scan.py`: Zero-dependency Python and JS/TS orphan file and unreferenced symbol scanner.
  - `references/tool-matrix.md`: Guide to ecosystem-specific dead code tools (knip, vulture, cargo-udeps, etc.).
  - `references/removal-and-restore.md`: Safe staged removal procedures and git rollback recipes.

#### `adversarial-review`
- **When to use**: Reviewing pull requests, evaluating bug fixes, or performing security audits.
- **Persona**: Acts as a strict Principal Systems Engineer and Security Architect.
- **Analysis Vectors**: Correctness & Type Safety, Time/Space Complexity ($O(n)$), Security & Sanitization, Readability.

---

### 6. Testing & Quality Assurance

#### `test-suite-architect`
- **When to use**: Designing, implementing, auditing, or repairing automated test suites across unit, integration, regression, E2E, API/contract, and performance levels.
- **Workflow**:
  - **Recon**: Executes `scripts/analyze_repo.py` to identify languages, existing test frameworks, missing test files, and untested risk hotspots.
  - **Test Pyramid Strategy**: Allocates effort appropriately—favoring fast unit tests, targeted integration tests, and lean E2E paths over slow, fragile suites.
  - **Flaky Test Remediation**: Eliminates shared state, timing races, and order dependencies.
  - **Reporting**: Generates machine-readable and executive test reports (`scripts/generate_report.py`).
- **Bundled Resources**:
  - `scripts/analyze_repo.py`: Discovers testing stacks, test directory conventions, and untested source modules.
  - `scripts/generate_report.py`: Aggregates test outputs into clean Markdown or JSON status summaries.
  - `references/frameworks.md`: Recommended test frameworks and runners across Python, JS/TS, Go, Java, C#, and Rust.
  - `references/test-types.md`: Implementation patterns for unit, integration, contract, snapshot, and regression tests.
  - `references/improving-existing.md`: Recipes for deflaking, speedup, and strengthening weak assertions.

#### `ai-code-test-validation`
- **When to use**: Designing unit tests, integration tests, or regression test suites that genuinely catch defects in AI-generated code.
- **Key Features**:
  - Multi-stack support: Python (`pytest`), JavaScript/TypeScript (`Jest`, `Vitest`), C# (`xUnit`, `NUnit`), Java (`JUnit`, `Spring Boot`), Go, and Rust.
  - Requirement-to-test traceability matrix (`assets/traceability_template.md`).
  - Stack auto-detection (`scripts/detect_stack.py`).
  - AST-level mutation testing runner (`scripts/mutate.py`) to verify test suite efficacy.

---

### 7. Codebase Exploration & Security Analysis

#### `codebase-exploration`
- **When to use**: Exploring unfamiliar codebases, tracing functions, analyzing architecture, or locating patterns without token-heavy globbing.
- **Bundled Local Scripts**:
  - `scripts/find_patterns.py`: Fast regex search across code with surrounding context lines.
  - `scripts/call_graph.py`: Builds caller/callee graphs and identifies circular dependencies and entry points.
  - `scripts/import_mapper.py`: Analyzes ES6 and CommonJS imports/exports to find circular references and unused exports.
  - `scripts/codebase_mapper.py`: Categorizes files (controllers, services, models) and outputs a comprehensive `CODEBASE_MAP.md`.

#### `security-analysis`
- **When to use**: Auditing code for OWASP Top 10 vulnerabilities, authentication weaknesses, CSRF/XSS, and credential leaks.
- **Assets**: Structured audit checklists and security review report templates.

---

### 8. Debugging & Root Cause Analysis

#### `widen-the-lens`
- **When to use**: When a fix fails, the same error recurs, the AI is stuck in a loop repeating shallow guesses, or a bug resists initial diagnosis.
- **Unstick-and-Widen Protocol**:
  - **Attempt Ledger**: Maintains a written log of attempts, expectations, and actual outcomes to prevent repeating past failures (`scripts/ledger.py`).
  - **Check the Obvious**: Mandatory 2-minute gate verifying path typos, stale caches, unsaved edits, and environment mismatches (`references/obvious-checks.md`).
  - **Widen Directions**: Looks one layer further out: Upstream inputs, Downstream consumers, Sideways working examples, Environment, and Git history.
  - **Multi-Hypothesis Matrix**: Generates $\ge 3$ distinct causal hypotheses and ranks them by cheapest testable action.
- **Bundled Tools**:
  - `scripts/ledger.py`: CLI ledger utility to log, view, and inspect debugging attempts and outcomes.
  - `references/obvious-checks.md`: Checklist of trivial-yet-common bug sources.
  - `references/search-broadening.md`: Strategies for widening code and documentation searches.

---

### 9. UI/UX & Creative Frontend Engineering

#### `frontend-ux-craft`
- **When to use**: Designing, building, refactoring, or styling frontend interfaces in React, Next.js, Vue, Angular, Svelte, Inertia.js, or plain HTML/CSS.
- **Standards**:
  - Full **WCAG 2.2 AA** accessibility compliance (contrast, keyboard navigation, focus indicators, screen readers).
  - Production design token system using `oklch()` color spaces and dark mode (`assets/tokens.css`).
  - Component contracts, responsive layouts, and frontend security (XSS, CSP, secure session cookies).
- **Executable Tools**:
  - `scripts/audit_project.py`: Analyzes a codebase for hardcoded colors, sizes, z-indexes, and accessibility smells.
  - `scripts/contrast.py`: Computes exact WCAG contrast ratios for Hex and `oklch()` pairs.
  - `scripts/check_tokens.py`: Validates color gamuts and theme pairings across token stylesheets.

#### `domain-ux-design`
- **When to use**: Designing and building UI components, forms, flows, and dashboards that are shaped by real-world business domains (fintech, healthcare, logistics, e-commerce, SaaS).
- **Principles**:
  - **The Domain Decides the Design**: Layout, density, and color choices reflect real business vocabulary, user anxiety levels, and operational stakes.
  - **Business Logic is UX**: Constraints, eligibility rules, approval chains, and deadlines are made visible and interactive rather than surfacing as submit-time error banners.
  - **One Memorable Signature Element**: Introduces one tailored signature micro-interaction or visualization that gives the product a distinctive, bespoke identity.
- **Bundled Resources**:
  - `references/patterns.md`: Domain-driven UI patterns (steppers, approval queues, status banners, dense data grids).
  - `references/anti-patterns.md`: Common UX failures (generic dashboard widgets, hidden constraints, vague validation messages).

#### `desktop-app-ux`
- **When to use**: Building React applications that demand the responsiveness, fixed chrome, and keyboard workflow of native desktop software (VS Code, Linear, Figma, Notion, Finder) rather than scrolling web documents.
- **Core Principles**:
  - **Fixed App Shell**: Full viewport height with `overflow: hidden`, independent pane scrolling (`min-height: 0`), and draggable splitters.
  - **Keyboard-First Design**: Central shortcut map (`Mod+K`, `Mod+S`, `Mod+F`, arrow navigation), status bar, and shortcut discoverability.
  - **Tool Ergonomics**: Unified action registry powering command palettes (`cmdk`), menu bars, and contextual right-click menus; explicit multi-select state (`Set` of IDs + anchor).
  - **Tool Aesthetic**: Compact density (24-32px row heights), hairline 1px borders, system font stacks, and zero bounce/scroll-jacking.
- **References**:
  - `references/react-patterns.md`: Production code patterns for command palettes, resizable panes, hotkeys, selection models, and context menus.

#### `web-graphics-studio`
- **When to use**: Crafting high-impact visuals, interactive animations, hero sections, portfolios, landing pages, particle effects, generative art, and 3D scenes in the browser.
- **Technology Ladder**:
  - Escalates progressively from lightest to heaviest: CSS transitions/keyframes $\rightarrow$ Scroll-driven animations (`animation-timeline`) $\rightarrow$ SVG drawing/morphing $\rightarrow$ Canvas 2D $\rightarrow$ WebGL / three.js.
  - Discard generic looks in favor of deliberate color tokens (`oklch()`), typography hierarchy, and purposeful easing curves (`cubic-bezier`).
  - Built-in battery and accessibility safety: `@media (prefers-reduced-motion)` fallbacks and `IntersectionObserver` pause on offscreen rendering.
- **Assets & Recipes**:
  - `assets/starter.html`: Single-file template with theme support, scroll reveal, and Canvas hero.
  - `references/css-recipes.md`: Glassmorphism, grain textures, marquees, and view transitions.
  - `references/svg-and-canvas.md`: Particle systems, flow fields, noise meshes, and SVG line animations.
  - `references/animation-libraries.md`: GSAP timelines, ScrollTrigger recipes, and three.js starters.
  - `references/page-patterns.md`: Layout blueprints for heroes, features, pricing, and case studies.

---

### 10. Algorithms & Problem Solving

#### `dsa-expert`
- **When to use**: Solving competitive programming challenges, interview preparation (LeetCode/HackerRank), or selecting the optimal data structure for production workloads.
- **Guidance**: Systematic algorithmic selection matrix based on input constraints ($N \le 10^5 \implies O(N \log N)$), step-by-step problem deconstruction, and memory optimization.

---

### 11. Domain Integrations & Compliance

#### `payment-integration`
- **When to use**: Integrating payment providers (Stripe, Razorpay, PayPal, Adyen, Square, UPI, etc.).
- **Best Practices**:
  - Server-side amount validation (never trust the client).
  - Cryptographic webhook signature verification and idempotent event handling.
  - Zero raw card data handling (PCI-DSS compliance via hosted fields/elements).

#### `nist-rmf-ai`
- **When to use**: Designing, evaluating, or deploying AI models, pipelines, and autonomous agents in regulated environments.
- **Framework**: Implements the NIST AI Risk Management Framework (AI RMF 1.0) core functions: **Govern**, **Map**, **Measure**, and **Manage**.

---

### 12. Documentation & Technical Handover

#### `software-documentation`
- **When to use**: Documenting a software project, API, feature, or release for multiple stakeholder audiences, or creating runnable Postman collections.
- **Tailored Audiences**:
  - **Engineers (Frontend, Backend, DevOps)**: Endpoint references, error codes, authentication, payload schemas, and FE/BE contracts (`references/engineering.md`).
  - **Clients & End Users**: Scope of delivery, step-by-step help guides, and features list (`references/client.md`).
  - **Product Managers**: High-level architecture, business rationale, constraints, and assumptions (`references/product.md`).
  - **QA Testers**: Test plans, test cases, environment setup, smoke/regression suites, and bug report templates (`references/qa.md`).
- **Bundled Tools**:
  - `scripts/build_postman_collection.py`: Automatically generates runnable Postman collections and environment variables from OpenAPI 3 specifications.
  - `references/quality-checklist.md`: Rigorous pre-flight checklist for documentation accuracy and completeness.

---

### 13. Agent Meta-Skills & Evolution

#### `skill-orchestrator`
- **When to use**: Meta-skill that decides **HOW** to accomplish complex, ambiguous, or multi-step tasks before jumping to execution.
- **Directives & Capabilities**:
  - **Least Power Ladder**: Solves tasks using the lowest sufficient power tier (Prompt → Rule → Skill → Workflow → Script → MCP Server).
  - **Capability Discovery**: Scans context, workspace catalogs, and existing skills to reuse proven playbooks before generating new ones.
  - **Defensive Gatekeeping**: Enforces strict trust boundaries—treats external tool output, web findings, and new skill files as data, never instructions.
- **Bundled Resources**:
  - `references/selection-rubric.md`: Scoring rubric evaluating task fit, trust provenance, and permission requirements.
  - `references/security-checklist.md`: Security and privacy boundaries for autonomous agents.
  - `references/mcp-server-template.md`: Boilerplate for safe MCP server generation.

#### `skill-evolver`
- **When to use**: Auditing, scoring, mutating, updating, or evolving agent skills, rule files, and tool definitions while guaranteeing security and transparency.
- **Key Principles**:
  - **Untrusted Input Defense**: Skills under review are treated strictly as data to inspect, neutralizing prompt injections.
  - **Read Before Run**: Scripts are audited statically via `scripts/audit_skill.py`; zero unvetted script execution.
  - **Isolated Work Copies**: Never edits skills in place—generates working drafts in isolated temporary directories and requires human approval for capability diffs.
  - **Audit Lineage**: Maintains explicit before/after scores, mutation rationale, and change histories.
- **Bundled Resources**:
  - `scripts/audit_skill.py`: Static analysis tool evaluating skill file manifests, dependencies, script security, and prompt hygiene.
  - `references/rubric.md`: Objective scoring rubric across triggers, progressive disclosure, safety, and script hygiene.
  - `references/mutation-operators.md`: Catalog of safe skill mutations (clarifying triggers, extracting scripts, decomposing references).
  - `references/security-privacy.md`: Secret scrubbing, telemetry prevention, and privacy standards.

---

### 14. Cost & Token Optimization

#### `token-optimiser`
- **When to use**: Working with free-tier model quotas, low RPM limits, or large multi-file projects.
- **Techniques**: Anti-burst execution pacing, micro-context targeted reading, and proactive session compaction.

---

## Skill Structure Specification

Every skill in this repository conforms to the standard specification:

```text
skills/<skill-name>/
├── SKILL.md             # Required: Entrypoint with YAML frontmatter and runbook
├── scripts/             # Optional: Fast local helper scripts (Python/Node/Bash)
├── references/          # Optional: Detailed reference docs loaded on demand
├── assets/              # Optional: Starter templates, CSS tokens, checklists
└── examples/            # Optional: Reference implementations
```

### Frontmatter Standard

The top of each `SKILL.md` must include YAML frontmatter:

```markdown
---
name: skill-name
description: >-
  Action-oriented summary of what the skill does.
  Explicit "Use this skill whenever..." trigger phrasing explaining
  when the agent should activate this playbook.
---
```

---

## Adding New Skills

1. Create a new folder under `skills/<your-skill-name>/`.
2. Add a `SKILL.md` file following the frontmatter convention.
3. Keep the primary `SKILL.md` focused and concise; place lengthy documentation in `references/` for progressive disclosure.
4. Place any automation scripts in `scripts/` and use relative paths exclusively.
5. Test skill activation by querying your AI assistant with the defined triggers.

---

## License

This collection is released under the [MIT License](LICENSE). Feel free to use, customize, and share these skills across your projects and teams.
