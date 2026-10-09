---
name: software-documentation
description: Create clear, accurate, complete operational documentation for a software project, tailored to its audience - API/integration docs for frontend and backend engineers, solution overview plus user help guide for clients, implementation/architecture/assumptions docs for product managers, and test plans, test cases and bug-report templates for QA testers. Also generates importable Postman collections and environments from API specs. Use this skill whenever the user asks to document a project, API, feature, module, release or handover; write an API reference, FE/BE contract, integration guide, user guide, help guide, README, runbook, architecture overview, design-decision record, scope-of-delivery, release notes, test plan, test cases, QA checklist, regression or smoke suite, UAT script or bug template; or create a Postman collection - even if they only say "write this up", "explain what we built", "document the endpoints" or "prepare handover docs".
---

# Software Documentation

Produce documentation that people can act on without asking the author a follow-up question. Different readers need different things, so the first job is to decide who the reader is. The second job is to make every statement traceable to something real (code, spec, config, a decision the user told you about) rather than to plausible-sounding guesses.

## The audiences

| Audience | They need to know | Reference to read |
|---|---|---|
| **Engineers (FE, BE, DevOps)** | Exact contracts: endpoints, payloads, errors, auth, data models, states, env setup, how to run and troubleshoot | `references/engineering.md` |
| **Client / end users** | What is included in the software, what is not, and how to use it step by step | `references/client.md` |
| **Product managers** | What was done, the logic behind it, assumptions, constraints, architecture, extensibility, and anything added beyond scope | `references/product.md` |
| **QA testers** | How to set up a test environment, what is in scope, what correct behaviour is, exact test steps with expected results, known issues, how to report bugs, release sign-off | `references/qa.md` |
| **Postman collection** (any API work) | Importable, runnable requests with tests | `references/postman.md` |

Read only the reference files for the audiences actually requested. If the request is "complete documentation" or "handover pack", produce all four audiences' docs plus Postman when there is an API.

## Workflow

### 1. Pin down scope and audience
Work out from the request: who will read this, what they will do with it, and which document types are needed. If the audience is ambiguous and the answer changes the output materially, ask one short question; otherwise state your assumption at the top of your reply and proceed. Do not interview the user at length - gather facts from the project itself first.

### 2. Gather facts before writing
Documentation is only useful if it is true. Look for sources in this order, and read what is available rather than recalling from memory:

1. Code and config in the container or uploaded files: routes/controllers, schemas/models, validators, middleware (auth, rate limits), env files, migrations, package manifests, CI/deploy config, UI components and routes.
2. Existing specs and docs: OpenAPI/Swagger, README, ADRs, tickets, PRDs, Postman collections.
3. What the user told you in the conversation.

Rules for facts:
- **Never invent** endpoints, fields, error codes, limits, screens, or business rules. If something is not in the sources, write `TBC` and list it under "Open questions" with a suggested owner (e.g. "BE lead", "PM").
- **Separate what the code does from what was intended.** If code and spec disagree, document the actual behaviour, flag the discrepancy, and say which one you believe is correct and why.
- **Mark inferences.** Anything you deduced rather than read (e.g. "appears to be soft-delete because of the `deleted_at` column") gets labelled as inferred.
- **Use real examples.** Request/response samples should come from fixtures, tests, or the schema, and must be valid against the documented schema.
- If no code or spec exists and the user only describes the system verbally, document what they said, mark the doc as based on a verbal description, and keep the `TBC` list visible.

### 3. Write using the audience template
Open the relevant reference file and follow its structure. Adapt - drop sections that genuinely do not apply (and say so in one line rather than silently omitting), but do not skip the sections that carry the most value: error handling and edge cases for engineers, "not included" for clients, assumptions and constraints for product managers, sourced expected results and known issues for QA.

### 4. If there is an API, build the Postman collection
Make the OpenAPI spec the single source of truth. If the project has one, use it. If not, write a minimal OpenAPI 3 file from the code first (it also doubles as the engineering reference), then run `scripts/build_postman_collection.py`. See `references/postman.md`. Hand-writing collection JSON drifts from the docs and is error-prone; generate it.

### 5. Verify before delivering
Run through `references/quality-checklist.md`. At minimum: every endpoint documented has a success and an error example; every example is consistent with the schema; no placeholder text remains except deliberate `TBC` items and `[Screenshot: ...]` markers; terminology is consistent across all documents; the same fact is not stated differently in two places.

### 6. Deliver
Default to Markdown files, because they live well in repos and diff cleanly. Switch format when asked: Word -> follow the docx skill, PDF -> the pdf skill, a shared editable document -> the docs skill. Do not change format on your own.

Recommended layout for a full documentation set:

```
docs/
├── README.md                 # index: what each doc is, who it is for, how current it is
├── engineering/
│   ├── api-reference.md
│   ├── fe-be-contract.md     # states, validation, permissions, flags the UI must honour
│   ├── data-models.md
│   ├── setup-and-operations.md
│   └── changelog.md
├── client/
│   ├── solution-overview.md  # what is included / not included
│   └── user-guide.md
├── product/
│   └── implementation-overview.md
├── qa/
│   ├── test-plan.md
│   ├── environment-and-test-data.md
│   ├── coverage-map.md
│   ├── test-cases.md         # or test-cases.xlsx if the team tracks execution in a sheet
│   ├── smoke-and-regression.md
│   ├── known-issues.md
│   ├── bug-report-template.md
│   └── uat-script.md         # only if client acceptance is needed
├── postman/
│   ├── <project>.postman_collection.json
│   └── <project>.postman_environment.json
└── openapi.yaml (or .json)
```

For a single-doc request, produce just that one file. When replying to the user, summarise in a few lines: what you created, what sources it is based on, and the open questions (`TBC` items) that need a human answer. Do not paste the full documents into chat.

## Writing rules that apply to every audience

- **Lead with the point.** Each document opens with 2-4 sentences: what this is, who it is for, what they can do after reading it.
- **One idea per sentence, active voice, present tense.** "The API returns 409 when the email exists", not "A 409 may potentially be returned in the event that...".
- **Be specific.** Replace "fast", "secure", "flexible" with the number, mechanism, or extension point. "Tokens expire after 15 minutes" beats "short-lived tokens".
- **Define terms once**, in a glossary, then use them consistently. Pick one name per concept (do not alternate between "customer", "client", "account holder").
- **Show, then explain.** An example request followed by a table of fields is faster to absorb than paragraphs.
- **Use tables for reference data** (fields, errors, roles) and numbered lists for procedures. Use prose for reasoning and rationale.
- **Write for the reader's vocabulary.** Engineers get precise technical terms. Clients and PMs get plain language; if a technical term is unavoidable, explain it in a short parenthetical.
- **Record the why for non-obvious decisions**, in one or two lines, next to the decision. Future readers will otherwise undo it.
- **Date and version everything.** Put the version, date, and author/source at the top of each doc so readers can tell how stale it is.
- **Never include secrets**: real keys, tokens, passwords, production URLs with credentials, personal data. Use obvious placeholders such as `<YOUR_API_KEY>`.
- **Do not fabricate visuals.** For UI steps where a screenshot would help and you cannot capture one, insert `[Screenshot: <what it should show>]`. For architecture and flows, use Mermaid diagrams, which can be written as text.

## Common situations

- **Documenting an existing codebase retroactively:** start from routes and models, produce the OpenAPI file, then derive the rest. Expect gaps in business rules; put them in open questions rather than guessing.
- **QA documents:** write expected results only from a source (spec, code, acceptance criteria); otherwise mark `Expected: TBC`. Leave result/status columns blank - documenting tests is not running them, so never claim anything passed.
- **Documenting a feature mid-development:** mark status per endpoint/screen (`planned`, `in progress`, `stable`, `deprecated`) so FE and BE know what they can rely on.
- **Release or handover:** the QA pack needs a sign-off sheet and known-issues list; the client doc must state what is delivered, what environments exist, what is out of scope, known limitations, and who to contact. The PM doc must list deviations from the original scope and why.
- **Updating existing docs:** preserve structure and IDs readers may link to, add a changelog entry, and highlight breaking changes at the top.
- **Breaking changes:** always call out explicitly - what changed, who is affected (FE, mobile, third parties), the migration step, and the date.
