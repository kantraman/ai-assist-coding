# Client documentation

Two documents, written for non-technical readers who care about outcomes:

- **Part A - Solution Overview:** what the client is getting (and not getting).
- **Part B - User Guide:** how to use it.

Write in plain language. No stack names, class names, or internal jargon unless the client's own team will operate the system, in which case put those in a clearly separate "For your IT team" section.

## Contents
1. Part A: Solution Overview
2. Part B: User Guide
3. Style rules for client docs
4. Worked example of a guide task

---

## Part A - Solution Overview

Purpose: remove ambiguity about what was delivered, so there are no surprises at acceptance or later support requests.

```markdown
# <Product name> - Solution Overview
Version | Date | Prepared for | Prepared by

## 1. Summary
Two to four sentences: what the software does and the problem it solves.

## 2. Who uses it
Table: Role | What they can do | What they cannot do
(Use the roles that actually exist in the product.)

## 3. What is included
Group by module or business area. For each feature:
- **Feature name** - one sentence on what it lets the user do.
Mark status where relevant: Delivered / Delivered with limitations / Planned.

## 4. What is not included
Explicit list of things a reasonable person might expect but that are not part of this delivery,
with a one-line reason or "available as a future addition" where true.

## 5. Integrations and third-party services
Table: Service | Purpose | Who owns the account | Cost implication | What happens if it is unavailable

## 6. Environments and access
Table: Environment | Purpose | URL | Who has access
(Never include credentials; say where they are handed over securely.)

## 7. Supported platforms
Browsers/versions, mobile OS versions, screen sizes, languages, accessibility level if known.

## 8. Data
What data is stored, where, retention, backups, who can export or delete it, and any compliance relevant to the client's industry (only state what is verifiably implemented).

## 9. Known limitations
Honest list with workarounds. Better the client reads it here than discovers it.

## 10. Operating the system after handover
Routine tasks the client's team must do (renew certificates/keys, review logs, top up third-party credits), with frequency and owner.

## 11. Support and contact
How to report an issue, what information to include, expected response times if agreed, escalation path.

## 12. Glossary
Plain-language definitions of terms used in the product and in these documents.
```

Guidance:
- Derive the feature list from the code (routes, screens, permissions) and any scope document, then cross-check against each other. Anything in the scope document that you cannot find in the code goes to "Open questions" for the user rather than being listed as delivered.
- "What is not included" is the highest-value section. Populate it from the scope document, the PM notes, features that are stubbed or feature-flagged off, and obvious adjacent capabilities.
- Describe features by benefit and action ("Export a month of invoices as a spreadsheet"), not by implementation ("CSV endpoint").

---

## Part B - User Guide (help guide)

Organise by **what the user wants to do**, not by how the software is built. People arrive with a task in mind.

```markdown
# <Product name> - User Guide
Version | Date | Applies to app version

## Quick start (5 minutes)
Numbered steps from first sign-in to the first meaningful result.

## Getting around
Screen-by-screen orientation: navigation, search, profile/settings, notifications. [Screenshot: ...]

## Tasks
Grouped by role if roles differ substantially, otherwise by area.
### How to <do the thing>
(see template below)

## Settings and account
Password reset, profile, notification preferences, language, user management (for admins).

## Troubleshooting
Symptom -> what to try -> when to contact support. Use the exact wording of on-screen messages so users can search for them.

## FAQ
Real questions a new user would ask; keep answers to 1-3 sentences with a link to the full task.

## Glossary
```

### Task template

```markdown
### How to <verb + object>
**Who can do this:** <roles>
**Before you start:** <prerequisites, e.g. "You need at least one product created">

1. Go to **Menu name > Page name**.
2. Click **Button label**.
3. Fill in the form:
   | Field | What to enter | Notes |
   |---|---|---|
4. Click **Save**.

**You should see:** <the visible confirmation or result>.
[Screenshot: <what it shows>]

**Tips:** <short, useful, optional>
**If something goes wrong:** <the most likely error message and the fix>
```

Rules for the guide:
- **Use the product's exact labels** in bold (buttons, menus, field names) copied from the UI code or strings file, not paraphrased. If you cannot read the UI source, state that labels are provisional.
- **One action per step**, starting with a verb.
- **Say what the user will see** after the key steps, so they know it worked.
- **Cover the unhappy path**: validation messages, permissions denied, empty states, what to do if a job is slow.
- **Warn before destructive actions** (delete, bulk change, irreversible send), and say whether they can be undone.
- **Separate role content** so a viewer is not wading through admin tasks.
- **Screenshots:** you usually cannot capture them. Insert `[Screenshot: <specific description of the screen state>]` at the points a screenshot would help most, and tell the user in your reply how many placeholders there are.
- **Do not describe features you have not verified exist.** If a screen is implied but not found in the code, leave it out and flag it.

## Style rules for client docs
- Reading level: aim for clear, friendly, and direct; short sentences; second person ("you").
- Avoid: "simply", "just", "obviously" - these make users feel stupid when something does not work.
- Replace internal terms: "payload" -> "information you send", "endpoint" -> omit, "auth token" -> "sign-in session".
- Consistent naming: use exactly the label shown in the product.
- Keep each task to one page where possible; link to related tasks rather than duplicating steps.

## Worked example of a guide task

```markdown
### How to invite a team member
**Who can do this:** Admins
**Before you start:** Have the person's work email address ready.

1. Go to **Settings > Team**.
2. Click **Invite member**.
3. Enter their email address and choose a **Role** (Editor can change content; Viewer can only read).
4. Click **Send invite**.

**You should see:** The person appears in the list with the status **Pending**. They receive an email valid for 7 days.
[Screenshot: Team page with a Pending member in the list]

**If something goes wrong:**
- *"This email is already a member"* - the person already has access; check the list.
- The person did not get the email - ask them to check spam, then click **Resend** next to their name.
```
