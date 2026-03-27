## Phase 4 — Completion & Contract Report

1. Run `uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py status "{run_dir}/plan.md"` to get final task counts.
2. Update `~/.claude/codex-orchestrator.local.md`: change `status: running` to `status: completed`.
3. Present the **Contract Status Report** to the caller:

```
## Orchestration Complete

### Contract Status（交付物验收报告）
| ID | 交付物 | 验收标准 | 状态 |
|----|--------|---------|------|
| D1 | <description> | <criterion> | ✅ PASS |
| D2 | <description> | <criterion> | ✅ PASS |
| D3 | <description> | <criterion> | ❌ FAIL: <reason> |

### Summary
- Deliverables: {passed}/{total} passed
- QA Status: PASS / FAIL
- Rounds executed: {N}
- Tasks: {done} done / {failed} failed / {total} total
- Plan: {run_dir}/plan.md
- Logs: {logs_dir}/
```

**CRITICAL**: This Contract Status Report is the **ONLY output the main agent needs to see**.
The main agent does NOT need to read any code, worker outputs, or detailed logs.
If all deliverables are PASS, the job is done. If any are FAIL, the report explains why.
