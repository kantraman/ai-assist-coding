# Stack Profiles

Build a Stack Profile in Phase 0 so every later choice fits the user's stack instead of fighting it.

## Profile fields

```
Language/runtime + version:
Backend framework:
Frontend framework + rendering mode (SPA / SSR / SSG / islands):
Database + ORM/query layer + migration tool:
Auth approach:
Package manager + monorepo?:
Test tools (unit / integration / e2e):
Lint, format, type-check:
CI/CD + hosting target:
Budgets: p95 latency, users, data volume, availability, compliance:
Constraints: team size, existing code, must-use services:
```

Infer from repo files first; ask only for the fields that are missing and that change the design. If you can browse or search the web, check current stable versions, deprecations, and migration notes for the chosen tools before pinning.

## Typical defaults (starting points, verify versions and fit)

| Stack | Structure idiom | Data / migrations | Tests |
|---|---|---|---|
| Next.js / React + Node + Postgres | route groups + `features/` mirroring `modules/` | Prisma or Drizzle + migrations | Vitest/Jest, Playwright, Testing Library |
| NestJS + React/Angular | Nest modules = fractal modules | TypeORM/Prisma/MikroORM | Jest, Supertest, Playwright |
| Django (+ DRF) + React/HTMX | apps = modules, `services.py` as Core | Django ORM migrations | pytest-django, Playwright |
| FastAPI + React/Vue | routers/services/repositories per module | SQLAlchemy + Alembic | pytest, httpx, Playwright |
| Spring Boot + Angular/React | packages per module, ports/adapters (hexagonal) | JPA/jOOQ + Flyway/Liquibase | JUnit, Testcontainers, ArchUnit, Playwright |
| Rails (+ Hotwire) | engines or namespaced modules, service objects | ActiveRecord migrations | RSpec/Minitest, Capybara |
| Laravel (+ Inertia/Livewire) | domain folders, actions/services | Eloquent migrations | Pest/PHPUnit, Dusk |
| Go + HTMX/React | internal packages per module, interfaces at consumer | sqlc/pgx + goose/atlas | `testing`, testcontainers-go, Playwright |
| .NET + Blazor/React | projects per layer/module, MediatR optional | EF Core migrations | xUnit, Testcontainers, Playwright |

Architecture-test tools (ArchUnit, dependency-cruiser, import-linter, NetArchTest) can enforce the same layering rules the graph validator checks; use them where available.

## Unknown or mixed stacks

If the user gives only a goal, propose one conventional stack with a one-line reason and proceed unless they object. If the stack is unusual, keep the four-part fractal shape and translate names; the principles do not depend on the framework.
