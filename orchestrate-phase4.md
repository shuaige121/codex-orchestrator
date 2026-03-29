## Phase 4 — Completion & Contract Report

> **Note**: In v3, this phase is executed by the Coordinator 分身 (coordinator-loop.md Step 7), not by the main Claude session. This file serves as the report format reference.

1. Read `{run_dir}/checklist.md` to get final state.
2. Run `uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py checklist-status "{run_dir}/checklist.md"` to get task counts.
3. Update `~/.claude/codex-orchestrator.local.md`: change `status: running` to `status: completed`.
4. Update checklist.md Meta: change `status: RUNNING` to `status: COMPLETED`.
5. Write `{run_dir}/report.md` with the **Contract Status Report**:

```
## Orchestration Complete

### Contract Status（交付物验收报告）
| ID | Deliverable | Criterion | Status |
|----|------------|-----------|--------|
| D1 | <description> | <criterion> | PASS |
| D2 | <description> | <criterion> | PASS |
| D3 | <description> | <criterion> | FAIL: <reason> |

### QA Summary
- Code Review (Codex): PASS/FAIL
- Code Review (Claude): PASS/FAIL
- Runtime (lint/test/build): PASS/FAIL
- Acceptance Test: PASS/FAIL

### Summary
- Deliverables: {passed}/{total} passed
- QA Status: PASS / FAIL
- Tasks: {done} done / {failed} failed / {total} total
- Run directory: {run_dir}
- Checklist: {run_dir}/checklist.md
- Signals: {run_dir}/signals/
```

6. Create marker file: `touch "{run_dir}/.completed"`

**CRITICAL**: This Contract Status Report is the **ONLY output the main agent needs to see**.
The main agent runs `cat {run_dir}/report.md` to get the result. No code reading required.
If all deliverables are PASS, the job is done. If any are FAIL, the report explains why.
