---
name: nist-rmf-ai
description: Enforces the NIST AI Risk Management Framework (AI RMF 1.0) core functions (Govern, Map, Measure, Manage) to ensure AI software engineering pipelines are trustworthy, fair, secure, and compliant. Use this whenever designing, testing, auditing, or deploying AI models, ML pipelines, or agentic applications.
---

# NIST AI Risk Management Framework (AI RMF) Execution

When this skill is activated, you must guide the AI system lifecycle through the four core functions of the [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework). Do not proceed to deployment without auditing each stage.

## 1. Trustworthiness Core Pillars
Ensure the AI system strictly aligns with the 7 NIST trustworthiness characteristics:
- **Valid and Reliable:** Define explicit accuracy, precision, and fallback metrics.
- **Safe:** Design bounds to prevent physical, psychological, or operational harm.
- **Secure and Resilient:** Protect against adversarial attacks (data poisoning, prompt injection, model inversion).
- **Accountable and Transparent:** Maintain structured audit logs of dataset choices, training parameters, and tool outputs.
- **Explainable and Interpretable:** Ensure model decisions or LLM reasoning paths (e.g., chain-of-thought) can be interpreted by human operators.
- **Privacy-Enhanced:** Enforce data minimization, anonymization, or differential privacy mechanisms.
- **Fair (Harmful Bias Managed):** Continuously evaluate and mitigate bias in training datasets and model outputs.

---

## 2. Framework Execution Steps

### STEP 1: GOVERN (Establish Culture & Process)
- Identify all AI Actors (developers, users, auditors) and their roles.
- Draft an `ai-governance-policy.md` if it does not exist.
- Verify legal, safety, and compliance parameters before writing code.

### STEP 2: MAP (Context & Risk Identification)
- Document the precise operational context, intended end-users, and system limitations.
- Map out potential third-party supply chain risks (e.g., base model vulnerabilities, API dependencies).
- Classify potential socio-technical impacts and downstream harms using a risk register file (`ai-risk-register.json`).

### STEP 3: MEASURE (Analysis & Testing)
- Execute rigorous testing for dataset bias, model drift, and security vulnerabilities.
- Run automated prompt injection and boundary testing for generative AI interfaces.
- Log formal validation metrics to `logs/nist-measurement-report.json`.

### STEP 4: MANAGE (Risk Mitigation)
- Implement architectural guardrails (e.g., input/output sanitization, retrieval-augmented validation).
- Establish automated fallback plans for when the AI operates outside specified reliability bounds.
- Set up active monitoring tools to watch for real-time model failure or drift.

---

## 3. Mandatory Artifact Deliverables
You must verify or generate the following compliance assets in the workspace:
1. `.cline/skills/nist-rmf-ai/compliance-checklist.md` - A running checklist of requirements met.
2. `ai-risk-register.json` - Tracking mapped risks, impact scores, and corresponding mitigation code.
3. `tests/adversarial/` - Explicit unit/integration test suites targeting AI-specific threat vectors.

## 4. Error & Drift Handling
- **If a risk score exceeds acceptable thresholds:** Immediately halt the pipeline, notify the user, and propose a specific technical control (e.g., synthetic data balancing, rigorous input filtering).
- **If an unexpected failure or data leak occurs:** Fall back immediately to a deterministic or safer, lower-risk secondary system.