# Agent Skills Library

A curated, battle-tested collection of modular **skills, runbooks, and executable toolkits** designed for agentic AI coding assistants—including **Google Antigravity (AGY)**, **Gemini CLI**, **Claude Code**, and coding agents implementing the `.agents/skills` customization protocol.

Each skill acts as a specialized playbook that equips the AI agent with domain expertise, proven engineering workflows, decision trees, and local automation scripts—without needing external containers or heavyweight dependencies.

---

## Table of Contents

- [Overview](#overview)
- [How Skills Work](#how-skills-work)
- [Installation & Setup](#installation--setup)
- [Skills Catalog](#skills-catalog)
  - [Planning & Architecture](#1-planning--architecture)
  - [Code Quality & Review](#2-code-quality--review)
  - [Testing & Quality Assurance](#3-testing--quality-assurance)
  - [Codebase Exploration & Analysis](#4-codebase-exploration--analysis)
  - [UI/UX & Frontend Engineering](#5-uiux--frontend-engineering)
  - [Algorithms & Problem Solving](#6-algorithms--problem-solving)
  - [Domain Integrations & Compliance](#7-domain-integrations--compliance)
  - [Cost & Token Optimization](#8-cost--token-optimization)
- [Skill Structure Specification](#skill-structure-specification)
- [Adding New Skills](#adding-new-skills)
- [License](#license)

---

## Overview

Modern AI coding agents excel when guided by clear protocols and targeted domain knowledge rather than generic prompts. This repository packages production-grade software engineering practices into modular directories:

- **Token Efficient**: Uses progressive disclosure—agents load only the frontmatter index initially, reading detailed instructions and reference manuals only when relevant.
- **Runnable Local Tools**: Ships with fast, zero-dependency Python utilities for tasks like dependency analysis, AST pattern matching, WCAG contrast verification, and mutation testing.
- **Portable & Isolated**: All script and asset paths are self-contained and relative to each skill directory.

---

## How Skills Work

Skills leverage **Progressive Disclosure** to maintain a lean context window:

1. **Discovery**: On startup, the agent indexes the `name` and `description` frontmatter from every `SKILL.md`.
2. **Triggering**: When user requests match the skill's triggers or domain (e.g., "audit accessibility", "generate call graph", "write unit tests"), the agent activates the skill.
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
│       ├── codebase-exploration/
│       ├── frontend-ux-craft/
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

| Skill | Purpose | Key Tools / Resources |
|---|---|---|
| [`autonomous-planner`](#autonomous-planner) | Turns vague briefs into approved Markdown execution plans (`PLAN.md`) before coding | Step-by-step interview, plan templates |
| [`specification-planning`](#specification-planning) | Systemic architectural discovery and interface mapping before refactors | Interface discovery protocol |
| [`code-quality`](#code-quality) | Writing and refactoring clean, maintainable, and sensibly performant code | `references/maintainability.md`, `references/performance.md` |
| [`adversial-review`](#adversial-review) | Strict Principal Engineer & Security Architect code review | Correctness, complexity, security vectors |
| [`coding-expert`](#coding-expert) | Pragmatic, low-overhead code generation tuned for cost/context efficiency | Architecture preservation rules |
| [`ai-code-test-validation`](#ai-code-test-validation) | Requirement-driven unit/regression tests with mutation verification | Stack detector, AST mutation runner (`scripts/`) |
| [`codebase-exploration`](#codebase-exploration) | High-speed regex pattern search, import/dependency mapping, call graphs | `find_patterns.py`, `call_graph.py`, `import_mapper.py`, `codebase_mapper.py` |
| [`security-analysis`](#security-analysis) | OWASP vulnerability detection, threat modeling, and input validation | Security checklists and reporting templates |
| [`frontend-ux-craft`](#frontend-ux-craft) | Senior UI/UX engineering, WCAG 2.2 AA accessibility, design tokens, security | `tokens.css`, `audit_project.py`, `contrast.py`, `check_tokens.py` |
| [`dsa-expert`](#dsa-expert) | Algorithm selection, Big-O analysis, LeetCode/DSA problem solving | Decision matrix, patterns catalog |
| [`payment-integration`](#payment-integration) | Payment gateways (Stripe, Razorpay, PayPal, UPI) with safe webhook verification | Plan template, security checklist |
| [`nist-rmf-ai`](#nist-rmf-ai) | NIST AI Risk Management Framework (Govern, Map, Measure, Manage) compliance | 7 AI trustworthiness pillars |
| [`token-optimiser`](#token-optimiser) | Anti-burst request pacing and context compaction for free-tier models | Throttling rules, context strategies |

---

### 1. Planning & Architecture

#### `autonomous-planner`
- **When to use**: When starting any non-trivial feature, complex bug fix, or greenfield project where coding without a plan is risky.
- **Workflow**: Clarifies underspecified requirements, conducts targeted web research, coordinates with other skills, and outputs a clear, step-by-step `PLAN.md` with verification criteria.
- **Example triggers**: `"plan this feature"`, `"create a spec"`, `"how should we build this"`, `"write a design doc"`.

#### `specification-planning`
- **When to use**: When initiating complex refactors or component redesigns.
- **Workflow**: Enforces a strict pause before touching code: maps existing dependencies, defines explicit interfaces and data types, and traces side effects.

---

### 2. Code Quality & Review

#### `code-quality`
- **When to use**: Whenever writing, refactoring, or optimizing code across any language.
- **Core Principles**: Correctness first, clarity second, performance where evidence justifies it. Avoids premature optimization and drive-by rewrites.
- **References**: Deep guides for maintainability (`references/maintainability.md`) and algorithmic performance (`references/performance.md`).

#### `adversial-review`
- **When to use**: Reviewing pull requests, evaluating bug fixes, or performing security audits.
- **Persona**: Acts as a strict Principal Systems Engineer and Security Architect.
- **Analysis Vectors**: Correctness & Type Safety, Time/Space Complexity ($O(n)$), Security & Sanitization, Readability.

#### `coding-expert`
- **When to use**: Optimized for smaller models or constrained token budgets.
- **Focus**: Produces surgical, working code with minimal diffs, avoiding unnecessary dependencies, verbose explanations, or stylistic churn.

---

### 3. Testing & Quality Assurance

#### `ai-code-test-validation`
- **When to use**: Designing unit tests, integration tests, or regression test suites that genuinely catch defects in AI-generated code.
- **Key Features**:
  - Multi-stack support: Python (`pytest`), JavaScript/TypeScript (`Jest`, `Vitest`), C# (`xUnit`, `NUnit`), Java (`JUnit`, `Spring Boot`), Go, and Rust.
  - Requirement-to-test traceability matrix (`assets/traceability_template.md`).
  - Stack auto-detection (`scripts/detect_stack.py`).
  - AST-level mutation testing runner (`scripts/mutate.py`) to verify test suite efficacy.

---

### 4. Codebase Exploration & Analysis

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

### 5. UI/UX & Frontend Engineering

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

---

### 6. Algorithms & Problem Solving

#### `dsa-expert`
- **When to use**: Solving competitive programming challenges, interview preparation (LeetCode/HackerRank), or selecting the optimal data structure for production workloads.
- **Guidance**: Systematic algorithmic selection matrix based on input constraints ($N \le 10^5 \implies O(N \log N)$), step-by-step problem deconstruction, and memory optimization.

---

### 7. Domain Integrations & Compliance

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

### 8. Cost & Token Optimization

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
