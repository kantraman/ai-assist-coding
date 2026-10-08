# Plan Template

Use this structure for the generated plan file. Delete sections that don't apply. Keep language direct and imperative, since a coding assistant will read it as instructions.

Contents: [Template](#template) · [Task writing guide](#task-writing-guide) · [Example task](#example-task)

## Template

````markdown
# Plan: <short title>

> Status: Draft | Approved  
> Created: <date>  
> Owner: <user>  
> Intended reader: AI coding assistant. Follow tasks in order unless noted.

## 1. Goal
One or two sentences: what will exist when this is done, and why it matters.

## 2. Context
- Existing project / repo state (language, framework, key directories)
- Users and primary use case
- Constraints (deadline, performance, compliance, budget, platforms)

## 3. Requirements
### Must have
- R1: ...
- R2: ...
### Should have
- R3: ...
### Out of scope
- ...

## 4. Decisions
Choices already made, with the reason and source, so they aren't re-litigated.
| ID | Decision | Reason | Source |
|----|----------|--------|--------|
| D1 | Use X for Y | ... | user / URL / skill name |

## 5. Assumptions
Guesses made without confirmation. The coding assistant should stop and ask if any of these turn out to be false.
- A1: ...

## 6. Open questions
Unresolved items. Mark which tasks are blocked by each.
- Q1: ... (blocks: T4)

## 7. Architecture / Approach
Short description of components and how they interact. Include a file/module layout if new files are created:
```
src/
  module/
    file.ext   # purpose
```
Key interfaces, data shapes, or API contracts if they affect multiple tasks.

## 8. Tasks
Ordered by dependency. One task ≈ one focused change / commit.

### T1: <verb phrase>
- **Depends on:** none
- **Covers:** R1
- **Files:** `path/to/file`
- **Do:** concrete steps
- **Done when:** observable, checkable outcome
- **Verify:** command or manual check

### T2: ...

## 9. Testing strategy
What to test, at which level (unit / integration / e2e / manual), and any commands to run.

## 10. Risks and mitigations
- Risk → mitigation

## 11. Sources
- User-provided info
- Research: <title> - <URL> - what it informed
- Skills consulted: <skill name> - what it contributed

## 12. Instructions for the coding assistant
- Work through tasks in order; mark each done in this file when complete.
- Do not expand scope beyond Section 3.
- If an Assumption proves wrong or an Open question blocks a task, stop and ask the user.
- Prefer small commits, one per task.
- Run the Verify step for each task before moving on.
````

## Task writing guide

Good tasks are:

- **Specific about location.** Name files, functions, or modules. "Add rate limiting" is vague; "Add `RateLimiter` middleware in `src/middleware/rate_limit.py` and register it in `src/app.py`" is executable.
- **Checkable.** "Done when" should be something a person or a test can confirm, such as "GET /health returns 200 with `{status: ok}`", not "health endpoint works well".
- **Right-sized.** If a task has more than about five "Do" steps or touches more than a handful of files, split it.
- **Traceable.** Each task lists which requirement IDs it covers; each Must-have requirement is covered by at least one task.
- **Independent where possible.** Mark tasks that can run in parallel so the assistant isn't forced into false ordering.

## Example task

```markdown
### T3: Add password reset endpoint
- **Depends on:** T1 (user model), T2 (email service)
- **Covers:** R4
- **Files:** `app/routes/auth.py`, `app/services/tokens.py`, `tests/test_auth.py`
- **Do:**
  1. Add `POST /auth/reset-request` that accepts an email and always returns 202 (no account enumeration).
  2. Generate a single-use token, expiry 30 min (per D2), store hashed.
  3. Add `POST /auth/reset` that validates the token and sets the new password.
- **Done when:** valid token resets password once; expired or reused token returns 400.
- **Verify:** `pytest tests/test_auth.py -k reset`
```
