## Phase 2 — Generate Checklist (Hardcoded Format — No Deviations)

Generate and write `{run_dir}/checklist.md` with this **exact** structure.

### Checklist Template

```markdown
# Orchestration Checklist

## Meta
- goal: <goal text>
- workspace: <workspace path>
- stack: <stack_id>
- run_dir: <run_dir path>
- tmux_session: (filled at handoff)
- max_workers: <N>
- max_batch: <N>
- started: <ISO timestamp>
- status: PENDING

## Deliverables Contract
| ID | Deliverable | Criterion | Status |
|----|------------|-----------|--------|
| D1 | <description> | <verification command/check> | PENDING |
| D2 | <description> | <verification command/check> | PENDING |

## Stack
- ID: <stack_id>
- Rationale: <why this stack was chosen>

## Verification Commands
- Lint: <command>
- Test: <command>
- Build: <command>

## Task Board
| Task | Type | Description | Deps | Status | Worker | Signal | Retries |
|------|------|------------|------|--------|--------|--------|---------|
<coding tasks T1..TN>
<QA tasks — see formula below>

## Log
- <ISO timestamp> | checklist created, awaiting handoff
```

### Coding Tasks (T1 through TN)

Generate coding tasks with these rules:

```
TASK_COUNT = max(4, min(10, num_deliverables * 2))

FOR i in 1..TASK_COUNT:
  task_id = "T<i>"
  type = "code"
  status = "PENDING"
  worker = "-"
  signal = "-"
  retries = 0
  deps:
    IF task has no prerequisites: "-"
    ELSE: comma-separated T-ids (uppercase T, digits only, no spaces)
```

Task distribution across workers (hardcoded round-robin):
```
FOR each coding task T<i>:
  preferred_worker = "codex-" + (((i - 1) % max_workers) + 1)
```

### QA Tasks (Hardcoded — Always Exactly 4, Always After All Coding Tasks)

```
N = number of coding tasks
all_coding_deps = "T1,T2,...,TN"  (comma-joined, no spaces)

QA TASK 1:
  | T<N+1> | qa-review-codex | Cross-review: code quality and correctness | <all_coding_deps> | PENDING | - | - | 0 |

QA TASK 2:
  | T<N+2> | qa-review-claude | Cross-review: architecture and integration | <all_coding_deps> | PENDING | - | - | 0 |

QA TASK 3:
  | T<N+3> | qa-runtime | Runtime verification: lint + test + build | T<N+1>,T<N+2> | PENDING | - | - | 0 |

QA TASK 4:
  | T<N+4> | qa-accept | Acceptance test: verify deliverables contract | T<N+3> | PENDING | - | - | 0 |
```

**No variations allowed.** Always 4 QA tasks. Always these exact types, descriptions, and dependency chain:
- Review codex + Review claude (parallel, both depend on all coding tasks)
- Runtime (depends on both reviews)
- Accept (depends on runtime)

### Dependency Format (Hardcoded)

```
VALID: T1 | T1,T2 | T1,T2,T3 | -
INVALID: T1, T2 (space after comma) | t1 (lowercase) | T1;T2 (semicolon) | none | N/A
```

Regex: `^(T\d+,)*T\d+$` or exactly `-`

### Task Types (Hardcoded — Coordinator Maps These to Contract Templates)

| Type | Created by | Contract template |
|------|-----------|-------------------|
| `code` | Phase 2 planning | `coder.contract.md` |
| `qa-review-codex` | Phase 2 planning | `reviewer-codex.contract.md` |
| `qa-review-claude` | Phase 2 planning | `reviewer-claude.contract.md` |
| `qa-runtime` | Phase 2 planning | `qa-runtime.contract.md` |
| `qa-accept` | Phase 2 planning | `acceptance.contract.md` |
| `fix` | Coordinator (dynamic) | `fixer.contract.md` |
| `specialist` | Coordinator (dynamic) | `specialist.contract.md` |

### Deliverables Criterion Format (Hardcoded Patterns)

Each criterion MUST match one of these patterns:

```
PATTERN 1 — Run command, check exit code:
  "运行 `<command>` 成功退出 (exit 0)"
  Example: "运行 `uv run pytest tests/test_auth.py` 成功退出 (exit 0)"

PATTERN 2 — File exists with content:
  "文件 `<path>` 存在且包含 `<text>`"
  Example: "文件 `src/models/user.py` 存在且包含 `class User`"

PATTERN 3 — Command output contains text:
  "运行 `<command>` 输出包含 `<text>`"
  Example: "运行 `python main.py` 输出包含 `hello world`"
```

Criteria that don't match a pattern are REJECTED. Rewrite them to match.

---

### Also Generate coordinator-vars.json

Write `{run_dir}/coordinator-vars.json` with ALL these fields (all REQUIRED):

```json
{
  "run_dir": "<exact run_dir path>",
  "workspace": "<exact workspace path>",
  "stack_name": "<stack_id>",
  "max_workers": "<N>",
  "max_batch": "<N>",
  "worker_timeout": "<from state file, default 540>",
  "orch_py": "~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py",
  "contracts_dir": "~/.claude/plugins/codex-orchestrator-v2/contracts",
  "executor_info": "<exact JSON output of orch.py executor-info>",
  "stack_profile": "<exact output of orch.py profile <stack>>",
  "extra_flags": "<IF codex_model set: '--model <model>', ELSE: ''>"
}
```

### Also Create Subdirectories

```bash
mkdir -p {run_dir}/prompts {run_dir}/signals {run_dir}/outputs
```

(These may already exist from `orch.py setup`, but mkdir -p is idempotent.)

Write the checklist using the Write tool.
