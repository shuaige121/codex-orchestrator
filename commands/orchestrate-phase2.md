## Phase 2 — Initial Plan

Generate and write `{run_dir}/plan.md` with this **exact** structure:

```
# Loop Plan

## Goal
<goal text>

## Deliverables Contract（交付物合同 — 从任务描述.md 复制）
| ID | 交付物 | 验收标准 | 状态 |
|----|--------|---------|------|
| D1 | <description> | <verification> | PENDING |
| D2 | <description> | <verification> | PENDING |
| D3 | <description> | <verification> | PENDING |

## Stack
选择: <stack_id>
理由: <why this stack was chosen>

## Stack Profile（机能包 — 自动生成，勿手动修改）
<output from `orch.py profile <stack>`>

## Global Contract
<Rules all participants follow — auto-populated from stack coding_rules + coordinator additions>

## Verification Contract
<Copy the stack's verification_sequence section here. Then check the project's own config (package.json scripts, pyproject.toml, Makefile) and add project-specific commands. Workers will use project commands first, falling back to stack profile commands.>

## Executor Contracts
- codex-1: <actionable contract for this executor>
- codex-2: <actionable contract for this executor>
...

## Task Board
- [ ] T1 | owner=codex-1 | <task description>
- [ ] T2 | owner=codex-2 | <task description>
- [ ] T3 | owner=codex-1 | <task description>
...

## Coordinator Decision
DECISION: CONTINUE
NOTE: initial plan created, stack=<stack_id>
```

**Planning rules**:
- Include **4–10** concrete, actionable tasks in the Task Board.
- Every task line **MUST** match: `- [ ] T<number> | owner=<executor> | <description>`
- Distribute tasks across executors to maximize parallelism.
- Verification Contract must include **concrete commands** (e.g. `pytest`, `npm test`, `go build`).
- Tasks should be ordered by dependency — earlier tasks first.
- **Sandbox limitation**: Workers have NO network access and CANNOT install new packages (`uv add`, `npm install`, `pip install`, `cargo add` will fail). If a task requires a new dependency, the coordinator MUST install it during setup (Phase 0.5) or between rounds (outside sandbox). Never assign "install package X" as a worker task.

Write this file using the Write tool.
