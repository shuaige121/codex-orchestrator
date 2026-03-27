## Phase 1 — Task Description & Deliverables Contract（硬性）

Generate and write `{run_dir}/任务描述.md` with this structure:

```
# 任务描述

## 目标
<Restate the goal clearly and concisely>

## Deliverables Contract（交付物合同）

Each deliverable MUST have:
- A unique ID (D1, D2, ...)
- A concrete description
- Verifiable acceptance criteria (how to confirm it's done)

| ID | 交付物 | 验收标准 |
|----|--------|---------|
| D1 | <deliverable description> | <concrete verification: command, file exists, test passes, etc.> |
| D2 | <deliverable description> | <concrete verification> |
| D3 | <deliverable description> | <concrete verification> |

**验收标准必须是可执行的**:
- GOOD: "运行 `uv run pytest tests/test_auth.py` 全部通过"
- GOOD: "文件 `src/auth/login.py` 存在且包含 `class LoginHandler`"
- GOOD: "`npm run build` 成功退出，无错误"
- BAD: "代码质量好" (不可验证)
- BAD: "功能完善" (不具体)

## 角色与分工
- Coordinator (Claude Code): plans, dispatches, QA verification, contract enforcement
- Executors (codex-1, codex-2, …): execute tasks, self-check
- QA (Claude Code): independent verification of all deliverables after coding

## 技术栈
- Stack: {stack_id} ({stack_name})
- 工具链: {toolchain from profile}

## 运行约束
- Max parallel workers: {max_workers}
- Max batch size: {max_batch}
- Max orchestration rounds: {max_steps}
```

**CRITICAL**: The Deliverables Contract is the single source of truth for determining success.
Phase 3.10 QA verifies against this contract. Phase 4 reports contract status.
The main agent (caller) only needs to see the contract status report — no code reading required.

Write this file using the Write tool.
