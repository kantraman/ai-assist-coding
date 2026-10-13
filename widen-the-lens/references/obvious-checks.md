# Obvious checks

Run this list before building theories. Mark each: checked / not applicable / cannot check.
Missing the obvious is the most common failure, so do not skip items because they seem too simple.

## Table of contents
1. Am I looking at the right thing?
2. Is my change actually running? (the "no effect" checks)
3. Inputs and data
4. Environment and versions
5. Code-level slips
6. Reading the evidence

## 1. Am I looking at the right thing?
- Am I editing the same file that is actually executed or imported? (Search for duplicate file names, copies, build output folders.)
- Am I in the right directory, branch, project, or environment?
- Is the failing case the same one the user reported, not a similar one I made up?
- Did I read the whole error message, including the last lines and any "caused by" section?

## 2. Is my change actually running? (the "no effect" checks)
Use these whenever a fix changes nothing.
- Add an obvious marker (a print, a log line, a deliberate error) in the changed code. Does it appear?
- Was the service, server, or process restarted? Is hot reload really on?
- Is there a cache, build step, compiled output, or bundled copy that must be regenerated?
- Is a different version of the package installed than the one in the source folder?
- Is the test or run using a stale snapshot, fixture, or container image?
- Is the setting overridden elsewhere (env var, config layer, command-line flag, default)?

## 3. Inputs and data
- Print the real input value and its type. Is it what I assumed? (null, empty, string vs number, wrong encoding, extra whitespace, wrong case.)
- Is the data the same shape in the failing case as in the working case?
- Are there edge values: zero, one, empty, very large, negative, duplicates, unicode, time zones?
- Is the input coming from the place I think it is?

## 4. Environment and versions
- Language, runtime, and library versions. Did anything update recently?
- Environment variables, secrets, config files, feature flags.
- File paths: relative vs absolute, case sensitivity, slashes, spaces, working directory.
- Permissions, disk space, network access, ports already in use.
- Does it work on another machine or in a clean environment?

## 5. Code-level slips
- Typos in names, strings, keys, or imports. Is the name spelled the same everywhere?
- Off-by-one errors, wrong comparison operator, inverted condition, `=` vs `==`.
- Variable shadowing, reused names, mutated shared state.
- Async problems: missing await, race conditions, callback not awaited, order of operations.
- Missing return, wrong return type, swallowed exception, empty catch block.
- Wrong argument order, wrong units, wrong default.

## 6. Reading the evidence
- Are warnings being ignored? Warnings often contain the answer.
- Is the first error hiding behind a later, louder error? Look for the earliest one.
- Does the log timestamp match my run, or am I reading an old log?
- Is the output from my run, or from a cached or previous run?
