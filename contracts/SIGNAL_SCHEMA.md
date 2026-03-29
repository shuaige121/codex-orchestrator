# Signal Protocol Schema (Hardcoded — No Deviations)

## Universal Rules

1. The signal block MUST be the LAST thing in your output. No text after `---END-SIGNAL---`.
2. Every line inside the signal block is `key: value` format. One per line. No blank lines.
3. All text values are single-line (no `\n`), max 200 characters. Truncate with `[...]` if needed.
4. Task ID format: `T` followed by digits only (e.g. `T1`, `T12`). Case-sensitive, uppercase T.
5. Worker name format: `codex-N` or `claude-qa-N` (e.g. `codex-1`, `claude-qa-1`).

## Required Fields (ALL signals must have these)

```
---SIGNAL---
status: <DONE | FAIL | BLOCKED>
task: <T-id, exact value from contract>
worker: <worker-name, exact value from contract>
---END-SIGNAL---
```

## Status-Specific Required Fields

### status: FAIL
```
error: <one-line description, max 200 chars, REQUIRED>
```

### status: BLOCKED
```
blocked_by: <T-id of blocking task, REQUIRED>
```

### status: DONE
No additional required fields for basic tasks.

## Role-Specific Extra Fields (REQUIRED when present)

### coder / fixer
- If status=DONE and type=fix: `fixed: <original T-id>` (REQUIRED)

### reviewer-codex / reviewer-claude
- `review_verdict: <PASS | FAIL>` (REQUIRED)
- `review_details: <D1=PASS D2=FAIL:reason>` (REQUIRED, space-separated, max 500 chars)

### qa-runtime
- `lint: <PASS | FAIL | SKIP>` (REQUIRED)
- `test: <PASS | FAIL | SKIP>` (REQUIRED)
- `build: <PASS | FAIL | SKIP>` (REQUIRED)
- `fail_details: <semicolon-separated summaries, or "none">` (REQUIRED)

### acceptance
- `acceptance: <D1=PASS D2=FAIL:reason>` (REQUIRED, space-separated, max 500 chars)

### specialist
- `diagnosis: <one-line root cause, max 200 chars>` (REQUIRED)
- `fix_applied: <yes | no>` (REQUIRED)
- If fix_applied=no: `fix_plan: <one-line, max 200 chars>` (REQUIRED)
- If fix_applied=no: `fix_files: <comma-separated paths>` (REQUIRED)

## Parsing Rules (for orch.py extract-signal)

1. Scan output for `---SIGNAL---` ... `---END-SIGNAL---` delimiters
2. If not found: `status=UNKNOWN, error="No signal block found"`
3. If `status` field missing: `status=UNKNOWN, error="Missing status field"`
4. If status=FAIL and `error` field missing: append `error: unspecified failure`
5. Treat UNKNOWN as FAIL in all coordinator logic
