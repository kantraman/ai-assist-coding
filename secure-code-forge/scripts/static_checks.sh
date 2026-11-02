#!/usr/bin/env bash
# Run offline pattern scan + complexity check + any installed scanners.
# Usage: bash static_checks.sh <path-to-code>
# Missing tools are reported as SKIPPED, never silently ignored.
TARGET="${1:-.}"
HERE="$(cd "$(dirname "$0")" && pwd)"
have() { command -v "$1" >/dev/null 2>&1; }
section() { printf '\n==== %s ====\n' "$1"; }
skipped=()
has_ext() { find "$TARGET" -type f \( -name "$1" \) -not -path '*/node_modules/*' -not -path '*/.git/*' 2>/dev/null | head -1 | grep -q .; }

section "Built-in pattern scan (offline)"
python3 "$HERE/pattern_scan.py" "$TARGET"

section "Maintainability / complexity"
python3 "$HERE/complexity_check.py" "$TARGET"

if has_ext '*.py'; then
  section "Python tools"
  if have bandit; then bandit -q -r "$TARGET" 2>&1 | tail -n 60; else skipped+=("bandit"); fi
  if have ruff; then ruff check "$TARGET" 2>&1 | tail -n 60; else skipped+=("ruff"); fi
  if have mypy; then mypy --ignore-missing-imports "$TARGET" 2>&1 | tail -n 40; else skipped+=("mypy"); fi
  if have pip-audit && [ -f "$TARGET/requirements.txt" ]; then pip-audit -r "$TARGET/requirements.txt" 2>&1 | tail -n 30; else skipped+=("pip-audit (needs network + requirements.txt)"); fi
fi

if has_ext '*.js' || has_ext '*.ts' || has_ext '*.jsx' || has_ext '*.tsx'; then
  section "JavaScript/TypeScript tools"
  if have eslint; then eslint "$TARGET" 2>&1 | tail -n 60; else skipped+=("eslint"); fi
  if have npm && [ -f "$TARGET/package-lock.json" ]; then (cd "$TARGET" && npm audit --omit=dev 2>&1 | tail -n 30); else skipped+=("npm audit"); fi
fi

if has_ext '*.go'; then
  section "Go tools"
  if have gosec; then gosec -quiet "$TARGET/..." 2>&1 | tail -n 60; else skipped+=("gosec"); fi
  if have go; then (cd "$TARGET" && go vet ./... 2>&1 | tail -n 30); else skipped+=("go vet"); fi
fi

if has_ext '*.rs'; then
  section "Rust tools"
  if have cargo; then (cd "$TARGET" && cargo clippy -q 2>&1 | tail -n 40); else skipped+=("cargo clippy"); fi
fi

if has_ext '*.sh'; then
  section "Shell tools"
  if have shellcheck; then find "$TARGET" -name '*.sh' -not -path '*/.git/*' -exec shellcheck {} + 2>&1 | tail -n 40; else skipped+=("shellcheck"); fi
fi

section "Cross-language scanners"
if have semgrep; then semgrep --config auto --quiet "$TARGET" 2>&1 | tail -n 80; else skipped+=("semgrep"); fi
if have gitleaks; then gitleaks detect --no-git -s "$TARGET" 2>&1 | tail -n 30; else skipped+=("gitleaks"); fi

section "Summary"
if [ ${#skipped[@]} -gt 0 ]; then
  echo "SKIPPED (not installed or unavailable): ${skipped[*]}"
  echo "Mention these in the review summary as 'not checked'."
fi
echo "Tool output is evidence, not verdict: triage each finding."
