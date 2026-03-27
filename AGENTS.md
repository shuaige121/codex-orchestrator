# Codex Orchestrator v2 — Agent Conventions

## Architecture

- **Coordinator**: Claude Code itself. Selects stack, reads plan, picks tasks, dispatches workers, collects results, makes decisions, and performs QA verification.
- **Executors**: Codex CLI workers (`codex exec --full-auto`). Each runs one task at a time, with language-specific skill pack (机能包) injected into their prompt.
- **QA Role**: The Coordinator (Claude Code) acts as the independent QA reviewer after all coding tasks complete. Workers are "运动员" (players), Claude Code is "裁判" (referee). QA is NEVER delegated to Codex workers.

## Stack Profiles (机能包)

Before any work begins, the coordinator MUST select a tech stack. Available stacks:
- `python-backend`, `vue-frontend`, `javascript-frontend`, `javascript-backend`, `typescript-frontend`, `typescript-backend`, `nextjs-fullstack`, `rust-backend`, `go-backend`, `django-fullstack`, `java-backend`, `react-native-mobile`, `svelte-fullstack`

Each stack provides: toolchain commands, coding rules, verification sequence, common pitfalls, and project structure guide. These are injected into every worker prompt.

## File Structure

Per run, under `{workspace}/.claude_codex_runs/{timestamp}/`:

```
├── 任务描述.md          # Task description (created once)
├── plan.md             # Living plan document (append-only logs)
└── logs/
    ├── round01_T1_codex-1_prompt.md   # Prompt sent to worker
    ├── round01_T1_codex-1.md          # Worker output (NEVER read directly by coordinator)
    └── ...
```

## plan.md Structure

```
## Goal
## Deliverables Contract  # D1, D2, D3... with verifiable acceptance criteria + status
## Stack                  # Selected stack ID + rationale
## Stack Profile          # Auto-generated from orch.py profile (read-only)
## Global Contract
## Verification Contract
## Executor Contracts
## Task Board
## Coordinator Decision
## QA Verification        # Added after Phase 3.10 — contract-based verification results
```

## Task Line Format

```
^- \[(?P<status>[ x!\-])\] (?P<id>T\d+) \| owner=(?P<owner>[A-Za-z0-9_-]+) \| (?P<title>.+)$
```

Status: ` ` pending, `-` running, `x` done, `!` failed

## Deliverables Contract

Phase 1 defines a contract with numbered deliverables (D1, D2, ...), each with verifiable acceptance criteria.
Phase 3.10 QA verifies each deliverable. Phase 4 reports contract status.
**The caller only reads the Contract Status Report — no code reading needed.**

## QA Verification Flow

After all coding tasks complete, the Coordinator runs QA directly (Phase 3.10):
1. **Run verification commands** from the stack profile on the actual project (lint, test, build)
2. **Verify each deliverable** against its acceptance criteria from the contract
3. **Check cross-task integration** — imports, naming consistency, regressions
4. **All deliverables PASS** → Phase 4 (Contract Status Report)
5. **Any deliverable FAILS** → Create targeted fix tasks, return to orchestration loop

## Context Protection Rules

- **NEVER** read worker output files directly — use `orch.py batch` or `orch.py collect` (4-line hard contract)
- **ALWAYS** run `orch.py advise` before each batch — follow the zone recommendation
- Worker output stays on disk, never enters coordinator context
- During QA (Phase 3.10), the coordinator MAY read specific source files for deliverable verification only

## Coordinator Boundaries (Anti-Drift)

The coordinator is a **project manager**, not a developer. Hard rules:
- **NEVER** read source code during Phase 3 (dispatch phase). Create analysis tasks instead.
- **NEVER** edit/create source files. Even 1-line fixes go through Codex workers.
- **NEVER** read worker output files. Use `orch.py batch` (4-line contract).
- **NEVER** think "this is simple, I'll do it myself". Create a task.
- Phase 3.10 QA: MAY run verification commands and read specific files for deliverable checks.
- Self-check: "Am I about to read/write a non-plan file during Phase 3?" → STOP, create task.

## CLI Commands

- `orch.py stacks` — list available stack profiles
- `orch.py profile <stack>` — output full stack profile as markdown
- `orch.py setup --stack <stack> ...` — initialize run with selected stack
- `orch.py advise <plan.md> [--max-batch N]` — zone-based batch recommendation (JSON). Use --max-batch to avoid reading global state file.
- `orch.py batch <logs_dir> <round>` — collect results (4 lines per task)
- `orch.py collect <output_file> <task_id>` — collect single task result
- `orch.py status <plan.md>` — compact task board summary
- `orch.py memcheck` — memory status and safe worker estimate
- `orch.py sandbox-check` — verify Landlock sandbox is functional (JSON output, exit 1 if unavailable)
- `orch.py cleanup [--workspace DIR] [--keep N] [--all]` — clean up old run directories (keeps 5 most recent by default)

## Security

### Sandbox (Landlock)
- Workers run with `--full-auto` which enables `--sandbox workspace-write` (Landlock on Linux)
- **Write restriction**: Workers can ONLY write to the workspace directory and their per-worker TMPDIR
- **Per-worker TMPDIR**: Each worker gets a unique `/tmp/codex-worker-XXXXXX` directory — prevents cross-worker temp file interference
- **Ephemeral sessions**: Workers run with `--ephemeral` — no session files persisted to `~/.codex/memories` (prevents shared state pollution)
- **Sandbox verification**: `orch.py setup` checks Landlock availability at startup and warns if sandbox is NOT functional
- **`orch.py sandbox-check`**: Standalone command to verify sandbox status (tests Landlock syscall directly)

### Other Protections
- **NOTE sanitization**: Worker NOTE field is sanitized before output — newlines flattened, markdown task patterns stripped, TASK_STATUS patterns neutralized. Prevents plan.md injection via malicious worker output.
- **Orphan protection**: Worker launch template includes `trap cleanup EXIT INT TERM` to kill all child workers and clean up temp dirs when the coordinator shell exits.
- **Lock file rule**: Tasks that run package managers (npm install, pip install, etc.) must NOT run in parallel.

## Slash Commands

- `/clco2 <goal> [--stack STACK] [--flags]` — start v2 orchestration
- `/orchestrate-status` — check current status
- `/orchestrate-cancel` — cancel running orchestration

## State File

`~/.claude/codex-orchestrator.local.md` — current run config (workspace, dirs, stack, limits, status).
