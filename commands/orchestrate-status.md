# Orchestration Status

Check the current status of a running or completed orchestration.

## Instructions

1. Read `~/.claude/codex-orchestrator.local.md`. If it doesn't exist, report "No orchestration state found."

2. Extract `run_dir`, `status`, `timestamp`, `workspace`, and config values.

3. Read `{run_dir}/plan.md`. If it doesn't exist, report "Plan file not found at {run_dir}/plan.md."

4. Extract the **Task Board** section. Count tasks by status:
   - `[ ]` = pending
   - `[-]` = running
   - `[x]` = done
   - `[!]` = failed

5. Extract the latest **Coordinator Decision** section (the last `## Round N Coordinator Decision` block).

6. List log files in `{run_dir}/logs/` using `ls -lt` to show most recent first.

7. Present a summary:

```
## Orchestration Status

- Status: {status}
- Started: {timestamp}
- Workspace: {workspace}
- Config: {max_workers} workers, {max_batch} batch, {max_steps} max steps

### Task Board
- Pending: {count}
- Running: {count}
- Done: {count}
- Failed: {count}
- Total: {count}

### Latest Decision
{last decision block}

### Recent Logs
{last 10 log files}

### Files
- Plan: {run_dir}/plan.md
- Task Description: {run_dir}/任务描述.md
- Logs: {run_dir}/logs/
```
