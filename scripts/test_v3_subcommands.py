"""Unit tests for v3 subcommands: extract-signal, read-signal, checklist-*, next-tasks, render-contract."""

import json
import subprocess
import tempfile
from pathlib import Path

ORCH = Path(__file__).resolve().parent / "orch.py"


def run_orch(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(ORCH), *args],
        capture_output=True, text=True, check=check,
    )


# ── extract-signal ──────────────────────────────────────────────────────────

def test_extract_signal_basic():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "output.md"
        sig = Path(d) / "T1.signal"
        out.write_text("blah blah\n\n---SIGNAL---\nstatus: DONE\ntask: T1\nworker: codex-1\n---END-SIGNAL---\n")
        r = run_orch("extract-signal", str(out), str(sig))
        data = json.loads(r.stdout)
        assert data["status"] == "DONE"
        assert data["task"] == "T1"
        assert data["worker"] == "codex-1"
        assert sig.exists()
        content = sig.read_text()
        assert "status: DONE" in content


def test_extract_signal_with_extra_keys():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "output.md"
        sig = Path(d) / "T5.signal"
        out.write_text(
            "review results...\n\n"
            "---SIGNAL---\n"
            "status: DONE\n"
            "task: T5\n"
            "worker: codex-2\n"
            "review_verdict: FAIL\n"
            "review_details: D1=PASS D2=FAIL:missing-handler\n"
            "---END-SIGNAL---\n"
        )
        r = run_orch("extract-signal", str(out), str(sig))
        data = json.loads(r.stdout)
        assert data["review_verdict"] == "FAIL"
        assert "D2=FAIL" in data["review_details"]


def test_extract_signal_missing_block():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "output.md"
        sig = Path(d) / "T1.signal"
        out.write_text("no signal here at all\n")
        r = run_orch("extract-signal", str(out), str(sig))
        data = json.loads(r.stdout)
        assert data["status"] == "UNKNOWN"


def test_extract_signal_missing_file():
    with tempfile.TemporaryDirectory() as d:
        sig = Path(d) / "T1.signal"
        r = run_orch("extract-signal", "/nonexistent/output.md", str(sig))
        data = json.loads(r.stdout)
        assert data["status"] == "UNKNOWN"
        assert sig.exists()


def test_extract_signal_fail_status():
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "output.md"
        sig = Path(d) / "T3.signal"
        out.write_text(
            "tried but failed\n\n"
            "---SIGNAL---\n"
            "status: FAIL\n"
            "task: T3\n"
            "worker: codex-1\n"
            "error: test_auth.py:42 assertion error\n"
            "---END-SIGNAL---\n"
        )
        r = run_orch("extract-signal", str(out), str(sig))
        data = json.loads(r.stdout)
        assert data["status"] == "FAIL"
        assert "assertion error" in data["error"]


# ── read-signal ─────────────────────────────────────────────────────────────

def test_read_signal():
    with tempfile.TemporaryDirectory() as d:
        sig = Path(d) / "T1.signal"
        sig.write_text("status: DONE\ntask: T1\nworker: codex-1\n")
        r = run_orch("read-signal", str(sig))
        data = json.loads(r.stdout)
        assert data["status"] == "DONE"
        assert data["task"] == "T1"


def test_read_signal_missing():
    r = run_orch("read-signal", "/nonexistent/T1.signal", check=False)
    assert r.returncode == 1
    data = json.loads(r.stdout)
    assert data["status"] == "UNKNOWN"


# ── checklist-status ────────────────────────────────────────────────────────

SAMPLE_CHECKLIST = """\
# Orchestration Checklist

## Meta
- goal: Build hello world
- status: RUNNING

## Deliverables Contract
| ID | Deliverable | Criterion | Status |
|----|------------|-----------|--------|
| D1 | Script | python main.py works | PENDING |

## Task Board
| Task | Type | Description | Deps | Status | Worker | Signal |
|------|------|------------|------|--------|--------|--------|
| T1 | code | Create structure | - | DONE | codex-1 | signals/T1.signal |
| T2 | code | Implement main | T1 | PENDING | - | - |
| T3 | code | Add tests | T1 | PENDING | - | - |
| T4 | qa-review-codex | Review | T2,T3 | PENDING | - | - |
| T5 | qa-runtime | lint+test | T4 | PENDING | - | - |

## Log
- started
"""


def test_checklist_status():
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(SAMPLE_CHECKLIST)
        r = run_orch("checklist-status", str(cl))
        data = json.loads(r.stdout)
        assert data["total"] == 5
        assert data["counts"]["DONE"] == 1
        assert data["counts"]["PENDING"] == 4
        assert "T2" in data["ready"]
        assert "T3" in data["ready"]
        # T4 depends on T2,T3 which aren't done yet
        assert "T4" not in data["ready"]
        assert data["all_done"] is False


# ── checklist-update ────────────────────────────────────────────────────────

def test_checklist_update():
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(SAMPLE_CHECKLIST)
        r = run_orch("checklist-update", str(cl), "T2", "RUNNING", "--worker", "codex-1")
        data = json.loads(r.stdout)
        assert data["ok"] is True

        # Verify the file was updated
        r2 = run_orch("checklist-status", str(cl))
        data2 = json.loads(r2.stdout)
        assert data2["counts"]["RUNNING"] == 1
        # T2 is now running, so only T3 is ready
        assert "T3" in data2["ready"]
        assert "T2" not in data2["ready"]


def test_checklist_update_done_with_signal():
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(SAMPLE_CHECKLIST)
        run_orch("checklist-update", str(cl), "T2", "DONE", "--worker", "codex-1", "--signal", "signals/T2.signal")
        run_orch("checklist-update", str(cl), "T3", "DONE", "--worker", "codex-2", "--signal", "signals/T3.signal")

        r = run_orch("checklist-status", str(cl))
        data = json.loads(r.stdout)
        assert data["counts"]["DONE"] == 3
        # Now T4 should be ready (T2 and T3 are done)
        assert "T4" in data["ready"]


def test_checklist_update_nonexistent_task():
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(SAMPLE_CHECKLIST)
        r = run_orch("checklist-update", str(cl), "T99", "DONE", check=False)
        assert r.returncode == 1


# ── next-tasks ──────────────────────────────────────────────────────────────

def test_next_tasks():
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(SAMPLE_CHECKLIST)
        r = run_orch("next-tasks", str(cl))
        data = json.loads(r.stdout)
        assert data["count"] == 2
        task_ids = [t["task"] for t in data["ready"]]
        assert "T2" in task_ids
        assert "T3" in task_ids


def test_next_tasks_with_max_batch():
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(SAMPLE_CHECKLIST)
        r = run_orch("next-tasks", str(cl), "--max-batch", "1")
        data = json.loads(r.stdout)
        assert data["count"] == 1


def test_next_tasks_all_done():
    checklist = """\
# Orchestration Checklist

## Meta
- status: RUNNING

## Task Board
| Task | Type | Description | Deps | Status | Worker | Signal |
|------|------|------------|------|--------|--------|--------|
| T1 | code | Do thing | - | DONE | codex-1 | signals/T1.signal |

## Log
"""
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(checklist)
        r = run_orch("next-tasks", str(cl))
        data = json.loads(r.stdout)
        assert data["count"] == 0


# ── render-contract ─────────────────────────────────────────────────────────

def test_render_contract_basic():
    with tempfile.TemporaryDirectory() as d:
        tpl = Path(d) / "test.contract.md"
        tpl.write_text("Hello {{name}}, your task is {{task_id}}.")
        r = run_orch("render-contract", str(tpl), "--vars", "name=Alice", "task_id=T1")
        assert "Hello Alice, your task is T1." in r.stdout


def test_render_contract_to_file():
    with tempfile.TemporaryDirectory() as d:
        tpl = Path(d) / "test.contract.md"
        out = Path(d) / "rendered.md"
        tpl.write_text("Task: {{task_id}}")
        r = run_orch("render-contract", str(tpl), "--vars", "task_id=T5", "--output", str(out))
        data = json.loads(r.stdout)
        assert data["ok"] is True
        assert out.read_text() == "Task: T5"


def test_render_contract_vars_file_json():
    with tempfile.TemporaryDirectory() as d:
        tpl = Path(d) / "test.contract.md"
        vf = Path(d) / "vars.json"
        tpl.write_text("{{workspace}} / {{stack_name}}")
        vf.write_text('{"workspace": "/tmp/project", "stack_name": "python-backend"}')
        r = run_orch("render-contract", str(tpl), "--vars-file", str(vf))
        assert "/tmp/project / python-backend" in r.stdout


def test_render_contract_vars_file_kv():
    with tempfile.TemporaryDirectory() as d:
        tpl = Path(d) / "test.contract.md"
        vf = Path(d) / "vars.txt"
        tpl.write_text("{{a}} and {{b}}")
        vf.write_text("a=hello\nb=world\n# comment\n")
        r = run_orch("render-contract", str(tpl), "--vars-file", str(vf))
        assert "hello and world" in r.stdout


def test_render_contract_vars_override_file():
    """CLI --vars should override --vars-file."""
    with tempfile.TemporaryDirectory() as d:
        tpl = Path(d) / "test.contract.md"
        vf = Path(d) / "vars.json"
        tpl.write_text("{{name}}")
        vf.write_text('{"name": "from-file"}')
        # vars-file loaded first, then --vars overrides
        r = run_orch("render-contract", str(tpl), "--vars-file", str(vf), "--vars", "name=from-cli")
        assert "from-cli" in r.stdout


# ── retries column ──────────────────────────────────────────────────────────

def test_checklist_with_retries_column():
    """8-column checklist with Retries column."""
    checklist = """\
# Orchestration Checklist

## Meta
- status: RUNNING

## Task Board
| Task | Type | Description | Deps | Status | Worker | Signal | Retries |
|------|------|------------|------|--------|--------|--------|---------|
| T1 | code | Do thing | - | FAIL | codex-1 | signals/T1.signal | 1 |
| T2 | fix | Fix T1 | T1 | PENDING | - | - | 0 |

## Log
"""
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(checklist)
        r = run_orch("checklist-status", str(cl))
        data = json.loads(r.stdout)
        assert data["counts"]["FAIL"] == 1
        assert data["counts"]["PENDING"] == 1
        # T2 depends on T1 which is FAIL, not DONE — so T2 is NOT ready
        assert "T2" not in data["ready"]


def test_checklist_update_retries():
    """Update retries counter."""
    checklist = """\
# Orchestration Checklist

## Meta
- status: RUNNING

## Task Board
| Task | Type | Description | Deps | Status | Worker | Signal | Retries |
|------|------|------------|------|--------|--------|--------|---------|
| T1 | code | Do thing | - | FAIL | codex-1 | signals/T1.signal | 0 |

## Log
"""
    with tempfile.TemporaryDirectory() as d:
        cl = Path(d) / "checklist.md"
        cl.write_text(checklist)
        r = run_orch("checklist-update", str(cl), "T1", "FAIL", "--retries", "1")
        data = json.loads(r.stdout)
        assert data["ok"] is True
        # Verify retries persisted
        content = cl.read_text()
        assert "| 1 |" in content


if __name__ == "__main__":
    import sys
    failures = []
    tests = [v for k, v in globals().items() if k.startswith("test_") and callable(v)]
    for t in tests:
        try:
            t()
            print(f"  PASS: {t.__name__}")
        except Exception as e:
            print(f"  FAIL: {t.__name__}: {e}")
            failures.append(t.__name__)
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    if failures:
        print(f"FAILED: {', '.join(failures)}")
        sys.exit(1)
