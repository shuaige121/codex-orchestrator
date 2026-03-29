#!/usr/bin/env python3
from __future__ import annotations

import shlex
import subprocess
import tempfile
import time
from pathlib import Path

RESULT_FILE = Path("/tmp/timeout-integration-results.txt")


def run_cmd(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", "-lc", command],
        capture_output=True,
        text=True,
    )


def chmod_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def main() -> int:
    output_lines: list[str] = []
    failures: list[str] = []

    def report(test_num: int, name: str, ok: bool, reason: str = "") -> None:
        if ok:
            line = f"TEST {test_num}: {name} ... PASSED"
        else:
            line = f"TEST {test_num}: {name} ... FAILED: {reason}"
            failures.append(line)
        print(line)
        output_lines.append(line)

    # Case 1
    case1 = run_cmd("which timeout")
    report(
        1,
        "timeout command exists",
        case1.returncode == 0,
        f"which timeout rc={case1.returncode}, stderr={case1.stderr.strip()}",
    )

    # Case 2
    case2 = run_cmd("timeout 2 sleep 10")
    report(
        2,
        "timeout 2 sleep 10 exits 124",
        case2.returncode == 124,
        f"expected 124, got {case2.returncode}",
    )

    # Case 3
    case3 = run_cmd("timeout 5 sleep 1")
    report(
        3,
        "timeout 5 sleep 1 exits 0",
        case3.returncode == 0,
        f"expected 0, got {case3.returncode}",
    )

    with tempfile.TemporaryDirectory(prefix="t4_timeout_") as td:
        tmp_dir = Path(td)

        # Case 4
        slow_writer = tmp_dir / "slow_writer.sh"
        timed_out_output = tmp_dir / "worker_output.txt"
        slow_writer.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "sleep 10\n"
            "echo done > \"$1\"\n",
            encoding="utf-8",
        )
        chmod_executable(slow_writer)

        case4_cmd = (
            f"timeout 2 bash {shlex.quote(str(slow_writer))} "
            f"{shlex.quote(str(timed_out_output))}"
        )
        case4 = run_cmd(case4_cmd)
        case4_ok = case4.returncode == 124 and not timed_out_output.exists()
        case4_reason = (
            f"rc={case4.returncode}, output_exists={timed_out_output.exists()}"
        )
        report(
            4,
            "timeout prevents output file creation",
            case4_ok,
            case4_reason,
        )

        # Case 5
        trap_script = tmp_dir / "trap_cleanup.sh"
        pid_file = tmp_dir / "child.pid"
        trap_script.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            "PID_FILE=\"$1\"\n"
            "sleep 300 &\n"
            "CHILD_PID=$!\n"
            "echo \"$CHILD_PID\" > \"$PID_FILE\"\n"
            "trap \"kill $CHILD_PID 2>/dev/null\" EXIT\n"
            "wait $CHILD_PID\n",
            encoding="utf-8",
        )
        chmod_executable(trap_script)

        case5_cmd = f"timeout 2 bash {shlex.quote(str(trap_script))} {shlex.quote(str(pid_file))}"
        case5 = run_cmd(case5_cmd)
        child_pid: str | None = None
        if pid_file.exists():
            child_pid = pid_file.read_text(encoding="utf-8").strip()

        child_gone = False
        if child_pid:
            for _ in range(10):
                alive = run_cmd(f"kill -0 {shlex.quote(child_pid)}")
                if alive.returncode != 0:
                    child_gone = True
                    break
                time.sleep(0.2)

        case5_ok = (
            case5.returncode == 124
            and child_pid is not None
            and child_gone
        )
        case5_reason = (
            f"timeout_rc={case5.returncode}, pid_file_exists={pid_file.exists()}, "
            f"child_pid={child_pid}, child_gone={child_gone}"
        )
        report(
            5,
            "trap cleanup removes child after timeout",
            case5_ok,
            case5_reason,
        )

        if child_pid and not child_gone:
            run_cmd(f"kill {shlex.quote(child_pid)} 2>/dev/null || true")

    if failures:
        summary = "FAILURES: " + " | ".join(failures)
    else:
        summary = "ALL PASSED"
    print(summary)
    output_lines.append(summary)

    RESULT_FILE.write_text("\n".join(output_lines) + "\n", encoding="utf-8")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
