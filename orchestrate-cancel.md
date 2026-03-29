# Cancel Orchestration

Cancel a running orchestration and clean up.

## Instructions

1. Read `~/.claude/codex-orchestrator.local.md`. If it doesn't exist, report "No orchestration state found."

2. If `status` is not `running`, report "Orchestration is not running (status: {status})."

3. Kill the tmux session (v3) and any worker processes:
   ```bash
   # Kill tmux session if it exists
   TMUX_SESSION=$(grep 'tmux_session' {run_dir}/checklist.md 2>/dev/null | sed 's/.*: //')
   if [ -n "$TMUX_SESSION" ]; then
     tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
   fi

   # Kill any running codex/claude worker processes
   pkill -f "codex exec" 2>/dev/null || true
   pkill -f "claude.*--bare" 2>/dev/null || true
   ```

4. Update state:
   - If `{run_dir}/checklist.md` exists (v3):
     - Change any RUNNING tasks to FAIL
     - Append to Log: `<ISO timestamp> | cancelled by user`
     - Update Meta `status: CANCELLED`
   - If `{run_dir}/plan.md` exists (v2 legacy):
     - Change any `[-]` (running) tasks to `[!]` (failed)
     - Append: `## Orchestration Cancelled`

5. Update `~/.claude/codex-orchestrator.local.md`: change `status: running` to `status: cancelled`.

6. Report:
   ```
   Orchestration cancelled.
   - Run dir: {run_dir}
   - tmux session killed: {tmux_session}
   - Running tasks marked as failed.
   - Worker processes terminated.
   ```
