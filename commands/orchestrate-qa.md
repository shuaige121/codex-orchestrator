### 3.10 QA Verification（硬性 — Coordinator 亲自执行，不可委派给 Codex）

When all coding tasks are done (or max_steps reached), the **Coordinator (Claude Code) itself** performs QA.
This is NOT delegated to a Codex worker — the coordinator is the independent reviewer.

**Why**: Codex workers are "运动员" (players). Claude Code is "裁判" (referee).
Workers self-check during their task, but the coordinator does the final holistic verification.

#### Step 1: Run the project's verification commands YOURSELF

Based on the selected stack profile, run the verification sequence directly:

```bash
# Example for python-backend (use absolute paths or chain with &&):
cd {workspace} && ruff check .
cd {workspace} && uv run pytest -x
```

**IMPORTANT**: Check `package.json` scripts / `pyproject.toml` / `Makefile` FIRST.
Use the project's own commands (`npm run lint`, `npm test`, `make check`).
Fall back to profile commands only if the project has no equivalent.

Run each verification step. Record results.

#### Step 2: Verify Deliverables Contract（逐项验收交付物）

Read the **Deliverables Contract** from plan.md. For EACH deliverable:

1. Execute its verification criterion (run command, check file exists, etc.)
2. Record PASS or FAIL with evidence
3. Update the contract table in plan.md:

Change status from `PENDING` to `PASS` or `FAIL`:
```
| D1 | Add login API | `pytest tests/test_auth.py` passes | PASS |
| D2 | Add user model | file `src/models/user.py` exists with `class User` | PASS |
| D3 | API docs | `curl localhost:8080/docs` returns 200 | FAIL — route not found |
```

#### Step 3: Check cross-task integration

- Are there import errors between files modified by different workers?
- Do changed files have consistent naming, style, and patterns?
- Are there obvious regressions in existing functionality?

You may read the changed source files directly (context protection rules about
worker OUTPUT files don't apply to the actual source code).

#### Step 4: Make QA decision

Append to plan.md:
```
## QA Verification
QA_STATUS: PASS or FAIL
DELIVERABLES: {passed}/{total} passed
LINT: <pass/fail>
TEST: <pass/fail>
BUILD: <pass/fail>
FAILED_ITEMS: <D3: reason, or "none">
```

- If **ALL deliverables PASS** and lint/test/build pass: QA_STATUS = PASS → proceed to Phase 4.
- If **ANY deliverable FAILS** or verification fails: QA_STATUS = FAIL →
  Create targeted fix tasks for each failed deliverable, append to Task Board,
  and return to Phase 3.1 to continue the orchestration loop.
  ```
  ## QA Fix Tasks
  - [ ] T<next_id> | owner=codex-1 | QA fix D3: add /docs route for API documentation
  ```
