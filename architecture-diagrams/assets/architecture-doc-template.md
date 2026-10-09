# <System Name>: Architecture Overview

> **Status:** Draft · **Owner:** <team or person> · **Last updated:** <date>

## 1. Summary

<Two or three sentences in plain language: what the system does, who uses it, and why it exists. A non-technical reader should be able to stop here and understand the system.>

## 2. System Context (C4 Level 1)

**Purpose:** Shows who uses the system and which external systems it depends on.

```mermaid
<level 1 flowchart: see references/c4-in-mermaid.md>
```

**How to read it:** <2 to 4 sentences.>

## 3. Containers (C4 Level 2)

**Purpose:** Shows the deployable parts of the system and how they communicate.

```mermaid
<level 2 flowchart>
```

**How to read it:** <2 to 4 sentences.>

| Container | Technology | Responsibility |
|---|---|---|
| <name> | <tech> | <plain-language responsibility> |

## 4. Key Flows

### 4.1 <Flow name, for example "Customer places an order">

```mermaid
<sequenceDiagram>
```

**Notes:** <failure handling, retries, timeouts, anything not obvious from the diagram.>

## 5. Components (C4 Level 3, optional)

<One subsection per container worth zooming into. Skip containers that are simple.>

## 6. Data Model (optional)

```mermaid
<erDiagram or classDiagram>
```

## 7. Deployment (optional)

```mermaid
<deployment flowchart>
```

## 8. Legend

- Dark blue = person · Blue = our system · Light blue = parts inside it · Grey = external system
- Solid arrow = synchronous call · Dashed arrow = asynchronous message or event

## 9. Assumptions and Open Questions

- <Anything inferred rather than confirmed. Each item should be resolvable by a named person.>

## 10. Related Documents

- <ADRs, runbooks, API specs>
