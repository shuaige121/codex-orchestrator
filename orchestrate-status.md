# Orchestration Status

Check the current status of a running or completed orchestration.

## Instructions

1. Read `~/.claude/codex-orchestrator.local.md`. If it doesn't exist, report "No orchestration state found."

2. Extract `run_dir`, `status`, `timestamp`, `workspace`, and config values.

3. Check for checklist (v3) or plan (v2):
   - If `{run_dir}/checklist.md` exists → use v3 status method
   - If `{run_dir}/plan.md` exists → use v2 status method (legacy)
   - If neither exists → report "No checklist or plan file found."

### v3 Status (checklist.md)

Run:
```bash
uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py checklist-status "{run_dir}/checklist.md"
```

Parse the JSON and present:

```
## Orchestration Status

- Status: {status from checklist Meta section}
- Started: {timestamp}
- Workspace: {workspace}
- tmux session: {tmux_session from Meta, if any}

### Task Board
- Pending: {count}
- Running: {count}
- Done: {count}
- Failed: {count}
- Total: {count}
- Ready to dispatch: {ready list}

### Deliverables
{Deliverables Contract table from checklist}

### Recent Log
{last 10 lines from Log section}

### Files
- Checklist: {run_dir}/checklist.md
- Task Description: {run_dir}/任务描述.md
- Signals: {run_dir}/signals/
- Report: {run_dir}/report.md (if completed)

### tmux
- Attach: tmux attach -t {tmux_session}
- Kill: tmux kill-session -t {tmux_session}
```

### v2 Status (plan.md) — Legacy

Run:
```bash
uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py status "{run_dir}/plan.md"
```

Present the output as-is.
