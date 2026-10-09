---
name: architecture-diagrams
description: Draft software architecture diagrams for documentation using Mermaid, following the C4 model (system context, container, component) plus UML (sequence, class, state, ER) for behaviour and detail. Use this skill whenever the user wants to diagram, visualize, document, or explain a software system, service, API, data flow, deployment, microservices layout, or integration, even if they only say "draw how X works", "add a diagram to the README/design doc/ADR", or "show how these services talk". Produces diagrams readable by both engineers and non-technical stakeholders, with syntax kept simple enough to render reliably in GitHub, GitLab, Notion, Confluence, and MkDocs.
---

# Architecture Diagrams (Mermaid + C4 + UML)

Draft clear, correct, renderable architecture diagrams for documentation. The audience is mixed: engineers need accuracy, non-technical stakeholders need to grasp the picture in under a minute. Every choice below serves both.

## Core principles

1. **One diagram, one question.** Each diagram answers a single question ("What does the system touch?", "What is it made of?", "What happens when a user checks out?"). Split rather than cram.
2. **Zoom levels, not detail dumps.** Use C4 levels so readers can zoom in progressively. Never mix levels in one diagram.
3. **Plain language first.** Label boxes with what they *do* ("Order Service"), then the technology in small text ("Spring Boot"). A non-technical reader should understand the diagram from names and descriptions alone.
4. **Never invent facts silently.** If the user did not tell you something (a database, a queue, a protocol), either ask or include it and list it under "Assumptions" in the output. Wrong diagrams are worse than no diagrams.
5. **Simple Mermaid only.** This skill must produce syntax that works across Mermaid versions and when written by any capable model. Follow `references/mermaid-pitfalls.md` strictly. Do not use native `C4Context`/`C4Container` blocks, `architecture-beta`, icons, `click` handlers, custom themes, or `%%{init}%%` directives unless the user explicitly asks.

## Workflow

### Step 1: Understand the system

Collect, from the conversation, uploaded files, or code the user shares:

- **Purpose**: one sentence on what the system is for and who uses it.
- **People** (actors/roles) and **external systems** (payment provider, email service, identity provider).
- **Containers**: separately running/deployable things (web app, API, worker, database, queue, cache). A container is *not* a Docker container specifically.
- **Key interactions**: who calls whom, over what protocol, synchronously or asynchronously.
- **Key flows** worth showing step by step (login, checkout, ingest pipeline).

If the user supplies code, configs, docker-compose, Terraform, or Kubernetes manifests, derive the inventory from them and say so. If information is thin, do **not** interrogate the user at length. Ask at most one or two questions, or proceed with clearly labelled assumptions.

### Step 2: Pick the right diagram

| User wants to show | Diagram | Mermaid type | Reference |
|---|---|---|---|
| The system, its users, and external dependencies | C4 Level 1: System Context | `flowchart` | `references/c4-in-mermaid.md` |
| Deployable parts and how they communicate | C4 Level 2: Container | `flowchart` | `references/c4-in-mermaid.md` |
| Internals of one container | C4 Level 3: Component | `flowchart` | `references/c4-in-mermaid.md` |
| Step-by-step runtime behaviour, API calls, auth flows | UML Sequence | `sequenceDiagram` | `references/uml-in-mermaid.md` |
| Domain model or code structure of one component | UML Class (C4 Level 4) | `classDiagram` | `references/uml-in-mermaid.md` |
| Lifecycle of an entity (order, job, ticket) | UML State | `stateDiagram-v2` | `references/uml-in-mermaid.md` |
| Database tables and relationships | ER | `erDiagram` | `references/uml-in-mermaid.md` |
| Where things run (cloud, regions, clusters, networks) | Deployment | `flowchart` with nested subgraphs | `references/c4-in-mermaid.md` |

Default when the request is vague ("diagram my system"): produce **Level 1 and Level 2** together. That pair covers most documentation needs. Offer a sequence diagram for the single most important flow.

Read the matching reference file before writing the diagram. It contains copy-ready templates, and `assets/example-food-delivery.md` shows a full delivered answer.

### Step 3: Write an element inventory first

Before any Mermaid, list every element in a short table. This prevents missing, duplicated, or unlabeled nodes and is the best defense against errors.

```
| ID        | Name              | Kind            | Technology     | Description (plain language)        |
|-----------|-------------------|-----------------|----------------|-------------------------------------|
| customer  | Customer          | Person          |                | Buys products online                |
| webApp    | Web Storefront    | Container       | React          | Lets customers browse and order     |
| orderApi  | Order API         | Container       | Node.js        | Handles orders and payments         |
| orderDb   | Order Database    | Container (DB)  | PostgreSQL     | Stores orders and customer records  |
| stripe    | Stripe            | External system |                | Processes card payments             |
```

Include this table in the response only when it helps the reader or the user asked for it. Always build it mentally or in your reasoning. Keep ≤ 12 nodes per diagram (≤ 8 is better for non-technical readers). If you exceed that, split into more focused diagrams or group elements.

### Step 4: Draft the diagram

Apply the templates from the reference files, then these rules:

- **IDs**: camelCase letters and digits only, starting with a letter (`orderApi`, not `order-api` or `Order API`). Never use reserved words: `end`, `graph`, `subgraph`, `style`, `class`, `default`, `click`.
- **Labels**: always wrap in double quotes. Use `<br/>` for line breaks, never `\n`. Avoid double quotes, parentheses, and special characters inside labels. Use words instead.
- **Direction**: `flowchart LR` for context/container diagrams (reads like a sentence); `flowchart TB` for layered or deployment views.
- **Edges**: every arrow gets a label with a short verb phrase, plus the protocol when relevant (`"Places orders<br/>HTTPS"`). Unlabeled arrows are the top cause of confusing diagrams.
- **Arrow style**: solid `-->` for synchronous calls, dotted `-.->` for asynchronous/events. Say so in the legend.
- **Boundaries**: use `subgraph` with a quoted title for the system boundary or deployment zones. Keep nesting ≤ 2 levels.
- **Styling**: use the shared `classDef` palette from `references/c4-in-mermaid.md` so all diagrams in a document look consistent. Define classDefs at the bottom, apply with `class id1,id2 className`, and give every boundary `subgraph` the dashed-outline `style` line from the palette.
- **Dependencies**: arrows point in the direction of the *call/dependency* (client to server), not the data return.

### Step 5: Self-check, then lint

Run through this checklist before delivering:

- [ ] Diagram has a single level of abstraction and answers one question
- [ ] Every node has a plain-language name; containers show technology
- [ ] Every arrow has a label
- [ ] All IDs are simple and unique; no reserved words
- [ ] All labels are in double quotes; no `\n`; no stray parentheses
- [ ] Every `subgraph` has a matching `end`
- [ ] ≤ 12 nodes (≤ 8 for exec-facing diagrams)
- [ ] Nothing included that the user didn't provide, unless listed under Assumptions

Then, if a shell is available, validate with the bundled linter:

```bash
python scripts/lint_mermaid.py path/to/file.md      # checks every ```mermaid block
python scripts/lint_mermaid.py --render diagram.mmd # also tries mmdc if installed
```

Fix everything it reports and re-run until clean. If no shell is available, walk through `references/mermaid-pitfalls.md` manually.

### Step 6: Deliver in documentation-ready form

For each diagram, deliver this block (adapt headings to the user's doc style):

````markdown
### <Diagram title>: <C4 level or UML type>

**Purpose:** One sentence on what question this answers and for whom.

```mermaid
<diagram>
```

**How to read it:** 2 to 4 sentences in plain language: what the main flow is, what to notice.

**Legend:** (only if styles or arrow types need explaining)
- Blue box = our system · Grey box = external system · Dashed arrow = asynchronous

**Assumptions / open questions:** (only if any)
- ...
````

Delivery format:
- **In the chat reply** by default, as fenced `mermaid` code blocks the user can paste into their docs.
- **As a `.md` file** if the user asks for a document, wants several diagrams, or is writing an architecture doc / ADR. Use `assets/architecture-doc-template.md` as the skeleton.
- **As rendered PNG/SVG** only if the user asks for images and `mmdc` is available (`mmdc -i in.mmd -o out.svg`). Mention that the Mermaid source is the thing to keep in version control.

Offer one natural next step at the end (for example "Want a sequence diagram for the checkout flow?"), not a menu.

## Handling common situations

- **User pastes code or infra files**: infer containers from entry points, services, datastores, and queues; infer relationships from imports, HTTP clients, env vars, and connection strings. State what you inferred.
- **User asks to update an existing diagram**: keep their IDs, names, and layout direction; change only what was requested; show the full updated block.
- **User asks for "UML" generically**: ask which view they mean only if it cannot be inferred. Otherwise default to sequence for behaviour and class for structure.
- **Very large system**: produce a Level 1, a Level 2, then separate Level 3 diagrams per important container. Never one giant diagram.
- **Non-technical audience (executives, clients)**: stay at Level 1 or 2, drop protocols and technology from labels, use business verbs ("Sends invoices"), and keep ≤ 8 nodes.
- **Security or compliance docs**: add trust boundaries as subgraphs and label data sensitivity on arrows (for example "Card data, encrypted").
- **User wants a different tool** (PlantUML, draw.io, Structurizr): the element inventory transfers directly. Build it, then translate, and say Mermaid was the default.

## Files in this skill

- `references/c4-in-mermaid.md`: templates for C4 levels 1 to 3 and deployment views, with shared styling
- `references/uml-in-mermaid.md`: templates for sequence, class, state, and ER diagrams
- `references/mermaid-pitfalls.md`: the syntax errors that break rendering, and their fixes. Read this if anything fails to render
- `scripts/lint_mermaid.py`: static checker for Mermaid blocks (optionally renders via `mmdc`)
- `assets/architecture-doc-template.md`: skeleton for a full architecture document
- `assets/example-food-delivery.md`: a complete worked example (Level 1, Level 2, sequence) showing the expected quality and format. Read it first if unsure what a good answer looks like
