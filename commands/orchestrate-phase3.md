## Phase 3 — Orchestration Loop

> **PHASE 3 RULES**: Do NOT read source code. Do NOT read worker output files. Do NOT fix code yourself. All coding work goes through `codex exec` workers. Use `orch.py batch` for results (4-line contract only). If you catch yourself about to read a non-plan file, STOP and create a task instead.

Initialize `round_num = 1`. Execute rounds 1 through `max_steps`. Increment `round_num` at the start of each iteration. For each round:

### 3.1 Read Current State

Read `{run_dir}/plan.md`. Extract:
- The **Task Board** section (all lines matching `- [<status>] T<id> | owner=<owner> | <title>`)
- **Executor Contracts** section
- **Verification Contract** section
- Task counts: pending=`[ ]`, running=`[-]`, done=`[x]`, failed=`[!]`

### 3.2 Handle No Pending Tasks

If **zero pending tasks**:

1. If failed tasks exist, auto-create fix tasks:
   For each `[!]` task, add: `- [ ] T<next_id> | owner=<same_owner> | Fix/retry: <original_title>`
   Insert new lines at the end of the Task Board section in plan.md.

2. Make a decision:
   - **QA** — all tasks done, no failures → proceed to QA verification (Phase 3.10)
   - **CONTINUE** — new fix tasks were added, keep going
   - **TEST** — need to run verification → add a verification task for a codex worker
   - **DEBUG** — issues need investigation → add debug tasks

3. Append to plan.md:
   ```
   ## Round {N} Coordinator Decision
   DECISION: <decision>
   NOTE: <explanation>
   ```

4. If QA and no pending/failed tasks → **exit loop**, go to Phase 3.10 (QA).

If pending tasks exist → continue to 3.3.

### 3.3 Run Advise（硬性 — 必须遵守）

Before picking tasks, run the advise command to get zone-based throttling recommendation:

```
uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py advise "{run_dir}/plan.md" --max-batch {max_batch}
```

This returns JSON with `zone` and `recommended_batch`. You **MUST** follow the recommendation:
- **GREEN**: full speed — use `recommended_batch` as batch size
- **YELLOW**: half speed — use `recommended_batch` (already halved)
- **RED**: serial — run 1 task at a time
- **HALT**: **STOP immediately**. Tell the user to split the goal into smaller sub-goals.
- **DONE**: all tasks complete — exit loop, go to Phase 3.10 (QA). Never skip QA.

If `recommended_batch` is 0 and reason contains "WAITING": tasks are still running but none are pending. **Do NOT dispatch new tasks.** Wait for the running tasks to complete (re-run `orch.py batch` to collect results), then loop back to Phase 3.1.

**You may NOT override the recommended batch size.** The advise command also applies memory-based throttling.

### 3.4 Pick Batch

Select up to `recommended_batch` (from advise output) pending tasks:
1. **First pass**: pick one task per distinct executor (maximize parallelism).
2. **Second pass**: fill remaining slots from leftover pending tasks.
3. **File conflict check**: do NOT run two tasks that modify the same file in the same batch. Detection: read each task's title and description — if two tasks mention the same file or directory path, they conflict. When unsure, be conservative and schedule them in separate rounds.
   - **Git workspace safety**: All workers share the same workspace directory. Parallel workers that edit different files are safe. If tasks might touch overlapping files (e.g., package.json, shared configs, lock files), schedule them sequentially.
   - **Lock file rule**: Tasks that run `npm install`, `pip install`, or other package managers MUST NOT run in parallel — they can corrupt lock files.
4. Update plan.md: change each selected task from `[ ]` to `[-]` (running).

### 3.5 Write Prompt Files

For **each task** in the batch, write a prompt file at:
`{logs_dir}/round{NN}_{task_id}_{owner}_prompt.md`

(where `{NN}` is the zero-padded round number, e.g. `01`, `02`)

Prompt file content:

```
You are Codex executor {owner}.

Goal:
{goal}

## Stack Profile（机能包）
{stack profile content from orch.py profile output}

## 验证要求（硬性 — 完成代码后必须执行）
{verification_sequence from the stack profile}

Executor contract:
{contract for this executor from the Executor Contracts section}

Current task board snapshot:
{full Task Board text}

Current task:
{task_id} | owner={owner} | {title}

Requirements:
1. Execute ONLY this task. Do not touch other tasks.
2. Follow the coding rules from the Stack Profile above.
3. **SANDBOX CONSTRAINT**: You have NO network access. Do NOT run `uv add`, `pip install`, `npm install`, `cargo add`, or any command that downloads packages. All dependencies and tools are pre-installed. Use only what is already available.
4. After code changes, run the verification sequence with this priority:
   a. FIRST: Check the project's own config (package.json "scripts", pyproject.toml, Cargo.toml, Makefile)
      for existing lint/test/build/format commands. USE THOSE if they exist (e.g. `npm run lint`, `uv run pytest`).
   b. SECOND: If the project has NO equivalent command, use the profile's toolchain command as fallback.
   c. SKIP: If a tool is completely irrelevant (e.g. TypeScript checker on a JavaScript project),
      skip that step entirely. Do NOT install tools that aren't in the project.
   d. If lint/format changes files, that's expected — re-stage before committing.
5. If tests fail, fix the code and re-run.
6. Keep your final response SHORT. Use ONLY this format:
   TASK_STATUS: DONE or FAILED
   TASK_ID: {task_id}
   OWNER: {owner}
   NOTE: one short sentence describing what was done or what failed
```

### 3.6 Launch Workers in Parallel

**Step 1**: Get executor configuration:
```
uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py executor-info
```
This returns JSON with `worker_cmd` (command template), `env_setup`, and `extra_flags_*`.

**Step 2**: Build and run a **single Bash command** that launches all batch workers in parallel.

For each worker, construct the command by substituting variables in the `worker_cmd` template:
- `{timeout}` → `worker_timeout` from state file
- `{workspace}` → workspace path
- `{output}` → `{logs_dir}/round{NN}_{task_id}_{owner}.md`
- `{prompt}` → `{logs_dir}/round{NN}_{task_id}_{owner}_prompt.md`
- `{tmpdir}` → per-worker TMPDIR (from `mktemp -d /tmp/codex-worker-XXXXXX`)
- `{extra_flags}` → model flag (`extra_flags_model` if codex_model set) + no-git flag if needed
- `{env_setup}` → from executor config

Template (adapt for the actual batch):

```bash
# Round {N} — launch {batch_size} workers
WORKER_PIDS=()
WORKER_TMPDIRS=()
cleanup() {
  for p in "${WORKER_PIDS[@]}"; do kill "$p" 2>/dev/null; done
  for d in "${WORKER_TMPDIRS[@]}"; do rm -rf "$d" 2>/dev/null; done
}
trap cleanup EXIT INT TERM

# Worker 1 — substitute {worker_cmd} template from executor-info
TMPDIR_W1=$(mktemp -d /tmp/codex-worker-XXXXXX); WORKER_TMPDIRS+=("$TMPDIR_W1")
{rendered_worker_cmd_1} &
PID1=$!; WORKER_PIDS+=($PID1)

# Worker 2
TMPDIR_W2=$(mktemp -d /tmp/codex-worker-XXXXXX); WORKER_TMPDIRS+=("$TMPDIR_W2")
{rendered_worker_cmd_2} &
PID2=$!; WORKER_PIDS+=($PID2)
# ... one line per task in batch ...

# Wait and collect exit codes
wait $PID1; echo "RESULT:{T1}:$?"
wait $PID2; echo "RESULT:{T2}:$?"
```

If `codex_model` is set, include the executor's `extra_flags_model` template (substituting `{model}`).

If `{workspace}` is NOT inside a git repository, include `extra_flags_no_git` from the executor config.

Use `run_in_background: true` for this Bash command with `timeout: 600000` since workers may take several minutes.

> **Sandbox policy**: Depends on executor backend. For `codex`: `--full-auto` enables Landlock sandbox, restricting workers to workspace + TMPDIR. **Network is DISABLED**. For `claude`: no sandbox by default, use with caution.

> **Pre-installed tools**: Because network may be disabled in sandbox, ALL tools must be installed BEFORE launching workers. The coordinator runs `install_tools` from the stack profile during Phase 0.5.

> **Sandbox-safe cache**: For Codex executor, `XDG_CACHE_HOME` is set to each worker's TMPDIR. Do NOT set `CARGO_HOME`, `GOPATH`, or `GRADLE_USER_HOME` to TMPDIR.

> **Per-worker TMPDIR isolation**: Each worker gets a unique `/tmp/codex-worker-XXXXXX` directory. The `cleanup` function removes all worker TMPDIRs on exit.

> **Orphan protection**: `trap cleanup EXIT INT TERM` ensures child processes are terminated on exit.

> **Per-worker timeout**: Each worker is wrapped in `timeout {worker_timeout}` (from state file, default 540s, configurable via `--worker-timeout`). Set outer Bash timeout to `worker_timeout + 60s` for margin.

### 3.7 Collect Results（上下文保护 — 绝不直接读 worker 输出）

After the Bash command completes, use `orch.py batch` to collect results safely:

```
uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py batch "{logs_dir}" {round_num}
```

This outputs **exactly 4 lines per task** (the hard contract), blank-line separated:
```
TASK_STATUS: DONE or FAILED
TASK_ID: T1
OWNER: codex-1
NOTE: one sentence summary (max 150 chars)
```

**NEVER read worker output files directly** — they can be huge and blow up your context window. The `batch` command extracts only the structured status from the last 30 lines of each output file.

For each task result:
1. Parse TASK_STATUS from the batch output.
2. Update plan.md based on status:
   - **DONE** → change `[-]` to `[x]`
   - **FAILED** → change `[-]` to `[!]`
   - **UNKNOWN** → treat as FAILED, change `[-]` to `[!]`. The NOTE explains why (file missing, too large, no structured output). Create a retry task in Phase 3.8.
3. If a **fix task** (title starts with "Fix/retry:") completed as DONE, also update the **original failed task** from `[!]` to `[x]`. This ensures the failed count drops and `advise` can reach DONE zone.
4. Append a one-line log to plan.md:
   ```
   Round {N}: {task_id} -> {STATUS} -- {NOTE}
   ```

### 3.8 Coordinator Decision

After processing all worker results for this round:

1. Re-read the updated Task Board.
2. Count remaining pending, done, failed tasks.
3. Review the 4-line batch summaries from Phase 3.7 for context (NEVER read worker output files directly).
4. Decide:
   - **CONTINUE** — more pending tasks, or you created new tasks
   - **TEST** — want to run verification checks → create a verification task
   - **DEBUG** — issues found → create investigation/fix tasks
   - **QA** — all tasks complete, no failures → exit loop, proceed to Phase 3.10

5. If you create new tasks, append them to the Task Board in plan.md:
   `- [ ] T<next_id> | owner=<executor> | <description>`
   Use the next available T-number (scan existing IDs to find max, then +1).

6. Append decision to plan.md:
   ```
   ## Round {N} Coordinator Decision
   DECISION: <decision>
   NOTE: <explanation>

   ## Round {N} New Tasks
   <new task lines, if any>
   ```

7. If QA and no pending tasks remain → exit loop, proceed to Phase 3.10.

### 3.9 Loop Termination

- If round reaches `max_steps` without completing, append to plan.md:
  ```
  ## Orchestration Ended
  Reached max_steps ({max_steps}). Stopping.
  ```
  Then proceed to Phase 3.10 QA (even on timeout, run QA to assess current state).
