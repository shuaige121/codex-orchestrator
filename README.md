# codex-orchestrator

A contract-driven multi-agent orchestrator that pairs **Claude Code** as the
coordinator and QA referee with **Codex CLI** workers as executors, mediated by
language-specific **stack profiles** (机能包) so every worker prompt carries
the toolchain rules, verification sequence, and common pitfalls for the target
tech stack.

Built for one-person teams who want to run several Codex workers in parallel
under human-readable governance — every task is recorded, every deliverable
has a verifiable acceptance criterion, and the coordinator never touches
source code directly.

## How it works

```
┌────────────────┐    dispatch      ┌───────────────────┐
│ Claude Code    │ ───────────────► │ Codex CLI workers │
│ (coordinator   │                  │  (executors, run  │
│  + QA referee) │ ◄─────────────── │   --full-auto)    │
└────────┬───────┘    4-line        └───────────────────┘
         │            collect
         ▼
    plan.md  (append-only contract + task board)
```

- **Coordinator** selects the stack, writes the plan, dispatches tasks,
  collects results via a 4-line-per-task contract, and runs QA verification
  against each deliverable. Anti-drift rules prevent the coordinator from
  drifting into developer mode.
- **Executors** are Codex CLI workers running `codex exec --full-auto` with
  the stack profile injected into every prompt. One task per worker, sandboxed
  via Landlock with a per-worker temp dir, `--ephemeral` sessions.
- **QA role** stays with the coordinator — workers are 运动员 (players),
  Claude Code is 裁判 (referee). QA is never delegated to the executors.

## Stack profiles

Each stack provides: toolchain commands, coding rules, verification sequence
(lint / test / build), common pitfalls, and project structure guide. Profiles
live in `stacks/<stack-id>/` and are emitted by `orch.py profile <stack>`.

Available:

| Backend | Frontend | Fullstack | Mobile |
|---|---|---|---|
| `python-backend`, `javascript-backend`, `typescript-backend`, `rust-backend`, `go-backend`, `java-backend`, `cloudflare-workers` | `vue-frontend`, `javascript-frontend`, `typescript-frontend` | `nextjs-fullstack`, `django-fullstack`, `svelte-fullstack` | `react-native-mobile`, `flutter-mobile` |

The profile is selected during `orch.py setup` and is read-only after that —
workers always see the same rules.

## Install

Requires:
- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) (runs `scripts/orch.py` via its
  inline shebang — no venv management needed)
- [Claude Code](https://docs.claude.com/en/docs/claude-code) as the
  coordinator shell
- [Codex CLI](https://github.com/openai/codex) as the executor (`codex`
  on `$PATH`)
- Linux with Landlock LSM available, for sandboxing (verify with
  `uv run scripts/orch.py sandbox-check`)

Clone and smoke-test:

```bash
git clone https://github.com/shuaige121/codex-orchestrator.git
cd codex-orchestrator
uv run scripts/orch.py stacks          # list profiles
uv run scripts/orch.py sandbox-check   # verify Landlock
```

Slash commands are exposed by copying or symlinking the top-level
`orchestrate*.md` and `clco.md` files into a directory Claude Code loads as
skills (typically `~/.claude/commands/` or a per-project
`.claude/commands/`).

## Usage

Typical loop, from inside Claude Code:

```
/clco2 "build a CLI that wraps the PDF-signer library with a watch mode" --stack python-backend
```

Under the hood this runs:

1. `orch.py setup --workspace . --stack python-backend` — scaffolds
   `.claude_codex_runs/<timestamp>/` with `plan.md` and a fresh `logs/` dir.
2. Phase 1 — coordinator drafts the Deliverables Contract (D1, D2, ...)
   with verifiable acceptance criteria.
3. Phase 2 — coordinator breaks work into tasks, assigns to workers,
   recorded on the task board inside `plan.md`.
4. Phase 3 — dispatch loop. `orch.py advise plan.md` returns a zone-based
   batch recommendation; `orch.py batch logs/ <round>` collects 4-line
   per-task summaries back into `plan.md`.
5. Phase 3.10 — QA run. Coordinator executes the stack's verification
   commands (lint/test/build) and verifies each deliverable against its
   acceptance criterion. Failures become targeted fix tasks; the loop
   continues until every deliverable passes.
6. Phase 4 — emit the Contract Status Report. The caller only reads this
   report; no code reading is required.

Status / cancel:

```
/orchestrate-status
/orchestrate-cancel
```

## Project layout

```
AGENTS.md                  Architecture, contracts, anti-drift rules
orchestrate*.md            Per-phase slash-command definitions loaded by Claude Code
clco.md                    /clco2 entry point
contracts/                 Role contracts (coder, fixer, reviewer, QA, specialist)
schemas/                   JSON schemas (e.g. worker_result.schema.json)
stacks/                    Stack profiles, one directory per tech stack
templates/                 Reusable snippets injected into prompts
scripts/orch.py            CLI: stacks | profile | setup | advise | batch | collect | status | sandbox-check | memcheck | cleanup
scripts/profiles.py        Stack profile registry
scripts/test_*.py          Tests for orch.py subcommands
```

## Run artifacts

Each invocation creates a timestamped directory:

```
{workspace}/.claude_codex_runs/{timestamp}/
├── 任务描述.md          Initial task description
├── plan.md             Living plan document (contract + task board + logs)
└── logs/
    ├── round01_T1_codex-1_prompt.md    Prompt sent to worker
    ├── round01_T1_codex-1.md           Worker output (NEVER read by coordinator)
    └── ...
```

Old runs are pruned with `orch.py cleanup` (keeps the 5 most recent by
default).

## Security posture

- **Landlock sandbox**: workers run with `--sandbox workspace-write` —
  writes are confined to the workspace dir plus a per-worker
  `/tmp/codex-worker-XXXXXX`.
- **Ephemeral sessions**: `--ephemeral` prevents session state from
  leaking into `~/.codex/memories` across workers.
- **NOTE sanitization**: worker `NOTE` fields are stripped of newlines
  and task-marker patterns before being appended to `plan.md`, so a
  compromised worker can't inject fake completed tasks.
- **Orphan protection**: worker launch templates trap `EXIT INT TERM`
  and kill child processes + clean per-worker tmpdirs.
- **Parallel-safe**: tasks that run package managers (`npm install`,
  `pip install`, etc.) are excluded from parallel batches to avoid
  lockfile corruption.

## License

No license file is currently included — treat this repository as
all rights reserved until one is added. Open an issue if you need a
specific license attached for a fork or integration.
