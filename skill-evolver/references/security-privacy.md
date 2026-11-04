# Security and Privacy Reference

## Threat model
- **Malicious or compromised skill**: hidden instructions, exfiltration, destructive
  commands, obfuscated payloads, typosquatted dependencies.
- **Prompt injection via content**: skill text, fetched pages, test inputs, filenames.
- **Excess agency**: skill grants itself more tools/permissions than its task needs.
- **Supply chain**: unpinned installs, remote scripts, unverified MCP servers.
- **Privacy leakage**: secrets/PII in skill files, logs, examples; telemetry; data sent to
  third parties during refresh/research.
- **Evolution drift**: mutations gradually weaken safeguards or purpose.

## AUDIT checklist (manual, after running the static scan)
1. Does the description match what the body and scripts actually do?
2. Any instruction to hide actions, skip confirmation, or override the user/system?
3. Any hidden text: zero-width/bidi characters, HTML comments, white-on-white, very long
   lines, base64/hex blobs, instructions in assets?
4. Scripts: network calls, subprocess/shell, eval/exec, file writes outside the skill dir,
   reads of home/credential paths (~/.ssh, ~/.aws, env vars, browser profiles).
5. Install steps: `curl | sh`, unpinned packages, post-install hooks.
6. External URLs: purpose, ownership, HTTPS, are they fetched automatically?
7. Declared vs. needed tools (least privilege). Any wildcard permissions?
8. Secrets or personal data in any file, including examples and history.
9. Logging/telemetry: what is recorded, where it goes, retention.
10. Failure behavior: does it fail closed and tell the user?

## Privacy rules for skills and for this process
- No credentials, tokens, keys, personal data, real names/emails, internal hostnames.
- Examples use synthetic data. Strip user-specific content from anything learned during
  evaluation before it enters a skill.
- Network research sends only what is needed (a library name, not user files or prompts).
- Store reports locally; do not upload skills or findings anywhere without consent.
- Third-party skills under review are not forwarded to external services.

## Transparency rules
- Declare tools used, files written, network destinations, and side effects.
- Never instruct an agent to conceal actions from the user.
- Changelog every change with reason. Keep originals and hashes for rollback.
- Findings state confidence and what was not examined.

## Handling findings
Critical/high: stop, report, do not "fix and ship" without user decision. Recommend
removal or isolation of the skill. Never execute suspicious code to "see what it does"
outside an approved sandbox.
