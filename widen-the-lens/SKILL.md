---
name: widen-the-lens
description: A structured unstick-and-widen protocol for debugging, issue fixing, root-cause analysis, and any task where the model keeps missing the obvious, repeats a failed fix, loops on the same idea, or gives shallow answers. Use this skill whenever a fix did not work, the same error comes back, the user says "still not working", "you already tried that", "think harder", "you're missing something", or when a bug, failing test, wrong output, or confusing result needs more careful investigation than a first guess. Also use it proactively at the start of any non-trivial debugging or analysis task, and after any failed attempt, even if the user did not ask for deeper reasoning.
---

# Widen the Lens

Smaller models fail in debugging and analysis in predictable ways:

1. **Tunnel vision**: they lock onto the first idea and keep polishing it.
2. **Repeating**: they retry the same fix with tiny changes.
3. **Skipping the obvious**: wrong file, typo, wrong environment, stale cache.
4. **Guessing instead of looking**: they reason from memory about code or output they never read.
5. **Declaring victory early**: they say "fixed" without proving it.

This skill fixes those by forcing a fixed loop: observe, widen, hypothesize, test cheaply, record, verify. Follow the steps in order. Do not skip a step because it feels unnecessary; the steps you want to skip are usually the ones that find the problem.

## The loop

### Step 0: Start the attempt log

Keep a short written log for the whole task (in your reply, or with `scripts/ledger.py` if you can run code). Every attempt gets one line: what you tried, what you expected, what actually happened. This log is what stops you repeating yourself. See "Attempt log" below.

### Step 1: State the problem in facts only

Write three short parts:

- **Expected**: what should happen.
- **Actual**: what happens instead. Copy the exact error text or output. Do not paraphrase it.
- **Unknowns**: what you have not yet seen or confirmed.

Keep observations (things you saw) separate from inferences (things you think). If you have not read the actual error, file, or output, go read it now. Read all of it, not only the first line. The last lines of a stack trace and the first error in a long log often matter most.

### Step 2: Check the obvious first (2 minutes, no cleverness)

Before any theory, run the quick checklist in `references/obvious-checks.md`. Most "hard" bugs are one of these: wrong file edited, code not reloaded, wrong version or environment, typo, wrong path, bad config value, input is not what you assumed. Mark each item checked or not applicable. If you cannot check an item, say so rather than assuming it is fine.

### Step 3: Widen the view

Tunnel vision means the real cause is outside the area you are staring at. Deliberately look one layer further out in each direction:

- **Upstream**: what produces the input to the failing code? Print or inspect the real value.
- **Downstream**: what consumes the output? Is the failure actually here, or only noticed here?
- **Sideways**: other places that do the same thing and work. What differs?
- **Environment**: versions, config, env vars, permissions, OS, data, time, network.
- **History**: what changed recently? Did it ever work? (`git log`, `git diff`, last known good.)
- **Assumptions**: list 3 things you are treating as true without having verified them. Verify them.

For how to search more broadly (different keywords, callers, error strings, docs), read `references/search-broadening.md`.

### Step 4: Generate at least three different hypotheses

Write at least three possible causes that are truly different from each other, not variations of one idea. Include at least one that feels unlikely or that contradicts your current favorite. For each, write:

| Hypothesis | Evidence for | Evidence against | Cheapest test |
|---|---|---|---|

Rank by (likelihood x how cheap the test is). Run the cheapest informative test first. A test that only prints or inspects something is better than a test that changes code, because it cannot make things worse.

### Step 5: Test one thing at a time

Change or check one variable per attempt. If you change three things and it works, you do not know which one mattered. After each attempt, add a line to the attempt log with the actual result, including when the result is "no change".

### Step 6: Apply the repeat rule

Before each new attempt, compare it to the log:

- **Same idea as a previous attempt, even if reworded?** Do not run it. Pick a different hypothesis.
- **Two failed attempts on the same hypothesis?** Drop that hypothesis. Go back to Step 3 and widen further. Your picture of the problem is probably wrong, not your execution of it.
- **Three failed attempts overall?** Do a full reset (see below).
- **Result did not change at all after your fix?** That is a strong clue that your change is not being executed, or you are looking at the wrong thing. Go to the "no effect" checks in `references/obvious-checks.md`.

### Step 7: Reset when stuck

When you are stuck after three failed attempts, stop and do this:

1. Rewrite the problem from scratch using only the facts from Step 1, ignoring all earlier theories.
2. List what the attempt log proved is NOT the cause.
3. Flip it: "What if the thing I trust most is the broken part?" Test that.
4. Shrink it: build the smallest example that still fails, or remove parts until the failure disappears. The last part removed is a suspect.
5. Bisect: if it worked before, find the exact change where it broke. If it never worked, find the exact step where the data first becomes wrong.
6. If you are still stuck, say so plainly, summarize what you ruled out, and ask the user for the one specific piece of information that would help most. An honest "here is what I ruled out and what I need" beats another repeat guess.

### Step 8: Verify before claiming it is fixed

A fix is not done until all of these are true:

- You reproduced the original failure first (or confirmed it from the user's report).
- After the fix, the exact same steps now succeed. Show the evidence (output, test result).
- You checked that nearby behavior still works (run related tests or the neighboring case).
- You can explain **why** the fix works and why the bug happened. If you cannot explain it, you may have hidden the symptom, not fixed the cause.

Do not say "this should work". Say what you ran and what you saw.

### Step 9: Record the lesson

After solving, or after giving up, write a short lesson so the next attempt starts smarter. Use the template in `references/lessons-template.md`. Good lessons name the symptom, the real cause, the misleading clue, and the quick check that would have found it sooner. If a lessons file already exists in the project, read it at the start of the task, since past mistakes often repeat.

## Attempt log

Use this format, one line each:

```
#1 | idea: <what I tried> | expected: <result> | actual: <result> | verdict: worked / no change / worse / new info
```

If you can run code, `scripts/ledger.py` keeps the log in a file and warns when a new attempt looks too similar to an earlier one:

```
python scripts/ledger.py add "increase timeout to 30s" --expected "request succeeds" --actual "still times out"
python scripts/ledger.py check "raise the timeout to 60s"   # warns: similar to #1
python scripts/ledger.py show
```

## Habits that help throughout

- **Look, do not recall.** Open the file, run the command, read the output. Memory of a library or a file is often wrong.
- **Quote evidence.** When you claim something, point to the line or output that shows it.
- **Prefer cheap, safe checks** (print, read, grep, dry-run) before edits.
- **Say what you do not know.** Unknown is a useful state. Pretending to know causes loops.
- **Be suspicious of fast fixes** that need no explanation.
- **If the user says you already tried something, believe them** and check your log. Do not defend the earlier attempt.

## Output format when reporting back

Keep the final report short and in this order:

1. **Cause**: what was actually wrong, in one or two sentences.
2. **Fix**: what you changed.
3. **Evidence**: the command or test you ran and what it showed.
4. **Ruled out**: other things you checked that were not the cause (this saves the user time).
5. **Lesson**: one line to remember next time.
