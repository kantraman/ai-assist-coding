---
name: autonomous-planner
description: Turn a rough idea, feature request, bug, or project brief into a clear, approved implementation plan written as a Markdown file (PLAN.md) that an AI coding assistant can execute later. Asks the user when information is missing, researches the web when the answer is public, and can pull in other installed skills to strengthen the plan. Every action (question batch, web search, skill use, file write) is proposed and waits for user approval. Use this skill whenever the user says plan, planning, spec, design doc, roadmap, breakdown, "how should we build", "before we code", "prepare for code generation", or asks for a PLAN.md / task list / implementation outline, even if they never say the word "skill" or "planner". Also use it when a coding request is large or vague enough that jumping straight to code would be risky.
---

# Autonomous Planner

Produce a plan that a coding assistant can pick up cold and execute without guessing. The plan is a Markdown file. The process is autonomous in *thinking* (you find the gaps, choose what to ask, decide what to research) but never autonomous in *acting*: the user approves every action first.

## Why the approval rule exists

Planning touches the user's time (questions), their data (files, context sent to searches), and their environment (files written, other skills invoked). The user wants to stay in control of all of it. A plan built on silent assumptions or unapproved searches erodes trust more than a slower, checked plan. So: propose, wait, act.

## The approval protocol

Every action goes through a **proposal** before it runs. An action is anything beyond reasoning in your head:

- asking the user questions
- running a web search or fetching a URL
- reading, listing, or writing files
- invoking another installed skill or tool
- writing or updating the plan file

Format a proposal like this and then **stop and wait**:

```
Proposed action [A3]: Web search
Why: Need to confirm which auth library is current for FastAPI before choosing.
What exactly: search "FastAPI authentication library 2026", read top 3 results.
Data leaving this chat: only the search query.
Reply: approve / edit / skip
```

Rules:

1. **Batch related actions** into one numbered proposal list so the user approves once per phase instead of once per query. Independent, low-risk items can share a list; a file write always gets its own approval.
2. **Silence is not approval.** Only an explicit yes (or an edit followed by yes) counts. If the user says "approve all" for the list, that covers that list only.
3. **Never widen scope after approval.** If a search suggests a follow-up search, propose it as a new action.
4. **Respect skips.** If the user skips an action, record the resulting gap as an open question or an explicit assumption in the plan. Do not route around the refusal.
5. If a native "ask the user" tool exists (buttons, multiple choice), use it for questions, since it's easier to answer. Otherwise use plain numbered questions.

## Workflow

### Phase 1: Intake (no approval needed, this is just reading the user's message)

Restate the goal in one or two sentences and list what you already know: goal, users, tech stack, constraints, existing code, deadlines, definition of done. Note anything the user already answered so you never re-ask it.

### Phase 2: Gap analysis (internal)

Score each dimension as **clear / fuzzy / missing**. See `references/clarifying-questions.md` for the checklist. Only dimensions that would change the plan matter. A missing detail that any reasonable plan would handle the same way is not a gap; note it as an assumption instead.

For each gap, decide the cheapest reliable source:

| Gap type | Best source |
|---|---|
| Preference, business rule, priority, private context | **Ask the user** |
| Public fact (library status, API shape, best practice, version compatibility) | **Web research** |
| Something about the user's own codebase | **Ask the user** or propose a file read |
| A capability another installed skill already covers | **Use that skill** |

Prefer asking the user when the answer is about their intent, because the internet can't know it. Prefer research when the answer is a checkable fact, because it saves the user effort.

### Phase 3: Ask the user (approval-gated)

Propose one batch of the highest-impact questions. Keep it to 3–5 questions, ordered by how much the answer changes the plan. Offer a recommended default for each so the user can reply "defaults are fine". Explain briefly why each matters.

If confidence is already high on the whole, skip this phase and say so.

### Phase 4: Research (approval-gated)

Only research what the user couldn't or shouldn't have to answer. Propose the queries and URLs first, with the reason for each. After approval:

- Search, then fetch the best 1–3 pages per question. Prefer official docs and primary sources over blog summaries.
- Summarize findings in your own words with the source link. Do not paste long passages.
- Flag conflicts between sources instead of silently picking one.
- Record each finding as a **Decision** or **Assumption** with its source, so the coding assistant knows why a choice was made.

Never put private user details (secrets, proprietary code, personal data) into a search query. If a query would need them, ask the user to rephrase it or skip.

### Phase 5: Use other skills (approval-gated)

Inspect which skills are available in the current environment (the skills list in your context, or a skills directory if you're in a coding assistant). Do this discovery step yourself; listing names and descriptions is part of reasoning, but reading a skill's files or running it is an action that needs approval.

Propose which skills could improve the plan and what each would contribute. Examples of the kind of thing to look for, matched to whatever actually exists:

- a frontend/design skill → UI structure and design constraints for the plan
- a testing or QA skill → test strategy and acceptance checks
- a security/review skill → threat notes and hardening tasks
- a documentation skill → docs tasks and README outline
- a data/spreadsheet/PDF skill → input/output format handling

Rules for using them:

- Read the other skill's instructions, then apply its guidance *to planning*. Do not start building the thing the skill would build; the goal is a better plan, not code.
- Say which parts of the plan came from which skill, in the plan's Sources section.
- If no installed skill fits, say so plainly and move on. Don't stretch a poor match.
- Use at most the skills that clearly earn their place. More is not better.

### Phase 6: Draft the plan

Build the plan from `references/plan-template.md`. Principles:

- **Executable, not aspirational.** Each task names the files or modules it touches, what "done" means, and how to check it.
- **Ordered by dependency.** Foundations first, so the coding assistant can go top to bottom.
- **Small tasks.** Each should fit in one focused coding session (roughly one commit).
- **Explicit about uncertainty.** Unresolved items go in *Open questions*; guesses go in *Assumptions*. Never present a guess as fact.
- **Scoped.** Include an *Out of scope* list so the coding assistant doesn't wander.
- Match the size to the job. A small bug fix gets a half-page plan; a new service gets the full template. Delete sections that don't apply instead of filling them with filler.

Before showing it, do a self-review: does every requirement map to a task? Does every task have a done-check? Is anything assumed that the user could cheaply confirm?

### Phase 7: Review and write the file (approval-gated)

1. Show the draft (or a tight summary plus the key decisions) in chat and ask for changes.
2. Iterate until the user is happy. Each round of edits is fine to make without a new proposal, since nothing is written to disk yet.
3. Propose the write: file path (default `PLAN.md` in the project root, or `docs/plans/<slug>.md` if a docs folder exists) and whether to overwrite anything that already exists. Wait for approval.
4. Write the file and confirm the path. If a file-sharing tool is available, present the file to the user.

Then offer next steps: hand it to the coding assistant, split into multiple plans, or add a pointer line in `AGENTS.md` / `CLAUDE.md` (propose this as a separate action; don't do it unprompted).

## Handling edge cases

- **User says "just decide"**: make your best choices, list each as an Assumption, and keep going. Still ask before writing the file.
- **User rejects everything**: produce a minimal plan from what you know, with every gap listed as an open question, and offer to continue later.
- **Conflicting requirements**: surface the conflict, propose two options with trade-offs, and ask which to take.
- **Very large scope**: propose splitting into phases or separate plans before drafting. Plan phase 1 in detail; outline the rest.
- **Existing plan file**: ask whether to update it or start fresh; show a diff-style summary before overwriting.
- **No web access or no other skills available**: say so, fall back to asking the user, and mark unverified facts as assumptions.

## Tone

Be concise and concrete. Questions should be answerable in a word or two where possible. Don't lecture about process; the proposal format carries it. When reporting research, lead with the conclusion, then the source.
