# /// script
# requires-python = ">=3.10"
# ///
"""
clco orchestrator v2 CLI — orchestration plumbing with stack profiles (机能包).

Usage:
    uv run orch.py stacks
    uv run orch.py profile <stack_name>
    uv run orch.py setup   --workspace /path --stack <stack> [--max-workers 4] [--max-batch 4] [--max-steps 50]
    uv run orch.py collect <output_file> <task_id>
    uv run orch.py batch   <logs_dir> <round_num>
    uv run orch.py advise  <plan_md>
    uv run orch.py status  <plan_md>
    uv run orch.py sandbox-check
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Import STACKS from sibling module
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))
from profiles import STACKS  # noqa: E402

# ── Hard limits ──────────────────────────────────────────────────────────────
MAX_WORKERS_HARD = 12
MAX_STEPS_HARD = 50
MAX_TASKS_PER_SESSION = 15
MAX_FIX_TASKS = 5  # max auto-created fix tasks before HALT
NOTE_MAX_CHARS = 150  # truncate worker NOTE to this
FAIL_TAIL_LINES = 10  # lines to show on failure
MAX_OUTPUT_FILE_BYTES = 10_000_000  # 10MB — skip files larger than this
WORKER_TIMEOUT_HARD = 1800  # absolute max: 30 minutes
WORKER_TIMEOUT_DEFAULT = 540  # default: 9 minutes
WORKER_MEM_ESTIMATE_MB_DEFAULT = 500  # default estimated memory per codex worker
WORKER_MEM_ESTIMATE_MB = WORKER_MEM_ESTIMATE_MB_DEFAULT  # mutable at setup time
MEM_RESERVE_MB = 1024  # always keep this much free (OS + Claude Code)

# ── Executor backends ────────────────────────────────────────────────────────
EXECUTORS: dict[str, dict] = {
    "codex": {
        "binary": "codex",
        "description": "OpenAI Codex CLI (codex exec --full-auto)",
        "worker_cmd": (
            '{env_setup} timeout {timeout} codex exec --full-auto --ephemeral '
            '-C "{workspace}" {extra_flags} '
            '--output-last-message "{output}" '
            '"$(cat "{prompt}")"'
        ),
        "env_setup": 'TMPDIR={tmpdir} XDG_CACHE_HOME={tmpdir}/.cache',
        "sandbox_mode": "landlock",
        "extra_flags_model": "--model {model}",
        "extra_flags_no_git": "--skip-git-repo-check",
    },
    "claude": {
        "binary": "claude",
        "description": "Anthropic Claude Code CLI",
        "worker_cmd": (
            '{env_setup} timeout {timeout} claude '
            '--dangerously-skip-permissions -C "{workspace}" {extra_flags} '
            '--output-file "{output}" '
            '-p "$(cat "{prompt}")"'
        ),
        "env_setup": 'TMPDIR={tmpdir}',
        "sandbox_mode": "none",
        "extra_flags_model": "--model {model}",
        "extra_flags_no_git": "",
    },
}
DEFAULT_EXECUTOR = "codex"


def _positive_int(value: str) -> int:
    """argparse type: positive integer (>=1)."""
    try:
        ivalue = int(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError("must be an integer") from e
    if ivalue < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return ivalue


def _atomic_write_text(path: Path, content: str) -> None:
    """Atomically write text to path via temp file + os.replace()."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, path)
        tmp_path = None
    finally:
        if tmp_path and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


# ── Task JSON sidecar ────────────────────────────────────────────────────────
# tasks.json lives alongside plan.md as the structured source of truth for
# task status.  plan.md task board is rendered FROM this file for human
# readability, but parsing (advise, status) reads tasks.json when available.

TASK_STATUSES = {"pending": " ", "running": "-", "done": "x", "failed": "!"}
STATUS_FROM_CHAR = {v: k for k, v in TASK_STATUSES.items()}


def _tasks_json_path(plan_md: Path) -> Path:
    """Return tasks.json path next to plan.md."""
    return plan_md.parent / "tasks.json"


def _load_tasks(plan_md: Path) -> list[dict] | None:
    """Load tasks from tasks.json sidecar. Returns None if not found."""
    p = _tasks_json_path(plan_md)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("tasks", [])
    except (json.JSONDecodeError, OSError):
        return None


def _save_tasks(plan_md: Path, tasks: list[dict], meta: dict | None = None) -> None:
    """Atomically write tasks.json sidecar."""
    data = {"version": 1, "tasks": tasks}
    if meta:
        data["meta"] = meta
    _atomic_write_text(_tasks_json_path(plan_md), json.dumps(data, indent=2, ensure_ascii=False))


def _tasks_to_markdown(tasks: list[dict]) -> str:
    """Render tasks list as markdown task board lines."""
    lines = []
    for t in tasks:
        char = TASK_STATUSES.get(t.get("status", "pending"), " ")
        tid = t.get("id", "T?")
        owner = t.get("owner", "unassigned")
        desc = t.get("description", "")
        lines.append(f"- [{char}] {tid} | owner={owner} | {desc}")
    return "\n".join(lines)


def _count_tasks(tasks: list[dict]) -> dict:
    """Count tasks by status."""
    counts = {"pending": 0, "running": 0, "done": 0, "failed": 0}
    for t in tasks:
        s = t.get("status", "pending")
        if s in counts:
            counts[s] += 1
    return counts


def _parse_tasks_from_markdown(task_scope: str) -> list[dict]:
    """Fallback: parse tasks from plan.md task board text."""
    task_re = re.compile(r"^- \[(.)\] (T\d+) \| owner=(\S+) \| (.+)$", re.MULTILINE)
    tasks = []
    for m in task_re.finditer(task_scope):
        char = m.group(1)
        tasks.append({
            "id": m.group(2),
            "owner": m.group(3),
            "description": m.group(4),
            "status": STATUS_FROM_CHAR.get(char, "pending"),
        })
    return tasks


def _get_tasks(plan_md: Path) -> list[dict]:
    """Get tasks from JSON sidecar, falling back to plan.md parsing."""
    tasks = _load_tasks(plan_md)
    if tasks is not None:
        return tasks
    # Fallback to markdown parsing
    text = plan_md.read_text(encoding="utf-8", errors="replace")
    return _parse_tasks_from_markdown(_task_board_scope(text))


def _task_board_scope(text: str) -> str:
    """Return Task Board section (## Task Board ... next ##), fallback to full text."""
    m = re.search(r"^##\s+Task Board\s*$", text, re.MULTILINE)
    if not m:
        return text
    tail = text[m.end() :]
    next_h2 = re.search(r"^##\s+", tail, re.MULTILINE)
    return tail[: next_h2.start()] if next_h2 else tail


def _check_sandbox() -> dict:
    """Test if Landlock sandbox is functional on this system.

    Uses the landlock_create_ruleset syscall to check if Landlock is available.
    Syscall number: 444 on x86_64/aarch64, 445 on i386.
    Returns dict with 'available' bool and details.
    """
    import ctypes
    import ctypes.util
    import platform
    import struct

    # landlock_create_ruleset syscall number by architecture
    _NR_LANDLOCK = {
        "x86_64": 444,
        "amd64": 444,
        "aarch64": 444,
        "arm64": 444,
        "i386": 445,
        "i686": 445,
        "x86": 445,
        "riscv64": 444,
    }
    arch = platform.machine().lower()
    nr = _NR_LANDLOCK.get(arch)

    result = {"available": False, "backend": "landlock", "details": ""}
    if nr is None:
        result["details"] = f"Unsupported architecture for Landlock check: {arch}"
        return result
    try:
        libc = ctypes.CDLL(None, use_errno=True)
    except OSError:
        libc_path = ctypes.util.find_library("c")
        if not libc_path:
            result["details"] = "Unable to load libc for Landlock check"
            return result
        try:
            libc = ctypes.CDLL(libc_path, use_errno=True)
        except OSError as e:
            result["details"] = f"Unable to load libc ({libc_path}): {e}"
            return result
    try:
        # landlock_create_ruleset(attr, size, flags=0) — ABI v1 fs flags
        attr = struct.pack("QQ", 0x1FFF, 0)
        fd = libc.syscall(nr, attr, len(attr), 0)
        if fd >= 0:
            os.close(fd)
            result["available"] = True
            result["details"] = f"Landlock syscall functional (arch={arch})"
            # Try to get ABI version
            ver = libc.syscall(nr, None, 0, 1)  # LANDLOCK_CREATE_RULESET_VERSION
            if ver > 0:
                result["abi_version"] = ver
        else:
            errno = ctypes.get_errno()
            result["details"] = (
                f"landlock_create_ruleset failed (errno={errno}: {os.strerror(errno)})"
            )
    except Exception as e:
        result["details"] = f"Landlock check error: {e}"
    return result


def _get_memory_info() -> dict:
    """Read memory info from /proc/meminfo (Linux only, no deps).

    Returns dict with keys: total_mb, available_mb, used_mb, usage_pct.
    Returns empty dict on non-Linux or read failure.
    """
    try:
        text = Path("/proc/meminfo").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    info = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            key = parts[0].rstrip(":")
            if key in {"MemTotal", "MemAvailable"}:
                # Values in /proc/meminfo are in kB
                try:
                    val_mb = int(parts[1]) // 1024
                except ValueError:
                    return {}
                if key == "MemTotal":
                    info["total_mb"] = val_mb
                else:
                    info["available_mb"] = val_mb
    if "total_mb" in info and "available_mb" in info:
        try:
            info["used_mb"] = info["total_mb"] - info["available_mb"]
            info["usage_pct"] = round(info["used_mb"] / info["total_mb"] * 100, 1)
            info["max_safe_workers"] = max(
                0, (info["available_mb"] - MEM_RESERVE_MB) // WORKER_MEM_ESTIMATE_MB
            )
        except (ValueError, ZeroDivisionError):
            return {}
    return info


def cmd_stacks(_args: argparse.Namespace) -> None:
    """List all available stack profiles."""
    print("Available Stacks:")
    for stack_id, stack in STACKS.items():
        print(f"  {stack_id:<22s}{stack['name']:<24s}[{stack['category']}]")


def cmd_profile(args: argparse.Namespace) -> None:
    """Output a full stack profile as formatted markdown for worker prompt injection."""
    stack_name = args.stack_name
    if stack_name not in STACKS:
        print(
            f"ERROR: Unknown stack '{stack_name}'. Use 'orch.py stacks' to list available stacks.",
            file=sys.stderr,
        )
        sys.exit(1)

    stack = STACKS[stack_name]
    tc = stack["toolchain"]

    lines = [
        f"## Stack Profile: {stack['name']}",
        "",
        "### Toolchain",
    ]
    for key, cmd in tc.items():
        lines.append(f"- {key}: {cmd}")

    install_tools = stack.get("install_tools", "")
    if install_tools:
        lines += [
            "",
            "### Install Tools (run BEFORE sandbox — network required)",
            "```bash",
            install_tools,
            "```",
        ]

    lines += [
        "",
        "### Coding Rules",
        stack["coding_rules"],
        "",
        "### Verification Sequence",
        stack["verification_sequence"],
        "",
        "### Common Pitfalls",
        stack["common_pitfalls"],
        "",
        "### Project Structure Guide",
        stack["project_structure"],
    ]
    print("\n".join(lines))


def cmd_setup(args: argparse.Namespace) -> None:
    """Phase 0: validate env, create run dir, write state file."""
    executor_name = getattr(args, "executor", DEFAULT_EXECUTOR)
    if executor_name not in EXECUTORS:
        print(
            f"ERROR: Unknown executor '{executor_name}'. "
            f"Available: {', '.join(EXECUTORS.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)
    executor = EXECUTORS[executor_name]

    if not shutil.which(executor["binary"]):
        print(
            f"ERROR: '{executor['binary']}' not found in PATH. Install it first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Guard: warn if another run is active
    state_file = Path.home() / ".claude" / "codex-orchestrator.local.md"
    if state_file.is_file():
        existing = state_file.read_text(encoding="utf-8", errors="replace")
        if "status: running" in existing:
            m_run = re.search(r"run_dir:\s*(.+)", existing)
            active_dir = m_run.group(1).strip() if m_run else "unknown"
            print("WARNING: Another orchestration appears to be running!")
            print(f"  Active run: {active_dir}")
            print(
                "  State file will be overwritten. The previous run's advise/status may break."
            )
            print("  (If the previous run crashed, this is safe to ignore.)")

    # Validate stack
    stack = args.stack
    if stack not in STACKS:
        print(
            f"ERROR: Unknown stack '{stack}'. Use 'orch.py stacks' to list available stacks.",
            file=sys.stderr,
        )
        sys.exit(1)

    workspace = Path(args.workspace).resolve()
    max_workers = max(1, min(int(args.max_workers), MAX_WORKERS_HARD))
    max_batch = max(
        1,
        min(
            int(args.max_batch)
            if args.max_batch is not None and int(args.max_batch) > 0
            else max_workers,
            max_workers,
        ),
    )
    max_steps = max(1, min(int(args.max_steps), MAX_STEPS_HARD))
    codex_model = args.codex_model or ""
    worker_timeout = max(30, min(int(args.worker_timeout), WORKER_TIMEOUT_HARD))
    worker_mem = max(100, int(args.worker_mem))
    # Update the global so advise/memcheck use the configured value
    global WORKER_MEM_ESTIMATE_MB
    WORKER_MEM_ESTIMATE_MB = worker_mem

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = workspace / ".claude_codex_runs" / ts
    logs_dir = run_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    executors = ", ".join(f"codex-{i}" for i in range(1, max_workers + 1))

    state_file = Path.home() / ".claude" / "codex-orchestrator.local.md"
    state_content = (
        f"# Codex Orchestrator State\n\n"
        f"- workspace: {workspace}\n"
        f"- run_dir: {run_dir}\n"
        f"- logs_dir: {logs_dir}\n"
        f"- max_workers: {max_workers}\n"
        f"- max_batch: {max_batch}\n"
        f"- max_steps: {max_steps}\n"
        f"- max_tasks_per_session: {MAX_TASKS_PER_SESSION}\n"
        f"- max_fix_tasks: {MAX_FIX_TASKS}\n"
        f"- codex_model: {codex_model}\n"
        f"- executor: {executor_name}\n"
        f"- executors: {executors}\n"
        f"- stack: {stack}\n"
        f"- worker_timeout: {worker_timeout}\n"
        f"- worker_mem_estimate_mb: {worker_mem}\n"
        f"- timestamp: {ts}\n"
        f"- status: running\n"
    )
    try:
        _atomic_write_text(state_file, state_content)
    except OSError as e:
        print(f"ERROR: Failed to write state file {state_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # ── Sandbox verification ──
    sandbox = _check_sandbox()

    print("=== Codex Orchestrator Setup ===")
    print(f"Workspace:   {workspace}")
    print(f"Run Dir:     {run_dir}")
    print(f"Logs Dir:    {logs_dir}")
    print(f"Stack:       {stack} ({STACKS[stack]['name']})")
    print(f"Max Workers: {max_workers}")
    print(f"Max Batch:   {max_batch}")
    print(f"Max Steps:   {max_steps}")
    print(f"Task Limit:  {MAX_TASKS_PER_SESSION} per session")
    print(f"Fix Limit:   {MAX_FIX_TASKS} auto-fix tasks max")
    print(f"Executor:    {executor_name} ({executor['description']})")
    print(f"Model:       {codex_model or 'default'}")
    print(f"Worker Timeout: {worker_timeout}s ({worker_timeout // 60}m{worker_timeout % 60}s)")
    print(f"Worker Mem Est: {worker_mem} MB")
    print(f"Executors:   {executors}")

    print("--- Sandbox ---")
    if sandbox["available"]:
        abi = sandbox.get("abi_version", "?")
        print(f"Status:      ACTIVE (Landlock ABI v{abi})")
        print(
            "Policy:      workspace-write (workers can only write to workspace + per-worker TMPDIR)"
        )
    else:
        print("Status:      NOT AVAILABLE")
        print(f"Detail:      {sandbox['details']}")
        print("WARNING:     Codex workers will run WITHOUT filesystem sandbox!")
        print("             Workers can read/write ANY file on the system.")
        print("             Consider fixing Landlock or using Docker-based isolation.")

    mem = _get_memory_info()
    if mem:
        print("--- Memory ---")
        print(f"Total:       {mem['total_mb']} MB")
        print(f"Available:   {mem['available_mb']} MB")
        print(f"Usage:       {mem['usage_pct']}%")
        print(f"Est/worker:  ~{WORKER_MEM_ESTIMATE_MB} MB")
        print(
            f"Safe workers:{mem['max_safe_workers']} (keeping {MEM_RESERVE_MB}MB reserve)"
        )
        if max_workers > mem["max_safe_workers"]:
            print(
                f"WARNING: {max_workers} workers requested but only {mem['max_safe_workers']} safe by memory!"
            )

    install_tools = STACKS[stack].get("install_tools", "")
    if install_tools:
        print("--- Pre-install Tools (REQUIRED — sandbox disables network) ---")
        print(f"Command:     {install_tools}")
        print(
            "IMPORTANT:   Run this BEFORE launching workers. Workers have NO network access."
        )
    print("================================")


# ── Status extraction ────────────────────────────────────────────────────────
# Only parse the LAST 30 lines of output to avoid false matches from code
# samples, debug logs, or test cases that happen to contain "TASK_STATUS:".
_STATUS_SCAN_LINES = 30
_TASK_STATUS_RE = re.compile(r"^TASK_STATUS:\s*(DONE|FAILED)\s*$")


def _extract_status(text: str, task_id: str) -> dict:
    """Parse structured status lines from the LAST N lines of worker output.

    Only scans the tail to avoid false positives from status strings
    appearing in code, comments, or debug output earlier in the file.
    Uses forward scan so the LAST occurrence of each key wins.
    Requires TASK_STATUS to be present to consider any result valid.
    """
    result = {
        "TASK_STATUS": "UNKNOWN",
        "TASK_ID": task_id,
        "OWNER": "unknown",
        "NOTE": "",
    }
    in_fence = False
    # Forward scan — overwrite values so last occurrence wins
    lines = text.splitlines()[-_STATUS_SCAN_LINES:]
    for line in lines:
        stripped = line.strip()
        # Skip fenced code blocks entirely.
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith("#") or stripped.startswith("//"):
            continue
        m_status = _TASK_STATUS_RE.match(stripped)
        if m_status:
            result["TASK_STATUS"] = m_status.group(1)
            continue
        if stripped.upper().startswith("TASK_ID:"):
            result["TASK_ID"] = stripped.split(":", 1)[1].strip()
            continue
        if stripped.upper().startswith("OWNER:"):
            result["OWNER"] = stripped.split(":", 1)[1].strip()
            continue
        if stripped.upper().startswith("NOTE:"):
            result["NOTE"] = stripped.split(":", 1)[1].strip()
    return result


def _sanitize_note(s: str) -> str:
    """Sanitize worker NOTE before it enters plan.md or coordinator context.

    Strips newlines, markdown task patterns, control characters, and markdown
    injection vectors (links, images, HTML) that could corrupt plan.md.
    """
    # Strip ANSI/control chars except tab/newline/carriage-return (handled below)
    s = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]", "", s)
    # Flatten to single line (remove newlines, carriage returns)
    s = re.sub(r"[\r\n]+", " ", s)
    # Strip markdown task patterns that could inject fake tasks
    s = re.sub(r"[-*]\s*\[.\]\s*[Tt]\d+\b", "[STRIPPED]", s)
    # Strip markdown headers that could inject fake sections
    s = re.sub(r"^#{1,6}\s", "", s)
    # Strip markdown links [text](url) and images ![alt](url)
    s = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", s)
    # Strip inline HTML tags
    s = re.sub(r"<[^>]+>", "", s)
    # Strip markdown reference-style links [text][ref]
    s = re.sub(r"\[([^\]]*)\]\[[^\]]*\]", r"\1", s)
    # Neutralize status/key markers to prevent re-parsing confusion
    s = re.sub(r"\b(TASK_STATUS|TASK_ID|OWNER|NOTE):", r"\1_", s, flags=re.IGNORECASE)
    return s.strip()


def _truncate(s: str, maxlen: int) -> str:
    return s[:maxlen] + "..." if len(s) > maxlen else s


def _read_output_safe(path: Path) -> str | None:
    """Read output file with size guard. Returns None if too large."""
    try:
        size = path.stat().st_size
    except OSError:
        return None
    if size > MAX_OUTPUT_FILE_BYTES:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def cmd_collect(args: argparse.Namespace) -> None:
    """Collect result from a single worker output file.

    Returns EXACTLY 4 lines. Nothing more. This is the hard contract.
    """
    output_file = Path(args.output_file)
    task_id = args.task_id

    if not output_file.is_file():
        _print_result(
            "FAILED", task_id, "unknown", f"Output file not found: {output_file.name}"
        )
        return

    text = _read_output_safe(output_file)
    if text is None:
        size_mb = output_file.stat().st_size / 1_000_000
        _print_result(
            "UNKNOWN",
            task_id,
            "unknown",
            f"Output file too large ({size_mb:.1f}MB) or unreadable",
        )
        return

    r = _extract_status(text, task_id)

    if r["TASK_STATUS"] != "UNKNOWN":
        _print_result(
            r["TASK_STATUS"],
            r["TASK_ID"],
            r["OWNER"],
            _truncate(r["NOTE"], NOTE_MAX_CHARS),
        )
        return

    # No structured output — show tail
    file_size = output_file.stat().st_size
    tail = text.strip().splitlines()[-FAIL_TAIL_LINES:]
    tail_str = _truncate(
        " | ".join(line.strip() for line in tail if line.strip()), NOTE_MAX_CHARS
    )
    _print_result(
        "UNKNOWN",
        task_id,
        "unknown",
        f"No structured output ({file_size}B). Tail: {tail_str}",
    )


def _print_result(status: str, task_id: str, owner: str, note: str) -> None:
    """Print exactly 4 lines — the hard output contract."""
    note = _sanitize_note(note)
    print(f"TASK_STATUS: {status}")
    print(f"TASK_ID: {task_id}")
    print(f"OWNER: {owner}")
    print(f"NOTE: {note}")


def cmd_batch(args: argparse.Namespace) -> None:
    """Collect results for all tasks in a round. One block per task, blank-line separated."""
    logs_dir = Path(args.logs_dir)
    round_num = args.round_num

    # Try both zero-padded and unpadded patterns
    patterns = [f"round{round_num:02d}_T*_codex-*", f"round{round_num}_T*_codex-*"]
    output_files = []
    for pat in patterns:
        output_files = sorted(
            f for f in logs_dir.glob(f"{pat}.md") if "_prompt" not in f.name
        )
        if output_files:
            break

    if not output_files:
        print(f"No output files found for round {round_num} in {logs_dir}")
        return

    for i, f in enumerate(output_files):
        match = re.search(r"_(T\d+)_", f.name)
        task_id = match.group(1) if match else "T?"

        text = _read_output_safe(f)
        if text is None:
            try:
                size_mb = f.stat().st_size / 1_000_000
                size_msg = f"{size_mb:.1f}MB"
            except OSError:
                size_msg = "unknown size"
            _print_result(
                "UNKNOWN",
                task_id,
                "unknown",
                f"Output file too large ({size_msg}) or unreadable",
            )
        else:
            r = _extract_status(text, task_id)
            if r["TASK_STATUS"] == "UNKNOWN":
                file_size = f.stat().st_size
                tail = text.strip().splitlines()[-FAIL_TAIL_LINES:]
                tail_str = _truncate(
                    " | ".join(line.strip() for line in tail if line.strip()),
                    NOTE_MAX_CHARS,
                )
                r["TASK_ID"] = task_id
                r["OWNER"] = "unknown"
                r["NOTE"] = f"No structured output ({file_size}B). Tail: {tail_str}"
            r["NOTE"] = _truncate(r["NOTE"], NOTE_MAX_CHARS)
            _print_result(r["TASK_STATUS"], r["TASK_ID"], r["OWNER"], r["NOTE"])

        if i < len(output_files) - 1:
            print()  # blank line separator


def cmd_advise(args: argparse.Namespace) -> None:
    """Analyze plan.md and recommend batch size for next round.

    Zones:
      GREEN   (rounds 1-3, <8 total tasks, <2 failed)    -> max parallel
      YELLOW  (rounds 4-6, or 8-15 tasks, or 2-3 failed) -> half batch (min 2)
      RED     (rounds 7+, or >15 tasks, or >3 failed)    -> serial (batch=1)
      HALT    (>20 tasks, or >5 fix tasks created)        -> stop entirely
      DONE    (all tasks complete, 0 pending/running/failed) -> exit loop
      WAITING (GREEN zone, batch=0: running>0, pending=0) -> wait for workers

    Output: one JSON line with recommendation. Coordinator MUST follow it.
    """
    plan_file = Path(args.plan_md)
    if not plan_file.is_file():
        print('{"error": "plan.md not found"}')
        sys.exit(1)

    text = plan_file.read_text(encoding="utf-8", errors="replace")

    # Parse max_batch: CLI arg > state file > default(4)
    max_batch = 4
    if hasattr(args, "max_batch") and args.max_batch is not None and args.max_batch > 0:
        max_batch = args.max_batch
    else:
        state_file = Path.home() / ".claude" / "codex-orchestrator.local.md"
        if state_file.is_file():
            st = state_file.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"max_batch:\s*(\d+)", st)
            if m:
                max_batch = int(m.group(1))

    # Load tasks from JSON sidecar (preferred) or fallback to markdown
    tasks = _get_tasks(plan_file)
    counts = _count_tasks(tasks)
    total = sum(counts.values())

    # Count rounds completed (support both "## Round N ..." and "Round N:")
    task_scope = _task_board_scope(text)
    round_matches = re.findall(r"^##\s+Round\s+(\d+)\b", task_scope, re.MULTILINE)
    if not round_matches:
        round_matches = re.findall(r"^Round\s+(\d+):\s*$", task_scope, re.MULTILINE)
    rounds_done = max((int(r) for r in round_matches), default=0)

    # Count fix/retry tasks
    fix_tasks = sum(1 for t in tasks if "Fix/retry:" in t.get("description", ""))

    # Check for HALT condition first
    if total > 20 or fix_tasks > MAX_FIX_TASKS:
        zone = "HALT"
        recommended_batch = 0
        reason = []
        if total > 20:
            reason.append(f"{total} tasks (>20 hard limit)")
        if fix_tasks > MAX_FIX_TASKS:
            reason.append(f"{fix_tasks} fix tasks (>{MAX_FIX_TASKS} limit)")
        reason_str = "HALT — " + ", ".join(reason) + ". Split into sub-goals."
    elif counts["pending"] == 0 and counts["running"] == 0:
        recommended_batch = 0
        if counts["failed"] == 0:
            zone = "DONE"
            reason_str = "ALL TASKS COMPLETE"
        else:
            zone = "RED"
            reason_str = f"NO PENDING TASKS but {counts['failed']} failed — create fix tasks or DONE"
    elif counts["pending"] == 0 and counts["running"] > 0:
        recommended_batch = 0
        if counts["failed"] > 3:
            zone = "RED"
            reason_str = (
                f"WAITING — {counts['running']} tasks still running, "
                f"no pending tasks, {counts['failed']} failures (>3)"
            )
        else:
            zone = "GREEN"
            reason_str = (
                f"WAITING — {counts['running']} tasks still running, no pending tasks"
            )
    elif rounds_done >= 7 or total > MAX_TASKS_PER_SESSION or counts["failed"] > 3:
        zone = "RED"
        recommended_batch = 1
        reason = []
        if rounds_done >= 7:
            reason.append(f"round {rounds_done} (>=7)")
        if total > MAX_TASKS_PER_SESSION:
            reason.append(f"{total} tasks (>{MAX_TASKS_PER_SESSION})")
        if counts["failed"] > 3:
            reason.append(f"{counts['failed']} failures (>3)")
        reason_str = "SERIAL — " + ", ".join(reason)
    elif rounds_done >= 4 or total >= 8 or counts["failed"] >= 2:
        zone = "YELLOW"
        recommended_batch = min(max(2, max_batch // 2), counts["pending"])
        reason = []
        if rounds_done >= 4:
            reason.append(f"round {rounds_done} (>=4)")
        if total >= 8:
            reason.append(f"{total} tasks (>=8)")
        if counts["failed"] >= 2:
            reason.append(f"{counts['failed']} failures (>=2)")
        reason_str = "HALF SPEED — " + ", ".join(reason)
    else:
        zone = "GREEN"
        recommended_batch = min(max_batch, counts["pending"])
        reason_str = "FULL SPEED — early rounds, few tasks, low failures"

    # ── Memory-based throttle (can only lower batch, never raise) ──
    mem = _get_memory_info()
    mem_info = {}
    if mem and recommended_batch > 0:
        safe = mem["max_safe_workers"]
        mem_info = {
            "available_mb": mem["available_mb"],
            "usage_pct": mem["usage_pct"],
            "max_safe_workers": safe,
        }
        if safe <= 0:
            old_batch = recommended_batch
            recommended_batch = 0
            zone = "RED"
            reason_str += (
                f" | MEM BLOCK: {mem['available_mb']}MB free -> 0 workers "
                f"(was {old_batch})"
            )
        elif recommended_batch > safe:
            old_batch = recommended_batch
            recommended_batch = safe
            if safe <= 1:
                zone = "RED"
            elif zone == "GREEN":
                zone = "YELLOW"
            reason_str += (
                f" | MEM THROTTLE: {mem['available_mb']}MB free -> "
                f"{recommended_batch} workers (was {old_batch})"
            )

    result = {
        "zone": zone,
        "recommended_batch": recommended_batch,
        "reason": reason_str,
        "rounds_done": rounds_done,
        "tasks": counts,
        "total_tasks": total,
        "fix_tasks_created": fix_tasks,
        "memory": mem_info,
    }
    print(json.dumps(result))


def cmd_status(args: argparse.Namespace) -> None:
    """Print compact task board summary from JSON sidecar or plan.md."""
    plan_file = Path(args.plan_md)
    if not plan_file.is_file():
        print("ERROR: plan.md not found", file=sys.stderr)
        sys.exit(1)

    text = plan_file.read_text(encoding="utf-8", errors="replace")
    tasks = _get_tasks(plan_file)
    counts = _count_tasks(tasks)
    total = sum(counts.values())

    source = "tasks.json" if _load_tasks(plan_file) is not None else "plan.md"
    print(
        f"Tasks: {total} total | "
        f"done {counts['done']} | "
        f"running {counts['running']} | "
        f"pending {counts['pending']} | "
        f"failed {counts['failed']}"
        f"  (source: {source})"
    )

    if total > MAX_TASKS_PER_SESSION:
        print(f"WARNING: {total} tasks exceeds limit of {MAX_TASKS_PER_SESSION}.")

    fix_tasks = sum(1 for t in tasks if "Fix/retry:" in t.get("description", ""))
    if fix_tasks > 0:
        print(f"Fix tasks: {fix_tasks}/{MAX_FIX_TASKS} max")

    decisions = re.findall(r"^DECISION:\s*(.+)$", text, re.MULTILINE)
    if decisions:
        print(f"Last decision: {decisions[-1]}")


def cmd_memcheck(_args: argparse.Namespace) -> None:
    """Show current memory status and safe worker estimate."""
    mem = _get_memory_info()
    if not mem:
        print("ERROR: Cannot read /proc/meminfo (Linux only)", file=sys.stderr)
        sys.exit(1)

    print(
        f"Memory: {mem['available_mb']}MB available / {mem['total_mb']}MB total ({mem['usage_pct']}% used)"
    )
    print(f"Estimated per worker: ~{WORKER_MEM_ESTIMATE_MB}MB")
    print(f"Reserve for OS/Claude: {MEM_RESERVE_MB}MB")
    print(f"Max safe parallel workers: {mem['max_safe_workers']}")
    if mem["available_mb"] < MEM_RESERVE_MB + WORKER_MEM_ESTIMATE_MB:
        print("WARNING: Not enough memory for even 1 worker!")
    print(json.dumps(mem))


_CHECKPOINT_TIMEOUT = 60  # seconds per verification command


def cmd_compact(args: argparse.Namespace) -> None:
    """Compact plan.md: archive old rounds, keep last N + task board + deliverables.

    This protects coordinator context by removing historical round details
    that no longer inform the next decision. Archived content goes to archive.md.
    """
    plan_file = Path(args.plan_md)
    if not plan_file.is_file():
        print("ERROR: plan.md not found", file=sys.stderr)
        sys.exit(1)

    keep_rounds = args.keep_rounds
    text = plan_file.read_text(encoding="utf-8", errors="replace")

    # Split into sections by ## headings
    sections: list[tuple[str, str]] = []  # (heading, content)
    current_heading = ""
    current_lines: list[str] = []

    for line in text.splitlines(keepends=True):
        if line.startswith("## "):
            if current_heading or current_lines:
                sections.append((current_heading, "".join(current_lines)))
            current_heading = line.strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_heading or current_lines:
        sections.append((current_heading, "".join(current_lines)))

    # Identify round sections and non-round sections
    round_re = re.compile(r"^##\s+Round\s+(\d+)\b")
    round_sections: list[tuple[int, str, str]] = []  # (round_num, heading, content)
    preserved_sections: list[tuple[str, str]] = []
    archive_summary_idx = -1

    for i, (heading, content) in enumerate(sections):
        m = round_re.match(heading)
        if m:
            round_sections.append((int(m.group(1)), heading, content))
        else:
            preserved_sections.append((heading, content))
            if "Archive Summary" in heading:
                archive_summary_idx = len(preserved_sections) - 1

    if not round_sections:
        print("No round sections found, nothing to compact")
        return

    # Sort rounds, determine which to keep vs archive
    round_sections.sort(key=lambda x: x[0])
    max_round = round_sections[-1][0]
    cutoff = max_round - keep_rounds + 1

    to_archive = [(n, h, c) for n, h, c in round_sections if n < cutoff]
    to_keep = [(n, h, c) for n, h, c in round_sections if n >= cutoff]

    if not to_archive:
        print(f"All {len(round_sections)} rounds within keep window ({keep_rounds}), nothing to compact")
        return

    # Generate 1-line summaries for archived rounds
    archive_summaries = []
    for rnum, heading, content in to_archive:
        # Count task results mentioned in this round
        done_count = len(re.findall(r"\bDONE\b", content))
        failed_count = len(re.findall(r"\bFAILED\b", content))
        files = re.findall(r"files_modified.*?:\s*(.+)", content, re.IGNORECASE)
        summary = f"- Round {rnum}: {done_count} DONE, {failed_count} FAILED"
        archive_summaries.append(summary)

    # Write archived content to archive.md (append)
    archive_file = plan_file.parent / "archive.md"
    archive_content = ""
    for _, heading, content in to_archive:
        archive_content += f"{heading}\n{content}\n"

    with open(archive_file, "a", encoding="utf-8") as f:
        f.write(f"\n--- Archived {datetime.now().isoformat()} ---\n")
        f.write(archive_content)

    # Rebuild plan.md
    output_lines = []

    # Write preserved (non-round) sections, injecting/updating archive summary
    archive_summary_written = False
    for heading, content in preserved_sections:
        if "Archive Summary" in heading:
            # Update existing archive summary
            output_lines.append(heading)
            output_lines.append("")
            # Keep existing summaries + add new ones
            existing = [l for l in content.splitlines() if l.strip().startswith("- Round")]
            for line in existing:
                output_lines.append(line)
            for line in archive_summaries:
                output_lines.append(line)
            output_lines.append("")
            archive_summary_written = True
        else:
            output_lines.append(heading)
            output_lines.append(content)

    # If no archive summary section existed, add one before rounds
    if not archive_summary_written:
        output_lines.append("## Archive Summary")
        output_lines.append("")
        for line in archive_summaries:
            output_lines.append(line)
        output_lines.append("")

    # Write kept round sections
    for _, heading, content in to_keep:
        output_lines.append(heading)
        output_lines.append(content)

    new_text = "\n".join(output_lines)

    # Backup before writing
    backup_dir = plan_file.parent / "backups"
    backup_dir.mkdir(exist_ok=True)
    backup_path = backup_dir / f"plan.md.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    plan_file.rename(backup_path)

    _atomic_write_text(plan_file, new_text)

    old_lines = len(text.splitlines())
    new_lines = len(new_text.splitlines())
    print(
        f"Compacted: {len(to_archive)} rounds archived to archive.md, "
        f"plan.md reduced from {old_lines} to {new_lines} lines"
    )


def cmd_checkpoint(args: argparse.Namespace) -> None:
    """Run lightweight verification (lint/test/build exit codes) without spawning workers.

    Returns compact 3-line result for coordinator context.
    Coordinator should run this every N rounds to catch integration issues early.
    """
    import subprocess

    # Resolve workspace and stack
    workspace = Path(args.workspace).resolve()
    stack_name = args.stack

    # If stack not provided, read from state file
    if not stack_name:
        state_file = Path.home() / ".claude" / "codex-orchestrator.local.md"
        if state_file.is_file():
            st = state_file.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"stack:\s*(\S+)", st)
            if m:
                stack_name = m.group(1)

    if not stack_name or stack_name not in STACKS:
        print(f"ERROR: Unknown or missing stack '{stack_name}'", file=sys.stderr)
        sys.exit(1)

    stack = STACKS[stack_name]
    tc = stack["toolchain"]

    # Determine round number from args or state
    round_num = args.round if args.round else "?"

    # Run each verification step, capture only exit code
    results = {}
    fail_details = []
    for step in ("lint", "test", "build"):
        cmd = tc.get(step, "")
        if not cmd:
            results[step] = "SKIP"
            continue

        try:
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=_CHECKPOINT_TIMEOUT,
            )
            if proc.returncode == 0:
                results[step] = "PASS"
            else:
                results[step] = "FAIL"
                # Extract last line of stderr or stdout for context
                err_output = (proc.stderr or proc.stdout or "").strip().splitlines()
                last_line = err_output[-1] if err_output else f"exit code {proc.returncode}"
                fail_details.append(f"{step}: {_truncate(last_line, 120)}")
        except subprocess.TimeoutExpired:
            results[step] = "FAIL"
            fail_details.append(f"{step}: timed out after {_CHECKPOINT_TIMEOUT}s")
        except Exception as e:
            results[step] = "FAIL"
            fail_details.append(f"{step}: {e}")

    # Output compact result (designed for coordinator context)
    status_parts = " ".join(f"{k.upper()}={v}" for k, v in results.items())
    print(f"CHECKPOINT round={round_num}: {status_parts}")

    if fail_details:
        print(f"FAIL_DETAIL: {'; '.join(fail_details)}")
        print("ACTION: create fix tasks for failing checks before continuing")
    else:
        print("ALL CHECKS PASSED")


def cmd_tasks(args: argparse.Namespace) -> None:
    """Manage tasks.json sidecar for structured task state."""
    plan_file = Path(args.plan_md)
    action = args.action

    if action == "init":
        # Initialize tasks.json from plan.md task board (migration)
        if not plan_file.is_file():
            print("ERROR: plan.md not found", file=sys.stderr)
            sys.exit(1)
        existing = _load_tasks(plan_file)
        if existing is not None and not args.force:
            print(f"tasks.json already exists with {len(existing)} tasks. Use --force to overwrite.")
            return
        text = plan_file.read_text(encoding="utf-8", errors="replace")
        tasks = _parse_tasks_from_markdown(_task_board_scope(text))
        _save_tasks(plan_file, tasks)
        print(f"Initialized tasks.json with {len(tasks)} tasks from plan.md")

    elif action == "add":
        tasks = _load_tasks(plan_file) or []
        # Auto-generate next task ID
        max_id = 0
        for t in tasks:
            m = re.match(r"T(\d+)", t.get("id", ""))
            if m:
                max_id = max(max_id, int(m.group(1)))
        new_id = f"T{max_id + 1}"
        task = {
            "id": new_id,
            "owner": args.owner or "unassigned",
            "description": args.description,
            "status": "pending",
        }
        tasks.append(task)
        _save_tasks(plan_file, tasks)
        print(f"Added {new_id}: {args.description}")

    elif action == "update":
        tasks = _load_tasks(plan_file)
        if tasks is None:
            print("ERROR: tasks.json not found. Run 'tasks init' first.", file=sys.stderr)
            sys.exit(1)
        found = False
        for t in tasks:
            if t["id"] == args.task_id:
                if args.status:
                    t["status"] = args.status
                if args.owner:
                    t["owner"] = args.owner
                if args.note:
                    t["note"] = args.note
                found = True
                break
        if not found:
            print(f"ERROR: Task {args.task_id} not found", file=sys.stderr)
            sys.exit(1)
        _save_tasks(plan_file, tasks)
        print(f"Updated {args.task_id}")

    elif action == "list":
        tasks = _get_tasks(plan_file)
        source = "tasks.json" if _load_tasks(plan_file) is not None else "plan.md"
        print(f"Source: {source}")
        print(_tasks_to_markdown(tasks))

    elif action == "render":
        # Output markdown task board from tasks.json (for updating plan.md)
        tasks = _load_tasks(plan_file)
        if tasks is None:
            print("ERROR: tasks.json not found", file=sys.stderr)
            sys.exit(1)
        print(_tasks_to_markdown(tasks))

    else:
        print(f"Unknown action: {action}", file=sys.stderr)
        sys.exit(1)


def cmd_save_checkpoint(args: argparse.Namespace) -> None:
    """Save a round-level checkpoint for crash recovery.

    Writes {run_dir}/checkpoint.json with full state snapshot:
    tasks, round number, zone, timestamp.  On recovery, coordinator
    reads this instead of parsing a possibly half-written plan.md.
    """
    plan_file = Path(args.plan_md)
    if not plan_file.is_file():
        print("ERROR: plan.md not found", file=sys.stderr)
        sys.exit(1)

    run_dir = plan_file.parent
    tasks = _get_tasks(plan_file)
    counts = _count_tasks(tasks)

    checkpoint = {
        "version": 1,
        "round": args.round,
        "timestamp": datetime.now().isoformat(),
        "tasks": tasks,
        "counts": counts,
        "total_tasks": sum(counts.values()),
        "plan_md": str(plan_file),
        "run_dir": str(run_dir),
    }

    # Read zone from state file if available
    state_file = Path.home() / ".claude" / "codex-orchestrator.local.md"
    if state_file.is_file():
        st = state_file.read_text(encoding="utf-8", errors="replace")
        for key in ("stack", "workspace", "status", "worker_timeout"):
            m = re.search(rf"{key}:\s*(.+)", st)
            if m:
                checkpoint[key] = m.group(1).strip()

    cp_path = run_dir / "checkpoint.json"
    _atomic_write_text(cp_path, json.dumps(checkpoint, indent=2, ensure_ascii=False))
    print(f"Checkpoint saved: round {args.round}, {sum(counts.values())} tasks")
    print(json.dumps(counts))


def cmd_load_checkpoint(args: argparse.Namespace) -> None:
    """Load checkpoint for crash recovery. Outputs JSON state."""
    run_dir = Path(args.run_dir)
    cp_path = run_dir / "checkpoint.json"
    if not cp_path.is_file():
        print('{"error": "No checkpoint found"}')
        sys.exit(1)

    data = json.loads(cp_path.read_text(encoding="utf-8"))
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_executor_info(args: argparse.Namespace) -> None:
    """Output executor configuration as JSON.

    Reads executor name from state file or --executor flag.
    Coordinator uses this to build the worker launch template.
    """
    executor_name = getattr(args, "executor", None)

    # Try state file if not specified
    if not executor_name:
        state_file = Path.home() / ".claude" / "codex-orchestrator.local.md"
        if state_file.is_file():
            st = state_file.read_text(encoding="utf-8", errors="replace")
            m = re.search(r"executor:\s*(\S+)", st)
            if m:
                executor_name = m.group(1)

    executor_name = executor_name or DEFAULT_EXECUTOR
    if executor_name not in EXECUTORS:
        print(f'{{"error": "Unknown executor: {executor_name}"}}')
        sys.exit(1)

    info = {**EXECUTORS[executor_name], "name": executor_name}
    print(json.dumps(info, indent=2))


def cmd_sandbox_check(_args: argparse.Namespace) -> None:
    """Verify that the Codex sandbox (Landlock) is functional.

    Outputs JSON with sandbox status. Used by the coordinator to verify
    that workers will actually be sandboxed before dispatching tasks.
    """
    sandbox = _check_sandbox()
    print(json.dumps(sandbox))
    if not sandbox["available"]:
        print(
            "WARNING: Sandbox not available! Workers will run without filesystem restrictions.",
            file=sys.stderr,
        )
        sys.exit(1)


def cmd_cleanup(args: argparse.Namespace) -> None:
    """Clean up old run directories. Keeps the N most recent runs (default 5).

    Removes prompt files and worker output files from completed runs.
    If --all is specified, removes entire run directories (except the current one).
    """
    workspace = Path(args.workspace)
    runs_root = workspace / ".claude_codex_runs"
    if not runs_root.is_dir():
        print(f"No runs directory found at {runs_root}")
        return

    keep = args.keep
    delete_all = args.all

    # Find all run dirs sorted by name (timestamp-based)
    run_dirs = sorted(
        [d for d in runs_root.iterdir() if d.is_dir()],
        key=lambda d: d.name,
        reverse=True,
    )

    # Identify current run from state file
    state_file = Path.home() / ".claude" / "codex-orchestrator.local.md"
    current_run = ""
    if state_file.is_file():
        st = state_file.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"run_dir:\s*(.+)", st)
        if m:
            current_run = m.group(1).strip()

    removed = 0
    kept = 0
    for d in run_dirs:
        if str(d) == current_run:
            print(f"  SKIP (current): {d.name}")
            kept += 1
            continue
        if kept < keep:
            print(f"  KEEP: {d.name}")
            kept += 1
            continue

        if delete_all:
            shutil.rmtree(d, ignore_errors=True)
            print(f"  REMOVED: {d.name}")
        else:
            # Only remove logs (prompt + output files), keep plan.md
            logs = d / "logs"
            if logs.is_dir():
                shutil.rmtree(logs, ignore_errors=True)
                print(f"  CLEANED logs: {d.name}")
            else:
                print(f"  SKIP (no logs): {d.name}")
        removed += 1

    print(f"\nTotal: {kept} kept, {removed} {'removed' if delete_all else 'cleaned'}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="orch", description="clco orchestrator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("stacks", help="List all available stack profiles")

    p_profile = sub.add_parser("profile", help="Output full stack profile as markdown")
    p_profile.add_argument("stack_name", help="Stack ID (e.g. python-backend)")

    p_setup = sub.add_parser("setup", help="Initialize orchestration run")
    p_setup.add_argument("--workspace", default=os.getcwd())
    p_setup.add_argument(
        "--stack", required=True, help="Stack profile ID (e.g. python-backend)"
    )
    p_setup.add_argument("--max-workers", default=4, type=int)
    p_setup.add_argument("--max-batch", default=None, type=int)
    p_setup.add_argument("--max-steps", default=50, type=int)
    p_setup.add_argument("--codex-model", default="")
    p_setup.add_argument(
        "--worker-timeout",
        default=WORKER_TIMEOUT_DEFAULT,
        type=int,
        help=f"Per-worker timeout in seconds (default: {WORKER_TIMEOUT_DEFAULT}, max: {WORKER_TIMEOUT_HARD})",
    )
    p_setup.add_argument(
        "--worker-mem",
        default=WORKER_MEM_ESTIMATE_MB_DEFAULT,
        type=int,
        help=f"Estimated MB per worker for memory throttling (default: {WORKER_MEM_ESTIMATE_MB_DEFAULT})",
    )
    p_setup.add_argument(
        "--executor",
        default=DEFAULT_EXECUTOR,
        choices=list(EXECUTORS.keys()),
        help=f"Executor backend (default: {DEFAULT_EXECUTOR})",
    )

    p_collect = sub.add_parser("collect", help="Collect result from one worker output")
    p_collect.add_argument("output_file", help="Path to worker output file")
    p_collect.add_argument("task_id", help="Task ID (e.g. T3)")

    p_batch = sub.add_parser("batch", help="Collect all results for a round")
    p_batch.add_argument("logs_dir", help="Path to logs directory")
    p_batch.add_argument("round_num", type=_positive_int, help="Round number (>=1)")

    p_advise = sub.add_parser("advise", help="Recommend batch size for next round")
    p_advise.add_argument("plan_md", help="Path to plan.md")
    p_advise.add_argument(
        "--max-batch",
        type=int,
        default=None,
        help="Override max_batch (avoids reading global state file)",
    )

    p_status = sub.add_parser("status", help="Show task board summary from plan.md")
    p_status.add_argument("plan_md", help="Path to plan.md")

    sub.add_parser("memcheck", help="Show memory status and safe worker count")
    sub.add_parser("sandbox-check", help="Verify Landlock sandbox is functional")

    p_compact = sub.add_parser("compact", help="Compact plan.md by archiving old rounds")
    p_compact.add_argument("plan_md", help="Path to plan.md")
    p_compact.add_argument(
        "--keep-rounds", type=int, default=3, help="Number of recent rounds to keep (default 3)"
    )

    p_checkpoint = sub.add_parser(
        "checkpoint", help="Run lightweight verification (lint/test/build exit codes)"
    )
    p_checkpoint.add_argument("--workspace", default=os.getcwd(), help="Project workspace root")
    p_checkpoint.add_argument("--stack", default=None, help="Stack ID (auto-detect from state file if omitted)")
    p_checkpoint.add_argument("--round", type=int, default=None, help="Current round number (for display)")

    p_exec_info = sub.add_parser("executor-info", help="Show executor backend configuration")
    p_exec_info.add_argument("--executor", default=None, help="Executor name (reads from state file if omitted)")

    p_save_cp = sub.add_parser("save-checkpoint", help="Save round-level checkpoint")
    p_save_cp.add_argument("plan_md", help="Path to plan.md")
    p_save_cp.add_argument("--round", type=int, required=True, help="Current round number")

    p_load_cp = sub.add_parser("load-checkpoint", help="Load checkpoint for recovery")
    p_load_cp.add_argument("run_dir", help="Path to run directory")

    p_tasks = sub.add_parser("tasks", help="Manage tasks.json sidecar")
    p_tasks.add_argument("plan_md", help="Path to plan.md")
    p_tasks.add_argument(
        "action",
        choices=["init", "add", "update", "list", "render"],
        help="Action to perform",
    )
    p_tasks.add_argument("--task-id", help="Task ID for update (e.g. T3)")
    p_tasks.add_argument("--status", choices=["pending", "running", "done", "failed"], help="New status")
    p_tasks.add_argument("--owner", help="Task owner (e.g. codex-1)")
    p_tasks.add_argument("--description", help="Task description (for add)")
    p_tasks.add_argument("--note", help="Note to attach (for update)")
    p_tasks.add_argument("--force", action="store_true", help="Force overwrite (for init)")

    p_cleanup = sub.add_parser("cleanup", help="Clean up old run directories")
    p_cleanup.add_argument(
        "--workspace", default=os.getcwd(), help="Project workspace root"
    )
    p_cleanup.add_argument(
        "--keep",
        type=_positive_int,
        default=5,
        help="Number of recent runs to keep (>=1, default 5)",
    )
    p_cleanup.add_argument(
        "--all", action="store_true", help="Remove entire run dirs (not just logs)"
    )

    args = parser.parse_args()
    cmds = {
        "stacks": cmd_stacks,
        "profile": cmd_profile,
        "setup": cmd_setup,
        "collect": cmd_collect,
        "batch": cmd_batch,
        "advise": cmd_advise,
        "status": cmd_status,
        "memcheck": cmd_memcheck,
        "sandbox-check": cmd_sandbox_check,
        "compact": cmd_compact,
        "checkpoint": cmd_checkpoint,
        "executor-info": cmd_executor_info,
        "save-checkpoint": cmd_save_checkpoint,
        "load-checkpoint": cmd_load_checkpoint,
        "tasks": cmd_tasks,
        "cleanup": cmd_cleanup,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
