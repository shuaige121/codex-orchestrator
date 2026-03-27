#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

ORCH = Path.home() / ".claude" / "plugins" / "codex-orchestrator-v2" / "scripts" / "orch.py"
RESULT_FILE = Path("/tmp/fixtask-flow-results.txt")


def run_orch(*args: str) -> str:
    cmd = ["uv", "run", str(ORCH), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "Command failed: " + " ".join(cmd) + "\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )
    return proc.stdout.strip()


def parse_advise(output: str) -> dict:
    line = output.strip().splitlines()[-1]
    return json.loads(line)


def write_plan(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def assert_contains(text: str, needle: str, msg: str) -> None:
    if needle not in text:
        raise AssertionError(f"{msg} | missing={needle!r} | text={text!r}")


def main() -> None:
    checks: list[str] = []

    with tempfile.TemporaryDirectory(prefix="t6_fix_flow_") as td:
        root = Path(td)

        # a. 2 done + 1 failed => RED + NO PENDING
        plan_a = root / "plan_a.md"
        write_plan(
            plan_a,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | done-1",
                "- [x] T2 | owner=codex-2 | done-2",
                "- [!] T3 | owner=codex-3 | failed-3",
            ],
        )
        a = parse_advise(run_orch("advise", str(plan_a)))
        if a["zone"] != "RED":
            raise AssertionError(f"a: expected RED, got {a}")
        assert_contains(a["reason"], "NO PENDING", "a: expected NO PENDING reason")
        checks.append("a")

        # b. add pending fix task => GREEN + batch=1
        write_plan(
            plan_a,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | done-1",
                "- [x] T2 | owner=codex-2 | done-2",
                "- [!] T3 | owner=codex-3 | failed-3",
                "- [ ] T4 | owner=codex-3 | Fix/retry: retry T3",
            ],
        )
        b = parse_advise(run_orch("advise", str(plan_a)))
        if b["zone"] != "GREEN" or b["recommended_batch"] != 1:
            raise AssertionError(f"b: expected GREEN/batch=1, got {b}")
        checks.append("b")

        # c. fake worker outputs + batch contract check (4-line blocks)
        logs_c = root / "logs_c"
        logs_c.mkdir(parents=True, exist_ok=True)
        (logs_c / "round01_T1_codex-1.md").write_text(
            "some logs\nTASK_STATUS: DONE\nTASK_ID: T1\nOWNER: codex-1\nNOTE: ok\n",
            encoding="utf-8",
        )
        (logs_c / "round01_T2_codex-2.md").write_text(
            "logs\nTASK_STATUS: FAILED\nTASK_ID: T2\nOWNER: codex-2\nNOTE: bad\n",
            encoding="utf-8",
        )
        # ignored by batch collection
        (logs_c / "round01_T3_codex-3_prompt.md").write_text("prompt", encoding="utf-8")

        c_out = run_orch("batch", str(logs_c), "1")
        blocks = [blk.strip().splitlines() for blk in c_out.split("\n\n") if blk.strip()]
        if len(blocks) != 2:
            raise AssertionError(f"c: expected 2 blocks, got {len(blocks)} | out={c_out!r}")
        for idx, block in enumerate(blocks, start=1):
            if len(block) != 4:
                raise AssertionError(f"c: block {idx} not 4 lines: {block!r}")
            if not all(block[i].startswith(prefix) for i, prefix in enumerate([
                "TASK_STATUS:", "TASK_ID:", "OWNER:", "NOTE:"
            ])):
                raise AssertionError(f"c: invalid contract block {idx}: {block!r}")
        checks.append("c")

        # d. 5 done / 0 pending / 0 failed => DONE
        plan_d = root / "plan_d.md"
        write_plan(
            plan_d,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | done",
                "- [x] T2 | owner=codex-1 | done",
                "- [x] T3 | owner=codex-2 | done",
                "- [x] T4 | owner=codex-2 | done",
                "- [x] T5 | owner=codex-3 | done",
            ],
        )
        d = parse_advise(run_orch("advise", str(plan_d)))
        if d["zone"] != "DONE":
            raise AssertionError(f"d: expected DONE, got {d}")
        checks.append("d")

        # e. status mixed states => totals and correct counts
        plan_e = root / "plan_e.md"
        write_plan(
            plan_e,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | done",
                "- [-] T2 | owner=codex-2 | running",
                "- [ ] T3 | owner=codex-3 | pending",
                "- [!] T4 | owner=codex-1 | failed",
                "- [x] T5 | owner=codex-2 | done",
            ],
        )
        e_out = run_orch("status", str(plan_e))
        assert_contains(e_out, "Tasks: 5 total", "e: total")
        assert_contains(e_out, "done 2", "e: done count")
        assert_contains(e_out, "running 1", "e: running count")
        assert_contains(e_out, "pending 1", "e: pending count")
        assert_contains(e_out, "failed 1", "e: failed count")
        checks.append("e")

        # f. batch on empty dir => graceful message
        logs_f = root / "logs_f"
        logs_f.mkdir(parents=True, exist_ok=True)
        f_out = run_orch("batch", str(logs_f), "9")
        assert_contains(f_out, "No output files found for round 9", "f: no output files message")
        checks.append("f")

        # g. full fix flow: failed -> add fix -> running -> fix done -> original done -> DONE
        plan_g = root / "plan_g.md"
        write_plan(
            plan_g,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | baseline done",
                "- [!] T2 | owner=codex-2 | unit test failed",
            ],
        )
        g1 = parse_advise(run_orch("advise", str(plan_g)))
        if g1["zone"] != "RED":
            raise AssertionError(f"g1: expected RED, got {g1}")

        write_plan(
            plan_g,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | baseline done",
                "- [!] T2 | owner=codex-2 | unit test failed",
                "- [ ] T3 | owner=codex-3 | Fix/retry: investigate T2 failure",
            ],
        )
        g2 = parse_advise(run_orch("advise", str(plan_g)))
        if g2["zone"] != "GREEN" or g2["recommended_batch"] != 1:
            raise AssertionError(f"g2: expected GREEN/batch=1, got {g2}")

        write_plan(
            plan_g,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | baseline done",
                "- [!] T2 | owner=codex-2 | unit test failed",
                "- [-] T3 | owner=codex-3 | Fix/retry: investigate T2 failure",
            ],
        )
        g3 = parse_advise(run_orch("advise", str(plan_g)))
        if g3["zone"] != "GREEN" or g3["recommended_batch"] != 0:
            raise AssertionError(f"g3: expected GREEN/batch=0(waiting), got {g3}")

        write_plan(
            plan_g,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | baseline done",
                "- [!] T2 | owner=codex-2 | unit test failed",
                "- [x] T3 | owner=codex-3 | Fix/retry: investigate T2 failure",
            ],
        )
        g4 = parse_advise(run_orch("advise", str(plan_g)))
        if g4["zone"] != "RED":
            raise AssertionError(f"g4: expected RED before original resolved, got {g4}")

        write_plan(
            plan_g,
            [
                "# Plan",
                "- [x] T1 | owner=codex-1 | baseline done",
                "- [x] T2 | owner=codex-2 | unit test failed",
                "- [x] T3 | owner=codex-3 | Fix/retry: investigate T2 failure",
            ],
        )
        g5 = parse_advise(run_orch("advise", str(plan_g)))
        if g5["zone"] != "DONE":
            raise AssertionError(f"g5: expected DONE, got {g5}")
        checks.append("g")

    RESULT_FILE.write_text(
        "T6 fix task + batch/status workflow tests\n"
        "ALL PASSED\n"
        f"checks: {', '.join(checks)}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        RESULT_FILE.write_text(f"FAILED\n{exc}\n", encoding="utf-8")
        raise
