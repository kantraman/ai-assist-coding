# Clarifying Questions Playbook

Use this during gap analysis and when writing the question batch. The aim is to ask *few* questions that *change the plan*, not to interrogate.

## Dimensions to check

Score each: clear / fuzzy / missing. Only ask about fuzzy or missing ones that would change the plan.

| Dimension | Ask when unclear | Typical source |
|---|---|---|
| **Goal & success** | What does "done" look like? How will you know it works? | User |
| **Users & scenarios** | Who uses it, and what are the top 1–3 flows? | User |
| **Scope boundaries** | What is explicitly *not* included? MVP vs full? | User |
| **Tech stack** | Language, framework, hosting, database, existing conventions? | User / codebase |
| **Existing code** | Greenfield or extending something? Where does it live? | User / file read |
| **Constraints** | Deadline, performance, budget, compliance, browser/device support | User |
| **Integrations** | Third-party APIs, auth, data sources | User + research |
| **Data** | Shapes, volume, persistence, privacy | User |
| **Quality bar** | Test expectations, accessibility, security level | User + skills |
| **Best practice / library choice** | Current, maintained, compatible options | Research |
| **Version and compatibility facts** | Does X work with Y at version Z? | Research |

## Deciding: ask, research, or assume

1. Would any reasonable plan handle this the same way? → **Assume** and log it.
2. Is it about the user's intent, taste, or private context? → **Ask**.
3. Is it a public, checkable fact? → **Research** (with approval).
4. Is it cheap for the user to answer but costly to get wrong? → **Ask**, even if you could guess.
5. Is it expensive for the user to answer (they'd have to look something up)? → **Research or assume**, and let them correct you.

## Writing good questions

- Lead with the decision, then the options, then your recommendation.
- Offer a default so "go with your defaults" is a valid reply.
- One question per line; avoid compound questions.
- Prefer choices over open text when the space is small.
- Say why it matters when it isn't obvious ("affects whether we need a background worker").
- Cap the batch at 3–5. If more remain, ask the top ones first and hold the rest for a second round only if the answers reveal they still matter.

### Example batch

```
Proposed action [A1]: Ask 4 clarifying questions
1. Hosting: where will this run? (a) Vercel/serverless (b) your own server/VPS (c) not decided → I'd suggest (a)
2. Auth: do users need accounts at launch? (a) yes, email+password (b) social login only (c) no → default (b)
3. Data: expected size in the first year? (a) <10k rows (b) up to 1M (c) more → default (a); affects DB choice
4. Existing code: is there a repo I should plan around, or is this greenfield? → default greenfield
Reply with answers, or "defaults" to accept all recommendations.
```

## Stop conditions

Stop asking and start drafting when:
- The remaining unknowns wouldn't change task order, file layout, or tech choices, or
- The user signals impatience or says to decide for them (log every choice as an Assumption).
