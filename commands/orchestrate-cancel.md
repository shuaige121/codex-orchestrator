# Cancel Orchestration

Cancel a running orchestration and clean up.

## Instructions

1. Read `~/.claude/codex-orchestrator.local.md`. If it doesn't exist, report "No orchestration state found."

2. If `status` is not `running`, report "Orchestration is not running (status: {status})."

3. Kill any running codex processes for this orchestration:
   ```bash
   # Find and kill codex exec processes
   pkill -f "codex exec" 2>/dev/null || true
   ```

4. Read `{run_dir}/plan.md`. Change any `[-]` (running) tasks to `[!]` (failed).

5. Append to plan.md:
   ```
   ## Orchestration Cancelled
   Cancelled by user at {ISO timestamp}.
   ```

6. Update `~/.claude/codex-orchestrator.local.md`: change `status: running` to `status: cancelled`.

7. Report:
   ```
   Orchestration cancelled.
   - Run dir: {run_dir}
   - Running tasks marked as failed.
   - Codex processes terminated.
   ```
