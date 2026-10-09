<!-- Worked example: the expected shape of a delivered answer (verified to lint and render).
     Request was: food-delivery app, React web + mobile, FastAPI, Postgres, Redis, Celery, Stripe, Twilio;
     audience includes ops managers. Imitate the structure and label style, not the content. -->

### QuickBite: System Context (C4 Level 1)

**Purpose:** Shows who uses the QuickBite platform and which outside services it relies on.

```mermaid
flowchart LR
    customer(["<b>Customer</b><br/>Orders food"])
    driver(["<b>Driver</b><br/>Delivers orders"])
    ops(["<b>Operations Manager</b><br/>Monitors deliveries"])

    quickbite["<b>QuickBite Platform</b><br/>Takes orders, assigns drivers,<br/>and tracks deliveries"]

    stripe["<b>Stripe</b><br/>Processes card payments"]
    twilio["<b>Twilio</b><br/>Sends text messages"]

    customer -->|"Places and tracks orders"| quickbite
    driver -->|"Accepts and completes deliveries"| quickbite
    ops -->|"Reviews activity"| quickbite
    quickbite -->|"Charges customers"| stripe
    quickbite -->|"Sends SMS updates"| twilio
    twilio -.->|"Delivers texts"| customer

    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    classDef system fill:#1168bd,stroke:#0b4884,color:#ffffff
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff
    class customer,driver,ops person
    class quickbite system
    class stripe,twilio external
```

**How to read it:** Customers order through QuickBite, drivers receive and complete deliveries, and operations managers watch it all. QuickBite hands payments to Stripe and text messages to Twilio rather than building those itself.

### QuickBite: Containers (C4 Level 2)

**Purpose:** Shows the deployable parts of QuickBite and how they communicate.

```mermaid
flowchart LR
    customer(["<b>Customer</b>"])
    stripe["<b>Stripe</b><br/>[External]"]
    twilio["<b>Twilio</b><br/>[External]"]

    subgraph qb ["QuickBite Platform"]
        web["<b>Web App</b><br/>[React]<br/>Order and track food"]
        mobile["<b>Mobile App</b><br/>[Customer and driver]<br/>Order, track, deliver"]
        api["<b>Backend API</b><br/>[FastAPI]<br/>Orders, payments, accounts"]
        cache[("<b>Cache</b><br/>[Redis]<br/>Fast lookups")]
        db[("<b>Database</b><br/>[PostgreSQL]<br/>Orders and users")]
        queue[["<b>Task Queue</b><br/>[Celery broker]<br/>Pending jobs"]]
        workers["<b>Dispatch Workers</b><br/>[Celery]<br/>Match drivers to orders"]
    end

    customer -->|"Uses<br/>HTTPS"| web
    customer -->|"Uses"| mobile
    web -->|"Calls<br/>JSON/HTTPS"| api
    mobile -->|"Calls<br/>JSON/HTTPS"| api
    api -->|"Reads and writes<br/>SQL"| db
    api -->|"Caches hot data"| cache
    api -->|"Charges cards<br/>HTTPS"| stripe
    api -.->|"Queues dispatch jobs"| queue
    queue -.->|"Delivers jobs"| workers
    workers -->|"Updates assignments<br/>SQL"| db
    workers -->|"Sends SMS<br/>HTTPS"| twilio

    classDef person fill:#08427b,stroke:#052e56,color:#ffffff
    classDef container fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef database fill:#438dd5,stroke:#2e6295,color:#ffffff
    classDef external fill:#999999,stroke:#6b6b6b,color:#ffffff
    class customer person
    class web,mobile,api,queue,workers container
    class db,cache database
    class stripe,twilio external
    style qb fill:none,stroke:#1168bd,stroke-width:2px,stroke-dasharray:6 4,color:#1168bd
```

### Assignment flow: UML Sequence

```mermaid
sequenceDiagram
    autonumber
    actor customer as Customer
    participant api as Backend API
    participant queue as Task Queue
    participant worker as Dispatch Workers
    participant twilio as Twilio

    customer->>api: Place order
    api-->>customer: Order confirmed
    api-)queue: Queue driver dispatch
    queue-)worker: Deliver dispatch job
    loop Until a driver accepts
        worker->>worker: Pick nearest available driver
        worker->>twilio: Notify driver by SMS
    end
    worker->>api: Record driver assignment
    api-->>customer: Show driver on the way
```
