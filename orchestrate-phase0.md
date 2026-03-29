## Phase 0 — Stack Selection（硬性 — 不可跳过）

You MUST select a tech stack BEFORE setup. This is not optional.

### Step 1: List available stacks
```
uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py stacks
```

### Step 2: Analyze the workspace
If `--stack` was provided by the user, use it. Otherwise, look at the project files to determine:
- Is this frontend, backend, or fullstack?
- What language/framework is used?
- What existing toolchain is already configured (package.json, pyproject.toml, Cargo.toml, go.mod)?

### Step 3: Select and get profile
Choose the best matching stack. Run:
```
uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py profile <stack_name>
```

Store the profile output — you will inject it into every worker prompt.

**CRITICAL**: If none of the available stacks match the project, you may proceed with a generic profile, but you MUST inform the user and explain why.

---

## Phase 0.5 — Setup

Run the setup command with the selected stack:

```
uv run ~/.claude/plugins/codex-orchestrator-v2/scripts/orch.py setup \
  --workspace <WORKSPACE> --max-workers <MAX_WORKERS> \
  --max-batch <MAX_BATCH> --max-steps <MAX_STEPS> \
  --stack <SELECTED_STACK> \
  [--codex-model <MODEL>]
```

Then read `~/.claude/codex-orchestrator.local.md` to obtain `run_dir`, `workspace`, `executors`, `stack`, and all config values. Store these for later phases.

The setup creates these subdirectories under `{run_dir}`:
- `prompts/` — contract files sent to agents
- `signals/` — signal files returned by agents
- `outputs/` — raw agent output (never read by coordinator)
- `logs/` — legacy, kept for backward compatibility

### Sandbox Verification（硬性 — 不可跳过）

The setup output includes sandbox status. Check it:
- **ACTIVE**: Landlock sandbox is functional. Workers are restricted to writing only to workspace + their TMPDIR. **Network is DISABLED** inside the sandbox — workers cannot download packages. Proceed normally.
- **NOT AVAILABLE**: Landlock is NOT working. Workers will run WITHOUT filesystem sandbox — they can read/write ANY file. **Warn the user** and ask for confirmation before proceeding. If the user declines, abort.

### Pre-install Tools（硬性 — 不可跳过）

The setup output includes a `Pre-install Tools` section with the command to run.
**Workers have NO network access** inside the sandbox — tools like `ruff`, `pyright`, `eslint` must be installed BEFORE launching workers.

**Step 1**: Run the `install_tools` command shown in setup output (installs lint/format/typecheck tools).

**Step 2**: Install project dependencies (so `uv run`, `npx`, `cargo build`, etc. work offline):
```bash
# Python — install project deps into venv
cd {workspace} && uv sync

# Node.js — install node_modules from lockfile
cd {workspace} && npm install

# Rust — pre-fetch crate dependencies
cd {workspace} && cargo fetch

# Go — pre-fetch module dependencies
cd {workspace} && go mod download
```

Only run the commands relevant to the selected stack. This ensures all tools and dependencies are cached locally and accessible without network.
