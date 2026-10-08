# Maintainability Reference

Read this when refactoring, reviewing, or writing a non-trivial module. Contents: smells and fixes, design guidance, error handling, testing, documentation.

## Code smells and the usual fix

| Smell | Why it hurts | Typical fix |
|---|---|---|
| Long function (> ~40 lines, or several responsibilities) | Hard to hold in your head, hard to test | Extract well-named helper functions |
| Deep nesting (> 3 levels) | Hidden conditions, hard to follow | Guard clauses, early returns, extract function |
| Long parameter list (> 4) | Easy to misorder, hard to extend | Group into an object/dataclass/struct, or split the function |
| Boolean flag parameters | Call sites are unreadable (`run(True, False)`) | Separate functions, or an enum / named options |
| Duplicated logic (3+ copies) | Fixes must be made in many places | Extract shared function; keep it parameter-light |
| Magic numbers/strings | Meaning is invisible, changes are risky | Named constants or enums |
| God class/module | Everything depends on it, changes ripple | Split by responsibility |
| Primitive obsession | Invalid states representable, logic scattered | Small value types (e.g. `Email`, `Money`) |
| Hidden global state | Order-dependent bugs, hard tests | Pass dependencies explicitly |
| Boolean/None-returning errors | Failures ignored by callers | Exceptions or explicit result types, per project convention |
| Dead code / commented-out code | Noise; version control already remembers | Delete it |

## Design guidance

- **Single responsibility**: each function/class has one reason to change.
- **Separate policy from mechanism**: business rules shouldn't be tangled with I/O, formatting, or framework glue.
- **Depend on narrow interfaces**: pass in what a function needs, not a whole context object.
- **Make illegal states unrepresentable** where the language allows (enums, types, validation at boundaries).
- **Validate at the boundary**: check external input once, where it enters; trust validated data inside.
- **Prefer composition over inheritance** unless there's a true "is-a" relationship.
- **Immutability by default**: mutate only when there's a reason; it removes a class of bugs.
- **Rule of three**: tolerate duplication twice; abstract on the third occurrence, when the real shape is clear.

## Naming

- Functions are verbs (`parse_config`), values and types are nouns (`config`, `Invoice`), booleans read as questions (`is_expired`, `has_access`).
- Use the domain's vocabulary consistently; one concept, one name.
- Avoid abbreviations unless universal (`id`, `url`). Avoid encoding types in names.
- Scope-proportional length: short names in tiny scopes (loop index), descriptive names otherwise.

## Error handling

- Fail fast with messages that say what happened, with what input, and ideally what to do.
- Catch only what you can handle; don't catch broad exception types just to silence them.
- Clean up resources deterministically (context managers, `try/finally`, `defer`, RAII).
- Don't use exceptions for ordinary control flow.
- Log with enough context to debug; never log secrets or personal data.
- Retries: bounded, with backoff, and only for idempotent or safe operations.

## Testing for maintainability

- Test behavior, not implementation details, so refactors don't break tests.
- Cover: happy path, boundaries, empty/null input, invalid input, error paths.
- One reason to fail per test; descriptive names (`test_rejects_expired_token`).
- Keep tests fast and deterministic: no real network, clocks, or randomness without control.
- For bug fixes, write the failing test first.

## Documentation

- Public functions/classes: a short docstring covering purpose, parameters, return value, and raised errors where non-obvious.
- Inline comments: *why*, not *what*. Link to tickets or specs for non-obvious constraints.
- Keep README-level docs accurate: how to run, test, and configure.
- When behavior changes, update docs in the same change.

## Security hygiene (maintainability's close cousin)

- Never hardcode secrets; read from environment or a secret manager.
- Parameterize queries; never build SQL, shell commands, or paths by string concatenation with untrusted input.
- Escape output according to context (HTML, shell, SQL).
- Keep dependencies minimal and pinned.
