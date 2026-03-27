"""End-to-end tests for all new clco features."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ORCH = str(Path.home() / ".claude/plugins/codex-orchestrator-v2/scripts/orch.py")


def run(*args: str) -> tuple[str, str, int]:
    r = subprocess.run(["uv", "run", ORCH, *args], capture_output=True, text=True)
    return r.stdout.strip(), r.stderr.strip(), r.returncode


def test_stacks_loads_from_files():
    out, _, rc = run("stacks")
    assert rc == 0
    assert "python-backend" in out
    assert "vue-frontend" in out


def test_profile_content():
    out, _, rc = run("profile", "python-backend")
    assert rc == 0
    assert "Python Backend" in out
    assert "ruff" in out


def test_executor_info_default():
    out, _, rc = run("executor-info")
    assert rc == 0
    info = json.loads(out)
    assert info["name"] == "codex"
    assert "codex exec" in info["worker_cmd"]


def test_executor_info_claude():
    out, _, rc = run("executor-info", "--executor", "claude")
    assert rc == 0
    info = json.loads(out)
    assert info["name"] == "claude"
    assert "claude" in info["worker_cmd"]


def test_tasks_json_sidecar():
    with tempfile.TemporaryDirectory() as d:
        plan = Path(d) / "plan.md"
        plan.write_text(
            "## Task Board\n"
            "- [ ] T1 | owner=codex-1 | Do thing\n"
            "- [x] T2 | owner=codex-2 | Done thing\n"
        )
        # init
        out, _, rc = run("tasks", str(plan), "init")
        assert rc == 0
        tasks_json = Path(d) / "tasks.json"
        assert tasks_json.exists()
        data = json.loads(tasks_json.read_text())
        assert len(data["tasks"]) == 2

        # add
        out, _, rc = run("tasks", str(plan), "add", "--owner", "codex-1", "--description", "New task")
        assert rc == 0
        data = json.loads(tasks_json.read_text())
        assert len(data["tasks"]) == 3
        assert data["tasks"][-1]["id"] == "T3"

        # update
        out, _, rc = run("tasks", str(plan), "update", "--task-id", "T1", "--status", "done")
        assert rc == 0
        data = json.loads(tasks_json.read_text())
        assert data["tasks"][0]["status"] == "done"

        # advise reads from json
        out, _, rc = run("advise", str(plan))
        assert rc == 0
        adv = json.loads(out)
        assert adv["tasks"]["done"] == 2
        assert adv["tasks"]["pending"] == 1

        # status reads from json
        out, _, rc = run("status", str(plan))
        assert rc == 0
        assert "tasks.json" in out


def test_checkpoint_save_load():
    with tempfile.TemporaryDirectory() as d:
        plan = Path(d) / "plan.md"
        plan.write_text("## Task Board\n- [x] T1 | owner=codex-1 | Done\n")
        run("tasks", str(plan), "init")

        out, _, rc = run("save-checkpoint", str(plan), "--round", "3")
        assert rc == 0
        cp = Path(d) / "checkpoint.json"
        assert cp.exists()
        data = json.loads(cp.read_text())
        assert data["round"] == 3
        assert len(data["tasks"]) == 1

        # load
        out, _, rc = run("load-checkpoint", d)
        assert rc == 0
        loaded = json.loads(out)
        assert loaded["round"] == 3


def test_sanitize_note_markdown_injection():
    sys.path.insert(0, str(Path(ORCH).parent))
    import orch

    # links stripped but text preserved
    assert "click" in orch._sanitize_note("[click here](http://evil.com)")
    assert "http" not in orch._sanitize_note("[click here](http://evil.com)")

    # images
    assert "http" not in orch._sanitize_note("![alt](http://evil.com/img.png)")

    # html
    assert "<script>" not in orch._sanitize_note("<script>alert(1)</script>")

    # reference links
    result = orch._sanitize_note("[text][ref]")
    assert "[ref]" not in result

    # task injection still blocked
    assert "STRIPPED" in orch._sanitize_note("- [x] T99 injected task")
