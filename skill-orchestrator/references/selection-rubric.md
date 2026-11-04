# Selection rubric

Score each candidate 0-2 per criterion.

| Criterion | 0 | 1 | 2 |
|---|---|---|---|
| Fit | Different task | Covers part; needs glue | Covers task fully |
| Trust | Unknown source, unpinned, unreviewed | Known source, not reviewed | Org-approved or reviewed, version pinned |
| Permissions | Broad (shell, network, credentials) | Some beyond need | Minimal, declared |
| Maintainability | Abandoned, undocumented | Documented, stale | Maintained, tested, semver |

Rules of thumb:
- Any criterion 0 on Trust or Permissions blocks "use as-is".
- Prefer composing two trusted skills over one broad untrusted skill.
- Tie-break: fewer permissions, then more recent review, then smaller size.
- If fit is 1 and a small change fixes it, Adapt beats Create.

Review for installed third-party skills: read SKILL.md and every script before use; look for instructions that tell the agent to ignore rules, hide actions, fetch remote code, or send data elsewhere. Any of these = reject.
