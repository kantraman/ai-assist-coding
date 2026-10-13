# Lessons log template

Keep one file per project (for example `LESSONS.md`) and add an entry after every solved or abandoned problem. Read it at the start of new debugging tasks. This is how mistakes stop repeating across sessions.

Keep entries short. Write for a future reader who knows nothing about today's task.

```
## <short title of the problem>   (<date>)

- Symptom: what it looked like from the outside.
- Real cause: what was actually wrong.
- Misleading clue: what pointed the wrong way, and why it was tempting.
- Time sink: the approach that wasted effort (so it is skipped next time).
- Fast check: the one check that would have found it sooner.
- General rule: the reusable lesson in one sentence.
```

## Example

```
## Config change had no effect   (2026-03-02)

- Symptom: raised the timeout to 60s, requests still failed at 30s.
- Real cause: a second config file in the deploy folder overrode the value.
- Misleading clue: the edited file did contain 60; looked correct.
- Time sink: three attempts changing the timeout value in code.
- Fast check: print the effective config at startup.
- General rule: when a change has no effect, prove the change is being used before trying another change.
```

## Patterns to look for across entries
When three or more entries share a cause, turn it into a standing checklist item. Add it to `obvious-checks.md` for that project.
