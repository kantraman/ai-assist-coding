# Quality checklist

Run this before delivering. Fix what you can; for anything you cannot verify, convert it to an explicit `TBC` entry rather than leaving a confident-sounding guess.

## Accuracy
- [ ] Every endpoint, field, role, screen, setting, and number comes from a source (code, spec, config, user statement), not from memory or convention.
- [ ] Where code and existing docs disagree, the doc describes the code's behaviour and flags the discrepancy.
- [ ] Inferred statements are labelled as inferred.
- [ ] Every JSON example parses and conforms to the documented schema (required fields present, enums valid, types correct, same field names and casing as the real API).
- [ ] Constants (limits, timeouts, expiry, page sizes) match the code or config exactly, and say where they are configured.
- [ ] Version, date, and sources are stated at the top of each document.

## Completeness
- [ ] Engineering: conventions, auth, every endpoint (success + errors), error catalogue, data models, env vars, setup, deploy, troubleshooting, changelog.
- [ ] FE-BE contract: validation rules, UI states, permissions, async behaviour, sequencing, feature flags.
- [ ] Client overview: included features, **not included**, roles, integrations, environments, limitations, post-handover responsibilities, support contact.
- [ ] User guide: quick start, task-based how-tos with expected results, error cases and fixes, FAQ, glossary.
- [ ] PM doc: requirement traceability, deviations, additions beyond scope, business logic, assumptions (with impact), constraints, architecture diagram + explanation, extensibility with change-cost guide, decisions, limitations/risks, next steps, open questions.
- [ ] QA: test plan with scope and exit criteria, environment/test-data guide, coverage map with gaps visible, cases derived across validation/boundary/permission/error/state lenses, smoke and regression lists, known issues, bug template and severity scale, sign-off sheet.
- [ ] Postman (if API): collection + environment generated from the spec, import steps documented, no secrets, login/token flow works.

## Clarity
- [ ] Each document opens with what it is, who it is for, and what the reader can do after.
- [ ] Reference data in tables; procedures in numbered steps; rationale in short prose.
- [ ] No vague adjectives where a number or mechanism exists.
- [ ] One term per concept, consistent across all documents and matching the UI labels.
- [ ] Client-facing text contains no unexplained jargon, and no condescending words ("simply", "just", "obviously").
- [ ] Steps start with a verb and describe one action; key steps say what the user will see.

## QA-specific accuracy
- [ ] Every expected result traces to a spec, code path, or acceptance criterion; otherwise it says `TBC`.
- [ ] No result, pass/fail status, or execution date is filled in on the tester's behalf.
- [ ] Each test case has explicit preconditions, exact test data, and observable expected results (messages, status codes, field values, side effects).
- [ ] Every documented error code and every role/permission boundary has at least one case.
- [ ] Known-issues list matches limitations stated in the client and PM documents.

## Consistency across documents
- [ ] The feature list in the client overview matches the PM traceability table, the API reference and the QA coverage map.
- [ ] Role names, status names, and enum values are identical everywhere.
- [ ] Limits and behaviours (e.g. token lifetime, file size limit) are stated identically in every document that mentions them.
- [ ] The Postman collection matches the API reference version.

## Safety and hygiene
- [ ] No secrets, personal data, or real production credentials. Placeholders like `<YOUR_API_KEY>` only.
- [ ] Destructive actions carry a warning in the user guide and in the API notes (irreversible, who can do it).
- [ ] Breaking changes are called out at the top with migration steps.

## Honesty about gaps
- [ ] Every `TBC` is listed in an "Open questions" section with a suggested owner.
- [ ] Screenshot placeholders are marked `[Screenshot: ...]` and counted in the reply to the user.
- [ ] The reply to the user states which sources the docs were built from and what could not be verified.
