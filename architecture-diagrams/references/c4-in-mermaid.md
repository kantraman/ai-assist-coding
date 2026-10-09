# C4 Diagrams in Mermaid (flowchart-based)

Mermaid has native `C4Context` / `C4Container` blocks, but they are experimental, have weak layout control, and are frequently written incorrectly by LLMs. This skill uses plain `flowchart` with consistent styling instead. It renders identically on GitHub, GitLab, Notion, Confluence plugins, and MkDocs.

## Contents
1. Shared palette (paste at the bottom of every C4 diagram)
2. Node shape conventions
3. Level 1: System Context
4. Level 2: Container
5. Level 3: Component
6. Deployment view
7. Label formula

---

## 1. Shared palette

Paste only the classes you use, at the **bottom** of the diagram:

```
    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    classDef system fill:#1168bd,stroke:#0b4884,color:#ffffff
    classDef container fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef component fill:#85bbf0,stroke:#5d82a8,color:#000000
    classDef database fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff
```

Style every system/deployment boundary (`subgraph`) with a dashed outline and no fill, using the subgraph's id:

```
    style shop fill:none,stroke:#1168bd,stroke-width:2px,stroke-dasharray:6 4,color:#1168bd
```

Meaning (put in the Legend when the audience is non-technical):
- Dark blue = person/user
- Blue = the system being documented
- Lighter blue = parts inside it (containers, components)
- Grey = external systems we do not own

## 2. Node shape conventions

| Element | Shape syntax | Class |
|---|---|---|
| Person | `id(["..."])` stadium | `person` |
| Our system (Level 1) | `id["..."]` rectangle | `system` |
| Container / component | `id["..."]` rectangle | `container` / `component` |
| Database / datastore | `id[("...")]` cylinder | `database` |
| Queue / event bus | `id[["..."]]` subroutine | `container` |
| External system | `id["..."]` rectangle | `external` |

## 3. Level 1: System Context

Question answered: *What is this system, who uses it, and what does it depend on?* Audience: everyone. No internal parts, no technology.

```mermaid
flowchart LR
    customer(["<b>Customer</b><br/>Buys products online"])
    support(["<b>Support Agent</b><br/>Handles customer issues"])

    shop["<b>Online Shop</b><br/>Lets customers browse,<br/>order, and track products"]

    payments["<b>Payment Provider</b><br/>Processes card payments"]
    email["<b>Email Service</b><br/>Sends order emails"]

    customer -->|"Browses and orders"| shop
    support -->|"Manages orders"| shop
    shop -->|"Takes payments"| payments
    shop -->|"Sends notifications"| email
    email -.->|"Delivers emails"| customer

    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    classDef system fill:#1168bd,stroke:#0b4884,color:#ffffff
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff
    class customer,support person
    class shop system
    class payments,email external
```

Rules: exactly one `system` node (the thing being documented). Everything else is a person or an external system. ≤ 8 nodes total.

## 4. Level 2: Container

Question answered: *What is the system made of, and how do the parts talk?* Audience: engineers plus curious stakeholders. Show the system boundary as a subgraph; people and external systems sit outside it.

```mermaid
flowchart LR
    customer(["<b>Customer</b>"])
    payments["<b>Payment Provider</b><br/>[External]"]

    subgraph shop ["Online Shop"]
        web["<b>Web Storefront</b><br/>[React]<br/>Browse and order"]
        api["<b>Order API</b><br/>[Node.js]<br/>Orders and payments logic"]
        worker["<b>Email Worker</b><br/>[Python]<br/>Sends order emails"]
        queue[["<b>Message Queue</b><br/>[RabbitMQ]<br/>Order events"]]
        db[("<b>Order Database</b><br/>[PostgreSQL]<br/>Orders and customers")]
    end

    customer -->|"Uses<br/>HTTPS"| web
    web -->|"Calls<br/>JSON/HTTPS"| api
    api -->|"Reads and writes<br/>SQL"| db
    api -->|"Charges cards<br/>HTTPS"| payments
    api -.->|"Publishes order events"| queue
    queue -.->|"Delivers events"| worker

    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    classDef container fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef database fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff
    class customer person
    class web,api,worker,queue container
    class db database
    class payments external
    style shop fill:none,stroke:#1168bd,stroke-width:2px,stroke-dasharray:6 4,color:#1168bd
```

Rules: every container shows `[Technology]`. Dotted arrows are asynchronous. Subgraph syntax is `subgraph id ["Title"]` (id first, quoted title in brackets).

## 5. Level 3: Component

Question answered: *What are the major building blocks inside one container?* Audience: engineers. Pick ONE container, show its components, and show only the neighbours it talks to as outside nodes.

```mermaid
flowchart TB
    web["<b>Web Storefront</b><br/>[Container]"]
    db[("<b>Order Database</b><br/>[Container]")]

    subgraph api ["Order API (Node.js)"]
        controller["<b>Order Controller</b><br/>[Express router]<br/>Receives HTTP requests"]
        service["<b>Order Service</b><br/>Business rules for orders"]
        payClient["<b>Payment Client</b><br/>Talks to payment provider"]
        repo["<b>Order Repository</b><br/>Reads and writes orders"]
    end

    web -->|"Sends requests<br/>JSON/HTTPS"| controller
    controller -->|"Delegates to"| service
    service -->|"Charges via"| payClient
    service -->|"Saves via"| repo
    repo -->|"Reads and writes<br/>SQL"| db

    classDef container fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef component fill:#85bbf0,stroke:#5d82a8,color:#000000
    classDef database fill:#438dd5,stroke:#2e6295,color:#ffffff
    class web container
    class db database
    class controller,service,payClient,repo component
```

## 6. Deployment view

Question answered: *Where does each piece run?* Use nested subgraphs for environment, region, cluster, network zone. Max 2 levels of nesting.

```mermaid
flowchart TB
    user(["<b>Customer</b><br/>Browser"])

    subgraph cloud ["AWS eu-west-1"]
        subgraph pub ["Public subnet"]
            lb["<b>Load Balancer</b><br/>[ALB]"]
        end
        subgraph priv ["Private subnet"]
            apiNodes["<b>Order API</b><br/>[3 x ECS tasks]"]
            dbNode[("<b>Order Database</b><br/>[RDS PostgreSQL]")]
        end
    end

    user -->|"HTTPS"| lb
    lb -->|"HTTP"| apiNodes
    apiNodes -->|"SQL over TLS"| dbNode

    classDef container fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    class lb,apiNodes,dbNode container
    class user person
```

## 7. Label formula

```
"<b>Name</b><br/>[Technology]<br/>One-line plain-language responsibility"
```

- Name: 1 to 3 words, business language.
- `[Technology]`: omit at Level 1 and in exec-facing diagrams.
- Responsibility: ≤ 8 words, starts with a verb or noun phrase, no jargon.
- Edge label: `"Verb phrase<br/>Protocol"`, for example `"Places orders<br/>HTTPS"`.

If a renderer shows raw `<b>` tags (rare), drop the bold tags and keep `<br/>`.
